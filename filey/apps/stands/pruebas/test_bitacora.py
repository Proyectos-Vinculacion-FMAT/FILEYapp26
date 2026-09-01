"""
La bitácora de `STD` (modelo de datos §3.12).

**Una por módulo, y a propósito**: lo que se registra son las acciones
sensibles *de un dominio*, y validar un abono no se parece a mover la
fecha de cierre de una convocatoria. Ésta es la primera de las tres que
el proyecto va a tener.

No sustituye al rastro que ya vive en cada fila —`Movimiento` dice quién
validó, `Reserva` quién la canceló—. Contesta la pregunta que ninguna de
esas contesta: **«¿qué pasó con esta convocatoria el martes?»**, que hoy
exige unir cinco tablas y ordenarlas por cinco fechas distintas.

Lo que se defiende aquí:

1. **Las cuatro acciones invisibles quedan escritas.** Retirar un
   descuento, caducar un pronto pago, prorrogar y mover el corte borran
   una fila o sobreescriben una fecha: sin bitácora no hay dónde leerlas.
2. **Anotar nunca tumba la acción.** Un fallo escribiendo la bitácora se
   traga, como el del correo. Lo contrario sería que una línea de
   historial reventara una validación que el banco ya respaldó.
3. **Nadie la edita.** Una bitácora que se puede reescribir no prueba
   nada.
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..formularios import ConfiguracionForm
from ..models import (
    BitacoraSTD,
    DescuentoAplicado,
    Movimiento,
    Reserva,
    Solicitud,
)
from ..servicios import (
    bitacora,
    configuracion,
    dictamen,
    mapas,
    pagos,
    reservas,
    solicitudes,
)
from . import fabricas

pytestmark = pytest.mark.django_db


def _admin(feria, correo="rita@filey.org"):
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


def _pdf():
    return SimpleUploadedFile("r.pdf", b"%PDF")


@pytest.fixture
def reserva(feria_2027):
    """Una reserva de $15 000: 6 m² a $2 500."""
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
        r = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        # El montaje deja su propia línea —importar el mapa se anota— y
        # aquí es ruido: lo que cada prueba mira es lo que hace ella.
        BitacoraSTD.objects.all().delete()
    return feria_2027, conv, ana, r


def _acciones(objeto):
    return list(bitacora.de(objeto).values_list("accion", flat=True))


# ── Las cuatro que no dejan rastro en ninguna otra parte ──────


def test_retirar_un_descuento_queda_escrito(reserva):
    """La fila se borra: sin esto, el total sube y nada lo explica."""
    feria, _, _, r = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        pagos.aplicar_descuento_especial(
            reserva=r, administrador=admin, porcentaje=20, motivo="Convenio"
        )
        pagos.retirar_descuento_especial(reserva=r, administrador=admin)

        assert BitacoraSTD.Accion.DESCUENTO_RETIRADO in _acciones(r)
        entrada = bitacora.de(r).get(
            accion=BitacoraSTD.Accion.DESCUENTO_RETIRADO
        )
        # Con el porcentaje dentro: el objeto que lo decía ya no existe.
        assert entrada.detalle["porcentaje"] == 20
        assert entrada.detalle["motivo"] == "Convenio"
        assert entrada.persona == admin
        assert not DescuentoAplicado.objects.filter(
            tipo=DescuentoAplicado.Tipo.ESPECIAL
        ).exists()


def test_el_pronto_pago_que_caduca_lo_firma_el_sistema(reserva):
    """Sin persona **es** el dato: no lo decidió nadie, se cumplió `RN-04`."""
    feria, conv, _, r = reserva
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() - timedelta(days=1)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])
        DescuentoAplicado.objects.create(
            reserva=r, tipo=DescuentoAplicado.Tipo.PRONTO_PAGO, porcentaje=10
        )

        pagos.caducar_pronto_pago(Reserva.objects.get(pk=r.pk))

        entrada = bitacora.de(r).get(
            accion=BitacoraSTD.Accion.PRONTO_PAGO_CADUCADO
        )
        assert entrada.persona is None
        assert entrada.detalle["porcentaje"] == 10
        assert str(entrada).startswith("El sistema:")


def test_prorrogar_y_mover_el_corte_quedan_escritos(reserva):
    """Las dos sobreescriben una fecha: la vieja no se lee en ningún lado."""
    feria, _, _, r = reserva
    admin = _admin(feria)
    nueva = timezone.now() + timedelta(days=20)
    with schema_context(feria.schema_name):
        antes = r.fecha_vencimiento_anticipo
        reservas.prorrogar(reserva=r, administrador=admin, fecha=nueva)
        reservas.mover_fecha_de_corte(
            reserva=r, administrador=admin,
            fecha=timezone.localdate() + timedelta(days=60),
        )

        prorroga = bitacora.de(r).get(
            accion=BitacoraSTD.Accion.RESERVA_PRORROGADA
        )
        assert prorroga.detalle["vencia"] == antes.isoformat()
        assert prorroga.detalle["vence"] == nueva.isoformat()

        corte = bitacora.de(r).get(accion=BitacoraSTD.Accion.CORTE_MOVIDO)
        assert corte.detalle["antes"] is None


# ── Las que el modelo de datos nombra ─────────────────────────


def test_el_dinero_deja_su_linea(reserva):
    feria, _, ana, r = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        reportado = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("2000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_pdf(),
        )
        pagos.validar(movimiento=reportado, administrador=admin)
        otro = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("500"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_pdf(),
        )
        pagos.rechazar(movimiento=otro, administrador=admin, motivo="No llegó")
        pagos.registrar(
            reserva=r, persona=admin, monto=Decimal("1000"),
            metodo=Movimiento.Metodo.DEPOSITO, archivo=_pdf(), manual=True,
        )

        assert set(_acciones(r)) == {
            BitacoraSTD.Accion.ABONO_VALIDADO,
            BitacoraSTD.Accion.ABONO_RECHAZADO,
            BitacoraSTD.Accion.ABONO_MANUAL,
        }


def test_lo_que_reporta_el_aplicante_no_entra(reserva):
    """La bitácora es de acciones de administración, no de todo lo que
    pasa: un abono reportado ya se ve en la cola de A5, y anotarlo
    llenaría la línea de tiempo de ruido que nadie viene a leer."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("2000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_pdf(),
        )

        assert _acciones(r) == []


def test_cancelar_queda_escrito_con_los_espacios_que_libero(
    reserva, django_capture_on_commit_callbacks
):
    feria, _, _, r = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            reservas.cancelar(
                reserva=r, administrador=admin, motivo="No cubrió el anticipo"
            )

        entrada = bitacora.de(r).get(
            accion=BitacoraSTD.Accion.RESERVA_CANCELADA
        )
        assert entrada.detalle["espacios"] == ["A1"]
        assert entrada.detalle["motivo"] == "No cubrió el anticipo"


# ── Cómo se comporta ──────────────────────────────────────────


def test_la_linea_de_tiempo_sale_de_lo_mas_reciente_atras(reserva):
    """Es la pregunta que hace útil la tabla: «¿qué pasó el martes?»."""
    feria, _, _, r = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        pagos.aplicar_descuento_especial(
            reserva=r, administrador=admin, porcentaje=10, motivo="Convenio"
        )
        pagos.retirar_descuento_especial(reserva=r, administrador=admin)

        assert _acciones(r) == [
            BitacoraSTD.Accion.DESCUENTO_RETIRADO,
            BitacoraSTD.Accion.DESCUENTO_APLICADO,
        ]


def test_anotar_no_tumba_la_accion(reserva):
    """El mismo criterio que el correo: perder una línea de historial es
    mejor que revertir un cobro que el banco ya respaldó.

    **El fallo que se simula es de base de datos**, que es el realista y
    el único que necesita el savepoint: atrapar la excepción no basta
    —PostgreSQL deja la transacción abortada y todo lo que venga después
    revienta con `TransactionManagementError`—. Con un `OSError`, que es
    lo que esta prueba simulaba antes, pasaba sin probar nada: el fallo
    de verdad apareció guardando la configuración desde la pantalla.
    """
    feria, _, ana, r = reserva
    admin = _admin(feria)

    def _sql_roto(*args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM una_tabla_que_no_existe")

    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_pdf(),
        )

        with patch(
            "apps.stands.servicios.bitacora.BitacoraSTD.objects.create",
            side_effect=_sql_roto,
        ):
            pagos.validar(movimiento=movimiento, administrador=admin)

        # Y la transacción sigue viva: esto es lo que fallaba.
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.CONFIRMADA
        assert r.monto_abonado == Decimal("7500.00")
        assert not BitacoraSTD.objects.exists()


def test_una_anotacion_no_sobrevive_a_un_rollback(reserva):
    """Al revés que el correo, que espera al commit **porque** no se
    puede deshacer. Una anotación sí, y una que sobreviviera diría que
    pasó algo que no pasó.
    """
    feria, _, _, r = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        # La anotación se escribe **antes** del recálculo; si el recálculo
        # revienta, la transacción del servicio se va entera y la
        # anotación con ella.
        with patch(
            "apps.stands.servicios.pagos._recalcular_total",
            side_effect=RuntimeError("se cayó a mitad"),
        ):
            with pytest.raises(RuntimeError):
                pagos.aplicar_descuento_especial(
                    reserva=r, administrador=admin, porcentaje=10,
                    motivo="Convenio",
                )

        assert not BitacoraSTD.objects.exists()
        # Y el descuento tampoco quedó: es la misma transacción.
        assert not DescuentoAplicado.objects.exists()


# ── Partida por convocatoria ──────────────────────────────────


def test_cada_convocatoria_tiene_la_suya(reserva):
    """`RN-19`: una feria puede tener la general y la de un pabellón.

    Son dos ventas distintas, con dos mapas y dos precios. Mezclarlas
    convierte la bitácora en algo que hay que leer entero para encontrar
    una cosa.
    """
    feria, conv, _, r = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        pagos.aplicar_descuento_especial(
            reserva=r, administrador=admin, porcentaje=10, motivo="Convenio"
        )
        pabellon = fabricas.convocatoria(nombre="Pabellón infantil")
        mapas.importar(
            convocatoria=pabellon,
            datos={
                "grid": {"salon": "S", "cols": 10, "rows": 10,
                         "meters_per_cell": 1.0, "cell_size": 32},
                "stands": [{"id": "B1", "label": "B1", "col": 0, "row": 0,
                            "w": 2, "h": 2}],
                "decorations": [],
            },
            persona=admin,
        )

        de_la_general = bitacora.de_la_convocatoria(conv)
        del_pabellon = bitacora.de_la_convocatoria(pabellon)

        assert list(de_la_general.values_list("accion", flat=True)) == [
            BitacoraSTD.Accion.DESCUENTO_APLICADO
        ]
        assert list(del_pabellon.values_list("accion", flat=True)) == [
            BitacoraSTD.Accion.MAPA_IMPORTADO
        ]


def test_la_convocatoria_sale_del_objeto_sin_que_nadie_la_pase(reserva):
    """Se guarda al anotar y no se deduce al leer: cada punto de escritura
    tendría que acordarse, y el que se olvidara dejaría entradas fuera de
    todos los filtros sin que nada lo señalara."""
    feria, conv, ana, r = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("1000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_pdf(),
        )
        # Un `Movimiento` está a tres saltos de su convocatoria.
        pagos.rechazar(movimiento=movimiento, administrador=admin, motivo="No")

        assert bitacora.de(r).get().convocatoria == conv


# ── Los dos eventos que faltaban ──────────────────────────────


def test_el_dictamen_queda_en_la_misma_linea_de_tiempo(reserva):
    """Aceptar es lo que habilita a reservar (`RN-16`): es el primer
    eslabón de todo lo que viene después, y hasta hoy no salía en la
    bitácora aunque `Solicitud` guardara quién y cuándo."""
    feria, conv, _, _ = reserva
    revisor = _admin(feria)
    with schema_context(feria.schema_name):
        otra = fabricas.persona(correo="beto@ej.com")
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=otra, editorial=fabricas.editorial(otra)
        )

        dictamen.rechazar(solicitud, revisor=revisor, motivo="Falta la carta")

        entrada = bitacora.de(solicitud).get()
        assert entrada.accion == BitacoraSTD.Accion.SOLICITUD_DICTAMINADA
        assert entrada.persona == revisor
        assert entrada.detalle["resultado"] == Solicitud.Estado.RECHAZADA
        assert entrada.detalle["motivo"] == "Falta la carta"
        assert entrada.convocatoria == conv


def test_cambiar_el_precio_deja_quien_y_de_cuanto_a_cuanto(reserva):
    """Lo más sensible que se toca desde una pantalla, y hasta hoy no
    dejaba rastro en ninguna parte."""
    feria, conv, _, _ = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        ajustes = configuracion.de_la_convocatoria(conv)
        form = ConfiguracionForm(
            {
                "costo_m2": "3000.00",
                "porcentaje_anticipo": ajustes.porcentaje_anticipo,
                "plazo_reserva_dias": ajustes.plazo_reserva_dias,
                "descuento_pronto_pago": ajustes.descuento_pronto_pago,
                "banco_clabe": "012 914 002 010 987 654",
            },
            instance=ajustes,
        )
        assert form.is_valid(), form.errors

        configuracion.guardar(form=form, administrador=admin)

        entrada = bitacora.de(ajustes).get()
        assert entrada.accion == BitacoraSTD.Accion.CONFIGURACION_CAMBIADA
        assert entrada.detalle["cambios"]["costo_m2"] == ["2500.00", "3000.00"]
        assert entrada.detalle["cambios"]["banco_clabe"][0] == "—"
        assert entrada.convocatoria == conv


def test_guardar_sin_cambiar_nada_no_anota(reserva):
    """Una bitácora con líneas que dicen «no tocó nada» es una que hay
    que leer entera para encontrar algo."""
    feria, conv, _, _ = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        ajustes = configuracion.de_la_convocatoria(conv)
        form = ConfiguracionForm(
            {
                "costo_m2": ajustes.costo_m2,
                "porcentaje_anticipo": ajustes.porcentaje_anticipo,
                "plazo_reserva_dias": ajustes.plazo_reserva_dias,
                "descuento_pronto_pago": ajustes.descuento_pronto_pago,
            },
            instance=ajustes,
        )
        assert form.is_valid(), form.errors

        configuracion.guardar(form=form, administrador=admin)

        assert not BitacoraSTD.objects.exists()


def _mapa_chico():
    return {
        "grid": {"salon": "Otro", "cols": 10, "rows": 10,
                 "meters_per_cell": 1.0, "cell_size": 32},
        "stands": [{"id": "Z9", "label": "Z9", "col": 0, "row": 0,
                    "w": 2, "h": 2}],
        "decorations": [],
    }


def test_importar_un_mapa_dice_quien_y_si_reemplazo(reserva):
    """La operación más destructiva del dominio, y la única que no deja
    rastro en ninguna fila: las viejas ya no existen.

    Se importa sobre una convocatoria nueva y no sobre la del montaje:
    reemplazar un mapa con reservas vivas encima está prohibido, y con
    razón (`CU-STD-039` E1).
    """
    feria, _, _, _ = reserva
    operador = _admin(feria)
    with schema_context(feria.schema_name):
        otra = fabricas.convocatoria(nombre="Pabellón infantil")
        mapas.importar(convocatoria=otra, datos=_mapa_chico(), persona=operador)
        mapas.importar(
            convocatoria=otra, datos=_mapa_chico(), confirmado=True,
            persona=operador,
        )

        entradas = list(
            BitacoraSTD.objects.filter(
                accion=BitacoraSTD.Accion.MAPA_IMPORTADO
            ).order_by("fecha")
        )
        assert [e.persona for e in entradas] == [operador, operador]
        assert entradas[0].detalle["reemplazo"] is False
        assert entradas[1].detalle["reemplazo"] is True
        assert entradas[0].detalle["stands"] == 1


def test_desde_un_comando_el_mapa_no_lo_firma_nadie(reserva):
    """`manage.py importar_mapa` no tiene sesión detrás, y eso es la
    verdad: no lo hizo ninguna persona identificada."""
    feria, _, _, _ = reserva
    with schema_context(feria.schema_name):
        otra = fabricas.convocatoria(nombre="Pabellón infantil")
        mapas.importar(convocatoria=otra, datos=_mapa_chico())

        assert BitacoraSTD.objects.get().persona is None


def test_todas_las_acciones_declaradas_se_escriben_de_verdad(reserva):
    """El conjunto de `Accion` está cerrado **y coincide con lo que se
    anota**.

    Una acción declarada que nadie escribe es una promesa que la pantalla
    del admin ofrece filtrar y siempre devuelve vacía. Esta prueba es lo
    que impide que el conjunto y el código se separen: si se añade una
    entrada al enum sin cablearla, falla aquí.
    """
    import inspect

    # Se recorren los módulos que anotan, buscando la constante usada.
    escritas = set()

    from ..servicios import configuracion as srv_cfg
    from ..servicios import dictamen as srv_dic
    from ..servicios import mapas as srv_map
    from ..servicios import pagos as srv_pag
    from ..servicios import reservas as srv_res

    for modulo in (srv_pag, srv_res, srv_dic, srv_cfg, srv_map):
        fuente = inspect.getsource(modulo)
        for accion in BitacoraSTD.Accion:
            if f"Accion.{accion.name}" in fuente:
                escritas.add(accion)

    assert escritas == set(BitacoraSTD.Accion), (
        "declaradas y nunca escritas: "
        f"{[a.name for a in set(BitacoraSTD.Accion) - escritas]}"
    )


def test_nadie_la_edita_desde_el_admin(reserva):
    """Una bitácora que se puede reescribir no prueba nada."""
    from comun.admin_feria import admin_feria

    registrado = admin_feria._registry[BitacoraSTD]
    assert not registrado.has_add_permission(None)
    assert not registrado.has_change_permission(None)
    assert not registrado.has_delete_permission(None)
