"""
Lo que el formulario rechaza antes de tocar la base (`CU-EVT-002` E1/E2).

La pantalla del prototipo abre la semblanza cuando el nombre tiene algo
escrito y no deja agregar a la siguiente persona hasta que la anterior
está completa. Eso es comodidad; **lo que impide de verdad que se guarde
media persona es esto**, y por eso las pruebas de la cascada mandan datos
como los mandaría un POST a mano, sin pasar por la pantalla.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from ..formularios import FORMULARIO_POR_TIPO, PresentacionLibroForm, SolicitudForm
from ..models import MAX_SINOPSIS, MAX_SINOPSIS_PUBLICACION, MODELO_POR_TIPO

COMUNES = {
    "institucion": "Editorial La Nave",
    "cargo": "Coordinadora editorial",
    "titulo_actividad": "El mar que nos habita",
    "nombre_organizador_organizacion": "Editorial La Nave",
    "nombre_moderador": "",
    "publico_objetivo": ["publico_general"],
    "sinopsis": "Una conversación sobre la memoria del puerto.",
    "requiere_constancia": "on",
    "comentarios": "",
    "bases_aceptadas": "on",
}


def solicitud(**cambios):
    return SolicitudForm({**COMUNES, **cambios})


# ── Los ocho formularios y las ocho tablas ────────────────────


def test_cada_tipo_tiene_su_formulario():
    """Los dos mapas crecen juntos o no crecen.

    Agregar un tipo con su tabla pero sin su formulario deja una opción
    que se puede elegir y no se puede llenar.
    """
    assert set(FORMULARIO_POR_TIPO) == set(MODELO_POR_TIPO)


# ── Lo común ──────────────────────────────────────────────────


def test_sin_publico_no_pasa():
    """Al menos uno: es lo que dice el CU y lo que el comité necesita."""
    formulario = solicitud(publico_objetivo=[])
    assert not formulario.is_valid()
    assert "publico_objetivo" in formulario.errors


def test_sin_aceptar_las_bases_no_pasa():
    """La aceptación es expresa y se guarda con la propuesta."""
    formulario = SolicitudForm({k: v for k, v in COMUNES.items() if k != "bases_aceptadas"})
    assert not formulario.is_valid()
    assert "bases_aceptadas" in formulario.errors


def test_la_constancia_sin_marcar_es_una_respuesta():
    """Una casilla, no un sí/no que haya que contestar.

    Dejarla sin marcar significa «no la necesito», que es la opción
    inofensiva: nadie se queda sin constancia por descuido, porque quien
    la quiere la pide. Por eso no lleva asterisco y no bloquea el envío.
    """
    formulario = SolicitudForm(
        {k: v for k, v in COMUNES.items() if k != "requiere_constancia"}
    )
    assert formulario.is_valid(), formulario.errors
    assert formulario.cleaned_data["requiere_constancia"] is False


def test_marcarla_la_pide():
    formulario = solicitud(requiere_constancia="on")
    assert formulario.is_valid(), formulario.errors
    assert formulario.cleaned_data["requiere_constancia"] is True


def test_el_publico_se_guarda_como_lista():
    """Filtrar por público es un `contains`, no recorrer una cadena."""
    formulario = solicitud(publico_objetivo=["academico", "infantil"])
    assert formulario.is_valid(), formulario.errors
    assert formulario.cleaned_data["publico_objetivo"] == ["academico", "infantil"]


# ── Los topes de la sinopsis ──────────────────────────────────


def test_la_sinopsis_de_una_actividad_se_acota_a_dos_mil():
    formulario = SolicitudForm({**COMUNES, "sinopsis": "x" * (MAX_SINOPSIS + 1)})
    assert not formulario.is_valid()
    assert "sinopsis" in formulario.errors


def test_la_de_una_publicacion_admite_cuatro_mil():
    """La sinopsis de un libro pide más espacio que la de una charla.

    La columna admite el tope mayor y quien acota a los demás es el
    formulario: subirlo mañana no obliga a una migración.
    """
    largo = SolicitudForm({**COMUNES, "sinopsis": "x" * 3000}, es_publicacion=True)
    assert largo.is_valid(), largo.errors

    demasiado = SolicitudForm(
        {**COMUNES, "sinopsis": "x" * (MAX_SINOPSIS_PUBLICACION + 1)},
        es_publicacion=True,
    )
    assert not demasiado.is_valid()


# ── La cascada de personas ────────────────────────────────────


def test_una_actividad_sin_nadie_no_pasa():
    formulario = FORMULARIO_POR_TIPO["conversatorio"]({})
    assert not formulario.is_valid()
    assert "nombre_participante_1" in formulario.errors


def test_media_persona_no_pasa():
    """Nombre sin semblanza no se puede mandar a un comité."""
    formulario = FORMULARIO_POR_TIPO["conversatorio"](
        {"nombre_participante_1": "Elena Poniatowska"}
    )
    assert not formulario.is_valid()
    assert "semblanza_participante_1" in formulario.errors


def test_una_semblanza_sin_su_nombre_tampoco():
    """El caso que la pantalla impide y un POST a mano no."""
    formulario = FORMULARIO_POR_TIPO["conversatorio"](
        {"semblanza_participante_1": "Escritora y periodista."}
    )
    assert not formulario.is_valid()
    assert "nombre_participante_1" in formulario.errors


def test_no_se_puede_dejar_un_hueco_en_medio():
    """El 3 lleno con el 2 vacío rompe «los participantes, en orden».

    Cualquier listado que recorra las columnas se saltaría a alguien o
    contaría de menos.
    """
    formulario = FORMULARIO_POR_TIPO["conversatorio"](
        {
            "nombre_participante_1": "Elena Poniatowska",
            "semblanza_participante_1": "Escritora.",
            "nombre_participante_3": "Juan Villoro",
            "semblanza_participante_3": "Escritor.",
        }
    )
    assert not formulario.is_valid()
    assert "nombre_participante_3" in formulario.errors


def test_dos_participantes_seguidos_si_pasan():
    formulario = FORMULARIO_POR_TIPO["conversatorio"](
        {
            "nombre_participante_1": "Elena Poniatowska",
            "semblanza_participante_1": "Escritora.",
            "nombre_participante_2": "Juan Villoro",
            "semblanza_participante_2": "Escritor.",
        }
    )
    assert formulario.is_valid(), formulario.errors


# ── Presentación de libro (`A1`) ──────────────────────────────


def libro(**cambios):
    datos = {
        "titulo_publicacion": "El mar que nos habita",
        "tipo_presentador": "autor",
        "nombre_editorial": "La Nave",
        "nombre_autor_1": "Elena Poniatowska",
        "semblanza_autor_1": "Escritora y periodista.",
        "autor_1_participa": "on",
    }
    archivos = {
        "retrato_autor": SimpleUploadedFile("autora.jpg", b"img"),
        "portada_libro": SimpleUploadedFile("portada.jpg", b"img"),
    }
    return PresentacionLibroForm({**datos, **cambios}, archivos)


def test_el_libro_completo_pasa():
    formulario = libro()
    assert formulario.is_valid(), formulario.errors


def test_el_libro_sin_sus_archivos_no_pasa():
    """`A1`: la fotografía del autor y la portada son obligatorias."""
    formulario = PresentacionLibroForm(
        {
            "titulo_publicacion": "El mar que nos habita",
            "tipo_presentador": "autor",
            "nombre_editorial": "La Nave",
            "nombre_autor_1": "Elena Poniatowska",
            "semblanza_autor_1": "Escritora.",
        }
    )
    assert not formulario.is_valid()
    assert "retrato_autor" in formulario.errors
    assert "portada_libro" in formulario.errors


def test_los_presentadores_de_un_libro_son_opcionales():
    """Pero si se pone uno, va completo: la cascada también los cubre."""
    completo = libro()
    assert completo.is_valid(), completo.errors

    a_medias = libro(nombre_participante_1="Ana Pech")
    assert not a_medias.is_valid()
    assert "semblanza_participante_1" in a_medias.errors


def test_cada_autor_lleva_su_casilla_de_participacion():
    """Cinco autores, cinco respuestas: no un sí/no para «el autor».

    Y sin marcar significa que no estará: nadie queda apuntado al
    programa por no haber desmarcado una casilla.
    """
    formulario = libro(
        nombre_autor_2="Juan Villoro",
        semblanza_autor_2="Escritor.",
        # `autor_2_participa` sin marcar: ese no estará presente. Con que
        # asista el 1 basta, así que no hace falta presentador.
    )
    assert formulario.is_valid(), formulario.errors
    assert formulario.cleaned_data["autor_1_participa"] is True
    assert formulario.cleaned_data["autor_2_participa"] is False


# ── Que la actividad no se quede sin nadie delante ────────────
#
# Quien sostiene una presentación es un autor que asista o un presentador.
# Basta con uno de los dos; pedir el segundo sobraría.


def test_sin_ningun_autor_presente_hace_falta_un_presentador():
    """El caso que la regla existe para atrapar: no va nadie."""
    formulario = libro(
        nombre_autor_1="Elena Poniatowska",
        semblanza_autor_1="Escritora.",
        autor_1_participa="",  # sin marcar
    )
    assert not formulario.is_valid()
    assert "nombre_participante_1" in formulario.errors


def test_con_un_autor_presente_los_presentadores_sobran():
    """Basta uno: el autor 1 asiste, y con eso la actividad tiene quién."""
    formulario = libro()  # `autor_1_participa` marcado
    assert formulario.is_valid(), formulario.errors


def test_basta_con_que_asista_uno_de_varios():
    """Tres autores, dos ausentes: sigue habiendo quien la sostenga.

    Es el caso que distingue esta regla de «que no falte ninguno»: no se
    exige que estén todos, se exige que esté alguien.
    """
    formulario = libro(
        nombre_autor_2="Juan Villoro",
        semblanza_autor_2="Escritor.",
        nombre_autor_3="Ana Pech",
        semblanza_autor_3="Editora.",
        # solo el 1 va marcado
    )
    assert formulario.is_valid(), formulario.errors


def test_sin_autores_presentes_pero_con_presentador_si_pasa():
    formulario = libro(
        autor_1_participa="",
        nombre_participante_1="Jorge Cortés Ancona",
        semblanza_participante_1="Crítico literario.",
    )
    assert formulario.is_valid(), formulario.errors


def test_un_nombre_escrito_no_es_alguien_que_asiste():
    """Solo cuenta la marca, no el nombre.

    Con el nombre puesto y la casilla en blanco, ese autor no sostiene
    nada: escribir a alguien no lo trae a la feria.
    """
    formulario = libro(autor_1_participa="")
    assert not formulario.is_valid()


def test_lo_mismo_vale_para_los_editores_de_una_revista():
    from apps.eventos.formularios import PresentacionRevistaForm

    def revista(**cambios):
        datos = {
            "titulo_publicacion": "Cuadernos del Mayab",
            "tipo_presentador": "editor",
            "nombre_editorial": "La Nave",
            "nombre_editor_1": "Ana Pech",
            "semblanza_editor_1": "Editora.",
        }
        return PresentacionRevistaForm(
            {**datos, **cambios},
            {"portada_revista": SimpleUploadedFile("portada.jpg", b"img")},
        )

    assert not revista().is_valid()  # sin marcar que asista
    assert revista(editor_1_participa="on").is_valid()


# ── Los campos largos ─────────────────────────────────────────


def test_los_campos_largos_no_llenan_la_pantalla():
    """Django pinta diez renglones y una semblanza sola tapaba el resto."""
    from apps.eventos.formularios import RENGLONES

    assert str(SolicitudForm()["sinopsis"]).count(f'rows="{RENGLONES}"') == 1
    assert str(libro()["semblanza_autor_1"]).count(f'rows="{RENGLONES}"') == 1


def test_los_adjuntos_salen_emparejados_con_su_tipo():
    """Lo que consume el servicio para crear los `Documento`."""
    formulario = libro()
    assert formulario.is_valid(), formulario.errors
    tipos = [tipo for tipo, _ in formulario.documentos()]
    assert tipos == ["retrato_autor", "portada_libro"]


def test_un_adjunto_con_la_extension_equivocada_no_pasa():
    """Lo que pide la convocatoria en papel: la foto va en JPG o PNG.

    Es distinto de la lista blanca de seguridad que aplica
    `DocumentoAdmisible` al guardar (`ADR-0007`), que es más amplia: ésta
    es del formato que el programa necesita para imprimirse.
    """
    formulario = PresentacionLibroForm(
        {
            "titulo_publicacion": "El mar que nos habita",
            "tipo_presentador": "autor",
            "nombre_editorial": "La Nave",
            "nombre_autor_1": "Elena Poniatowska",
            "semblanza_autor_1": "Escritora.",
        },
        {
            "retrato_autor": SimpleUploadedFile("autora.pdf", b"pdf"),
            "portada_libro": SimpleUploadedFile("portada.jpg", b"img"),
        },
    )
    assert not formulario.is_valid()
    assert "retrato_autor" in formulario.errors


def test_los_tipos_sin_adjuntos_no_devuelven_ninguno():
    formulario = FORMULARIO_POR_TIPO["charla"](
        {
            "nombre_participante_1": "Elena Poniatowska",
            "semblanza_participante_1": "Escritora.",
        }
    )
    assert formulario.is_valid(), formulario.errors
    assert list(formulario.documentos()) == []
