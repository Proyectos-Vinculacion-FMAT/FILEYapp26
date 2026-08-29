"""
La barra lateral del panel de administración.

Se prueba desde `STD` porque es el único módulo que hoy declara
secciones; lo que se defiende, sin embargo, es del chasis: que **todas**
las pantallas de administración la tengan, que marque dónde está uno, y
que no ofrezca puertas que van a responder 403.

.. note:: Por qué se comprueba que exista en cada pantalla

   Una pantalla de administración sin navegación es un callejón: se
   entra y solo se sale con el botón de atrás. El fallo es mudo —la
   pantalla se ve perfecta— y aparece cuando alguien copia una plantilla
   vieja y hereda el layout equivocado.
"""

import re
from decimal import Decimal

import pytest
from django.conf import settings
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.modulos import Modulo, SeccionPanel, modulo_temporal
from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Solicitud
from ..servicios import configuracion, mapas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _plano(html: str) -> str:
    """El HTML con los espacios colapsados.

    Las aserciones que buscan `class="..." href="..."` se rompen con
    cualquier cambio de indentación de la plantilla —anidar un `{% if %}`
    ya basta—, y ese no es el fallo que quieren cazar.
    """
    return re.sub(r"\s+", " ", html)


def _mapa():
    return {
        "grid": {"salon": "Salón de pruebas", "cols": 12, "rows": 4,
                 "meters_per_cell": 1.0, "cell_size": 32},
        "stands": [{"id": "A1", "label": "A1", "col": 0, "row": 0, "w": 3, "h": 2}],
        "decorations": [],
    }


@pytest.fixture
def escenario(feria_2027):
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_mapa())
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
    return feria_2027, conv, solicitud


def _admin(feria, correo="rita@filey.org"):
    """Administra la feria, pero no es su dueña."""
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


def _duena(feria):
    """La dueña que la feria ya trae.

    No se crea otra: `un_solo_dueno_por_feria` lo impide, y esa
    restricción es justo la que hace que esto tenga una sola respuesta.
    """
    return AdminFeria.objects.get(feria=feria, es_dueno=True).persona


# ── Está en todas las pantallas del módulo ────────────────────


def test_todas_las_pantallas_de_administracion_la_llevan(client, escenario):
    """El callejón sin salida es un fallo mudo: la pantalla se ve bien."""
    feria, conv, solicitud = escenario
    client.force_login(_admin(feria))

    pantallas = [
        _url(feria, "stands:panel", convocatoria_id=conv.pk),
        _url(feria, "stands:solicitudes", convocatoria_id=conv.pk),
        _url(feria, "stands:mapa_completo", convocatoria_id=conv.pk),
        _url(feria, "stands:reservas", convocatoria_id=conv.pk),
        _url(feria, "stands:detalle_solicitud", solicitud_id=solicitud.pk),
    ]

    for url in pantallas:
        cuerpo = client.get(url).content.decode()
        assert '<aside class="sidebar"' in cuerpo, url
        assert "Solicitudes" in cuerpo, url


def test_las_secciones_son_las_que_declara_el_modulo(client, escenario):
    """`ADR-0006`: la plantilla no sabe qué pantallas tiene `STD`."""
    feria, conv, _ = escenario
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    plano = _plano(cuerpo)
    # Las siete que declara `apps.py`, en su orden.
    for etiqueta in (
        "Resumen", "Solicitudes", "Reservas", "Pagos por validar",
        "Expositores", "Mapa del salón", "Configuración",
    ):
        assert f"</span> {etiqueta} " in plano, etiqueta
    # Y bajo el nombre del módulo, no bajo uno inventado por el chasis.
    assert '<div class="side-section">Venta de stands</div>' in cuerpo


def test_un_modulo_sin_secciones_no_pinta_un_grupo_vacio(client, escenario):
    """Es el estado de los otros cinco módulos, no una avería."""
    feria, conv, _ = escenario
    client.force_login(_admin(feria))
    sin_secciones = Modulo(
        tipo=TipoConvocatoria.STD,
        etiqueta="Venta de stands",
        url_aplicar="stands:solicitud",
        url_panel="stands:panel",
    )

    with modulo_temporal(sin_secciones):
        cuerpo = client.get(
            _url(feria, "stands:panel", convocatoria_id=conv.pk)
        ).content.decode()

    assert '<aside class="sidebar"' in cuerpo
    # El grupo del módulo no aparece; el de la feria sí. Se mira el
    # encabezado del grupo y no el texto suelto: "Venta de stands" es
    # también el título de la pantalla.
    assert '<div class="side-section">Venta de stands</div>' not in cuerpo
    assert '<div class="side-section">' in cuerpo
    assert "Convocatorias" in cuerpo


# ── Marca dónde está uno ──────────────────────────────────────


def test_la_seccion_actual_va_marcada(client, escenario):
    feria, conv, _ = escenario
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:reservas", convocatoria_id=conv.pk)
    ).content.decode()

    reservas_url = _url(feria, "stands:reservas", convocatoria_id=conv.pk)
    assert (
        f'class="side-link active" href="{reservas_url}"' in _plano(cuerpo)
    )
    assert 'aria-current="page"' in cuerpo


def test_una_pantalla_que_cuelga_de_una_seccion_marca_la_seccion(
    client, escenario
):
    """El detalle de una solicitud sigue siendo "Solicitudes".

    Por eso la comparación es por prefijo y no por igualdad: si no,
    entrar a un detalle apagaría la barra entera y nadie sabría de dónde
    venía.
    """
    feria, conv, solicitud = escenario
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_solicitud", solicitud_id=solicitud.pk)
    ).content.decode()

    assert 'class="side-link active"' in cuerpo


# ── No ofrece puertas cerradas ────────────────────────────────


def test_el_panel_de_una_convocatoria_no_ofrece_los_accesos(client, escenario):
    """El panel de una convocatoria habla de esa convocatoria.

    Los accesos —quién puede administrar la feria— son de otro nivel.
    Ofrecerlos desde aquí invita a confundir "administrar esta
    convocatoria" con "administrar esta feria", que son permisos
    distintos (`ADR-0004`).
    """
    feria, conv, _ = escenario
    client.force_login(_duena(feria))

    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Accesos" not in cuerpo
    # Y sigue habiendo salida hacia arriba.
    assert "Convocatorias" in cuerpo


def test_ni_siquiera_a_la_duena(client, escenario):
    """No es una cuestión de permiso, es de a qué nivel pertenece."""
    feria, conv, _ = escenario
    client.force_login(_duena(feria))
    duena_ve = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()
    client.force_login(_admin(feria))
    admin_ve = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert "accesos" not in duena_ve.lower()
    assert "accesos" not in admin_ve.lower()


# ── El aplicante no la ve ─────────────────────────────────────


def test_el_mapa_del_aplicante_no_lleva_barra_de_administracion(
    client, escenario
):
    """La misma plantilla sirve a los dos públicos (`CU-STD-009` y `032`).

    El layout lo elige la vista, así que este es justo el sitio donde un
    despiste dejaría al expositor viendo el menú del administrador.
    """
    feria, conv, solicitud = escenario
    client.force_login(solicitud.registro.persona)

    cuerpo = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'id="mapa-canvas"' in cuerpo, "no llegó a montar el canvas"
    assert '<aside class="sidebar"' not in cuerpo
    # `Convocatorias` sale también en la barra **superior**, que sí le
    # toca; lo que no debe haber es ningún enlace de la lateral.
    assert "side-link" not in cuerpo


def test_las_pantallas_del_aplicante_siguen_con_su_layout(client, escenario):
    feria, conv, solicitud = escenario
    client.force_login(solicitud.registro.persona)

    for nombre in ("stands:solicitud", "stands:carrito", "stands:cuenta"):
        cuerpo = client.get(
            _url(feria, nombre, convocatoria_id=conv.pk)
        ).content.decode()
        assert '<aside class="sidebar"' not in cuerpo, nombre


# ── El botón que la alterna ───────────────────────────────────


def test_el_boton_alterna_la_barra_y_sin_javascript_queda_abierta(
    client, escenario
):
    """`sidenav.toggle()` del prototipo de STD, degradando bien.

    El estado vive en un objeto literal de Alpine, no en un componente
    con nombre: así solo depende de que Alpine cargue. Sin JavaScript la
    barra se queda **abierta** —que es su estado por omisión en el
    prototipo, `mode="side" opened`, y el útil— y el botón ni se pinta.
    Un componente con nombre habría dejado `abierta` en `undefined` y la
    barra escondida, que es peor que no tener JavaScript.
    """
    feria, conv, _ = escenario
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'x-data="{ abierta: true }"' in cuerpo
    assert '@click="abierta = !abierta"' in cuerpo
    # El botón se esconde hasta que Alpine arranque: uno que no hace nada
    # durante medio segundo se pulsa igual.
    assert "x-cloak" in cuerpo
    # Y la barra no nace cerrada: `is-cerrada` solo aparece dentro del
    # `:class` que Alpine evalúa, nunca en el atributo servido.
    assert 'class="sidebar is-cerrada"' not in cuerpo
    assert "\'is-cerrada\': !abierta" in cuerpo


def test_el_boton_dice_lo_que_controla(client, escenario):
    """Sin `aria-controls` y `aria-expanded` es un botón mudo."""
    feria, conv, _ = escenario
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'aria-controls="barra-lateral"' in cuerpo
    assert 'id="barra-lateral"' in cuerpo
    assert ":aria-expanded=" in cuerpo


# ── Las secciones que están en el plan y no construidas ───────


def test_una_seccion_planeada_se_pinta_apagada_y_sin_enlace(client, escenario):
    """El menú enseña la forma completa del módulo.

    «Pagos por validar» y «Expositores» son dos de las seis secciones del
    prototipo de STD y no existen todavía. Omitirlas deja la pregunta
    "¿y dónde se validan los pagos?" respondiéndose buscando por todo el
    panel; enlazarlas sería peor, porque el enlace no lleva a ninguna
    parte.
    """
    feria, conv, _ = escenario
    client.force_login(_admin(feria))

    plano = _plano(client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode())

    for etiqueta in ("Pagos por validar", "Expositores", "Configuración"):
        assert (
            '<span class="side-link is-disabled" aria-disabled="true" '
            f'title="Todavía no construido"> <span class="ico" '
            f'aria-hidden="true">' in plano
        ), etiqueta
        assert f"</span> {etiqueta} </span>" in plano, etiqueta


def test_una_seccion_planeada_nunca_sale_marcada_como_actual(client, escenario):
    """Sin URL no puede ser la pantalla actual, y compararla reventaría.

    `actual.startswith(None)` es un `TypeError`, así que esto no es una
    sutileza de presentación: es la línea que tumbaría el panel entero.
    """
    feria, conv, _ = escenario
    client.force_login(_admin(feria))

    respuesta = client.get(_url(feria, "stands:panel", convocatoria_id=conv.pk))

    assert respuesta.status_code == 200
    # Una sola sección activa, y es la que corresponde a la pantalla.
    assert _plano(respuesta.content.decode()).count('side-link active') == 1


def test_el_catalogo_no_sale_marcado_en_todas_las_pantallas(client, escenario):
    """El fallo que delató la comparación por camino.

    La URL del catálogo es la raíz de la feria, y **todo** lo del panel
    empieza por ella: comparando prefijos, "Convocatorias" salía activa
    en cada pantalla y la barra dejaba de decir dónde estaba uno. Por eso
    se compara el nombre de la vista, que es exacto.
    """
    feria, conv, solicitud = escenario
    client.force_login(_admin(feria))

    for nombre, kwargs in (
        ("stands:panel", {"convocatoria_id": conv.pk}),
        ("stands:reservas", {"convocatoria_id": conv.pk}),
        ("stands:detalle_solicitud", {"solicitud_id": solicitud.pk}),
    ):
        plano = _plano(client.get(_url(feria, nombre, **kwargs)).content.decode())
        assert plano.count("side-link active") == 1, nombre
        catalogo = _url(feria, "convocatorias:catalogo").rstrip("/") + "/"
        assert f'class="side-link active" href="{catalogo}"' not in plano, nombre
