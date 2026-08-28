"""
Las tres pantallas de `STD` (U1, A1, A2).

Son las primeras vistas de participante que viven **dentro** de una
feria, y eso trae dos cosas que ninguna pantalla anterior había ejercido:

1. **El acceso está en el urlconf de fuera.** Un `reverse("registros:acceso")`
   normal revienta aquí dentro. Es lo que obligó a que
   `requiere_participante` resuelva su destino con `url_publica`.
2. **El catálogo sirve la raíz de la feria**, así que las rutas de un
   módulo tienen que resolverse antes que él.

Lo demás que se vigila es lo de siempre en este proyecto: que administrar
la feria A no conceda nada en la B, y que lo que no corresponde a alguien
no llegue a la respuesta en vez de ocultarse en la plantilla.
"""

import re
from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Documento, Editorial, SelloEditorial, Solicitud
from ..servicios import dictamen, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


@pytest.fixture
def escenario(feria_2027):
    """Una convocatoria de stands abierta con una solicitud pendiente."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv,
            persona=ana,
            editorial=fabricas.editorial(ana),
        )
    return feria_2027, conv, ana, solicitud


def _admin_de(feria, correo="rita@filey.org"):
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


def _url(feria, nombre, **kwargs):
    """La URL de una vista de stands, con el prefijo de su feria.

    Se resuelve contra ``ROOT_URLCONF`` **a secas** —el módulo, sin el
    envoltorio que `django-tenants` le pone— y se le antepone
    ``feria.url``. Hacerlo con un `reverse` normal dentro de
    ``schema_context`` es una trampa: ahí la conexión lleva un
    ``FakeTenant`` sin ``domain_subfolder``, y el resultado depende de si
    otra prueba ya calentó la caché del resolver.
    """
    return f"{feria.url.rstrip('/')}" + reverse(
        f"stands:{nombre}", kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


# ── U1 · el aplicante ─────────────────────────────────────────


def test_sin_sesion_manda_al_acceso_global(client, escenario):
    """El bug que esta pantalla destapó.

    `requiere_participante` redirigía con `reverse("registros:acceso")`,
    que **no resuelve dentro de una feria**: ese nombre vive en el
    urlconf público. Hasta ahora no se había notado porque ninguna vista
    de participante vivía dentro de una feria.

    El destino no lleva prefijo de edición, y es lo correcto: la cuenta
    es única en todo el sistema.
    """
    feria, conv, _, _ = escenario

    respuesta = client.get(_url(feria, "solicitud", convocatoria_id=conv.pk))

    assert respuesta.status_code == 302
    assert respuesta.url == "/acceso/"
    assert feria.url not in respuesta.url


def test_el_aplicante_ve_el_estado_de_su_solicitud(client, escenario):
    """`CU-STD-003`: entrar teniendo una solicitud enseña en qué va."""
    feria, conv, ana, _ = escenario
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "solicitud", convocatoria_id=conv.pk)).content.decode()

    assert "en revisión" in cuerpo


def test_con_una_pendiente_no_se_puede_reeditar(client, escenario):
    """Se muestra la fotografía, no el formulario."""
    feria, conv, ana, _ = escenario
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "solicitud", convocatoria_id=conv.pk)).content.decode()

    assert "Enviar solicitud" not in cuerpo
    assert "Ediciones del Mayab" in cuerpo


def test_con_cambios_pedidos_se_ofrece_el_formulario_y_el_motivo(client, escenario):
    """`CU-STD-002`: se corrige y se reenvía, con el motivo a la vista."""
    feria, conv, ana, solicitud = escenario
    with schema_context(feria.schema_name):
        dictamen.solicitar_cambios(
            solicitud, revisor=_admin_de(feria), motivo="Falta la constancia fiscal."
        )
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "solicitud", convocatoria_id=conv.pk)).content.decode()

    assert "Falta la constancia fiscal." in cuerpo
    assert "Reenviar solicitud" in cuerpo


def test_una_convocatoria_de_otro_tipo_no_existe_para_stands(client, escenario):
    """404 y no 403: no es un permiso que falte, es que no es de stands."""
    feria, _, ana, _ = escenario
    with schema_context(feria.schema_name):
        eventos = Convocatoria.objects.create(
            tipo=TipoConvocatoria.EVT,
            nombre="Eventos 2027",
            estado=Convocatoria.Estado.ABIERTA,
        )
    client.force_login(ana)

    respuesta = client.get(_url(feria, "solicitud", convocatoria_id=eventos.pk))

    assert respuesta.status_code == 404


def test_una_convocatoria_cerrada_se_consulta_pero_no_recibe(client, escenario):
    feria, conv, ana, solicitud = escenario
    with schema_context(feria.schema_name):
        solicitud.estado = Solicitud.Estado.RECHAZADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
        conv.estado = Convocatoria.Estado.CERRADA
        conv.save()
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "solicitud", convocatoria_id=conv.pk)).content.decode()

    assert "convocatoria está cerrada" in cuerpo
    # Lo que de verdad importa: no hay forma de enviar nada.
    assert "Enviar solicitud" not in cuerpo
    assert "Reenviar solicitud" not in cuerpo


def test_enviar_la_solicitud_desde_el_formulario(client, feria_2027):
    """`CU-STD-001` de punta a punta: formulario, archivos y expediente.

    Es el camino que de verdad recorre una editorial, y el que ejerce
    todo lo que la fase montó de una vez: el registro en la convocatoria
    (`FER`), la ficha, los sellos, los documentos en disco (`ADR-0007`) y
    la fotografía.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    respuesta = client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(sello_0="Fondo Azul", sello_1=""),
        follow=True,
    )

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        solicitud = Solicitud.objects.get()
        assert solicitud.estado == Solicitud.Estado.PENDIENTE
        assert solicitud.datos_editorial["nombre"] == "Ediciones del Mayab"
        assert solicitud.sellos == ["Fondo Azul"]
        assert solicitud.editorial.total_sellos == 1
        # Los documentos cuelgan de la editorial, no de la solicitud: es
        # lo que permite reenviar sin volver a subirlos (`CU-STD-002` A1).
        tipos = set(solicitud.editorial.documentos.values_list("tipo", flat=True))
        assert tipos == {"constancia_fiscal", "lista_titulos"}


def test_los_archivos_caen_bajo_el_schema_de_su_feria(client, feria_2027):
    """`ADR-0007`: el aislamiento por feria llega también al disco."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(
            constancia_fiscal=SimpleUploadedFile("RFC_ANA_PECH.pdf", b"%PDF")
        ),
    )

    with schema_context(feria_2027.schema_name):
        doc = Documento.objects.get(tipo="constancia_fiscal")

    assert doc.archivo.name.startswith("feria_2027/documentos/")
    # El nombre original no sobrevive en la ruta: trae datos personales.
    assert "ANA_PECH" not in doc.archivo.name
    # Pero sí se conserva aparte, para poder decirle cuál subió.
    assert doc.nombre_original == "RFC_ANA_PECH.pdf"


def test_faltar_un_documento_no_crea_nada(client, feria_2027):
    """E1: se señala lo que falta y no se envía la solicitud."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    respuesta = client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(con_documentos=False),
    )

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        assert not Solicitud.objects.exists()
        # Tampoco a medias: sin solicitud no queda ficha ni registro.
        assert not Editorial.objects.exists()


def test_un_envio_rechazado_no_deja_ficha_a_medias(client, feria_2027):
    """La convocatoria puede cerrarse entre el GET y el POST.

    Sin transacción, ese caso guardaría la ficha y los documentos y
    ninguna solicitud: un expediente que existe a medias y que nadie va a
    revisar, porque no está en ninguna cola.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    with patch(
        "apps.stands.views.solicitudes.enviar_solicitud",
        side_effect=solicitudes.EnvioRechazado("se cerró mientras llenabas"),
    ):
        respuesta = client.post(
            _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
            fabricas.envio(),
        )

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        assert not Solicitud.objects.exists()
        assert not Editorial.objects.exists()
        assert not Documento.objects.exists()


# ── Lo que la ficha oficial exige ─────────────────────────────


def test_sin_aceptar_las_bases_no_se_envia(client, feria_2027):
    """La ficha en papel no vale sin firma; ésta tampoco sin la casilla.

    Es la traducción de «RECONOZCO Y ACEPTO LAS BASES DE PARTICIPACIÓN»
    (Ficha de Registro, p. 2), y se comprueba en el servidor: quitar el
    `required` del navegador no debe bastar.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    datos = fabricas.envio()
    del datos["acepto"]
    client.post(_url(feria_2027, "solicitud", convocatoria_id=conv.pk), datos)

    with schema_context(feria_2027.schema_name):
        assert not Solicitud.objects.exists()


def test_al_enviar_queda_registrado_que_acepto(client, feria_2027):
    """Va en la solicitud, no en la ficha: se aceptan las bases **de esta**
    convocatoria, en el momento de enviar."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    client.post(_url(feria_2027, "solicitud", convocatoria_id=conv.pk), fabricas.envio())

    with schema_context(feria_2027.schema_name):
        assert Solicitud.objects.get().bases_aceptadas is True


def test_marcar_otro_sin_decir_cual_no_se_admite(client, feria_2027):
    """La ficha pide «Otro (especificar)»; sin el texto no dice nada."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(materiales=["Libro", "Otro"]),
    )

    with schema_context(feria_2027.schema_name):
        assert not Solicitud.objects.exists()


def test_las_tematicas_son_las_de_la_ficha():
    """La lista completa del papel, no las nueve que había antes.

    La cuenta sale de la Ficha de Registro p. 2: 21 de la primera
    columna, 22 de la segunda y 17 de la tercera —19 impresas, menos
    «Pintura» que aparece repetida y menos «Otros», que va aparte— dan 60
    temáticas, más «Otros» como escape: 61 entradas.
    """
    from ..models import TEMATICAS

    assert len(TEMATICAS) == 61
    assert TEMATICAS[-1] == "Otros"
    # Sin repetir: la ficha impresa trae «Pintura» dos veces.
    assert len(set(TEMATICAS)) == len(TEMATICAS)
    # Y con las dos erratas del formato corregidas.
    assert "Braille" in TEMATICAS and "Braile" not in TEMATICAS
    assert "Software" in TEMATICAS and "Sofware" not in TEMATICAS


def test_los_materiales_son_los_de_la_ficha():
    from ..models import MATERIALES

    assert MATERIALES == [
        "Libro",
        "Audiolibro",
        "Revista",
        "Material didáctico",
        "Libros electrónicos",
        "Otro",
    ]


# ── El país ───────────────────────────────────────────────────


def test_el_pais_se_guarda_como_codigo_no_como_nombre(client, feria_2027):
    """Igual que `Persona.pais`, y por el mismo motivo.

    Con un campo de texto libre acababan «Mexico», «MEX» y «méxico» en la
    misma columna, y agrupar por país exigía normalizar cadenas a mano.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(pais="CO"),
    )

    with schema_context(feria_2027.schema_name):
        assert Editorial.objects.get().pais == "CO"


def test_la_fotografia_guarda_el_nombre_del_pais(client, feria_2027):
    """La fotografía se lee —en A2 y en el correo— y «CO» no se lee."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(pais="CO"),
    )

    with schema_context(feria_2027.schema_name):
        assert Solicitud.objects.get().datos_editorial["pais"] == "Colombia"


def test_el_desplegable_propone_el_pais_de_la_cuenta(client, feria_2027):
    """Y lo pone arriba, para no recorrer 197 entradas."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        ana.pais = "CO"
        ana.save()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk)
    ).content.decode()

    seccion = cuerpo[cuerpo.index('name="pais"') :]
    seccion = seccion[: seccion.index("</select>")]
    codigos = re.findall(r'value="([A-Z]{2})"', seccion)

    assert codigos[:2] == ["CO", "MX"], "el suyo primero, México segundo"
    assert 'value="CO" selected' in seccion


def test_sin_pais_en_la_cuenta_propone_mexico(client, feria_2027):
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'value="MX" selected' in cuerpo


def test_el_catalogo_de_paises_no_se_duplica_ni_se_encoge():
    """`opciones()` reordena; no añade ni quita."""
    from apps.registros.paises import PAISES, opciones

    for preferido in (None, "MX", "CO", "ZZ"):
        lista = opciones(preferido)
        assert len(lista) == len(PAISES)
        assert len({c for c, _ in lista}) == len(PAISES)


# ── Los sellos y sus cartas (RN-17) ───────────────────────────


def test_cada_sello_guarda_su_propia_carta(client, feria_2027):
    """`RN-17`: la carta autoriza a representar **a ese** sello.

    En dos listas paralelas —sellos por un lado, cartas por otro— nadie
    podría decir qué carta corresponde a cuál.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(
            sello_0="Fondo Azul",
            carta_0=SimpleUploadedFile("azul.pdf", b"%PDF azul"),
            sello_1="Fondo Verde",
            carta_1=SimpleUploadedFile("verde.pdf", b"%PDF verde"),
        ),
    )

    with schema_context(feria_2027.schema_name):
        azul = SelloEditorial.objects.get(nombre="Fondo Azul")
        verde = SelloEditorial.objects.get(nombre="Fondo Verde")

    assert azul.carta.nombre_original == "azul.pdf"
    assert verde.carta.nombre_original == "verde.pdf"


def test_un_sello_sin_carta_se_admite(client, feria_2027):
    """La carta solo hace falta si se representa a otra casa editora."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(sello_0="Fondo Propio"),
    )

    with schema_context(feria_2027.schema_name):
        sello = SelloEditorial.objects.get()

    assert sello.carta is None


def test_una_carta_sin_sello_se_descarta(client, feria_2027):
    """Un archivo sin sello al que pertenecer no autoriza nada."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(sello_0="", carta_0=SimpleUploadedFile("huerfana.pdf", b"%PDF")),
    )

    with schema_context(feria_2027.schema_name):
        assert not SelloEditorial.objects.exists()
        assert not Documento.objects.filter(tipo="carta_representacion").exists()


def test_reenviar_conserva_la_carta_que_ya_estaba(client, escenario):
    """`CU-STD-002` A1, y la razón de reconciliar por nombre.

    Borrar los sellos y recrearlos —que es lo que hacía— se llevaría por
    delante la carta en cada reenvío, aunque el sello no hubiera cambiado.
    """
    feria, conv, ana, solicitud = escenario
    with schema_context(feria.schema_name):
        ficha = ana.editorial
        sello = ficha.sellos.create(nombre="Fondo Azul")
        Documento.objects.create(
            tipo=Documento.Tipo.CARTA_REPRESENTACION,
            archivo=SimpleUploadedFile("azul.pdf", b"%PDF"),
            nombre_original="azul.pdf",
            editorial=ficha,
            sello=sello,
        )
        dictamen.solicitar_cambios(
            solicitud, revisor=_admin_de(feria), motivo="Corrige el teléfono."
        )
    client.force_login(ana)

    client.post(
        _url(feria, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(
            con_documentos=False, sello_0="Fondo Azul", telefono_celular="9990000000"
        ),
    )

    with schema_context(feria.schema_name):
        sello.refresh_from_db()
        assert sello.carta is not None
        assert sello.carta.nombre_original == "azul.pdf"


def test_quitar_un_sello_se_lleva_su_carta(client, escenario):
    """Una carta que autoriza a un sello que ya no está no autoriza nada."""
    feria, conv, ana, solicitud = escenario
    with schema_context(feria.schema_name):
        ficha = ana.editorial
        sello = ficha.sellos.create(nombre="Fondo Azul")
        Documento.objects.create(
            tipo=Documento.Tipo.CARTA_REPRESENTACION,
            archivo=SimpleUploadedFile("azul.pdf", b"%PDF"),
            nombre_original="azul.pdf",
            editorial=ficha,
            sello=sello,
        )
        dictamen.solicitar_cambios(
            solicitud, revisor=_admin_de(feria), motivo="Quita el sello."
        )
    client.force_login(ana)

    client.post(
        _url(feria, "solicitud", convocatoria_id=conv.pk),
        fabricas.envio(con_documentos=False),
    )

    with schema_context(feria.schema_name):
        assert not SelloEditorial.objects.exists()
        assert not Documento.objects.filter(tipo="carta_representacion").exists()


def test_no_caben_mas_de_diez_sellos(client, feria_2027):
    """El tope es del formulario: la fila once no existe, así que se ignora."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    extras = {f"sello_{i}": f"Fondo {i}" for i in range(12)}
    client.post(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk), fabricas.envio(**extras)
    )

    with schema_context(feria_2027.schema_name):
        assert SelloEditorial.objects.count() == 10


def test_la_pantalla_pinta_las_diez_filas(client, feria_2027):
    """Regla 6: sin JavaScript no hay forma de añadir una.

    El servidor manda las diez y Alpine enseña las que hacen falta. Sin
    Alpine se ven las diez y el formulario funciona igual.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk)
    ).content.decode()

    assert cuerpo.count('name="sello_') == 10
    assert cuerpo.count('name="carta_') == 10
    # Y los dos controles que Alpine acciona.
    assert "Añadir otro sello" in cuerpo
    assert "fileyQuitarFila" in cuerpo


def test_las_filas_no_dependen_de_que_filey_js_llegue(client, feria_2027):
    """El estado va en un objeto literal, no en un `Alpine.data`.

    Con un componente con nombre, un `filey.js` que no cargue —cacheado,
    o caído— deja `visibles` en `undefined`, todos los `x-show` en falso
    y **la sección entera invisible**. Peor que no tener JavaScript, que
    es el caso que la regla 6 sí contempla.
    """
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria_2027, "solicitud", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'x-data="{ visibles: 1, maximo: 10 }"' in cuerpo


# ── A1 y A2 · el administrador ────────────────────────────────


def test_la_cola_de_revision_pide_administrar_esta_feria(client, escenario, feria_2028):
    """Administrar otra feria no da acceso a ésta (`ADR-0004`)."""
    feria, conv, _, _ = escenario
    client.force_login(_admin_de(feria_2028, correo="beto@filey.org"))

    respuesta = client.get(_url(feria, "solicitudes", convocatoria_id=conv.pk))

    assert respuesta.status_code == 403


def test_el_aplicante_no_entra_a_la_cola(client, escenario):
    feria, conv, ana, _ = escenario
    client.force_login(ana)

    respuesta = client.get(_url(feria, "solicitudes", convocatoria_id=conv.pk))

    assert respuesta.status_code == 403


def test_la_cola_lista_las_solicitudes(client, escenario):
    feria, conv, _, _ = escenario
    client.force_login(_admin_de(feria))

    cuerpo = client.get(_url(feria, "solicitudes", convocatoria_id=conv.pk)).content.decode()

    assert "Ediciones del Mayab" in cuerpo


def test_el_filtro_de_estado_va_en_la_consulta(client, escenario):
    """Lo que no se pide no llega a la respuesta."""
    feria, conv, _, _ = escenario
    client.force_login(_admin_de(feria))

    url = _url(feria, "solicitudes", convocatoria_id=conv.pk)
    cuerpo = client.get(url, {"estado": "aceptada"}).content.decode()

    assert "Ediciones del Mayab" not in cuerpo
    assert "Ninguna solicitud cumple estos filtros" in cuerpo


def test_el_operador_de_la_plataforma_alcanza_la_cola(client, escenario):
    """`ADR-0005`: sin fila en `AdminFeria`."""
    feria, conv, _, _ = escenario
    client.force_login(
        Persona.objects.create_superuser(correo="raiz@filey.org", password="x")
    )

    respuesta = client.get(_url(feria, "solicitudes", convocatoria_id=conv.pk))

    assert respuesta.status_code == 200


def test_aceptar_desde_el_detalle(client, escenario):
    """`CU-STD-006`: el camino entero, del botón al correo."""
    from django.core import mail

    feria, _, _, solicitud = escenario
    client.force_login(_admin_de(feria))
    mail.outbox.clear()

    respuesta = client.post(
        _url(feria, "detalle_solicitud", solicitud_id=solicitud.pk),
        {"accion": "aceptar", "motivo": ""},
        follow=True,
    )

    assert respuesta.status_code == 200
    with schema_context(feria.schema_name):
        solicitud.refresh_from_db()
    assert solicitud.estado == Solicitud.Estado.ACEPTADA
    assert len(mail.outbox) == 1


def test_pedir_cambios_sin_motivo_no_resuelve_nada(client, escenario):
    """`CU-STD-007` E1, comprobado en el servidor y no solo en el navegador."""
    feria, _, _, solicitud = escenario
    client.force_login(_admin_de(feria))

    client.post(
        _url(feria, "detalle_solicitud", solicitud_id=solicitud.pk),
        {"accion": "cambios", "motivo": "  "},
    )

    with schema_context(feria.schema_name):
        solicitud.refresh_from_db()
    assert solicitud.estado == Solicitud.Estado.PENDIENTE


def test_el_detalle_ensena_la_fotografia_y_no_la_ficha_viva(client, escenario):
    """`RN-22`: se dictamina lo que se envió."""
    feria, _, ana, solicitud = escenario
    with schema_context(feria.schema_name):
        ficha = ana.editorial
        ficha.nombre = "Nombre cambiado despues"
        ficha.save()
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "detalle_solicitud", solicitud_id=solicitud.pk)
    ).content.decode()

    assert "Ediciones del Mayab" in cuerpo
    assert "Nombre cambiado despues" not in cuerpo
