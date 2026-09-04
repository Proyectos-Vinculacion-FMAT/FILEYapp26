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

from comun.archivos import ArchivoNoDisponible, entregar

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
