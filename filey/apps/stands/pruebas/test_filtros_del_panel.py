"""
La barra de filtros de las colas del panel (A1 y A3).

Sustituye al `<select>` + «Filtrar» que había. Lo que estas pruebas fijan
no es el aspecto sino lo que la barra tiene que **saber responder**:

- cuántas hay en cada estado, sin que nadie filtre para averiguarlo;
- que elegir un estado sea un clic y no tres;
- que los dos filtros convivan — cambiar de estado no borra la búsqueda,
  y buscar no pierde el estado.
"""

import re

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Reserva, Solicitud
from ..servicios import configuracion, mapas, reservas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _admin(feria):
    persona = Persona.objects.create_user(
        correo="rita@filey.org", nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


def _plano(cuerpo):
    return re.sub(r"\s+", " ", cuerpo)


@pytest.fixture
def cola(feria_2027):
    """Cuatro solicitudes: dos pendientes, una aceptada y una rechazada."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        for indice, estado in enumerate(
            ["pendiente", "pendiente", "aceptada", "rechazada"]
        ):
            persona = fabricas.persona(
                correo=f"e{indice}@ejemplo.com", nombre=f"Persona {indice}"
            )
            solicitud = solicitudes.enviar_solicitud(
                convocatoria=conv,
                persona=persona,
                editorial=fabricas.editorial(persona, nombre=f"Editorial {indice}"),
            )
            if estado != "pendiente":
                solicitud.estado = estado
                solicitud.fecha_revision = solicitud.fecha_envio
                solicitud.save()
    return feria_2027, conv


# ── Los conteos ───────────────────────────────────────────────


def test_cada_estado_dice_cuantas_hay(client, cola):
    """Es lo que quien revisa viene a saber, y antes había que filtrar."""
    feria, conv = cola
    client.force_login(_admin(feria))

    plano = _plano(
        client.get(
            _url(feria, "stands:solicitudes", convocatoria_id=conv.pk)
        ).content.decode()
    )

    assert "Todas <span class=\"count\">4</span>" in plano
    assert "Pendiente de revisión <span class=\"count\">2</span>" in plano
    assert "Aceptada <span class=\"count\">1</span>" in plano
    # El cero se pinta: dice algo distinto de que la fila no exista.
    assert "Cambios solicitados <span class=\"count\">0</span>" in plano


def test_los_conteos_no_se_encogen_al_filtrar(client, cola):
    """Un chip que dijera «0» por culpa de otro filtro no sirve para navegar."""
    feria, conv = cola
    client.force_login(_admin(feria))

    plano = _plano(
        client.get(
            _url(feria, "stands:solicitudes", convocatoria_id=conv.pk),
            {"estado": "aceptada"},
        ).content.decode()
    )

    assert "Pendiente de revisión <span class=\"count\">2</span>" in plano
    assert "<strong>1</strong> de 4 solicitudes" in plano


def test_el_estado_activo_no_es_un_enlace(client, cola):
    """Llevaría a donde ya se está; `aria-current` lo dice sin el color."""
    feria, conv = cola
    client.force_login(_admin(feria))

    plano = _plano(
        client.get(
            _url(feria, "stands:solicitudes", convocatoria_id=conv.pk),
            {"estado": "pendiente"},
        ).content.decode()
    )

    assert (
        '<span class="chip is-active" aria-current="true"> Pendiente de revisión'
        in plano
    )


# ── Los dos filtros conviven ──────────────────────────────────


def test_cambiar_de_estado_conserva_la_busqueda(client, cola):
    feria, conv = cola
    client.force_login(_admin(feria))

    plano = _plano(
        client.get(
            _url(feria, "stands:solicitudes", convocatoria_id=conv.pk),
            {"q": "Editorial 1"},
        ).content.decode()
    )

    assert "q=Editorial+1&amp;estado=aceptada" in plano


def test_buscar_conserva_el_estado(client, cola):
    """La contraparte: el buscador lleva el estado escondido."""
    feria, conv = cola
    client.force_login(_admin(feria))

    plano = _plano(
        client.get(
            _url(feria, "stands:solicitudes", convocatoria_id=conv.pk),
            {"estado": "pendiente"},
        ).content.decode()
    )

    assert '<input type="hidden" name="estado" value="pendiente">' in plano


def test_los_dos_filtros_a_la_vez_recortan_de_verdad(client, cola):
    feria, conv = cola
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:solicitudes", convocatoria_id=conv.pk),
        {"estado": "pendiente", "q": "Editorial 1"},
    ).content.decode()

    assert "Editorial 1" in cuerpo
    assert "Editorial 0" not in cuerpo
    assert "<strong>1</strong> de 4 solicitudes" in _plano(cuerpo)


def test_sin_filtros_se_dice_el_total(client, cola):
    feria, conv = cola
    client.force_login(_admin(feria))

    plano = _plano(
        client.get(
            _url(feria, "stands:solicitudes", convocatoria_id=conv.pk)
        ).content.decode()
    )

    assert "<strong>4</strong> solicitudes en total" in plano
    assert "Quitar filtros" not in plano, "no hay ninguno que quitar"


# ── La cola de reservas ───────────────────────────────────────


def test_las_vencidas_se_cuentan_aparte_y_no_suman_al_total(client, feria_2027):
    """`RN-12`: una vencida es `por_confirmar` con el plazo pasado.

    Sumarla al total contaría dos veces la misma reserva.
    """
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(
            convocatoria=conv,
            datos={
                "grid": {"salon": "S", "cols": 30, "rows": 10,
                         "meters_per_cell": 1.0, "cell_size": 32},
                "stands": [
                    {"id": f"A{i}", "label": f"A{i}", "col": i * 4, "row": 0,
                     "w": 3, "h": 2}
                    for i in (1, 2)
                ],
                "decorations": [],
            },
        )
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = 2500
        cfg.save(update_fields=["costo_m2"])
        for indice, clave in enumerate(["A1", "A2"]):
            persona = fabricas.persona(
                correo=f"r{indice}@ejemplo.com", nombre=f"Persona {indice}"
            )
            solicitud = solicitudes.enviar_solicitud(
                convocatoria=conv,
                persona=persona,
                editorial=fabricas.editorial(persona, nombre=f"Editorial {indice}"),
            )
            solicitud.estado = Solicitud.Estado.ACEPTADA
            solicitud.fecha_revision = solicitud.fecha_envio
            solicitud.save()
            reservas.crear(convocatoria=conv, persona=persona, claves=[clave])
        # Una de las dos se pasó del plazo.
        Reserva.objects.filter(pk=Reserva.objects.first().pk).update(
            fecha_vencimiento_anticipo=timezone.now() - timezone.timedelta(days=1)
        )

    client.force_login(_admin(feria_2027))
    plano = _plano(
        client.get(
            _url(feria_2027, "stands:reservas", convocatoria_id=conv.pk)
        ).content.decode()
    )

    assert "Todas <span class=\"count\">2</span>" in plano
    assert "Por confirmar <span class=\"count\">2</span>" in plano
    assert "Vencidas <span class=\"count\">1</span>" in plano


# ── Lo que se quitó ───────────────────────────────────────────


def test_la_cola_ya_no_repite_la_navegacion_de_la_barra_lateral(client, cola):
    """«Ver el mapa» y «Reservas» estaban dentro del formulario de filtros.

    Son navegación, no filtros, y la barra lateral ya lleva a las dos.
    """
    feria, conv = cola
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:solicitudes", convocatoria_id=conv.pk)
    ).content.decode()
    dentro_de_la_barra = cuerpo.split('class="filtros"')[1].split("</p>")[0]

    assert "Ver el mapa" not in dentro_de_la_barra
    # Queda un solo botón, y es el de buscar: elegir un estado ya filtra.
    # («Filtrar» sobrevive como `aria-label` del grupo de chips, que es
    # justo lo que ese grupo hace.)
    assert ">Filtrar<" not in dentro_de_la_barra
    assert dentro_de_la_barra.count("<button") == 1


# ── La barra se comporta igual en las dos colas ───────────────


@pytest.mark.parametrize(
    "vista, cuantos_chips",
    [("stands:solicitudes", 5), ("stands:reservas", 6)],
)
def test_el_buscador_va_siempre_dentro_de_la_barra(
    client, cola, vista, cuantos_chips
):
    """Mismo orden en las dos, tengan cinco estados o seis.

    Con la caja de búsqueda flexible, reservas —que tiene un chip más—
    la mandaba a un segundo renglón y solicitudes no: la misma barra con
    dos formas según la cola. Ahora el orden del marcado es siempre
    chips → buscador dentro del mismo contenedor, y quien decide que no
    baje es el `flex-wrap: nowrap` de `.filtros`.
    """
    feria, conv = cola
    client.force_login(_admin(feria))

    plano = _plano(
        client.get(_url(feria, vista, convocatoria_id=conv.pk)).content.decode()
    )
    barra = plano.split('class="filtros"')[1].split("</div>")[0]

    # Se cuentan los conteos y no las clases: `class="chips"` es el
    # contenedor y contaría de más.
    assert barra.count('<span class="count">') == cuantos_chips
    assert barra.index("</nav>") < barra.index('class="searchbox"')
