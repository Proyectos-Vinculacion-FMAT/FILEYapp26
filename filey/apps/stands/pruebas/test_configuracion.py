"""
La configuración de la convocatoria, y el paso 6 de `CU-FER-005`.

Con `apps.stands` instalado, el alta de una convocatoria de stands deja
de correr en vacío: llama al callback que esta app inscribió y crea la
configuración **dentro de la misma transacción**. Es la primera vez que
el enganche de `ADR-0006` se ejerce de verdad, y estas pruebas son las
que lo comprueban de punta a punta — desde `apps/convocatorias` hasta una
fila de `apps/stands`.
"""

import pytest
from django_tenants.utils import schema_context

from apps.convocatorias import modulos
from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.servicios import altas

from ..models import ConfiguracionSistema
from ..servicios import configuracion
from . import fabricas

pytestmark = pytest.mark.django_db


def test_el_alta_de_una_convocatoria_std_crea_su_configuracion(feria_2027):
    """`CU-FER-005` paso 6, cerrado de verdad.

    Es la prueba que recorre los dos dominios: el alta vive en
    `apps/convocatorias`, la fila que se crea es de `apps/stands`, y
    entre las dos no hay ningún import — solo el registro de módulos.
    """
    with schema_context(feria_2027.schema_name):
        resultado = altas.crear_convocatoria(
            tipo=TipoConvocatoria.STD, nombre="Stands 2027"
        )

        configuracion_creada = ConfiguracionSistema.objects.get()
        assert configuracion_creada.convocatoria == resultado.convocatoria


def test_una_convocatoria_de_otro_tipo_no_recibe_configuracion_de_stands(feria_2027):
    with schema_context(feria_2027.schema_name):
        altas.crear_convocatoria(tipo=TipoConvocatoria.VIS, nombre="Visitas 2027")

        assert not ConfiguracionSistema.objects.exists()


def test_los_valores_por_omision_son_los_de_las_reglas(feria_2027):
    """50% de anticipo (`RN-02`), 30 días (`RN-03`), 10% (`RN-04`)."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()

        cfg = configuracion.crear_por_defecto(conv)

        assert cfg.porcentaje_anticipo == 50
        assert cfg.plazo_reserva_dias == 30
        assert cfg.descuento_pronto_pago == 10


def test_el_precio_nace_en_cero_y_no_se_adivina(feria_2027):
    """No hay un costo por m² razonable que inventar.

    El dueño de la feria lo fija antes de abrir la convocatoria. Que nazca
    en cero es visible; que naciera en una cifra inventada, no.
    """
    with schema_context(feria_2027.schema_name):
        cfg = configuracion.crear_por_defecto(fabricas.convocatoria())

        assert cfg.costo_m2 == 0


def test_el_callback_es_idempotente(feria_2027):
    """Un callback que falla por correr dos veces se lleva un alta buena."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()

        primera = configuracion.crear_por_defecto(conv)
        segunda = configuracion.crear_por_defecto(conv)

        assert primera.pk == segunda.pk
        assert ConfiguracionSistema.objects.count() == 1


def test_no_se_configura_una_convocatoria_de_otro_tipo(feria_2027):
    with schema_context(feria_2027.schema_name):
        eventos = fabricas.convocatoria("Eventos", tipo=TipoConvocatoria.EVT)

        with pytest.raises(ValueError):
            configuracion.crear_por_defecto(eventos)


def test_cada_convocatoria_tiene_la_suya(feria_2027):
    """Dos convocatorias de stands en la misma feria, dos precios.

    "El costo por m² de la feria" dejó de significar nada el 2026-08-25.
    """
    with schema_context(feria_2027.schema_name):
        general = fabricas.convocatoria("Stands general")
        pabellon = fabricas.convocatoria("Pabellón infantil")

        cfg_general = configuracion.de_la_convocatoria(general)
        cfg_pabellon = configuracion.de_la_convocatoria(pabellon)
        cfg_general.costo_m2 = 2500
        cfg_general.save()

        cfg_pabellon.refresh_from_db()
        assert cfg_pabellon.costo_m2 == 0
        assert ConfiguracionSistema.objects.count() == 2


def test_si_la_configuracion_falla_no_queda_ni_la_convocatoria(feria_2027):
    """`CU-FER-005` E1, ahora con un módulo de verdad enganchado.

    La fase 0 lo probó con un callback de mentira sobre un tipo que nadie
    servía. Esto comprueba que la transacción sigue siendo la misma
    ahora que quien contesta al registro es `apps/stands`: se sustituye
    su módulo por uno que revienta, sin tocar nada más del camino.
    """

    def revienta(convocatoria):
        raise RuntimeError("sin costo_m2 por omisión")

    real = modulos.modulo_de(TipoConvocatoria.STD)
    roto = modulos.Modulo(
        tipo=real.tipo,
        etiqueta=real.etiqueta,
        url_aplicar=real.url_aplicar,
        url_panel=real.url_panel,
        crear_configuracion=revienta,
    )

    with schema_context(feria_2027.schema_name), modulos.modulo_temporal(roto):
        with pytest.raises(altas.ConfiguracionDelModuloFallo):
            altas.crear_convocatoria(tipo=TipoConvocatoria.STD, nombre="Stands 2027")

        assert not Convocatoria.objects.exists()
        assert not ConfiguracionSistema.objects.exists()
