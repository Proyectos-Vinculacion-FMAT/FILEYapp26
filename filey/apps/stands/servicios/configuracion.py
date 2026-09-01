"""
La configuración de una convocatoria de stands (`CU-STD-034`).

Aquí vive el callback que `apps/stands/apps.py` inscribe en el registro
de módulos. Es lo que cierra el paso 6 de `CU-FER-005`, que hasta ahora
corría en vacío porque nadie servía el tipo `STD`.
"""

import logging

from django.db import transaction

from apps.convocatorias.models import Convocatoria, TipoConvocatoria

from ..models import BitacoraSTD, ConfiguracionSistema
from . import bitacora

logger = logging.getLogger(__name__)

#: Cuánto de un valor cabe en la anotación. `instrucciones_pago` es un
#: campo libre y sin tope la bitácora acabaría guardando párrafos.
LARGO_MAXIMO = 120


def crear_por_defecto(convocatoria: Convocatoria) -> ConfiguracionSistema:
    """Le da a una convocatoria de stands recién creada su configuración.

    Lo llama `apps/convocatorias/servicios/altas.py` **dentro de la
    transacción del alta**: si esto revienta, no queda ni la convocatoria
    (`CU-FER-005` E1). Es deliberadamente más duro que el fallo de un
    correo de cortesía — una convocatoria de stands sin `costo_m2` no se
    puede operar, y a medias engaña: se ve igual que una buena en el
    catálogo.

    Los valores por omisión son los de las reglas de negocio —50% de
    anticipo (`RN-02`), 30 días de plazo (`RN-03`), 10% de pronto pago
    (`RN-04`)—. El **precio no**: nace en cero, porque no hay un costo
    por metro cuadrado razonable que adivinar. El dueño de la feria lo
    fija antes de abrir la convocatoria.

    Es idempotente. Volver a llamarlo con la misma convocatoria devuelve
    la configuración que ya existe en vez de reventar contra la
    restricción de unicidad: quien lo invoca es un callback, y un
    callback que falla por haberse ejecutado dos veces se lleva por
    delante un alta que estaba bien.
    """
    if convocatoria.tipo != TipoConvocatoria.STD:
        # No debería pasar —el registro de módulos llama a cada uno con
        # su tipo—, pero es la misma clase de invariante que la de
        # `Solicitud`: si el día de mañana alguien invoca esto a mano,
        # que falle aquí y no dejando una configuración de stands colgada
        # de una convocatoria de eventos.
        raise ValueError(
            f"«{convocatoria.nombre}» es una convocatoria {convocatoria.tipo}; "
            "esta configuración es de stands."
        )

    configuracion, creada = ConfiguracionSistema.objects.get_or_create(
        convocatoria=convocatoria
    )
    if creada:
        logger.info(
            "Configuración de stands creada para la convocatoria «%s»",
            convocatoria.nombre,
        )
    return configuracion


@transaction.atomic
def guardar(*, form, administrador) -> ConfiguracionSistema:
    """Guarda los ajustes de A10 y anota qué cambió (`CU-STD-034`).

    **Es lo más sensible que se toca desde una pantalla**, y hasta hoy no
    dejaba rastro en ninguna parte: quién subió el `costo_m2` a mitad de
    campaña, quién movió la fecha del pronto pago o quién cambió la CLABE
    no se podía saber. Las reservas ya hechas no se mueven (`RN-01`), lo
    que cambia es lo que costará la siguiente — y eso es exactamente el
    tipo de cosa por la que meses después alguien pregunta.

    Recibe el **formulario ya validado** y no un diccionario de campos
    porque lo que se anota es *qué cambió*, y eso lo sabe el formulario:
    `changed_data` compara contra lo que se le pintó a quien lo llenó,
    que es justo la pregunta. Reconstruirlo fuera obligaría a leer la
    fila antes de guardar y a comparar campo por campo.

    Si no cambió nada, no anota: una bitácora con líneas que dicen "no
    tocó nada" es una que hay que leer entera para encontrar algo.
    """
    cambios = {
        campo: [
            _legible(form.initial.get(campo)),
            _legible(form.cleaned_data.get(campo)),
        ]
        for campo in form.changed_data
    }
    ajustes = form.save()
    if cambios:
        bitacora.anotar(
            persona=administrador,
            accion=BitacoraSTD.Accion.CONFIGURACION_CAMBIADA,
            objeto=ajustes,
            cambios=cambios,
        )
        logger.info(
            "Configuración de «%s» cambiada por %s: %s",
            ajustes.convocatoria.nombre,
            administrador.pk,
            ", ".join(cambios),
        )
    return ajustes


def _legible(valor) -> str:
    """Un valor de formulario como texto corto, para meterlo en el JSON.

    Todo a texto: `Decimal` y `date` no son serializables, y en una
    bitácora lo que se lee es "2500.00 → 3000.00", no el tipo.
    """
    if valor in (None, ""):
        return "—"
    texto = str(valor)
    return texto if len(texto) <= LARGO_MAXIMO else texto[:LARGO_MAXIMO] + "…"


def de_la_convocatoria(convocatoria: Convocatoria) -> ConfiguracionSistema:
    """La configuración de **esta** convocatoria.

    Existe para que ninguna pantalla escriba
    ``ConfiguracionSistema.objects.get()`` a secas. Desde el 2026-08-25
    una feria puede tener varias convocatorias de stands, así que "la
    configuración" sin convocatoria no significa nada — y la consulta sin
    filtro no falla: devuelve la primera que encuentre.

    Si no existe la crea. Una convocatoria dada de alta antes de que esta
    app estuviera instalada no pasó por el callback.
    """
    return crear_por_defecto(convocatoria)
