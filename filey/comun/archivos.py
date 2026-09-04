"""
Entregar un archivo a quien ya demostró que puede verlo.

`ADR-0007` dejó lo que sube la gente **fuera de toda URL**: `MEDIA_URL`
no está montada en ningún urlconf. Son constancias fiscales, portadas
inéditas y comprobantes de personas identificadas; servirlos desde una
dirección estática los deja al alcance de cualquiera que la adivine.

Esto vive en `comun` y no en un dominio porque **la entrega no sabe de
qué dominio es el archivo**. Nació en `apps/stands/servicios/archivos.py`
—que sigue siendo el patrón de cómo se usa— y subió aquí cuando `EVT`
necesitó lo mismo para las portadas de una publicación: copiarla habría
dejado dos versiones de la misma decisión de seguridad, y la que se
corrige nunca es la copia. `eventos` no puede importar de `stands` de
todas formas (regla 4 de `CLAUDE.md`: nunca en círculo entre hermanos).

Lo que **no** sube aquí es quién puede ver qué: eso depende de de quién
cuelga el archivo, y eso sí es del dominio. Cada uno se queda con su
``puede_ver``.
"""

import logging
import mimetypes

from django.conf import settings
from django.http import FileResponse, HttpResponseRedirect

logger = logging.getLogger(__name__)

#: Con qué `Content-Type` se sirve algo cuya extensión no reconocemos.
#: Es lo que fuerza al navegador a guardarlo en vez de interpretarlo.
TIPO_DESCONOCIDO = "application/octet-stream"


class ArchivoNoDisponible(Exception):
    """La fila existe y el archivo no.

    Pasa cuando el almacén perdió el fichero pero la fila sigue: un
    volumen que no se montó, una restauración a medias, un borrado
    manual. Es una excepción propia y no un `FileNotFoundError` suelto
    porque quien llama tiene que poder distinguirla de "no tienes
    permiso" — son el mismo 404 en la respuesta y dos incidencias
    distintas en el log.
    """


def entregar(documento):
    """La respuesta que lleva el archivo. **No comprueba permisos.**

    Eso lo hace el ``puede_ver`` de cada dominio, y están separadas a
    propósito: una función que decide y entrega a la vez es una que
    alguien puede llamar saltándose la mitad sin que se note.

    Recibe cualquier fila que tenga ``archivo`` (un `FileField`) y
    ``nombre_original``; no importa de qué app sea. Es lo que permite que
    `STD` y `EVT` compartan la entrega teniendo tablas distintas.

    Hay **una sola decisión y dos entregas**, elegidas por la misma
    variable que `ADR-0007`: con ``s3`` se firma una URL con caducidad y
    el archivo no pasa por Django; con ``local`` Django lee y transmite.
    Quien llama no cambia, así que el día que haya bucket la mejora entra
    sola con la variable de entorno.
    """
    if settings.ALMACENAMIENTO == "s3":
        # `django-storages` firma la URL con caducidad porque `ADR-0007`
        # deja `querystring_auth` activado. El bucket es privado: sin
        # firma, esa URL no sirve para nada.
        return HttpResponseRedirect(documento.archivo.url)

    nombre = documento.nombre_original or documento.archivo.name
    tipo, _ = mimetypes.guess_type(nombre)

    # Sin esto, un archivo que ya no está en el almacén levantaba
    # `FileNotFoundError` dentro de la vista y salía un 500: quien
    # revisaba se encontraba una página de error del servidor en vez de
    # una incidencia sobre **ese** documento, y el resto de la revisión
    # quedaba interrumpida.
    try:
        contenido = documento.archivo.open("rb")
    except FileNotFoundError as exc:
        logger.error(
            "El documento %s (%s) no está en el almacén: %s",
            documento.pk,
            documento.archivo.name,
            exc,
        )
        raise ArchivoNoDisponible("Este documento ya no está disponible.") from exc

    respuesta = FileResponse(
        contenido,
        # `as_attachment=False` para que un PDF se vea en el navegador:
        # quien revisa abre cuatro documentos seguidos y descargarlos
        # todos es peor. La lista blanca de extensiones de
        # `comun/almacenamiento.py` es lo que hace que esto sea seguro —
        # sin ella, un `.html` subido sería XSS en nuestro propio origen.
        as_attachment=False,
        filename=nombre,
        content_type=tipo or TIPO_DESCONOCIDO,
    )
    # Cinturón además del tirante: aunque un archivo se colara con una
    # extensión inocente y contenido de otra cosa, el navegador no debe
    # adivinar el tipo ni ejecutar nada de lo que venga dentro.
    respuesta["X-Content-Type-Options"] = "nosniff"
    respuesta["Content-Security-Policy"] = "sandbox; default-src 'none'"
    # Es un documento de una persona concreta: no lo cachea ningún
    # intermediario.
    respuesta["Cache-Control"] = "private, no-store"
    return respuesta
