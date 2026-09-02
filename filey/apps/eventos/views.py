"""
Las pantallas de `EVT` (U1 — captura y envío de una propuesta).

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

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.registros.permisos import requiere_participante
from comun.htmx import es_htmx

from .formularios import FORMULARIO_POR_TIPO, SolicitudForm
from .models import Solicitud
from .servicios import catalogo, solicitudes


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
    enviando = peticion.method == "POST"

    if enviando:
        form_solicitud = SolicitudForm(peticion.POST, es_publicacion=es_publicacion)
        form_tipo = (
            FormularioDelTipo(peticion.POST, peticion.FILES)
            if FormularioDelTipo
            else None
        )
    else:
        # `GET` con datos es elegir el tipo: se repuebla con lo que ya
        # estaba escrito, pero sin marcar errores —nadie ha enviado nada
        # todavía y señalar en rojo lo que aún se está llenando es
        # exactamente lo que la ley de Postel desaconseja—.
        datos = peticion.GET or None
        form_solicitud = SolicitudForm(datos, es_publicacion=es_publicacion)
        form_tipo = FormularioDelTipo(datos) if FormularioDelTipo else None
        if datos is not None:
            form_solicitud.errors.clear()
            if form_tipo is not None:
                form_tipo.errors.clear()

    if enviando and abierta and form_tipo is not None:
        if form_solicitud.is_valid() and form_tipo.is_valid():
            try:
                creada = solicitudes.crear(
                    convocatoria=convocatoria,
                    persona=peticion.user,
                    comunes=form_solicitud.cleaned_data,
                    nombre_tipo=nombre_tipo,
                    detalle=_detalle_de(form_tipo),
                    documentos=form_tipo.documentos(),
                )
            except solicitudes.EnvioRechazado as motivo:
                # `E1`: la convocatoria pudo cerrar entre que se pintó el
                # formulario y se pulsó enviar. Se vuelve al formulario
                # con lo capturado, que es lo que el CU pide.
                form_solicitud.add_error(None, str(motivo))
            else:
                return redirect("eventos:confirmacion", solicitud_id=creada.pk)

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


def _campos_de_archivo(form_tipo):
    from django.forms import FileField

    return [
        (nombre, campo)
        for nombre, campo in form_tipo.fields.items()
        if isinstance(campo, FileField)
    ]


@requiere_participante
def confirmacion(peticion, solicitud_id):
    """El acuse con el folio (paso 13 y 14 del CU).

    Solo la ve quien la envió: el folio y el título de una propuesta ajena
    no son de nadie más. Se comprueba por el registro, que es lo único
    que ata una propuesta a una persona.
    """
    propuesta_enviada = get_object_or_404(
        Solicitud.objects.select_related(
            "registro", "registro__convocatoria", "actividad", "actividad__tipo"
        ),
        pk=solicitud_id,
    )
    if propuesta_enviada.registro.persona_id != peticion.user.pk:
        raise Http404("Esa propuesta no es tuya.")

    convocatoria = propuesta_enviada.registro.convocatoria
    # Las otras que ya envió, para poder verlas desde aquí. No es el
    # listado de `CU-EVT-003` —ése filtra y lleva al detalle— sino la
    # respuesta a «¿qué llevo mandado?» en el momento en que se pregunta:
    # justo después de enviar.
    anteriores = [
        otra
        for otra in solicitudes.propuestas_de(convocatoria, peticion.user)
        if otra.pk != propuesta_enviada.pk
    ]
    return render(
        peticion,
        "eventos/confirmacion.html",
        {
            "propuesta": propuesta_enviada,
            "convocatoria": convocatoria,
            "anteriores": anteriores,
        },
    )
