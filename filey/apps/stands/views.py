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
from django.shortcuts import get_object_or_404, redirect, render

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.ferias.permisos import requiere_admin_feria
from apps.registros.permisos import requiere_participante

from .formularios import (
    MAXIMO_SELLOS,
    BasesForm,
    DictamenForm,
    DocumentoForm,
    EditorialForm,
    SellosForm,
)
from .models import Documento, Editorial, Solicitud
from .servicios import archivos, configuracion, dictamen, solicitudes


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
        messages.error(
            peticion,
            f"No se envió: falta {cuantos} campo por corregir."
            if cuantos == 1
            else f"No se envió: faltan {cuantos} campos por corregir.",
        )
        return None, formularios

    es_reenvio = (
        ultima is not None and ultima.estado == Solicitud.Estado.CAMBIOS_SOLICITADOS
    )

    # Todo o nada. Sin esta transacción, un envío rechazado a última hora
    # —la convocatoria se cerró entre el GET y el POST— dejaría la ficha
    # y los documentos guardados y ninguna solicitud: un expediente que
    # existe a medias y que nadie va a revisar.
    #
    # Lo capturado no se pierde igualmente (`CU-STD-001`, "en fallo"): lo
    # conservan los formularios ligados, que vuelven a la plantilla.
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
            messages.error(peticion, "Elige una de las tres acciones.")
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

    Hoy no es más que un desvío a la cola de revisión: es lo único que
    esta fase construye del panel. Existe para que el registro de módulos
    tenga a dónde apuntar `url_panel` sin inventar una pantalla vacía.
    """
    configuracion.de_la_convocatoria(_convocatoria_de_stands(convocatoria_id))
    return redirect("stands:solicitudes", convocatoria_id=convocatoria_id)


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
