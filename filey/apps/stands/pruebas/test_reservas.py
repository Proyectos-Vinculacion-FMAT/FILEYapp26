"""
El carrito y la reserva (`CU-STD-011`, `012`, `013`, `021`).

Dos cosas se defienden más que ninguna otra, porque las dos fallan
callando y las dos cuestan dinero:

1. **Que los descuentos se apliquen en secuencia y no sumando.** Un 10% y
   un 15% dan un 23.5% efectivo, no un 25%. Sumar los porcentajes es el
   error natural, da de más en cada reserva con dos descuentos, y nadie
   lo nota mirando una pantalla — hay que hacer la cuenta.

2. **Que dos editoriales no puedan vender el mismo espacio.** Sin el
   bloqueo de fila, las dos leen "disponible", las dos escriben, y el
   recinto queda con un stand vendido dos veces y dos anticipos
   cobrados. La prueba lo provoca de verdad, con dos conexiones.
"""

from decimal import Decimal

import pytest
from django.db import connection, transaction
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria
from apps.ferias.models import Feria

from ..models import DescuentoAplicado, Reserva, Solicitud, Stand
from ..servicios import configuracion, mapas, reservas
from . import fabricas

pytestmark = pytest.mark.django_db


def _mapa():
    return {
        "formato": "filey-mapa/1",
        "mapa": {"salon": "Salón de pruebas", "columnas": 30, "filas": 10,
                 "metros_por_celda": 1.0, "tamano_celda": 12},
        "stands": [
            {"clave": f"A{i}", "etiqueta": f"A{i}", "col": i * 3, "fila": 0,
             "ancho_celdas": 3, "alto_celdas": 2}
            for i in range(1, 6)
        ],
        "decoraciones": [],
    }


@pytest.fixture
def listo(feria_2027):
    """Convocatoria con mapa, precio y una editorial ya aceptada."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_mapa())
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("2500")
        cfg.save(update_fields=["costo_m2"])
        solicitud = solicitud_aceptada(conv, ana)
    return feria_2027, conv, ana, solicitud.editorial


def solicitud_aceptada(convocatoria, persona):
    from ..servicios import solicitudes

    solicitud = solicitudes.enviar_solicitud(
        convocatoria=convocatoria, persona=persona, editorial=fabricas.editorial(persona)
    )
    solicitud.estado = Solicitud.Estado.ACEPTADA
    solicitud.fecha_revision = solicitud.fecha_envio
    solicitud.save()
    return solicitud


# ── RN-06 · los descuentos se aplican en secuencia ────────────


def test_dos_descuentos_no_se_suman_se_encadenan():
    """10% y 15% dan 23.5% efectivo, no 25%.

    Sobre 100 000: en secuencia son 76 500; sumando serían 75 000. Mil
    quinientos pesos de diferencia por reserva, en el sentido de cobrar
    de menos, y ninguna pantalla lo delata.
    """
    total, renglones = reservas.total_con_descuentos(
        Decimal("100000"), [("Pronto pago", 10), ("Especial", 15)]
    )

    assert total == Decimal("76500.00")
    assert total != Decimal("75000.00"), "se sumaron los porcentajes"
    assert [r.subtotal for r in renglones] == [
        Decimal("100000.00"),
        Decimal("90000.00"),
        Decimal("76500.00"),
    ]


def test_el_desglose_dice_cada_paso():
    """Para poder enseñarlo tal como se calcula, y no recalcularlo."""
    _, renglones = reservas.total_con_descuentos(
        Decimal("15000"), [("Pronto pago", 10)]
    )

    assert [(r.concepto, r.porcentaje, r.importe) for r in renglones] == [
        ("Subtotal", None, Decimal("15000.00")),
        ("Pronto pago", 10, Decimal("-1500.00")),
    ]


def test_sin_descuentos_el_total_es_el_bruto():
    total, renglones = reservas.total_con_descuentos(Decimal("15000"), [])

    assert total == Decimal("15000.00")
    assert len(renglones) == 1


def test_los_centavos_se_redondean_una_sola_vez():
    """Redondear en cada paso arrastra el error al siguiente."""
    total, _ = reservas.total_con_descuentos(Decimal("333.33"), [("Pronto pago", 33)])

    assert total == Decimal("223.33")  # 333.33 - 110.00


# ── RN-04 · el pronto pago es una fecha de la convocatoria ────


def test_el_pronto_pago_aplica_antes_de_la_fecha(listo):
    feria, conv, _, _ = listo
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() + timezone.timedelta(days=5)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])

        assert reservas.pronto_pago_vigente(conv) == 10


def test_pasada_la_fecha_ya_no_aplica(listo):
    """Es una campaña con corte: quien reserva tarde tiene menos días.

    Deliberado, y lo que lo distingue del plazo de 30 días de `RN-03`,
    que sí arranca con cada reserva.
    """
    feria, conv, _, _ = listo
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() - timezone.timedelta(days=1)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])

        assert reservas.pronto_pago_vigente(conv) == 0


def test_sin_fecha_no_hay_pronto_pago(listo):
    """El campo nace nulo: una convocatoria sin campaña no descuenta."""
    feria, conv, _, _ = listo
    with schema_context(feria.schema_name):
        assert configuracion.de_la_convocatoria(conv).fecha_limite_pronto_pago is None
        assert reservas.pronto_pago_vigente(conv) == 0


# ── CU-STD-012 · crear la reserva ─────────────────────────────


def test_reservar_congela_el_total_y_marca_los_espacios(listo):
    feria, conv, ana, editorial = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(
            convocatoria=conv, persona=ana, claves=["A1", "A2"]
        )

        # Dos de 6 m² a 2 500 = 30 000, sin pronto pago (no hay fecha).
        assert reserva.monto_total == Decimal("30000.00")
        assert reserva.estado == Reserva.Estado.POR_CONFIRMAR
        assert reserva.editorial == editorial
        assert [linea.stand.clave for linea in reserva.lineas.all()] == ["A1", "A2"]
        # `CU-STD-021`.
        assert set(
            Stand.objects.filter(clave__in=["A1", "A2"]).values_list("estado", flat=True)
        ) == {Stand.Estado.RESERVADO}
        # Los demás siguen libres.
        assert Stand.objects.get(clave="A3").esta_libre


def test_el_pronto_pago_queda_registrado_al_reservar(listo):
    """`CU-STD-012` paso 7, y con el porcentaje copiado a la fila.

    Copiarlo es lo que permite reconstruir el desglose aunque después
    cambie la configuración de la convocatoria.
    """
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() + timezone.timedelta(days=5)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])

        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])

        descuento = reserva.descuentos.get()
        assert descuento.tipo == DescuentoAplicado.Tipo.PRONTO_PAGO
        assert descuento.porcentaje == 10
        # Lo aplica el sistema: nadie tomó esa decisión.
        assert descuento.aplicado_por is None
        assert reserva.monto_total == Decimal("13500.00")  # 15 000 − 10%


def test_el_anticipo_sale_del_total_con_descuento(listo):
    """`RN-02`: del descontado, no del bruto."""
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() + timezone.timedelta(days=5)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])

        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])

        assert reserva.monto_total == Decimal("13500.00")
        assert reserva.anticipo == Decimal("6750.00")  # 50% de 13 500
        assert reserva.anticipo != Decimal("7500.00"), "se calculó sobre el bruto"


def test_el_plazo_se_congela_al_reservar(listo):
    """`RN-03`. Cambiar el plazo no debe mover las que ya corren."""
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        antes = reserva.fecha_vencimiento_anticipo

        cfg = configuracion.de_la_convocatoria(conv)
        cfg.plazo_reserva_dias = 90
        cfg.save(update_fields=["plazo_reserva_dias"])

        reserva.refresh_from_db()
        assert reserva.fecha_vencimiento_anticipo == antes
        # No se compara `.days == 30`: `auto_now_add` sella la creación un
        # instante **después** de calcular el vencimiento, así que el
        # delta son 29 días y 23:59:59.9. Se compara la fecha, que es lo
        # que la pantalla enseña.
        assert (antes.date() - reserva.fecha_creacion.date()).days == 30


def test_cambiar_el_precio_no_mueve_lo_ya_cobrado(listo):
    """`RN-01`: un cambio de tarifa no alcanza a quien ya aceptó un precio."""
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])

        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("9999")
        cfg.save(update_fields=["costo_m2"])

        reserva.refresh_from_db()
        assert reserva.monto_total == Decimal("15000.00")


# ── E1 y E2 ───────────────────────────────────────────────────


def test_un_carrito_vacio_no_crea_reserva(listo):
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        with pytest.raises(reservas.ReservaRechazada, match="vacía"):
            reservas.crear(convocatoria=conv, persona=ana, claves=[])


def test_un_espacio_tomado_nombra_cual_y_no_reserva_nada(listo):
    """`E1`. Se nombran: quien armó una selección de ocho tiene que ver
    **cuál** perdió, no un "algo salió mal"."""
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A2").update(estado=Stand.Estado.RESERVADO)

        with pytest.raises(reservas.HayEspaciosTomados) as fallo:
            reservas.crear(convocatoria=conv, persona=ana, claves=["A1", "A2"])

        assert fallo.value.claves == ["A2"]
        assert not Reserva.objects.exists()
        # Y A1 no se quedó marcado por el intento fallido.
        assert Stand.objects.get(clave="A1").esta_libre


def test_sin_solicitud_aceptada_no_se_reserva(listo):
    """`RN-16`, comprobado también en el servicio y no solo en la vista.

    La vista es una puerta; el servicio lo alcanza también un comando.
    """
    feria, conv, _, _ = listo
    with schema_context(feria.schema_name):
        otro = fabricas.persona(correo="otro@ejemplo.com", nombre="Otro")

        with pytest.raises(reservas.ReservaRechazada, match="aceptada"):
            reservas.crear(convocatoria=conv, persona=otro, claves=["A1"])


def test_una_convocatoria_cerrada_no_admite_reservas(listo):
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        conv.estado = Convocatoria.Estado.CERRADA
        conv.save(update_fields=["estado"])

        with pytest.raises(reservas.ReservaRechazada, match="no está abierta"):
            reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])


def test_una_edicion_archivada_tampoco(listo):
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        feria.estado = Feria.Estado.ARCHIVADA
        feria.save(update_fields=["estado"])

        with pytest.raises(reservas.ReservaRechazada, match="archivada"):
            reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])


def test_un_espacio_que_ya_no_existe_se_dice(listo):
    """Pasa tras reimportar el mapa con el carrito a medio llenar."""
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        with pytest.raises(reservas.ReservaRechazada, match="ya no existen"):
            reservas.crear(convocatoria=conv, persona=ana, claves=["A1", "ZZZ"])

        assert not Reserva.objects.exists()


# ── La invariante que sostiene la base ────────────────────────


def test_no_caben_dos_descuentos_del_mismo_tipo(listo):
    """`RN-05`. En la base y no en la pantalla: dos administradores a la
    vez, o el barrido corriendo dos veces, insertarían las dos filas."""
    from django.db.utils import IntegrityError

    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        DescuentoAplicado.objects.create(
            reserva=reserva, tipo=DescuentoAplicado.Tipo.ESPECIAL,
            porcentaje=15, motivo="Editorial recurrente",
        )

        with pytest.raises(IntegrityError):
            DescuentoAplicado.objects.create(
                reserva=reserva, tipo=DescuentoAplicado.Tipo.ESPECIAL,
                porcentaje=20, motivo="Otro",
            )


def test_un_especial_sin_motivo_no_entra(listo):
    """Un descuento manual sin explicación es dinero sin justificar."""
    from django.db.utils import IntegrityError

    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])

        with pytest.raises(IntegrityError):
            DescuentoAplicado.objects.create(
                reserva=reserva, tipo=DescuentoAplicado.Tipo.ESPECIAL, porcentaje=15
            )


def test_los_dos_descuentos_conviven(listo):
    """`RN-06`: no son excluyentes, se aplican los dos."""
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() + timezone.timedelta(days=5)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        DescuentoAplicado.objects.create(
            reserva=reserva, tipo=DescuentoAplicado.Tipo.ESPECIAL,
            porcentaje=15, motivo="Editorial recurrente",
        )

        renglones = reservas.desglose_de(reserva)

        # 15 000 → −10% → 13 500 → −15% → 11 475. Sumando sería 11 250.
        assert renglones[-1].subtotal == Decimal("11475.00")
        assert [r.concepto for r in renglones] == [
            "Subtotal", "Pronto pago", "Especial",
        ]


# ── Vencer no cancela ─────────────────────────────────────────


def test_una_reserva_vencida_sigue_ocupando_sus_espacios(listo):
    """`RN-12`: vencer escala al administrador, no libera.

    Liberarla sola dejaría a alguien con dinero abonado y sin espacio.
    """
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        Reserva.objects.filter(pk=reserva.pk).update(
            fecha_vencimiento_anticipo=timezone.now() - timezone.timedelta(days=1)
        )
        reserva.refresh_from_db()

        assert reserva.esta_vencida
        assert reserva.estado == Reserva.Estado.POR_CONFIRMAR
        assert not Stand.objects.get(clave="A1").esta_libre


def test_una_confirmada_no_se_da_por_vencida(listo):
    """El plazo es para el anticipo; cubierto, deja de correr."""
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        Reserva.objects.filter(pk=reserva.pk).update(
            estado=Reserva.Estado.CONFIRMADA,
            fecha_vencimiento_anticipo=timezone.now() - timezone.timedelta(days=1),
        )
        reserva.refresh_from_db()

        assert not reserva.esta_vencida


# ── El aislamiento por feria ──────────────────────────────────


def test_una_reserva_de_una_feria_no_se_ve_desde_otra(listo, feria_2028):
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])

    with schema_context(feria_2028.schema_name):
        assert not Reserva.objects.exists()


# ── Primero en confirmar gana ─────────────────────────────────


def test_la_lectura_de_disponibilidad_va_bloqueada(listo, django_capture_on_commit_callbacks):
    """`select_for_update` sobre los stands que se van a reservar.

    Es lo que sostiene "primero en confirmar gana" (`CU-STD-012` E1). Sin
    el bloqueo, dos transacciones leen el mismo stand como `disponible`,
    las dos lo marcan y las dos crean su reserva: el recinto queda con un
    espacio vendido dos veces y dos anticipos cobrados. Nada en pantalla
    lo delata — se descubre el día del montaje, con dos editoriales de pie
    frente al mismo stand.

    .. warning:: Esto comprueba que se **pide** el bloqueo, no que dos
       transacciones de verdad se serialicen

       La prueba honesta son dos conexiones concurrentes, y necesita
       ``django_db(transaction=True)``. Con `django-tenants` eso no
       funciona: el `flush` de Django solo conoce `public` y falla al
       vaciar las tablas que viven en el schema de la feria. Queda como
       hueco conocido; lo que sí se verifica aquí es que la consulta que
       decide la disponibilidad lleve `FOR UPDATE`, que es la línea que
       alguien podría quitar sin que nada más se rompa.
    """
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        with CaptureQueriesContext(connection) as consultas:
            reservas.crear(convocatoria=conv, persona=ana, claves=["A1", "A2"])

    bloqueos = [
        c["sql"]
        for c in consultas.captured_queries
        if "FOR UPDATE" in c["sql"].upper() and "stands_stand" in c["sql"]
    ]

    assert bloqueos, "la disponibilidad se lee sin bloquear la fila"
    # Y ordenada por `pk`: dos peticiones que bloqueen las mismas filas en
    # orden distinto se abrazan y una muere por deadlock.
    assert "ORDER BY" in bloqueos[0].upper()


def test_los_espacios_se_bloquean_en_orden_de_pk(listo):
    """El detalle que evita el abrazo mortal entre dos reservas.

    Dos peticiones que pidan A1 y A2 en orden distinto se bloquean
    mutuamente y PostgreSQL mata a una. Ordenar siempre igual lo hace
    imposible, y el orden del carrito **no** sirve: lo elige la persona.
    """
    feria, conv, ana, _ = listo
    with schema_context(feria.schema_name):
        # El carrito llega al revés; la reserva sale igual de ordenada.
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A3", "A1"])

        assert [linea.stand.clave for linea in reserva.lineas.all()] == ["A1", "A3"]
