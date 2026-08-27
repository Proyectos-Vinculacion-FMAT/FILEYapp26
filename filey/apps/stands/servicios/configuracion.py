"""
La configuración de una convocatoria de stands (`CU-STD-034`).

Aquí vive el callback que `apps/stands/apps.py` inscribe en el registro
de módulos. Es lo que cierra el paso 6 de `CU-FER-005`, que hasta ahora
corría en vacío porque nadie servía el tipo `STD`.
"""

import logging

from apps.convocatorias.models import Convocatoria, TipoConvocatoria

from ..models import ConfiguracionSistema

logger = logging.getLogger(__name__)


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
