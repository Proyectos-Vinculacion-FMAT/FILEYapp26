"""
Consultar las propuestas propias (`CU-EVT-003`).

Lo que se vigila aquí:

1. **El listado enseña las propias y solo las propias.** Es una pantalla
   que se alcanza sin más credencial que la sesión, y la consulta —no un
   `if` posterior— es lo que ata cada propuesta a su dueño.
2. **`E1`: sin propuestas, la pantalla ofrece el formulario.** Es la
   puerta del módulo (`ADR-0006`), así que la lista vacía es el primer
   paso de alguien, no un error.
3. **El paso 4 enseña de verdad todos los datos enviados**, incluidos los
   del tipo, y **no** las filas de persona que nadie llenó.
4. **Cada estado dice lo suyo**, con el texto que escribió quien
   dictaminó cuando lo hay.
5. **Los adjuntos siguen sin URL** (`ADR-0007`): se alcanzan por una
   vista que primero decide.
"""

import pytest
from django.conf import settings
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria

from ..detalle import bloques_del_tipo
from ..models import (
    ActividadCharla,
    ActividadPresentacionLibro,
    Documento,
    Solicitud,
)
from ..servicios import seguimiento
from . import fabricas

pytestmark = pytest.mark.django_db

ESTADOS = Solicitud.Estado


# ── Ayudas ────────────────────────────────────────────────────


def _url(feria, nombre, **kwargs):
    """La dirección completa, con el prefijo de la feria.

    `reverse` a secas devuelve la ruta sin `/f/<slug>/`: el prefijo lo
    antepone `django-tenants` al resolver, no al construir.
    """
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _propuesta(convocatoria, persona, **cambios):
    """Una charla enviada, con su actividad."""
    registro = fabricas.registro(persona, convocatoria)
    creada = fabricas.solicitud(registro, **cambios)
    ActividadCharla.objects.create(
        solicitud=creada,
        tipo=fabricas.tipo("charla"),
        nombre_participante_1="Elena Poniatowska",
        semblanza_participante_1="Escritora y periodista.",
    )
    return creada


# ── El listado (pasos 1 y 2) ──────────────────────────────────


def test_el_listado_ensena_folio_tipo_titulo_y_estado(client, feria_2027):
    """Las cuatro columnas que enumera el paso 2, y ninguna más.

    La quinta del prototipo —la categoría— la asigna el administrador al
    dictaminar y hoy saldría vacía en todas las filas.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        propuesta = _propuesta(
            convocatoria, persona, titulo_actividad="El mar que nos habita"
        )
        folio = propuesta.folio
    url = _url(feria_2027, "eventos:mis_propuestas", convocatoria_id=convocatoria.pk)

    client.force_login(persona)
    contenido = client.get(url).content.decode()

    assert folio in contenido
    assert "Charla" in contenido
    assert "El mar que nos habita" in contenido
    assert "Pendiente" in contenido


def test_el_listado_no_ensena_las_de_otra_persona(client, feria_2027):
    """Quién pregunta es parte de la consulta, no un filtro posterior."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        laura = fabricas.persona()
        ajena = fabricas.persona(correo="otra@ejemplo.com", nombre="Otra")
        _propuesta(convocatoria, laura, titulo_actividad="La mía")
        _propuesta(convocatoria, ajena, titulo_actividad="La suya")
    url = _url(feria_2027, "eventos:mis_propuestas", convocatoria_id=convocatoria.pk)

    client.force_login(laura)
    contenido = client.get(url).content.decode()

    assert "La mía" in contenido
    assert "La suya" not in contenido


def test_sin_propuestas_la_pantalla_ofrece_el_formulario(client, feria_2027):
    """`E1`. Es la puerta del módulo: la lista vacía es el primer paso.

    Un "sin resultados" dejaría a quien acaba de pulsar "Registrarme" en
    el catálogo sin nada que hacer y sin saber que se equivocó de sitio.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
    url = _url(feria_2027, "eventos:mis_propuestas", convocatoria_id=convocatoria.pk)
    formulario = _url(feria_2027, "eventos:propuesta", convocatoria_id=convocatoria.pk)

    client.force_login(persona)
    contenido = client.get(url).content.decode()

    assert "Aún no has enviado propuestas" in contenido
    assert reverse(
        "eventos:propuesta",
        kwargs={"convocatoria_id": convocatoria.pk},
        urlconf=settings.ROOT_URLCONF,
    ) in contenido
    assert formulario  # la ruta existe; el enlace de arriba apunta a ella


def test_con_la_convocatoria_cerrada_no_se_ofrece_enviar(client, feria_2027):
    """Se puede consultar lo enviado; no empezar algo nuevo.

    El botón no se apaga: se retira, y en su lugar hay un texto que dice
    por qué. Un control gris y callado se lee como una avería.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria(estado=Convocatoria.Estado.CERRADA)
        persona = fabricas.persona()
        _propuesta(convocatoria, persona)
    url = _url(feria_2027, "eventos:mis_propuestas", convocatoria_id=convocatoria.pk)

    client.force_login(persona)
    contenido = client.get(url).content.decode()

    assert "ya cerró" in contenido
    assert "Enviar otra propuesta" not in contenido


def test_la_recien_enviada_llega_resaltada(client, feria_2027):
    """El acuse manda `?nueva=<id>` y la lista la señala.

    Dos señales y no una: el destello se apaga solo y la pastilla se
    queda. Un color que se desvanece no puede ser la única forma de
    decir cuál es, y para quien pidió no animar no llega a existir.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        vieja = _propuesta(convocatoria, persona, titulo_actividad="La vieja")
        nueva = _propuesta(convocatoria, persona, titulo_actividad="La nueva")
    url = _url(feria_2027, "eventos:mis_propuestas", convocatoria_id=convocatoria.pk)

    client.force_login(persona)
    contenido = client.get(f"{url}?nueva={nueva.pk}").content.decode()

    assert contenido.count("row-nueva") == 1
    assert contenido.count("pill-nueva") == 1
    # Y sin el parámetro no se resalta nada: recargar apaga el aviso.
    assert "row-nueva" not in client.get(url).content.decode()
    assert vieja.pk != nueva.pk


@pytest.mark.parametrize("basura", ["abc", "", "9999", "1;drop"])
def test_un_nueva_inventado_no_rompe_la_lista(client, feria_2027, basura):
    """Nadie escribe esto a mano, pero se puede teclear en la URL.

    La respuesta correcta a un adorno con un valor absurdo es no pintar
    el adorno, no una página de error.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        _propuesta(convocatoria, persona)
    url = _url(feria_2027, "eventos:mis_propuestas", convocatoria_id=convocatoria.pk)

    client.force_login(persona)
    respuesta = client.get(f"{url}?nueva={basura}")

    assert respuesta.status_code == 200
    assert "row-nueva" not in respuesta.content.decode()


def test_el_listado_pide_sesion(client, feria_2027):
    """No hay pantalla de seguimiento anónima: no habría qué seguir."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
    url = _url(feria_2027, "eventos:mis_propuestas", convocatoria_id=convocatoria.pk)

    assert client.get(url).status_code in (302, 403)


# ── El detalle (pasos 3 y 4) ──────────────────────────────────


def test_el_detalle_ensena_lo_comun_y_lo_del_tipo(client, feria_2027):
    """«Todos los datos enviados»: los de la solicitud y los del tipo.

    Es lo que separa esta pantalla del modal de cinco renglones que
    dibuja el prototipo — y la razón de que sea una página.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        propuesta = _propuesta(convocatoria, persona)
        detalle = _url(
            feria_2027,
            "eventos:detalle",
            convocatoria_id=convocatoria.pk,
            solicitud_id=propuesta.pk,
        )

    client.force_login(persona)
    contenido = client.get(detalle).content.decode()

    # Lo común (§2.4).
    assert "Editorial La Nave" in contenido
    assert "Una conversación sobre la memoria del puerto." in contenido
    # Los públicos, con su nombre y no con su código.
    assert "Público en general" in contenido
    assert "publico_general" not in contenido
    # Lo del tipo (§2.7).
    assert "Elena Poniatowska" in contenido
    assert "Escritora y periodista." in contenido


def test_el_detalle_de_otra_persona_no_se_ve(client, feria_2027):
    """Un 404 y no un 403: un 403 confirmaría que ese folio existe."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        laura = fabricas.persona()
        propuesta = _propuesta(convocatoria, laura)
        detalle = _url(
            feria_2027,
            "eventos:detalle",
            convocatoria_id=convocatoria.pk,
            solicitud_id=propuesta.pk,
        )
        intrusa = fabricas.persona(correo="otra@ejemplo.com", nombre="Otra")

    client.force_login(intrusa)
    assert client.get(detalle).status_code == 404


def test_el_detalle_no_se_alcanza_desde_otra_convocatoria(client, feria_2027):
    """La convocatoria de la ruta **es parte de la consulta**.

    Sin eso, la URL de una convocatoria enseñaría una propuesta de otra
    con el encabezado equivocado encima.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        otra = fabricas.convocatoria(nombre="Otra convocatoria")
        persona = fabricas.persona()
        propuesta = _propuesta(convocatoria, persona)
        cruzada = _url(
            feria_2027,
            "eventos:detalle",
            convocatoria_id=otra.pk,
            solicitud_id=propuesta.pk,
        )

    client.force_login(persona)
    assert client.get(cruzada).status_code == 404


@pytest.mark.parametrize(
    "estado, esperado",
    [
        (ESTADOS.PENDIENTE, "está en revisión"),
        (ESTADOS.ACEPTADA, "fue aceptada"),
        (ESTADOS.CAMBIOS_SOLICITADOS, "pide algunos cambios"),
        (ESTADOS.RECHAZADA, "no fue aceptada"),
        (ESTADOS.CANCELADA, "quedó cancelada"),
    ],
)
def test_cada_estado_dice_lo_suyo(client, feria_2027, estado, esperado):
    """Paso 4: el desenlace, arriba y con palabras.

    Los cinco con texto propio y no solo con color: un distintivo de
    color obliga a saberse el código para saber si hay que hacer algo.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        propuesta = _propuesta(convocatoria, persona, estado=estado)
        detalle = _url(
            feria_2027,
            "eventos:detalle",
            convocatoria_id=convocatoria.pk,
            solicitud_id=propuesta.pk,
        )

    client.force_login(persona)
    assert esperado in client.get(detalle).content.decode()


def test_el_mensaje_del_administrador_llega_a_la_pantalla(client, feria_2027):
    """Lo que pide corregir y lo que motiva un rechazo, cada uno en su estado.

    Es la mitad del paso 4 que no existía hasta que el dictamen tuvo
    dónde guardarla.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        con_cambios = _propuesta(
            convocatoria,
            persona,
            estado=ESTADOS.CAMBIOS_SOLICITADOS,
            mensaje="Acorta la sinopsis a una cuartilla.",
            motivo="Esto no debe salir.",
        )
        url_cambios = _url(
            feria_2027,
            "eventos:detalle",
            convocatoria_id=convocatoria.pk,
            solicitud_id=con_cambios.pk,
        )

    client.force_login(persona)
    contenido = client.get(url_cambios).content.decode()

    assert "Acorta la sinopsis a una cuartilla." in contenido
    # El otro texto existe en la fila y **no** se enseña: el estado dice
    # cuál toca, y sacar los dos a la vez sería contradecirse.
    assert "Esto no debe salir." not in contenido


# ── Lo que compone `detalle.py` ───────────────────────────────


def test_las_filas_de_persona_vacias_no_se_pintan(feria_2027):
    """Un libro admite cinco autores; casi nadie llena cinco.

    «Autor 4: —» tres veces seguidas no informa de nada y empuja hacia
    abajo lo que sí se llenó.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        registro = fabricas.registro(persona, convocatoria)
        propuesta = fabricas.solicitud(registro)
        actividad = ActividadPresentacionLibro.objects.create(
            solicitud=propuesta,
            tipo=fabricas.tipo("presentacion_libro"),
            titulo_publicacion="El mar que nos habita",
            tipo_presentador="autor",
            nombre_editorial="La Nave",
            nombre_autor_1="Elena Poniatowska",
            semblanza_autor_1="Escritora y periodista.",
            autor_1_participa=True,
        )

        autores = [b for b in bloques_del_tipo(actividad) if b["clase"] == "personas"]

    # Dos grupos: autores y presentadores. El de autores trae una fila
    # —no cinco— y el de presentadores, ninguna.
    assert [b["titulo"] for b in autores] == ["Autores", "Presentadores"]
    assert len(autores[0]["filas"]) == 1
    assert autores[0]["filas"][0]["participa"] is True
    assert autores[1]["filas"] == []


def test_los_tipos_sin_casilla_de_asistencia_no_la_inventan(feria_2027):
    """`participa` es `None` en los seis tipos que no la preguntan.

    `False` significaría «dijo que no viene», que es otra cosa, y la
    plantilla pintaría un distintivo que nadie eligió.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        propuesta = _propuesta(convocatoria, persona)
        bloques = bloques_del_tipo(propuesta.actividad)

    grupo = next(b for b in bloques if b["clase"] == "personas")
    assert grupo["filas"][0]["participa"] is None


def test_los_campos_con_opciones_salen_con_su_nombre(feria_2027):
    """«Autor/a», no «autor»: el valor de la columna es un código."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        registro = fabricas.registro(persona, convocatoria)
        propuesta = fabricas.solicitud(registro)
        actividad = ActividadPresentacionLibro.objects.create(
            solicitud=propuesta,
            tipo=fabricas.tipo("presentacion_libro"),
            titulo_publicacion="El mar que nos habita",
            tipo_presentador="antologador",
            nombre_editorial="La Nave",
            nombre_autor_1="Elena Poniatowska",
            semblanza_autor_1="Escritora y periodista.",
        )
        campos = {
            b["etiqueta"]: b["valor"]
            for b in bloques_del_tipo(actividad)
            if b["clase"] == "campo"
        }

    assert campos["el proponente es"] == "Antologador/a"


def test_el_orden_del_detalle_es_el_de_la_captura(feria_2027):
    """No hay una segunda lista que se pueda separar de la primera.

    Quien abre el detalle viene a comprobar algo que recuerda haber
    escrito, y lo busca donde lo escribió.
    """
    from ..formularios import FORMULARIO_POR_TIPO, Campo

    esperado = [
        p.nombre if isinstance(p, Campo) else "personas"
        for p in FORMULARIO_POR_TIPO["presentacion_libro"].orden
    ]

    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        registro = fabricas.registro(persona, convocatoria)
        propuesta = fabricas.solicitud(registro)
        actividad = ActividadPresentacionLibro.objects.create(
            solicitud=propuesta,
            tipo=fabricas.tipo("presentacion_libro"),
            titulo_publicacion="El mar que nos habita",
            tipo_presentador="autor",
            nombre_editorial="La Nave",
            nombre_autor_1="Elena Poniatowska",
            semblanza_autor_1="Escritora y periodista.",
        )
        bloques = bloques_del_tipo(actividad)

    # Los campos sueltos se comparan por su nombre de columna; los grupos
    # de personas solo por estar en su sitio.
    sale = [
        "personas" if b["clase"] == "personas" else b["etiqueta"] for b in bloques
    ]
    assert len(sale) == len(esperado)
    assert sale[0] == "título del libro"
    assert sale[1] == "el proponente es"
    assert sale[2] == "personas"
    assert sale[3] == "personas"
    assert sale[4] == "editorial"


# ── Los adjuntos (`ADR-0007`) ─────────────────────────────────


def _con_portada(convocatoria, persona):
    """Una presentación de libro con su portada adjunta."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    from ..servicios import solicitudes

    return solicitudes.crear(
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
            (
                Documento.Tipo.PORTADA_LIBRO,
                SimpleUploadedFile("portada.jpg", b"imagen", content_type="image/jpeg"),
            ),
        ),
    )


def test_el_detalle_enlaza_los_adjuntos_por_la_vista_que_decide(
    client, feria_2027, tmp_path, settings
):
    """Los archivos no tienen URL propia (`ADR-0007`).

    Lo que sale en la pantalla es el nombre con el que se subieron —el de
    disco es un UUID— y un enlace a `eventos:documento`, que comprueba
    antes de entregar.
    """
    settings.MEDIA_ROOT = tmp_path
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        propuesta = _con_portada(convocatoria, persona)
        adjunto = propuesta.actividad.documentos.get()
        detalle = _url(
            feria_2027,
            "eventos:detalle",
            convocatoria_id=convocatoria.pk,
            solicitud_id=propuesta.pk,
        )
        ruta_adjunto = reverse(
            "eventos:documento",
            kwargs={"documento_id": adjunto.pk},
            urlconf=settings.ROOT_URLCONF,
        )

    client.force_login(persona)
    contenido = client.get(detalle).content.decode()

    assert "portada.jpg" in contenido
    assert ruta_adjunto in contenido
    # `MEDIA_URL` no está montada en ningún urlconf: si el nombre de disco
    # apareciera en la página, alguien lo habría enlazado por su cuenta.
    assert adjunto.archivo.name not in contenido


def test_una_imagen_se_pinta_y_no_solo_se_nombra(
    client, feria_2027, tmp_path, settings
):
    """Un nombre de archivo no contesta «¿subí la portada que era?».

    Dos versiones de la misma imagen se llaman igual, y la que puso la
    cámara —`IMG_4471.jpg`— no distingue nada. Así que se pinta, con el
    mismo enlace que la abre en grande debajo.
    """
    settings.MEDIA_ROOT = tmp_path
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        propuesta = _con_portada(convocatoria, persona)
        adjunto = propuesta.actividad.documentos.get()
        assert adjunto.es_imagen
        detalle = _url(
            feria_2027,
            "eventos:detalle",
            convocatoria_id=convocatoria.pk,
            solicitud_id=propuesta.pk,
        )

    client.force_login(persona)
    contenido = client.get(detalle).content.decode()

    assert "<img" in contenido
    # Diferida: el navegador no descarga lo que está fuera de pantalla.
    assert 'loading="lazy"' in contenido
    # Y el marco es un enlace de verdad, que sin JavaScript abre el
    # archivo. `data-visor` es lo único que `filey.js` necesita.
    assert "data-visor" in contenido


def test_un_pdf_no_se_intenta_pintar(client, feria_2027, tmp_path, settings):
    """La portada admite PDF, y un `<img>` no lo puede enseñar.

    Se decide por la extensión de lo guardado y no por `nombre_original`:
    la primera la fija `CarpetaDeLaFeria` y siempre viene en minúsculas.
    """
    from django.core.files.uploadedfile import SimpleUploadedFile

    from ..servicios import solicitudes

    settings.MEDIA_ROOT = tmp_path
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        propuesta = solicitudes.crear(
            convocatoria=convocatoria,
            persona=persona,
            comunes=fabricas.PROPUESTA,
            nombre_tipo="presentacion_revista",
            detalle={
                "titulo_publicacion": "Revista de la Nave",
                "tipo_presentador": "editor",
                "nombre_editorial": "La Nave",
                "nombre_editor_1": "Elena Poniatowska",
                "semblanza_editor_1": "Escritora y periodista.",
            },
            documentos=(
                (
                    Documento.Tipo.PORTADA_REVISTA,
                    SimpleUploadedFile(
                        "PORTADA.PDF", b"%PDF-1.4", content_type="application/pdf"
                    ),
                ),
            ),
        )
        adjunto = propuesta.actividad.documentos.get()
        detalle = _url(
            feria_2027,
            "eventos:detalle",
            convocatoria_id=convocatoria.pk,
            solicitud_id=propuesta.pk,
        )

    assert not adjunto.es_imagen
    # Pero sí se puede enseñar dentro de la pantalla, con el visor del
    # navegador: no es lo mismo «no es una imagen» que «no se puede ver».
    assert adjunto.es_incrustable

    client.force_login(persona)
    contenido = client.get(detalle).content.decode()
    assert "data-visor-doc" in contenido
    # Y no se intenta pintar como imagen. Se mira `loading="lazy"`, que
    # solo lleva la galería, y no `<img` a secas: el logo de la barra
    # superior es uno y estaría siempre.
    assert 'loading="lazy"' not in contenido


@pytest.mark.parametrize(
    "partial, viewbox",
    [
        ("componentes/icono_pdf.html", "0 0 24 24"),
        ("componentes/icono_clip.html", "0 0 512 512"),
    ],
)
def test_los_iconos_en_linea_cumplen_las_reglas_de_svg(partial, viewbox):
    """`filey-ui-componentes` §8, que ningún script comprueba en Django.

    `check-ui.sh` mira los assets del prototipo; estos iconos van en línea
    en una plantilla y quedan fuera de su alcance. Las reglas cuestan lo
    mismo de romper que de escribir bien, y todas fallan en silencio: un
    `width` de fábrica lo deja gigante y un color escrito a mano no
    hereda, así que nadie sabe por qué ese icono no se aclara al apuntar
    y los de al lado sí.

    Los tres vienen del mismo banco externo y los tres traían las mismas
    tres cosas que hay que quitarles.
    """
    from django.template.loader import get_template

    svg = get_template(partial).render({}).strip()
    # Solo la etiqueta de apertura: el `d=` de un `<path>` lleva números
    # con comas y espacios que confundirían a cualquier búsqueda.
    apertura = svg[: svg.index(">") + 1]

    # El tamaño lo fija CSS. Los tres traían `800px`. Se mira ` width=`
    # con espacio delante para no chocar con `stroke-width`, que es otra
    # cosa y sí tiene que estar.
    assert " width=" not in apertura
    assert " height=" not in apertura
    # Sin `viewBox` no hay forma de escalarlo.
    assert f'viewBox="{viewbox}"' in apertura
    # El color se hereda. **Por qué atributo depende del icono**: los de
    # relleno usan `fill` y los de trazo `stroke`, y confundirlos pinta
    # una mancha negra donde debería haber una silueta.
    assert "currentColor" in apertura
    # Ningún color escrito a mano, en ninguna parte.
    assert "#" not in svg
    # Es decoración: al lado va el texto que hay que leer.
    assert 'aria-hidden="true"' in apertura


def test_un_archivo_que_nadie_pinta_se_queda_como_enlace():
    """Un `.docx` o un `.odt` de la lista blanca.

    Prometer un visor que saldría en blanco es peor que mandar a otra
    pestaña, así que su marco no lleva `data-visor` y el enlace hace lo
    suyo.
    """
    from ..models import Documento as Doc

    adjunto = Doc(archivo="feria_2027/eventos/abc.docx")
    assert not adjunto.es_imagen
    assert not adjunto.es_incrustable


def test_un_webp_cuenta_como_imagen():
    """Está en la lista blanca de subida, así que puede llegar.

    Dejarlo fuera lo enseñaría como «documento» sin que nadie entienda
    por qué esa portada no se ve y las otras sí.
    """
    from ..models import Documento as Doc

    assert Doc(archivo="feria_2027/eventos/portada.webp").es_imagen


def test_el_adjunto_se_entrega_embebible_en_la_propia_pantalla(
    client, feria_2027, tmp_path, settings
):
    """Las dos cabeceras que dejarían el visor en blanco sin decir nada.

    `X-Frame-Options: DENY` —que es lo que manda el proyecto para todo lo
    demás— y un `sandbox` de origen opaco impiden que el navegador pinte
    el documento dentro de un marco de la propia página. Ninguna de las
    dos da error visible: sale un rectángulo vacío.
    """
    settings.MEDIA_ROOT = tmp_path
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        propuesta = _con_portada(convocatoria, persona)
        adjunto = propuesta.actividad.documentos.get()
        url = _url(feria_2027, "eventos:documento", documento_id=adjunto.pk)

    client.force_login(persona)
    respuesta = client.get(url)

    assert respuesta["X-Frame-Options"] == "SAMEORIGIN"
    csp = respuesta["Content-Security-Policy"]
    assert "allow-same-origin" in csp
    # Y lo que **no** puede aparecer nunca: sin esto, un archivo disfrazado
    # podría ejecutar JavaScript en nuestro propio origen.
    assert "allow-scripts" not in csp
    assert respuesta["X-Content-Type-Options"] == "nosniff"


def test_el_adjunto_lo_entrega_quien_lo_subio(client, feria_2027, tmp_path, settings):
    """Y a nadie más, ni siquiera con el identificador en la mano."""
    settings.MEDIA_ROOT = tmp_path
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        propuesta = _con_portada(convocatoria, persona)
        adjunto = propuesta.actividad.documentos.get()
        url = _url(feria_2027, "eventos:documento", documento_id=adjunto.pk)
        intrusa = fabricas.persona(correo="otra@ejemplo.com", nombre="Otra")

    client.force_login(persona)
    assert client.get(url).status_code == 200

    # Un 404 y no un 403: un 403 confirmaría que ese documento existe.
    client.force_login(intrusa)
    assert client.get(url).status_code == 404
