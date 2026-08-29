"""
Enviar y reenviar la solicitud (`CU-STD-001`, `CU-STD-002`, `RN-22`).

`STD` es el primer módulo que estrena el enganche de `ADR-0006`, así que
lo que se vigila aquí no es solo el dominio: es que el patrón que los
otros cinco van a copiar funcione.

Cinco cosas, y las cinco fallan sin dar síntoma:

1. **El registro nace con la solicitud, no antes.** Si naciera al pulsar
   el botón del catálogo, los conteos de la convocatoria contarían gente
   que nunca aplicó.
2. **La invariante del tipo.** Nada en el esquema impide colgar una
   solicitud de stands de un registro de una convocatoria de eventos.
3. **Una sola solicitud viva por registro**, sostenida por la base y no
   solo por el servicio: dos envíos a la vez esquivarían la comprobación.
4. **La fotografía no se mueve.** Corregir la ficha después de enviar
   reescribiría lo que el administrador está dictaminando.
5. **Tras un rechazo se puede volver a aplicar** (`RN-22`).
"""

import pytest
from django.db import IntegrityError, transaction
from django_tenants.utils import schema_context

from apps.convocatorias.models import (
    Convocatoria,
    RegistroConvocatoria,
    TipoConvocatoria,
)
from apps.convocatorias.modulos import modulo_de
from apps.convocatorias.servicios import registros

from ..models import Solicitud
from ..servicios import solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


# ── El módulo está inscrito ───────────────────────────────────


def test_stands_se_inscribe_en_el_registro_de_modulos():
    """La prueba que `ADR-0006` exige a cada módulo, y por qué.

    Un módulo que se olvide de inscribirse **no da error**: su tarjeta
    dice "próximamente" para siempre y nadie puede aplicar. Es el único
    fallo del patrón que no se ve.
    """
    modulo = modulo_de(TipoConvocatoria.STD)

    assert modulo is not None
    assert modulo.url_aplicar == "stands:solicitud"
    assert modulo.crear_configuracion is not None


# ── El envío ──────────────────────────────────────────────────


def test_enviar_crea_el_registro_y_la_solicitud(feria_2027):
    """`CU-STD-001` paso 6: el registro nace aquí, no en el catálogo."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        ficha = fabricas.editorial(ana)

        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=ficha
        )

        assert solicitud.estado == Solicitud.Estado.PENDIENTE
        assert RegistroConvocatoria.objects.count() == 1
        assert solicitud.registro.persona == ana


def test_mirar_la_convocatoria_no_deja_registro(feria_2027):
    """El registro se crea al guardar el expediente, no al pasar por ahí.

    Es la mitad de `ADR-0006` que no se puede probar desde el catálogo:
    allí se ve que el enlace navega; aquí, que navegar no inscribe.
    """
    with schema_context(feria_2027.schema_name):
        fabricas.persona()
        fabricas.convocatoria()

        assert not RegistroConvocatoria.objects.exists()


def test_una_solicitud_de_stands_no_cuelga_de_una_convocatoria_de_eventos(feria_2027):
    """La invariante que la base no puede sostener (`ADR-0006`).

    Si esta prueba desaparece, la invariante desaparece con ella.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        eventos = fabricas.convocatoria("Eventos 2027", tipo=TipoConvocatoria.EVT)
        ficha = fabricas.editorial(ana)

        with pytest.raises(solicitudes.EnvioRechazado):
            solicitudes.enviar_solicitud(
                convocatoria=eventos, persona=ana, editorial=ficha
            )

        assert not Solicitud.objects.exists()


@pytest.mark.parametrize(
    "estado", [Convocatoria.Estado.BORRADOR, Convocatoria.Estado.CERRADA]
)
def test_una_convocatoria_que_no_esta_abierta_no_recibe(feria_2027, estado):
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria(estado=estado)
        ficha = fabricas.editorial(ana)

        with pytest.raises(solicitudes.EnvioRechazado):
            solicitudes.enviar_solicitud(
                convocatoria=conv, persona=ana, editorial=ficha
            )


def test_no_se_puede_enviar_una_segunda_con_una_viva(feria_2027):
    """`CU-STD-001` E2."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        ficha = fabricas.editorial(ana)
        solicitudes.enviar_solicitud(convocatoria=conv, persona=ana, editorial=ficha)

        with pytest.raises(solicitudes.EnvioRechazado):
            solicitudes.enviar_solicitud(
                convocatoria=conv, persona=ana, editorial=ficha
            )

        assert Solicitud.objects.count() == 1


def test_la_unicidad_de_la_solicitud_viva_la_sostiene_la_base(feria_2027):
    """No solo el servicio: dos envíos a la vez lo esquivarían.

    Es una restricción **parcial** —solo sobre `pendiente` y
    `cambios_solicitados`—, que es lo que permite que convivan varias
    rechazadas del mismo registro (`RN-22`).
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        ficha = fabricas.editorial(ana)
        primera = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=ficha
        )

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Solicitud.objects.create(
                    registro=primera.registro,
                    editorial=ficha,
                    estado=Solicitud.Estado.PENDIENTE,
                )


def test_la_misma_persona_aplica_a_dos_convocatorias(feria_2027):
    """Una feria puede tener dos convocatorias de stands (`CU-FER-005` A2)."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        ficha = fabricas.editorial(ana)
        general = fabricas.convocatoria("Stands general")
        pabellon = fabricas.convocatoria("Pabellón infantil")

        for conv in (general, pabellon):
            solicitudes.enviar_solicitud(
                convocatoria=conv, persona=ana, editorial=ficha
            )

        assert Solicitud.objects.count() == 2
        assert RegistroConvocatoria.objects.count() == 2


# ── La fotografía (RN-22) ─────────────────────────────────────


def test_corregir_la_ficha_no_reescribe_lo_enviado(feria_2027):
    """`RN-22`: se dictamina lo que se envió, no lo que hay ahora."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        ficha = fabricas.editorial(ana)
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=ficha
        )

        ficha.nombre = "Otro nombre completamente distinto"
        ficha.save()

        solicitud.refresh_from_db()
        assert solicitud.datos_editorial["nombre"] == "Ediciones del Mayab"


def test_la_fotografia_incluye_los_sellos(feria_2027):
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        ficha = fabricas.editorial(ana)
        ficha.sellos.create(nombre="Fondo Azul")
        ficha.sellos.create(nombre="Fondo Verde")

        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=ficha
        )

        assert sorted(solicitud.sellos) == ["Fondo Azul", "Fondo Verde"]


# ── Reenviar y volver a aplicar ───────────────────────────────


def test_reenviar_reusa_la_misma_solicitud(feria_2027):
    """`CU-STD-002`: es la misma, no una nueva. Esa es la diferencia."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        ficha = fabricas.editorial(ana)
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=ficha
        )
        solicitud.estado = Solicitud.Estado.CAMBIOS_SOLICITADOS
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.motivo_peticion = "Falta la constancia fiscal."
        solicitud.save()

        ficha.nombre = "Ediciones del Mayab, S.A."
        ficha.save()
        vuelta = solicitudes.reenviar_solicitud(solicitud)

        assert Solicitud.objects.count() == 1
        assert vuelta.pk == solicitud.pk
        assert vuelta.estado == Solicitud.Estado.PENDIENTE
        # La fotografía se rehace: es lo corregido lo que se revisa ahora.
        assert vuelta.datos_editorial["nombre"] == "Ediciones del Mayab, S.A."
        # Y el dictamen anterior deja de aplicar.
        assert vuelta.fecha_revision is None
        assert vuelta.revisado_por is None


def test_solo_se_reenvia_una_con_cambios_pedidos(feria_2027):
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )

        with pytest.raises(solicitudes.EnvioRechazado):
            solicitudes.reenviar_solicitud(solicitud)


def test_tras_un_rechazo_se_vuelve_a_aplicar(feria_2027):
    """`RN-22`: la rechazada se conserva y la nueva nace con su fotografía."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        ficha = fabricas.editorial(ana)
        primera = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=ficha
        )
        primera.estado = Solicitud.Estado.RECHAZADA
        primera.fecha_revision = primera.fecha_envio
        primera.save()

        segunda = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=ficha
        )

        assert Solicitud.objects.count() == 2
        assert segunda.pk != primera.pk
        # Un solo registro: lo que se repite es el expediente, no la
        # inscripción.
        assert RegistroConvocatoria.objects.count() == 1


def test_volver_a_aplicar_reactiva_un_registro_retirado(feria_2027):
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        ficha = fabricas.editorial(ana)
        registro, _ = registros.obtener_o_crear_registro(
            convocatoria=conv, persona=ana, tipo_esperado=TipoConvocatoria.STD
        )
        registro.estado = RegistroConvocatoria.Estado.RETIRADO
        registro.save()

        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=ficha
        )

        assert solicitud.registro.estado == RegistroConvocatoria.Estado.ACTIVO


# ── Consultas de apoyo ────────────────────────────────────────


def test_solicitud_viva_ignora_las_rechazadas(feria_2027):
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.RECHAZADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()

        assert solicitudes.solicitud_viva(conv, ana) is None
        # Pero la pantalla sí tiene que poder decir por qué (`CU-STD-003` A2).
        assert solicitudes.ultima_solicitud(conv, ana).pk == solicitud.pk


def test_la_solicitud_de_una_feria_no_se_ve_desde_otra(feria_2027, feria_2028):
    """La feria es el schema, no una columna (`ADR-0003`)."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        solicitudes.enviar_solicitud(
            convocatoria=fabricas.convocatoria(),
            persona=ana,
            editorial=fabricas.editorial(ana),
        )

    with schema_context(feria_2028.schema_name):
        assert not Solicitud.objects.exists()
