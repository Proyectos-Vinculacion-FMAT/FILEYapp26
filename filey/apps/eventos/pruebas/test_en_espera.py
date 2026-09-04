"""
Los adjuntos que sobreviven a un envío rechazado (`CU-EVT-002`).

Deuda técnica saldada el 2026-09-03. Un `<input type="file">` **no se
puede repoblar** —ningún navegador deja que una página le ponga un
archivo—, así que un envío rechazado por un campo de texto se llevaba por
delante los adjuntos: quien lo sufría tenía que volver a buscarlos en su
disco sin entender por qué solo se habían perdido ésos.

Lo que se vigila aquí es la política entera, que tiene cuatro partes y
ninguna se puede comprobar mirando la pantalla:

1. **Lo que llegó sobrevive**, y el campo deja de ser obligatorio.
2. **Es una cola con tope.** Al pasarse, se va el más viejo — y su
   archivo con él, o el disco crece sin que nada lo vuelva a tocar.
3. **Se vacía al enviar bien**, o cada adjunto del sistema quedaría
   duplicado en disco.
4. **Se vacía al salir del formulario**, por las dos puertas: el listado
   y el catálogo. La del catálogo pasa por una señal, porque
   `apps/convocatorias` no puede nombrar a un vertical (`ADR-0006`).
5. **Se puede descartar** un adjunto sin subir otro encima.
6. **La barrida recoge lo que ninguna de las dos salidas alcanza**: quien
   cierra la pestaña y no vuelve.
7. **Cambiar de tipo se lleva lo que el nuevo no pide.** Un adjunto sin
   campo donde enseñarse no es nada.
"""

import os
from io import StringIO

import pytest
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_tenants.utils import schema_context

from ..models import ArchivoEnEspera, Documento, Solicitud
from ..servicios import en_espera
from . import fabricas

pytestmark = pytest.mark.django_db

#: Lo común, con el título vacío para que el envío falle por ahí y no por
#: los adjuntos. Es el escenario exacto de la deuda: todo bien menos un
#: campo de texto.
SIN_TITULO = {
    "institucion": "Editorial La Nave",
    "cargo": "Coordinadora editorial",
    "titulo_actividad": "",
    "nombre_organizador_organizacion": "Editorial La Nave",
    "nombre_moderador": "",
    "publico_objetivo": ["publico_general"],
    "sinopsis": "Una conversación sobre la memoria del puerto.",
    "comentarios": "",
    "bases_aceptadas": "on",
}
LIBRO = {
    "tipo": "presentacion_libro",
    "titulo_publicacion": "El mar que nos habita",
    "tipo_presentador": "autor",
    "nombre_editorial": "La Nave",
    "nombre_autor_1": "Elena Poniatowska",
    "semblanza_autor_1": "Escritora y periodista.",
    "autor_1_participa": "on",
}


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


#: Una clave de sesión cualquiera, para las pruebas que llaman al
#: servicio sin pasar por HTTP. Lo que importa es que sea **la misma** en
#: toda una prueba: la cola es de la sesión, y con dos claves distintas
#: nada de lo guardado sería vigente.
SESION = "sesion-de-prueba"


def _imagen(nombre="portada.jpg"):
    return SimpleUploadedFile(nombre, b"imagen", content_type="image/jpeg")


def _escenario(feria):
    with schema_context(feria.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
    return convocatoria, persona, _url(
        feria, "eventos:propuesta", convocatoria_id=convocatoria.pk
    )


# ── 1 · Lo que llegó sobrevive ────────────────────────────────


def test_los_archivos_que_llegaron_quedan_en_espera(
    client, feria_2027, tmp_path, settings
):
    """Y el campo deja de pedirlos en el intento siguiente."""
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(
        url,
        {
            **SIN_TITULO,
            **LIBRO,
            "retrato_autor": _imagen("autora.jpg"),
            "portada_libro": _imagen("portada.jpg"),
        },
    )

    with schema_context(feria_2027.schema_name):
        guardados = en_espera.vigentes(convocatoria, persona)
        assert set(guardados) == {
            Documento.Tipo.RETRATO_AUTOR,
            Documento.Tipo.PORTADA_LIBRO,
        }
        assert guardados[Documento.Tipo.PORTADA_LIBRO].nombre_original == "portada.jpg"

    # Y la pantalla lo enseña **dentro del propio componente de subir**,
    # con `is-cargado` — la misma clase que pone `filey.js` al elegir un
    # archivo—, así que se ve igual que uno recién adjuntado.
    #
    # Se afirma sobre eso y no sobre un texto explicativo a propósito:
    # hubo uno ("se conserva") y se retiró el 2026-09-03 por contar el
    # funcionamiento interno. Que venga de un intento anterior no es
    # asunto de quien lo subió.
    contenido = client.get(f"{url}?tipo=presentacion_libro").content.decode()
    assert "file-mock is-cargado" in contenido
    assert "portada.jpg" in contenido
    # Y se puede quitar sin subir otro encima.
    assert 'name="descartar" value="portada_libro"' in contenido


def test_el_segundo_intento_pasa_sin_volver_a_adjuntar(
    client, feria_2027, tmp_path, settings
):
    """La prueba que dice que la deuda está saldada de verdad.

    Se envía sin título y con archivos; después, con título y **sin**
    archivos. La propuesta tiene que quedar creada y con sus dos
    `Documento`.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(
        url,
        {
            **SIN_TITULO,
            **LIBRO,
            "retrato_autor": _imagen("autora.jpg"),
            "portada_libro": _imagen("portada.jpg"),
        },
    )
    respuesta = client.post(
        url, {**SIN_TITULO, **LIBRO, "titulo_actividad": "El mar que nos habita"}
    )

    assert respuesta.status_code == 302
    with schema_context(feria_2027.schema_name):
        propuesta = Solicitud.objects.get()
        adjuntos = propuesta.actividad.documentos.all()
        assert adjuntos.count() == 2
        assert {d.nombre_original for d in adjuntos} == {"autora.jpg", "portada.jpg"}
        # Y viven donde viven los adjuntos de verdad, no en la carpeta de
        # espera: si no, mirar el disco no diría qué se puede borrar.
        for adjunto in adjuntos:
            assert "en-espera" not in adjunto.archivo.name


def test_un_archivo_nuevo_sustituye_al_guardado(
    client, feria_2027, tmp_path, settings
):
    """«Volver a subirlo» significa «sustituirlo», no «añadir otro»."""
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen("vieja.jpg")})
    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen("nueva.jpg")})

    with schema_context(feria_2027.schema_name):
        vigente = en_espera.vigentes(convocatoria, persona)[Documento.Tipo.PORTADA_LIBRO]
        assert vigente.nombre_original == "nueva.jpg"


def test_un_archivo_invalido_no_entra_en_la_cola(
    client, feria_2027, tmp_path, settings
):
    """Ocuparía sitio y desalojaría a uno bueno, para nada.

    El formulario lo va a rechazar igual en el intento siguiente: solo
    entra lo que pasó su propia validación.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(
        url,
        {
            **SIN_TITULO,
            **LIBRO,
            "portada_libro": SimpleUploadedFile(
                "hoja.txt", b"no soy una imagen", content_type="text/plain"
            ),
        },
    )

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 0


# ── 7 · Cambiar de tipo ───────────────────────────────────────


def test_cambiar_a_un_tipo_sin_adjuntos_los_barre(
    client, feria_2027, tmp_path, settings
):
    """Portada y retrato de un libro; se cambia a «charla».

    Una charla no pide adjuntos, así que esos dos archivos se quedan sin
    campo donde enseñarse y sin nada a lo que volver. Conservarlos sería
    guardar un borrador a medias — y reaparecerían al volver a «libro»,
    que es justo lo que este dominio no hace.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(
        url,
        {
            **SIN_TITULO,
            **LIBRO,
            "retrato_autor": _imagen("autora.jpg"),
            "portada_libro": _imagen("portada.jpg"),
        },
    )
    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 2

    client.get(f"{url}?tipo=charla")

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 0


def test_cambiar_a_otro_tipo_con_adjuntos_barre_solo_lo_que_sobra(
    client, feria_2027, tmp_path, settings
):
    """De libro a revista: la revista pide portada, pero no retrato.

    Es el caso que distingue «barrer todo al cambiar» de la regla que
    hay: lo que decide no es que se cambiara de tipo, sino si cada
    archivo cabe en el tipo que hay elegido ahora.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(
        url,
        {
            **SIN_TITULO,
            **LIBRO,
            "retrato_autor": _imagen("autora.jpg"),
            "portada_libro": _imagen("portada.jpg"),
        },
    )

    client.get(f"{url}?tipo=presentacion_revista")

    with schema_context(feria_2027.schema_name):
        # Los dos eran de libro y ninguno cabe en una revista, que solo
        # pide `PORTADA_REVISTA`.
        assert ArchivoEnEspera.objects.count() == 0


def test_seguir_en_el_mismo_tipo_no_barre_nada(
    client, feria_2027, tmp_path, settings
):
    """La comprobación de que esto no pisa el flujo normal.

    Volver a pintar el formulario del mismo tipo pasa todo el rato: tras
    un envío rechazado, al descartar un adjunto, al recargar. Si el
    barrido se llevara algo aquí, la cola no serviría para nada.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(
        url,
        {
            **SIN_TITULO,
            **LIBRO,
            "retrato_autor": _imagen("autora.jpg"),
            "portada_libro": _imagen("portada.jpg"),
        },
    )
    client.get(f"{url}?tipo=presentacion_libro")

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 2


def test_sin_tipo_elegido_no_se_barre_por_no_saber(
    client, feria_2027, tmp_path, settings
):
    """Abrir el formulario sin `?tipo=` no es cambiar de tipo.

    Sin tipo no hay con qué comparar. Barrer ahí sería borrar por no
    saber, y el formulario en blanco se abre en más sitios de los que
    parece — un enlace pegado, el botón de atrás del navegador.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen()})
    client.get(url)

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 1


def test_un_tipo_inventado_en_la_url_tampoco_barre(
    client, feria_2027, tmp_path, settings
):
    """`?tipo=loquesea` se trata como «todavía no eligió», no como un tipo.

    Es lo que ya hacía la vista para no reventar con una URL escrita a
    mano; el barrido tiene que seguir la misma puerta o un enlace mal
    copiado borraría archivos.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen()})
    client.get(f"{url}?tipo=loquesea")

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 1


# ── 2 · Es una cola con tope ──────────────────────────────────


def test_la_cola_desaloja_por_el_extremo_viejo(feria_2027, tmp_path, settings):
    """El tope es parametrizable, y aquí se baja para no subir siete."""
    settings.MEDIA_ROOT = tmp_path
    settings.EVT_MAX_ARCHIVOS_EN_ESPERA = 2

    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()

        for n in range(1, 4):
            en_espera.guardar(
                convocatoria,
                persona,
                ((Documento.Tipo.PORTADA_LIBRO, _imagen(f"portada-{n}.jpg")),),
                SESION,
            )

        quedan = list(en_espera.de(convocatoria, persona))
        assert len(quedan) == 2
        # La más vieja se fue; el orden del modelo es de nueva a vieja.
        assert [a.nombre_original for a in quedan] == [
            "portada-3.jpg",
            "portada-2.jpg",
        ]


def test_al_desalojar_se_borra_tambien_el_archivo(feria_2027, tmp_path, settings):
    """Django no borra el fichero al borrar la fila, desde la 1.3.

    Sin la señal, cada intento fallido de cada persona dejaría basura que
    nada volvería a tocar nunca. Es lo que más pesa de esta política.
    """
    settings.MEDIA_ROOT = tmp_path
    settings.EVT_MAX_ARCHIVOS_EN_ESPERA = 1

    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()

        en_espera.guardar(
            convocatoria,
            persona,
            ((Documento.Tipo.PORTADA_LIBRO, _imagen("vieja.jpg")),),
            SESION,
        )
        # `.path` es absoluta y la compone el propio almacén, así que
        # afirmar sobre ella es seguro en Windows y en Linux — no se
        # arma aquí con separadores a mano (`filey-render` §8).
        ruta_vieja = en_espera.de(convocatoria, persona).get().archivo.path
        assert os.path.exists(ruta_vieja)

        en_espera.guardar(
            convocatoria,
            persona,
            ((Documento.Tipo.PORTADA_LIBRO, _imagen("nueva.jpg")),),
            SESION,
        )

    assert not os.path.exists(ruta_vieja)


def test_el_desalojo_nunca_tira_uno_que_hace_falta(feria_2027, tmp_path, settings):
    """Lo que hace que el tope signifique algo.

    Con una FIFO a secas: cuatro adjuntos, se corrige uno, se corrige
    otro, se corrige un tercero — y la séptima subida tira la más vieja,
    que es el primer adjunto, el único que nadie ha vuelto a subir. El
    campo se queda vacío y el formulario vuelve a pedirlo, que es
    exactamente el problema que esto vino a resolver.
    """
    settings.MEDIA_ROOT = tmp_path
    settings.EVT_MAX_ARCHIVOS_EN_ESPERA = 2

    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()

        # Uno de cada tipo: los dos son vigentes y ninguno se puede tirar.
        en_espera.guardar(
            convocatoria,
            persona,
            ((Documento.Tipo.RETRATO_AUTOR, _imagen("autora.jpg")),),
            SESION,
        )
        en_espera.guardar(
            convocatoria,
            persona,
            ((Documento.Tipo.PORTADA_LIBRO, _imagen("portada.jpg")),),
            SESION,
        )
        # Un tercero pasa del tope. El que sobra tiene que ser la portada
        # vieja —que dejó de ser vigente— y **no** el retrato.
        en_espera.guardar(
            convocatoria,
            persona,
            ((Documento.Tipo.PORTADA_LIBRO, _imagen("portada-2.jpg")),),
            SESION,
        )

        vigente = en_espera.vigentes(convocatoria, persona)
        assert vigente[Documento.Tipo.RETRATO_AUTOR].nombre_original == "autora.jpg"
        assert vigente[Documento.Tipo.PORTADA_LIBRO].nombre_original == "portada-2.jpg"


# ── 5 · Descartar ─────────────────────────────────────────────


def test_descartar_quita_el_adjunto_y_vuelve_a_pedirlo(
    client, feria_2027, tmp_path, settings
):
    """Sin esto, el único modo de cambiar de idea sería subir otro encima."""
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen("portada.jpg")})
    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 1

    respuesta = client.post(
        url, {**SIN_TITULO, **LIBRO, "descartar": "portada_libro"}
    )

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 0
        # Y no se creó nada: descartar no es enviar.
        assert Solicitud.objects.count() == 0

    contenido = respuesta.content.decode()
    assert "portada.jpg" not in contenido
    # Lo escrito sigue ahí: descartar un archivo no vacía el formulario.
    assert "El mar que nos habita" in contenido


def test_el_boton_de_descartar_existe_desde_el_formulario_en_blanco(
    client, feria_2027
):
    """Sale al elegir un archivo, no solo tras un envío rechazado.

    Elegir un archivo ocurre **en el navegador**: el servidor no se
    entera hasta que se envía. Así que el botón se pinta siempre y nace
    `hidden`; quien lo revela al elegir es `filey.js`.

    Que nazca escondido en vez de aparecer por JavaScript tiene su
    motivo: crear el nodo al vuelo obligaría a duplicar en JavaScript el
    icono, las clases y el `aria-label` que ya están aquí, y a
    mantenerlos en dos sitios.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
    url = _url(feria_2027, "eventos:propuesta", convocatoria_id=convocatoria.pk)

    client.force_login(persona)
    contenido = client.get(f"{url}?tipo=presentacion_libro").content.decode()

    # Dos: uno por adjunto. Escondidos, y sin `name` — descartar algo que
    # nunca salió del navegador no es cosa del servidor.
    assert contenido.count("data-descartar") == 2
    assert 'name="descartar"' not in contenido
    # Sin rótulo, así que el nombre accesible tiene que estar.
    assert 'aria-label="Descartar el archivo"' in contenido


def test_descartar_no_toca_los_demas_adjuntos(client, feria_2027, tmp_path, settings):
    """Se descarta un campo, no la cola entera."""
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(
        url,
        {
            **SIN_TITULO,
            **LIBRO,
            "retrato_autor": _imagen("autora.jpg"),
            "portada_libro": _imagen("portada.jpg"),
        },
    )
    client.post(url, {**SIN_TITULO, **LIBRO, "descartar": "portada_libro"})

    with schema_context(feria_2027.schema_name):
        quedan = en_espera.vigentes(convocatoria, persona)
        assert set(quedan) == {Documento.Tipo.RETRATO_AUTOR}


def test_descartar_con_htmx_no_recarga_la_pantalla(
    client, feria_2027, tmp_path, settings
):
    """Descartar recargaba la página entera y la dejaba por arriba.

    En un formulario de treinta campos eso es perder el sitio: quien
    descarta un adjunto está a la mitad, no empezando. Con htmx cambia
    solo la sección del tipo, que es el mismo intercambio que ya hace
    elegir el tipo de actividad.

    Se comprueba por lo que **no** trae la respuesta: si volviera la
    página entera, traería el `<!doctype>` y la barra superior.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)
    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen()})

    respuesta = client.post(
        url,
        {**SIN_TITULO, **LIBRO, "descartar": "portada_libro"},
        HTTP_HX_REQUEST="true",
    )
    contenido = respuesta.content.decode()

    assert respuesta.status_code == 200
    assert "<!doctype" not in contenido.lower()
    assert 'id="campos-tipo"' in contenido
    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 0


def test_sin_javascript_descartar_vuelve_al_mismo_adjunto(
    client, feria_2027, tmp_path, settings
):
    """El ancla del `formaction`, que es el camino sin htmx.

    Sin JavaScript el botón es un envío normal y la respuesta es la
    página entera. Lo que evita empezar por arriba es el fragmento: el
    navegador lo aplica a la respuesta del `POST` y aterriza en el mismo
    adjunto que se acaba de descartar.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)
    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen()})

    contenido = client.get(f"{url}?tipo=presentacion_libro").content.decode()

    # El destino existe y el botón apunta a él.
    assert 'id="adjunto-portada_libro"' in contenido
    assert 'formaction="#adjunto-portada_libro"' in contenido


def test_descartar_uno_no_se_lleva_el_que_se_acaba_de_elegir(
    client, feria_2027, tmp_path, settings
):
    """El repro exacto del 2026-09-03, paso por paso.

    0. Se envía con un campo obligatorio vacío y los dos adjuntos puestos
       -> rechazado, los dos quedan en espera.
    1. Se descarta el retrato.
    2. Se vuelve a elegir un retrato (en el navegador; aún no se envía).
    3. Se descarta la portada.
    4. **Desaparecían los dos.**

    El de la portada era el único que llegaba al servidor, y al repintar
    la sección el retrato recién elegido se perdía: un `<input
    type="file">` no se puede repoblar. Ahora el descarte guarda lo que
    viene en su misma petición antes de borrar nada.

    Descartando dos veces el mismo campo nunca falló, y por eso costó
    verlo: el segundo clic no llegaba al servidor.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    # 0 · envío rechazado con los dos adjuntos.
    client.post(
        url,
        {
            **SIN_TITULO,
            **LIBRO,
            "retrato_autor": _imagen("autora.jpg"),
            "portada_libro": _imagen("portada.jpg"),
        },
    )
    # 1 · se descarta el retrato.
    client.post(url, {**SIN_TITULO, **LIBRO, "descartar": "retrato_autor"})
    with schema_context(feria_2027.schema_name):
        assert set(en_espera.vigentes(convocatoria, persona)) == {
            Documento.Tipo.PORTADA_LIBRO
        }

    # 2 y 3 · se elige otro retrato y, en la misma pantalla, se descarta
    # la portada. El retrato viaja en esa petición.
    client.post(
        url,
        {
            **SIN_TITULO,
            **LIBRO,
            "retrato_autor": _imagen("autora-2.jpg"),
            "descartar": "portada_libro",
        },
    )

    with schema_context(feria_2027.schema_name):
        quedan = en_espera.vigentes(convocatoria, persona)
        # 4 · el retrato sobrevive, y es el nuevo.
        assert set(quedan) == {Documento.Tipo.RETRATO_AUTOR}
        assert quedan[Documento.Tipo.RETRATO_AUTOR].nombre_original == "autora-2.jpg"


def test_descartar_el_mismo_campo_dos_veces_no_es_un_envio(
    client, feria_2027, tmp_path, settings
):
    """El segundo clic llega con la cola ya vacía.

    `_atender_descarte` devolvía si había borrado algo, así que el
    segundo clic contaba como envío: salía el formulario en rojo por un
    botón que solo quita un archivo.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)
    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen()})

    client.post(url, {**SIN_TITULO, **LIBRO, "descartar": "portada_libro"})
    respuesta = client.post(url, {**SIN_TITULO, **LIBRO, "descartar": "portada_libro"})

    assert respuesta.status_code == 200
    contenido = respuesta.content.decode()
    # Ni errores de validación ni propuesta creada: no era un envío.
    assert "msg-error" not in contenido
    with schema_context(feria_2027.schema_name):
        assert Solicitud.objects.count() == 0


def test_un_campo_inventado_no_descarta_nada(client, feria_2027, tmp_path, settings):
    """El botón manda el nombre del campo, y un `POST` a mano puede mandar
    cualquier cosa. Lo traduce el formulario del tipo, que es quien conoce
    la tabla: lo que no está en ella no encuentra tipo y no borra."""
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen()})
    client.post(url, {**SIN_TITULO, **LIBRO, "descartar": "lo_que_sea"})

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 1


# ── 3 y 4 · Cuándo se vacía ───────────────────────────────────


def test_enviar_bien_vacia_la_espera(client, feria_2027, tmp_path, settings):
    """Ya son `Documento`: dejarlos aquí duplicaría cada adjunto en disco."""
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(
        url,
        {
            **SIN_TITULO,
            **LIBRO,
            "retrato_autor": _imagen("autora.jpg"),
            "portada_libro": _imagen("portada.jpg"),
        },
    )
    client.post(
        url, {**SIN_TITULO, **LIBRO, "titulo_actividad": "El mar que nos habita"}
    )

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 0


def test_salir_al_listado_descarta_lo_que_quedaba(
    client, feria_2027, tmp_path, settings
):
    """Abandonar el llenado es abandonar lo subido (política del 2026-09-03)."""
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen()})
    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 1

    client.get(_url(feria_2027, "eventos:mis_propuestas", convocatoria_id=convocatoria.pk))

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 0


def test_salir_al_catalogo_tambien(client, feria_2027, tmp_path, settings):
    """Y por una señal, no por una llamada directa.

    `apps/convocatorias` no puede nombrar a `eventos` (`ADR-0006`): el
    catálogo anuncia que se abrió y cada vertical decide qué significa
    eso. Que esta prueba pase es que la señal está conectada.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)

    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen()})
    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 1

    client.get(f"{feria_2027.url.rstrip('/')}/")

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 0


def test_la_espera_de_otra_persona_no_se_toca(client, feria_2027, tmp_path, settings):
    """La cola es de cada quien: salir yo no borra lo tuyo."""
    settings.MEDIA_ROOT = tmp_path
    convocatoria, laura, url = _escenario(feria_2027)
    with schema_context(feria_2027.schema_name):
        otra = fabricas.persona(correo="otra@ejemplo.com", nombre="Otra")

    client.force_login(laura)
    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen("de-laura.jpg")})
    client.force_login(otra)
    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen("de-otra.jpg")})

    # Laura sale al listado; lo de la otra persona sigue ahí.
    client.force_login(laura)
    client.get(_url(feria_2027, "eventos:mis_propuestas", convocatoria_id=convocatoria.pk))

    with schema_context(feria_2027.schema_name):
        quedan = ArchivoEnEspera.objects.all()
        assert quedan.count() == 1
        assert quedan.get().nombre_original == "de-otra.jpg"


# ── 6 · La barrida, para lo que ninguna salida alcanza ────────


def _huerfano(archivo):
    """Le quita la sesión, que es lo que deja una pestaña cerrada.

    Con `update()` y no `save()` para no tocar `subido_en`, que es
    `auto_now_add` y se reescribiría — la fecha no interviene en nada,
    pero una prueba que la mueva sin querer confunde a quien la lea.
    """
    ArchivoEnEspera.objects.filter(pk=archivo.pk).update(session_key="ya-no-existe")


def test_la_barrida_borra_lo_que_perdio_su_sesion(client, feria_2027, tmp_path, settings):
    """El caso que ninguna de las cuatro salidas cubre: cerrar la pestaña.

    Ni enviar, ni volver al listado, ni abrir el catálogo, ni cerrar
    sesión — la persona cierra el navegador y no vuelve. Sin esto, sus
    archivos se quedan para siempre.

    El criterio **no es una fecha**: es que la sesión que los subió ya no
    exista. `EVT` no cuenta días porque aquí no hay borradores que
    conservar.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)
    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen("huerfana.jpg")})

    with schema_context(feria_2027.schema_name):
        colgada = ArchivoEnEspera.objects.get()
        ruta = colgada.archivo.path
        _huerfano(colgada)

    call_command("barrida_espera", "--todas")

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 0
    # Y el archivo también se fue, que es lo que ocupa disco.
    assert not os.path.exists(ruta)


def test_la_barrida_respeta_lo_de_una_sesion_viva(client, feria_2027, tmp_path, settings):
    """Alguien que está llenando el formulario ahora mismo.

    Si la barrida corriera a media captura y se llevara lo suyo, el
    formulario le volvería a pedir los adjuntos sin motivo — y en mitad
    de la noche, que es cuando corre.
    """
    settings.MEDIA_ROOT = tmp_path
    convocatoria, persona, url = _escenario(feria_2027)
    client.force_login(persona)
    client.post(url, {**SIN_TITULO, **LIBRO, "portada_libro": _imagen("en-curso.jpg")})

    call_command("barrida_espera", "--todas")

    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 1


def test_la_barrida_en_seco_no_toca_nada(feria_2027, tmp_path, settings):
    """`--seco` dice qué haría. Es como se comprueba antes de programarla."""
    settings.MEDIA_ROOT = tmp_path
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        en_espera.guardar(
            convocatoria,
            persona,
            ((Documento.Tipo.PORTADA_LIBRO, _imagen("vieja.jpg")),),
            "una-sesion-que-ya-no-existe",
        )

    salida = StringIO()
    call_command("barrida_espera", "--todas", "--seco", stdout=salida)

    assert "vieja.jpg" in salida.getvalue()
    with schema_context(feria_2027.schema_name):
        assert ArchivoEnEspera.objects.count() == 1


def test_la_barrida_exige_saber_sobre_que_ferias_corre():
    """Sin `--feria` ni `--todas` no adivina.

    Un comando programado que por omisión recorra todo es una forma
    barata de borrar de más el día que alguien lo ejecute a mano.
    """
    with pytest.raises(CommandError):
        call_command("barrida_espera")
