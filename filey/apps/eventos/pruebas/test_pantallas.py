"""
La pantalla de captura y el acuse (`CU-EVT-002`, U1).

Lo que se vigila aquí es lo que ni el modelo ni el servicio pueden:

1. **El módulo está inscrito** (`ADR-0006`). Olvidarlo no da error: la
   tarjeta del catálogo diría "próximamente" para siempre.
2. **Los datos de la cuenta no viajan en el POST.** Se enseñan, pero
   quien manda es `request.user`; si viajaran, un POST a mano cambiaría
   de quién es la propuesta.
3. **Elegir el tipo no borra lo escrito**, ni con JavaScript ni sin él.
4. **`E2`: un envío incompleto vuelve al formulario con lo capturado**,
   que es lo que el CU pide con esas palabras.
5. **`E1`: con la convocatoria cerrada no se envía**, aunque alguien
   llegue por URL.
6. **El acuse es de quien la envió** y de nadie más.
"""

import pytest
from django.conf import settings
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.modulos import modulo_de

from ..models import Solicitud
from ..servicios import solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db

CHARLA = {
    "tipo": "charla",
    "nombre_participante_1": "Elena Poniatowska",
    "semblanza_participante_1": "Escritora y periodista.",
}
COMUNES = {
    "institucion": "Editorial La Nave",
    "cargo": "Coordinadora editorial",
    "titulo_actividad": "El mar que nos habita",
    "nombre_organizador_organizacion": "Editorial La Nave",
    "nombre_moderador": "",
    "publico_objetivo": ["publico_general"],
    "sinopsis": "Una conversación sobre la memoria del puerto.",
    "requiere_constancia": "on",
    "comentarios": "",
    "bases_aceptadas": "on",
}


# ── El enganche con FER ───────────────────────────────────────


def test_eventos_se_inscribe_en_el_registro_de_modulos():
    """La prueba que `ADR-0006` exige a cada módulo, y por qué.

    Olvidar el `ready()` no revienta nada: el catálogo simplemente
    pintaría la convocatoria de eventos como "próximamente", para
    siempre y sin que nadie se entere.
    """
    modulo = modulo_de(TipoConvocatoria.EVT)
    assert modulo is not None
    # La puerta es el seguimiento y no el formulario: el catálogo dice
    # "Continuar" a quien ya tiene registro, y eso llevaba a un
    # formulario en blanco a quien ya había mandado tres propuestas.
    assert modulo.url_aplicar == "eventos:mis_propuestas"
    # El callback de configuración es lo que hace que una convocatoria
    # nazca con su prefijo de folio (`CU-FER-005` paso 6).
    assert modulo.crear_configuracion is not None


# ── Ayudas ────────────────────────────────────────────────────


def _url(feria, nombre, **kwargs):
    """La dirección completa, con el prefijo de la feria.

    `reverse` a secas devuelve la ruta sin `/f/<slug>/`: el prefijo lo
    antepone `django-tenants` al resolver, no al construir.
    """
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def escenario(feria, *, estado=Convocatoria.Estado.ABIERTA):
    """Convocatoria, persona y la URL de su formulario."""
    with schema_context(feria.schema_name):
        convocatoria = fabricas.convocatoria(estado=estado)
    persona = fabricas.persona()
    url = _url(feria, "eventos:propuesta", convocatoria_id=convocatoria.pk)
    return convocatoria, persona, url


# ── La pantalla ───────────────────────────────────────────────


def test_la_pantalla_precarga_la_cuenta_y_no_la_pide(client, feria_2027):
    """Paso 2 del CU: nombre, correo y teléfono salen del perfil.

    Y salen como campos de solo lectura sin `name`, así que no viajan en
    el POST: quien decide de quién es la propuesta es `request.user`.
    """
    convocatoria, persona, url = escenario(feria_2027)
    persona.telefono = "9994567890"
    persona.save()
    client.force_login(persona)

    respuesta = client.get(url)
    contenido = respuesta.content.decode()

    assert respuesta.status_code == 200
    assert persona.nombre_completo in contenido
    assert persona.correo in contenido
    assert "9994567890" in contenido
    # Ninguno de los tres se captura.
    for campo in ("nombre_completo", "correo", "telefono"):
        assert f'name="{campo}"' not in contenido


def test_sin_tipo_elegido_no_hay_seccion_tres(client, feria_2027):
    """No se pintan los ocho juegos de campos: no se pinta la sección.

    Es el comportamiento del prototipo, y la razón es la misma: enseñar
    cuarenta campos de los que treinta y cinco sobran es exactamente lo
    que las leyes de Hick y Miller desaconsejan.

    El ancla sí queda, vacía y oculta: es el destino del swap de htmx, y
    sin ella el primer clic no tendría dónde escribir.
    """
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    contenido = client.get(url).content.decode()
    assert '<div id="campos-tipo" hidden></div>' in contenido
    assert "Detalles de la actividad" not in contenido
    assert "nombre_participante_1" not in contenido


def test_el_tipo_elegido_se_ve_y_se_nombra_bien(client, feria_2027):
    """El rótulo sale del catálogo, no de la columna.

    Componerlo del valor guardado daba «Presentacion_Libro»: sin acento,
    con guion bajo y en mayúsculas donde no van.
    """
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    contenido = client.get(url, {"tipo": "presentacion_libro"}).content.decode()
    assert "Detalles de la actividad — Presentación de libro" in contenido
    # Y el botón de ese tipo queda marcado, uno y solo uno.
    assert contenido.count("tipo-opt is-active") == 1


def test_elegir_el_tipo_trae_sus_campos_y_conserva_lo_escrito(client, feria_2027):
    """Sin JavaScript, elegir el tipo es un GET que arrastra el formulario.

    Si no conservara lo escrito, quien ya llenó la institución la
    perdería al elegir el tipo — y volvería a perderla al cambiarlo.
    """
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    contenido = client.get(
        url, {"tipo": "charla", "institucion": "Editorial La Nave"}
    ).content.decode()

    assert "nombre_participante_1" in contenido
    assert "Editorial La Nave" in contenido
    # Y no se marca en rojo lo que todavía se está llenando.
    assert "Escribe el título de la actividad." not in contenido


def test_con_htmx_solo_vuelve_la_seccion_del_tipo(client, feria_2027):
    """El fragmento y la página comparten markup (§4 del skill).

    Lo que llega es la sección 3 y nada más: ni chasis ni el resto del
    formulario, que es lo que evita perder lo escrito sin recargar.
    """
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    respuesta = client.get(url, {"tipo": "charla"}, HTTP_HX_REQUEST="true")
    contenido = respuesta.content.decode()

    assert "nombre_participante_1" in contenido
    assert "<form" not in contenido
    assert "Datos de participación" not in contenido


def test_una_convocatoria_de_stands_no_existe_para_eventos(client, feria_2027):
    """404 y no 403: decir "no tienes permiso" insinuaría que con otro sí."""
    with schema_context(feria_2027.schema_name):
        ajena = fabricas.convocatoria(nombre="Stands", tipo=TipoConvocatoria.STD)
    persona = fabricas.persona()
    client.force_login(persona)

    url = _url(feria_2027, "eventos:propuesta", convocatoria_id=ajena.pk)
    assert client.get(url).status_code == 404


def test_sin_sesion_no_se_llega_al_formulario(client, feria_2027):
    """El acceso lo pone el decorador, no la carpeta de la plantilla."""
    convocatoria, persona, url = escenario(feria_2027)
    respuesta = client.get(url)
    assert respuesta.status_code in (302, 403)


# ── El envío ──────────────────────────────────────────────────


def test_el_envio_completo_crea_la_propuesta_y_lleva_al_acuse(client, feria_2027):
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    respuesta = client.post(url, {**COMUNES, **CHARLA})

    with schema_context(feria_2027.schema_name):
        propuesta = Solicitud.objects.get()
        assert propuesta.titulo_actividad == "El mar que nos habita"
        assert propuesta.actividad.tipo.nombre == "charla"
        assert propuesta.registro.persona == persona
        assert propuesta.bases_aceptadas is True
        esperado = _url(feria_2027, "eventos:confirmacion", solicitud_id=propuesta.pk)

    assert respuesta.status_code == 302
    assert respuesta.url.endswith(esperado)


def test_un_envio_incompleto_vuelve_con_lo_capturado(client, feria_2027):
    """`E2`: «devuelve al aplicante al formulario conservando los datos».

    Si se perdiera, quien falló un campo de treinta tendría que
    escribirlos todos otra vez — y ése es el momento en que la gente
    abandona.
    """
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    respuesta = client.post(
        url, {**COMUNES, **CHARLA, "titulo_actividad": ""}
    )
    contenido = respuesta.content.decode()

    assert respuesta.status_code == 200
    assert "Escribe el título de la actividad." in contenido
    # Lo demás sigue ahí, incluido el tipo y sus campos.
    assert "Editorial La Nave" in contenido
    assert "Elena Poniatowska" in contenido
    with schema_context(feria_2027.schema_name):
        assert Solicitud.objects.count() == 0


def test_el_fragmento_de_htmx_se_lleva_el_tipo_consigo(client, feria_2027):
    """El defecto que ninguna prueba de servidor podía ver.

    El campo oculto con el tipo vivía en la página, fuera de lo que htmx
    reemplaza. Al elegir un tipo sin recargar, ese campo se quedaba con el
    valor que tenía al cargar —vacío—, y al enviar el servidor creía que
    nadie había elegido nada: la sección 3 desaparecía y con ella todo lo
    capturado, adjuntos incluidos.

    Ahora el tipo viaja **dentro** del fragmento, que es lo único que
    puede decir la verdad después de un swap.
    """
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    fragmento = client.get(
        url, {"tipo": "charla"}, HTTP_HX_REQUEST="true"
    ).content.decode()

    assert 'name="tipo" value="charla"' in fragmento
    # Y la página sin tipo no lo lleva: enviar desde ahí es «no elegí».
    assert 'name="tipo" value=' not in client.get(url).content.decode()


def test_un_envio_incompleto_conserva_el_tipo_y_sus_campos(client, feria_2027):
    """Lo que se capturó del tipo sigue ahí, y el tipo sigue elegido.

    Es `E2` del CU llevado hasta el final: no basta con conservar los
    campos comunes si la sección que los contiene desaparece.
    """
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    contenido = client.post(
        url, {**COMUNES, **CHARLA, "titulo_actividad": ""}
    ).content.decode()

    assert "Detalles de la actividad" in contenido
    assert 'name="tipo" value="charla"' in contenido
    assert "Elena Poniatowska" in contenido
    assert "Escritora y periodista." in contenido
    assert contenido.count("tipo-opt is-active") == 1


def test_un_envio_rechazado_ya_no_pide_volver_a_adjuntar(client, feria_2027):
    """Esta prueba custodiaba la deuda; ahora custodia que esté saldada.

    Hasta el 2026-09-03 afirmaba lo contrario: que la pantalla avisara de
    que **había** que volver a adjuntar los archivos. Era lo honesto
    entonces —ningún navegador deja repoblar un `<input type="file">`— y
    dejó de serlo en cuanto el servidor empezó a guardarlos
    (`servicios/en_espera.py`).

    Se conserva el caso en vez de borrarlo porque la frase vieja es
    justamente lo que no puede volver: si alguien la reintroduce, algo se
    rompió en la cola y este renglón lo dice antes que nadie.

    Lo que se conserva de verdad y cómo se ve lo cubre
    `test_en_espera.py`; aquí solo vive el epitafio del aviso.
    """
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    libro = {
        "tipo": "presentacion_libro",
        "titulo_publicacion": "El mar que nos habita",
        "tipo_presentador": "autor",
        "nombre_editorial": "La Nave",
        "nombre_autor_1": "Elena Poniatowska",
        "semblanza_autor_1": "Escritora.",
    }
    contenido = client.post(
        url, {**COMUNES, **libro, "titulo_actividad": ""}
    ).content.decode()

    assert "volver a adjuntarlos" not in contenido


def test_sin_elegir_tipo_no_se_envia(client, feria_2027):
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    respuesta = client.post(url, COMUNES)

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        assert Solicitud.objects.count() == 0


def test_con_la_convocatoria_cerrada_no_se_envia(client, feria_2027):
    """`E1`, también por URL directa: la pantalla avisa y el POST no pasa."""
    convocatoria, persona, url = escenario(
        feria_2027, estado=Convocatoria.Estado.CERRADA
    )
    client.force_login(persona)

    contenido = client.get(url).content.decode()
    assert "no está recibiendo propuestas" in contenido

    respuesta = client.post(url, {**COMUNES, **CHARLA})
    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        assert Solicitud.objects.count() == 0


# ── El acuse ──────────────────────────────────────────────────


def test_el_acuse_enseña_el_folio(client, feria_2027):
    """Paso 13 del CU: el folio es con lo que se identifica la solicitud."""
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)
    client.post(url, {**COMUNES, **CHARLA})

    with schema_context(feria_2027.schema_name):
        propuesta = Solicitud.objects.get()
        folio = propuesta.folio
        acuse = _url(feria_2027, "eventos:confirmacion", solicitud_id=propuesta.pk)

    contenido = client.get(acuse).content.decode()
    assert folio in contenido
    # El estado, en las palabras del acuse nuevo. Antes decía «pendiente
    # de revisión» de corrido; ahora el estado va suelto y la cola se
    # nombra en la frase siguiente.
    assert "pendiente" in contenido
    assert "cola de revisión" in contenido


def test_el_acuse_de_otra_persona_no_se_ve(client, feria_2027):
    """El folio y el título de una propuesta ajena no son de nadie más."""
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)
    client.post(url, {**COMUNES, **CHARLA})

    with schema_context(feria_2027.schema_name):
        propuesta = Solicitud.objects.get()
        acuse = _url(feria_2027, "eventos:confirmacion", solicitud_id=propuesta.pk)

    intrusa = fabricas.persona(correo="otra@ejemplo.com", nombre="Otra")
    client.force_login(intrusa)
    assert client.get(acuse).status_code == 404


def test_el_acuse_no_repite_el_listado(client, feria_2027):
    """El acuse hace una sola cosa: dar el folio y decir qué sigue.

    Enseñó la lista de lo ya enviado hasta el 2026-09-03, cuando
    `CU-EVT-003` no existía. Con el seguimiento construido esa tabla era
    la misma lista dos veces —aquí sin poder abrir nada— y encima **sin
    la propuesta recién enviada**, que era la única que importaba en ese
    momento.
    """
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)

    client.post(url, {**COMUNES, **CHARLA, "titulo_actividad": "La primera"})
    client.post(url, {**COMUNES, **CHARLA, "titulo_actividad": "La segunda"})

    with schema_context(feria_2027.schema_name):
        ultima = Solicitud.objects.order_by("-pk").first()
        acuse = _url(feria_2027, "eventos:confirmacion", solicitud_id=ultima.pk)

    contenido = client.get(acuse).content.decode()
    assert "Tus otras propuestas" not in contenido
    assert "La primera" not in contenido


def test_el_acuse_manda_al_listado_senalando_la_nueva(client, feria_2027):
    """`?nueva=` es lo único que le dice a la lista cuál resaltar.

    Va en la barra de direcciones y no en la sesión: así el resalte se
    pierde al recargar, que es lo que tiene que pasar —una propuesta solo
    es nueva la primera vez que se mira—.
    """
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)
    client.post(url, {**COMUNES, **CHARLA})

    with schema_context(feria_2027.schema_name):
        enviada = Solicitud.objects.get()
        acuse = _url(feria_2027, "eventos:confirmacion", solicitud_id=enviada.pk)
        esperado = f"?nueva={enviada.pk}"

    assert esperado in client.get(acuse).content.decode()


def test_el_acuse_ofrece_enviar_otra(client, feria_2027):
    """Paso 14: en `EVT` se proponen varias actividades."""
    convocatoria, persona, url = escenario(feria_2027)
    client.force_login(persona)
    client.post(url, {**COMUNES, **CHARLA})

    with schema_context(feria_2027.schema_name):
        propuesta = Solicitud.objects.get()
        acuse = _url(feria_2027, "eventos:confirmacion", solicitud_id=propuesta.pk)

    contenido = client.get(acuse).content.decode()
    assert "Enviar otra propuesta" in contenido
