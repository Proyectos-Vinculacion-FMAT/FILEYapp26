"""
El enganche entre el catálogo y los módulos (`ADR-0006`).

Lo que se vigila aquí no es que el registro guarde cosas —eso es un
diccionario— sino las tres formas en que este patrón se rompe sin que
nadie se entere:

1. **El catálogo se cae por un módulo que no está.** Es una pantalla
   pública y hoy cinco de los seis tipos no tienen módulo; un
   `NoReverseMatch` en producción sería una portada rota por una función
   que aún no existe.
2. **Dos apps se pelean un tipo, o una se inscribe con un tipo mal
   escrito.** Lo primero se resolvería por el orden de `INSTALLED_APPS`;
   lo segundo dejaría el módulo inalcanzable para siempre, con su tarjeta
   diciendo "próximamente".
3. **Una convocatoria de stands nace sin su configuración.** `CU-FER-005`
   E1 pide que si eso pasa no quede ni la convocatoria: media alta es
   peor que ninguna, porque el módulo no se puede operar y nada lo
   señala.

.. note:: Por qué el módulo de mentira apunta a una ruta del admin

   Ninguna app vertical existe todavía, así que no hay ninguna
   ``stands:aplicar`` que resolver. Se usa la ruta de cambio del admin de
   la edición porque cumple lo único que importa para esto: es un nombre
   de ruta **real**, montado en el urlconf de dentro de una feria, que
   recibe el id de la convocatoria. Lo que se prueba es que el registro
   resuelve un nombre de ruta, no cuál.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria, Feria
from apps.registros.models import Persona

from .. import modulos
from ..models import Convocatoria, RegistroConvocatoria, TipoConvocatoria
from ..servicios import altas, catalogo

pytestmark = pytest.mark.django_db

#: El nombre de ruta que hace de `stands:aplicar` mientras `stands` no
#: exista. Ver la nota del encabezado.
RUTA_DE_MENTIRA = "admin_feria:convocatorias_convocatoria_change"


def modulo_falso(tipo=TipoConvocatoria.STD, crear_configuracion=None):
    return modulos.Modulo(
        tipo=tipo,
        etiqueta="Venta de stands",
        url_aplicar=RUTA_DE_MENTIRA,
        crear_configuracion=crear_configuracion,
    )


@pytest.fixture
def participante(db):
    return Persona.objects.create_user(
        correo="ana@ejemplo.com", nombre="Ana", primer_apellido="Pech"
    )


def _convocatoria(
    nombre="Stands 2027",
    estado=Convocatoria.Estado.ABIERTA,
    tipo=TipoConvocatoria.STD,
):
    return Convocatoria.objects.create(tipo=tipo, nombre=nombre, estado=estado)


# ── El registro de módulos ────────────────────────────────────


def test_un_tipo_sin_modulo_no_es_un_error():
    """Sigue siendo el estado de `EVT` y de `VIS`."""
    assert modulos.modulo_de(TipoConvocatoria.VIS) is None
    assert modulos.modulo_de(TipoConvocatoria.EVT) is None


def test_un_tipo_mal_escrito_no_se_inscribe():
    """Sin esto, `STND` quedaría inscrito y su módulo inalcanzable."""
    with pytest.raises(modulos.TipoNoValido):
        modulos.registrar(modulo_falso(tipo="STND"))

    assert "STND" not in modulos.modulos_registrados()


def test_dos_modulos_no_pueden_reclamar_el_mismo_tipo():
    """Cuál gana dependería del orden de `INSTALLED_APPS`."""
    otro = modulos.Modulo(
        tipo=TipoConvocatoria.STD, etiqueta="Otra cosa", url_aplicar="otra:ruta"
    )

    with modulos.modulo_temporal(modulo_falso()):
        with pytest.raises(modulos.ModuloDuplicado):
            modulos.registrar(otro)


def test_volver_a_inscribir_el_mismo_modulo_no_es_error():
    """`ready()` puede correr más de una vez y eso no es un síntoma."""
    with modulos.modulo_temporal(modulo_falso()):
        modulos.registrar(modulo_falso())
        assert modulos.modulo_de(TipoConvocatoria.STD).etiqueta == "Venta de stands"


def test_el_registro_vuelve_a_como_estaba_al_salir_del_bloque():
    """La contrapartida de que sea estado global del proceso.

    Se comprueba contra los dos casos, porque son distintos: `STD` tiene
    un módulo de verdad detrás —`apps.stands` se inscribe en su
    ``ready()``— y `VIS` no tiene ninguno. Restaurar mal el primero
    dejaría a las pruebas siguientes con un módulo de mentira; restaurar
    mal el segundo, con uno que no existe.
    """
    real = modulos.modulo_de(TipoConvocatoria.STD)
    assert real is not None, "apps.stands debería estar inscrito"

    with modulos.modulo_temporal(
        modulos.Modulo(
            tipo=TipoConvocatoria.STD, etiqueta="De mentira", url_aplicar=RUTA_DE_MENTIRA
        )
    ):
        assert modulos.modulo_de(TipoConvocatoria.STD).etiqueta == "De mentira"
    assert modulos.modulo_de(TipoConvocatoria.STD) == real

    with modulos.modulo_temporal(modulo_falso(tipo=TipoConvocatoria.VIS)):
        assert modulos.modulo_de(TipoConvocatoria.VIS) is not None
    assert modulos.modulo_de(TipoConvocatoria.VIS) is None


# ── Paso 6 y E1 de CU-FER-005 ─────────────────────────────────


def test_el_alta_llama_al_callback_del_modulo(feria_2027):
    """Paso 6: la convocatoria nace con la configuración de su módulo."""
    configuradas = []

    with schema_context(feria_2027.schema_name):
        with modulos.modulo_temporal(
            modulo_falso(crear_configuracion=configuradas.append)
        ):
            resultado = altas.crear_convocatoria(
                tipo=TipoConvocatoria.STD, nombre="Stands 2027"
            )

    assert configuradas == [resultado.convocatoria]


def test_sin_modulo_la_convocatoria_se_crea_igual(feria_2027):
    """Un tipo sin módulo se da de alta sin configuración y sin drama."""
    with schema_context(feria_2027.schema_name):
        altas.crear_convocatoria(tipo=TipoConvocatoria.VIS, nombre="Visitas 2027")

        assert Convocatoria.objects.filter(tipo=TipoConvocatoria.VIS).exists()


def test_si_la_configuracion_falla_no_queda_ni_la_convocatoria(feria_2027):
    """E1: la transacción se deshace entera.

    Es deliberadamente más duro que CU-FER-003 E3, donde lo que falla es
    un correo de cortesía. Aquí faltaría el dato sin el cual el módulo no
    se puede operar, y una convocatoria de stands a medias engaña: se ve
    igual que una buena en el catálogo del dueño.
    """

    def revienta(convocatoria):
        raise RuntimeError("no hay costo_m2 por omisión")

    with schema_context(feria_2027.schema_name):
        with modulos.modulo_temporal(modulo_falso(crear_configuracion=revienta)):
            with pytest.raises(altas.ConfiguracionDelModuloFallo):
                altas.crear_convocatoria(
                    tipo=TipoConvocatoria.STD, nombre="Stands 2027"
                )

        assert not Convocatoria.objects.exists()


# ── La tarjeta del catálogo ───────────────────────────────────


def test_sin_modulo_la_tarjeta_dice_proximamente(client, feria_2027):
    """El catálogo es público: no puede caerse por un módulo que falta."""
    with schema_context(feria_2027.schema_name):
        _convocatoria("Visitas 2027", tipo=TipoConvocatoria.VIS)

    cuerpo = client.get(feria_2027.url).content.decode()

    assert "Próximamente" in cuerpo
    assert "Registrarme" not in cuerpo


def test_con_modulo_la_tarjeta_lleva_de_verdad_al_formulario(client, feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()

    with modulos.modulo_temporal(modulo_falso()):
        cuerpo = client.get(feria_2027.url).content.decode()

    destino = (
        f"{feria_2027.url}django-admin/convocatorias/convocatoria/"
        f"{convocatoria.pk}/change/"
    )
    assert "Registrarme" in cuerpo
    assert destino in cuerpo


def test_un_modulo_inscrito_sin_sus_rutas_montadas_degrada(client, feria_2027):
    """La red de seguridad del `NoReverseMatch`.

    Un módulo puede inscribirse en `ready()` y no tener sus rutas en el
    urlconf —a medio construir, o montado solo en otro despliegue—. Que
    eso tire la portada de la feria sería desproporcionado.
    """
    with schema_context(feria_2027.schema_name):
        _convocatoria()

    huerfano = modulos.Modulo(
        tipo=TipoConvocatoria.STD, etiqueta="Stands", url_aplicar="stands:aplicar"
    )
    with modulos.modulo_temporal(huerfano):
        respuesta = client.get(feria_2027.url)

    assert respuesta.status_code == 200
    assert "Próximamente" in respuesta.content.decode()


def test_quien_ya_se_registro_ve_su_solicitud_y_no_el_alta(
    client, feria_2027, participante
):
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()
        RegistroConvocatoria.objects.create(
            convocatoria=convocatoria, persona=participante
        )

    client.force_login(participante)
    with modulos.modulo_temporal(modulo_falso()):
        cuerpo = client.get(feria_2027.url).content.decode()

    assert "Ver mi solicitud" in cuerpo
    assert "Registrarme" not in cuerpo


def test_una_edicion_archivada_no_ofrece_registro(client, feria_2027):
    """`CU-FER-006` E1, con independencia del estado de la convocatoria."""
    with schema_context(feria_2027.schema_name):
        _convocatoria()
    feria_2027.estado = Feria.Estado.ARCHIVADA
    feria_2027.save()

    with modulos.modulo_temporal(modulo_falso()):
        cuerpo = client.get(feria_2027.url).content.decode()

    assert "Registrarme" not in cuerpo


def test_quien_administra_ve_el_conteo_de_registros(client, feria_2027, participante):
    """El conteo no es dato del participante (`CU-FER-006`)."""
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()
        RegistroConvocatoria.objects.create(
            convocatoria=convocatoria, persona=participante
        )

    admin = Persona.objects.create_user(
        correo="rita@filey.org", nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria_2027, persona=admin, es_dueno=False)
    client.force_login(admin)

    cuerpo = client.get(feria_2027.url).content.decode()

    assert "1 registro" in cuerpo


def test_el_participante_no_ve_el_conteo(client, feria_2027, participante):
    with schema_context(feria_2027.schema_name):
        convocatoria = _convocatoria()
        RegistroConvocatoria.objects.create(
            convocatoria=convocatoria, persona=participante
        )

    client.force_login(participante)
    cuerpo = client.get(feria_2027.url).content.decode()

    assert "1 registro" not in cuerpo


def test_el_catalogo_no_consulta_una_vez_por_tarjeta(feria_2027, participante):
    """Las inscripciones de quien mira salen en una sola consulta.

    Sin esto el coste del catálogo crece con el número de convocatorias,
    que es justo lo que el patrón invita a hacer sin querer: la pregunta
    "¿ya se registró?" es por tarjeta, y contestarla por tarjeta es lo
    natural de escribir.

    Se cuentan solo los ``SELECT``: `django-tenants` intercala un
    ``SET search_path`` cada vez que `schema_context` entra o sale, y eso
    no es lo que esta prueba vigila.
    """
    with schema_context(feria_2027.schema_name):
        for i in range(5):
            _convocatoria(f"Stands {i}")

        with modulos.modulo_temporal(modulo_falso()):
            with CaptureQueriesContext(connection) as consultas:
                catalogo.entradas_visibles(
                    es_administrador=False, persona=participante, feria=feria_2027
                )

    selects = [c for c in consultas.captured_queries if c["sql"].startswith("SELECT")]

    # 1 el catálogo + 1 las inscripciones de esta persona. Cinco tarjetas
    # y las mismas dos consultas.
    assert len(selects) == 2
