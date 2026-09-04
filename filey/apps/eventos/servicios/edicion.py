"""
Corregir lo redactado de una propuesta (`CU-EVT-008`).

Quien revisa lee una propuesta para dictaminarla, y a veces lo que
encuentra no es motivo de rechazo ni de devolverla: es una errata, una
semblanza en tercera persona que hay que pasar a primera, o una sinopsis
con la que el programa impreso no se puede componer. `CU-EVT-004` existe
para lo que tiene que corregir **quien propuso**; esto es lo otro, y el
prototipo lo tiene desde el principio («Editar información del
formulario»).

Se corrige **solo lo redactado**: la sinopsis y la semblanza de cada
persona. Deliberadamente no se toca nada más:

- **Los nombres y el título no**, porque son la identidad de la propuesta
  y la de su gente; cambiarlos desde aquí convierte una corrección de
  estilo en otra propuesta.
- **Los datos del proponente tampoco**: salen de su cuenta y de lo que
  declaró, y `RN` del dominio los quiere tal como llegaron.
- **La autodeclaración de la UADY, menos todavía**: para corregirla ya
  existe `es_uady_confirmado`, que es del dictamen y deja constancia de
  que alguien la revisó (§3.1). Pisar `es_uady` borraría lo que dijo
  quien propuso, que es justo lo que hay que poder comparar.

Es un servicio y no un `ModelForm` en la vista por la regla de siempre:
la invariante que sostiene —una persona capturada nunca se queda sin
semblanza— tiene que valer también desde `manage.py`.
"""

import logging

from django.db import transaction

from ..models import MAX_SEMBLANZA, MAX_SINOPSIS, MAX_SINOPSIS_PUBLICACION, Solicitud
from . import catalogo, revision

logger = logging.getLogger(__name__)


class CorreccionRechazada(Exception):
    """Lo que se intentó guardar dejaría la propuesta peor de lo que estaba."""


def tope_de_sinopsis(solicitud: Solicitud) -> int:
    """Cuántos caracteres admite la sinopsis de **esta** propuesta.

    Los dos tipos de publicación admiten el doble, y no es un detalle de
    formulario: es lo que pedía la convocatoria en papel. El tope vive
    aquí y no en el modelo porque la columna es la misma para los ocho
    tipos —`Solicitud.sinopsis`— y quien la acota es el tipo elegido.
    """
    actividad = getattr(solicitud, "actividad", None)
    if actividad and catalogo.es_publicacion(actividad.tipo.nombre):
        return MAX_SINOPSIS_PUBLICACION
    return MAX_SINOPSIS


def corregir(solicitud: Solicitud, *, editor, sinopsis: str, semblanzas: dict) -> Solicitud:
    """Guarda la redacción corregida.

    ``semblanzas`` llega como ``{columna: texto}`` con las columnas que
    `revision.personas_de` nombró — nunca con las que traiga el POST—.
    Es lo que impide que un formulario fabricado a mano escriba en una
    columna que esta propuesta no tiene, o en una que sí tiene pero cuya
    persona nadie capturó.

    **Una persona capturada no se puede quedar sin semblanza.** Es la
    misma invariante que `formularios.validar_personas` sostiene en el
    alta: media persona no se puede imprimir en un programa ni mandar a
    un comité, y aquí sería aún más fácil de romper porque quien corrige
    ve el recuadro lleno y puede vaciarlo de un tirón.

    Las dos escrituras van en la misma transacción: la sinopsis vive en
    `Solicitud` y las semblanzas en la tabla del tipo, y guardar una sí y
    la otra no dejaría la propuesta a medio corregir sin que nada lo
    dijera.
    """
    sinopsis = (sinopsis or "").strip()
    if not sinopsis:
        raise CorreccionRechazada(
            "La sinopsis no puede quedar vacía: es lo que se lee para "
            "programar la actividad y lo que se imprime en el programa."
        )
    tope = tope_de_sinopsis(solicitud)
    if len(sinopsis) > tope:
        raise CorreccionRechazada(
            f"La sinopsis admite {tope} caracteres y lleva {len(sinopsis)}."
        )

    actividad = getattr(solicitud, "actividad", None)
    permitidas = {
        persona.campo_semblanza: persona
        for persona in revision.personas_de(actividad)
    }
    limpias = {}
    for columna, texto in semblanzas.items():
        persona = permitidas.get(columna)
        if persona is None:
            # No es un error del formulario: es un campo que esta
            # propuesta no tiene. Se ignora en silencio, como los filtros
            # inventados de la cola.
            continue
        texto = (texto or "").strip()
        if not texto:
            raise CorreccionRechazada(
                f"{persona.rol} «{persona.nombre}» se quedaría sin semblanza. "
                "Escribe una o deja la que estaba."
            )
        if len(texto) > MAX_SEMBLANZA:
            raise CorreccionRechazada(
                f"La semblanza de «{persona.nombre}» admite {MAX_SEMBLANZA} "
                f"caracteres y lleva {len(texto)}."
            )
        limpias[columna] = texto

    with transaction.atomic():
        Solicitud.objects.filter(pk=solicitud.pk).update(sinopsis=sinopsis)
        solicitud.sinopsis = sinopsis
        if limpias and actividad is not None:
            detalle = actividad.detalle
            for columna, texto in limpias.items():
                setattr(detalle, columna, texto)
            detalle.save(update_fields=list(limpias))

    logger.info(
        "Propuesta %s corregida por %s (%d semblanzas)",
        solicitud.pk,
        getattr(editor, "pk", "?"),
        len(limpias),
    )
    return solicitud
