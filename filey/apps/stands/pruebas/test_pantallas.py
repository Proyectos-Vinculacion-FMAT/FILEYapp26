"""
Las tres pantallas de `STD` (U1, A1, A2).

Son las primeras vistas de participante que viven **dentro** de una
feria, y eso trae dos cosas que ninguna pantalla anterior había ejercido:

1. **El acceso está en el urlconf de fuera.** Un `reverse("registros:acceso")`
   normal revienta aquí dentro. Es lo que obligó a que
   `requiere_participante` resuelva su destino con `url_publica`.
2. **El catálogo sirve la raíz de la feria**, así que las rutas de un
   módulo tienen que resolverse antes que él.

Lo demás que se vigila es lo de siempre en este proyecto: que administrar
la feria A no conceda nada en la B, y que lo que no corresponde a alguien
no llegue a la respuesta en vez de ocultarse en la plantilla.
"""

from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Documento, Editorial, Solicitud
from ..servicios import dictamen, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


@pytest.fixture
def escenario(feria_2027):
    """Una convocatoria de stands abierta con una solicitud pendiente."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv,
            persona=ana,
            editorial=fabricas.editorial(ana),
        )
    return feria_2027, conv, ana, solicitud


def _admin_de(feria, correo="rita@filey.org"):
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


def _url(feria, nombre, **kwargs):
    """La URL de una vista de stands, con el prefijo de su feria."""
    with schema_context(feria.schema_name):
        return f"{feria.url.rstrip('/')}{reverse(f'stands:{nombre}', kwargs=kwargs)}"


# ── U1 · el aplicante ─────────────────────────────────────────


def test_sin_sesion_manda_al_acceso_global(client, escenario):
    """El bug que esta pantalla destapó.

    `requiere_participante` redirigía con `reverse("registros:acceso")`,
    que **no resuelve dentro de una feria**: ese nombre vive en el
    urlconf público. Hasta ahora no se había notado porque ninguna vista
    de participante vivía dentro de una feria.

    El destino no lleva prefijo de edición, y es lo correcto: la cuenta
    es única en todo el sistema.
    """
    feria, conv, _, _ = escenario

    respuesta = client.get(_url(feria, "solicitud", convocatoria_id=conv.pk))

    assert respuesta.status_code == 302
    assert respuesta.url == "/acceso/"
    assert feria.url not in respuesta.url


def test_el_aplicante_ve_el_estado_de_su_solicitud(client, escenario):
    """`CU-STD-003`: entrar teniendo una solicitud enseña en qué va."""
    feria, conv, ana, _ = escenario
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "solicitud", convocatoria_id=conv.pk)).content.decode()

    assert "en revisión" in cuerpo


def test_con_una_pendiente_no_se_puede_reeditar(client, escenario):
    """Se muestra la fotografía, no el formulario."""
    feria, conv, ana, _ = escenario
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "solicitud", convocatoria_id=conv.pk)).content.decode()

    assert "Enviar solicitud" not in cuerpo
    assert "Ediciones del Mayab" in cuerpo


def test_con_cambios_pedidos_se_ofrece_el_formulario_y_el_motivo(client, escenario):
    """`CU-STD-002`: se corrige y se reenvía, con el motivo a la vista."""
    feria, conv, ana, solicitud = escenario
    with schema_context(feria.schema_name):
        dictamen.solicitar_cambios(
            solicitud, revisor=_admin_de(feria), motivo="Falta la constancia fiscal."
        )
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "solicitud", convocatoria_id=conv.pk)).content.decode()

    assert "Falta la constancia fiscal." in cuerpo
    assert "Reenviar solicitud" in cuerpo


def test_una_convocatoria_de_otro_tipo_no_existe_para_stands(client, escenario):
    """404 y no 403: no es un permiso que falte, es que no es de stands."""
    feria, _, ana, _ = escenario
    with schema_context(feria.schema_name):
        eventos = Convocatoria.objects.create(
            tipo=TipoConvocatoria.EVT,
            nombre="Eventos 2027",
            estado=Convocatoria.Estado.ABIERTA,
        )
    client.force_login(ana)

    respuesta = client.get(_url(feria, "solicitud", convocatoria_id=eventos.pk))

    assert respuesta.status_code == 404


def test_una_convocatoria_cerrada_se_consulta_pero_no_recibe(client, escenario):
    feria, conv, ana, solicitud = escenario
    with schema_context(feria.schema_name):
        solicitud.estado = Solicitud.Estado.RECHAZADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
        conv.estado = Convocatoria.Estado.CERRADA
        conv.save()
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "solicitud", convocatoria_id=conv.pk)).content.decode()

    assert "no está abierta" in cuerpo
    assert "Enviar solicitud" not in cuerpo


def test_enviar_la_solicitud_desde_el_formulario(client, feria_2027):
    """`CU-STD-001` de punta a punta: formulario, archivos y expediente.

    Es el camino que de verdad recorre una editorial, y el que ejerce
    todo lo que la fase montó de una vez: el registro en la convocatoria
    (`FER`), la ficha, los sellos, los documentos en disco (`ADR-0007`) y
    la fotografía.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    datos = {
        **fabricas.FICHA,
        "materiales": ["Libro"],
        "tematicas": ["Literatura"],
        "sello_0": "Fondo Azul",
        "sello_1": "",
        "constancia_fiscal": SimpleUploadedFile("csf.pdf", b"%PDF-1.4 csf"),
        "lista_titulos": SimpleUploadedFile("titulos.pdf", b"%PDF-1.4 lista"),
    }
    respuesta = client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk), datos, follow=True
    )

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        solicitud = Solicitud.objects.get()
        assert solicitud.estado == Solicitud.Estado.PENDIENTE
        assert solicitud.datos_editorial["nombre"] == "Ediciones del Mayab"
        assert solicitud.sellos == ["Fondo Azul"]
        assert solicitud.editorial.total_sellos == 1
        # Los documentos cuelgan de la editorial, no de la solicitud: es
        # lo que permite reenviar sin volver a subirlos (`CU-STD-002` A1).
        tipos = set(solicitud.editorial.documentos.values_list("tipo", flat=True))
        assert tipos == {"constancia_fiscal", "lista_titulos"}


def test_los_archivos_caen_bajo_el_schema_de_su_feria(client, feria_2027):
    """`ADR-0007`: el aislamiento por feria llega también al disco."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        {
            **fabricas.FICHA,
            "materiales": ["Libro"],
            "tematicas": ["Literatura"],
            "constancia_fiscal": SimpleUploadedFile("RFC_ANA_PECH.pdf", b"%PDF"),
            "lista_titulos": SimpleUploadedFile("titulos.pdf", b"%PDF"),
        },
    )

    with schema_context(feria_2027.schema_name):
        doc = Documento.objects.get(tipo="constancia_fiscal")

    assert doc.archivo.name.startswith("feria_2027/documentos/")
    # El nombre original no sobrevive en la ruta: trae datos personales.
    assert "ANA_PECH" not in doc.archivo.name
    # Pero sí se conserva aparte, para poder decirle cuál subió.
    assert doc.nombre_original == "RFC_ANA_PECH.pdf"


def test_faltar_un_documento_no_crea_nada(client, feria_2027):
    """E1: se señala lo que falta y no se envía la solicitud."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    respuesta = client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        {**fabricas.FICHA, "materiales": ["Libro"], "tematicas": ["Literatura"]},
    )

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        assert not Solicitud.objects.exists()
        # Tampoco a medias: sin solicitud no queda ficha ni registro.
        assert not Editorial.objects.exists()


def test_un_envio_rechazado_no_deja_ficha_a_medias(client, feria_2027):
    """La convocatoria puede cerrarse entre el GET y el POST.

    Sin transacción, ese caso guardaría la ficha y los documentos y
    ninguna solicitud: un expediente que existe a medias y que nadie va a
    revisar, porque no está en ninguna cola.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    with patch(
        "apps.stands.views.solicitudes.enviar_solicitud",
        side_effect=solicitudes.EnvioRechazado("se cerró mientras llenabas"),
    ):
        respuesta = client.post(
            _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
            {
                **fabricas.FICHA,
                "materiales": ["Libro"],
                "tematicas": ["Literatura"],
                "constancia_fiscal": SimpleUploadedFile("csf.pdf", b"%PDF"),
                "lista_titulos": SimpleUploadedFile("titulos.pdf", b"%PDF"),
            },
        )

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        assert not Solicitud.objects.exists()
        assert not Editorial.objects.exists()
        assert not Documento.objects.exists()


# ── A1 y A2 · el administrador ────────────────────────────────


def test_la_cola_de_revision_pide_administrar_esta_feria(client, escenario, feria_2028):
    """Administrar otra feria no da acceso a ésta (`ADR-0004`)."""
    feria, conv, _, _ = escenario
    client.force_login(_admin_de(feria_2028, correo="beto@filey.org"))

    respuesta = client.get(_url(feria, "solicitudes", convocatoria_id=conv.pk))

    assert respuesta.status_code == 403


def test_el_aplicante_no_entra_a_la_cola(client, escenario):
    feria, conv, ana, _ = escenario
    client.force_login(ana)

    respuesta = client.get(_url(feria, "solicitudes", convocatoria_id=conv.pk))

    assert respuesta.status_code == 403


def test_la_cola_lista_las_solicitudes(client, escenario):
    feria, conv, _, _ = escenario
    client.force_login(_admin_de(feria))

    cuerpo = client.get(_url(feria, "solicitudes", convocatoria_id=conv.pk)).content.decode()

    assert "Ediciones del Mayab" in cuerpo


def test_el_filtro_de_estado_va_en_la_consulta(client, escenario):
    """Lo que no se pide no llega a la respuesta."""
    feria, conv, _, _ = escenario
    client.force_login(_admin_de(feria))

    url = _url(feria, "solicitudes", convocatoria_id=conv.pk)
    cuerpo = client.get(url, {"estado": "aceptada"}).content.decode()

    assert "Ediciones del Mayab" not in cuerpo
    assert "Ninguna solicitud cumple estos filtros" in cuerpo


def test_el_operador_de_la_plataforma_alcanza_la_cola(client, escenario):
    """`ADR-0005`: sin fila en `AdminFeria`."""
    feria, conv, _, _ = escenario
    client.force_login(
        Persona.objects.create_superuser(correo="raiz@filey.org", password="x")
    )

    respuesta = client.get(_url(feria, "solicitudes", convocatoria_id=conv.pk))

    assert respuesta.status_code == 200


def test_aceptar_desde_el_detalle(client, escenario):
    """`CU-STD-006`: el camino entero, del botón al correo."""
    from django.core import mail

    feria, _, _, solicitud = escenario
    client.force_login(_admin_de(feria))
    mail.outbox.clear()

    respuesta = client.post(
        _url(feria, "detalle_solicitud", solicitud_id=solicitud.pk),
        {"accion": "aceptar", "motivo": ""},
        follow=True,
    )

    assert respuesta.status_code == 200
    with schema_context(feria.schema_name):
        solicitud.refresh_from_db()
    assert solicitud.estado == Solicitud.Estado.ACEPTADA
    assert len(mail.outbox) == 1


def test_pedir_cambios_sin_motivo_no_resuelve_nada(client, escenario):
    """`CU-STD-007` E1, comprobado en el servidor y no solo en el navegador."""
    feria, _, _, solicitud = escenario
    client.force_login(_admin_de(feria))

    client.post(
        _url(feria, "detalle_solicitud", solicitud_id=solicitud.pk),
        {"accion": "cambios", "motivo": "  "},
    )

    with schema_context(feria.schema_name):
        solicitud.refresh_from_db()
    assert solicitud.estado == Solicitud.Estado.PENDIENTE


def test_el_detalle_ensena_la_fotografia_y_no_la_ficha_viva(client, escenario):
    """`RN-22`: se dictamina lo que se envió."""
    feria, _, ana, solicitud = escenario
    with schema_context(feria.schema_name):
        ficha = ana.editorial
        ficha.nombre = "Nombre cambiado despues"
        ficha.save()
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "detalle_solicitud", solicitud_id=solicitud.pk)
    ).content.decode()

    assert "Ediciones del Mayab" in cuerpo
    assert "Nombre cambiado despues" not in cuerpo
