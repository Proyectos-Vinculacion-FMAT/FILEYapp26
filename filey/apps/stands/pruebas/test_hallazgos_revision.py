"""
Los agujeros que salieron de la revisión de la fase 2.

Cinco de los siete hallazgos caen en `STD`, y comparten una forma: todos
viven en un camino que las pruebas de la fase no recorrían. Ninguno se
veía con la suite en verde, y ninguno era una regla mal escrita — eran
caminos sin escribir.

Los otros dos —el operador en "mis ferias" y el `href="None"` del
catálogo— viven en `FER` y se prueban con los suyos.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.convocatorias.servicios import registros
from apps.ferias.models import Feria

from ..formularios import SellosForm
from ..models import Documento, Solicitud
from ..servicios import archivos, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _url(feria, nombre, **kwargs):
    from django.conf import settings

    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


# ── Una edición archivada no se opera por ninguna puerta ──────


def _archivar(feria):
    feria.estado = Feria.Estado.ARCHIVADA
    feria.save(update_fields=["estado"])


def test_enviar_en_una_feria_archivada_no_revienta_la_pantalla(client, feria_2027):
    """Salía un 500: la excepción era de `FER` y la vista solo veía la de `STD`.

    `enviar_solicitud` delega en `obtener_o_crear_registro`, que levanta
    `RegistroRechazado` — que no hereda de `EnvioRechazado`. La vista
    capturaba solo la segunda, así que la primera cruzaba entera y salía
    por pantalla como un error del servidor.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    _archivar(feria_2027)
    client.force_login(ana)

    respuesta = client.post(
        _url(feria_2027, "stands:solicitud", convocatoria_id=conv.pk),
        fabricas.envio(),
        follow=True,
    )

    assert respuesta.status_code == 200
    avisos = [m.message for m in respuesta.context["messages"]]
    assert any("archivada" in a for a in avisos), avisos
    with schema_context(feria_2027.schema_name):
        assert not Solicitud.objects.exists()


def test_reenviar_en_una_feria_archivada_tampoco_pasa(feria_2027):
    """El reenvío entraba por la puerta de atrás.

    No crea registro, así que no pasaba por `obtener_o_crear_registro` —
    que era donde vivía la única comprobación de `CU-FER-006` E1. Con la
    feria archivada, un primer envío se rechazaba y un reenvío pasaba.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.CAMBIOS_SOLICITADOS
        solicitud.motivo_peticion = "Falta la constancia."
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()

        _archivar(feria_2027)

        with pytest.raises(solicitudes.EnvioRechazado, match="archivada"):
            solicitudes.reenviar_solicitud(solicitud)

        solicitud.refresh_from_db()
        assert solicitud.estado == Solicitud.Estado.CAMBIOS_SOLICITADOS


def test_la_guarda_de_la_edicion_es_una_sola(feria_2027):
    """`FER` la expone; `STD` la usa. Dos copias divergirían."""
    with schema_context(feria_2027.schema_name):
        _archivar(feria_2027)
        with pytest.raises(registros.RegistroRechazado, match="archivada"):
            registros.exigir_edicion_operable()


# ── Las filas de sellos, tras un error de validación ──────────


def test_las_filas_de_sellos_no_se_esconden_al_volver_con_errores():
    """El caso que las hacía desaparecer.

    Ligado, `visibles_al_cargar` contaba los sellos **guardados** — que
    en un primer envío son cero—, así que volvía 1. Los cinco que la
    persona acababa de escribir seguían enviándose, pero `x-show` los
    escondía: no se veían ni se podían borrar.
    """
    datos = {f"sello_{i}": nombre for i, nombre in enumerate(["A", "B", "C"])}
    form = SellosForm({**datos, "sello_0": "Alfa", "sello_1": "Beta",
                       "sello_2": "Gama"})

    # Los tres escritos más una en blanco.
    assert form.visibles_al_cargar == 4


def test_sin_ligar_se_cuentan_los_sellos_guardados():
    """El caso normal, que no cambia."""
    form = SellosForm(sellos_actuales=["Alfa", "Beta"])

    assert form.visibles_al_cargar == 3


def test_una_ficha_sin_sellos_arranca_con_una_fila():
    assert SellosForm().visibles_al_cargar == 1
    assert SellosForm({}).visibles_al_cargar == 1


# ── Los documentos que cuelgan de una solicitud ───────────────


def test_el_dueno_alcanza_un_documento_colgado_de_su_solicitud(rf, feria_2027):
    """`puede_ver` miraba solo la rama `editorial`.

    La restricción admite las dos, y en la de `solicitud` el dueño se
    quedaba fuera de lo que él mismo subió mientras quien administra sí
    lo veía. Hoy nada crea documentos así; la fase de pago sí.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        documento = Documento.objects.create(
            tipo=Documento.Tipo.COMPROBANTE_PAGO,
            archivo=SimpleUploadedFile("pago.pdf", b"%PDF-1.4"),
            nombre_original="pago.pdf",
            solicitud=solicitud,
        )

        peticion = rf.get("/")
        peticion.user = ana

        assert archivos.puede_ver(peticion, documento)


def test_un_extrano_no_alcanza_un_documento_de_otra_persona(rf, feria_2027):
    """La otra mitad: abrir la rama no puede abrir la puerta."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        otro = fabricas.persona(correo="otro@ejemplo.com", nombre="Otro")
        conv = fabricas.convocatoria()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        documento = Documento.objects.create(
            tipo=Documento.Tipo.COMPROBANTE_PAGO,
            archivo=SimpleUploadedFile("pago.pdf", b"%PDF-1.4"),
            nombre_original="pago.pdf",
            solicitud=solicitud,
        )

        peticion = rf.get("/")
        peticion.user = otro

        assert not archivos.puede_ver(peticion, documento)
