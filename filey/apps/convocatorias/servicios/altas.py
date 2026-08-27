"""
Alta de una convocatoria dentro de una feria (`CU-FER-005`).

Toda la lógica vive aquí y no en el admin: el admin es un envoltorio que
llama a `crear_convocatoria`. Es la regla 3 de CLAUDE.md —si algo no se
puede ejecutar desde `manage.py` sin pasar por HTTP, está en el lugar
equivocado— y es el mismo reparto que ya usa `ferias/servicios/altas.py`
para el alta de una feria.

.. note:: En qué feria se crea **no es un parámetro**, y no puede serlo

   La convocatoria se escribe en el schema al que apunta la conexión
   (`ADR-0003`). Si además se recibiera una `feria` por parámetro habría
   dos fuentes para la misma pregunta, y el día que divergieran no daría
   error: se comprobaría el estado de una feria y la fila caería en el
   schema de otra. Por eso la feria se **deriva** de la conexión — el
   mismo criterio que sigue `apps/ferias/permisos.py::acceso_a`, que
   toma la feria de `peticion.tenant` en vez de re-resolver el slug.
"""

import logging
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django_tenants.utils import get_public_schema_name

from apps.ferias.models import Feria

from ..models import Convocatoria

logger = logging.getLogger(__name__)


class AltaRechazada(Exception):
    """El alta no se puede intentar: no hay feria, o no admite convocatorias."""


@dataclass
class ResultadoAlta:
    convocatoria: Convocatoria
    feria: Feria
    #: Las que ya había de este mismo tipo, para el aviso de A2. Se
    #: calculan **antes** de crear la nueva, así que nunca la incluyen.
    otras_del_mismo_tipo: list


def feria_de_la_conexion() -> Feria:
    """La feria en cuyo schema está escribiendo esta conexión.

    Se pregunta por `connection.schema_name` y no por `connection.tenant`
    a propósito: `schema_context("feria_2027")` deja ahí un `FakeTenant`
    que solo lleva el nombre del schema, sin `estado` que consultar. El
    nombre del schema, en cambio, siempre es el de verdad, y la fila
    completa se recupera de `public` —alcanzable porque `django-tenants`
    deja el `search_path` en `[feria_x, public]`—.
    """
    schema = connection.schema_name
    if schema == get_public_schema_name():
        raise AltaRechazada(
            "Una convocatoria pertenece a una feria: no se puede crear desde "
            "fuera de una edición. Entra por /f/<slug>/."
        )
    try:
        return Feria.objects.get(schema_name=schema)
    except Feria.DoesNotExist as exc:  # pragma: no cover - schema huérfano
        raise AltaRechazada(
            f"El schema «{schema}» no corresponde a ninguna feria registrada."
        ) from exc


def feria_que_admite_convocatorias() -> Feria:
    """La feria de la conexión, si además puede recibir una nueva (E2).

    Está separada de `crear_convocatoria` porque la pregunta se hace en
    tres momentos distintos —al pintar el botón de «añadir», al validar
    el formulario y al guardar— y las tres respuestas tienen que salir
    del mismo sitio. Si el botón y el guardado discreparan, el resultado
    sería un formulario que se deja llenar y falla al enviarlo.
    """
    feria = feria_de_la_conexion()
    # Una edición cerrada se consulta, no se opera. Consultarla sí se
    # puede: lo que se veta aquí es abrirle puertas nuevas, no mirarla.
    if feria.estado == Feria.Estado.ARCHIVADA:
        raise AltaRechazada(
            f"«{feria.nombre}» está archivada: una edición cerrada se consulta, "
            "no se le abren convocatorias nuevas."
        )
    return feria


def crear_convocatoria(
    *,
    tipo: str,
    nombre: str,
    fecha_apertura=None,
    fecha_cierre=None,
) -> ResultadoAlta:
    """Crea una convocatoria en `borrador`. O no crea nada.

    Pasos 4-7 del flujo principal de CU-FER-005.
    """
    feria = feria_que_admite_convocatorias()

    # A2: se mira ANTES de crear, para que la nueva no salga en su propio
    # aviso. No bloquea nada —varias del mismo tipo son legítimas—, solo
    # da de qué avisar a quien la está dando de alta.
    otras = list(Convocatoria.objects.filter(tipo=tipo))

    convocatoria = Convocatoria(
        tipo=tipo,
        nombre=(nombre or "").strip(),
        fecha_apertura=fecha_apertura,
        fecha_cierre=fecha_cierre,
        # Paso 6: nace en borrador, siempre y explícitamente. No se
        # delega en el `default` del campo porque es una postcondición
        # del caso de uso, no una comodidad: abrirla es un acto aparte
        # y deliberado (CU-FER-008).
        estado=Convocatoria.Estado.BORRADOR,
    )

    try:
        convocatoria.full_clean()
    except ValidationError as exc:
        # Quien llega por el admin no pasa por aquí —su formulario ya
        # validó—; esto es para el shell y para el día que haya un
        # comando de `manage.py`.
        raise AltaRechazada(
            " ".join(m for mensajes in exc.message_dict.values() for m in mensajes)
        ) from exc

    # El `atomic` protege un solo INSERT hoy, y aun así se escribe ya:
    # es donde entran, en la misma transacción, la `ConfiguracionSistema`
    # de las convocatorias `STD` (paso 6) y la entrada de `BitacoraFER`.
    # Ninguno de los dos modelos existe todavía; el sitio sí.
    with transaction.atomic():
        convocatoria.save()

    logger.info(
        "Convocatoria %s «%s» creada en la feria %s",
        convocatoria.tipo,
        convocatoria.nombre,
        feria.slug,
    )

    return ResultadoAlta(
        convocatoria=convocatoria,
        feria=feria,
        otras_del_mismo_tipo=otras,
    )
