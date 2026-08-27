"""
Dónde cae cada archivo que alguien sube (`ADR-0007`).

Ningún `FileField` del proyecto escribe su `upload_to` a mano: usa
`CarpetaDeLaFeria`. Dos motivos, y los dos son difíciles de arreglar
después:

**La feria también separa los archivos.** `ADR-0003` dice que cada
edición vive en su propio schema, pero un `upload_to="documentos/"` deja
los archivos de todas las ediciones en la misma carpeta. La base estaría
aislada y el disco no. Poner el schema por delante hace que el
aislamiento llegue igual de lejos que en la base — y en un almacén S3 el
prefijo es exactamente lo que permite dar credenciales acotadas a una
feria si algún día hace falta.

**El nombre original no se conserva.** Trae dos problemas de golpe: dice
cosas de quien lo subió (``RFC_JUAN_PEREZ_2019.pdf`` está lleno de datos
personales antes de abrirlo) y es adivinable. Se sustituye por un UUID.

Lo que queda es::

    feria_2027/solicitudes/9f2c…a1.pdf

.. warning:: Esto se congela en la primera migración que lo use

   ``upload_to`` viaja dentro de las migraciones, así que cambiar el
   esquema de rutas más adelante no reescribe lo ya guardado: deja los
   archivos viejos donde estaban y los nuevos en otro sitio. Si hay que
   cambiarlo, se cambia con una migración de datos que mueva los
   archivos, no editando esta clase.
"""

from pathlib import PurePosixPath
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import connection
from django.utils.deconstruct import deconstructible

#: Longitud máxima que se conserva de la extensión original. Un nombre
#: como `acta.pdf.exe.…` no debe poder alargar la ruta indefinidamente.
LARGO_MAXIMO_EXTENSION = 10


@deconstructible
class CarpetaDeLaFeria:
    """`upload_to` que guarda bajo el schema de la feria activa.

    Se usa así::

        comprobante = models.FileField(
            upload_to=CarpetaDeLaFeria("comprobantes"),
        )

    Es una clase y no una función que devuelve otra función porque
    ``upload_to`` se serializa dentro de las migraciones, y Django no
    sabe serializar un cierre. ``@deconstructible`` es lo que hace que
    en la migración aparezca ``CarpetaDeLaFeria('comprobantes')``.
    """

    def __init__(self, subcarpeta: str):
        self.subcarpeta = subcarpeta.strip("/")

    def __call__(self, instancia, nombre_original: str) -> str:
        """La ruta relativa dentro del almacén.

        Se pregunta por ``connection.schema_name`` y no por
        ``connection.tenant`` por lo mismo que en los servicios de
        `apps/convocatorias`: ``schema_context()`` deja ahí un
        ``FakeTenant``, y el nombre del schema siempre es el de verdad.
        """
        extension = PurePosixPath(nombre_original or "").suffix.lower()
        if len(extension) > LARGO_MAXIMO_EXTENSION:
            extension = ""
        return f"{connection.schema_name}/{self.subcarpeta}/{uuid4().hex}{extension}"

    def __eq__(self, otro):
        # Lo necesita `makemigrations`: sin esto, cada ejecución vería
        # dos instancias distintas donde hay la misma ruta y generaría
        # una migración `AlterField` que no cambia nada.
        return (
            isinstance(otro, CarpetaDeLaFeria) and otro.subcarpeta == self.subcarpeta
        )

    def __hash__(self):
        return hash((type(self), self.subcarpeta))

    def __repr__(self):
        return f"CarpetaDeLaFeria({self.subcarpeta!r})"


#: Qué se admite subir. Es una lista blanca y no una negra a propósito:
#: una negra deja pasar todo lo que nadie pensó en prohibir.
#:
#: `.html` y `.svg` **no están, y es la razón de ser de esta lista**. Los
#: documentos se entregan desde nuestro propio origen, así que un HTML
#: subido y servido en línea es XSS almacenado con nuestras cookies
#: detrás. Un SVG es un documento XML que puede traer `<script>`.
EXTENSIONES_ADMITIDAS = frozenset(
    {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".doc", ".docx", ".odt"}
)

#: 10 MB. Una constancia fiscal son dos páginas; una lista de títulos,
#: unas pocas más. Lo que esto corta no son documentos grandes: son
#: subidas que llenarían el disco del contenedor (`ADR-0007`).
TAMANO_MAXIMO_BYTES = 10 * 1024 * 1024


@deconstructible
class DocumentoAdmisible:
    """Valida un archivo subido: extensión de la lista blanca y tamaño.

    Va en el `FileField` y no en el formulario para que valga también
    desde el shell, desde el admin y desde cualquier comando — es la
    regla 3 de `CLAUDE.md` aplicada a un validador.
    """

    def __init__(self, extensiones=None, maximo_bytes=TAMANO_MAXIMO_BYTES):
        self.extensiones = frozenset(extensiones or EXTENSIONES_ADMITIDAS)
        self.maximo_bytes = maximo_bytes

    def __call__(self, archivo):
        extension = PurePosixPath(archivo.name or "").suffix.lower()
        if extension not in self.extensiones:
            admitidas = ", ".join(sorted(self.extensiones))
            raise ValidationError(
                f"«{extension or "sin extensión"}» no se admite. "
                f"Sube uno de estos: {admitidas}."
            )
        tamano = getattr(archivo, "size", None)
        if tamano is not None and tamano > self.maximo_bytes:
            megas = self.maximo_bytes / (1024 * 1024)
            raise ValidationError(f"El archivo pasa de {megas:.0f} MB.")

    def __eq__(self, otro):
        return (
            isinstance(otro, DocumentoAdmisible)
            and otro.extensiones == self.extensiones
            and otro.maximo_bytes == self.maximo_bytes
        )

    def __hash__(self):
        return hash((type(self), self.extensiones, self.maximo_bytes))
