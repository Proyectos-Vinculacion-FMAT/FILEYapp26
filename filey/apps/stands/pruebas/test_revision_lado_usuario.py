"""
Los defectos que salió a buscar la revisión del portal del aplicante.

Se revisaron los catorce casos de uso del lado del expositor contra el
código, y lo que aparece aquí es lo que **la documentación pedía y la
pantalla no hacía**. Comparten una forma: la regla estaba bien escrita en
`servicios/` y la pantalla ofrecía algo que esa regla iba a rechazar, o
callaba una cifra sin la cual la decisión no se puede tomar.

Cada prueba cita el paso del caso de uso que la origina, para que el día
que alguien cambie el caso de uso encuentre qué se cae.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria

from ..models import DescuentoAplicado, Documento, Movimiento, Reserva, Solicitud
from ..servicios import configuracion, mapa_json, mapas, pagos, reservas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _mapa():
    return {
        "grid": {"salon": "Salón de pruebas", "cols": 30, "rows": 10,
                 "meters_per_cell": 1.0, "cell_size": 32},
        "stands": [
            {"id": f"A{i}", "label": f"A{i}", "col": i * 3, "row": 0, "w": 3, "h": 2}
            for i in range(1, 6)
        ],
        "decorations": [],
    }


@pytest.fixture
def listo(feria_2027):
    """Una convocatoria con mapa, precio, pronto pago vigente y una expositora."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_mapa())
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("2500")
        cfg.fecha_limite_pronto_pago = timezone.localdate() + timedelta(days=10)
        cfg.instrucciones_pago = "BBVA · CLABE 012 345 678 901 234 567"
        cfg.save()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
    return feria_2027, conv, ana


def _cerrar(feria, conv):
    with schema_context(feria.schema_name):
        conv.estado = Convocatoria.Estado.CERRADA
        conv.save(update_fields=["estado"])


# ── CU-STD-037 A1 · la convocatoria cerrada ───────────────────


def test_con_la_convocatoria_cerrada_el_mapa_se_ve_pero_no_ofrece_agregar(
    client, listo
):
    """A1 paso 2 y 3: se entrega el mapa, la vista no ofrece el carrito."""
    feria, conv, ana = listo
    client.force_login(ana)
    _cerrar(feria, conv)

    cuerpo = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'id="mapa-canvas"' in cuerpo, "el plano tiene que seguir viéndose"
    assert "Ya no se pueden apartar espacios" in cuerpo
    assert 'id="carrito-lateral"' not in cuerpo


def test_con_la_convocatoria_cerrada_el_detalle_no_ofrece_agregar(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)
    _cerrar(feria, conv)

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1")
    ).content.decode()

    assert "6 m²" in cuerpo, "el detalle se sigue leyendo"
    assert "Agregar a mi selección" not in cuerpo


def test_con_la_convocatoria_cerrada_el_carrito_no_ofrece_confirmar(client, listo):
    """El botón que solo puede fallar no se pinta."""
    feria, conv, ana = listo
    client.force_login(ana)
    client.post(
        _url(feria, "stands:carrito", convocatoria_id=conv.pk),
        {"accion": "agregar", "clave": "A1"},
    )
    _cerrar(feria, conv)

    cuerpo = client.get(
        _url(feria, "stands:carrito", convocatoria_id=conv.pk)
    ).content.decode()

    assert "A1" in cuerpo, "lo elegido sigue siendo suyo y se ve"
    assert "Esta convocatoria ya cerró" in cuerpo
    assert "Confirmar la reserva" not in cuerpo


# ── CU-STD-013 paso 2 · el mapa de mi reserva ─────────────────


def test_mis_espacios_viajan_distinguibles_y_los_ajenos_no(listo):
    """`RN-09` esconde lo de los demás, no lo propio.

    Es la única forma que tiene el componente de marcar "el mío": solo
    admite tres estados, y el que sobra cuando los ajenos van colapsados
    es `reservado`.
    """
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        otra = fabricas.persona(correo="otra@ejemplo.com", nombre="Otra")
        suya = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=otra, editorial=fabricas.editorial(otra)
        )
        suya.estado = Solicitud.Estado.ACEPTADA
        suya.fecha_revision = suya.fecha_envio
        suya.save()
        reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        reservas.crear(convocatoria=conv, persona=otra, claves=["A2"])

        mapa = mapas.mapa_de(conv)
        datos = mapa_json.para_el_canvas(
            mapa, costo_m2=Decimal("2500"), mios={"A1"}
        )

    por_clave = {s["id"]: s["status"] for s in datos["stands"]}
    assert por_clave["A1"] == "reservado", "el suyo se distingue"
    assert por_clave["A2"] == "ocupado", "el ajeno sigue colapsado (RN-09)"
    assert por_clave["A3"] == "disponible"


def test_la_cuenta_tiene_una_pestana_con_el_plano(client, listo):
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
    client.force_login(ana)
    url = _url(feria, "stands:cuenta", convocatoria_id=conv.pk)

    resumen = client.get(url).content.decode()
    mapa = client.get(url + "?ver=mapa").content.decode()

    # El canvas **solo** cuando lo piden: son 39 MB por visita.
    assert 'id="mapa-canvas"' not in resumen
    assert 'id="mapa-canvas"' in mapa
    assert "Tus espacios" in mapa
    # Y de consulta: aquí no se aparta nada más (`RN-23`).
    assert "Agregar a mi selección" not in mapa


def test_desde_el_mapa_de_consulta_no_se_agrega_nada(client, listo):
    """Ni siquiera un espacio libre: su editorial ya tiene reserva (`RN-23`).

    El detalle es la misma vista para el mapa de elegir y para el de
    consultar, así que es aquí donde se decide — sin esto, un espacio
    verde ofrecería meterse a un carrito que ya no lleva a ninguna parte.
    """
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
    client.force_login(ana)

    libre = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A3")
    ).content.decode()

    assert "6 m²" in libre, "el detalle se sigue leyendo"
    assert "Agregar a mi selección" not in libre


def test_un_espacio_propio_no_se_anuncia_como_tomado(client, listo):
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1")
    ).content.decode()

    assert "Este espacio es tuyo" in cuerpo
    assert "ya está tomado" not in cuerpo


# ── CU-STD-023 A1 · el pronto pago que caduca ─────────────────


def test_el_pronto_pago_se_retira_si_vence_sin_liquidar(listo):
    """`RN-04`: el descuento es condicional, y hasta hoy no caducaba nunca."""
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        assert reserva.monto_total == Decimal("13500.00")  # 15 000 menos el 10%

        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() - timedelta(days=1)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])

        pagos.caducar_pronto_pago(reserva)
        reserva.refresh_from_db()

        assert reserva.monto_total == Decimal("15000.00")
        assert not reserva.descuentos.filter(
            tipo=DescuentoAplicado.Tipo.PRONTO_PAGO
        ).exists()


def test_quien_liquido_a_tiempo_conserva_el_descuento(listo):
    """"Liquidada" es cubrir el total ya descontado (`RN-04`)."""
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        movimiento = pagos.registrar(
            reserva=reserva, persona=ana, monto=reserva.monto_total,
            metodo="transferencia",
        )
        pagos.validar(movimiento=movimiento, administrador=ana)

        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() - timedelta(days=1)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])

        reserva.refresh_from_db()
        pagos.caducar_pronto_pago(reserva)
        reserva.refresh_from_db()

        assert reserva.monto_total == Decimal("13500.00")
        assert reserva.estado == Reserva.Estado.PAGADA


def test_caducar_es_idempotente_y_no_toca_lo_que_sigue_vigente(listo):
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])

        # La fecha sigue vigente: no se toca.
        pagos.caducar_pronto_pago(reserva)
        reserva.refresh_from_db()
        assert reserva.monto_total == Decimal("13500.00")

        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() - timedelta(days=1)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])

        pagos.caducar_pronto_pago(reserva)
        reserva.refresh_from_db()
        primero = reserva.monto_total
        pagos.caducar_pronto_pago(reserva)
        reserva.refresh_from_db()

        assert reserva.monto_total == primero == Decimal("15000.00")


def test_el_comando_recorre_la_feria(listo):
    """Es lo que hay que poner en el cron mientras no exista la barrida."""
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() - timedelta(days=1)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])

    call_command("caducar_pronto_pago", feria=feria.slug)

    with schema_context(feria.schema_name):
        reserva.refresh_from_db()
        assert reserva.monto_total == Decimal("15000.00")


def test_la_cuenta_dice_cuanto_sube_si_se_pasa_la_fecha(client, listo):
    """`CU-STD-013` paso 5: la fecha sola no deja sopesar nada."""
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
    ).content.decode()

    assert "10% de descuento" in cuerpo
    assert "10 días" in cuerpo
    assert "15000.00" in cuerpo, "a cuánto sube si lo deja pasar"


def test_el_carrito_dice_cuanto_sube_si_se_pasa_la_fecha(client, listo):
    """`CU-STD-012` paso 3, la misma cifra antes de confirmar."""
    feria, conv, ana = listo
    client.force_login(ana)
    client.post(
        _url(feria, "stands:carrito", convocatoria_id=conv.pk),
        {"accion": "agregar", "clave": "A1"},
    )

    cuerpo = client.get(
        _url(feria, "stands:carrito", convocatoria_id=conv.pk)
    ).content.decode()

    assert "10 días" in cuerpo
    assert "sube a" in cuerpo
    assert "15000.00" in cuerpo


# ── CU-STD-016 · el formulario de abono ───────────────────────


def test_con_la_reserva_cubierta_no_se_ofrece_reportar_un_abono(client, listo):
    """La precondición del caso de uso es saldo pendiente mayor que cero."""
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        movimiento = pagos.registrar(
            reserva=reserva, persona=ana, monto=reserva.monto_total,
            metodo="transferencia",
        )
        pagos.validar(movimiento=movimiento, administrador=ana)
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk) + "?ver=pagos"
    ).content.decode()

    assert "Tu reserva está cubierta" in cuerpo
    assert "Reportar el abono" not in cuerpo


def test_lo_que_esta_en_revision_ocupa_sitio(listo):
    """Reportar dos veces la misma transferencia cobraría el doble."""
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        pagos.registrar(
            reserva=reserva, persona=ana, monto=reserva.monto_total,
            metodo="transferencia",
        )

        with pytest.raises(pagos.PagoRechazado) as exc:
            pagos.registrar(
                reserva=reserva, persona=ana, monto=Decimal("100.00"),
                metodo="transferencia",
            )

    assert "en revisión" in str(exc.value)


def test_al_rechazarse_un_abono_el_hueco_vuelve(listo):
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        movimiento = pagos.registrar(
            reserva=reserva, persona=ana, monto=reserva.monto_total,
            metodo="transferencia",
        )
        pagos.rechazar(movimiento=movimiento, administrador=ana, motivo="No llegó")

        otro = pagos.registrar(
            reserva=reserva, persona=ana, monto=reserva.monto_total,
            metodo="transferencia",
        )

        assert otro.estado == Movimiento.Estado.PENDIENTE


# ── CU-STD-014 · el aviso de posible cancelación ──────────────


def test_el_aviso_de_vencida_dice_cuanto_falta_para_el_anticipo(client, listo):
    """Paso 2: es la cifra que decide si alguien paga hoy."""
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        Reserva.objects.filter(pk=reserva.pk).update(
            fecha_vencimiento_anticipo=timezone.now() - timedelta(days=1)
        )
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Se venció el plazo" in cuerpo
    assert "6750.00" in cuerpo, "el 50% de 13 500, que es lo que falta"


# ── ADR-0007 · los archivos no se quedan huérfanos ────────────


def test_borrar_un_documento_borra_su_archivo(listo):
    """Son constancias fiscales: no pueden quedarse en el disco sin fila."""
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        editorial = ana.editorial
        documento = Documento.objects.create(
            tipo=Documento.Tipo.CONSTANCIA_FISCAL,
            archivo=SimpleUploadedFile("csf.pdf", b"%PDF-1.4 rfc"),
            nombre_original="csf.pdf",
            editorial=editorial,
        )
        almacen = documento.archivo.storage
        ruta = documento.archivo.name
        assert almacen.exists(ruta)

        # En lote, que es como se borran de verdad al reemplazar uno.
        Documento.objects.filter(pk=documento.pk).delete()

        assert not almacen.exists(ruta)
