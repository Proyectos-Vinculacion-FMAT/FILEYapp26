"""
Resolver una solicitud y avisar (`CU-STD-006`, `007`, `008`).

Lo interesante no es que el estado cambie. Es el reparto entre las dos
cosas que pasan al dictaminar —se escribe la resolución y se manda un
correo— y qué ocurre cuando la segunda falla.

Tres cosas se vigilan:

1. **Un correo que no sale no deshace un dictamen.** El administrador
   aceptó la solicitud y eso pasó; lo que queda es una notificación
   `fallida` que se puede reintentar (`CU-STD-008` E1).
2. **Dos administradores no resuelven la misma solicitud.** Sin el
   bloqueo de fila los dos pasan la comprobación, el segundo pisa al
   primero y se mandan dos correos contradictorios.
3. **Pedir cambios sin decir cuáles no se puede** (`CU-STD-007` E1): el
   motivo es literalmente el contenido del correo.
"""

from unittest.mock import patch

import pytest
from django.core import mail
from django_tenants.utils import schema_context

from ..models import Notificacion, Solicitud
from ..servicios import dictamen, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _con_solicitud(feria):
    """Una solicitud pendiente y quien la va a revisar."""
    ana = fabricas.persona()
    revisor = fabricas.persona(correo="rita@filey.org", nombre="Rita")
    solicitud = solicitudes.enviar_solicitud(
        convocatoria=fabricas.convocatoria(),
        persona=ana,
        editorial=fabricas.editorial(ana),
    )
    return solicitud, revisor


# ── Las tres resoluciones ─────────────────────────────────────


def test_aceptar_registra_quien_y_cuando(feria_2027):
    with schema_context(feria_2027.schema_name):
        solicitud, revisor = _con_solicitud(feria_2027)

        resuelta = dictamen.aceptar(solicitud, revisor=revisor)

        assert resuelta.estado == Solicitud.Estado.ACEPTADA
        assert resuelta.revisado_por == revisor
        assert resuelta.fecha_revision is not None


def test_rechazar_no_exige_motivo(feria_2027):
    """`CU-STD-006` A2 la describe como una acción directa."""
    with schema_context(feria_2027.schema_name):
        solicitud, revisor = _con_solicitud(feria_2027)

        resuelta = dictamen.rechazar(solicitud, revisor=revisor)

        assert resuelta.estado == Solicitud.Estado.RECHAZADA


def test_pedir_cambios_sin_motivo_se_rechaza(feria_2027):
    """`CU-STD-007` E1: el motivo es el correo que recibe el aplicante."""
    with schema_context(feria_2027.schema_name):
        solicitud, revisor = _con_solicitud(feria_2027)

        with pytest.raises(dictamen.DictamenRechazado):
            dictamen.solicitar_cambios(solicitud, revisor=revisor, motivo="   ")

        solicitud.refresh_from_db()
        assert solicitud.estado == Solicitud.Estado.PENDIENTE


def test_una_solicitud_ya_resuelta_no_se_vuelve_a_resolver(feria_2027):
    """`CU-STD-006` E1: otro administrador pudo adelantarse."""
    with schema_context(feria_2027.schema_name):
        solicitud, revisor = _con_solicitud(feria_2027)
        dictamen.aceptar(solicitud, revisor=revisor)

        with pytest.raises(dictamen.DictamenRechazado):
            dictamen.rechazar(solicitud, revisor=revisor)

        solicitud.refresh_from_db()
        assert solicitud.estado == Solicitud.Estado.ACEPTADA


def test_tras_pedir_cambios_la_solicitud_vuelve_a_estar_viva(feria_2027):
    with schema_context(feria_2027.schema_name):
        solicitud, revisor = _con_solicitud(feria_2027)

        resuelta = dictamen.solicitar_cambios(
            solicitud, revisor=revisor, motivo="Falta la constancia fiscal."
        )

        assert resuelta.esta_viva
        assert resuelta.motivo_peticion == "Falta la constancia fiscal."


# ── El aviso (CU-STD-008) ─────────────────────────────────────


def test_el_dictamen_manda_correo_y_lo_registra(feria_2027):
    with schema_context(feria_2027.schema_name):
        solicitud, revisor = _con_solicitud(feria_2027)
        mail.outbox.clear()

        dictamen.aceptar(solicitud, revisor=revisor)

        assert len(mail.outbox) == 1
        aviso = Notificacion.objects.get()
        assert aviso.tipo == Notificacion.Tipo.APLICACION_ACEPTADA
        assert aviso.estado == Notificacion.Estado.ENVIADA


def test_el_correo_va_al_contacto_de_la_ficha_no_al_de_acceso(feria_2027):
    """Son dos correos distintos a propósito.

    `Persona.correo` es la cuenta de quien tramita; el de la ficha es el
    buzón comercial de la editorial. El resultado de la solicitud le
    interesa a la editorial.
    """
    with schema_context(feria_2027.schema_name):
        solicitud, revisor = _con_solicitud(feria_2027)
        mail.outbox.clear()

        dictamen.aceptar(solicitud, revisor=revisor)

        assert mail.outbox[0].to == ["contacto@mayab.mx"]
        assert solicitud.registro.persona.correo == "ana@ejemplo.com"


def test_el_motivo_de_los_cambios_viaja_en_el_correo(feria_2027):
    with schema_context(feria_2027.schema_name):
        solicitud, revisor = _con_solicitud(feria_2027)
        mail.outbox.clear()

        dictamen.solicitar_cambios(
            solicitud, revisor=revisor, motivo="Falta la constancia fiscal."
        )

        assert "Falta la constancia fiscal." in mail.outbox[0].body


def test_un_correo_que_no_sale_no_deshace_el_dictamen(feria_2027):
    """`CU-STD-008` E1, y la razón de que el aviso vaya fuera de la transacción.

    El administrador aceptó la solicitud y eso pasó. Lo que queda es una
    notificación `fallida` con el motivo, para poder reintentar.
    """
    with schema_context(feria_2027.schema_name):
        solicitud, revisor = _con_solicitud(feria_2027)

        with patch(
            "apps.stands.servicios.avisos.EmailMultiAlternatives.send",
            side_effect=OSError("el proveedor no contestó"),
        ):
            dictamen.aceptar(solicitud, revisor=revisor)

        solicitud.refresh_from_db()
        assert solicitud.estado == Solicitud.Estado.ACEPTADA

        aviso = Notificacion.objects.get()
        assert aviso.estado == Notificacion.Estado.FALLIDA
        assert "no contestó" in aviso.detalle_error


def test_se_puede_reintentar_un_aviso_fallido(feria_2027):
    with schema_context(feria_2027.schema_name):
        solicitud, revisor = _con_solicitud(feria_2027)
        with patch(
            "apps.stands.servicios.avisos.EmailMultiAlternatives.send",
            side_effect=OSError("cayó la red"),
        ):
            dictamen.aceptar(solicitud, revisor=revisor)
        mail.outbox.clear()

        segundo = dictamen.reintentar_aviso(solicitud)

        assert segundo.estado == Notificacion.Estado.ENVIADA
        assert len(mail.outbox) == 1
        # Los dos intentos quedan registrados: el fallido no se reescribe.
        assert Notificacion.objects.count() == 2


def test_una_solicitud_pendiente_no_tiene_resultado_que_avisar(feria_2027):
    with schema_context(feria_2027.schema_name):
        solicitud, _ = _con_solicitud(feria_2027)

        with pytest.raises(ValueError):
            dictamen.reintentar_aviso(solicitud)
