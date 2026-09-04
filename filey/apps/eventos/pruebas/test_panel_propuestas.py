"""
El panel del administrador: la cola, el detalle y el dictamen.

Cubre `CU-EVT-007` (lista filtrable), `CU-EVT-008` (detalle),
`CU-EVT-009` (dictaminar, con sus alternos y excepciones) y `CU-EVT-011`
(conteos por estado).

Lo que se vigila aquí es lo que ni el modelo ni la plantilla pueden:

1. **El módulo declara su panel** (`ADR-0006`). Olvidar `url_panel` o las
   secciones no da error: la barra lateral saldría vacía y el catálogo no
   ofrecería entrar a administrar, para siempre.
2. **Los filtros se combinan y se conservan.** Cambiar de estado no borra
   lo que se tecleó, ni al revés. Es lo que hace usable la cola y lo
   único que ninguna prueba de servicio alcanza.
3. **El folio se busca aunque no sea una columna.** Se compone (§2.4), y
   sin la traducción a `pk` el buscador que el CU pide no encontraría
   nunca nada.
4. **`E3`: sin el texto obligatorio no hay dictamen**, y la regla vive en
   el servicio para que un comando de `manage.py` tampoco se la salte.
5. **`E2`: un dictamen emitido solo lo cambia el operador.** Es la única
   lectura posible del permiso que pide `A3` dentro de ADR-0004/0005.
6. **Solo «cambios» manda correo.** Aceptar y rechazar esperan al lote
   (`CU-EVT-010`), y una prueba que los dejara mandando avisos escondería
   que ese lote todavía no existe.
"""

import pytest
from django.conf import settings
from django.core import mail
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.convocatorias.models import TipoConvocatoria
from apps.convocatorias.modulos import modulo_de
from apps.registros.models import Persona

from ..models import MODELO_POR_TIPO, CatalogoActividades, Solicitud
from ..servicios import dictamen, revision
from . import fabricas

pytestmark = pytest.mark.django_db


# ── Ayudas ────────────────────────────────────────────────────


def _url(feria, nombre, **kwargs):
    """La dirección completa, con el prefijo de la feria.

    `reverse` a secas devuelve la ruta sin `/f/<slug>/`: el prefijo lo
    antepone `django-tenants` al resolver, no al construir.
    """
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _propuesta(convocatoria, *, correo, nombre_tipo="charla", **cambios):
    """Una propuesta completa —solicitud y actividad— dentro del schema.

    La actividad hace falta aunque la prueba no la mire, y tiene que ser
    la **fila hija** y no el padre suelto: `Actividad.detalle` baja al
    tipo, y un padre sin hijo levanta al pintar el detalle. Una `Actividad`
    a secas no representa nada que el envío pueda producir — `crear` las
    hace siempre juntas, en la misma transacción.
    """
    persona = fabricas.persona(correo=correo, nombre=correo.split("@")[0].capitalize())
    registro = fabricas.registro(persona, convocatoria)
    solicitud = fabricas.solicitud(registro, **cambios)
    ModeloDelTipo = MODELO_POR_TIPO[nombre_tipo]
    ModeloDelTipo.objects.create(
        solicitud=solicitud,
        tipo=fabricas.tipo(nombre_tipo),
        # El mínimo que los seis tipos sin publicación exigen: una persona
        # con su semblanza.
        nombre_participante_1="Elena Poniatowska",
        semblanza_participante_1="Escritora y periodista.",
    )
    return solicitud


def _duena(feria):
    """La cuenta que administra la feria, que crea el alta."""
    return Persona.objects.get(correo="ana@uady.mx")


def _operador():
    return Persona.objects.create_superuser(
        correo="tecnica@uady.mx", nombre="Tec", primer_apellido="Nica"
    )


# ── El enganche con FER (`ADR-0006`) ──────────────────────────


def test_eventos_declara_su_panel_y_sus_secciones():
    """La prueba que el registro de módulos exige, para el lado admin.

    Sin `url_panel` el catálogo no ofrece entrar a administrar, y sin
    `secciones_panel` la barra lateral sale vacía. Ninguna de las dos
    cosas revienta: simplemente no aparecen, que es la peor forma de
    fallar.
    """
    modulo = modulo_de(TipoConvocatoria.EVT)
    assert modulo.url_panel == "eventos:propuestas"

    etiquetas = [seccion.etiqueta for seccion in modulo.secciones_panel]
    assert etiquetas[0] == "Propuestas"
    # El detalle **pertenece** a Propuestas: sin esto, abrir una propuesta
    # apaga el único renglón encendido de la barra.
    assert "eventos:detalle_propuesta" in modulo.secciones_panel[0].tambien
    # Las otras cuatro están en el plan y sin construir: se declaran sin
    # ruta para que el menú enseñe la forma completa del módulo.
    assert all(s.ruta is None for s in modulo.secciones_panel[1:])


# ── CU-EVT-007 · la cola y sus filtros ────────────────────────


def test_la_cola_lista_las_propuestas_de_esa_convocatoria(client, feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        _propuesta(convocatoria, correo="laura@ejemplo.com")

    client.force_login(_duena(feria_2027))
    respuesta = client.get(
        _url(feria_2027, "eventos:propuestas", convocatoria_id=convocatoria.pk)
    )

    assert respuesta.status_code == 200
    contenido = respuesta.content.decode()
    assert "El mar que nos habita" in contenido
    # El folio se compone y se enseña: es con lo que se nombra la
    # propuesta en cualquier trámite posterior.
    assert "EVE-" in contenido


def test_quien_no_administra_la_feria_no_entra_a_la_cola(client, feria_2027):
    """El decorador, no la carpeta de la plantilla, es lo que protege."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()

    client.force_login(fabricas.persona(correo="ajena@ejemplo.com"))
    respuesta = client.get(
        _url(feria_2027, "eventos:propuestas", convocatoria_id=convocatoria.pk)
    )
    assert respuesta.status_code == 403


def test_el_filtro_por_estado_recorta_la_cola(client, feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        _propuesta(convocatoria, correo="uno@ejemplo.com")
        _propuesta(
            convocatoria,
            correo="dos@ejemplo.com",
            titulo_actividad="Lengua maya y tecnología",
            estado=Solicitud.Estado.ACEPTADA,
        )

    client.force_login(_duena(feria_2027))
    url = _url(feria_2027, "eventos:propuestas", convocatoria_id=convocatoria.pk)

    contenido = client.get(url, {"estado": "aceptada"}).content.decode()
    assert "Lengua maya y tecnología" in contenido
    assert "El mar que nos habita" not in contenido


def test_el_filtro_por_tipo_recorta_la_cola(client, feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        _propuesta(convocatoria, correo="uno@ejemplo.com", nombre_tipo="charla")
        _propuesta(
            convocatoria,
            correo="dos@ejemplo.com",
            nombre_tipo="conferencia",
            titulo_actividad="Lengua maya y tecnología",
        )

        filas = revision.cola(convocatoria, tipo="conferencia")
        assert [s.titulo_actividad for s in filas] == ["Lengua maya y tecnología"]


def test_el_filtro_por_categoria_recorta_la_cola(feria_2027):
    """La categoría solo existe después del dictamen, y así se filtra."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        _propuesta(convocatoria, correo="uno@ejemplo.com")
        _propuesta(
            convocatoria,
            correo="dos@ejemplo.com",
            titulo_actividad="Lengua maya y tecnología",
            estado=Solicitud.Estado.ACEPTADA,
            categoria=Solicitud.Categoria.ACADEMICA,
        )

        filas = revision.cola(convocatoria, categoria="academica")
        assert [s.titulo_actividad for s in filas] == ["Lengua maya y tecnología"]


def test_se_busca_por_folio_aunque_no_sea_una_columna(feria_2027):
    """El folio se compone (§2.4): buscarlo es traducirlo a la clave.

    Sin esto, el buscador por folio que pide el paso 3 del caso de uso no
    encontraría nunca nada, y el fallo sería mudo — devolvería cero filas,
    que es indistinguible de "no hay ninguna".
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="uno@ejemplo.com")
        _propuesta(
            convocatoria,
            correo="dos@ejemplo.com",
            titulo_actividad="Lengua maya y tecnología",
        )

        # Las tres formas en que alguien teclea el mismo folio.
        for tecleado in (propuesta.folio, str(propuesta.pk), f"eve {propuesta.pk}"):
            encontradas = revision.cola(convocatoria, busqueda=tecleado)
            assert propuesta in encontradas, tecleado


def test_se_busca_por_titulo_por_persona_y_por_institucion(feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(
            convocatoria, correo="laura@ejemplo.com", institucion="Editorial La Nave"
        )

        for tecleado in ("mar que nos habita", "Peniche", "La Nave"):
            assert propuesta in revision.cola(convocatoria, busqueda=tecleado), tecleado


def test_sin_filtros_salen_todas(feria_2027):
    """`A1` del caso de uso."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        _propuesta(convocatoria, correo="uno@ejemplo.com")
        _propuesta(convocatoria, correo="dos@ejemplo.com")

        assert revision.cola(convocatoria).count() == 2


def test_sin_resultados_se_avisa_y_se_conservan_los_filtros(client, feria_2027):
    """`E1`: la lista vacía se puede ajustar, no es un callejón."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        _propuesta(convocatoria, correo="uno@ejemplo.com")

    client.force_login(_duena(feria_2027))
    contenido = client.get(
        _url(feria_2027, "eventos:propuestas", convocatoria_id=convocatoria.pk),
        {"q": "no existe nada así"},
    ).content.decode()

    assert "Ninguna propuesta cumple estos filtros" in contenido
    # Lo tecleado sigue en la caja: sin esto hay que volver a escribirlo
    # para corregir una letra.
    assert "no existe nada así" in contenido


def test_cambiar_de_estado_no_borra_lo_que_se_tecleo(client, feria_2027):
    """Los chips arrastran la búsqueda, y el buscador arrastra el resto.

    Es lo que permite combinar los cuatro filtros sin JavaScript, y se
    rompe en silencio: cada control seguiría funcionando por su cuenta.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        _propuesta(convocatoria, correo="uno@ejemplo.com")

    client.force_login(_duena(feria_2027))
    contenido = client.get(
        _url(feria_2027, "eventos:propuestas", convocatoria_id=convocatoria.pk),
        {"q": "mar", "tipo": "charla", "categoria": "literaria"},
    ).content.decode()

    # En los enlaces de los chips.
    assert "q=mar" in contenido
    assert "tipo=charla" in contenido
    # Y escondidos en el formulario del buscador.
    assert 'name="tipo" value="charla"' in contenido
    assert 'name="categoria" value="literaria"' in contenido


def test_la_cola_no_ve_las_propuestas_de_otra_convocatoria(feria_2027):
    with schema_context(feria_2027.schema_name):
        una = fabricas.convocatoria(nombre="Actividades 2027")
        otra = fabricas.convocatoria(nombre="Actividades infantiles 2027")
        _propuesta(una, correo="uno@ejemplo.com")

        assert revision.cola(otra).count() == 0


# ── CU-EVT-011 · los conteos ──────────────────────────────────


def test_los_cuatro_numeros_del_resumen(feria_2027):
    """«Por revisar» junta pendiente y cambios solicitados, a propósito.

    Las dos esperan algo del comité, que es la pregunta que contesta esa
    tarjeta. El desglose fino está en los chips.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        _propuesta(convocatoria, correo="uno@ejemplo.com")
        _propuesta(
            convocatoria,
            correo="dos@ejemplo.com",
            estado=Solicitud.Estado.CAMBIOS_SOLICITADOS,
        )
        _propuesta(
            convocatoria, correo="tres@ejemplo.com", estado=Solicitud.Estado.ACEPTADA
        )
        _propuesta(
            convocatoria, correo="cuatro@ejemplo.com", estado=Solicitud.Estado.RECHAZADA
        )

        numeros = revision.resumen(convocatoria)

    assert numeros["recibidas"] == 4
    assert numeros["por_revisar"] == 2
    assert numeros["aceptadas"] == 1
    assert numeros["rechazadas"] == 1


def test_los_conteos_no_los_mueve_un_filtro_puesto(client, feria_2027):
    """Un chip que dijera 0 por culpa de otro filtro no sirve para navegar."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        _propuesta(convocatoria, correo="uno@ejemplo.com")
        _propuesta(
            convocatoria, correo="dos@ejemplo.com", estado=Solicitud.Estado.ACEPTADA
        )

    client.force_login(_duena(feria_2027))
    respuesta = client.get(
        _url(feria_2027, "eventos:propuestas", convocatoria_id=convocatoria.pk),
        {"estado": "aceptada"},
    )
    # La cola trae una, pero el resumen sigue contando las dos.
    assert respuesta.context["cuantas"] == 1
    assert respuesta.context["resumen"]["recibidas"] == 2


# ── CU-EVT-008 · el detalle ───────────────────────────────────


def test_el_detalle_muestra_al_proponente_y_a_la_actividad(client, feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="laura@ejemplo.com")

    client.force_login(_duena(feria_2027))
    contenido = client.get(
        _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk)
    ).content.decode()

    assert "El mar que nos habita" in contenido
    assert "laura@ejemplo.com" in contenido
    assert "Editorial La Nave" in contenido
    # El público sale con su rótulo y no con el valor de la columna.
    assert "Público en general" in contenido
    assert "publico_general" not in contenido


def test_el_detalle_muestra_a_las_personas_con_el_rotulo_de_su_tipo(feria_2027):
    """En una presentación de libro, `nombre_participante_1` es el presentador.

    El rótulo sale del `verbose_name` y no del nombre en Python, y ésta es
    la diferencia: leer el nombre del campo diría «Participante 1» donde
    la convocatoria dice «Presentador 1».
    """
    from ..models import ActividadPresentacionLibro

    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona(correo="edit@ejemplo.com")
        registro = fabricas.registro(persona, convocatoria)
        solicitud = fabricas.solicitud(registro)
        actividad = ActividadPresentacionLibro.objects.create(
            solicitud=solicitud,
            tipo=fabricas.tipo(CatalogoActividades.Nombre.PRESENTACION_LIBRO),
            titulo_publicacion="El mar que nos habita",
            tipo_presentador="editor",
            nombre_editorial="La Nave",
            nombre_autor_1="Renata Solís",
            semblanza_autor_1="Narradora yucateca.",
            autor_1_participa=True,
            nombre_participante_1="Jorge Cauich",
            semblanza_participante_1="Crítico literario.",
        )

        gente = revision.personas_de(actividad)

    roles = {quien.rol: quien for quien in gente}
    assert "Autor 1" in roles
    assert "Presentador 1" in roles
    assert roles["Autor 1"].nombre == "Renata Solís"
    # La casilla de asistencia solo la tienen autores y editores.
    assert roles["Autor 1"].participa is True
    assert roles["Presentador 1"].participa is None


def test_los_huecos_opcionales_no_salen_en_la_ficha(feria_2027):
    """Una charla admite dos participantes y casi siempre trae uno."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona(correo="uno@ejemplo.com")
        registro = fabricas.registro(persona, convocatoria)
        solicitud = fabricas.solicitud(registro)
        from ..models import ActividadCharla

        actividad = ActividadCharla.objects.create(
            solicitud=solicitud,
            tipo=fabricas.tipo("charla"),
            nombre_participante_1="Elena Poniatowska",
            semblanza_participante_1="Escritora y periodista.",
        )

        gente = revision.personas_de(actividad)

    assert [quien.nombre for quien in gente] == ["Elena Poniatowska"]


# ── CU-EVT-009 · el dictamen ──────────────────────────────────


def test_aceptar_clasifica_y_deja_constancia_de_quien(feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="uno@ejemplo.com")
        revisora = _duena(feria_2027)

        dictamen.aceptar(
            propuesta,
            revisor=revisora,
            categoria=Solicitud.Categoria.LITERARIA,
            es_uady_confirmado=False,
        )
        propuesta.refresh_from_db()

    assert propuesta.estado == Solicitud.Estado.ACEPTADA
    assert propuesta.categoria == Solicitud.Categoria.LITERARIA
    assert propuesta.es_uady_confirmado is False
    assert propuesta.revisado_por_id == revisora.pk
    assert propuesta.fecha_revision is not None
    # La postcondición que alimenta el lote de `CU-EVT-010`.
    assert propuesta.resultado_notificado is False
    # Y la categoría se compone al leer, nunca se almacena junta.
    assert propuesta.categoria_completa == "Literaria · Externo"


def test_aceptar_sin_clasificar_no_se_puede(feria_2027):
    """Sin categoría la fila no entra en ningún grupo del conteo (§3.6)."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="uno@ejemplo.com")

        with pytest.raises(dictamen.DictamenRechazado):
            dictamen.aceptar(
                propuesta,
                revisor=_duena(feria_2027),
                categoria="",
                es_uady_confirmado=False,
            )
        propuesta.refresh_from_db()
        assert propuesta.estado == Solicitud.Estado.PENDIENTE


def test_rechazar_exige_motivo(feria_2027):
    """`E3`. En `STD` el motivo es opcional; aquí no, y es del caso de uso."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="uno@ejemplo.com")

        with pytest.raises(dictamen.DictamenRechazado):
            dictamen.rechazar(propuesta, revisor=_duena(feria_2027), motivo="   ")
        propuesta.refresh_from_db()
        assert propuesta.estado == Solicitud.Estado.PENDIENTE


def test_rechazar_registra_el_motivo(feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="uno@ejemplo.com")

        dictamen.rechazar(
            propuesta,
            revisor=_duena(feria_2027),
            motivo="No corresponde al perfil de la convocatoria.",
        )
        propuesta.refresh_from_db()

    assert propuesta.estado == Solicitud.Estado.RECHAZADA
    assert "perfil de la convocatoria" in propuesta.motivo_rechazo


def test_solicitar_cambios_exige_mensaje(feria_2027):
    """`E3`: es literalmente el cuerpo del correo."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="uno@ejemplo.com")

        with pytest.raises(dictamen.DictamenRechazado):
            dictamen.solicitar_cambios(propuesta, revisor=_duena(feria_2027), mensaje="")


def test_solicitar_cambios_avisa_en_el_momento(feria_2027):
    """`A1` paso 5. Es el único desenlace que no espera al lote."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="laura@ejemplo.com")
        mail.outbox.clear()

        dictamen.solicitar_cambios(
            propuesta,
            revisor=_duena(feria_2027),
            mensaje="Falta la semblanza del participante 2.",
        )
        propuesta.refresh_from_db()
        # El folio se lee **aquí dentro**: se compone recorriendo
        # `registro → convocatoria → configuracion`, que son tablas del
        # schema de la feria, y `refresh_from_db` acaba de vaciar la caché
        # de relaciones. Fuera del contexto la consulta iría a `public`,
        # donde esas tablas no existen (`ADR-0003`).
        folio = propuesta.folio

    assert propuesta.estado == Solicitud.Estado.CAMBIOS_SOLICITADOS
    assert len(mail.outbox) == 1
    correo = mail.outbox[0]
    assert correo.to == ["laura@ejemplo.com"]
    assert folio in correo.subject
    # El mensaje viaja tal cual: es lo que hay que corregir.
    assert "Falta la semblanza del participante 2." in correo.body


@pytest.mark.parametrize("accion", ["aceptar", "rechazar"])
def test_aceptar_y_rechazar_no_mandan_correo(feria_2027, accion):
    """Salen en lote (`CU-EVT-010`), que todavía no existe.

    Si esta prueba empieza a fallar porque hay un correo de más, lo que
    pasó es que alguien adelantó la notificación individual — y entonces
    el lote deja de tener sentido.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="uno@ejemplo.com")
        revisora = _duena(feria_2027)
        mail.outbox.clear()

        if accion == "aceptar":
            dictamen.aceptar(
                propuesta,
                revisor=revisora,
                categoria=Solicitud.Categoria.ACADEMICA,
                es_uady_confirmado=True,
            )
        else:
            dictamen.rechazar(propuesta, revisor=revisora, motivo="Fuera de tema.")

    assert mail.outbox == []


def test_se_pueden_pedir_cambios_varias_veces(feria_2027):
    """`A1` paso 6: pedir correcciones no es resolver la propuesta."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="uno@ejemplo.com")
        revisora = _duena(feria_2027)

        dictamen.solicitar_cambios(propuesta, revisor=revisora, mensaje="Falta A.")
        dictamen.solicitar_cambios(propuesta, revisor=revisora, mensaje="Y también B.")
        propuesta.refresh_from_db()

    assert propuesta.mensaje_cambios_solicitados == "Y también B."


# ── `A3` y `E2` · volver sobre un dictamen emitido ────────────


def test_quien_administra_no_puede_rehacer_un_dictamen(feria_2027):
    """`E2`. El resultado pudo salir ya, y deshacerlo no es lo mismo que
    emitirlo."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(
            convocatoria, correo="uno@ejemplo.com", estado=Solicitud.Estado.ACEPTADA
        )

        with pytest.raises(dictamen.DictamenRechazado):
            dictamen.rechazar(
                propuesta, revisor=_duena(feria_2027), motivo="Me equivoqué."
            )
        propuesta.refresh_from_db()
        assert propuesta.estado == Solicitud.Estado.ACEPTADA


def test_el_operador_si_puede_rehacerlo(feria_2027):
    """`A3`. El superusuario de la plataforma (`ADR-0005`) es quien puede."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(
            convocatoria, correo="uno@ejemplo.com", estado=Solicitud.Estado.ACEPTADA
        )
        # Ya se le había notificado: el cambio tiene que volver a quedar
        # pendiente, para salir como corrección en el siguiente lote.
        propuesta.resultado_notificado = True
        propuesta.save(update_fields=["resultado_notificado"])

        dictamen.rechazar(propuesta, revisor=_operador(), motivo="Se duplicó.")
        propuesta.refresh_from_db()

    assert propuesta.estado == Solicitud.Estado.RECHAZADA
    assert propuesta.resultado_notificado is False


def test_pedir_cambios_no_cuenta_como_dictamen_emitido(feria_2027):
    """`cambios_solicitados` deja la propuesta abierta, así que no topa
    con el permiso de re-dictamen."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(
            convocatoria,
            correo="uno@ejemplo.com",
            estado=Solicitud.Estado.CAMBIOS_SOLICITADOS,
        )

        dictamen.aceptar(
            propuesta,
            revisor=_duena(feria_2027),
            categoria=Solicitud.Categoria.LITERARIA,
            es_uady_confirmado=False,
        )
        propuesta.refresh_from_db()

    assert propuesta.estado == Solicitud.Estado.ACEPTADA


# ── El dictamen desde la pantalla ─────────────────────────────


def test_dictaminar_desde_la_pantalla(client, feria_2027):
    """El POST llega con el `name="accion"` del botón, sin JavaScript."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(convocatoria, correo="uno@ejemplo.com")

    client.force_login(_duena(feria_2027))
    url = _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk)
    respuesta = client.post(
        url,
        {
            "accion": "aceptar",
            "categoria": "academica",
            "es_uady_confirmado": "on",
            "motivo": "",
        },
    )

    assert respuesta.status_code == 302
    with schema_context(feria_2027.schema_name):
        propuesta.refresh_from_db()
    assert propuesta.estado == Solicitud.Estado.ACEPTADA
    assert propuesta.categoria_completa == "Académica · UADY"


def test_rehacer_un_dictamen_pide_confirmacion_expresa(client, feria_2027):
    """`A3` paso 3. Sin la casilla, el POST no toca nada."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(
            convocatoria, correo="uno@ejemplo.com", estado=Solicitud.Estado.ACEPTADA
        )
        operador = _operador()

    client.force_login(operador)
    url = _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk)

    client.post(url, {"accion": "rechazar", "motivo": "Se duplicó.", "categoria": ""})
    with schema_context(feria_2027.schema_name):
        propuesta.refresh_from_db()
    assert propuesta.estado == Solicitud.Estado.ACEPTADA

    client.post(
        url,
        {
            "accion": "rechazar",
            "motivo": "Se duplicó.",
            "categoria": "",
            "confirmar": "on",
        },
    )
    with schema_context(feria_2027.schema_name):
        propuesta.refresh_from_db()
    assert propuesta.estado == Solicitud.Estado.RECHAZADA


def test_a_quien_no_puede_rehacerlo_no_se_le_ofrece_el_formulario(client, feria_2027):
    """La pantalla pregunta lo mismo que el servicio, y dice a quién acudir."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _propuesta(
            convocatoria, correo="uno@ejemplo.com", estado=Solicitud.Estado.ACEPTADA
        )

    client.force_login(_duena(feria_2027))
    contenido = client.get(
        _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk)
    ).content.decode()

    assert "reservado al equipo técnico" in contenido
    assert 'value="aceptar"' not in contenido


# ── `CU-EVT-008` · corregir la redacción sin devolver la propuesta ──
#
# Lo que se vigila aquí es lo que la pantalla no puede sostener sola:
#
# 1. **Solo se escriben las dos cosas que se dejan escribir.** El resto de
#    la ficha llega en el mismo POST —los campos existen en la pantalla— y
#    un servicio que aceptara lo que le manden convertiría una corrección
#    de estilo en la reescritura de la propuesta.
# 2. **Nadie se queda sin semblanza.** Es la invariante que el alta
#    sostiene con `validar_personas`, y aquí es más fácil de romper: quien
#    corrige ve el recuadro lleno y lo puede vaciar de un tirón.
# 3. **Corregir no dictamina.** Son dos formularios en la misma pantalla y
#    comparten el `name="accion"`; cruzarlos aceptaría propuestas al
#    guardar una errata.


def _con_personas(convocatoria, correo="autora@ejemplo.com"):
    """Una propuesta de charla con una persona y su semblanza."""
    return _propuesta(convocatoria, correo=correo)


def test_corregir_guarda_la_sinopsis_y_la_semblanza(client, feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _con_personas(convocatoria)

    client.force_login(_duena(feria_2027))
    respuesta = client.post(
        _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk),
        {
            "accion": "corregir",
            "sinopsis": "Una charla sobre la crónica mexicana del siglo XX.",
            "semblanza_participante_1": "Escritora y periodista mexicana.",
        },
    )

    assert respuesta.status_code == 302
    with schema_context(feria_2027.schema_name):
        propuesta.refresh_from_db()
        detalle = propuesta.actividad.detalle
        assert propuesta.sinopsis.startswith("Una charla sobre la crónica")
        assert detalle.semblanza_participante_1 == "Escritora y periodista mexicana."


def test_corregir_no_toca_nada_mas_de_la_propuesta(client, feria_2027):
    """El POST trae la ficha entera; el servicio solo mira lo suyo."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _con_personas(convocatoria)
        titulo = propuesta.titulo_actividad
        institucion = propuesta.institucion

    client.force_login(_duena(feria_2027))
    client.post(
        _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk),
        {
            "accion": "corregir",
            "sinopsis": "Texto corregido.",
            "semblanza_participante_1": "Semblanza corregida.",
            # Todo esto viaja y **no** se debe escribir.
            "titulo_actividad": "Otro título",
            "institucion": "Otra institución",
            "es_uady": "on",
            "estado": "aceptada",
            "nombre_participante_1": "Otra persona",
        },
    )

    with schema_context(feria_2027.schema_name):
        propuesta.refresh_from_db()
        assert propuesta.titulo_actividad == titulo
        assert propuesta.institucion == institucion
        assert propuesta.es_uady is False
        assert propuesta.estado == Solicitud.Estado.PENDIENTE
        assert propuesta.actividad.detalle.nombre_participante_1 == "Elena Poniatowska"


def test_una_semblanza_no_se_puede_vaciar(client, feria_2027):
    """La misma invariante que el alta: media persona no se puede imprimir."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _con_personas(convocatoria)

    client.force_login(_duena(feria_2027))
    respuesta = client.post(
        _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk),
        {
            "accion": "corregir",
            "sinopsis": "Texto corregido.",
            "semblanza_participante_1": "   ",
        },
    )

    # Se queda en la pantalla, con lo escrito y el aviso de por qué.
    assert respuesta.status_code == 200
    assert "sin semblanza" in respuesta.content.decode()
    with schema_context(feria_2027.schema_name):
        propuesta.refresh_from_db()
        assert propuesta.actividad.detalle.semblanza_participante_1
        # Y la sinopsis tampoco entró: las dos escrituras van juntas.
        assert propuesta.sinopsis != "Texto corregido."


def test_la_sinopsis_no_se_puede_vaciar(client, feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _con_personas(convocatoria)
        antes = propuesta.sinopsis

    client.force_login(_duena(feria_2027))
    respuesta = client.post(
        _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk),
        {"accion": "corregir", "sinopsis": "", "semblanza_participante_1": "Algo."},
    )

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        propuesta.refresh_from_db()
        assert propuesta.sinopsis == antes


def test_corregir_no_dictamina(client, feria_2027):
    """Los dos formularios comparten `accion`, y no se pueden cruzar."""
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _con_personas(convocatoria)

    client.force_login(_duena(feria_2027))
    client.post(
        _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk),
        {
            "accion": "corregir",
            "sinopsis": "Texto corregido.",
            "semblanza_participante_1": "Semblanza corregida.",
            "categoria": "literaria",
        },
    )

    with schema_context(feria_2027.schema_name):
        propuesta.refresh_from_db()
        assert propuesta.estado == Solicitud.Estado.PENDIENTE
        assert propuesta.categoria == ""
        assert propuesta.fecha_revision is None


def test_el_modo_de_edicion_se_puede_abrir_sin_javascript(client, feria_2027):
    """`?editar=1` es la otra puerta del botón «Corregir textos».

    Con Alpine el botón desbloquea los recuadros en el acto; sin él es un
    enlace a esta dirección, y entonces es el servidor quien tiene que
    pintarlos ya desbloqueados.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _con_personas(convocatoria)

    client.force_login(_duena(feria_2027))
    url = _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk)

    assert client.get(url).context["editando"] is False
    assert client.get(url, {"editar": "1"}).context["editando"] is True


# ── `CU-EVT-009` · las dos ventanas que piden un texto ────────


def test_pedir_cambios_sin_motivo_devuelve_la_ventana_abierta(client, feria_2027):
    """Es lo que pasa sin JavaScript: el botón envía, el servicio rechaza
    y la pantalla vuelve con la ventana abierta y el aviso dentro.

    Sin esto, quien no tiene JavaScript recibe un error y una pantalla en
    la que no se ve dónde escribir la respuesta.
    """
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _con_personas(convocatoria)

    client.force_login(_duena(feria_2027))
    respuesta = client.post(
        _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk),
        {"accion": "cambios", "motivo": "", "categoria": ""},
    )

    assert respuesta.status_code == 200
    assert respuesta.context["modal_abierto"] == "cambios"
    with schema_context(feria_2027.schema_name):
        propuesta.refresh_from_db()
        assert propuesta.estado == Solicitud.Estado.PENDIENTE


def test_rechazar_sin_motivo_devuelve_su_propia_ventana(client, feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _con_personas(convocatoria)

    client.force_login(_duena(feria_2027))
    respuesta = client.post(
        _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk),
        {"accion": "rechazar", "motivo": "", "categoria": ""},
    )

    assert respuesta.context["modal_abierto"] == "rechazar"


def test_un_dictamen_que_cuaja_no_deja_ninguna_ventana_abierta(client, feria_2027):
    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        propuesta = _con_personas(convocatoria)

    client.force_login(_duena(feria_2027))
    url = _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=propuesta.pk)
    client.post(url, {"accion": "rechazar", "motivo": "Fuera de tema.", "categoria": ""})

    assert client.get(url).context["modal_abierto"] == ""


def test_el_detalle_de_una_publicacion_pinta_su_seccion_y_su_tope(client, feria_2027):
    """La sección 4 y el tope doble de la sinopsis, en la pantalla.

    Es la única rama del detalle que solo tienen dos de los ocho tipos, y
    la que nombra a la columna `detalle` —la fila hija—: si el `tipo` y el
    modelo se separan, revienta aquí y en ninguna otra parte.
    """
    from ..models import MAX_SINOPSIS_PUBLICACION, ActividadPresentacionLibro

    with schema_context(feria_2027.schema_name):
        convocatoria = fabricas.convocatoria()
        persona = fabricas.persona(correo="edit@ejemplo.com")
        registro = fabricas.registro(persona, convocatoria)
        solicitud = fabricas.solicitud(registro)
        ActividadPresentacionLibro.objects.create(
            solicitud=solicitud,
            tipo=fabricas.tipo(CatalogoActividades.Nombre.PRESENTACION_LIBRO),
            titulo_publicacion="El mar que nos habita",
            tipo_presentador="editor",
            nombre_editorial="La Nave",
            nombre_autor_1="Renata Solís",
            semblanza_autor_1="Narradora yucateca.",
            autor_1_participa=True,
        )

    client.force_login(_duena(feria_2027))
    respuesta = client.get(
        _url(feria_2027, "eventos:detalle_propuesta", solicitud_id=solicitud.pk)
    )
    contenido = respuesta.content.decode()

    assert respuesta.context["es_publicacion"] is True
    assert respuesta.context["tope_sinopsis"] == MAX_SINOPSIS_PUBLICACION
    # El rótulo dice de qué es la sinopsis, que es lo único que distingue
    # la de un libro de la de una charla: la columna es la misma.
    assert "Sinopsis de la publicación" in contenido
    assert "Datos de la publicación" in contenido
    assert "La Nave" in contenido
    # Y la semblanza del autor llega como recuadro corregible.
    assert 'name="semblanza_autor_1"' in contenido
