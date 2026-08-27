"""
El admin de Django **de dentro de una feria** — `/f/<slug>/django-admin/`.

Existe porque el admin de siempre no puede servir el contenido de una
feria, y el motivo es el mismo que ordena todo el sistema:

    /django-admin/            search_path = [public]
                              ve Feria, AdminFeria, Persona, SesionOTP

    /f/2027/django-admin/     search_path = [feria_2027, public]
                              ve Convocatoria — y, cuando existan, EVT,
                              TAL, STD, VIS, PRG y SAL

Una app de `TENANT_APPS` **no tiene tabla en `public`** (`ADR-0003`), así
que registrar `Convocatoria` en el `admin.site` de siempre no da un
error de configuración: da una entrada que se ve bien en el índice y
revienta con `relation "..." does not exist` al abrirla. Por eso hay dos
sitios y no uno con excepciones.

Es la tercera vez que el proyecto parte algo en dos por esta misma
frontera, y las tres se leen igual: dos urlconfs (`config/urls_feria.py`
frente a `config/urls_publicas.py`), dos namespaces (`accesos:` frente a
`ferias:`) y ahora dos sitios de admin. Lo de dentro de una feria nunca
resuelve contra lo de fuera.

> [!warning] Registrar un modelo en el sitio equivocado no falla al arrancar
> Falla cuando alguien abre la pantalla, que puede ser semanas después.
> La regla es mecánica y no admite criterio: **si la app está en
> `TENANT_APPS`, su `admin.py` registra en `admin_feria`; si está en
> `SHARED_APPS`, en `admin.site`.**

> [!note] Vive en `comun/` y no en un dominio
> Lo van a compartir todos los módulos por feria que faltan. `comun` no
> conoce dominios —solo la frontera—, que es exactamente lo que este
> archivo necesita saber.
"""

from django.contrib.admin import AdminSite
from django.db import connection
from django_tenants.utils import get_public_schema_name


def feria_activa(peticion):
    """La feria de esta petición, o `None` si no estamos dentro de una.

    `peticion.tenant` lo pone `TenantSubfolderMiddleware`. Fuera de
    `/f/<slug>/` ahí queda la fila de sistema, que no es una feria (ver
    `apps/ferias/models.py`), y pintar su nombre en la cabecera sería
    anunciar una edición llamada «(sistema)».
    """
    if connection.schema_name == get_public_schema_name():
        return None
    feria = getattr(peticion, "tenant", None)
    if feria is None or getattr(feria, "es_la_de_sistema", False):
        return None
    return feria


class AdminDeFeria(AdminSite):
    """Admin de una edición. Mismo mecanismo, otro alcance.

    No filtra nada por feria y no le hace falta: lo que ve depende del
    `search_path` que dejó el middleware, no de un `WHERE`. Escribir una
    convocatoria desde `/f/2027/django-admin/` la deja en `feria_2027`
    porque es el único schema donde esa tabla existe.
    """

    site_title = "FILEY · edición"
    index_title = "Contenido de esta edición"
    # Sobra en el índice: enlaza a `/f/<slug>/`, que es el catálogo
    # público de la propia feria, y así se vuelve a lo que ve la gente.
    site_url = "/"

    def has_permission(self, peticion):
        """`is_staff`, y estar dentro de una feria de verdad.

        Es el mismo techo que `/django-admin/`: esto es la herramienta
        interna del equipo técnico, no el panel del dueño. Mientras el
        alta de convocatorias viva aquí, quien la ejecuta es el operador
        de la plataforma y no el dueño de la feria — desviación
        deliberada y temporal respecto de CU-FER-005, que se cierra
        cuando exista la pantalla del panel.

        **No se exige que la feria esté sin archivar.** Consultar una
        edición archivada es legítimo (ver
        `apps/ferias/servicios/seleccion.py`); lo que no se puede es
        abrirle convocatorias nuevas, y eso lo veta el servicio de alta
        (CU-FER-005 E2), no la puerta.
        """
        usuario = getattr(peticion, "user", None)
        if usuario is None or not (usuario.is_active and usuario.is_staff):
            return False
        return feria_activa(peticion) is not None

    def each_context(self, peticion):
        """Pone el nombre de la edición en la cabecera.

        No es decoración. Dos pestañas de este admin en dos ferias
        distintas son idénticas píxel a píxel, y escriben en schemas
        distintos: la cabecera es la única señal de en cuál se está.
        """
        contexto = super().each_context(peticion)
        feria = feria_activa(peticion)
        if feria is not None:
            contexto["site_header"] = f"{feria.nombre} · administración"
            contexto["site_title"] = f"FILEY · {feria.slug}"
        return contexto


#: El sitio que montan `config/urls_feria.py` y los `admin.py` de las
#: apps por feria. El `name` es el namespace: `reverse()` sobre él
#: devuelve la URL ya con su prefijo `/f/<slug>/`.
admin_feria = AdminDeFeria(name="admin_feria")
