"""
Quién alcanza un adjunto de `EVT`.

La **entrega** —transmitir con `FileResponse` o firmar una URL de S3, y
las cabeceras que hacen que eso sea seguro— vive en `comun/archivos.py`:
es la misma decisión de `ADR-0007` para todo el sistema y no puede tener
dos copias. Lo que se queda aquí es lo único que sí es del dominio: **de
quién es un documento**, que depende de las tablas de `EVT`.

Es el mismo reparto que en `apps/stands/servicios/archivos.py`, y no
podría ser una sola función compartida: el camino de un documento hasta
su dueño es distinto en cada dominio.

Los dos nombres de `comun` se reexportan a propósito, para que la vista
de esta app llame `archivos.entregar(...)` y atrape
`archivos.ArchivoNoDisponible` sin tener que saber en qué capa acabó cada
mitad.
"""

from apps.ferias.permisos import administra

from comun.archivos import ArchivoNoDisponible
from comun.archivos import entregar as _entregar

from ..models import Documento

__all__ = ["ArchivoNoDisponible", "entregar", "puede_ver"]


def puede_ver(peticion, documento: Documento) -> bool:
    """Quién alcanza un documento: quien lo subió y quien administra la feria.

    No hace falta comprobar la edición: el documento vive en el schema de
    su feria (`ADR-0003`), así que uno de 2027 no es alcanzable desde
    `/f/2028/` — la consulta no lo encuentra.

    ``administra`` es la misma función que usan los decoradores y las
    pantallas, así que cuenta también al operador de la plataforma
    (`ADR-0005`). Que sea la misma es lo que evita tener dos respuestas
    distintas a "¿administra ésta?".
    """
    usuario = getattr(peticion, "user", None)
    if usuario is None or not usuario.is_authenticated:
        return False
    if administra(peticion):
        return True
    return _de_quien_es(documento) == usuario.pk


def _de_quien_es(documento: Documento):
    """La persona de la que es este documento.

    Se llega por la cadena completa —documento → actividad → solicitud →
    registro → persona— y no por ``subido_por``, que es quién apretó el
    botón. Hoy son la misma cuenta siempre, pero no es lo mismo: el día
    que un administrador suba una portada que faltaba, ``subido_por``
    diría que el archivo es suyo y le quitaría el acceso a quien propuso.
    De quién es un adjunto lo decide de qué propuesta cuelga.
    """
    return documento.actividad.solicitud.registro.persona_id


#: La política con la que salen **los adjuntos de `EVT`**, y solo ellos.
#:
#: Un `sandbox` a secas deja el documento en un origen opaco, y el visor
#: de PDF integrado del navegador trata eso como contenido ajeno: se
#: niega a pintarlo dentro de un marco, y `CU-EVT-003` lo enseña dentro
#: de su propia pantalla (`ADR-0010`).
#:
#: **`allow-same-origin` no habilita ejecución.** Sigue sin
#: `allow-scripts` —el token que encendería JavaScript—, sin
#: `allow-forms`, sin `allow-popups` y sin `allow-top-navigation`. Sin
#: scripts no hay nada que pueda leer el origen recuperado.
CSP_DEL_VISOR = "sandbox allow-same-origin; default-src 'none'"


def entregar(documento: Documento):
    """La respuesta que lleva el archivo. **No comprueba permisos.**

    Envuelve la de `comun/archivos.py` para fijar la política de este
    dominio. `STD` no la comparte: sus constancias fiscales no se
    incrustan en ninguna pantalla y conservan la cerrada.
    """
    return _entregar(documento, csp=CSP_DEL_VISOR)
