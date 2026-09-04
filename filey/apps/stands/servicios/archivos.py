"""
Quién alcanza un adjunto de `STD`.

La **entrega** —transmitir con `FileResponse` o firmar una URL de S3, y
las cabeceras que hacen que eso sea seguro— vive en `comun/archivos.py`
desde que `EVT` necesitó lo mismo: es la misma decisión de `ADR-0007` y
no puede tener dos copias, porque la que se corrige nunca es la copia.

Lo que se queda aquí es lo único que sí es del dominio: **de quién es un
documento**. Eso depende de las tablas de `STD` y no se puede generalizar
sin inventar un contrato que ninguna otra app cumpliría.

Los dos nombres de `comun` se reexportan a propósito. Las vistas y las
pruebas de esta app llaman `archivos.entregar(...)` y atrapan
`archivos.ArchivoNoDisponible`, y esa sigue siendo la forma correcta de
usarlo desde `STD`: quien está en el dominio no debería tener que saber
en qué capa acabó cada mitad.
"""

from apps.ferias.permisos import administra

from comun.archivos import ArchivoNoDisponible, entregar

from ..models import Documento

__all__ = ["ArchivoNoDisponible", "entregar", "puede_ver"]


def puede_ver(peticion, documento: Documento) -> bool:
    """Quién alcanza un documento: su dueño y quien administra la feria.

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
    """La persona de la que es este documento, o ``None``.

    Se miran **las dos** ramas que la restricción
    ``un_documento_cuelga_de_exactamente_una_entidad`` admite. Mirar solo
    `editorial` dejaba al dueño de un documento colgado de una solicitud
    sin poder abrir lo que él mismo subió, mientras quien administra sí lo
    veía. Hoy no hay ninguno así —todo cuelga de la editorial—, pero el
    modelo anuncia la forma y la fase de pago la va a usar para los
    comprobantes.
    """
    if documento.editorial_id is not None:
        return documento.editorial.persona_id
    if documento.solicitud_id is not None:
        return documento.solicitud.registro.persona_id
    return None
