"""
Entregar un documento a quien tiene derecho a verlo.

`ADR-0007` dejó los archivos **fuera de toda URL**: no hay ruta para
`MEDIA_URL` en ningún urlconf, y es deliberado. Son actas constitutivas,
RFC y comprobantes de pago de personas identificadas; servirlos desde una
dirección estática los deja al alcance de cualquiera que la tenga o la
adivine, sin pasar por ninguna comprobación.

Así que hay que ponerlos de vuelta en circulación, y la pregunta es **por
dónde pasan los bytes**. Django tiene que estar en el camino de la
decisión; no necesariamente en el del archivo:

+----------------------+------------------------------------------------+
| ``X-Accel-Redirect`` | Lo correcto con un nginx delante — Django       |
|                      | comprueba y el servidor web sirve. **No lo      |
|                      | tenemos:** el servicio corre `gunicorn` directo |
|                      | y el proxy de Render no interpreta la cabecera. |
+----------------------+------------------------------------------------+
| URL firmada          | Con almacén de objetos: se comprueba y se       |
|                      | redirige a una URL con caducidad que genera el  |
|                      | bucket. El archivo **no pasa por Django**.      |
+----------------------+------------------------------------------------+
| ``FileResponse``     | Django lee y transmite. Ocupa un worker         |
|                      | mientras dura, y funciona siempre.              |
+----------------------+------------------------------------------------+

Lo que hay aquí es **una sola decisión y dos entregas**, elegidas por la
misma variable que `ADR-0007`: con `local` se transmite, con `s3` se
firma. Quien llama no cambia, así que el día que haya bucket la mejora
entra sola con la variable de entorno.
"""

import mimetypes

from django.conf import settings
from django.http import FileResponse, HttpResponseRedirect

from apps.ferias.permisos import administra

from ..models import Documento

#: Con qué `Content-Type` se sirve algo cuya extensión no reconocemos.
#: Es lo que fuerza al navegador a guardarlo en vez de interpretarlo.
TIPO_DESCONOCIDO = "application/octet-stream"


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


def entregar(documento: Documento):
    """La respuesta que lleva el archivo. **No comprueba permisos.**

    Eso lo hace `puede_ver`, y están separadas a propósito: una función
    que decide y entrega a la vez es una que alguien puede llamar
    saltándose la mitad sin que se note.
    """
    if settings.ALMACENAMIENTO == "s3":
        # `django-storages` firma la URL con caducidad porque `ADR-0007`
        # deja `querystring_auth` activado. El bucket es privado: sin
        # firma, esa URL no sirve para nada.
        return HttpResponseRedirect(documento.archivo.url)

    nombre = documento.nombre_original or documento.archivo.name
    tipo, _ = mimetypes.guess_type(nombre)

    respuesta = FileResponse(
        documento.archivo.open("rb"),
        # `as_attachment=False` para que un PDF se vea en el navegador:
        # quien revisa una solicitud abre cuatro documentos seguidos y
        # descargarlos todos es peor. La lista blanca de extensiones de
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
