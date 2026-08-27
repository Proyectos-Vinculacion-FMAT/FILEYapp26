"""
Alta de una convocatoria (`CU-FER-005`), por servicio y por el admin.

Lo que de verdad se prueba aquí no es que la fila se cree —eso es lo
fácil— sino las tres cosas que, si se rompen, **no dan síntoma**:

1. Que la convocatoria caiga en el schema de su feria y en ningún otro.
   Es la garantía entera de `ADR-0003`, y una fila en el schema
   equivocado no falla: simplemente aparece en la edición de otro.
2. Que el admin de `/django-admin/` **no** sirva este modelo. Registrarlo
   ahí no rompe el arranque; rompe la primera vez que alguien lo abre.
3. Que la puerta del admin de feria pida `is_staff`. Es la herramienta
   interna del equipo, no el panel del dueño.

Todas necesitan schemas de verdad: lo que se mira es en cuál quedó cada
cosa.
"""

import pytest
from django.db import IntegrityError, transaction
from django_tenants.utils import schema_context

from apps.ferias.models import Feria
from apps.registros.models import Persona

from ..models import Convocatoria, TipoConvocatoria
from ..servicios import altas

pytestmark = pytest.mark.django_db


def _crear(feria, **kwargs):
    """Llama al servicio desde dentro del schema de `feria`."""
    datos = {
        "tipo": TipoConvocatoria.EVT,
        "nombre": "Convocatoria de actividades",
        **kwargs,
    }
    with schema_context(feria.schema_name):
        return altas.crear_convocatoria(**datos)


def _staff(correo="tecnico@filey.org"):
    """Cuenta del equipo técnico: la que abre el admin de Django."""
    return Persona.objects.create_superuser(correo=correo, password="x")


def _url_alta(feria):
    return f"{feria.url}django-admin/convocatorias/convocatoria/add/"


# ── El servicio ───────────────────────────────────────────────


def test_nace_en_borrador(feria_2027):
    """Paso 6: abrirla es un acto aparte y deliberado (CU-FER-008)."""
    resultado = _crear(feria_2027)

    assert resultado.convocatoria.estado == Convocatoria.Estado.BORRADOR
    assert resultado.feria == feria_2027


def test_la_convocatoria_queda_en_el_schema_de_su_feria(feria_2027, feria_2028):
    """El aislamiento de ADR-0003, que es lo único que ata una fila a su feria."""
    _crear(feria_2027, nombre="Actividades 2027")

    with schema_context(feria_2027.schema_name):
        assert Convocatoria.objects.filter(nombre="Actividades 2027").exists()
    with schema_context(feria_2028.schema_name):
        assert not Convocatoria.objects.exists()


def test_fuera_de_una_feria_no_hay_donde_crearla(db):
    """Sobre `public` la tabla no existe: se rechaza antes de tocarla."""
    with pytest.raises(altas.AltaRechazada, match="pertenece a una feria"):
        altas.crear_convocatoria(tipo=TipoConvocatoria.EVT, nombre="Huérfana")


def test_una_edicion_archivada_no_admite_convocatorias_nuevas(feria_2027):
    """E2: una edición cerrada se consulta, no se le abren puertas."""
    feria_2027.estado = Feria.Estado.ARCHIVADA
    feria_2027.save()

    with pytest.raises(altas.AltaRechazada, match="archivada"):
        _crear(feria_2027)


def test_el_cierre_tiene_que_ser_posterior_a_la_apertura(feria_2027):
    with pytest.raises(altas.AltaRechazada, match="posterior"):
        _crear(feria_2027, fecha_apertura="2027-03-10", fecha_cierre="2027-03-01")


def test_un_nombre_de_una_letra_no_distingue_nada(feria_2027):
    """Con dos del mismo tipo el nombre es lo único que las separa (A2)."""
    with pytest.raises(altas.AltaRechazada):
        _crear(feria_2027, nombre="X")


def test_avisa_de_las_otras_del_mismo_tipo(feria_2027):
    """A2: no bloquea, avisa. Y no se cuenta a sí misma."""
    primera = _crear(feria_2027, nombre="Actividades generales")
    assert primera.otras_del_mismo_tipo == []

    segunda = _crear(feria_2027, nombre="Actividades infantiles")

    assert [c.nombre for c in segunda.otras_del_mismo_tipo] == ["Actividades generales"]


def test_la_base_tambien_rechaza_las_fechas_al_reves(feria_2027):
    """El invariante no depende de que se pase por el servicio.

    Es lo que separa una validación de formulario de una garantía: vale
    igual para el shell, para una carga masiva y para el módulo que
    mañana escriba una convocatoria por su cuenta.
    """
    with schema_context(feria_2027.schema_name):
        with pytest.raises(IntegrityError), transaction.atomic():
            Convocatoria.objects.create(
                tipo=TipoConvocatoria.VIS,
                nombre="Fechas al revés",
                fecha_apertura="2027-03-10",
                fecha_cierre="2027-03-01",
            )


# ── El admin de la feria ──────────────────────────────────────


def test_el_alta_desde_el_admin_de_una_feria_no_toca_la_otra(
    client, feria_2027, feria_2028
):
    """El mismo formulario, servido bajo dos prefijos, escribe en dos schemas."""
    client.force_login(_staff())

    respuesta = client.post(
        _url_alta(feria_2027),
        {"tipo": TipoConvocatoria.STD, "nombre": "Venta de stands 2027"},
    )

    assert respuesta.status_code == 302  # alta correcta → redirect al listado
    with schema_context(feria_2027.schema_name):
        assert Convocatoria.objects.get().nombre == "Venta de stands 2027"
    with schema_context(feria_2028.schema_name):
        assert not Convocatoria.objects.exists()


def test_el_alta_del_admin_pasa_por_el_servicio(client, feria_2027):
    """Nace en `borrador` aunque el formulario no pregunte por el estado."""
    client.force_login(_staff())

    client.post(
        _url_alta(feria_2027),
        {"tipo": TipoConvocatoria.VIS, "nombre": "Visitas escolares 2027"},
    )

    with schema_context(feria_2027.schema_name):
        assert Convocatoria.objects.get().estado == Convocatoria.Estado.BORRADOR


def test_el_admin_de_feria_no_lo_abre_quien_no_es_del_equipo(client, feria_2027):
    """Un participante con sesión sigue sin ser `is_staff`."""
    participante = Persona.objects.create_user(
        correo="ana@ejemplo.com", nombre="Ana", primer_apellido="Pech"
    )
    client.force_login(participante)

    respuesta = client.get(_url_alta(feria_2027))

    assert respuesta.status_code == 302
    assert "login" in respuesta.url


def test_una_edicion_archivada_no_ofrece_el_formulario(client, feria_2027):
    """E2 en la puerta: no se enseña un formulario que no se puede enviar."""
    feria_2027.estado = Feria.Estado.ARCHIVADA
    feria_2027.save()
    client.force_login(_staff())

    assert client.get(_url_alta(feria_2027)).status_code == 403


def test_el_admin_publico_no_sirve_las_convocatorias(client, feria_2027):
    """El modelo se registra en `admin_feria`, no en `admin.site`.

    Si alguien lo registrara en los dos, esta URL respondería 200 y
    reventaría al consultar: sobre `public` la tabla no existe.
    """
    client.force_login(_staff())

    respuesta = client.get("/django-admin/convocatorias/convocatoria/")

    assert respuesta.status_code == 404
