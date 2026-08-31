"""
A qué buzón salió cada aviso (`CU-STD-008` E1).

Estas pruebas nacen de una pregunta que el sistema no sabía contestar:
«¿por qué no llegó el correo de cambios solicitados?». La tabla decía
`enviada` y nada más — ni a qué dirección, ni con qué acuse del
proveedor—, así que la única forma de responder era abrir la base y
recomponer la dirección desde la ficha… que se puede haber corregido
desde entonces.

`enviada` significa **«el proveedor aceptó la petición»**, no «llegó al
buzón». El rebote, el filtro de spam y la supresión pasan después y solo
constan del lado del proveedor: por eso se guarda su acuse, que es lo
que permite casar una fila de aquí con una línea de allá.
"""

import pytest
from django.core import mail
from django_tenants.utils import schema_context

from ..models import Notificacion, Solicitud
from ..servicios import dictamen
from .test_flujo_expositor import _aplica, escenario  # noqa

pytestmark = pytest.mark.django_db


def _dictaminar(feria, solicitud, revisor, accion):
    with schema_context(feria.schema_name):
        return getattr(dictamen, accion)(
            solicitud, revisor=revisor, **({} if accion == "aceptar" else {"motivo": "falta la constancia"})
        )


# ── Los tres desenlaces avisan, no solo el de aceptada ────────


@pytest.mark.parametrize(
    "accion, tipo",
    [
        ("aceptar", Notificacion.Tipo.APLICACION_ACEPTADA),
        ("rechazar", Notificacion.Tipo.APLICACION_RECHAZADA),
        ("solicitar_cambios", Notificacion.Tipo.APLICACION_CAMBIOS),
    ],
)
def test_cada_desenlace_manda_su_correo(escenario, accion, tipo):
    """Los tres, y con su propio tipo: no es que «el de aceptada funcione».

    Se comprueban aquí juntos y parametrizados a propósito. Repartidos
    en tres pruebas es donde se cuela que dos pasen y una no exista.
    """
    feria, conv, ana = escenario
    solicitud = _aplica(feria, conv, ana)
    mail.outbox.clear()

    _dictaminar(feria, solicitud, ana, accion)

    assert len(mail.outbox) == 1
    with schema_context(feria.schema_name):
        aviso = Notificacion.objects.get(solicitud=solicitud)
    assert aviso.tipo == tipo
    assert aviso.estado == Notificacion.Estado.ENVIADA


def test_el_motivo_va_dentro_del_correo_de_cambios(escenario):
    """`CU-STD-007` E1: el motivo **es** el contenido del correo."""
    feria, conv, ana = escenario
    solicitud = _aplica(feria, conv, ana)
    mail.outbox.clear()

    _dictaminar(feria, solicitud, ana, "solicitar_cambios")

    assert "falta la constancia" in mail.outbox[0].body


# ── El rastro de a dónde fue ──────────────────────────────────


def test_se_guarda_la_direccion_que_se_uso(escenario):
    feria, conv, ana = escenario
    solicitud = _aplica(feria, conv, ana)

    _dictaminar(feria, solicitud, ana, "solicitar_cambios")

    with schema_context(feria.schema_name):
        aviso = Notificacion.objects.get(solicitud=solicitud)
        esperada = solicitud.datos_editorial.get("correo_electronico") or ana.correo
    assert aviso.destino == esperada
    assert mail.outbox[-1].to == [esperada]


def test_la_direccion_guardada_es_la_de_la_ficha_no_la_de_la_cuenta(escenario):
    """Son cosas distintas —la cuenta de quien tramita frente al buzón
    comercial de la editorial— y es la confusión que hace buscar el
    correo en la bandeja equivocada."""
    feria, conv, ana = escenario
    solicitud = _aplica(feria, conv, ana)
    with schema_context(feria.schema_name):
        solicitud.datos_editorial["correo_electronico"] = "ventas@editorial.mx"
        solicitud.save(update_fields=["datos_editorial"])

    _dictaminar(feria, solicitud, ana, "rechazar")

    with schema_context(feria.schema_name):
        aviso = Notificacion.objects.get(solicitud=solicitud)
    assert aviso.destino == "ventas@editorial.mx" != ana.correo


def test_sin_acuse_del_proveedor_queda_vacio(escenario):
    """Con `locmem` no hay proveedor que acuse nada, y un campo vacío es
    información correcta: no hubo acuse. No se inventa uno."""
    feria, conv, ana = escenario
    solicitud = _aplica(feria, conv, ana)

    _dictaminar(feria, solicitud, ana, "aceptar")

    with schema_context(feria.schema_name):
        assert Notificacion.objects.get(solicitud=solicitud).referencia_externa == ""


def test_el_acuse_del_backend_se_guarda(escenario, monkeypatch):
    """Lo que deja `ResendBackend` en el mensaje acaba en la fila: es lo
    que casa un aviso de aquí con una línea del panel del proveedor."""
    from django.core.mail.backends import locmem

    original = locmem.EmailBackend.send_messages

    def con_acuse(self, mensajes):
        for m in mensajes:
            m.acuse_proveedor = "re_abc123"
        return original(self, mensajes)

    monkeypatch.setattr(locmem.EmailBackend, "send_messages", con_acuse)
    feria, conv, ana = escenario
    solicitud = _aplica(feria, conv, ana)

    _dictaminar(feria, solicitud, ana, "aceptar")

    with schema_context(feria.schema_name):
        aviso = Notificacion.objects.get(solicitud=solicitud)
    assert aviso.referencia_externa == "re_abc123"
