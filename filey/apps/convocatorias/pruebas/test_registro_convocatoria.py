"""
Inscribirse a una convocatoria (`RegistroConvocatoria`, `ADR-0006`).

La tabla es de tres columnas y su servicio cabe en una pantalla, así que
lo interesante no es que guarde: es que es **la única puerta** por la que
los seis módulos entrarán a `FER`, y todo lo que se le escape aquí se
escapa seis veces.

Cuatro cosas se vigilan, y las cuatro fallan en silencio si no se miran:

1. **La invariante del tipo.** El esquema no puede impedir que una
   solicitud de stands cuelgue de un registro de una convocatoria de
   eventos: el ``tipo`` vive un salto más allá. Es la única invariante de
   `FER` que es de código, y esta es la prueba que el ADR exige a cambio.
2. **La unicidad.** Dos registros de la misma persona a la misma puerta
   partirían su expediente en dos y descuadrarían los conteos.
3. **La clave foránea que cruza de schema.** `RegistroConvocatoria` vive
   en `feria_2027` y `Persona` en `public`: es la primera del proyecto
   que atraviesa esa frontera, y si no se creara de verdad, la base
   dejaría pasar registros de personas que no existen.
4. **El aislamiento.** Inscribirse en 2027 no puede verse desde 2028.
"""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError, connection, transaction
from django.db.models import ProtectedError
from django_tenants.utils import schema_context

from apps.ferias.models import Feria
from apps.registros.models import Persona

from ..models import Convocatoria, RegistroConvocatoria, TipoConvocatoria
from ..servicios import registros

pytestmark = pytest.mark.django_db


@pytest.fixture
def ana(db):
    return Persona.objects.create_user(
        correo="ana@ejemplo.com", nombre="Ana", primer_apellido="Pech"
    )


def _convocatoria(
    nombre="Stands 2027",
    estado=Convocatoria.Estado.ABIERTA,
    tipo=TipoConvocatoria.STD,
):
    return Convocatoria.objects.create(tipo=tipo, nombre=nombre, estado=estado)


# ── La invariante que la base no puede sostener ───────────────


def test_un_modulo_no_puede_colgar_de_una_convocatoria_de_otro_tipo(feria_2027, ana):
    """`ADR-0006`: la comprobación que sustituye a la clave compuesta.

    Si esta prueba desaparece, la invariante desaparece con ella: no hay
    nada en PostgreSQL que la sostenga.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria("Eventos 2027", tipo=TipoConvocatoria.EVT)

        with pytest.raises(registros.TipoQueNoCorresponde):
            registros.obtener_o_crear_registro(
                convocatoria=convocatoria,
                persona=ana,
                tipo_esperado=TipoConvocatoria.STD,
            )

        assert not RegistroConvocatoria.objects.exists()


def test_declarar_el_tipo_es_obligatorio(feria_2027, ana):
    """No tiene valor por omisión, y ese es todo su propósito.

    Con uno, olvidarlo pasaría inadvertido y la comprobación quedaría
    apagada en el módulo que lo olvidara.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()

        with pytest.raises(TypeError):
            registros.obtener_o_crear_registro(
                convocatoria=convocatoria, persona=ana
            )


# ── Cuándo se puede entrar ────────────────────────────────────


def test_inscribirse_a_una_convocatoria_abierta(feria_2027, ana):
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()

        registro, se_creo = registros.obtener_o_crear_registro(
            convocatoria=convocatoria, persona=ana, tipo_esperado=TipoConvocatoria.STD
        )

        assert se_creo
        assert registro.estado == RegistroConvocatoria.Estado.ACTIVO


@pytest.mark.parametrize(
    "estado", [Convocatoria.Estado.BORRADOR, Convocatoria.Estado.CERRADA]
)
def test_solo_la_convocatoria_abierta_admite_registros(feria_2027, ana, estado):
    """`estado` es lo que abre la puerta, no las fechas (`CU-FER-008`).

    El borrador no tiene revisada su configuración y la cerrada ya no
    recibe. Se comprueba en `FER` y no en cada módulo: es una regla sobre
    la convocatoria, y repartirla entre seis apps son seis ocasiones de
    olvidarla.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria(estado=estado)

        with pytest.raises(registros.RegistroRechazado):
            registros.obtener_o_crear_registro(
                convocatoria=convocatoria,
                persona=ana,
                tipo_esperado=TipoConvocatoria.STD,
            )


def test_una_edicion_archivada_no_recibe_registros(feria_2027, ana):
    """`CU-FER-006` E1: una edición cerrada se consulta, no se opera."""
    feria_2027.estado = Feria.Estado.ARCHIVADA
    feria_2027.save()

    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()

        with pytest.raises(registros.RegistroRechazado):
            registros.obtener_o_crear_registro(
                convocatoria=convocatoria,
                persona=ana,
                tipo_esperado=TipoConvocatoria.STD,
            )


def test_sin_cuenta_no_hay_registro(feria_2027):
    """El registro apunta a una `Persona`: mirar no la pide, entrar sí."""
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()

        with pytest.raises(registros.RegistroRechazado):
            registros.obtener_o_crear_registro(
                convocatoria=convocatoria,
                persona=AnonymousUser(),
                tipo_esperado=TipoConvocatoria.STD,
            )


# ── Volver a aplicar, y la unicidad ───────────────────────────


def test_volver_a_aplicar_reusa_el_registro(feria_2027, ana):
    """RN-22 de `STD`: tras un rechazo se aplica otra vez.

    Lo que se repite es el **expediente**, no la inscripción: el registro
    es el mismo y de él cuelgan los dos intentos.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()

        primero, _ = registros.obtener_o_crear_registro(
            convocatoria=convocatoria, persona=ana, tipo_esperado=TipoConvocatoria.STD
        )
        segundo, se_creo = registros.obtener_o_crear_registro(
            convocatoria=convocatoria, persona=ana, tipo_esperado=TipoConvocatoria.STD
        )

        assert not se_creo
        assert segundo.pk == primero.pk
        assert RegistroConvocatoria.objects.count() == 1


def test_quien_se_retiro_y_vuelve_queda_activo(feria_2027, ana):
    """Dejarlo `retirado` lo borraría de los conteos con expediente vivo."""
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()
        RegistroConvocatoria.objects.create(
            convocatoria=convocatoria,
            persona=ana,
            estado=RegistroConvocatoria.Estado.RETIRADO,
        )

        registro, _ = registros.obtener_o_crear_registro(
            convocatoria=convocatoria, persona=ana, tipo_esperado=TipoConvocatoria.STD
        )

        assert registro.estado == RegistroConvocatoria.Estado.ACTIVO


def test_la_unicidad_la_sostiene_la_base(feria_2027, ana):
    """No solo el `get_or_create`: dos escrituras a la vez lo esquivarían."""
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()
        RegistroConvocatoria.objects.create(convocatoria=convocatoria, persona=ana)

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                RegistroConvocatoria.objects.create(
                    convocatoria=convocatoria, persona=ana
                )


def test_la_misma_persona_si_entra_a_dos_convocatorias(feria_2027, ana):
    """La unicidad es por puerta, no por persona.

    Una feria puede tener dos convocatorias de stands (`CU-FER-005` A2) y
    apuntarse a las dos es legítimo: son dos registros y dos expedientes.
    """
    with schema_context(feria_2027.schema_name):
        general = _convocatoria("Stands general")
        pabellon = _convocatoria("Stands del pabellón infantil")

        for convocatoria in (general, pabellon):
            registros.obtener_o_crear_registro(
                convocatoria=convocatoria,
                persona=ana,
                tipo_esperado=TipoConvocatoria.STD,
            )

        assert RegistroConvocatoria.objects.count() == 2


# ── Las dos fronteras: el schema y la cuenta ──────────────────


def test_el_registro_no_se_ve_desde_otra_feria(feria_2027, feria_2028, ana):
    """La feria es el schema, no una columna (`ADR-0003`)."""
    with schema_context(feria_2027.schema_name):
        registros.obtener_o_crear_registro(
            convocatoria=_convocatoria(),
            persona=ana,
            tipo_esperado=TipoConvocatoria.STD,
        )

    with schema_context(feria_2028.schema_name):
        assert not RegistroConvocatoria.objects.exists()


def test_la_clave_foranea_a_persona_la_valida_postgresql(feria_2027):
    """Cruza a `public`, y es la primera del proyecto que lo hace.

    Si `django-tenants` no dejara el `search_path` en `[feria_x, public]`
    al migrar, la restricción no existiría y esto pasaría sin protestar.

    Hace falta `check_constraints()` porque Django declara sus claves
    foráneas como ``DEFERRABLE INITIALLY DEFERRED``: sin forzarla, la
    violación no sale al soltar el savepoint sino al cerrar la
    transacción de la prueba, ya fuera de este bloque.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                RegistroConvocatoria.objects.create(
                    convocatoria=convocatoria, persona_id=999_999
                )
                connection.check_constraints()


def test_una_persona_con_registro_no_se_puede_borrar(feria_2027, ana):
    """`PROTECT`: de un registro cuelga el expediente entero de alguien.

    Con `CASCADE`, dar de baja una cuenta se llevaría por delante su
    solicitud, su reserva y sus abonos sin que nadie se entere.
    """
    with schema_context(feria_2027.schema_name):
        registros.obtener_o_crear_registro(
            convocatoria=_convocatoria(),
            persona=ana,
            tipo_esperado=TipoConvocatoria.STD,
        )

        with pytest.raises(ProtectedError):
            ana.delete()
