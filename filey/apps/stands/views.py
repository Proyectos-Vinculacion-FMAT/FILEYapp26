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
from django.db.models import Count, Q
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.formats import date_format
from django.utils.http import urlencode

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.servicios import registros
from apps.ferias import permisos
from apps.ferias.permisos import requiere_admin_feria
from apps.registros.permisos import requiere_participante

from .formularios import (
    MAXIMO_SELLOS,
    AbonoForm,
    AbonoManualForm,
    BasesForm,
    CancelacionForm,
    ConfiguracionForm,
    DescuentoEspecialForm,
    DictamenForm,
    FechaDeCorteForm,
    ProrrogaForm,
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

    La tercera condición es el precio. Sin `costo_m2` toda la reserva
    valdría cero, y una de esas no admite abonos ni puede confirmarse
    nunca: `crear` la rechaza, y aquí se retira el botón para que nadie
    llegue hasta ese aviso.
    """
    if convocatoria.estado != Convocatoria.Estado.ABIERTA:
        return False
    if not configuracion.de_la_convocatoria(convocatoria).costo_m2:
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
            # Solo los de la ficha: las cartas se enseñan junto a su
            # sello, y un comprobante de pago no es parte de la solicitud.
            "documentos": (
                editorial.documentos.filter(tipo__in=Documento.DE_LA_FICHA)
                if editorial
                else []
            ),
            # Los que **se enviaron**, con su carta, para el resumen de
            # solo lectura. Distinto de `sellos_actuales`, que es la ficha
            # viva y alimenta el formulario.
            "sellos_enviados": (
                solicitudes.sellos_con_carta(ultima) if ultima else []
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
def ajustes_de_la_convocatoria(peticion, convocatoria_id):
    """A10 · Los ajustes de la convocatoria (`CU-STD-034`).

    Lo que cuesta un espacio y dónde se paga, en una pantalla. Hasta hoy
    esto vivía en `/f/<slug>/django-admin/`, que era provisional por dos
    motivos: el actor era el equipo técnico (`is_staff`) y no quien
    administra la feria, y la pantalla no podía explicar lo que un
    cambio de precio **no** hace.

    .. important:: Cambiar el precio no mueve lo ya reservado

       `RN-01`: `Reserva.monto_total` se congela al reservar. Subir el
       `costo_m2` a mitad de campaña cambia lo que costará la siguiente
       reserva, no lo que aceptó quien reservó ayer. La pantalla lo dice
       porque es la duda que trae quien entra aquí.

    El mapa **no** se toca desde aquí: importarlo reemplaza el showfloor
    entero y es del operador de la plataforma (`ADR-0005`).
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    ajustes = configuracion.de_la_convocatoria(convocatoria)

    if peticion.method == "POST":
        form = ConfiguracionForm(peticion.POST, instance=ajustes)
        if form.is_valid():
            # Por el servicio y no `form.save()` a secas: guardar y anotar
            # qué cambió son una sola operación, y una vista no es el
            # sitio donde eso se decide.
            configuracion.guardar(form=form, administrador=peticion.user)
            messages.success(
                peticion,
                "Guardamos la configuración. Las reservas que ya existen "
                "conservan el precio que aceptaron.",
            )
            return redirect(
                "stands:configuracion", convocatoria_id=convocatoria.pk
            )
        messages.error(
            peticion, "No guardamos nada: revisa los campos señalados."
        )
    else:
        form = ConfiguracionForm(instance=ajustes)

    return render(
        peticion,
        "stands/configuracion.html",
        {
            "convocatoria": convocatoria,
            "configuracion": ajustes,
            "form": form,
            # El mapa se enseña aquí aunque no se edite: quien administra
            # tiene que poder ver si hay showfloor cargado sin ir a
            # buscarlo a otra pantalla.
            "mapa": mapas.mapa_de(convocatoria),
            # Lo que impide operar, dicho donde se arregla.
            "falta_precio": not ajustes.costo_m2,
            "falta_cuenta": not ajustes.tiene_datos_bancarios,
            "reservas_vivas": reservas.de_la_convocatoria(convocatoria)
            .filter(estado__in=Reserva.VIVAS)
            .count(),
            "zona_admin": True,
        },
    )


def _chips_de_estado(
    conteos: dict,
    opciones,
    activo: str,
    busqueda: str,
    *,
    total: int | None = None,
    etiqueta_vacio: str = "Todas",
) -> list:
    """La barra de estados de una cola, con cuántas hay en cada uno.

    Sustituye al `<select>` que había: son cinco opciones excluyentes y
    conocidas, y con la lista desplegada **se ve el vocabulario entero
    sin abrir nada** (ley de Hick, tope de siete). Además cada una dice
    su número, que es lo que quien revisa viene a saber —"¿qué necesita
    de mí hoy?"— sin tener que filtrar para averiguarlo.

    Elegir un estado **es** filtrar: cada chip es un enlace, no un
    control que después haya que enviar. Un clic en vez de dos, y el
    filtro sigue siendo compartible por GET.

    :param conteos: ``{valor_del_estado: cuántas}``. Las que no aparecen
        salen en cero, y eso es información: "Rechazadas 0" dice algo
        distinto de que la fila no exista.
    :param opciones: pares ``(valor, etiqueta)``, incluida cualquier
        pseudo-columna como las reservas vencidas.
    :param busqueda: se arrastra en el enlace. Cambiar de estado no debe
        borrar en silencio lo que alguien tecleó.
    :param total: cuántas hay en «Todas», si no es la suma de los
        conteos. Hace falta cuando alguna opción no es un estado sino un
        recorte de otro —las reservas vencidas son `por_confirmar` con el
        plazo pasado (`RN-12`)—: sumarla contaría dos veces las mismas.
    :param etiqueta_vacio: cómo se llama el primer chip, el que no lleva
        parámetro. Es «Todas» en las colas que no filtran de entrada, y
        la cola de pagos lo cambia porque **entrar ahí ya es filtrar**:
        su estado natural es «por validar», que es el trabajo del día.
    """
    filtro = {"q": busqueda} if busqueda else {}
    chips = [
        {
            "etiqueta": etiqueta_vacio,
            "cuantas": sum(conteos.values()) if total is None else total,
            "activo": not activo,
            "parametros": urlencode(filtro),
        }
    ]
    for valor, etiqueta in opciones:
        chips.append(
            {
                "etiqueta": etiqueta,
                "cuantas": conteos.get(valor, 0),
                "activo": valor == activo,
                "parametros": urlencode({**filtro, "estado": valor}),
            }
        )
    return chips


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

    # Los conteos salen de **todas** las solicitudes, no de la lista
    # filtrada: un chip que dijera "0" solo porque hay otro filtro puesto
    # no sirve para navegar entre estados.
    conteos = {
        fila["estado"]: fila["n"]
        for fila in Solicitud.objects.filter(registro__convocatoria=convocatoria)
        .values("estado")
        .annotate(n=Count("id"))
    }
    return render(
        peticion,
        "stands/solicitudes.html",
        {
            "convocatoria": convocatoria,
            "solicitudes": cola,
            "estado_activo": estado,
            "busqueda": busqueda,
            "chips": _chips_de_estado(
                conteos, Solicitud.Estado.choices, estado, busqueda
            ),
            "url_limpia": reverse("stands:solicitudes", args=[convocatoria.pk]),
            "cuantas": cola.count(),
            "total": sum(conteos.values()),
            "hay_filtros": bool(estado or busqueda),
            "zona_admin": True,
        },
    )


@requiere_admin_feria
def pagos_por_validar(peticion, convocatoria_id):
    """A5 · La cola de pagos por validar (`CU-STD-018`).

    Es **transversal**: cruza todas las reservas de la convocatoria,
    porque quien coteja el banco lo hace por lotes y no reserva por
    reserva. La otra puerta a la misma acción es el detalle de una
    reserva (A4), y las dos llaman al mismo servicio.

    **Entrar aquí ya es filtrar.** La pantalla se llama "pagos por
    validar" y su estado natural es `pendiente_validacion`; los chips
    sirven para mirar lo ya resuelto, no al revés.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)

    pedido = peticion.GET.get("estado", "")
    busqueda = (peticion.GET.get("q") or "").strip()

    # Sin estado en la URL, la cola son los pendientes. `todos` es la
    # salida explícita a la vista completa.
    if pedido == TODOS:
        filtro = None
    elif pedido in Movimiento.Estado.values:
        filtro = pedido
    else:
        filtro = Movimiento.Estado.PENDIENTE

    cola = pagos.de_la_convocatoria(convocatoria, estado=filtro)
    if busqueda:
        cola = cola.filter(reserva__editorial__nombre__icontains=busqueda)

    conteos = {
        fila["estado"]: fila["n"]
        for fila in pagos.de_la_convocatoria(convocatoria)
        .values("estado")
        .annotate(n=Count("id"))
    }
    chips = _chips_de_estado(
        conteos,
        [
            (Movimiento.Estado.VALIDADO, "Validados"),
            (Movimiento.Estado.RECHAZADO, "Rechazados"),
            (TODOS, "Todos"),
        ],
        pedido,
        busqueda,
        etiqueta_vacio="Por validar",
    )
    # El primer chip cuenta los pendientes, no la suma: es el filtro que
    # aplica cuando no se pide nada.
    chips[0]["cuantas"] = conteos.get(Movimiento.Estado.PENDIENTE, 0)
    chips[-1]["cuantas"] = sum(conteos.values())

    return render(
        peticion,
        "stands/pagos.html",
        {
            "convocatoria": convocatoria,
            "movimientos": cola,
            "estado_activo": pedido,
            "busqueda": busqueda,
            "chips": chips,
            "url_limpia": reverse("stands:pagos", args=[convocatoria.pk]),
            "cuantas": cola.count(),
            "total": sum(conteos.values()),
            "hay_filtros": bool(pedido or busqueda),
            "zona_admin": True,
        },
    )


@requiere_admin_feria
def movimiento(peticion, movimiento_id):
    """El detalle de un abono, y las dos decisiones sobre él (`CU-STD-018`).

    Una sola vista para el modal y para la pantalla suelta, como el
    detalle de un espacio: htmx pide **solo el cuerpo** y sin JavaScript
    el mismo enlace abre la página entera. Así las dos no pueden decir
    cifras distintas del mismo abono.

    El POST no pasa por htmx a propósito: validar mueve dinero y cambia
    el estado de una reserva, así que la respuesta es una recarga con su
    aviso y la cola ya al día. Un intercambio parcial dejaría la fila
    vieja en pantalla al lado del aviso de que se validó.

    A dónde vuelve lo dice `desde`, porque `CU-STD-018` tiene **dos
    puertas**: la cola de A5 y el detalle de la reserva (A4). No es una
    URL de vuelta sino una de dos palabras conocidas: una URL en un
    parámetro es un redirector abierto, y ésta se alcanza con sesión de
    administración.
    """
    abono = get_object_or_404(
        Movimiento.objects.select_related(
            "reserva__editorial",
            "reserva__registro__persona",
            "reserva__registro__convocatoria",
            "comprobante",
            "registrado_por",
            "validado_por",
        ),
        pk=movimiento_id,
    )
    convocatoria = abono.reserva.registro.convocatoria
    desde = (
        "reserva"
        if (peticion.POST.get("desde") or peticion.GET.get("desde")) == "reserva"
        else "cola"
    )
    destino = (
        redirect("stands:detalle_reserva", reserva_id=abono.reserva_id)
        if desde == "reserva"
        else redirect("stands:pagos", convocatoria_id=convocatoria.pk)
    )

    if peticion.method == "POST":
        accion = peticion.POST.get("accion")
        motivo = (peticion.POST.get("motivo") or "").strip()
        try:
            if accion == "validar":
                reserva = pagos.validar(movimiento=abono, administrador=peticion.user)
                messages.success(
                    peticion,
                    f"Validaste ${abono.monto} de "
                    f"{abono.reserva.editorial.nombre}. La reserva quedó "
                    f"{reserva.get_estado_display().lower()}.",
                )
            elif accion == "rechazar":
                pagos.rechazar(
                    movimiento=abono, administrador=peticion.user, motivo=motivo
                )
                messages.success(
                    peticion,
                    "Rechazaste el abono. El saldo de la reserva no cambió y "
                    "la editorial lo verá en su historial.",
                )
            else:
                messages.error(
                    peticion, "Elige qué hacer con el abono: validarlo o rechazarlo."
                )
        except pagos.PagoRechazado as exc:
            messages.error(peticion, str(exc))
        return destino

    en_modal = peticion.headers.get("HX-Request") == "true"
    return render(
        peticion,
        (
            "stands/parciales/movimiento.html"
            if en_modal
            else "stands/movimiento.html"
        ),
        {
            "convocatoria": convocatoria,
            "movimiento": abono,
            "reserva": abono.reserva,
            "proyeccion": _proyeccion_del_abono(abono),
            "desde": desde,
            "url_volver": destino.url,
            "en_modal": en_modal,
            "zona_admin": True,
        },
    )


def _proyeccion_del_abono(abono) -> dict | None:
    """Qué le haría este abono a la reserva, si se validara.

    `CU-STD-018` paso 8: al validar, el sistema evalúa si el nuevo saldo
    cruza el 50% (`RN-13`) o el 100% (`RN-14`). Quien valida tiene que
    poder **ver esa consecuencia antes de pulsar**, y no calcularla de
    cabeza con tres cifras sueltas en pantalla.

    Devuelve ``None`` para un abono ya resuelto: ahí no hay nada que
    proyectar, lo que hubo se cuenta en el historial.

    Los porcentajes son para dibujar la barra, así que se acotan a 100 y
    el tramo de este abono empieza donde acaba lo ya validado — un abono
    que se pasa del total no puede pintar más allá del extremo.
    """
    if abono.estado != Movimiento.Estado.PENDIENTE:
        return None

    reserva = abono.reserva
    total = reserva.monto_total
    abonado = reserva.monto_abonado
    despues = abonado + abono.monto
    resultante = pagos.estado_si_se_valida(reserva, abono.monto)

    def porcentaje(cantidad):
        if total <= 0:
            return 100
        return min(100, int(cantidad * 100 / total))

    ya = porcentaje(abonado)
    return {
        "abonado": abonado,
        "despues": despues,
        "total": total,
        "pct_abonado": ya,
        "pct_este": min(100 - ya, porcentaje(despues) - ya),
        # El umbral que confirma, de la convocatoria y no de la plantilla
        # (`RN-02`): es la misma cifra con la que `_estado_para` decide,
        # así que la marca de la barra no puede caer donde no confirma.
        "umbral": reserva.configuracion.porcentaje_anticipo,
        "estado_resultante": Reserva.Estado(resultante).label,
        "cambia": resultante != reserva.estado,
    }


@requiere_admin_feria
def expositores_de_la_convocatoria(peticion, convocatoria_id):
    """A6 · Quién está habilitado para reservar (`CU-STD-030`).

    No es un listado de editoriales: son las que tienen la solicitud
    **aceptada** (`RN-16`), que es lo que las convierte en expositores.
    Por eso la lista vacía no dice "no hay editoriales" sino que manda a
    la bandeja de solicitudes (`E1`): si no hay ninguna, es que falta
    dictaminar, no que nadie haya aplicado.

    Sin chips de estado, al revés que las otras tres listas del panel:
    aquí solo hay un estado por definición. Lo que sí lleva es el
    buscador, porque el paso 4 del caso de uso es localizar a uno
    concreto para atenderlo por teléfono.
    """
    convocatoria = _convocatoria_de_stands(convocatoria_id)
    busqueda = (peticion.GET.get("q") or "").strip()

    cola = solicitudes.expositores_de(convocatoria)
    total = cola.count()
    if busqueda:
        # Por nombre o por correo. **No por RFC**: no existe como
        # columna — la información fiscal llega como constancia adjunta,
        # y buscar dentro de un PDF no es buscar.
        cola = cola.filter(
            Q(editorial__nombre__icontains=busqueda)
            | Q(editorial__correo_electronico__icontains=busqueda)
            | Q(registro__persona__correo__icontains=busqueda)
        )

    return render(
        peticion,
        "stands/expositores.html",
        {
            "convocatoria": convocatoria,
            "expositores": cola,
            "busqueda": busqueda,
            "url_limpia": reverse("stands:expositores", args=[convocatoria.pk]),
            "cuantas": cola.count(),
            "total": total,
            "hay_filtros": bool(busqueda),
            "zona_admin": True,
        },
    )


@requiere_admin_feria
def detalle_expositor(peticion, editorial_id):
    """A7 · El expediente de un expositor (`CU-STD-031`).

    **El alcance es la feria, no la convocatoria**, y es lo que hace útil
    la pantalla: la misma editorial puede haber aplicado a la general y a
    la de un pabellón, y quien atiende una llamada necesita ver las dos
    (`RN-19`). Por eso la URL no lleva convocatoria, como el detalle de
    una solicitud o de una reserva.
    """
    editorial = get_object_or_404(
        Editorial.objects.select_related("persona"), pk=editorial_id
    )
    expediente = solicitudes.expediente_de(editorial)
    # Para volver: la convocatoria de su solicitud más reciente. Sin
    # ninguna —una ficha llenada y nunca enviada— se vuelve al panel.
    ultima = expediente["solicitudes"].first()
    return render(
        peticion,
        "stands/detalle_expositor.html",
        {
            **expediente,
            "convocatoria": ultima.registro.convocatoria if ultima else None,
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
            # Cada sello con su carta al lado: quien dictamina tiene que
            # poder comprobar **cuál autoriza cuál** (`RN-17`), y en una
            # lista donde todas se llaman «Carta de representación» eso no
            # se puede.
            "sellos": solicitudes.sellos_con_carta(solicitud_obj),
            # Los documentos cuelgan de la editorial: son los vigentes.
            # Solo los de la ficha — las cartas van con su sello y los
            # comprobantes de pago son de una reserva, no del expediente.
            "documentos": solicitud_obj.editorial.documentos.filter(
                tipo__in=Documento.DE_LA_FICHA
            ),
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
    es_admin = permisos.ve_como_admin(peticion)
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
            # La misma función que usa el tope de `pagos.registrar`: lo
            # que la pantalla enseña como «en revisión» y lo que el
            # servicio descuenta del hueco tienen que ser la misma cifra.
            "en_revision": (
                pagos.suma_en_revision(reserva) if reserva else Decimal("0.00")
            ),
            "form_abono": AbonoForm(),
            "ajustes": ajustes,
            "porcentaje_pagado": _porcentaje_pagado(reserva),
            # Dónde cae el umbral que confirma la reserva (`RN-02`). Va
            # al contexto y no escrito en la plantilla porque el
            # porcentaje es **de la convocatoria** y `A10` lo deja
            # cambiar: con un 50 fijo, una convocatoria al 40% enseñaba
            # la marca en un sitio y confirmaba en otro.
            "umbral": ajustes.porcentaje_anticipo,
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


#: El chip que sale del filtro por estado y enseña la cola entera. No es
#: un estado de `Movimiento`: es la ausencia de filtro, dicha con nombre
#: para que quepa en una URL compartible.
TODOS = "todos"


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
        raise Http404("No tienes ninguna reserva a la que registrarle un pago.")

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
        f"Registramos tu pago de ${movimiento.monto}. "
        "Te avisamos en cuanto lo validemos contra el banco.",
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

    todas = reservas.de_la_convocatoria(convocatoria)
    conteos = {
        fila["estado"]: fila["n"]
        for fila in todas.values("estado").annotate(n=Count("id"))
    }
    # `vencidas` no es un estado del modelo sino `por_confirmar` con el
    # plazo pasado (`RN-12`), así que se cuenta aparte y **no** suma al
    # total: sus reservas ya están contadas en «Por confirmar».
    vencidas = todas.filter(
        estado=Reserva.Estado.POR_CONFIRMAR,
        fecha_vencimiento_anticipo__lt=timezone.now(),
    ).count()
    chips = _chips_de_estado(
        {**conteos, "vencidas": vencidas},
        # «Vencidas» a secas: es la etiqueta más larga de las seis y la
        # columna «Vence» de la tabla ya dice de qué van. Con la barra en
        # un solo renglón, cada palabra de más empuja a las demás.
        [*Reserva.Estado.choices, ("vencidas", "Vencidas")],
        estado,
        busqueda,
        total=sum(conteos.values()),
    )

    return render(
        peticion,
        "stands/reservas.html",
        {
            "convocatoria": convocatoria,
            # `con_saldo` al final y no en `de_la_convocatoria`: la
            # consulta de los chips agrupa por estado, y con la unión de
            # los movimientos encima contaría filas de más.
            "reservas": reservas.con_saldo(cola),
            "estado_activo": estado,
            "busqueda": busqueda,
            "chips": chips,
            "url_limpia": reverse("stands:reservas", args=[convocatoria.pk]),
            "cuantas": cola.count(),
            "total": sum(conteos.values()),
            "hay_filtros": bool(estado or busqueda),
            "zona_admin": True,
        },
    )


@requiere_admin_feria
def detalle_reserva(peticion, reserva_id):
    """A4 · El expediente de una reserva y lo que se hace con él.

    `CU-STD-029` la describe como **vista contenedor**: no es una ficha de
    consulta sino el sitio desde el que se opera una reserva. De aquí
    cuelgan el historial de abonos (paso 5) y, del paso 6, las dos
    acciones que hoy existen —asentar un abono manual (`CU-STD-019`) y
    aplicar o retirar un descuento especial (`CU-STD-020`)—. Validar un
    abono suelto (`CU-STD-018`) se abre desde el historial, en el mismo
    modal que la cola de A5.

    Todas las escrituras son un POST con `accion` y vuelven aquí (patrón
    *post/redirect/get*): mueven dinero o cierran la reserva, y recargar
    una pantalla con el POST puesto asentaría el abono dos veces.
    """
    reserva = get_object_or_404(
        Reserva.objects.select_related(
            "editorial", "registro__persona", "registro__convocatoria"
        ).prefetch_related("lineas__stand__mapa", "descuentos"),
        pk=reserva_id,
    )
    convocatoria = reserva.registro.convocatoria
    aqui = redirect("stands:detalle_reserva", reserva_id=reserva.pk)

    form_abono = AbonoManualForm()
    form_descuento = DescuentoEspecialForm()
    form_prorroga = ProrrogaForm()
    form_corte = FechaDeCorteForm(
        initial={"fecha": reserva.fecha_corte_pago_total}
    )
    form_cancelar = CancelacionForm()

    if peticion.method == "POST":
        accion = peticion.POST.get("accion")
        if accion == "abono_manual":
            form_abono = AbonoManualForm(peticion.POST, peticion.FILES)
            if form_abono.is_valid():
                try:
                    movimiento_nuevo = pagos.registrar(
                        reserva=reserva,
                        persona=peticion.user,
                        monto=form_abono.cleaned_data["monto"],
                        metodo=form_abono.cleaned_data["metodo"],
                        archivo=form_abono.cleaned_data["comprobante"],
                        manual=True,
                    )
                except pagos.PagoRechazado as exc:
                    messages.error(peticion, str(exc))
                else:
                    # Se relee: el abono manual nace validado y pasa por
                    # los umbrales en el acto (`CU-STD-019` paso 9), así
                    # que la instancia de arriba ya no dice el estado.
                    al_dia = Reserva.objects.get(pk=reserva.pk)
                    messages.success(
                        peticion,
                        f"Asentaste ${movimiento_nuevo.monto} en la reserva "
                        f"de {reserva.editorial.nombre}. Quedó "
                        f"{al_dia.get_estado_display().lower()}, con "
                        f"${al_dia.monto_pendiente} pendientes.",
                    )
                    return aqui
            else:
                # Genérico arriba y el detalle bajo cada campo, como en
                # A10: la pantalla lleva tres formularios y repetir aquí
                # el texto de cada error lo diría dos veces.
                messages.error(
                    peticion,
                    "No registramos el abono: revisa los campos señalados.",
                )

        elif accion == "descuento_especial":
            form_descuento = DescuentoEspecialForm(peticion.POST)
            if form_descuento.is_valid():
                try:
                    al_dia = pagos.aplicar_descuento_especial(
                        reserva=reserva,
                        administrador=peticion.user,
                        porcentaje=form_descuento.cleaned_data["porcentaje"],
                        motivo=form_descuento.cleaned_data["motivo"],
                    )
                except pagos.PagoRechazado as exc:
                    messages.error(peticion, str(exc))
                else:
                    messages.success(
                        peticion,
                        f"Aplicaste un {form_descuento.cleaned_data['porcentaje']}% "
                        f"de descuento. La reserva pasa a "
                        f"${al_dia.monto_total} y queda "
                        f"{al_dia.get_estado_display().lower()}.",
                    )
                    return aqui
            else:
                messages.error(
                    peticion,
                    "No aplicamos el descuento: revisa los campos señalados.",
                )

        elif accion == "prorrogar":
            form_prorroga = ProrrogaForm(peticion.POST)
            if form_prorroga.is_valid():
                try:
                    al_dia = reservas.prorrogar(
                        reserva=reserva,
                        administrador=peticion.user,
                        fecha=form_prorroga.cleaned_data["fecha"],
                    )
                except reservas.ReservaRechazada as exc:
                    messages.error(peticion, str(exc))
                else:
                    messages.success(
                        peticion,
                        "Ampliaste el plazo hasta el "
                        f"{date_format(timezone.localtime(al_dia.fecha_vencimiento_anticipo), 'j \\d\\e F \\d\\e Y')}. "
                        "La reserva deja de estar vencida.",
                    )
                    return aqui
            else:
                messages.error(
                    peticion, "No ampliamos el plazo: revisa la fecha."
                )

        elif accion == "mover_corte":
            form_corte = FechaDeCorteForm(peticion.POST)
            if form_corte.is_valid():
                try:
                    al_dia = reservas.mover_fecha_de_corte(
                        reserva=reserva,
                        administrador=peticion.user,
                        fecha=form_corte.cleaned_data["fecha"],
                    )
                except reservas.ReservaRechazada as exc:
                    messages.error(peticion, str(exc))
                else:
                    messages.success(
                        peticion,
                        "Guardamos el corte del pago total."
                        if al_dia.fecha_corte_pago_total
                        else "Quitaste la fecha de corte del pago total.",
                    )
                    return aqui
            else:
                messages.error(peticion, "No guardamos la fecha: revísala.")

        elif accion == "cancelar":
            form_cancelar = CancelacionForm(peticion.POST)
            if form_cancelar.is_valid():
                try:
                    reservas.cancelar(
                        reserva=reserva,
                        administrador=peticion.user,
                        motivo=form_cancelar.cleaned_data["motivo"],
                    )
                except reservas.ReservaRechazada as exc:
                    messages.error(peticion, str(exc))
                else:
                    messages.success(
                        peticion,
                        f"Cancelaste la reserva de {reserva.editorial.nombre}. "
                        "Sus espacios volvieron al mapa y se le avisó por "
                        "correo.",
                    )
                    return aqui
            else:
                for errores in form_cancelar.errors.values():
                    messages.error(peticion, errores[0])

        elif accion == "retirar_descuento":
            try:
                al_dia = pagos.retirar_descuento_especial(
                    reserva=reserva, administrador=peticion.user
                )
            except pagos.PagoRechazado as exc:
                messages.error(peticion, str(exc))
            else:
                messages.success(
                    peticion,
                    f"Retiraste el descuento especial. La reserva vuelve a "
                    f"${al_dia.monto_total}.",
                )
                return aqui
        else:
            messages.error(peticion, "Elige qué hacer con la reserva.")

    ajustes = configuracion.de_la_convocatoria(convocatoria)
    return render(
        peticion,
        "stands/detalle_reserva.html",
        {
            "convocatoria": convocatoria,
            "reserva": reserva,
            "desglose": reservas.desglose_de(reserva),
            "vencida": reserva.esta_vencida,
            # `CU-STD-029` paso 5. Con el comprobante y con quién lo
            # registró: es lo que se pregunta al cuadrar meses después.
            "movimientos": reserva.movimientos.select_related(
                "comprobante", "registrado_por", "validado_por"
            ),
            "en_revision": pagos.suma_en_revision(reserva),
            # El especial, si lo hay: decide si la tarjeta ofrece
            # aplicarlo o retirarlo. Nunca las dos cosas — `RN-05` deja
            # uno solo, y ofrecer «aplicar» con uno puesto es ofrecer un
            # botón que solo puede contestar que ya existe.
            "especial": reserva.descuentos.filter(
                tipo=DescuentoAplicado.Tipo.ESPECIAL
            ).first(),
            "form_abono": form_abono,
            "form_descuento": form_descuento,
            "form_prorroga": form_prorroga,
            "form_corte": form_corte,
            "form_cancelar": form_cancelar,
            # `CU-STD-035`: prorrogar solo tiene sentido mientras se
            # espera el anticipo. En una confirmada el plazo ya no corre,
            # y el formulario solo podría contestar que no hay nada que
            # prorrogar.
            "se_puede_prorrogar": reserva.estado == Reserva.Estado.POR_CONFIRMAR,
            "esta_viva": reserva.estado in Reserva.VIVAS,
            "porcentaje_pagado": _porcentaje_pagado(reserva),
            "umbral": ajustes.porcentaje_anticipo,
            "zona_admin": True,
        },
    )
