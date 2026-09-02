"""
El acuse de recepción (`CU-EVT-002`, paso 13).

Dos cosas, y la segunda es la que importa de verdad:

1. **El correo lleva el folio.** Es con lo que se identifica la solicitud
   en cualquier trámite posterior; sin él, quien propuso no tiene forma
   de nombrar su propuesta.
2. **Que el correo falle no deshace la propuesta.** Cuando se manda, ya
   está guardada y tiene folio. Un buzón que rebota no puede tirar lo que
   alguien acaba de enviar.
"""

from unittest.mock import patch

import pytest
from django.conf import settings
from django.core import mail
from django.urls import reverse
from django_tenants.utils import schema_context

from ..models import Solicitud
from ..servicios import avisos, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db

CHARLA = {
    "nombre_participante_1": "Elena Poniatowska",
    "semblanza_participante_1": "Escritora y periodista.",
}


def test_el_acuse_lleva_el_folio_y_el_titulo(feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona()
        propuesta = solicitudes.crear(
            convocatoria=convocatoria, persona=persona,
            comunes=fabricas.PROPUESTA, nombre_tipo="charla", detalle=CHARLA,
        )

        mail.outbox.clear()
        assert avisos.avisar_recepcion(propuesta) is True

        assert len(mail.outbox) == 1
        correo = mail.outbox[0]
        assert correo.to == [persona.correo]
        assert propuesta.folio in correo.subject
        assert propuesta.folio in correo.body
        assert propuesta.titulo_actividad in correo.body
        # Y va en texto **y** en HTML: no todos los clientes pintan HTML.
        assert correo.alternatives


def test_el_acuse_no_promete_lo_que_no_puede(feria_2027):
    """Enviar no garantiza aceptación, y el horario lo asigna la feria.

    Es lo mismo que dicen las bases. Un acuse que sonara a «quedaste
    dentro» crearía una expectativa que el dictamen tendría que
    desmentir.
    """
    with schema_context(feria_2027.schema_name):
        propuesta = solicitudes.crear(
            convocatoria=fabricas.convocatoria(), persona=fabricas.persona(),
            comunes=fabricas.PROPUESTA, nombre_tipo="charla", detalle=CHARLA,
        )
        mail.outbox.clear()
        avisos.avisar_recepcion(propuesta)

        cuerpo = mail.outbox[0].body
        assert "pendiente de revisión" in cuerpo
        assert "no garantiza su aceptación" in cuerpo


def test_si_el_correo_falla_la_propuesta_sigue_en_pie(feria_2027):
    """El caso que justifica que `avisar_recepcion` no levante.

    Se simula un transporte que revienta: la solicitud ya está guardada,
    y lo que corresponde es dejar constancia en el log, no perderla.
    """
    with schema_context(feria_2027.schema_name):
        propuesta = solicitudes.crear(
            convocatoria=fabricas.convocatoria(), persona=fabricas.persona(),
            comunes=fabricas.PROPUESTA, nombre_tipo="charla", detalle=CHARLA,
        )

        with patch(
            "django.core.mail.EmailMultiAlternatives.send",
            side_effect=RuntimeError("el buzón rebota"),
        ):
            assert avisos.avisar_recepcion(propuesta) is False

        assert Solicitud.objects.filter(pk=propuesta.pk).exists()


def test_el_envio_por_pantalla_dispara_el_acuse(client, feria_2027, django_capture_on_commit_callbacks):
    """Va en `on_commit`: no se avisa de algo que aún puede deshacerse.

    Sin esa precaución, una propuesta que reventara después de guardarse
    habría mandado ya un correo con un folio que no existe.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
    persona = fabricas.persona()
    url = f"{feria_2027.url.rstrip('/')}" + reverse(
        "eventos:propuesta",
        kwargs={"convocatoria_id": convocatoria.pk},
        urlconf=settings.ROOT_URLCONF,
    )
    client.force_login(persona)
    mail.outbox.clear()

    with django_capture_on_commit_callbacks(execute=True):
        respuesta = client.post(
            url,
            {
                "tipo": "charla",
                "institucion": "Editorial La Nave",
                "cargo": "",
                "titulo_actividad": "El mar que nos habita",
                "nombre_organizador_organizacion": "Editorial La Nave",
                "nombre_moderador": "",
                "publico_objetivo": ["publico_general"],
                "sinopsis": "Una conversación sobre la memoria del puerto.",
                "requiere_constancia": "on",
                "comentarios": "",
                "bases_aceptadas": "on",
                **CHARLA,
            },
        )

    assert respuesta.status_code == 302
    assert len(mail.outbox) == 1
    assert persona.correo in mail.outbox[0].to
