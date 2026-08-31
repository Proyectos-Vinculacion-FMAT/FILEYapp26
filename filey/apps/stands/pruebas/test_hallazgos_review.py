"""
Los cinco agujeros que encontró el code review del 2026-08-30.

Cada uno se reprodujo antes de arreglarlo, y lo que hay aquí es esa
reproducción convertida en prueba. Están juntos y no repartidos por los
archivos de su caso de uso a propósito: lo que tienen en común no es el
caso de uso sino **cómo se escaparon** —una guarda que vivía solo en la
plantilla, una condición de más, un conjunto de estados que se quedó
corto—, y leerlos seguidos es lo que enseña el patrón.

1. `RN-14` no se cumplía con un descuento del 100% (`_estado_para`).
2. Los dos servicios de descuento no miraban el estado (`RN-01`, `RN-11`).
3. Una solicitud `aceptada` no impedía enviar otra (`RN-22`, `RN-16`).
4. Un `?estado=` desconocido dejaba la cola de A5 filtrada y sin marcar.
5. Un archivo perdido del almacén daba un 500 (`CU-STD-005` E1).
"""

from decimal import Decimal

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Documento, Editorial, Movimiento, Reserva, Solicitud, Stand
from ..servicios import archivos, configuracion, mapas, pagos, reservas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _admin(feria, correo="rita@filey.org"):
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


def _pdf(nombre="respaldo.pdf"):
    return SimpleUploadedFile(nombre, b"%PDF-1.4 respaldo")


@pytest.fixture
def con_reserva(feria_2027):
    """Una reserva de $15 000 —6 m² a $2 500— sin abonos ni descuentos."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(
            convocatoria=conv,
            datos={
                "grid": {"salon": "S", "cols": 30, "rows": 10,
                         "meters_per_cell": 1.0, "cell_size": 32},
                "stands": [{"id": "A1", "label": "A1", "col": 0, "row": 0,
                            "w": 3, "h": 2}],
                "decorations": [],
            },
        )
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("2500")
        cfg.save(update_fields=["costo_m2"])
        ana = fabricas.persona()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
    return feria_2027, conv, ana, reserva


# ── 1 · RN-14 con un total de cero ────────────────────────────


def test_un_descuento_del_100_deja_la_reserva_pagada(con_reserva, django_capture_on_commit_callbacks):
    """`RN-14`: cubierto el total, la reserva queda pagada.

    Un total de cero **está cubierto**. Antes se quedaba en `confirmada`
    para siempre: sin correo de liquidación, sin espacios en `ocupado` y
    con la barra de A4 marcando 100% al lado de la insignia equivocada.
    """
    feria, _, ana, reserva = con_reserva
    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            al_dia = pagos.aplicar_descuento_especial(
                reserva=reserva, administrador=ana,
                porcentaje=100, motivo="convenio institucional",
            )

        assert al_dia.monto_total == Decimal("0.00")
        assert al_dia.estado == Reserva.Estado.PAGADA
        # `RN-10`: y sus espacios pasan a ocupado, que es lo que hace que
        # la ocupación del panel cuente ese recinto como vendido.
        assert Stand.objects.get(clave="A1").estado == Stand.Estado.OCUPADO


def test_el_100_por_ciento_avisa_de_la_liquidacion(con_reserva, mailoutbox, django_capture_on_commit_callbacks):
    """`CU-STD-027`: y con el correo, que antes tampoco salía."""
    feria, _, ana, reserva = con_reserva
    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            pagos.aplicar_descuento_especial(
                reserva=reserva, administrador=ana,
                porcentaje=100, motivo="convenio",
            )

    assert [m.subject for m in mailoutbox] == ["Tu reserva está liquidada"]


def test_una_reserva_normal_sigue_confirmandose_al_anticipo(con_reserva):
    """La contraprueba: quitar la guarda no adelantó ningún umbral."""
    feria, _, ana, reserva = con_reserva
    with schema_context(feria.schema_name):
        abono = pagos.registrar(
            reserva=reserva, persona=ana, monto=Decimal("7500.00"),
            metodo="transferencia", archivo=_pdf(),
        )
        al_dia = pagos.validar(movimiento=abono, administrador=ana)

    assert al_dia.estado == Reserva.Estado.CONFIRMADA


# ── 2 · los descuentos, solo sobre reservas vivas ─────────────


def test_no_se_descuenta_una_reserva_cancelada(con_reserva):
    """`RN-01` acota los descuentos a las reservas vivas; `RN-11` cierra.

    Antes esto reescribía `monto_total` de una cancelada —de $15 000 a
    $7 500— y nada protestaba: la única guarda era `{% if esta_viva %}`
    en la plantilla de A4, y la vista despacha la acción sin volver a
    preguntar.
    """
    feria, _, ana, reserva = con_reserva
    with schema_context(feria.schema_name):
        reservas.cancelar(reserva=reserva, administrador=ana, motivo="prueba")

        with pytest.raises(pagos.PagoRechazado, match="cancelada"):
            pagos.aplicar_descuento_especial(
                reserva=Reserva.objects.get(pk=reserva.pk),
                administrador=ana, porcentaje=50, motivo="post mortem",
            )

        # Y el importe sigue siendo el que esa reserva costó.
        assert Reserva.objects.get(pk=reserva.pk).monto_total == Decimal("15000.00")


def test_no_se_retira_el_descuento_de_una_cancelada(con_reserva):
    """La otra mitad: retirar sube el total, y tampoco sobre una cerrada."""
    feria, _, ana, reserva = con_reserva
    with schema_context(feria.schema_name):
        pagos.aplicar_descuento_especial(
            reserva=reserva, administrador=ana, porcentaje=20, motivo="convenio"
        )
        reservas.cancelar(reserva=reserva, administrador=ana)
        con_descuento = Reserva.objects.get(pk=reserva.pk).monto_total

        with pytest.raises(pagos.PagoRechazado, match="cancelada"):
            pagos.retirar_descuento_especial(
                reserva=Reserva.objects.get(pk=reserva.pk), administrador=ana
            )

        assert Reserva.objects.get(pk=reserva.pk).monto_total == con_descuento


def test_sobre_una_reserva_viva_el_descuento_sigue_entrando(con_reserva):
    """La contraprueba: la guarda no cerró el camino bueno."""
    feria, _, ana, reserva = con_reserva
    with schema_context(feria.schema_name):
        al_dia = pagos.aplicar_descuento_especial(
            reserva=reserva, administrador=ana, porcentaje=10, motivo="convenio"
        )

    assert al_dia.monto_total == Decimal("13500.00")


# ── 3 · una aceptada ocupa el registro ────────────────────────


def test_con_una_aceptada_no_se_envia_otra_solicitud(con_reserva):
    """`RN-22` abre la reaplicación **tras un rechazo**, no tras entrar.

    Antes salían dos filas del mismo registro —una `aceptada` y una
    `pendiente`—: la cola de A1 enseñaba a alguien que ya era expositor,
    y rechazar esa segunda no le quitaba la habilitación, porque `RN-16`
    la lee de la primera.
    """
    feria, conv, ana, _ = con_reserva
    with schema_context(feria.schema_name):
        ficha = Editorial.objects.get(persona=ana)

        with pytest.raises(solicitudes.EnvioRechazado, match="ya fue aceptada"):
            solicitudes.enviar_solicitud(
                convocatoria=conv, persona=ana, editorial=ficha
            )

        assert Solicitud.objects.filter(registro__persona=ana).count() == 1


def test_la_base_tambien_lo_impide(con_reserva):
    """No solo el servicio: dos envíos a la vez pasarían la comprobación.

    Es la misma razón por la que la restricción existía para las vivas.
    """
    feria, conv, ana, _ = con_reserva
    with schema_context(feria.schema_name):
        aceptada = Solicitud.objects.get(registro__persona=ana)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Solicitud.objects.create(
                    registro=aceptada.registro,
                    editorial=aceptada.editorial,
                    estado=Solicitud.Estado.PENDIENTE,
                )


def test_tras_un_rechazo_si_se_vuelve_a_aplicar(feria_2027):
    """La contraprueba, que es justo lo que `RN-22` protege."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        ana = fabricas.persona()
        primera = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        primera.estado = Solicitud.Estado.RECHAZADA
        primera.fecha_revision = primera.fecha_envio
        primera.save()

        segunda = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=Editorial.objects.get(persona=ana)
        )

        assert segunda.pk != primera.pk
        assert segunda.estado == Solicitud.Estado.PENDIENTE


# ── 4 · el `?estado=` que no reconocemos ──────────────────────


def test_un_estado_desconocido_no_deja_la_cola_filtrada_a_escondidas(
    client, con_reserva
):
    """A5 filtra por pendientes cuando no le piden nada, y lo dice.

    Con basura en el parámetro seguía filtrando pero ningún chip salía
    marcado: la pantalla decía «sin filtro» enseñando una lista filtrada.
    """
    feria, conv, ana, reserva = con_reserva
    with schema_context(feria.schema_name):
        pagos.registrar(
            reserva=reserva, persona=ana, monto=Decimal("1000.00"),
            metodo="transferencia", archivo=_pdf(),
        )
    client.force_login(_admin(feria))

    respuesta = client.get(
        _url(feria, "stands:pagos", convocatoria_id=conv.pk) + "?estado=basura"
    )

    assert respuesta.context["estado_activo"] == ""
    # El primer chip —«Por validar»— es el que está aplicado.
    assert respuesta.context["chips"][0]["activo"] is True


def test_un_estado_conocido_sigue_marcando_su_chip(client, con_reserva):
    """La contraprueba: normalizar no se llevó por delante el filtro."""
    feria, conv, _, _ = con_reserva
    client.force_login(_admin(feria))

    respuesta = client.get(
        _url(feria, "stands:pagos", convocatoria_id=conv.pk)
        + f"?estado={Movimiento.Estado.VALIDADO}"
    )

    assert respuesta.context["estado_activo"] == Movimiento.Estado.VALIDADO
    assert respuesta.context["chips"][0]["activo"] is False


# ── 5 · el archivo que ya no está ─────────────────────────────


def test_un_documento_perdido_del_almacen_da_404_y_no_500(client, feria_2027):
    """`CU-STD-005` E1: la incidencia es de ese documento, no de la página.

    Antes el `FileNotFoundError` salía sin capturar y quien revisaba una
    solicitud se encontraba un error del servidor.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        adjunto = fabricas.editorial(ana).documentos.create(
            tipo=Documento.Tipo.CONSTANCIA_FISCAL,
            archivo=SimpleUploadedFile("csf.pdf", b"%PDF-1.4 secreto"),
            nombre_original="csf.pdf",
        )
        # Se borra el fichero y se deja la fila: es exactamente lo que
        # pasa con un volumen que no se montó o una restauración a medias.
        adjunto.archivo.storage.delete(adjunto.archivo.name)

    client.force_login(ana)
    respuesta = client.get(
        _url(feria_2027, "stands:documento", documento_id=adjunto.pk)
    )

    assert respuesta.status_code == 404


def test_el_servicio_lo_dice_con_su_propia_excepcion(feria_2027):
    """Y no con un `FileNotFoundError` suelto: son dos incidencias."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        adjunto = fabricas.editorial(ana).documentos.create(
            tipo=Documento.Tipo.CONSTANCIA_FISCAL,
            archivo=SimpleUploadedFile("csf.pdf", b"%PDF-1.4 secreto"),
            nombre_original="csf.pdf",
        )
        adjunto.archivo.storage.delete(adjunto.archivo.name)

        with pytest.raises(archivos.ArchivoNoDisponible):
            archivos.entregar(adjunto)
