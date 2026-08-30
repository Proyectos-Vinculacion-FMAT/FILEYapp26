"""
Anotar lo que se hizo (`BitacoraSTD`, modelo de datos §3.12).

Una sola función, y a propósito: la bitácora tiene que ser **barata de
escribir**, porque si anotar cuesta tres líneas se acaba anotando solo
donde alguien se acordó.

.. important:: Se anota dentro de la transacción de la acción

   Al revés que los avisos por correo, que van con
   ``transaction.on_commit`` porque no se pueden deshacer. Una anotación
   sí se deshace, y una que sobreviviera a un rollback diría que pasó
   algo que no pasó. Como se llama desde servicios que ya son atómicos,
   no hace falta nada más que llamarla ahí dentro.

.. note:: Anotar nunca tumba la acción

   Un fallo escribiendo la bitácora se registra en el log y se traga. La
   alternativa —que una anotación fallida reviente una validación de pago
   que el banco ya respaldó— es peor que perder una línea de historial.
   Es el mismo criterio que `avisos.py` con el correo.
"""

import logging

from ..models import BitacoraSTD

logger = logging.getLogger(__name__)


def anotar(*, persona, accion: str, objeto, **detalle) -> BitacoraSTD | None:
    """Deja constancia de una acción sobre un objeto de `STD`.

    :param persona: quién la hizo. ``None`` cuando la hace el sistema —la
        barrida diaria caducando un pronto pago—, y que no haya persona
        **es** el dato: nadie lo decidió, se cumplió una regla.
    :param accion: una de `BitacoraSTD.Accion`.
    :param objeto: la instancia afectada; de ahí salen `entidad_tipo` y
        `entidad_id`.
    :param detalle: las cifras del cambio, que es lo que hace legible la
        línea sin abrir el objeto — y lo que sigue diciendo algo cuando
        el objeto ya cambió otra vez. Todo tiene que ser serializable a
        JSON: los `Decimal` y las fechas se pasan como texto.
    :returns: la entrada, o ``None`` si no se pudo escribir.
    """
    try:
        return BitacoraSTD.objects.create(
            persona=persona,
            accion=accion,
            entidad_tipo=objeto._meta.model_name,
            entidad_id=objeto.pk,
            detalle=detalle,
        )
    except Exception:  # noqa: BLE001 — anotar no puede tumbar la acción
        logger.exception(
            "No se pudo anotar «%s» sobre %s %s",
            accion,
            objeto._meta.model_name,
            objeto.pk,
        )
        return None


def de(objeto):
    """Lo que se ha anotado sobre este objeto, de lo más reciente atrás."""
    return BitacoraSTD.objects.filter(
        entidad_tipo=objeto._meta.model_name, entidad_id=objeto.pk
    ).select_related("persona")
