"""
A5 · La cola de pagos por validar y su modal (`CU-STD-018`).

Es la pieza que cerraba el ciclo del dinero: hasta hoy una editorial
reportaba su transferencia, el movimiento nacía `pendiente_validacion` y
**no había ningún camino** para darlo por bueno —ni pantalla, ni admin de
Django, ni comando—. Con eso, ninguna reserva podía llegar nunca a
`confirmada` ni a `pagada`, y los umbrales de `RN-13` y `RN-14` eran
código muerto.

El servicio ya existía y estaba probado; lo que faltaba era la puerta.
"""

from decimal import Decimal

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Movimiento, Reserva, Solicitud
from ..servicios import configuracion, mapas, pagos, reservas, solicitudes
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


@pytest.fixture
def con_abono(feria_2027):
    """Una reserva de $15 000 con un abono de $7 500 esperando validación.

    El monto no es casual: es **exactamente el anticipo** del 50%
    (`RN-02`), para que validarlo cruce el umbral de `RN-13` y se pueda
    comprobar que la reserva se confirma en la misma petición.
    """
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
        abono = pagos.registrar(
            reserva=reserva,
            persona=ana,
            monto=Decimal("7500.00"),
            metodo="transferencia",
            archivo=SimpleUploadedFile("recibo.pdf", b"%PDF banco"),
        )
    return feria_2027, conv, reserva, abono


# ── La cola ───────────────────────────────────────────────────


def test_la_cola_trae_lo_que_espera_decision(client, con_abono):
    feria, conv, _, abono = con_abono
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:pagos", convocatoria_id=conv.pk)
    ).content.decode()

    assert "7500.00" in cuerpo
    assert "Transferencia" in cuerpo
    assert abono.reserva.editorial.nombre in cuerpo


def test_entrar_a_la_cola_ya_es_filtrar(client, con_abono):
    """La pantalla se llama «pagos por validar»: su estado natural es ése.

    Un abono ya resuelto no estorba en la cola del día, y por eso el
    primer chip no dice «Todas» como en las otras dos listas.
    """
    feria, conv, reserva, abono = con_abono
    with schema_context(feria.schema_name):
        otro = pagos.registrar(
            reserva=reserva, persona=reserva.registro.persona,
            monto=Decimal("300.00"), metodo="deposito",
        )
        pagos.rechazar(
            movimiento=otro, administrador=_admin(feria, "otra@filey.org"),
            motivo="No llegó al banco",
        )
    client.force_login(_admin(feria))
    url = _url(feria, "stands:pagos", convocatoria_id=conv.pk)

    cola = client.get(url).content.decode()
    rechazados = client.get(url, {"estado": "rechazado"}).content.decode()

    assert "7500.00" in cola and "300.00" not in cola
    assert "300.00" in rechazados and "7500.00" not in rechazados
    assert "Por validar" in cola, "el primer chip nombra el filtro por omisión"


def test_la_cola_vacia_es_una_buena_noticia(client, feria_2027):
    """No es un error ni un hueco: es que no hay nada que hacer."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
    client.force_login(_admin(feria_2027))

    cuerpo = client.get(
        _url(feria_2027, "stands:pagos", convocatoria_id=conv.pk)
    ).content.decode()

    assert "No hay pagos por validar" in cuerpo


def test_un_participante_no_entra(client, con_abono):
    feria, conv, _, _ = con_abono
    with schema_context(feria.schema_name):
        curiosa = fabricas.persona(correo="curiosa@ejemplo.com", nombre="Curiosa")
    client.force_login(curiosa)

    respuesta = client.get(_url(feria, "stands:pagos", convocatoria_id=conv.pk))

    assert respuesta.status_code == 403


# ── El modal ──────────────────────────────────────────────────


def test_el_modal_y_la_pantalla_suelta_son_la_misma_vista(client, con_abono):
    """Sin JavaScript el mismo enlace abre la página; con él, el modal.

    Que sea una sola vista es lo que impide que las dos digan cifras
    distintas del mismo abono.
    """
    feria, _, _, abono = con_abono
    client.force_login(_admin(feria))
    url = _url(feria, "stands:movimiento", movimiento_id=abono.pk)

    pagina = client.get(url).content.decode()
    modal = client.get(url, headers={"hx-request": "true"}).content.decode()

    assert "<html" in pagina, "la suelta trae su chasis"
    assert "<html" not in modal, "el modal es solo el cuerpo"
    for cuerpo in (pagina, modal):
        assert "7500.00" in cuerpo
        assert "Validar el abono" in cuerpo
    assert 'class="modal-back"' in modal, "y trae su propio velo"


def test_el_modal_anuncia_lo_que_hara_la_validacion(client, con_abono):
    """`CU-STD-018` paso 8, dicho **antes** de pulsar.

    Validar es lo que puede cruzar el 50% (`RN-13`) o el 100%
    (`RN-14`). Enseñar la consecuencia es la diferencia entre decidir y
    calcularla de cabeza con tres cifras sueltas en pantalla.
    """
    feria, _, reserva, abono = con_abono
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:movimiento", movimiento_id=abono.pk)
    ).content.decode()

    assert "Si validas este abono" in cuerpo
    assert "7500.00 de $15000.00" in " ".join(cuerpo.split())
    assert "La reserva pasaría a" in cuerpo
    assert "confirmada" in cuerpo
    assert "Abrir el comprobante" in cuerpo


def test_lo_que_anuncia_es_lo_que_ocurre(client, con_abono):
    """La promesa y el cobro salen de la misma función (`_estado_para`).

    Separarlas es cómo se llega a que la pantalla diga «quedaría
    confirmada» y la validación deje la reserva donde estaba.
    """
    feria, _, reserva, abono = con_abono
    client.force_login(_admin(feria))
    url = _url(feria, "stands:movimiento", movimiento_id=abono.pk)

    anunciado = "confirmada" in client.get(url).content.decode()
    client.post(url, {"accion": "validar"})

    with schema_context(feria.schema_name):
        reserva.refresh_from_db()
    assert anunciado
    assert reserva.estado == Reserva.Estado.CONFIRMADA


def test_un_abono_que_no_alcanza_el_umbral_lo_dice(client, con_abono):
    """Y no promete un cambio de estado que no va a ocurrir."""
    feria, _, reserva, _ = con_abono
    with schema_context(feria.schema_name):
        pequeno = pagos.registrar(
            reserva=reserva, persona=reserva.registro.persona,
            monto=Decimal("100.00"), metodo="deposito",
        )
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:movimiento", movimiento_id=pequeno.pk)
    ).content.decode()

    assert "no alcanza el siguiente umbral" in cuerpo


def test_un_abono_ya_resuelto_no_proyecta_nada(client, con_abono):
    """No hay nada que anunciar de algo que ya ocurrió."""
    feria, _, _, abono = con_abono
    client.force_login(_admin(feria))
    url = _url(feria, "stands:movimiento", movimiento_id=abono.pk)
    client.post(url, {"accion": "validar"})

    cuerpo = client.get(url).content.decode()

    assert "Si validas este abono" not in cuerpo
    assert "Validado" in cuerpo


# ── Validar ───────────────────────────────────────────────────


def test_validar_suma_al_saldo_y_confirma_la_reserva(client, con_abono):
    """`CU-STD-018` pasos 6 a 8, de punta a punta.

    $7 500 sobre $15 000 es justo el anticipo: la reserva queda
    confirmada (`RN-13`) en la misma petición, sin nada que esperar. Es
    lo que estaba escrito y no podía ocurrir, porque nadie podía validar.
    """
    feria, conv, reserva, abono = con_abono
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:movimiento", movimiento_id=abono.pk),
        {"accion": "validar"},
        follow=True,
    )

    assert "Validaste $7500.00" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        abono.refresh_from_db()
        reserva.refresh_from_db()
        assert abono.estado == Movimiento.Estado.VALIDADO
        assert abono.validado_por is not None and abono.fecha_validacion is not None
        assert reserva.monto_abonado == Decimal("7500.00")
        assert reserva.estado == Reserva.Estado.CONFIRMADA


def test_validar_dos_veces_no_cobra_dos_veces(client, con_abono):
    """El servicio ya lo impedía; esto comprueba que la pantalla lo dice."""
    feria, _, reserva, abono = con_abono
    client.force_login(_admin(feria))
    url = _url(feria, "stands:movimiento", movimiento_id=abono.pk)

    client.post(url, {"accion": "validar"})
    respuesta = client.post(url, {"accion": "validar"}, follow=True)

    assert "ya está validado" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        reserva.refresh_from_db()
        assert reserva.monto_abonado == Decimal("7500.00")


# ── Rechazar ──────────────────────────────────────────────────


def test_rechazar_no_toca_el_saldo_y_guarda_el_motivo(client, con_abono):
    feria, _, reserva, abono = con_abono
    client.force_login(_admin(feria))

    client.post(
        _url(feria, "stands:movimiento", movimiento_id=abono.pk),
        {"accion": "rechazar", "motivo": "El comprobante es de otra cuenta."},
    )

    with schema_context(feria.schema_name):
        abono.refresh_from_db()
        reserva.refresh_from_db()
        assert abono.estado == Movimiento.Estado.RECHAZADO
        assert abono.motivo_rechazo == "El comprobante es de otra cuenta."
        assert reserva.monto_abonado == Decimal("0.00")
        assert reserva.estado == Reserva.Estado.POR_CONFIRMAR


def test_el_motivo_es_opcional(client, con_abono):
    """`CU-STD-018` A1 paso 3 lo deja opcional, y el prototipo no.

    Se sigue el caso de uso: la pantalla insiste en que es lo único que
    la editorial va a leer, pero no bloquea el rechazo por no escribirlo.
    """
    feria, _, _, abono = con_abono
    client.force_login(_admin(feria))

    client.post(
        _url(feria, "stands:movimiento", movimiento_id=abono.pk),
        {"accion": "rechazar", "motivo": "  "},
    )

    with schema_context(feria.schema_name):
        abono.refresh_from_db()
        assert abono.estado == Movimiento.Estado.RECHAZADO
        assert abono.motivo_rechazo == ""


def test_lo_rechazado_llega_al_historial_de_la_editorial(client, con_abono):
    """`CU-STD-017`: es donde el motivo cumple su función."""
    feria, conv, reserva, abono = con_abono
    client.force_login(_admin(feria))
    client.post(
        _url(feria, "stands:movimiento", movimiento_id=abono.pk),
        {"accion": "rechazar", "motivo": "El comprobante es de otra cuenta."},
    )

    client.force_login(reserva.registro.persona)
    cuerpo = client.get(
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk) + "?ver=pagos"
    ).content.decode()

    assert "Rechazado" in cuerpo
    assert "El comprobante es de otra cuenta." in cuerpo


def test_sin_accion_no_pasa_nada(client, con_abono):
    feria, _, _, abono = con_abono
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:movimiento", movimiento_id=abono.pk), {}, follow=True
    )

    assert "Elige qué hacer con el abono" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        abono.refresh_from_db()
        assert abono.estado == Movimiento.Estado.PENDIENTE
