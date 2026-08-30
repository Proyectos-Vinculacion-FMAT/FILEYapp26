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

.. warning:: Y para eso hace falta un savepoint, no un ``try``

   Dentro de una transacción, **atrapar un error de base de datos no
   basta**: PostgreSQL deja la transacción abortada y *todo* lo que venga
   después falla con ``TransactionManagementError``, aunque la excepción
   original se haya tragado. El ``with transaction.atomic()`` de abajo es
   un savepoint: absorbe el fallo y devuelve la transacción del llamador
   en estado utilizable.

   Sin él, la promesa de arriba era falsa justo donde importa —el fallo
   realista es de base de datos, no de otra cosa— y la prueba no lo
   veía, porque simulaba un ``OSError``, que no ensucia nada.
"""

import logging

from django.db import transaction

from ..models import BitacoraSTD

logger = logging.getLogger(__name__)


#: Cómo se llega de cada objeto anotable a su convocatoria. Explícito y
#: no adivinado: son cinco, se enumeran, y el día que entre un sexto la
#: prueba de su acción lo señala. Adivinar recorriendo relaciones sería
#: un `getattr` en cadena que falla en silencio, que es justo lo que una
#: bitácora no puede hacer.
DE_QUE_CONVOCATORIA = {
    "reserva": lambda o: o.registro.convocatoria_id,
    "solicitud": lambda o: o.registro.convocatoria_id,
    "movimiento": lambda o: o.reserva.registro.convocatoria_id,
    "configuracionsistema": lambda o: o.convocatoria_id,
    "mapashowfloor": lambda o: o.convocatoria_id,
}


def anotar(*, persona, accion: str, objeto, **detalle) -> BitacoraSTD | None:
    """Deja constancia de una acción sobre un objeto de `STD`.

    :param persona: quién la hizo. ``None`` cuando la hace el sistema —la
        barrida diaria caducando un pronto pago—, y que no haya persona
        **es** el dato: nadie lo decidió, se cumplió una regla.
    :param accion: una de `BitacoraSTD.Accion`.
    :param objeto: la instancia afectada. De ahí salen `entidad_tipo`,
        `entidad_id` **y la convocatoria**, por `DE_QUE_CONVOCATORIA`.
    :param detalle: las cifras del cambio, que es lo que hace legible la
        línea sin abrir el objeto — y lo que sigue diciendo algo cuando
        el objeto ya cambió otra vez. Todo tiene que ser serializable a
        JSON: los `Decimal` y las fechas se pasan como texto.
    :returns: la entrada, o ``None`` si no se pudo escribir.
    """
    modelo = objeto._meta.model_name
    try:
        convocatoria_id = DE_QUE_CONVOCATORIA[modelo](objeto)
        # El `atomic` anidado es el savepoint que hace cierta la promesa
        # de "anotar no tumba la acción": ver la advertencia de arriba.
        with transaction.atomic():
            return BitacoraSTD.objects.create(
                convocatoria_id=convocatoria_id,
                persona=persona,
                accion=accion,
                entidad_tipo=modelo,
                entidad_id=objeto.pk,
                detalle=detalle,
            )
    except Exception:  # noqa: BLE001 — anotar no puede tumbar la acción
        logger.exception(
            "No se pudo anotar «%s» sobre %s %s", accion, modelo, objeto.pk
        )
        return None


def de(objeto):
    """Lo que se ha anotado sobre este objeto, de lo más reciente atrás."""
    return BitacoraSTD.objects.filter(
        entidad_tipo=objeto._meta.model_name, entidad_id=objeto.pk
    ).select_related("persona")


def de_la_convocatoria(convocatoria):
    """La línea de tiempo de **una** convocatoria de stands.

    Es la pregunta para la que existe la tabla, y por la que la
    convocatoria se guarda en vez de deducirse: una feria puede tener la
    convocatoria general y la de un pabellón (`RN-19`), y son dos ventas
    distintas con dos mapas y dos precios. Mezclarlas convierte la
    bitácora en algo que hay que leer entero para encontrar una cosa.
    """
    return BitacoraSTD.objects.filter(convocatoria=convocatoria).select_related(
        "persona"
    )
