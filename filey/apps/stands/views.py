"""
Las pantallas de `STD` (U1, A1, A2).

Vistas delgadas: traducen HTTP a una llamada de `servicios/` y de vuelta.
Ninguna decide si una solicitud se puede enviar, si una convocatoria
admite registros o si un dictamen es válido — eso vive en los servicios,
donde un comando de `manage.py` también lo alcanza.

El control de acceso se importa, no se reimplementa: `requiere_participante`
para la zona del aplicante y `requiere_admin_feria` para el panel, que es
el que cuenta también al operador de la plataforma (`ADR-0005`).
"""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.formats import date_format

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.servicios import registros
from apps.ferias import permisos
from apps.ferias.permisos import requiere_admin_feria
from apps.registros.permisos import requiere_participante

from .formularios import (
    MAXIMO_SELLOS,
    AbonoForm,
    BasesForm,
    DictamenForm,
    DocumentoForm,
    EditorialForm,
    SellosForm,
)
from django.urls import reverse
from django.utils import timezone

from decimal import Decimal

from .models import (
    DescuentoAplicado,
    Documento,
    Editorial,
    Movimiento,
    Reserva,
    Solicitud,
    Stand,
)
from .servicios import (
    archivos,
    carrito,
    configuracion,
    mapa_json,
    dictamen,
    mapas,
    pagos,
    reservas,
    solicitudes,
)


def _convocatoria_de_stands(convocatoria_id: int) -> Convocatoria:
    """La convocatoria del prefijo, si de verdad es de stands.

    Un 404 y no un 403: una convocatoria de eventos **no existe** para
    este módulo, y decir "no tienes permiso" insinuaría que con otro
    permiso sí. No hace falta filtrar por feria — el schema ya lo hace
    (`ADR-0003`).
    """
    convocatoria = get_object_or_404(Convocatoria, pk=convocatoria_id)
    if convocatoria.tipo != TipoConvocatoria.STD:
        raise Http404("Esta convocatoria no es de venta de stands.")
    return convocatoria


def puede_reservarse(convocatoria) -> bool:
    """Si hoy se admite armar una selección y confirmarla.

    Son las dos condiciones que `servicios/reservas.py::crear` va a
    comprobar de todas formas —la convocatoria abierta y la edición
    operable—, preguntadas **antes** de pintar el botón. Sin esto, con
    la convocatoria cerrada el mapa sigue ofreciendo «Agregar» y el
    carrito «Confirmar la reserva», y el único freno es la excepción del
    servicio: un botón que solo puede fallar (`CU-STD-037` A1 dice que la
    vista no debe ofrecerlo).

    El mapa **sí se sigue enseñando** con la convocatoria cerrada: quien
    tiene una reserva en curso necesita poder consultarlo (`CU-STD-037`
    A1 paso 2). Lo que se retira son las acciones, no la información.
    """
    if convocatoria.estado != Convocatoria.Estado.ABIERTA:
        return False
    try:
        registros.exigir_edicion_operable()
    except registros.RegistroRechazado:
        return False
    return True


# ── El ruteador del expositor ─────────────────────────────────


#: Los cinco pasos del expositor, en orden. Los nombra el ruteador para
#: decidir a dónde entra cada quien, y la barra de pasos para pintarse:
#: dos listas se habrían separado al primer paso nuevo, y la barra
#: acabaría marcando un paso distinto del que se está viendo.
PASOS = (
    ("solicitud", "Solicitud", "stands:solicitud"),
    ("revision", "Revisión", None),
    ("espacios", "Espacios", "stands:mapa"),
    ("confirmacion", "Confirmación", "stands:carrito"),
    ("cuenta", "Pago", "stands:cuenta"),
)


def paso_actual(convocatoria, persona) -> str:
    """En qué paso del flujo está esta persona (`CU-STD-003`).

    Una sola función responde la pregunta para las dos cosas que la
    hacen: el ruteador —"¿a dónde la mando?"— y la barra de pasos
    —"¿dónde le digo que está?"—. Separarlas dejaría a alguien viendo el
    mapa con la barra marcando "Solicitud".

    El orden de las preguntas es el del flujo al revés, de lo más
    avanzado a lo menos: quien tiene reserva ya pasó por todo lo demás.
    """
    if reservas.reserva_viva_de(convocatoria, persona) is not None:
        return "cuenta"
    if solicitudes.habilitada_para_reservar(convocatoria, persona) is not None:
        return "espacios"
    viva = solicitudes.solicitud_viva(convocatoria, persona)
    if viva is not None and viva.estado == Solicitud.Estado.PENDIENTE:
        return "revision"
    return "solicitud"


@requiere_participante
def inicio(peticion, convocatoria_id):
    """La puerta del módulo: manda a cada quien a donde le toca.

    Es a donde apunta el "Registrarme" del catálogo (`ADR-0006`), y por
    eso es un `redirect` y no una pantalla: entrar a una convocatoria de
    stands no es un destino, es reanudar un trámite que empezó antes.
    Quien ya tiene reserva no vuelve a ver el mapa, y quien está
    aprobado no vuelve a ver su solicitud.

    Las pantallas siguen alcanzables por su URL —se puede volver a leer
    la solicitud enviada—; lo que decide esto es **dónde se entra**.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    destino = {
        "cuenta": "stands:cuenta",
        "espacios": "stands:mapa",
    }.get(paso_actual(convocatoria, peticion.user), "stands:solicitud")
    return redirect(destino, convocatoria_id=convocatoria.pk)


# ── U1 · Portal del aplicante ─────────────────────────────────


@requiere_participante
def solicitud(peticion, convocatoria_id):
    """La solicitud de expositor: enviarla, seguirla y corregirla.

    Es **una sola pantalla para los cinco estados** (`CU-STD-001`,
    `002`, `003`), y no cinco pantallas, porque para el aplicante es una
    sola cosa —"mi solicitud"— y lo que cambia es qué puede hacer con
    ella. `CU-STD-003` la describe como un ruteador; aquí el ruteo es el
    estado del formulario, no un `redirect`.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    persona = peticion.user

    viva = solicitudes.solicitud_viva(convocatoria, persona)
    ultima = viva or solicitudes.ultima_solicitud(convocatoria, persona)
    editorial = Editorial.objects.filter(persona=persona).first()
    sellos_actuales = (
        list(editorial.sellos.prefetch_related("cartas")) if editorial else []
    )

    # Se puede capturar cuando no hay ninguna solicitud, cuando la última
    # fue rechazada (`RN-22`: se vuelve a aplicar) o cuando piden
    # cambios. Con una `pendiente` o una `aceptada`, la pantalla es de
    # solo lectura.
    editable = ultima is None or ultima.estado in (
        Solicitud.Estado.RECHAZADA,
        Solicitud.Estado.CAMBIOS_SOLICITADOS,
    )
    puede_operar = convocatoria.estado == Convocatoria.Estado.ABIERTA

    if peticion.method == "POST" and editable and puede_operar:
        respuesta, formularios = _guardar_solicitud(
            peticion, convocatoria, editorial, ultima
        )
        if respuesta is not None:
            return respuesta
        # Sin respuesta hay errores: se vuelve a pintar con los mismos
        # formularios ligados, que es lo que conserva lo capturado.
    else:
        formularios = {
            "form_editorial": EditorialForm(instance=editorial, persona=persona),
            "form_sellos": SellosForm(
                sellos_actuales=[s.nombre for s in sellos_actuales]
            ),
            "form_documentos": DocumentoForm(
                ya_hay_documentos=editorial is not None
                and editorial.documentos.exists()
            ),
            "form_bases": BasesForm(),
        }

    return render(
        peticion,
        "stands/solicitud.html",
        {
            "convocatoria": convocatoria,
            "solicitud": ultima,
            "editorial": editorial,
            # Solo los generales: las cartas se enseñan junto a su sello.
            "documentos": (
                editorial.documentos.filter(sello__isnull=True) if editorial else []
            ),
            "sellos_actuales": sellos_actuales,
            "maximo_sellos": MAXIMO_SELLOS,
            "editable": editable and puede_operar,
            "convocatoria_abierta": puede_operar,
            "es_reenvio": ultima is not None
            and ultima.estado == Solicitud.Estado.CAMBIOS_SOLICITADOS,
            # La barra de pasos dice dónde va **el trámite**, no en qué
            # plantilla está: una solicitud aceptada la enseña ya en
            # "Espacios", que es lo que le toca hacer a continuación.
            "paso": paso_actual(convocatoria, persona),
            **formularios,
        },
    )


def _guardar_solicitud(peticion, convocatoria, editorial, ultima):
    """El POST de U1.

    Devuelve ``(respuesta, formularios)``. Con ``respuesta`` a ``None``
    hay errores y la vista vuelve a pintar con esos mismos formularios
    ligados, que es lo que conserva lo capturado (E1).

    Separado de la vista porque son dos caminos —primer envío y reenvío—
    que comparten la captura entera y solo difieren en la última línea.
    """
    form_editorial = EditorialForm(
        peticion.POST, instance=editorial, persona=peticion.user
    )
    form_sellos = SellosForm(peticion.POST, peticion.FILES)
    form_documentos = DocumentoForm(
        peticion.POST,
        peticion.FILES,
        ya_hay_documentos=editorial is not None and editorial.documentos.exists(),
    )
    form_bases = BasesForm(peticion.POST)
    formularios = {
        "form_editorial": form_editorial,
        "form_sellos": form_sellos,
        "form_documentos": form_documentos,
        "form_bases": form_bases,
    }

    # Los cuatro se validan siempre —y no con cortocircuito— para que los
    # errores salgan todos de una vez. Enterarse de tres cosas en tres
    # envíos es lo que hace abandonar un formulario largo.
    validos = [f.is_valid() for f in formularios.values()]
    if not all(validos):
        # E1 de `CU-STD-001` y de `CU-STD-002`: se señala lo que falta y
        # no se envía nada. Se dice **cuántos** son: "revisa los campos"
        # obliga a recorrer un formulario de treinta a ciegas.
        cuantos = sum(len(f.errors) for f in formularios.values())
        aviso = (
            f"No enviamos tu solicitud: falta {cuantos} campo por corregir."
            if cuantos == 1
            else f"No enviamos tu solicitud: faltan {cuantos} campos por corregir."
        )
        # Y hay que decir lo de los archivos. Un `<input type="file">` no
        # se puede repoblar desde el servidor —ningún navegador acepta un
        # `value` ahí, y es una defensa contra que una página se lleve
        # ficheros sin permiso—, así que lo adjuntado en este envío **sí**
        # se pierde. Callarlo deja a alguien reenviando sin entender por
        # qué le sigue faltando la constancia.
        if peticion.FILES:
            aviso += " Vuelve a adjuntar los archivos: el navegador no los conserva."
        messages.error(peticion, aviso)
        return None, formularios

    es_reenvio = (
        ultima is not None and ultima.estado == Solicitud.Estado.CAMBIOS_SOLICITADOS
    )

    # Todo o nada. Sin esta transacción, un envío rechazado a última hora
    # —la convocatoria se cerró entre el GET y el POST— dejaría la ficha
    # y los documentos guardados y ninguna solicitud: un expediente que
    # existe a medias y que nadie va a revisar.
    #
    # Lo **escrito** no se pierde igualmente (`CU-STD-001`, "en fallo"):
    # lo conservan los formularios ligados, que vuelven a la plantilla.
    # Lo **adjuntado** sí, y no hay forma de evitarlo sin guardar el
    # archivo antes de validarlo; por eso se avisa arriba.
    try:
        with transaction.atomic():
            ficha = form_editorial.save(commit=False)
            ficha.persona = peticion.user
            solicitudes.guardar_editorial(ficha, sellos=form_sellos.declarados())
            _guardar_documentos(ficha, form_documentos)
            if es_reenvio:
                solicitudes.reenviar_solicitud(ultima)
            else:
                solicitudes.enviar_solicitud(
                    convocatoria=convocatoria, persona=peticion.user, editorial=ficha
                )
    except ValidationError as exc:
        for campo, errores in exc.message_dict.items():
            for error in errores:
                form_editorial.add_error(
                    campo if campo in form_editorial.fields else None, error
                )
        return None, formularios
    except solicitudes.EnvioRechazado as exc:
        messages.error(peticion, str(exc))
        return None, formularios

    messages.success(
        peticion,
        "Solicitud reenviada. Te avisamos por correo en cuanto la revisemos."
        if es_reenvio
        else "Solicitud enviada. Te avisamos por correo en cuanto la revisemos.",
    )
    return redirect("stands:solicitud", convocatoria_id=convocatoria.pk), formularios


def _guardar_documentos(editorial, form):
    """Los adjuntos generales cuelgan de la editorial, no de la solicitud.

    Es lo que permite reenviar corrigiendo solo un teléfono sin volver a
    subir la constancia fiscal (`CU-STD-002` A1). Uno nuevo del mismo
    tipo **sustituye** al anterior: la ficha tiene una constancia fiscal,
    no un historial de constancias.

    Las cartas de representación no pasan por aquí: cada una cuelga de su
    sello y las guarda `servicios/solicitudes.py::guardar_editorial`.
    """
    for campo, tipo in form.TIPOS.items():
        archivo = form.cleaned_data.get(campo)
        if not archivo:
            continue
        editorial.documentos.filter(tipo=tipo, sello__isnull=True).delete()
        editorial.documentos.create(
            tipo=tipo, archivo=archivo, nombre_original=archivo.name[:255]
        )


# ── A1 y A2 · Panel del administrador ─────────────────────────


@requiere_admin_feria
def solicitudes_de_la_convocatoria(peticion, convocatoria_id):
    """La cola de revisión (`CU-STD-004`).

    El filtro va en la consulta y no en la plantilla por lo mismo que en
    el catálogo de `FER`: lo que no se pide no debe llegar a la
    respuesta.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)

    estado = peticion.GET.get("estado", "")
    busqueda = (peticion.GET.get("q") or "").strip()

    cola = Solicitud.objects.filter(
        registro__convocatoria=convocatoria
    ).select_related("editorial", "registro__persona")
    if estado in Solicitud.Estado.values:
        cola = cola.filter(estado=estado)
    if busqueda:
        # Los dos nombres: el de la ficha viva y el de la fotografía. Si
        # la editorial se renombró después de enviar, buscar solo por uno
        # deja de encontrar la solicitud que la pantalla sí muestra.
        cola = cola.filter(
            Q(editorial__nombre__icontains=busqueda)
            | Q(datos_editorial__nombre__icontains=busqueda)
        )

    return render(
        peticion,
        "stands/solicitudes.html",
        {
            "convocatoria": convocatoria,
            "solicitudes": cola,
            "estado_activo": estado,
            "busqueda": busqueda,
            "estados": Solicitud.Estado.choices,
            "hay_filtros": bool(estado or busqueda),
            "zona_admin": True,
        },
    )


@requiere_admin_feria
def detalle_solicitud(peticion, solicitud_id):
    """Revisar y resolver una solicitud (`CU-STD-005` a `007`).

    Lo que se muestra es la **fotografía** (`datos_editorial`), no la
    ficha viva: es lo que la persona envió y lo que se dictamina. Si la
    editorial corrigió su ficha después, aquí no se ve — y es lo
    correcto (`RN-22`).
    """
    solicitud_obj = get_object_or_404(
        Solicitud.objects.select_related(
            "editorial", "registro__convocatoria", "registro__persona", "revisado_por"
        ),
        pk=solicitud_id,
    )

    if peticion.method == "POST":
        form = DictamenForm(peticion.POST)
        if form.is_valid():
            accion = form.cleaned_data["accion"]
            motivo = form.cleaned_data["motivo"]
            try:
                if accion == "aceptar":
                    dictamen.aceptar(solicitud_obj, revisor=peticion.user)
                    messages.success(
                        peticion,
                        f"Aceptaste a {solicitud_obj.datos_editorial.get('nombre', 'la editorial')}. "
                        "Ya puede reservar stands y se le avisó por correo.",
                    )
                elif accion == "rechazar":
                    dictamen.rechazar(solicitud_obj, revisor=peticion.user, motivo=motivo)
                    messages.success(
                        peticion,
                        "Solicitud rechazada. Se le avisó por correo y puede "
                        "volver a aplicar mientras la convocatoria siga abierta.",
                    )
                else:
                    dictamen.solicitar_cambios(
                        solicitud_obj, revisor=peticion.user, motivo=motivo
                    )
                    messages.success(
                        peticion,
                        "Cambios pedidos. Se le mandó tu nota por correo; la "
                        "solicitud vuelve a la cola cuando la corrija.",
                    )
                return redirect("stands:detalle_solicitud", solicitud_id=solicitud_obj.pk)
            except dictamen.DictamenRechazado as exc:
                messages.error(peticion, str(exc))
        else:
            messages.error(
                peticion,
                "Elige qué hacer con la solicitud: aceptarla, pedir cambios "
                "o rechazarla.",
            )
    else:
        form = DictamenForm()

    return render(
        peticion,
        "stands/detalle_solicitud.html",
        {
            "solicitud": solicitud_obj,
            "convocatoria": solicitud_obj.registro.convocatoria,
            "datos": solicitud_obj.datos_editorial,
            "sellos": solicitud_obj.sellos,
            # Los documentos cuelgan de la editorial: son los vigentes.
            "documentos": solicitud_obj.editorial.documentos.all(),
            "notificaciones": solicitud_obj.notificaciones.all(),
            "form": form,
            "zona_admin": True,
        },
    )


@requiere_admin_feria
def panel(peticion, convocatoria_id):
    """La portada del módulo dentro de una convocatoria.

    Responde a una sola pregunta —**¿qué necesita de mí hoy?**— y, si no
    hay nada, lo dice y se aparta. Todo lo demás de la pantalla es
    contexto para leer esa respuesta.

    Por eso los números van en dos grupos y no en una fila de seis: los
    que **piden una acción** enlazan a donde se actúa, y los que
    describen **cómo va** no enlazan a ninguna parte. Mezclarlos deja
    «3 solicitudes por revisar» con el mismo peso que «$2 500 el m²», que
    es un ajuste y no una tarea.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    ajustes = configuracion.de_la_convocatoria(convocatoria)
    mapa = mapas.mapa_de(convocatoria)

    vivas = reservas.de_la_convocatoria(convocatoria).filter(
        estado__in=Reserva.VIVAS
    )
    return render(
        peticion,
        "stands/panel.html",
        {
            "convocatoria": convocatoria,
            "configuracion": ajustes,
            "mapa": mapa,
            "pendientes": Solicitud.objects.filter(
                registro__convocatoria=convocatoria, estado__in=Solicitud.VIVOS
            ).count(),
            "por_validar": Movimiento.objects.filter(
                reserva__registro__convocatoria=convocatoria,
                estado=Movimiento.Estado.PENDIENTE,
            ).count(),
            "vencidas": vivas.filter(
                estado=Reserva.Estado.POR_CONFIRMAR,
                fecha_vencimiento_anticipo__lt=timezone.now(),
            ).count(),
            "aceptadas": Solicitud.objects.filter(
                registro__convocatoria=convocatoria,
                estado=Solicitud.Estado.ACEPTADA,
            ).count(),
            "reservas_vivas": vivas.count(),
            **_ocupacion(mapa, vivas),
            # Lo que impide operar. Se dice aquí porque es donde alguien
            # llega antes de encontrarse la pantalla vacía.
            "falta_precio": not ajustes.costo_m2,
            "falta_mapa": mapa is None,
            "zona_admin": True,
        },
    )


def _ocupacion(mapa, reservas_vivas) -> dict:
    """Cuánto recinto se ha vendido, **en metros y no en espacios**.

    Es la diferencia que hace útil esta cifra: vender treinta espacios
    chicos no es vender tres grandes, y lo que sigue el dinero es la
    superficie. Contar cajas daría una barra que avanza rápido mientras
    la recaudación no se mueve.

    Los porcentajes se calculan aquí y no en la plantilla porque una
    división por cero en una plantilla de Django no falla: devuelve vacío
    y la barra se queda plana sin que nadie sepa por qué.
    """
    if mapa is None:
        return {"hay_ocupacion": False}

    por_estado = {Stand.Estado.DISPONIBLE: 0, Stand.Estado.RESERVADO: 0,
                  Stand.Estado.OCUPADO: 0}
    for stand in mapa.stands.select_related("mapa"):
        por_estado[stand.estado] += stand.metros_cuadrados
    total = sum(por_estado.values())
    if not total:
        return {"hay_ocupacion": False}

    comprometido = sum(
        (r.monto_total for r in reservas_vivas), start=Decimal("0.00")
    )
    cobrado = sum(
        (r.monto_abonado for r in reservas_vivas), start=Decimal("0.00")
    )
    return {
        "hay_ocupacion": True,
        "m2_total": total,
        "m2_libres": por_estado[Stand.Estado.DISPONIBLE],
        "tramos": [
            # El orden es el del recorrido: lo que queda por vender
            # primero, porque es lo que hay que mirar.
            ("disponible", "Disponible", por_estado[Stand.Estado.DISPONIBLE]),
            ("reservado", "Reservado", por_estado[Stand.Estado.RESERVADO]),
            ("ocupado", "Pagado", por_estado[Stand.Estado.OCUPADO]),
        ],
        "porcentajes": {
            clave: round(metros * 100 / total, 1)
            for clave, _, metros in [
                ("disponible", "", por_estado[Stand.Estado.DISPONIBLE]),
                ("reservado", "", por_estado[Stand.Estado.RESERVADO]),
                ("ocupado", "", por_estado[Stand.Estado.OCUPADO]),
            ]
        },
        "comprometido": comprometido,
        "cobrado": cobrado,
    }


# ── La entrega de archivos ────────────────────────────────────


@requiere_participante
def documento(peticion, documento_id):
    """Entrega un adjunto a quien tiene derecho a verlo (`ADR-0007`).

    Lleva `requiere_participante` y no `requiere_admin_feria` porque los
    dos públicos pasan por aquí: la editorial revisando lo que subió y
    quien administra la feria revisándolo para dictaminar. Quién puede
    ver qué lo decide `archivos.puede_ver`.

    **Un 404 y no un 403 cuando no se puede.** Un 403 confirmaría que ese
    documento existe, que es justo lo que no queremos decirle a alguien
    que está probando identificadores.
    """
    adjunto = get_object_or_404(
        Documento.objects.select_related("editorial"), pk=documento_id
    )
    if not archivos.puede_ver(peticion, adjunto):
        raise Http404("No hay ningún documento con ese identificador.")
    return archivos.entregar(adjunto)


# ── El mapa del showfloor ─────────────────────────────────────


def _datos_del_mapa(convocatoria, *, con_detalle, mios=()):
    """El JSON que consume el canvas (`CU-STD-037` y `CU-STD-038`).

    Un 404 cuando la convocatoria no tiene mapa: para el canvas es que no
    hay nada que pedir. Quien enseña "el mapa todavía no está listo" es
    la pantalla, que ya lo sabe antes de montar el `<iframe>`.
    """
    mapa = mapas.mapa_de(convocatoria)
    if mapa is None:
        raise Http404("Esta convocatoria no tiene mapa.")
    costo_m2 = configuracion.de_la_convocatoria(convocatoria).costo_m2
    datos = mapa_json.para_el_canvas(
        mapa, costo_m2=costo_m2, con_detalle=con_detalle, mios=mios
    )
    # `private`: el recorte de `RN-09` depende de quién pregunta, así que
    # esta respuesta **no la puede cachear un intermediario** — serviría
    # la carga del administrador a un aplicante.
    respuesta = JsonResponse(datos)
    respuesta["Cache-Control"] = "private, no-store"
    return respuesta


@requiere_participante
def mapa(peticion, convocatoria_id):
    """El showfloor, como lo ve quien aplica (`CU-STD-009`).

    `RN-09`: los estados `reservado` y `ocupado` llegan colapsados en uno
    solo. Quien aplica no necesita distinguirlos —no puede reservar
    ninguno de los dos— y separarlos diría quién va ganando el reparto
    del recinto.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    # `RN-23`: con una reserva en pie no hay nada que elegir — su
    # editorial ya tiene la suya, y el paso siguiente es pagarla. Se
    # manda a la cuenta en vez de enseñar un mapa donde cada clic
    # acabaría en el mismo aviso.
    if reservas.reserva_viva_de(convocatoria, peticion.user) is not None:
        return redirect("stands:cuenta", convocatoria_id=convocatoria.pk)
    # `RN-16`: solo una solicitud aceptada habilita a reservar. `E1`.
    editorial = solicitudes.habilitada_para_reservar(convocatoria, peticion.user)
    mapa = mapas.mapa_de(convocatoria) if editorial else None

    return render(
        peticion,
        "stands/mapa.html",
        {
            # La plantilla del mapa la comparten `CU-STD-009` y `032`, así
            # que el layout no puede ser fijo: quien aplica no tiene panel
            # de administración y no debe ver su barra lateral.
            "plantilla_base": "layouts/panel.html",
            "convocatoria": convocatoria,
            "editorial": editorial,
            "habilitada": editorial is not None,
            "mapa": mapa,
            # De dónde saca el canvas sus datos. La plantilla no arma
            # URLs: si el nombre de la ruta cambia, esto falla al pintar y
            # no en silencio dentro de un `fetch`.
            "url_datos": (
                reverse("stands:mapa_datos", args=[convocatoria.pk]) if mapa else None
            ),
            "puede_reservar": puede_reservarse(convocatoria),
            "costo_m2": (
                configuracion.de_la_convocatoria(convocatoria).costo_m2
                if mapa
                else None
            ),
            "paso": "espacios",
            # El carrito llega pintado con la página: sin esto la columna
            # de la derecha nace vacía y se llena de golpe al primer
            # intercambio de htmx, que se lee como si se hubiera perdido
            # lo elegido antes.
            **(_contexto_del_carrito(peticion, convocatoria) if mapa else {}),
        },
    )


@requiere_participante
def mapa_datos(peticion, convocatoria_id):
    """`CU-STD-037` · el mapa que ve quien aplica.

    `reservado` y `ocupado` llegan colapsados (`RN-09`), y el recorte
    ocurre **antes de serializar**: si el estado real viajara aquí
    —aunque el canvas no lo pintara— cualquiera con las herramientas de
    desarrollo abiertas vería qué editorial tiene apartado qué espacio.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    if solicitudes.habilitada_para_reservar(convocatoria, peticion.user) is None:
        raise Http404("Todavía no puedes consultar el mapa.")
    # Sus propios espacios viajan distinguibles (`CU-STD-013`): es lo que
    # convierte el plano en "dónde me tocó". Para quien todavía no ha
    # reservado el conjunto está vacío y el mapa sale igual que siempre.
    return _datos_del_mapa(
        convocatoria, con_detalle=False, mios=_mis_claves(convocatoria, peticion.user)
    )


def _mis_claves(convocatoria, persona) -> list[str]:
    """Las claves de los espacios de la reserva viva de esta persona."""
    reserva = reservas.reserva_viva_de(convocatoria, persona)
    if reserva is None:
        return []
    return [linea.stand.clave for linea in reserva.lineas.all()]


@requiere_admin_feria
def mapa_datos_completo(peticion, convocatoria_id):
    """`CU-STD-038` · el mapa sin censura, para quien administra (`RN-18`)."""
    return _datos_del_mapa(
        _convocatoria_de_stands(convocatoria_id), con_detalle=True
    )


@requiere_participante
def detalle_stand(peticion, convocatoria_id, clave):
    """Dimensiones, superficie, precio y qué incluye (`CU-STD-010`).

    Pantalla propia y no un panel dentro del mapa: sin JavaScript el mapa
    es un SVG con enlaces, y el enlace tiene que llevar a algún sitio
    (regla 6). Con JavaScript, lo mismo se puede traer con htmx sin
    cambiar nada de aquí.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    # Dos públicos, como el mapa. Quien administra llega aquí desde
    # `CU-STD-032` y no tiene solicitud aceptada: exigirla dejaba su modal
    # cargando para siempre.
    es_admin = permisos.administra(peticion)
    if (
        not es_admin
        and solicitudes.habilitada_para_reservar(convocatoria, peticion.user) is None
    ):
        raise Http404("Todavía no puedes consultar los espacios.")

    mapa_showfloor = mapas.mapa_de(convocatoria)
    if mapa_showfloor is None:
        raise Http404("Esta convocatoria no tiene mapa.")
    stand = get_object_or_404(
        mapa_showfloor.stands.select_related("mapa"), clave=clave
    )

    costo_m2 = configuracion.de_la_convocatoria(convocatoria).costo_m2
    # A htmx se le da **solo el cuerpo**: es el modal del mapa pidiendo el
    # detalle, y devolverle la página entera metería otro chasis dentro
    # del diálogo. La misma vista sirve las dos, así que la pantalla y el
    # modal no pueden decir cifras distintas.
    en_modal = peticion.headers.get("HX-Request") == "true"
    return render(
        peticion,
        (
            "stands/parciales/detalle_stand.html"
            if en_modal
            else "stands/detalle_stand.html"
        ),
        {
            "convocatoria": convocatoria,
            "stand": stand,
            "metros_cuadrados": stand.metros_cuadrados,
            "precio": stand.precio(costo_m2),
            "costo_m2": costo_m2,
            "libre": stand.esta_libre,
            "metros_por_celda": mapa_showfloor.metros_por_celda,
            "en_modal": en_modal,
            "zona_admin": es_admin,
            # Dos motivos para no ofrecer «agregar», y los dos se ven
            # desde aquí: la convocatoria cerrada (`CU-STD-037` A1 paso
            # 3) y tener ya una reserva viva (`RN-23`). El segundo importa
            # porque este mismo detalle se abre desde el mapa de consulta
            # de la cuenta: sin él, un espacio libre ofrecería meterse a
            # un carrito que ya no lleva a ninguna parte.
            "puede_reservar": (
                not es_admin
                and puede_reservarse(convocatoria)
                and reservas.reserva_viva_de(convocatoria, peticion.user) is None
            ),
            # Un espacio de su propia reserva no es "un espacio tomado":
            # es el suyo, y decírselo así en el mapa de su reserva sería
            # una mentira con forma de aviso.
            "es_mio": (
                not es_admin
                and clave in _mis_claves(convocatoria, peticion.user)
            ),
            # `CU-STD-032`: quien administra ve **quién reservó y cuánto
            # debe**. `RN-09` lo prohíbe para quien aplica, y por eso la
            # consulta ni se hace si no administra: lo que no se pide no
            # puede acabar en la respuesta por un descuido de plantilla.
            "reserva": _reserva_del_espacio(stand) if es_admin else None,
        },
    )


def _reserva_del_espacio(stand: Stand):
    """La reserva viva que tiene apartado este espacio, si la hay.

    Un stand pertenece como mucho a una: `RN-10` y `RN-12` lo garantizan
    —vencer no libera— así que la primera es la única.
    """
    linea = (
        stand.lineas_de_reserva.filter(reserva__estado__in=Reserva.VIVAS)
        .select_related("reserva__editorial", "reserva__registro__persona")
        .first()
    )
    return linea.reserva if linea else None


@requiere_admin_feria
def mapa_completo(peticion, convocatoria_id):
    """El showfloor sin censura, para quien administra (`CU-STD-032`).

    `RN-18`: aquí sí se distinguen los tres estados de `RN-10`. Es la
    diferencia entera con `CU-STD-009`, y son la misma plantilla con un
    parámetro, no dos pantallas: dos plantillas se separan al primer
    cambio y acaban dibujando mapas distintos.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    mapa = mapas.mapa_de(convocatoria)
    return render(
        peticion,
        "stands/mapa.html",
        {
            "plantilla_base": "layouts/admin.html",
            "convocatoria": convocatoria,
            "habilitada": True,
            "zona_admin": True,
            "mapa": mapa,
            "url_datos": (
                reverse("stands:mapa_datos_completo", args=[convocatoria.pk])
                if mapa
                else None
            ),
            "costo_m2": (
                configuracion.de_la_convocatoria(convocatoria).costo_m2
                if mapa
                else None
            ),
        },
    )


# ── U · El carrito y la reserva ───────────────────────────────


def _exige_habilitacion(peticion, convocatoria):
    """`RN-16`. Un 404 y no un 403 en las pantallas de reserva.

    Un 403 confirmaría que ese carrito y esa reserva existen para alguien;
    quien no está habilitado no tiene por qué enterarse de nada.
    """
    editorial = solicitudes.habilitada_para_reservar(convocatoria, peticion.user)
    if editorial is None:
        raise Http404("Todavía no puedes reservar espacios.")
    return editorial


def _contexto_del_carrito(peticion, convocatoria):
    """Lo que el carrito necesita para pintarse, venga de donde venga.

    Lo comparten la pantalla del mapa —que lo trae al cargar— y el
    parcial que htmx intercambia. Que salga de una sola función es lo que
    evita que el carrito de al lado del mapa y el de la pantalla de
    confirmar digan cifras distintas.
    """
    mapa = mapas.mapa_de(convocatoria)
    ajustes = configuracion.de_la_convocatoria(convocatoria)
    contenido = carrito.contenido(
        peticion.session, convocatoria, mapa, ajustes.costo_m2
    )
    total, _ = reservas.cotizar(
        convocatoria, [linea.stand for linea in contenido.lineas if linea.disponible]
    )
    return {
        "convocatoria": convocatoria,
        "contenido": contenido,
        "total": total,
        "anticipo": total * ajustes.porcentaje_anticipo / 100,
        "puede_reservar": puede_reservarse(convocatoria),
    }


def _mover_el_carrito(peticion, convocatoria) -> None:
    """Agregar, quitar o vaciar, según lo que diga el POST.

    Las tres van por POST aunque solo toquen la sesión: un GET que la
    modifica lo dispara cualquier precarga del navegador, y la selección
    se movería sola.
    """
    clave = (peticion.POST.get("clave") or "").strip()
    accion = peticion.POST.get("accion")
    if accion == "agregar" and clave:
        carrito.agregar(peticion.session, convocatoria, clave)
    elif accion == "quitar" and clave:
        carrito.quitar(peticion.session, convocatoria, clave)
    elif accion == "vaciar":
        carrito.vaciar(peticion.session, convocatoria)


@requiere_participante
def carrito_lateral(peticion, convocatoria_id):
    """El carrito de al lado del mapa (`CU-STD-011`).

    Devuelve **solo el carrito**, para que htmx lo intercambie sin
    recargar la página. Es lo que permite que agregar un espacio no te
    saque del mapa: recargar aquí costaría volver a bajar los 39 MB del
    canvas y perder el zoom donde estabas.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    _exige_habilitacion(peticion, convocatoria)
    if mapas.mapa_de(convocatoria) is None:
        raise Http404("Esta convocatoria no tiene mapa.")

    # `RN-23`. Aquí la salida es `HX-Redirect` y no un `redirect`: htmx
    # seguiría el 302 y metería la página entera dentro de la columna del
    # carrito. La cabecera le dice al navegador que cambie de página.
    if reservas.reserva_viva_de(convocatoria, peticion.user) is not None:
        respuesta = HttpResponse(status=204)
        respuesta["HX-Redirect"] = reverse(
            "stands:cuenta", args=[convocatoria.pk]
        )
        return respuesta

    if peticion.method == "POST":
        _mover_el_carrito(peticion, convocatoria)

    return render(
        peticion,
        "stands/parciales/carrito_lateral.html",
        _contexto_del_carrito(peticion, convocatoria),
    )


@requiere_participante
def carrito_de_stands(peticion, convocatoria_id):
    """La selección de trabajo (`CU-STD-011`).

    Agregar y quitar van por POST aunque no cambien nada persistente: un
    GET que modifica la sesión lo dispara cualquier precarga del
    navegador, y la selección se movería sola.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    _exige_habilitacion(peticion, convocatoria)
    if reservas.reserva_viva_de(convocatoria, peticion.user) is not None:
        return redirect("stands:cuenta", convocatoria_id=convocatoria.pk)

    if peticion.method == "POST":
        clave = (peticion.POST.get("clave") or "").strip()
        accion = peticion.POST.get("accion")
        if accion == "agregar" and clave:
            carrito.agregar(peticion.session, convocatoria, clave)
        elif accion == "quitar" and clave:
            carrito.quitar(peticion.session, convocatoria, clave)
        elif accion == "vaciar":
            carrito.vaciar(peticion.session, convocatoria)
        return redirect("stands:carrito", convocatoria_id=convocatoria.pk)

    mapa = mapas.mapa_de(convocatoria)
    if mapa is None:
        raise Http404("Esta convocatoria no tiene mapa.")

    ajustes = configuracion.de_la_convocatoria(convocatoria)
    contenido = carrito.contenido(
        peticion.session, convocatoria, mapa, ajustes.costo_m2
    )
    total, renglones = reservas.cotizar(
        convocatoria, [linea.stand for linea in contenido.lineas if linea.disponible]
    )
    porcentaje_pronto_pago = reservas.pronto_pago_vigente(convocatoria)
    return render(
        peticion,
        "stands/carrito.html",
        {
            "convocatoria": convocatoria,
            "contenido": contenido,
            "costo_m2": ajustes.costo_m2,
            "total": total,
            "renglones": renglones,
            "anticipo": total * ajustes.porcentaje_anticipo / 100,
            "porcentaje_anticipo": ajustes.porcentaje_anticipo,
            "plazo_dias": ajustes.plazo_reserva_dias,
            "fecha_pronto_pago": ajustes.fecha_limite_pronto_pago,
            # `CU-STD-012` paso 3: la nota del pronto pago dice **cuánto
            # falta** para el corte y **a cuánto sube** si se deja pasar.
            # Con la fecha sola, "después se retira" no se puede sopesar.
            "porcentaje_pronto_pago": porcentaje_pronto_pago,
            "dias_pronto_pago": _dias_hasta(ajustes.fecha_limite_pronto_pago),
            "total_sin_pronto_pago": (
                renglones[0].subtotal if porcentaje_pronto_pago else None
            ),
            "puede_reservar": puede_reservarse(convocatoria),
            "paso": "confirmacion",
        },
    )


def _dias_hasta(fecha) -> int | None:
    """Cuántos días naturales faltan para esa fecha, o ``None``.

    Cero cuando es hoy —el último día cuenta— y ``None`` cuando ya pasó
    o no hay fecha: quien llama no debe tener que distinguir "quedan -3
    días" de "no hay campaña".
    """
    if fecha is None:
        return None
    faltan = (fecha - timezone.localdate()).days
    return faltan if faltan >= 0 else None


@requiere_participante
def reservar(peticion, convocatoria_id):
    """Formaliza la reserva (`CU-STD-012`).

    Solo POST: es la escritura de la vertical, y llegar aquí por un
    enlace —o por volver atrás— crearía una reserva que nadie pidió.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    _exige_habilitacion(peticion, convocatoria)
    if peticion.method != "POST":
        return redirect("stands:carrito", convocatoria_id=convocatoria.pk)

    claves = carrito.claves_en(peticion.session, convocatoria)
    try:
        reserva = reservas.crear(
            convocatoria=convocatoria, persona=peticion.user, claves=claves
        )
    except reservas.YaTieneReserva as exc:
        # No es un error del que recuperarse: es que ya está un paso más
        # adelante. Se le lleva a su cuenta con el aviso, y el carrito se
        # vacía — lo que tuviera elegido ya no puede reservarlo.
        carrito.vaciar(peticion.session, convocatoria)
        messages.info(peticion, str(exc))
        return redirect("stands:cuenta", convocatoria_id=convocatoria.pk)
    except reservas.HayEspaciosTomados as exc:
        # Se sacan del carrito por ella: reintentar tiene que costar un
        # clic, no volver a quitar uno por uno lo que ya se perdió.
        for clave in exc.claves:
            carrito.quitar(peticion.session, convocatoria, clave)
        messages.error(peticion, str(exc))
        return redirect("stands:carrito", convocatoria_id=convocatoria.pk)
    except reservas.ReservaRechazada as exc:
        messages.error(peticion, str(exc))
        return redirect("stands:carrito", convocatoria_id=convocatoria.pk)

    carrito.vaciar(peticion.session, convocatoria)
    # La fecha se formatea con `date_format` y no con `strftime`: `%B` sale
    # del locale del sistema —que en el servidor es el de C— y escribía
    # "01 de December" en una pantalla en español.
    messages.success(
        peticion,
        f"Reservaste {reserva.lineas.count()} espacio"
        f"{'s' if reserva.lineas.count() != 1 else ''}. "
        "Tienes hasta el "
        f"{date_format(reserva.fecha_vencimiento_anticipo, r'j \d\e F')} "
        "para cubrir el anticipo.",
    )
    # `CU-STD-012` paso 8: se le deja en las instrucciones de pago, que
    # es lo único que tiene que hacer a continuación.
    return redirect(
        reverse("stands:cuenta", args=[convocatoria.pk]) + "?ver=pagos"
    )


@requiere_participante
def cuenta(peticion, convocatoria_id):
    """Mi cuenta: qué debo, hasta cuándo, y lo que he abonado.

    Es el último paso del flujo (`CU-STD-013` y `CU-STD-017`) y el
    único que no se abandona: quien tiene una reserva vuelve aquí cada
    vez que entra, hasta que la termine de pagar.

    Una sola reserva viva (`RN-23`), y debajo el historial de las
    canceladas — que no es relleno: explica por qué unos espacios
    estuvieron apartados y ya no lo están.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    _exige_habilitacion(peticion, convocatoria)

    reserva = reservas.reserva_viva_de(convocatoria, peticion.user)
    cerradas = [
        r
        for r in reservas.reservas_de(convocatoria, peticion.user)
        if r.estado not in Reserva.VIVAS
    ]
    ajustes = configuracion.de_la_convocatoria(convocatoria)
    desglose = reservas.desglose_de(reserva) if reserva else []
    mapa = mapas.mapa_de(convocatoria) if reserva else None
    return render(
        peticion,
        "stands/cuenta.html",
        {
            "convocatoria": convocatoria,
            "reserva": reserva,
            "desglose": desglose,
            "vencida": reserva.esta_vencida if reserva else False,
            # `CU-STD-014` paso 2: cuánto falta para llegar al anticipo,
            # que es la cifra que decide si alguien paga hoy. No es el
            # saldo: es lo mínimo para que la reserva deje de peligrar.
            "falta_para_el_anticipo": (
                max(reserva.anticipo - reserva.monto_abonado, Decimal("0.00"))
                if reserva
                else Decimal("0.00")
            ),
            # El desglose se recalcula con la tarifa de hoy y el total
            # está congelado (`RN-01`). Si discrepan hay que decirlo aquí
            # también, no solo en la pantalla del administrador.
            "recalculado": desglose[-1].subtotal if desglose else None,
            "movimientos": (
                list(reserva.movimientos.select_related("comprobante"))
                if reserva
                else []
            ),
            "en_revision": (
                sum(
                    (
                        m.monto
                        for m in reserva.movimientos.all()
                        if m.estado == Movimiento.Estado.PENDIENTE
                    ),
                    start=Decimal("0.00"),
                )
                if reserva
                else Decimal("0.00")
            ),
            "form_abono": AbonoForm(),
            "ajustes": ajustes,
            "porcentaje_pagado": _porcentaje_pagado(reserva),
            # `CU-STD-013` paso 5. Solo mientras el descuento siga vivo:
            # una vez retirado no hay nada que conservar.
            "pronto_pago": _aviso_de_pronto_pago(reserva, ajustes),
            "cerradas": cerradas,
            # La tercera pestaña: el plano en modo consulta (`CU-STD-013`
            # paso 2, "en mapa y/o lista"). Va por `?ver=` y no por
            # JavaScript **a propósito**: el canvas pesa 39 MB, y con
            # pestañas de cliente se descargarían en cada visita a la
            # cuenta aunque nadie abriera el mapa.
            "ver": _pestana(peticion),
            "mapa": mapa,
            "url_datos": (
                reverse("stands:mapa_datos", args=[convocatoria.pk])
                if mapa
                else None
            ),
            "mis_claves": (
                [linea.stand.clave for linea in reserva.lineas.all()]
                if reserva
                else []
            ),
            "paso": "cuenta",
        },
    )


#: Las pestañas de la cuenta, y la que se enseña si no dicen cuál.
PESTANAS = ("resumen", "pagos", "mapa")


def _pestana(peticion) -> str:
    """Qué pestaña pidieron, o `resumen`.

    Se valida contra la lista en vez de confiar en el parámetro: llega de
    la URL, y con él se elige qué bloque se pinta.
    """
    pedida = peticion.GET.get("ver", "")
    return pedida if pedida in PESTANAS else "resumen"


def _aviso_de_pronto_pago(reserva, ajustes) -> dict | None:
    """Lo que hay que decir del pronto pago, o ``None`` si no hay nada.

    `CU-STD-013` paso 5 pide las dos cifras juntas: **cuánto queda** para
    la fecha de corte y **a cuánto sube** el total si se deja pasar. Con
    la fecha sola nadie puede sopesar si le conviene adelantar el pago.
    """
    if reserva is None:
        return None
    descuento = reserva.descuentos.filter(
        tipo=DescuentoAplicado.Tipo.PRONTO_PAGO
    ).first()
    if descuento is None or ajustes.fecha_limite_pronto_pago is None:
        return None
    # Ya liquidada: el descuento se consolidó y no hay riesgo que avisar.
    if reserva.monto_abonado >= reserva.monto_total:
        return None
    return {
        "porcentaje": descuento.porcentaje,
        "fecha": ajustes.fecha_limite_pronto_pago,
        "dias": _dias_hasta(ajustes.fecha_limite_pronto_pago),
        "vencido": _dias_hasta(ajustes.fecha_limite_pronto_pago) is None,
        "total_sin_el": reservas.total_sin_pronto_pago(reserva),
    }


def _porcentaje_pagado(reserva) -> int:
    """Cuánto del total lleva cubierto, para la barra de progreso.

    Entero y acotado a 100: la barra no puede pasar del 100%, y un
    decimal en una barra de 200 píxeles no dice nada que el entero no
    diga. Con total cero —una reserva de una convocatoria sin precio
    puesto— se cuenta como cubierta: no hay nada que pagar.
    """
    if reserva is None:
        return 0
    if reserva.monto_total <= 0:
        return 100
    return min(100, int(reserva.monto_abonado * 100 / reserva.monto_total))


@requiere_participante
def registrar_abono(peticion, convocatoria_id):
    """Reporta un pago hecho fuera del sistema (`CU-STD-016`).

    Solo POST, como `reservar`: es una escritura, y llegar por un enlace
    dejaría un movimiento que nadie reportó.

    El formulario valida la forma —monto positivo, método de la lista,
    archivo admisible— y `servicios/pagos.py` la regla: que quepa en lo
    pendiente y que la reserva admita abonos. Los errores del servicio
    salen como aviso y no bajo un campo porque no son de un campo: son
    del estado de la cuenta.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    _exige_habilitacion(peticion, convocatoria)
    # De vuelta a la pestaña de pagos: el resultado —el aviso y el abono
    # nuevo en el historial— está ahí, no en el resumen.
    destino = redirect(
        reverse("stands:cuenta", args=[convocatoria.pk]) + "?ver=pagos"
    )
    if peticion.method != "POST":
        return destino

    reserva = reservas.reserva_viva_de(convocatoria, peticion.user)
    if reserva is None:
        raise Http404("No tienes ninguna reserva que abonar.")

    form = AbonoForm(peticion.POST, peticion.FILES)
    if not form.is_valid():
        # El primer error de cada campo, y no el formulario repintado: el
        # de abonar es un formulario de tres campos dentro de una pantalla
        # que es sobre todo cifras, y repintarla entera para señalar uno
        # obliga a buscar dónde quedó.
        for errores in form.errors.values():
            messages.error(peticion, errores[0])
        return destino

    try:
        movimiento = pagos.registrar(
            reserva=reserva,
            persona=peticion.user,
            monto=form.cleaned_data["monto"],
            metodo=form.cleaned_data["metodo"],
            archivo=form.cleaned_data.get("comprobante"),
        )
    except pagos.PagoRechazado as exc:
        messages.error(peticion, str(exc))
        return destino

    messages.success(
        peticion,
        f"Registramos tu abono de ${movimiento.monto}. "
        "Lo revisamos y te avisamos en cuanto quede validado.",
    )
    return destino


@requiere_admin_feria
def reservas_de_la_convocatoria(peticion, convocatoria_id):
    """La lista de todas las reservas, filtrable (`CU-STD-028`)."""
    convocatoria = _convocatoria_de_stands(convocatoria_id)

    estado = peticion.GET.get("estado", "")
    busqueda = (peticion.GET.get("q") or "").strip()

    cola = reservas.de_la_convocatoria(convocatoria)
    if estado == "vencidas":
        # No es un estado del modelo: es `por_confirmar` con el plazo
        # pasado (`RN-12`). Se filtra en la consulta y no en la plantilla
        # por lo mismo de siempre — lo que no se pide no debe llegar.
        cola = cola.filter(
            estado=Reserva.Estado.POR_CONFIRMAR,
            fecha_vencimiento_anticipo__lt=timezone.now(),
        )
    elif estado in Reserva.Estado.values:
        cola = cola.filter(estado=estado)
    if busqueda:
        cola = cola.filter(editorial__nombre__icontains=busqueda)

    return render(
        peticion,
        "stands/reservas.html",
        {
            "convocatoria": convocatoria,
            "reservas": cola,
            "estado_activo": estado,
            "busqueda": busqueda,
            "estados": Reserva.Estado.choices,
            "hay_filtros": bool(estado or busqueda),
            "zona_admin": True,
        },
    )


@requiere_admin_feria
def detalle_reserva(peticion, reserva_id):
    """El detalle de una reserva (`CU-STD-029`)."""
    reserva = get_object_or_404(
        Reserva.objects.select_related(
            "editorial", "registro__persona", "registro__convocatoria"
        ).prefetch_related("lineas__stand__mapa", "descuentos"),
        pk=reserva_id,
    )
    return render(
        peticion,
        "stands/detalle_reserva.html",
        {
            "convocatoria": reserva.registro.convocatoria,
            "reserva": reserva,
            "desglose": reservas.desglose_de(reserva),
            "vencida": reserva.esta_vencida,
            "zona_admin": True,
        },
    )
