"""
El alta de una propuesta (`CU-EVT-002`), sin pasar por HTTP.

Lo que se vigila aquí es lo que ninguna pantalla puede garantizar:

1. **El registro nace con la propuesta.** Si naciera al pulsar el botón
   del catálogo, los conteos contarían gente que nunca propuso.
2. **`E1`: con la convocatoria cerrada no se crea nada.** Ni la
   solicitud, ni la actividad, ni el registro — el CU lo dice con esas
   palabras.
3. **La invariante del tipo.** Nada en el esquema impide colgar una
   propuesta de eventos de un registro de una convocatoria de stands.
4. **En `EVT` se proponen varias.** A diferencia de `STD`, no hay una
   sola solicitud viva por registro: el paso 14 ofrece «crear otra».
"""

import pytest
from django_tenants.utils import schema_context

from apps.convocatorias.models import (
    Convocatoria,
    RegistroConvocatoria,
    TipoConvocatoria,
)

from ..models import (
    ActividadConversatorio,
    ActividadPresentacionLibro,
    ConfiguracionConvocatoria,
    Documento,
    Solicitud,
)
from ..servicios import catalogo, configuracion, seguimiento, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db

CONVERSATORIO = {
    "nombre_participante_1": "Elena Poniatowska",
    "semblanza_participante_1": "Escritora y periodista.",
}


# ── El alta ───────────────────────────────────────────────────


def test_la_propuesta_trae_consigo_su_registro(feria_2027):
    """Antes de enviar no hay inscripción; después, exactamente una."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        assert RegistroConvocatoria.objects.count() == 0

        propuesta = solicitudes.crear(
            convocatoria=convocatoria,
            persona=persona,
            comunes=fabricas.PROPUESTA,
            nombre_tipo="conversatorio",
            detalle=CONVERSATORIO,
        )

        assert RegistroConvocatoria.objects.count() == 1
        assert propuesta.registro.persona == persona
        # Nace en `pendiente` por el valor por omisión de la columna.
        assert propuesta.estado == Solicitud.Estado.PENDIENTE
        assert propuesta.actividad.tipo.nombre == "conversatorio"
        assert propuesta.actividad.detalle.nombre_participante_1 == "Elena Poniatowska"


def test_varias_propuestas_cuelgan_del_mismo_registro(feria_2027):
    """`EVT` no es `STD`: aquí se proponen varias actividades.

    El paso 14 del CU ofrece «crear una nueva solicitud», así que una
    regla de «una viva por registro» rompería el flujo principal.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()

        primera = solicitudes.crear(
            convocatoria=convocatoria, persona=persona,
            comunes=fabricas.PROPUESTA, nombre_tipo="conversatorio",
            detalle=CONVERSATORIO,
        )
        segunda = solicitudes.crear(
            convocatoria=convocatoria, persona=persona,
            comunes={**fabricas.PROPUESTA, "titulo_actividad": "Otra cosa"},
            nombre_tipo="charla", detalle=CONVERSATORIO,
        )

        assert primera.registro == segunda.registro
        assert RegistroConvocatoria.objects.count() == 1
        assert seguimiento.propuestas_de(convocatoria, persona).count() == 2


def test_los_adjuntos_quedan_colgados_de_la_actividad(feria_2027, tmp_path):
    """Los archivos son del tipo, no del expediente (§2.8)."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        retrato = SimpleUploadedFile("autora.jpg", b"imagen", content_type="image/jpeg")
        portada = SimpleUploadedFile("portada.jpg", b"imagen", content_type="image/jpeg")

        propuesta = solicitudes.crear(
            convocatoria=convocatoria,
            persona=persona,
            comunes=fabricas.PROPUESTA,
            nombre_tipo="presentacion_libro",
            detalle={
                "titulo_publicacion": "El mar que nos habita",
                "tipo_presentador": "autor",
                "nombre_editorial": "La Nave",
                "nombre_autor_1": "Elena Poniatowska",
                "semblanza_autor_1": "Escritora y periodista.",
            },
            documentos=(
                (Documento.Tipo.RETRATO_AUTOR, retrato),
                (Documento.Tipo.PORTADA_LIBRO, portada),
            ),
        )

        adjuntos = propuesta.actividad.documentos.all()
        assert adjuntos.count() == 2
        # El nombre real en disco es un UUID (`ADR-0007`), así que el que
        # la persona le puso se guarda aparte o se pierde para siempre.
        assert {d.nombre_original for d in adjuntos} == {"autora.jpg", "portada.jpg"}


# ── E1: la convocatoria cerrada ───────────────────────────────


@pytest.mark.parametrize(
    "estado", [Convocatoria.Estado.CERRADA, Convocatoria.Estado.BORRADOR]
)
def test_con_la_convocatoria_no_abierta_no_queda_nada(feria_2027, estado):
    """`E1`: «no se crea ningún registro». Ni a medias.

    Importa que sea todo o nada: una solicitud sin actividad se vería en
    el panel del administrador como una propuesta vacía, y nadie sabría
    de dónde salió.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria(estado=estado)

        with pytest.raises(solicitudes.EnvioRechazado):
            solicitudes.crear(
                convocatoria=convocatoria,
                persona=fabricas.persona(),
                comunes=fabricas.PROPUESTA,
                nombre_tipo="conversatorio",
                detalle=CONVERSATORIO,
            )

        assert Solicitud.objects.count() == 0
        assert ActividadConversatorio.objects.count() == 0
        assert RegistroConvocatoria.objects.count() == 0


def test_admite_propuestas_mira_el_estado_y_no_las_fechas(feria_2027):
    """`CU-FER-008`: adelantar el cierre no cierra la convocatoria."""
    with schema_context(feria_2027.schema_name):
        assert solicitudes.admite_propuestas(fabricas.convocatoria()) is True
        assert (
            solicitudes.admite_propuestas(
                fabricas.convocatoria(
                    nombre="Cerrada", estado=Convocatoria.Estado.CERRADA
                )
            )
            is False
        )


# ── La invariante que el esquema no sostiene ──────────────────


def test_una_propuesta_no_cuelga_de_una_convocatoria_de_stands(feria_2027):
    """`ADR-0006`: la base no puede impedirlo; el servicio sí.

    El `tipo` que dice de qué es esta convocatoria vive un salto más allá
    del registro, así que ninguna clave foránea lo alcanza.
    """
    with schema_context(feria_2027.schema_name):
        ajena = fabricas.convocatoria(nombre="Stands 2027", tipo=TipoConvocatoria.STD)

        with pytest.raises(solicitudes.EnvioRechazado):
            solicitudes.crear(
                convocatoria=ajena,
                persona=fabricas.persona(),
                comunes=fabricas.PROPUESTA,
                nombre_tipo="conversatorio",
                detalle=CONVERSATORIO,
            )

        assert Solicitud.objects.count() == 0


def test_un_tipo_inventado_no_llega_a_la_base(feria_2027):
    """El formulario ya acota al catálogo; esto es la red de abajo."""
    with schema_context(feria_2027.schema_name):
        with pytest.raises(solicitudes.EnvioRechazado):
            solicitudes.crear(
                convocatoria=fabricas.convocatoria(),
                persona=fabricas.persona(),
                comunes=fabricas.PROPUESTA,
                nombre_tipo="mesa_de_debate",
                detalle={},
            )


# ── La configuración y el catálogo ────────────────────────────


def test_la_configuracion_se_puede_crear_dos_veces(feria_2027):
    """Es un callback: fallar por ejecutarse dos veces se llevaría el alta."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        primera = configuracion.crear_por_defecto(convocatoria)
        segunda = configuracion.crear_por_defecto(convocatoria)

        assert primera.pk == segunda.pk
        assert ConfiguracionConvocatoria.objects.count() == 1
        assert primera.prefijo_folio == "EVE"


def test_el_catalogo_sale_en_el_orden_del_selector(feria_2027):
    """El de la convocatoria en papel, no el alfabético."""
    with schema_context(feria_2027.schema_name):
        nombres = [t.nombre for t in catalogo.tipos()]
        assert nombres[0] == "conversatorio"
        assert nombres[-1] == "encuentro"
        assert len(nombres) == 8


def test_un_tipo_que_no_existe_no_revienta(feria_2027):
    """Llega de la barra de direcciones: es entrada, no error del sistema."""
    with schema_context(feria_2027.schema_name):
        assert catalogo.tipo_por_nombre("mesa_de_debate") is None
        assert catalogo.tipo_por_nombre("conversatorio") is not None


def test_solo_libro_y_revista_son_publicacion():
    """`A1` del CU: son los dos que piden archivos y ejemplar físico."""
    assert catalogo.es_publicacion("presentacion_libro")
    assert catalogo.es_publicacion("presentacion_revista")
    assert not catalogo.es_publicacion("conversatorio")
