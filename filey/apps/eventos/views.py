"""
Las pantallas de `EVT`, las dos caras.

**U1 y U2**, lo que ve quien propone: capturar y enviar (`CU-EVT-002`) con
su acuse, el listado de seguimiento y el detalle de lo enviado
(`CU-EVT-003`). El listado es además la **puerta del módulo**: es a donde
apunta el catálogo (`ADR-0006`), y sin ninguna propuesta enseña `E1`, que
lleva al formulario.

**A1 y A2**, lo que ve quien administra: la cola de propuestas con sus
filtros y sus conteos (`CU-EVT-007`, `CU-EVT-011`) y el detalle desde
donde se dictamina (`CU-EVT-008`, `CU-EVT-009`).

Entre las dos está la entrega de adjuntos, que sirve a los dos públicos y
por eso no es de ninguno (`ADR-0007`).

No son dos módulos ni dos carpetas de plantillas: el rol lo resuelve el
decorador, no la ubicación del archivo.

Vistas delgadas: traducen HTTP a una llamada de `servicios/` y de vuelta.
Ninguna decide si una convocatoria admite envíos ni si el registro
corresponde al tipo — eso vive en los servicios, donde un comando de
`manage.py` también lo alcanza.

.. note:: Por qué el tipo viaja en la barra de direcciones

   El formulario cambia según el tipo de actividad, y **toda pantalla
   tiene que funcionar sin JavaScript**. Con el tipo en `?tipo=`, elegirlo
   es enviar el formulario por `GET`: el navegador arrastra lo que ya
   estaba escrito —institución, cargo, título— y la pantalla vuelve con
   esos valores y con los campos del tipo. Con htmx, la misma petición
   cambia solo la sección 3 y ni siquiera hay recarga.

   La alternativa —pintar los ocho juegos de campos y esconder siete— deja
   sin JavaScript una pantalla con cuarenta campos contradictorios, y
   además obliga a que el POST traiga los ocho.
"""

from dataclasses import replace

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.ferias import permisos
from apps.ferias.permisos import requiere_admin_feria
from apps.registros.permisos import requiere_participante
from comun.filtros import chips_de_estado
from comun.htmx import es_htmx

from . import detalle as composicion
from .formularios import FORMULARIO_POR_TIPO, DictamenForm, SolicitudForm
from .models import MAX_SEMBLANZA, Documento, Solicitud
from .servicios import (
    archivos,
    catalogo,
    dictamen,
    edicion,
    en_espera,
    revision,
    seguimiento,
    solicitudes,
)


def _convocatoria_de_eventos(convocatoria_id: int) -> Convocatoria:
    """La convocatoria del prefijo, si de verdad es de eventos.

    Un 404 y no un 403: una convocatoria de stands **no existe** para
    este módulo, y decir "no tienes permiso" insinuaría que con otro
    permiso sí. No hace falta filtrar por feria — el schema ya lo hace
    (`ADR-0003`).
    """
    convocatoria = get_object_or_404(Convocatoria, pk=convocatoria_id)
    if convocatoria.tipo != TipoConvocatoria.EVT:
        raise Http404("Esta convocatoria no es de actividades del programa.")
    return convocatoria


@requiere_participante
def propuesta(peticion, convocatoria_id):
    """Capturar y enviar una propuesta (`CU-EVT-002`).

    Una sola pantalla para los pasos 1 a 14: elegir el tipo, llenar lo
    común y lo del tipo, y enviar. Lo que cambia entre un estado y otro
    es qué se pinta, no a dónde se va.
    """
    convocatoria = _convocatoria_de_eventos(convocatoria_id)
    abierta = solicitudes.admite_propuestas(convocatoria)

    # El tipo llega de la barra de direcciones al elegirlo y del POST al
    # enviar. Un valor inventado no es un error del sistema: es alguien
    # tecleando en la URL, así que se trata como "todavía no eligió".
    nombre_tipo = (peticion.POST.get("tipo") or peticion.GET.get("tipo") or "").strip()
    tipo = catalogo.tipo_por_nombre(nombre_tipo)
    if tipo is None:
        nombre_tipo = ""
    es_publicacion = bool(nombre_tipo) and catalogo.es_publicacion(nombre_tipo)

    FormularioDelTipo = FORMULARIO_POR_TIPO.get(nombre_tipo)

    # La sesión sella cada adjunto en espera, así que tiene que existir
    # antes de tocarlos. Quien acaba de entrar puede no tener clave aún.
    if not peticion.session.session_key:
        peticion.session.save()
    sesion = peticion.session.session_key

    # Descartar un adjunto es un `POST` que **no es un envío**: escribe
    # —borra una fila y su archivo— y vuelve a pintar la pantalla. Se
    # atiende antes que nada y con lo demás sin validar, porque nadie ha
    # intentado enviar todavía: marcar en rojo lo que aún se está
    # llenando es lo que la ley de Postel desaconseja.
    descartado = _atender_descarte(peticion, convocatoria, FormularioDelTipo, sesion)
    enviando = peticion.method == "POST" and not descartado

    # Cambiar de tipo se lleva los adjuntos que el nuevo no pide. Quien
    # subió la portada de un libro y pasa a «charla» no tiene ya dónde
    # enseñarla ni campo al que volver.
    #
    # Solo cuando hay un tipo elegido y válido: sin tipo no hay con qué
    # comparar, y barrer ahí sería borrar por no saber. Los seis tipos
    # que no piden adjuntos declaran `TIPO_POR_ADJUNTO` vacío, así que
    # este mismo paso los deja sin nada — que es lo correcto.
    #
    # Va **después** del descarte —que pudo guardar archivos de esta
    # misma petición— y **antes** de leer lo vigente, o el formulario se
    # construiría contando adjuntos que se acaban de ir.
    if tipo is not None:
        en_espera.descartar_los_que_ya_no_caben(
            convocatoria,
            peticion.user,
            sesion,
            FormularioDelTipo.TIPO_POR_ADJUNTO.values() if FormularioDelTipo else (),
        )

    # Lo que esa persona subió **en esta sesión** y no llegó a enviarse.
    # Se consulta al final, cuando ya no queda nada que lo cambie, y antes
    # de construir el formulario, que es quien decide con esto si los
    # adjuntos siguen siendo obligatorios.
    #
    # Por sesión y no por persona: `EVT` no guarda borradores, así que
    # volver mañana empieza de cero.
    guardados = en_espera.vigentes(convocatoria, peticion.user, sesion)

    if enviando:
        form_solicitud = SolicitudForm(peticion.POST, es_publicacion=es_publicacion)
        form_tipo = (
            FormularioDelTipo(peticion.POST, peticion.FILES, en_espera=guardados)
            if FormularioDelTipo
            else None
        )
    else:
        # `GET` con datos es elegir el tipo, y un `POST` que llega aquí
        # es un descarte: en los dos casos se repuebla con lo que ya
        # estaba escrito, pero sin marcar errores —nadie ha enviado nada
        # todavía y señalar en rojo lo que aún se está llenando es
        # exactamente lo que la ley de Postel desaconseja—.
        datos = peticion.POST or peticion.GET or None
        form_solicitud = SolicitudForm(datos, es_publicacion=es_publicacion)
        form_tipo = (
            FormularioDelTipo(datos, en_espera=guardados) if FormularioDelTipo else None
        )
        if datos is not None:
            form_solicitud.errors.clear()
            if form_tipo is not None:
                form_tipo.errors.clear()

    if enviando and abierta and form_tipo is not None:
        # Los dos se validan **siempre**, y en dos líneas y no en un
        # `and`: el `and` cortocircuita, así que con lo común inválido
        # `form_tipo` nunca llegaba a validarse y se quedaba sin
        # `cleaned_data`. Eso reventaba justo al guardar los adjuntos,
        # que es lo único que pasa cuando el envío falla.
        comun_valido = form_solicitud.is_valid()
        tipo_valido = form_tipo.is_valid()
        if comun_valido and tipo_valido:
            try:
                creada = solicitudes.crear(
                    convocatoria=convocatoria,
                    persona=peticion.user,
                    comunes=form_solicitud.cleaned_data,
                    nombre_tipo=nombre_tipo,
                    detalle=_detalle_de(form_tipo),
                    documentos=_adjuntos_del_envio(form_tipo, guardados),
                )
            except solicitudes.EnvioRechazado as motivo:
                # `E1`: la convocatoria pudo cerrar entre que se pintó el
                # formulario y se pulsó enviar. Se vuelve al formulario
                # con lo capturado, que es lo que el CU pide.
                form_solicitud.add_error(None, str(motivo))
            else:
                # Ya son `Documento` de la propuesta: aquí no queda nada
                # que recuperar, y dejarlo duplicaría cada adjunto.
                en_espera.limpiar(convocatoria, peticion.user)
                return redirect("eventos:confirmacion", solicitud_id=creada.pk)

        # El envío no pasó. Lo que sí llegó se guarda para el siguiente
        # intento: es lo único que el navegador no puede repoblar solo.
        if peticion.FILES:
            en_espera.guardar(
                convocatoria, peticion.user, _adjuntos_validos(form_tipo), sesion
            )
            guardados = en_espera.vigentes(convocatoria, peticion.user, sesion)
            form_tipo.en_espera = guardados

    contexto = {
        "convocatoria": convocatoria,
        "abierta": abierta,
        "tipos": catalogo.tipos(),
        # El objeto y no solo su nombre: el rótulo bonito —«Presentación
        # de libro»— lo sabe el catálogo, y componerlo en la plantilla a
        # partir del valor de la columna daba «Presentacion_Libro».
        "tipo": tipo,
        "tipo_elegido": nombre_tipo,
        "es_publicacion": es_publicacion,
        "form": form_solicitud,
        "form_tipo": form_tipo,
        "enviado": enviando,
    }

    # El fragmento y la página comparten el markup: elegir un tipo con
    # htmx cambia solo la sección 3 (§4 del skill de render).
    if es_htmx(peticion) and not enviando:
        return render(peticion, "eventos/parciales/campos_tipo.html", contexto)
    return render(peticion, "eventos/propuesta.html", contexto)


def _detalle_de(form_tipo) -> dict:
    """Los campos del tipo, sin los adjuntos.

    Los archivos no son columnas de `Actividad_*`: se guardan como
    `Documento` (§2.8), y el servicio los recibe aparte.
    """
    archivos = {campo for campo, _ in _campos_de_archivo(form_tipo)}
    return {
        campo: valor
        for campo, valor in form_tipo.cleaned_data.items()
        if campo not in archivos
    }


def _atender_descarte(peticion, convocatoria, FormularioDelTipo, sesion) -> bool:
    """Quita un adjunto, si la petición viene de ese botón.

    :returns: si esto era un descarte. La vista lo usa para saber que
        este `POST` no era un envío.

    El botón manda el **nombre del campo** —`portada_libro`— y no el
    `tipo_documento`, porque el nombre es lo que la plantilla tiene a
    mano. La traducción la hace el formulario del tipo, que es quien
    conoce la tabla; así un nombre inventado en un `POST` a mano no
    encuentra tipo y no borra nada.

    .. warning:: Primero se guarda lo que llega, y **después** se borra

       Descartar repinta el formulario, y un `<input type="file">` no se
       puede repoblar: un archivo que la persona hubiera elegido en el
       navegador y no hubiera enviado todavía desaparecía al repintar.

       El síntoma era desconcertante —descartar **un** adjunto se llevaba
       los **dos**— y solo salía en un orden concreto: enviar y que lo
       rechacen, descartar uno, volver a adjuntar ése, descartar el otro.
       Descartando dos veces el mismo no pasaba, porque el segundo clic
       ya no llegaba al servidor.

       Los dos pasos van juntos y en este orden. Guardar primero recoge
       lo que venía en la misma petición; borrar después se lleva el que
       se pidió **incluido lo que se acabe de guardar de ese campo**, que
       es lo correcto: quien pulsa «descartar» no quiere ninguno ahí, ni
       el viejo ni el que acaba de elegir.

       Para que los archivos lleguen hace falta además
       `hx-encoding="multipart/form-data"` en el botón: htmx manda
       `x-www-form-urlencoded` por omisión, y eso no sabe llevar
       archivos. Sin JavaScript no hace falta nada — el formulario ya es
       multiparte.
    """
    campo = (peticion.POST.get("descartar") or "").strip()
    if not campo or FormularioDelTipo is None:
        return False
    tipo_documento = FormularioDelTipo.TIPO_POR_ADJUNTO.get(campo)
    if tipo_documento is None:
        return False

    if peticion.FILES:
        # Una instancia de usar y tirar, solo para que los archivos pasen
        # por la misma validación que en un envío: la lista blanca de
        # extensiones vive en el campo del formulario, no aquí. Sus
        # errores no se miran — el formulario que se pinta es otro.
        sonda = FormularioDelTipo(peticion.POST, peticion.FILES)
        sonda.is_valid()
        en_espera.guardar(convocatoria, peticion.user, _adjuntos_validos(sonda), sesion)

    en_espera.descartar(convocatoria, peticion.user, tipo_documento)
    # `True` aunque no hubiera nada que borrar: lo que la vista necesita
    # saber es que **esto no era un envío**, no cuántas filas se fueron.
    # Con `> 0`, un segundo clic sobre una cola ya vacía se trataba como
    # un envío y devolvía el formulario en rojo.
    return True


def _adjuntos_del_envio(form_tipo, guardados):
    """Los adjuntos con los que se crea la propuesta.

    El que llegó ahora manda; si no llegó ninguno para ese campo, se usa
    el que estaba en espera. Ese orden es el que hace que "volver a
    subirlo" signifique "sustituirlo" y no "añadir otro".
    """
    del_envio = []
    for tipo_documento, archivo in form_tipo.documentos():
        if archivo:
            del_envio.append((tipo_documento, archivo))
        elif tipo_documento in guardados:
            del_envio.append(
                (tipo_documento, en_espera.adoptar(guardados[tipo_documento]))
            )
    return tuple(del_envio)


def _adjuntos_validos(form_tipo):
    """Lo que llegó y **pasó su propia validación**, para meterlo en la cola.

    Un archivo con la extensión equivocada no se guarda: el formulario lo
    va a rechazar igual en el siguiente intento, y guardarlo llenaría la
    cola de basura que ocupa sitio y desaloja a los buenos.

    `cleaned_data` solo trae los campos que validaron, así que preguntarle
    a él es exactamente esa comprobación.
    """
    return tuple(
        (tipo_documento, form_tipo.cleaned_data.get(nombre))
        for nombre, tipo_documento in form_tipo.TIPO_POR_ADJUNTO.items()
    )


def _campos_de_archivo(form_tipo):
    from django.forms import FileField

    return [
        (nombre, campo)
        for nombre, campo in form_tipo.fields.items()
        if isinstance(campo, FileField)
    ]


@requiere_participante
def confirmacion(peticion, solicitud_id):
    """El acuse con el folio (pasos 13 y 14 del CU).

    Hace una sola cosa: dar el folio y decir qué sigue. Enseñaba además
    la lista de lo ya enviado, y dejó de hacerlo cuando existió
    `CU-EVT-003` — era la misma lista dos veces, y aquí sin la propuesta
    recién enviada, que era la que importaba en ese momento.

    Solo la ve quien la envió: el folio y el título de una propuesta ajena
    no son de nadie más. Se comprueba por el registro, que es lo único
    que ata una propuesta a una persona.
    """
    propuesta_enviada = get_object_or_404(
        Solicitud.objects.select_related("registro", "registro__convocatoria"),
        pk=solicitud_id,
    )
    if propuesta_enviada.registro.persona_id != peticion.user.pk:
        raise Http404("Esa propuesta no es tuya.")

    return render(
        peticion,
        "eventos/confirmacion.html",
        {
            "propuesta": propuesta_enviada,
            "convocatoria": propuesta_enviada.registro.convocatoria,
        },
    )


@requiere_participante
def mis_propuestas(peticion, convocatoria_id):
    """El listado de seguimiento (`CU-EVT-003`, pasos 1 y 2).

    Es la puerta del módulo: el "Registrarme" y el "Continuar" del
    catálogo llegan aquí (`ADR-0006`). Sin propuestas no es un error ni
    una pantalla distinta —es `E1`—, y la plantilla ofrece el formulario.

    No filtra ni ordena: el CU pide todas las de la edición y el orden lo
    fija el modelo. Un filtro aquí sería inventar trabajo para una lista
    que en la práctica tiene tres renglones.

    ``?nueva=<id>`` lo pone el acuse, y sirve para resaltar la fila de la
    propuesta que se acaba de enviar. Va en la barra de direcciones y no
    en la sesión a propósito: así el resalte se pierde al recargar, que
    es lo que tiene que pasar —una propuesta solo es nueva la primera vez
    que se mira—. Un valor inventado no resalta nada y no es un error:
    aquí solo decide qué fila lleva una clase.
    """
    convocatoria = _convocatoria_de_eventos(convocatoria_id)
    # Llegar aquí es haber salido del formulario: lo que quedara a medio
    # subir se descarta (política del 2026-09-03). Es idempotente, así
    # que no hace falta saber si había algo.
    en_espera.limpiar(convocatoria, peticion.user)
    return render(
        peticion,
        "eventos/mis_propuestas.html",
        {
            "convocatoria": convocatoria,
            "propuestas": seguimiento.propuestas_de(convocatoria, peticion.user),
            "recien_enviada": _entero_o_nada(peticion.GET.get("nueva")),
            # Para no ofrecer "Enviar otra propuesta" cuando el envío va a
            # rechazarla: es la misma pregunta que se hace U1 (`E1` de
            # `CU-EVT-002`), y quien la contesta es el mismo servicio.
            "abierta": solicitudes.admite_propuestas(convocatoria),
        },
    )


# ── El panel del administrador (`CU-EVT-007`, `008`, `009`, `011`) ──


@requiere_admin_feria
def propuestas(peticion, convocatoria_id):
    """La cola de propuestas, filtrable (`CU-EVT-007` y `CU-EVT-011`).

    Es la portada del módulo para quien administra: a donde apuntan el
    "Propuestas" de la barra lateral y la tarjeta del catálogo
    (`ADR-0006`).

    Los filtros van **en la consulta** y no en la plantilla, por lo mismo
    que en el catálogo de `FER`: lo que no se pide no debe llegar a la
    respuesta. Y viajan por `GET` para que una vista filtrada se pueda
    compartir por su dirección y se pueda volver atrás sin reenviar nada.

    Los conteos de los chips y los del resumen salen del **mismo**
    diccionario (`revision.resumen`): son la misma pregunta hecha con dos
    agrupaciones, y calcularlos por separado los dejaría discrepando en
    cuanto alguien tocara uno.
    """
    convocatoria = _convocatoria_de_eventos(convocatoria_id)

    estado = peticion.GET.get("estado", "")
    tipo = peticion.GET.get("tipo", "")
    categoria = peticion.GET.get("categoria", "")
    busqueda = (peticion.GET.get("q") or "").strip()

    numeros = revision.resumen(convocatoria)
    filas = revision.cola(
        convocatoria,
        estado=estado,
        tipo=tipo,
        categoria=categoria,
        busqueda=busqueda,
    )
    return render(
        peticion,
        "eventos/propuestas.html",
        {
            "convocatoria": convocatoria,
            "propuestas": filas,
            "resumen": numeros,
            "estado_activo": estado,
            "tipo_activo": tipo,
            "categoria_activa": categoria,
            "busqueda": busqueda,
            "tipos": catalogo.tipos(),
            "categorias": Solicitud.Categoria.choices,
            "chips": chips_de_estado(
                numeros["conteos"],
                Solicitud.Estado.choices,
                estado,
                busqueda,
                otros={"tipo": tipo, "categoria": categoria},
            ),
            # Su gemelo del otro lado: los mismos dos filtros, escondidos
            # en el formulario del buscador. Los tres controles de la barra
            # arrastran lo que los otros dos tengan puesto, que es lo que
            # hace que se puedan combinar sin JavaScript.
            "filtros_extra": [
                {"nombre": "tipo", "valor": tipo},
                {"nombre": "categoria", "valor": categoria},
            ],
            "url_limpia": reverse("eventos:propuestas", args=[convocatoria.pk]),
            "cuantas": filas.count(),
            "total": numeros["recibidas"],
            "hay_filtros": bool(estado or tipo or categoria or busqueda),
            "zona_admin": True,
        },
    )


def _entero_o_nada(crudo):
    """El id de la barra de direcciones, o ``None`` si no es un número.

    Nadie escribe esto a mano: lo pone el enlace del acuse. Si llega otra
    cosa es que alguien está tecleando en la URL, y la respuesta correcta
    a eso es no resaltar nada — no una página de error por un adorno.
    """
    try:
        return int(crudo)
    except (TypeError, ValueError):
        return None


@requiere_participante
def detalle(peticion, convocatoria_id, solicitud_id):
    """Una propuesta enviada, entera (`CU-EVT-003`, pasos 3 y 4).

    Solo lectura. Editar es `CU-EVT-004` y todavía no existe; mientras
    tanto, la pantalla dice qué hay que corregir pero no deja corregirlo,
    y lo dice con esas palabras en vez de enseñar un botón que no lleva a
    ninguna parte.

    Un 404 cubre las tres formas de no tener nada que enseñar —no existe,
    es de otra persona, o es de otra convocatoria—: distinguirlas
    confirmaría a un curioso que ese folio existe.
    """
    convocatoria = _convocatoria_de_eventos(convocatoria_id)
    propuesta_enviada = seguimiento.propuesta_de(
        convocatoria, peticion.user, solicitud_id
    )
    if propuesta_enviada is None:
        raise Http404("Esa propuesta no es tuya o no existe.")

    actividad = propuesta_enviada.actividad
    # `mi_propuesta.html` y no `detalle_propuesta.html`: ése es **A2**, el
    # expediente de quien administra (`CU-EVT-008`). Son dos pantallas de
    # la misma propuesta vistas desde los dos lados, y el nombre las
    # empareja con quien las abre — como `mis_propuestas.html`.
    return render(
        peticion,
        "eventos/mi_propuesta.html",
        {
            "convocatoria": convocatoria,
            "propuesta": propuesta_enviada,
            "actividad": actividad,
            # Lo propio del tipo, ya en bloques: la plantilla recorre y
            # pinta, y no sabe que existen ocho tipos distintos.
            "bloques": composicion.bloques_del_tipo(actividad),
            "documentos": actividad.documentos.all(),
        },
    )


@requiere_admin_feria
def detalle_propuesta(peticion, solicitud_id):
    """Revisar una propuesta y dictaminarla (`CU-EVT-008` y `CU-EVT-009`).

    Una sola pantalla para las dos cosas, y no dos: el detalle **es** la
    antesala del dictamen (`CU-EVT-008` paso 6), y separarlas obligaría a
    volver a leerlo todo en otra dirección para poder decidir.

    No lleva la convocatoria en la ruta: la propuesta ya sabe de cuál
    cuelga, y repetirla daría dos fuentes para lo mismo y una URL que
    puede mentir. Es la misma decisión que en `stands:detalle_solicitud`.

    Cuál de las **cuatro** acciones se ejecuta lo dice el ``name="accion"``
    del botón pulsado: las tres del dictamen y `corregir`, que es la
    corrección de redacción de `CU-EVT-008` (`servicios/edicion.py`).

    .. note:: Las dos modales del dictamen se abren desde el servidor

       Pedir cambios y rechazar piden un texto, y ese texto vive en una
       ventana modal —es lo que pide el prototipo y lo que evita tener un
       recuadro de motivo permanentemente abierto en un panel donde casi
       siempre se acepta—. Alpine la abre al pulsar el botón; sin
       JavaScript, el botón envía el formulario sin motivo, el servicio lo
       rechaza y **esta vista devuelve la pantalla con la modal abierta**
       (``modal_abierto``). Las dos rutas acaban en el mismo sitio, y la
       segunda cuesta una ida y vuelta.

       Lo mismo con el modo de edición: con JavaScript el botón desbloquea
       los recuadros en el acto, y sin él es un enlace a ``?editar=1``.
    """
    propuesta_en_revision = get_object_or_404(
        Solicitud.objects.select_related(*revision.RELACIONES), pk=solicitud_id
    )
    actividad = getattr(propuesta_en_revision, "actividad", None)
    personas = revision.personas_de(actividad)

    form = None
    accion = peticion.POST.get("accion", "") if peticion.method == "POST" else ""
    editando = peticion.GET.get("editar") == "1"

    if accion == "corregir":
        editando = True
        if _corregir(peticion, propuesta_en_revision, personas):
            return redirect(
                "eventos:detalle_propuesta", solicitud_id=propuesta_en_revision.pk
            )
        # Se volvió a leer del POST lo que se estaba escribiendo: la
        # pantalla tiene que devolver el texto corregido, no el guardado.
        personas = _personas_con_lo_tecleado(peticion, personas)
    elif peticion.method == "POST":
        form = DictamenForm(peticion.POST)
        if form.is_valid():
            respuesta = _dictaminar(peticion, propuesta_en_revision, form)
            if respuesta is not None:
                return respuesta
        else:
            messages.error(
                peticion,
                "Elige qué hacer con la propuesta: aceptarla, pedir cambios "
                "o rechazarla.",
            )

    if form is None:
        # La clasificación llega premarcada con lo que declaró quien
        # propuso: el paso 2 del caso de uso pide **sugerir** una opción,
        # no dejar el control en blanco para que alguien la teclee de cero.
        form = DictamenForm(
            initial={
                "categoria": propuesta_en_revision.categoria or None,
                "es_uady_confirmado": propuesta_en_revision.uady_sugerido,
            }
        )

    es_publicacion = bool(actividad) and catalogo.es_publicacion(actividad.tipo.nombre)
    return render(
        peticion,
        "eventos/detalle_propuesta.html",
        {
            "propuesta": propuesta_en_revision,
            "convocatoria": propuesta_en_revision.registro.convocatoria,
            "persona": propuesta_en_revision.persona,
            "actividad": actividad,
            # La fila hija, con los campos propios del tipo. La plantilla
            # no puede resolverla sola: qué atributo la alcanza depende
            # del `tipo`, y eso lo sabe el modelo.
            "detalle": actividad.detalle if actividad else None,
            # Los ocho tipos enseñan a su gente igual y solo cambian los
            # rótulos, así que la plantilla recibe una lista y no ocho
            # bloques condicionales.
            "personas": personas,
            "es_publicacion": es_publicacion,
            "documentos": revision.documentos_de(propuesta_en_revision),
            "form": form,
            # `A3`: volver sobre un dictamen emitido está reservado al
            # operador de la plataforma. La pantalla pregunta lo mismo que
            # el servicio, para no ofrecer un botón que va a rebotar.
            "puede_redictaminar": permisos.es_operador(peticion),
            # Corregir la redacción (`CU-EVT-008`). El tope se enseña
            # junto al recuadro: son 2 000 caracteres, o 4 000 en una
            # publicación, y descubrirlo al guardar es tarde.
            "editando": editando,
            # Cómo se llama la sinopsis en **este** tipo. La columna es la
            # misma para los ocho, pero en una presentación lo que ahí se
            # cuenta es el libro y en una charla la actividad: el rótulo
            # es lo único que lo dice.
            "etiqueta_sinopsis": (
                "Sinopsis de la publicación"
                if es_publicacion
                else "Sinopsis de la actividad"
            ),
            "tope_sinopsis": edicion.tope_de_sinopsis(propuesta_en_revision),
            "tope_semblanza": MAX_SEMBLANZA,
            # Cuál de las dos modales del dictamen tiene que salir
            # abierta. Vacío es "ninguna", que es el caso normal.
            "modal_abierto": _modal_que_reabrir(peticion, accion),
            "motivo_tecleado": peticion.POST.get("motivo", ""),
            "zona_admin": True,
        },
    )


def _modal_que_reabrir(peticion, accion: str) -> str:
    """Qué modal del dictamen sigue abierta tras un envío que no cuajó.

    Solo se llega aquí cuando el POST no acabó en redirección, es decir
    cuando el servicio rechazó la acción —típicamente porque el motivo
    venía vacío, que es exactamente lo que pasa sin JavaScript—. Dejarla
    cerrada mandaría el mensaje de error a una pantalla en la que no se ve
    dónde se escribe la respuesta.
    """
    if peticion.method != "POST":
        return ""
    return accion if accion in ("cambios", "rechazar") else ""


def _corregir(peticion, propuesta_en_revision, personas) -> bool:
    """Guarda la redacción corregida. Devuelve si se pudo (`CU-EVT-008`).

    Las columnas que se dejan escribir salen de ``personas`` y no del
    POST: es lo que impide que un formulario fabricado a mano toque una
    semblanza de otra persona o un campo que esta propuesta no tiene.
    """
    try:
        edicion.corregir(
            propuesta_en_revision,
            editor=peticion.user,
            sinopsis=peticion.POST.get("sinopsis", ""),
            semblanzas={
                quien.campo_semblanza: peticion.POST.get(quien.campo_semblanza, "")
                for quien in personas
            },
        )
    except edicion.CorreccionRechazada as negativa:
        messages.error(peticion, str(negativa))
        return False
    messages.success(
        peticion,
        "Guardado. La propuesta queda con el texto corregido; el dictamen "
        "no cambió.",
    )
    return True


def _personas_con_lo_tecleado(peticion, personas):
    """Las mismas personas, con la semblanza que se estaba escribiendo.

    Sin esto, un guardado que rebota vuelve con los textos de la base y
    quien corregía pierde lo que llevaba escrito — que es la manera más
    rápida de que nadie vuelva a usar el modo de edición.
    """
    return [
        replace(quien, semblanza=peticion.POST.get(quien.campo_semblanza, ""))
        for quien in personas
    ]


def _dictaminar(peticion, propuesta_en_revision, form):
    """Ejecuta la acción elegida. Devuelve a dónde ir, o ``None``.

    ``None`` significa "quédate en la pantalla y enseña el error": es lo
    que corresponde cuando el servicio rechaza el dictamen, porque lo que
    se escribió tiene que seguir ahí para poder corregirlo.

    Vive aparte de la vista para que ésta siga siendo lo que dice el
    contrato de capas —traducir HTTP a una llamada de servicio— y no una
    escalera de cuatro condicionales con avisos intercalados.
    """
    accion = form.cleaned_data["accion"]
    motivo = form.cleaned_data["motivo"]

    # `A3` paso 3 · la doble verificación. Se pide **antes** de llamar al
    # servicio porque no es una regla de negocio sino una barrera de la
    # interfaz: quien llama `dictamen.aceptar` desde `manage.py` ya sabe
    # lo que hace. Lo que sí es regla —quién puede rehacer un dictamen—
    # está en el servicio, y esto no lo sustituye.
    if propuesta_en_revision.esta_dictaminada and not form.cleaned_data["confirmar"]:
        messages.error(
            peticion,
            "Esta propuesta ya tiene dictamen. Marca la casilla de "
            "confirmación para cambiarlo.",
        )
        return None

    try:
        if accion == "aceptar":
            dictamen.aceptar(
                propuesta_en_revision,
                revisor=peticion.user,
                categoria=form.cleaned_data["categoria"],
                es_uady_confirmado=form.cleaned_data["es_uady_confirmado"],
            )
            messages.success(
                peticion,
                f"Aceptaste «{propuesta_en_revision.titulo_actividad}» como "
                f"{propuesta_en_revision.categoria_completa}. El resultado sale "
                "en el próximo lote de notificaciones.",
            )
        elif accion == "rechazar":
            dictamen.rechazar(
                propuesta_en_revision, revisor=peticion.user, motivo=motivo
            )
            messages.success(
                peticion,
                "Propuesta rechazada, con su motivo registrado. Se comunica "
                "en el próximo lote de resultados.",
            )
        else:
            dictamen.solicitar_cambios(
                propuesta_en_revision, revisor=peticion.user, mensaje=motivo
            )
            messages.success(
                peticion,
                "Cambios pedidos. Se le mandó tu nota por correo ahora mismo, "
                "para que le dé tiempo a corregir.",
            )
    except dictamen.DictamenRechazado as negativa:
        messages.error(peticion, str(negativa))
        return None

    return redirect("eventos:detalle_propuesta", solicitud_id=propuesta_en_revision.pk)


@requiere_participante
@xframe_options_sameorigin
def documento(peticion, documento_id):
    """Entrega un adjunto a quien tiene derecho a verlo (`ADR-0007`).

    Lleva `requiere_participante` y no `requiere_admin_feria` porque los
    dos públicos pasan por aquí: quien propuso, mirando lo que subió, y
    quien administra la feria, abriéndolo para dictaminar. Quién puede ver
    qué lo decide `archivos.puede_ver`.

    **Un 404 y no un 403 cuando no se puede.** Un 403 confirmaría que ese
    documento existe, que es justo lo que no hay que decirle a alguien que
    está probando identificadores.

    Y un 404 también cuando el archivo se perdió del almacén
    (`CU-EVT-008` `E1`): es otra incidencia —queda en el log como tal—
    pero la misma respuesta, porque la alternativa era un 500 que cortaba
    la revisión entera en vez de fallar solo ese enlace.
    """
    adjunto = get_object_or_404(
        Documento.objects.select_related("actividad__solicitud__registro"),
        pk=documento_id,
    )
    if not archivos.puede_ver(peticion, adjunto):
        raise Http404("No hay ningún documento con ese identificador.")
    try:
        return archivos.entregar(adjunto)
    except archivos.ArchivoNoDisponible as exc:
        raise Http404(str(exc)) from exc
