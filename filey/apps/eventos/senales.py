"""
Lo que `EVT` escucha de `FER`.

Dos receptores, los dos por la política de adjuntos de `CU-EVT-002`:
**lo que quedara a medio subir se descarta en cuanto deja de haber un
formulario a medio llenar**.

- **El catálogo.** Volver a él es abandonar el formulario. No puede
  llamarnos —`apps/convocatorias` no nombra a ningún vertical
  (`ADR-0006`)—, así que anuncia y esto escucha. (El listado de
  propuestas es de esta app y lo limpia en su propia vista.)
- **El cierre de sesión.** La cola es de la sesión: sin sesión no hay
  nada que continuar. La señal es la de Django, no una nuestra, y por
  eso `registros` no tiene que saber que existimos.
"""

import logging

from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from apps.convocatorias.senales import se_abrio_el_catalogo

from .servicios import en_espera

logger = logging.getLogger(__name__)


@receiver(se_abrio_el_catalogo, dispatch_uid="evt_limpia_la_espera")
def _descartar_los_adjuntos_a_medio_subir(sender, persona=None, **kwargs):
    """Volver al catálogo es abandonar el formulario.

    ``dispatch_uid`` porque ``ready()`` puede correr más de una vez en
    algunos arranques, y sin él el receptor quedaría conectado dos veces
    y borraría dos veces lo mismo —inofensivo, pero duplica consultas en
    la pantalla más visitada de la feria—.

    **No falla nunca hacia arriba.** El catálogo es la portada de la
    feria y no puede caerse porque una limpieza de archivos temporales
    tenga un mal día; lo peor que pasa si esto revienta es que unos
    adjuntos provisionales sobrevivan un rato más.

    .. warning:: Este ``try`` no basta por sí solo, y creerlo costó caro

       En PostgreSQL una consulta fallida **aborta la transacción
       entera**: atrapar la excepción en Python no la deshace, y todo lo
       que venga después responde ``InFailedSqlTransaction``. Quien de
       verdad rescata la transacción es el ``atomic()`` que hay dentro
       de `en_espera`, que acota el fallo a un savepoint. Esto solo
       evita que la excepción suba.
    """
    try:
        en_espera.limpiar_la_feria(persona)
    except Exception:  # noqa: BLE001 — a propósito, ver el docstring
        logger.exception("No se pudo vaciar la espera de adjuntos de EVT")


@receiver(user_logged_out, dispatch_uid="evt_limpia_la_espera_al_salir")
def _descartar_al_cerrar_sesion(sender, user=None, request=None, **kwargs):
    """Sin sesión no hay formulario a medio llenar que continuar.

    Se conecta a la señal de Django y no a una nuestra: así
    `apps/registros` —que es quien cierra la sesión— no tiene que saber
    que este módulo existe, igual que no lo sabe `apps/convocatorias`.

    Corre **antes** de que la sesión se destruya, así que `request.user`
    todavía sirve. Lo que no se puede es apoyarse en el schema: cerrar
    sesión se hace desde el urlconf público, donde las tablas de `EVT` no
    existen. Por eso limpia por feria, recorriendo schemas.

    No falla nunca hacia arriba: que alguien no pueda cerrar sesión
    porque una limpieza de temporales tuvo un mal día sería mucho peor
    que unos archivos de más.

    .. warning:: Y eso pasó de verdad, con este mismo ``try`` puesto

       Una feria cuyo schema no tenía la tabla hacía fallar la consulta;
       el ``except`` la atrapaba y anotaba en el log, pero la transacción
       ya estaba abortada y el ``logout()`` de la línea siguiente no
       podía ni borrar la fila de la sesión. **Nadie podía cerrar
       sesión**, y el log solo hablaba de unos temporales.

       Lo que lo arregla es el ``atomic()`` de `en_espera`, que acota el
       fallo a un savepoint. Lo cazó
       `test_cerrar_sesion_del_admin_regresa_a_su_acceso`.
    """
    try:
        en_espera.limpiar_toda_la_plataforma(user)
    except Exception:  # noqa: BLE001 — a propósito, ver el docstring
        logger.exception("No se pudo vaciar la espera de adjuntos de EVT al salir")
