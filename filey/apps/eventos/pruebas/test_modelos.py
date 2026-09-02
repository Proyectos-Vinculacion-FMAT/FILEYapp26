"""
Los modelos de `EVT` y, sobre todo, la forma que toma el polimorfismo.

El modelo de datos describe un `RouterActividades` con un `detalle_id`
suelto hacia una de ocho tablas. Aquí eso es herencia multitabla, y lo
que se vigila es justo lo que se compró con el cambio:

1. **Los ocho tipos existen sin que nadie los dé de alta.** Los siembra
   una migración, así que una feria recién creada puede recibir
   propuestas el mismo día.
2. **Del padre se baja a la hija por el tipo**, no probando las ocho.
3. **La liga es una clave foránea de verdad.** Un `detalle_id` entero
   dejaría colgar una actividad de una fila que no existe; aquí la base
   lo impide, y ésa era la razón de elegir herencia multitabla.
4. **El folio se compone, no se guarda** (§2.4): cambiar el prefijo lo
   cambia en todas partes a la vez.
5. **Las tablas viven en el schema de la feria**, no en `public`.
"""

import pytest
from django.db import connection, transaction
from django.db.utils import ProgrammingError
from django_tenants.utils import schema_context

from ..models import (
    MODELO_POR_TIPO,
    ActividadConversatorio,
    ActividadPresentacionLibro,
    CatalogoActividades,
    ConfiguracionConvocatoria,
    Solicitud,
)
from . import fabricas

pytestmark = pytest.mark.django_db


# ── El catálogo ───────────────────────────────────────────────


def test_los_ocho_tipos_llegan_con_el_schema(feria_2027):
    """Sembrar el catálogo es de la migración, no de un comando.

    Si dependiera de que alguien lo ejecute, una feria recién creada
    tendría el formulario sin tipos que elegir y nada lo avisaría hasta
    que alguien intentara proponer.
    """
    with schema_context(feria_2027.schema_name):
        assert CatalogoActividades.objects.count() == 8
        # El orden es el del selector, no el alfabético: es el que la
        # Coordinación lee de arriba abajo.
        primeros = list(
            CatalogoActividades.objects.values_list("nombre", flat=True)[:3]
        )
        assert primeros == ["conversatorio", "conferencia", "charla"]


def test_cada_tipo_del_catalogo_tiene_su_tabla():
    """Los ocho valores y los ocho modelos se corresponden uno a uno.

    Agregar un tipo al catálogo sin su tabla dejaría un formulario que se
    puede elegir y no se puede guardar.
    """
    assert set(MODELO_POR_TIPO) == set(CatalogoActividades.Nombre.values)


# ── Del padre a la hija ───────────────────────────────────────


@pytest.mark.parametrize("nombre_tipo", CatalogoActividades.Nombre.values)
def test_cada_tipo_se_captura_y_se_resuelve_desde_el_padre(feria_2027, nombre_tipo):
    """Una propuesta de cada tipo, y `detalle` devuelve su fila hija.

    Es la prueba de que la herencia multitabla sostiene lo que el
    documento pide del router: saber el tipo y llegar al detalle.
    """
    with schema_context(feria_2027.schema_name):
        registro = fabricas.registro(fabricas.persona(), fabricas.convocatoria())
        propuesta = fabricas.solicitud(registro)
        Modelo = MODELO_POR_TIPO[nombre_tipo]

        # Cada tabla exige lo suyo; lo común es el primer nombre y su
        # semblanza, que es lo único obligatorio en los ocho.
        campos = {"nombre_participante_1": "Elena Poniatowska",
                  "semblanza_participante_1": "Escritora y periodista."}
        if nombre_tipo == "presentacion_libro":
            campos = {
                "titulo_publicacion": "El mar que nos habita",
                "tipo_presentador": "autor",
                "nombre_editorial": "La Nave",
                "nombre_autor_1": "Elena Poniatowska",
                "semblanza_autor_1": "Escritora y periodista.",
            }
        elif nombre_tipo == "presentacion_revista":
            campos = {
                "titulo_publicacion": "Cuadernos del Mayab",
                "tipo_presentador": "editor",
                "nombre_editorial": "La Nave",
                "nombre_editor_1": "Elena Poniatowska",
                "semblanza_editor_1": "Escritora y periodista.",
            }

        detalle = Modelo.objects.create(
            solicitud=propuesta, tipo=fabricas.tipo(nombre_tipo), **campos
        )

        # Y desde el padre se baja a la hija, sin probar las ocho.
        propuesta.refresh_from_db()
        assert propuesta.actividad.detalle == detalle
        assert propuesta.actividad.tipo.nombre == nombre_tipo


def test_la_actividad_no_puede_colgar_de_una_solicitud_que_no_existe(feria_2027):
    """La razón de elegir herencia multitabla sobre un entero suelto.

    Con `detalle_id` como entero, esto se guardaría sin protestar y la
    fila quedaría huérfana. Con clave foránea real, la base lo rechaza.
    """
    with schema_context(feria_2027.schema_name):
        tipo = fabricas.tipo("conversatorio")
        with pytest.raises(Exception):
            with transaction.atomic():
                ActividadConversatorio.objects.create(
                    solicitud_id=999_999,
                    tipo=tipo,
                    nombre_participante_1="Nadie",
                    semblanza_participante_1="Nadie.",
                )


def test_borrar_la_solicitud_se_lleva_su_actividad(feria_2027):
    """La actividad no tiene sentido sin su solicitud: `CASCADE`.

    Es lo contrario que el registro de `FER`, que va con `PROTECT`
    porque de él cuelga el expediente entero de alguien en la feria.
    """
    with schema_context(feria_2027.schema_name):
        registro = fabricas.registro(fabricas.persona(), fabricas.convocatoria())
        propuesta = fabricas.solicitud(registro)
        ActividadConversatorio.objects.create(
            solicitud=propuesta,
            tipo=fabricas.tipo("conversatorio"),
            nombre_participante_1="Elena Poniatowska",
            semblanza_participante_1="Escritora y periodista.",
        )

        propuesta.delete()
        assert ActividadConversatorio.objects.count() == 0


# ── El folio ──────────────────────────────────────────────────


def test_el_folio_se_compone_y_no_se_guarda(feria_2027):
    """Cambiar el prefijo cambia el folio de todas, sin migrar nada.

    Si el folio fuera una columna, cambiar el prefijo dejaría dos
    formatos conviviendo en la misma convocatoria.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        ConfiguracionConvocatoria.objects.create(
            convocatoria=convocatoria, prefijo_folio="EVE"
        )
        registro = fabricas.registro(fabricas.persona(), convocatoria)
        propuesta = fabricas.solicitud(registro)

        assert propuesta.folio == f"EVE-{propuesta.pk}"

        convocatoria.configuracion_eventos.prefijo_folio = "ACT"
        convocatoria.configuracion_eventos.save()
        propuesta = Solicitud.objects.get(pk=propuesta.pk)
        assert propuesta.folio == f"ACT-{propuesta.pk}"


def test_sin_configuracion_el_folio_no_revienta(feria_2027):
    """Un folio es una etiqueta, no una decisión.

    No debería faltar —la crea el alta de la convocatoria—, pero si
    falta, la pantalla de alguien no puede caerse por eso.
    """
    with schema_context(feria_2027.schema_name):
        registro = fabricas.registro(fabricas.persona(), fabricas.convocatoria())
        propuesta = fabricas.solicitud(registro)
        assert propuesta.folio == f"EVE-{propuesta.pk}"


# ── Aislamiento por feria ─────────────────────────────────────


def test_las_tablas_de_eventos_no_existen_en_public(feria_2027):
    """`ADR-0003`: el contenido vive en el schema de su feria.

    Que la tabla no exista en `public` es lo que hace imposible que una
    consulta desde fuera de una feria alcance sus propuestas. Si algún
    día `apps.eventos` acabara en `SHARED_APPS`, esto lo delata.
    """
    connection.set_schema_to_public()
    with pytest.raises(ProgrammingError):
        with transaction.atomic():
            Solicitud.objects.count()


def test_cada_feria_ve_solo_sus_propuestas(feria_2027, feria_2028):
    """Dos ferias, dos schemas, ninguna consulta cruzada.

    No hay filtro que escribir ni `feria_id` que recordar: la propuesta
    de 2027 no está en el `search_path` de 2028.
    """
    with schema_context(feria_2027.schema_name):
        registro = fabricas.registro(fabricas.persona(), fabricas.convocatoria())
        fabricas.solicitud(registro)
        assert Solicitud.objects.count() == 1

    with schema_context(feria_2028.schema_name):
        assert Solicitud.objects.count() == 0


# ── Lo que el aplicante declara ───────────────────────────────


def test_es_uady_es_autodeclaracion_y_nace_en_falso(feria_2027):
    """Lo que cuenta para la categoría es lo que valide el administrador.

    Aquí solo se guarda lo que dijo quien propone (§2.4); el valor bueno
    lo escribe el dictamen, en la etapa 2.
    """
    with schema_context(feria_2027.schema_name):
        registro = fabricas.registro(fabricas.persona(), fabricas.convocatoria())
        propuesta = Solicitud.objects.create(
            registro=registro,
            **{**fabricas.PROPUESTA, **{"es_uady": True}},
        )
        assert propuesta.es_uady is True
        assert Solicitud._meta.get_field("es_uady").default is False


def test_los_autores_de_un_libro_participan_uno_por_uno(feria_2027):
    """Cinco autores, cinco casillas: no un sí/no para «el autor».

    Es el cambio del 2026-08-30: con más de un autor, la pregunta en
    singular no tiene respuesta, y la lista de nombres presentes escrita
    a mano podía nombrar a quien no estaba entre los autores.

    Y **nacen en falso**: que alguien estará en la feria es una
    afirmación que hay que hacer, no algo que se dé por supuesto y haya
    que desmarcar; marcarlas por omisión llenaría el programa de
    asistentes que nadie confirmó.
    """
    with schema_context(feria_2027.schema_name):
        registro = fabricas.registro(fabricas.persona(), fabricas.convocatoria())
        propuesta = fabricas.solicitud(registro)
        libro = ActividadPresentacionLibro.objects.create(
            solicitud=propuesta,
            tipo=fabricas.tipo("presentacion_libro"),
            titulo_publicacion="El mar que nos habita",
            tipo_presentador="autor",
            nombre_editorial="La Nave",
            nombre_autor_1="Elena Poniatowska",
            semblanza_autor_1="Escritora y periodista.",
            nombre_autor_2="Juan Villoro",
            semblanza_autor_2="Escritor.",
            autor_2_participa=True,
        )

        # Sin decir nada, no participa. Solo el que se marcó, participa.
        assert libro.autor_1_participa is False
        assert libro.autor_2_participa is True
        # Y hay hueco para los cinco que admite la tabla.
        assert all(
            hasattr(libro, f"autor_{n}_participa") for n in range(1, 6)
        )
