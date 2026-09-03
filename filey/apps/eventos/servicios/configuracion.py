"""
La configuración de una convocatoria de eventos (`CU-EVT-001`).

Hoy es una sola cosa —el prefijo del folio—, y aun así vive en su propia
tabla y no como una columna de `Convocatoria`: `FER` enmarca las
convocatorias y no sabe qué hay detrás de ninguna (`ADR-0006`). Los
parámetros de la etapa 2 (cupos meta, fechas de notificación) se añaden
aquí conforme se construyan.
"""

from apps.convocatorias.models import Convocatoria

from ..models import ConfiguracionConvocatoria


def crear_por_defecto(convocatoria: Convocatoria) -> ConfiguracionConvocatoria:
    """Le da a una convocatoria de eventos recién creada su configuración.

    Lo llama `apps/convocatorias/servicios/altas.py` **dentro de la
    transacción del alta**: si esto revienta, no queda ni la convocatoria
    (`CU-FER-005` E1).

    Es idempotente. Volver a llamarlo con la misma convocatoria devuelve
    la que ya existe en vez de reventar contra la restricción de
    unicidad: quien lo invoca es un callback, y un callback que falla por
    haberse ejecutado dos veces se lleva por delante un alta que estaba
    bien.
    """
    configuracion, _ = ConfiguracionConvocatoria.objects.get_or_create(
        convocatoria=convocatoria
    )
    return configuracion


def de(convocatoria: Convocatoria) -> ConfiguracionConvocatoria:
    """La configuración de esa convocatoria, creándola si falta.

    Que falte no debería pasar —la crea el alta—, pero una convocatoria
    dada de alta antes de que esta app existiera no la tiene, y esa es
    exactamente la situación de cualquier feria que ya estuviera creada.
    """
    return crear_por_defecto(convocatoria)
