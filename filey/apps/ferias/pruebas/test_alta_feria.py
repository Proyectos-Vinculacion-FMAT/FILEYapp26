"""
Alta de una feria (`CU-FER-001`).

Lo que más se prueba aquí es **E2**: que no quede una feria a medias.
Una feria registrada pero sin schema migrado, sin slug de ruteo o sin
dueño es peor que no tenerla — aparece en los listados, alguien intenta
entrar, y la aplicación revienta contra tablas que no existen a mitad de
operación y sin causa evidente.
"""

import pytest
from django.core import mail
from django.db import connection
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria, Domain, Feria
from apps.ferias.servicios import altas
from apps.registros.models import Persona

pytestmark = pytest.mark.django_db


def _schemas():
    with connection.cursor() as cur:
        cur.execute("select nspname from pg_namespace")
        return {fila[0] for fila in cur.fetchall()}


# ── Camino feliz ──────────────────────────────────────────────


def test_el_alta_crea_feria_schema_ruteo_y_dueno(feria_2027):
    """Los cuatro artefactos del paso 3-7, o ninguno."""
    assert feria_2027.schema_name == "feria_2027"
    assert feria_2027.estado == Feria.Estado.EN_PREPARACION
    assert feria_2027.schema_name in _schemas()

    assert Domain.objects.get(tenant=feria_2027).domain == "2027"

    acceso = AdminFeria.objects.get(feria=feria_2027)
    assert acceso.es_dueno
    # `creado_por` nulo: nadie de dentro de la feria le dio ese acceso.
    assert acceso.creado_por is None


def test_el_slug_y_el_slug_de_ruteo_no_divergen(feria_2027):
    """Guardan lo mismo en dos sitios; el servicio es el único que escribe.

    `Feria.slug` es del modelo de dominio y `Domain.domain` es la
    mecánica de `django-tenants` en modo subfolder. Si se separaran, la
    feria existiría con una URL y sería alcanzable por otra.
    """
    assert Domain.objects.get(tenant=feria_2027).domain == feria_2027.slug


def test_el_schema_lleva_las_migraciones_de_contenido_aplicadas(feria_2027):
    """El paso 5. Sin esto la feria existe pero no se puede usar."""
    with schema_context(feria_2027.schema_name):
        from apps.convocatorias.models import Convocatoria

        assert Convocatoria.objects.count() == 0  # la tabla existe y está vacía


def test_la_feria_nace_vacia_y_sin_publicar(feria_2027):
    """Crear la feria no abre ninguna convocatoria."""
    assert feria_2027.estado == Feria.Estado.EN_PREPARACION


# ── A1: la cuenta del dueño puede existir ya ──────────────────


def test_si_el_dueno_ya_tiene_cuenta_se_reutiliza_sin_tocarla(feria_2027):
    """A1: es la misma persona que ya usa el sistema en otras ferias."""
    ana = Persona.objects.get(correo="ana@uady.mx")

    resultado = altas.crear_feria(
        nombre="FILEY 2029",
        slug="2029",
        correo_dueno="ana@uady.mx",
        # Se manda otro nombre a propósito: no debe pisarse el suyo.
        nombre_dueno="Nombre Distinto",
        primer_apellido_dueno="Apellido Distinto",
        enviar_aviso=False,
        verbosity=0,
    )

    assert not resultado.cuenta_creada
    assert resultado.dueno.pk == ana.pk
    ana.refresh_from_db()
    assert ana.nombre == "Ana"
    assert ana.primer_apellido == "Pech"


def test_una_persona_puede_ser_duena_de_varias_ferias(feria_2027):
    altas.crear_feria(
        nombre="FILEY 2029",
        slug="2029",
        correo_dueno="ana@uady.mx",
        enviar_aviso=False,
        verbosity=0,
    )
    ana = Persona.objects.get(correo="ana@uady.mx")

    assert ana.ferias_admin.filter(es_dueno=True).count() == 2


# ── E1: el slug ───────────────────────────────────────────────


@pytest.mark.parametrize(
    "slug", ["", "2027 otono", "2027_otono", "feria/2027", "-2027", "ñ", "a" * 58]
)
def test_un_slug_invalido_se_rechaza_sin_crear_nada(slug):
    with pytest.raises(altas.AltaRechazada):
        altas.crear_feria(
            nombre="X",
            slug=slug,
            correo_dueno="x@uady.mx",
            enviar_aviso=False,
            verbosity=0,
        )

    assert not Feria.reales.exists()


def test_un_slug_repetido_se_rechaza_y_no_toca_la_feria_existente(feria_2027):
    """E1: reutilizarlo apuntaría dos ferias al mismo contenido."""
    with pytest.raises(altas.AltaRechazada):
        altas.crear_feria(
            nombre="Otra",
            slug="2027",
            correo_dueno="otro@uady.mx",
            enviar_aviso=False,
            verbosity=0,
        )

    assert Feria.reales.filter(slug="2027").count() == 1
    assert Feria.objects.get(slug="2027").nombre == "FILEY 2027"


def test_el_slug_se_normaliza_a_minusculas(db):
    """Escribirlo con mayúsculas no es un error, es un descuido.

    Se normaliza porque el schema y la URL van en minúsculas de todos
    modos: rechazarlo obligaría a adivinar la regla sin ganar nada.
    """
    resultado = altas.crear_feria(
        nombre="FILEY 2034",
        slug="  FILEY2034  ",
        correo_dueno="x@uady.mx",
        enviar_aviso=False,
        verbosity=0,
    )

    assert resultado.feria.slug == "filey2034"
    assert resultado.feria.schema_name == "feria_filey2034"
    assert Domain.objects.get(tenant=resultado.feria).domain == "filey2034"


def test_sin_correo_de_dueno_no_hay_alta():
    with pytest.raises(altas.AltaRechazada):
        altas.crear_feria(
            nombre="X", slug="2030", correo_dueno="", enviar_aviso=False, verbosity=0
        )

    assert not Feria.reales.exists()


# ── E2: no queda una feria a medias ───────────────────────────


def test_si_falla_un_paso_posterior_no_queda_ni_feria_ni_schema(monkeypatch):
    """El caso que el servicio compensa a mano.

    `TenantMixin.save()` ya deshace el schema si falla al crearlo, pero
    no sabe nada de lo que viene después. Si el dueño no se puede crear,
    la feria y su schema ya existen — y hay que borrarlos.
    """
    def _explotar(*args, **kwargs):
        raise RuntimeError("la base se cayó a mitad del alta")

    monkeypatch.setattr(AdminFeria.objects, "create", _explotar)

    with pytest.raises(RuntimeError):
        altas.crear_feria(
            verbosity=0,
            nombre="FILEY 2031",
            slug="2031",
            correo_dueno="quien@uady.mx",
            enviar_aviso=False,
        )

    assert not Feria.objects.filter(slug="2031").exists()
    assert "feria_2031" not in _schemas()
    assert not Domain.objects.filter(domain="2031").exists()


# ── E3: el aviso ──────────────────────────────────────────────


def test_el_aviso_sale_al_dueno(db):
    resultado = altas.crear_feria(
        nombre="FILEY 2032",
        slug="2032",
        correo_dueno="nueva@uady.mx",
        nombre_dueno="Nueva",
        primer_apellido_dueno="Persona",
        verbosity=0,
    )

    assert resultado.aviso_enviado
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["nueva@uady.mx"]
    assert "FILEY 2032" in mail.outbox[0].subject
    # Saluda por el nombre de pila, y enlaza a la feria.
    assert "Hola Nueva" in mail.outbox[0].body
    assert "/f/2032/" in mail.outbox[0].body


def test_un_fallo_de_correo_no_deshace_el_alta(db, monkeypatch):
    """E3: el correo es cortesía, no credencial.

    Compárese con CU-REG-002 E3, donde el correo **es** la credencial y
    por eso un fallo sí anula el código.
    """
    def _explotar(*args, **kwargs):
        raise RuntimeError("el proveedor rechazó el envío")

    monkeypatch.setattr(
        "django.core.mail.EmailMultiAlternatives.send", _explotar
    )

    resultado = altas.crear_feria(
        nombre="FILEY 2033", slug="2033", correo_dueno="otra@uady.mx", verbosity=0
    )

    assert not resultado.aviso_enviado
    assert resultado.error_aviso
    # Y sin embargo la feria es perfectamente válida.
    assert Feria.reales.filter(slug="2033").exists()
    assert AdminFeria.objects.filter(feria=resultado.feria, es_dueno=True).exists()


def test_a2_se_puede_dar_de_alta_sin_avisar(feria_2027):
    """A2: preparar ediciones con antelación sin escribirle a nadie."""
    assert mail.outbox == []


# ── La fila de sistema ────────────────────────────────────────


def test_la_feria_de_sistema_existe_pero_no_es_una_feria(db):
    """`Feria.objects` la ve porque `django-tenants` la busca ahí."""
    assert Feria.objects.filter(schema_name="public").exists()
    assert not Feria.reales.filter(schema_name="public").exists()


def test_reales_solo_devuelve_ediciones(feria_2027, feria_2028):
    assert set(Feria.reales.values_list("slug", flat=True)) == {"2027", "2028"}
    assert Feria.objects.count() == 3  # las dos más la de sistema
