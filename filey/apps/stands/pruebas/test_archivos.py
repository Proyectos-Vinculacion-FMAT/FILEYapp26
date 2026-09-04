"""
Entregar un adjunto (`ADR-0007`, `CU-STD-005`).

`MEDIA_URL` no está montada en ningún urlconf, así que esta vista es **la
única forma** de alcanzar un archivo. Eso la convierte en la puerta
entera, y lo que se vigila aquí es que sea una puerta y no un pasillo:

1. **Quién pasa.** El dueño del expediente y quien administra la feria.
   Nadie más, y quien no pasa recibe un 404 — un 403 confirmaría que ese
   documento existe.
2. **Que un `.html` no llegue a subirse.** Los archivos se sirven desde
   nuestro propio origen: un HTML servido en línea sería XSS almacenado
   con nuestras cookies detrás. La lista blanca de extensiones es lo que
   lo impide, y por eso es una prueba de seguridad y no de formato.
3. **Que con almacén de objetos el archivo no pase por Django.** Es la
   mitad de `ADR-0007` que hoy no se ejerce y que hay que dejar probada
   antes de que haya bucket, no después.
"""

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona
from comun.almacenamiento import DocumentoAdmisible

from ..models import Documento
from . import fabricas

pytestmark = pytest.mark.django_db


@pytest.fixture
def adjunto(feria_2027):
    """Una editorial con su constancia fiscal subida."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        ficha = fabricas.editorial(ana)
        doc = ficha.documentos.create(
            tipo=Documento.Tipo.CONSTANCIA_FISCAL,
            archivo=SimpleUploadedFile("csf.pdf", b"%PDF-1.4 secreto"),
            nombre_original="csf.pdf",
        )
    return feria_2027, ana, doc


def _url(feria, doc):
    """Ver la nota del mismo helper en `test_pantallas.py`."""
    return f"{feria.url.rstrip('/')}" + reverse(
        "stands:documento",
        kwargs={"documento_id": doc.pk},
        urlconf=settings.ROOT_URLCONF,
    )


# ── Quién pasa ────────────────────────────────────────────────


def test_el_dueno_abre_su_documento(client, adjunto):
    feria, ana, doc = adjunto
    client.force_login(ana)

    respuesta = client.get(_url(feria, doc))

    assert respuesta.status_code == 200
    assert b"secreto" in b"".join(respuesta.streaming_content)


def test_quien_administra_la_feria_lo_abre(client, adjunto):
    """Sin esto no se puede revisar una solicitud (`CU-STD-005` paso 4)."""
    feria, _, doc = adjunto
    admin = Persona.objects.create_user(
        correo="rita@filey.org", nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=admin, es_dueno=False)
    client.force_login(admin)

    assert client.get(_url(feria, doc)).status_code == 200


def test_otro_participante_no_lo_alcanza(client, adjunto):
    """404 y no 403: un 403 confirmaría que ese documento existe."""
    feria, _, doc = adjunto
    with schema_context(feria.schema_name):
        intruso = fabricas.persona(correo="beto@ejemplo.com", nombre="Beto")
    client.force_login(intruso)

    assert client.get(_url(feria, doc)).status_code == 404


def test_administrar_otra_feria_no_abre_los_de_esta(client, adjunto, feria_2028):
    feria, _, doc = adjunto
    ajeno = Persona.objects.create_user(
        correo="beto@filey.org", nombre="Beto", primer_apellido="Chan"
    )
    # `es_dueno=False`: la feria ya nace con su dueño en el alta, y solo
    # cabe uno por edición.
    AdminFeria.objects.create(feria=feria_2028, persona=ajeno, es_dueno=False)
    client.force_login(ajeno)

    assert client.get(_url(feria, doc)).status_code == 404


def test_sin_sesion_manda_al_acceso(client, adjunto):
    feria, _, doc = adjunto

    respuesta = client.get(_url(feria, doc))

    assert respuesta.status_code == 302
    assert respuesta.url == "/acceso/"


def test_un_documento_de_otra_feria_no_existe_aqui(client, adjunto, feria_2028):
    """El aislamiento lo da el schema, no un filtro (`ADR-0003`)."""
    feria, ana, doc = adjunto
    client.force_login(ana)

    url_en_2028 = (
        f"{feria_2028.url.rstrip('/')}/stands/documento/{doc.pk}/"
    )

    assert client.get(url_en_2028).status_code == 404


# ── Cómo se entrega ───────────────────────────────────────────


def test_el_archivo_no_se_deja_interpretar_por_el_navegador(client, adjunto):
    """La segunda línea de defensa tras la lista blanca.

    Aunque un archivo se colara con extensión inocente y contenido de
    otra cosa, el navegador no debe adivinar el tipo ni ejecutar nada.
    """
    feria, ana, doc = adjunto
    client.force_login(ana)

    respuesta = client.get(_url(feria, doc))

    assert respuesta["X-Content-Type-Options"] == "nosniff"
    assert "no-store" in respuesta["Cache-Control"]

    # La cabecera **completa y exacta**, no un `in`. El 2026-09-03 `EVT`
    # necesitó relajar el `sandbox` para enseñar un PDF dentro de su
    # pantalla, y como la entrega se había compartido, se lo relajó de
    # paso a estas constancias fiscales — que no lo pidieron ni lo
    # necesitan. Un `assert "sandbox" in ...` lo cumplen las dos
    # políticas, así que no se enteró nadie.
    #
    # Ahora cada dominio decide la suya (`comun/entrega.py`), y `STD`
    # conserva la cerrada: sus documentos no se incrustan en ninguna
    # parte.
    assert respuesta["Content-Security-Policy"] == "sandbox; default-src 'none'"
    assert "allow-same-origin" not in respuesta["Content-Security-Policy"]

    # Y sigue sin poder embeberse en ningún sitio: `SAMEORIGIN` es de la
    # vista de `EVT`, que sí lo necesita.
    assert respuesta.get("X-Frame-Options", "DENY") == "DENY"


def test_con_almacen_de_objetos_el_archivo_no_pasa_por_django(
    client, adjunto, settings, monkeypatch
):
    """La mitad de `ADR-0007` que todavía no se ejerce.

    Con bucket, Django comprueba el permiso y redirige a una URL firmada
    con caducidad; los bytes no lo atraviesan. Se prueba ahora y no
    cuando haya bucket, porque para entonces el cambio será una variable
    de entorno y nadie va a releer esta vista.
    """
    feria, ana, doc = adjunto
    settings.ALMACENAMIENTO = "s3"
    monkeypatch.setattr(
        type(doc.archivo),
        "url",
        property(lambda self: "https://bucket.example/firma?X-Amz-Expires=300"),
    )
    client.force_login(ana)

    respuesta = client.get(_url(feria, doc))

    assert respuesta.status_code == 302
    assert respuesta.url.startswith("https://bucket.example/")


# ── Qué se admite subir ───────────────────────────────────────


@pytest.mark.parametrize("nombre", ["evil.html", "logo.svg", "script.js", "sin_extension"])
def test_no_se_admite_lo_que_el_navegador_ejecutaria(nombre):
    """La razón de que la lista sea blanca y no negra.

    Un `.html` subido y servido desde nuestro origen es XSS almacenado.
    Un `.svg` es XML y puede traer `<script>`. Con una lista negra, el
    siguiente formato peligroso entra solo.
    """
    with pytest.raises(ValidationError):
        DocumentoAdmisible()(SimpleUploadedFile(nombre, b"<script>alert(1)</script>"))


@pytest.mark.parametrize("nombre", ["acta.pdf", "ACTA.PDF", "foto.jpg", "ficha.docx"])
def test_lo_que_manda_una_editorial_si_se_admite(nombre):
    DocumentoAdmisible()(SimpleUploadedFile(nombre, b"contenido"))


def test_un_archivo_enorme_se_rechaza():
    """Lo que esto corta no son documentos: es llenar el disco."""
    grande = SimpleUploadedFile("acta.pdf", b"x" * (11 * 1024 * 1024))

    with pytest.raises(ValidationError):
        DocumentoAdmisible()(grande)


def test_el_validador_es_serializable_en_una_migracion():
    """Va en el `FileField`, así que viaja dentro de las migraciones."""
    ruta, args, kwargs = DocumentoAdmisible().deconstruct()

    assert ruta == "comun.almacenamiento.DocumentoAdmisible"
    assert DocumentoAdmisible() == DocumentoAdmisible()


def test_el_formulario_rechaza_un_html(client, feria_2027):
    """Y no solo el modelo: es donde de verdad llega el intento."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    url = f"{feria_2027.url.rstrip('/')}" + reverse(
        "stands:solicitud",
        kwargs={"convocatoria_id": conv.pk},
        urlconf=settings.ROOT_URLCONF,
    )
    respuesta = client.post(
        url,
        {
            **fabricas.FICHA,
            "materiales": ["Libro"],
            "tematicas": ["Literatura"],
            "constancia_fiscal": SimpleUploadedFile(
                "csf.html", b"<script>alert(1)</script>"
            ),
            "lista_titulos": SimpleUploadedFile("titulos.pdf", b"%PDF"),
        },
    )

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        assert not Documento.objects.exists()
