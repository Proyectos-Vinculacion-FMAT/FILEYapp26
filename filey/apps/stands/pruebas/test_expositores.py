"""
A6 y A7 · Quién está habilitado y su expediente (`CU-STD-030`, `031`).

Era la única sección del panel que seguía apagada. No desbloquea nada
—todo lo que enseña se alcanza desde Reservas y Solicitudes— pero
contesta una pregunta que ninguna otra pantalla contesta entera: **quién
es este cliente y en qué va**, sin ir saltando entre tres listas.

Dos cosas que se defienden aquí:

1. **Expositor es quien tiene la solicitud aceptada** (`RN-16`), no quien
   llenó una ficha. La lista vacía manda a dictaminar, no a esperar.
2. **A7 enseña la ficha viva, no la fotografía.** A2 juzga lo que se
   envió (`RN-22`); A7 atiende a un cliente hoy. Si corrigió su correo
   después del dictamen, el bueno es el de A7 — y el de A2 sigue siendo
   el que se juzgó.
"""

from decimal import Decimal

import pytest
from django.conf import settings
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Editorial, SelloEditorial, Solicitud
from ..servicios import configuracion, mapas, reservas, solicitudes
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


def _mapa():
    return {
        "grid": {"salon": "S", "cols": 30, "rows": 10,
                 "meters_per_cell": 1.0, "cell_size": 32},
        "stands": [
            {"id": "A1", "label": "A1", "col": 0, "row": 0, "w": 3, "h": 2},
            {"id": "A2", "label": "A2", "col": 4, "row": 0, "w": 3, "h": 2},
        ],
        "decorations": [],
    }


def _aplicante(
    convocatoria, *, correo, nombre_editorial, contacto=None, aceptar=True
):
    """Una editorial con su solicitud, opcionalmente ya aceptada.

    `contacto` es el correo **de la ficha**, que no tiene por qué ser el
    de la cuenta: la ficha de fábrica trae el mismo para todas, y por ahí
    no se distingue a dos editoriales.
    """
    persona = fabricas.persona(correo=correo)
    editorial = fabricas.editorial(
        persona,
        nombre=nombre_editorial,
        correo_electronico=contacto or correo,
    )
    solicitud = solicitudes.enviar_solicitud(
        convocatoria=convocatoria, persona=persona, editorial=editorial
    )
    if aceptar:
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
    return persona, editorial, solicitud


@pytest.fixture
def convocatoria(feria_2027):
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_mapa())
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("2500")
        cfg.save(update_fields=["costo_m2"])
    return feria_2027, conv


# ── A6 · la lista ─────────────────────────────────────────────


def test_solo_aparecen_las_aceptadas(client, convocatoria):
    """`RN-16`: expositor es quien puede reservar, no quien aplicó."""
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        _aplicante(conv, correo="ana@ej.com", nombre_editorial="Ediciones Mayab")
        _aplicante(
            conv, correo="beto@ej.com", nombre_editorial="Casa Peninsular",
            aceptar=False,
        )
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:expositores", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Ediciones Mayab" in cuerpo
    assert "Casa Peninsular" not in cuerpo


def test_la_lista_vacia_manda_a_dictaminar(client, convocatoria):
    """`E1`. No dice «no hay editoriales» porque no es lo que pasa: es
    que ninguna solicitud está aceptada todavía."""
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        _aplicante(
            conv, correo="beto@ej.com", nombre_editorial="Casa Peninsular",
            aceptar=False,
        )
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:expositores", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Todavía no hay expositores habilitados" in cuerpo
    assert f"/stands/{conv.pk}/solicitudes/" in cuerpo


def test_se_busca_por_nombre_y_por_correo(client, convocatoria):
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        _aplicante(conv, correo="ana@ej.com", nombre_editorial="Ediciones Mayab")
        _aplicante(conv, correo="zoe@otra.com", nombre_editorial="Libros del Sur")
    client.force_login(_admin(feria))
    url = _url(feria, "stands:expositores", convocatoria_id=conv.pk)


    por_nombre = client.get(url, {"q": "Mayab"}).content.decode()
    por_correo = client.get(url, {"q": "otra.com"}).content.decode()

    assert "Ediciones Mayab" in por_nombre and "Libros del Sur" not in por_nombre
    assert "Libros del Sur" in por_correo and "Ediciones Mayab" not in por_correo


def test_la_cuenta_dice_cuantas_de_cuantas(client, convocatoria):
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        _aplicante(conv, correo="ana@ej.com", nombre_editorial="Ediciones Mayab")
        _aplicante(conv, correo="zoe@otra.com", nombre_editorial="Libros del Sur")
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:expositores", convocatoria_id=conv.pk), {"q": "Mayab"}
    ).content.decode()

    assert "1</strong> de 2" in cuerpo.replace("\n", "").replace("  ", "")


def test_la_seccion_del_panel_ya_enlaza(client, convocatoria):
    """Era la última sección apagada de la barra lateral."""
    feria, conv = convocatoria
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert f"/stands/{conv.pk}/expositores/" in cuerpo


def test_un_participante_no_entra(client, convocatoria):
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        ana, _, _ = _aplicante(
            conv, correo="ana@ej.com", nombre_editorial="Ediciones Mayab"
        )
    client.force_login(ana)

    respuesta = client.get(
        _url(feria, "stands:expositores", convocatoria_id=conv.pk)
    )

    assert respuesta.status_code == 403


# ── A7 · el expediente ────────────────────────────────────────


def test_el_expediente_trae_ficha_sellos_y_documentos(client, convocatoria):
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        _, editorial, _ = _aplicante(
            conv, correo="ana@ej.com", nombre_editorial="Ediciones Mayab"
        )
        SelloEditorial.objects.create(editorial=editorial, nombre="Sello Chichén")
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_expositor", editorial_id=editorial.pk)
    ).content.decode()

    assert "Ediciones Mayab" in cuerpo
    assert "Sello Chichén" in cuerpo
    assert editorial.correo_electronico in cuerpo
    assert editorial.director_general_email in cuerpo


def test_el_expediente_enseña_la_ficha_viva_y_no_la_fotografia(
    client, convocatoria
):
    """A2 juzga lo que se envió (`RN-22`); A7 atiende a un cliente hoy.

    Si corrigió su correo después del dictamen, el bueno aquí es el de
    ahora — y el de A2 sigue siendo el que se juzgó. Las dos tienen
    razón; no son la misma pregunta.
    """
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        _, editorial, solicitud = _aplicante(
            conv, correo="ana@ej.com", nombre_editorial="Ediciones Mayab",
            contacto="viejo@mayab.com",
        )
        # Corrige su correo **después** del dictamen.
        editorial.correo_electronico = "nuevo@mayab.com"
        editorial.save(update_fields=["correo_electronico"])
    client.force_login(_admin(feria))

    expediente = client.get(
        _url(feria, "stands:detalle_expositor", editorial_id=editorial.pk)
    ).content.decode()
    ficha = client.get(
        _url(feria, "stands:detalle_solicitud", solicitud_id=solicitud.pk)
    ).content.decode()

    assert "nuevo@mayab.com" in expediente
    assert "nuevo@mayab.com" not in ficha
    assert "viejo@mayab.com" in ficha


def test_el_expediente_cruza_las_convocatorias_de_la_feria(
    client, convocatoria
):
    """`RN-19` y `RN-21`: una editorial por persona y por feria, pero
    puede haber aplicado a la general y a la de un pabellón.

    Quien atiende una llamada necesita ver las dos, y por eso la URL no
    lleva convocatoria.
    """
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        ana, editorial, _ = _aplicante(
            conv, correo="ana@ej.com", nombre_editorial="Ediciones Mayab"
        )
        pabellon = fabricas.convocatoria(nombre="Pabellón infantil")
        mapas.importar(convocatoria=pabellon, datos=_mapa())
        cfg = configuracion.de_la_convocatoria(pabellon)
        cfg.costo_m2 = Decimal("1500")
        cfg.save(update_fields=["costo_m2"])
        segunda = solicitudes.enviar_solicitud(
            convocatoria=pabellon, persona=ana, editorial=editorial
        )
        segunda.estado = Solicitud.Estado.ACEPTADA
        segunda.fecha_revision = segunda.fecha_envio
        segunda.save()
        reservas.crear(convocatoria=pabellon, persona=ana, claves=["A1"])
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_expositor", editorial_id=editorial.pk)
    ).content.decode()

    assert "Pabellón infantil" in cuerpo
    assert cuerpo.count(conv.nombre) >= 1


def test_las_reservas_enlazan_a_su_gestion(client, convocatoria):
    """`CU-STD-031` paso 6: de aquí se salta a A4."""
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        ana, editorial, _ = _aplicante(
            conv, correo="ana@ej.com", nombre_editorial="Ediciones Mayab"
        )
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1", "A2"])
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_expositor", editorial_id=editorial.pk)
    ).content.decode()

    assert f"/stands/reserva/{reserva.pk}/" in cuerpo
    # Dos espacios de 6 m² a $2 500.
    assert "30,000.00" in cuerpo


def test_sin_reservas_lo_dice_sin_alarmar(client, convocatoria):
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        _, editorial, _ = _aplicante(
            conv, correo="ana@ej.com", nombre_editorial="Ediciones Mayab"
        )
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_expositor", editorial_id=editorial.pk)
    ).content.decode()

    assert "Todavía no ha reservado espacios" in cuerpo


def test_una_editorial_de_otra_feria_no_se_alcanza(client, convocatoria, feria_2028):
    """`ADR-0003`: vive en otro schema, así que la consulta no la
    encuentra — no hace falta comprobar la edición."""
    feria, _ = convocatoria
    with schema_context(feria_2028.schema_name):
        otra = fabricas.convocatoria()
        _, ajena, _ = _aplicante(
            otra, correo="lupe@ej.com", nombre_editorial="Del Golfo"
        )
        ajena_pk = ajena.pk
    client.force_login(_admin(feria))

    respuesta = client.get(
        _url(feria, "stands:detalle_expositor", editorial_id=ajena_pk)
    )

    with schema_context(feria.schema_name):
        assert not Editorial.objects.filter(pk=ajena_pk).exists()
    assert respuesta.status_code == 404
