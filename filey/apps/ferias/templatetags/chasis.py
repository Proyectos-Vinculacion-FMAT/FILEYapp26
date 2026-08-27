"""
La barra superior de todas las pantallas posteriores al acceso.

Está en `ferias` y no en `comun` porque todo lo que la barra decide es
sobre ferias: en cuál estamos, cuántas puede ver quien mira, y si la
administra. `comun` no conoce dominios, y no debería empezar aquí.

La plantilla sí vive en `plantillas/componentes/topbar.html`, con el
resto del chasis compartido: la barra la dibujan pantallas de varias
apps, y separarla ahí es lo que evita que cada una la maquete otra vez.

> [!note] Es un *inclusion tag* y no un context processor
> Un context processor cobraría sus consultas en **toda** plantilla,
> incluidas las de acceso, que no dibujan barra. Así solo paga quien la
> pinta, y una sola vez por página.
"""

from django import template

from comun.urls import url_publica

from .. import permisos
from ..servicios import seleccion

register = template.Library()


@register.inclusion_tag("componentes/topbar.html", takes_context=True)
def topbar(context):
    """Arma la barra según quién mira y desde dónde.

    Tres estados, y los tres se dan en la misma pantalla —el catálogo de
    una feria, que es público (CU-FER-006, A1)—:

    ============= =========================================================
    Anónimo       Marca y un botón de entrar. No hay sesión que cerrar.
    Participante  Chip de identidad y, si hay más de una feria, cambiar.
    Administrador Variante azul oscuro y la vuelta a "mis ferias".
    ============= =========================================================

    Todos los enlaces se resuelven con ``url_publica``: la barra se
    dibuja también dentro de ``/f/<slug>/``, donde ``{% url %}`` no
    encuentra los nombres del urlconf público.
    """
    peticion = context.get("request")
    usuario = getattr(peticion, "user", None)
    autenticada = usuario is not None and usuario.is_authenticated

    feria = getattr(peticion, "tenant", None)
    if feria is not None and feria.es_la_de_sistema:
        # La fila de sistema no es una feria: fuera de `/f/<slug>/` el
        # middleware deja esa, y pintarla sería anunciar una edición
        # llamada «(sistema)».
        feria = None

    # `administra` y no `acceso_a`: el operador de la plataforma no tiene
    # fila en `AdminFeria` y aun así ve la feria como quien la administra
    # (`ADR-0005`). Si la barra preguntara distinto que el decorador, un
    # superusuario vería el chasis de participante sobre pantallas de
    # administración.
    #
    # `zona_admin` del contexto es lo que usan las pantallas de fuera de
    # una feria —"mis ferias"—, donde no hay `tenant` contra el que
    # comprobar nada.
    zona_admin = (
        autenticada and permisos.administra(peticion)
    ) or bool(context.get("zona_admin"))

    return {
        "usuario": usuario,
        "autenticada": autenticada,
        "feria": feria,
        "zona_admin": zona_admin,
        "titulo": feria.nombre if feria else "FILEY",
        "subtitulo": _subtitulo(feria, zona_admin, autenticada),
        "url_inicio": _url_inicio(feria, zona_admin),
        "url_salir": url_publica("registros:salir"),
        "url_acceso": url_publica("registros:acceso"),
        "cambio": _cambio_de_feria(feria, zona_admin, usuario, autenticada),
    }


def _subtitulo(feria, zona_admin, autenticada):
    if zona_admin:
        return "Panel de administración"
    if feria:
        return "Convocatorias de esta edición"
    return "Portal del participante" if autenticada else "FILEY"


def _url_inicio(feria, zona_admin):
    if feria:
        return feria.url
    return url_publica("ferias:mis_ferias" if zona_admin else "ferias:elegir")


def _cambio_de_feria(feria, zona_admin, usuario, autenticada):
    """El enlace de vuelta a la lista de ferias, o ``None``.

    Existe porque la pantalla de selección **se salta cuando solo hay
    una feria** (CU-FER-010): sin esta puerta, quien entró cuando solo
    había una no encontraría la segunda el día que se cree.

    Por eso mismo solo se ofrece desde **dentro** de una feria y solo si
    hay a dónde ir: en la propia lista sobraría, y con una sola feria el
    enlace rebotaría a donde ya se está.
    """
    if feria is None or not autenticada:
        return None

    if zona_admin:
        if seleccion.ferias_administradas(usuario).count() < 2:
            return None
        return {"texto": "Mis ferias", "url": url_publica("ferias:mis_ferias")}

    if seleccion.ferias_para_participante().count() < 2:
        return None
    return {"texto": "Cambiar de feria", "url": url_publica("ferias:elegir")}
