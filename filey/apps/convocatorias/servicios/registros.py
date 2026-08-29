"""
Inscribirse a una convocatoria (`ADR-0006`).

Es la puerta por la que los seis módulos entran a `FER`. Ninguno escribe
`RegistroConvocatoria` por su cuenta: la tabla es de `FER`, y con ella
las tres reglas que `FER` es la única que puede hacer cumplir —si la
convocatoria admite registros, si la edición sigue viva, y que no haya
dos inscripciones de la misma persona a la misma puerta—.

.. note:: Aquí acaba `FER` y empieza el módulo

   Esto devuelve un registro. Qué se cuelga de él —una propuesta, una
   ficha de expositor, una solicitud de visita— es del módulo, y `FER` no
   lo sabe ni tiene que saberlo (`CU-FER-006`).
"""

import logging

from django.db import connection, transaction
from django_tenants.utils import get_public_schema_name

from apps.ferias.models import Feria

from ..models import Convocatoria, RegistroConvocatoria

logger = logging.getLogger(__name__)


class RegistroRechazado(Exception):
    """No se puede inscribir a nadie en esta convocatoria ahora mismo."""


class TipoQueNoCorresponde(RegistroRechazado):
    """Un módulo intenta colgar su expediente de una convocatoria ajena.

    Es **la** invariante que el esquema no puede sostener (`ADR-0006`), y
    por eso tiene excepción propia: cuando salte, lo que hay detrás no es
    un dato mal escrito por un usuario sino un módulo llamando a donde no
    debe.
    """


def _feria_de_la_conexion() -> Feria | None:
    """La feria en cuyo schema estamos, o ``None`` si estamos en `public`.

    Se pregunta por ``connection.schema_name`` y no por
    ``connection.tenant`` por lo mismo que en `altas.py`:
    ``schema_context()`` deja ahí un ``FakeTenant`` sin ``estado``.
    """
    schema = connection.schema_name
    if schema == get_public_schema_name():
        return None
    return Feria.objects.filter(schema_name=schema).first()


def exigir_edicion_operable() -> Feria:
    """Que la edición en la que estamos admita que se le escriba.

    `CU-FER-006` E1: una edición archivada se consulta, no se opera. Es
    una regla de `FER` sobre su propia edición, y por eso vive aquí y no
    repartida entre seis módulos — repartirla es repartir seis
    oportunidades de olvidarla.

    Es **pública** y no un detalle de `obtener_o_crear_registro` porque
    hay operaciones de módulo que no crean registro y siguen siendo
    escrituras: reenviar una solicitud, abonar, reservar. Ésas entraban
    en una feria archivada por la puerta de atrás, porque la única
    comprobación colgaba del alta del registro.

    :returns: la feria, ya comprobada.
    :raises RegistroRechazado: fuera de una feria, o en una archivada.
    """
    feria = _feria_de_la_conexion()
    if feria is None:
        raise RegistroRechazado(
            "Esto pertenece a una feria: no se puede hacer desde fuera de "
            "una edición."
        )
    if feria.estado == Feria.Estado.ARCHIVADA:
        raise RegistroRechazado(
            f"«{feria.nombre}» está archivada: una edición cerrada se "
            "consulta, no se le escribe."
        )
    return feria


def obtener_o_crear_registro(
    *,
    convocatoria: Convocatoria,
    persona,
    tipo_esperado: str,
) -> tuple[RegistroConvocatoria, bool]:
    """Inscribe a `persona` en `convocatoria`, o recupera su inscripción.

    Lo llama el módulo **dentro de la misma transacción que crea su
    expediente**, y de ahí sale el momento en que nace un registro: al
    guardarse el expediente, no al pulsar el botón del catálogo. Si
    naciera con el clic, cada visita curiosa dejaría una inscripción
    vacía y los conteos de la convocatoria contarían gente que nunca
    aplicó (`ADR-0006`).

    Devuelve ``(registro, se_creo)``. Que ``se_creo`` sea ``False`` es lo
    normal al volver a aplicar tras un rechazo (RN-22 de `STD`): el
    registro es el mismo, el expediente es otro.

    :param tipo_esperado: qué tipo de convocatoria sirve quien llama.
        **Es obligatorio y no tiene valor por omisión**, y ese es todo su
        propósito: es la única forma que hay de comprobar la invariante
        que el esquema no puede: que `Solicitud` de stands no cuelgue de
        un registro de una convocatoria de eventos. Cada módulo pasa aquí
        su propio tipo y esta función lo contrasta; si el parámetro
        tuviera valor por omisión, olvidarlo pasaría inadvertido.
    """
    if convocatoria.tipo != tipo_esperado:
        raise TipoQueNoCorresponde(
            f"«{convocatoria.nombre}» es una convocatoria {convocatoria.tipo} y "
            f"quien intenta colgar su expediente sirve {tipo_esperado}. La base "
            "de datos no puede impedirlo; esta comprobación sí."
        )

    if persona is None or not getattr(persona, "is_authenticated", False):
        raise RegistroRechazado(
            "Inscribirse necesita una cuenta: el registro apunta a una `Persona`."
        )

    # `estado` es lo que abre la puerta, no las fechas (`CU-FER-008`). Una
    # convocatoria en borrador no tiene revisada su configuración y una
    # cerrada ya no recibe: ni una ni otra admiten inscripciones.
    if convocatoria.estado != Convocatoria.Estado.ABIERTA:
        raise RegistroRechazado(
            f"«{convocatoria.nombre}» no está abierta: no admite registros."
        )

    feria = exigir_edicion_operable()

    with transaction.atomic():
        registro, se_creo = RegistroConvocatoria.objects.get_or_create(
            convocatoria=convocatoria,
            persona=persona,
            defaults={"estado": RegistroConvocatoria.Estado.ACTIVO},
        )
        # Alguien que se retiró y vuelve a aplicar se reactiva: la
        # restricción única impide crearle un registro nuevo, y dejarlo
        # `retirado` lo borraría de los conteos de la convocatoria pese a
        # tener un expediente vivo colgando.
        if not se_creo and registro.estado == RegistroConvocatoria.Estado.RETIRADO:
            registro.estado = RegistroConvocatoria.Estado.ACTIVO
            registro.save(update_fields=["estado"])

    if se_creo:
        logger.info(
            "Registro %s en la convocatoria %s «%s» de la feria %s",
            persona.pk,
            convocatoria.tipo,
            convocatoria.nombre,
            feria.slug,
        )

    return registro, se_creo
