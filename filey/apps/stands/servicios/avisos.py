"""
Lo que `STD` le dice por correo a quien aplica y reserva.

Tres momentos, y ninguno más: el desenlace de la solicitud
(`CU-STD-008`), la reserva confirmada al cubrir el anticipo
(`CU-STD-026`) y liquidada al cubrir el total (`CU-STD-027`).

El reparto es el que decidió el equipo el 2026-08-27: **la tabla es de
`STD`, el envío no**. `Notificacion` vive en el schema de esta feria
porque apunta a una solicitud de esta edición; quién entrega el correo lo
decide `EMAIL_BACKEND`, como todo el correo del proyecto.

.. warning:: Nunca se llama a Resend desde aquí

   Se compone un `EmailMultiAlternatives` y se envía por
   ``django.core.mail``. Es lo que permite que en pruebas el correo caiga
   en ``mail.outbox`` en vez de salir a la red, con `RESEND_API_KEY` en
   el entorno o sin ella.
"""

import logging
from decimal import Decimal

from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.html import escape

from comun.urls import url_absoluta, url_de_esta_feria, url_publica

from ..models import Notificacion, Reserva, Solicitud

logger = logging.getLogger(__name__)

#: Qué tipo de notificación corresponde a cada desenlace.
TIPO_POR_ESTADO = {
    Solicitud.Estado.ACEPTADA: Notificacion.Tipo.APLICACION_ACEPTADA,
    Solicitud.Estado.RECHAZADA: Notificacion.Tipo.APLICACION_RECHAZADA,
    Solicitud.Estado.CAMBIOS_SOLICITADOS: Notificacion.Tipo.APLICACION_CAMBIOS,
}


def _cuerpo(solicitud: Solicitud) -> tuple[str, list[str]]:
    """Asunto y párrafos según el desenlace (`CU-STD-008` paso 2)."""
    editorial = solicitud.datos_editorial.get("nombre", "tu editorial")
    convocatoria = solicitud.registro.convocatoria.nombre

    if solicitud.estado == Solicitud.Estado.ACEPTADA:
        asunto = f"Tu solicitud para {convocatoria} fue aceptada"
        parrafos = [
            f"La solicitud de {editorial} para «{convocatoria}» fue aceptada.",
            "Ya puedes elegir tus espacios en el mapa del showfloor y "
            "reservarlos.",
        ]
    elif solicitud.estado == Solicitud.Estado.RECHAZADA:
        asunto = f"Tu solicitud para {convocatoria} no fue aceptada"
        parrafos = [
            f"La solicitud de {editorial} para «{convocatoria}» no fue aceptada.",
            "Puedes volver a aplicar con la misma editorial corrigiendo lo "
            "que haga falta, mientras la convocatoria siga abierta.",
        ]
    else:
        asunto = f"Cambios pedidos en tu solicitud para {convocatoria}"
        parrafos = [
            f"Para poder resolver la solicitud de {editorial} hacen falta "
            "algunos cambios:",
            solicitud.motivo_peticion,
            "Entra a corregirla y vuelve a enviarla; conserva todo lo que ya "
            "habías capturado.",
        ]

    return asunto, parrafos


def _maquetar(
    asunto: str, parrafos: list[str], enlace: str, etiqueta: str
) -> tuple[str, str]:
    """El mismo sobre para los tres avisos: texto plano y HTML."""
    texto = "\n\n".join(
        [
            *[p for p in parrafos if p],
            f"{etiqueta}: {enlace}",
            "FILEY — Feria Internacional de la Lectura Yucatán",
        ]
    )
    html = (
        '<div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto;">'
        f'<h2 style="color: #1a1a1a;">{escape(asunto)}</h2>'
        + "".join(f"<p>{escape(p)}</p>" for p in parrafos if p)
        + f'<p><a href="{escape(enlace)}">{escape(etiqueta)}</a></p>'
        '<hr style="border: none; border-top: 1px solid #eaeaea; margin: 24px 0;" />'
        '<p style="color: #999; font-size: 12px;">'
        "FILEY — Feria Internacional de la Lectura Yucatán<br>"
        "Coordinación General de Contenidos · UADY"
        "</p></div>"
    )
    return texto, html


def _entregar(
    *, destinatario, destino: str, asunto: str, texto: str, html: str, tipo: str, **a_que
) -> Notificacion:
    """Manda el correo y deja el rastro. **Nunca levanta.**

    Un fallo de entrega no puede deshacer lo que ya pasó —un dictamen
    tomado, un abono validado—: se registra la notificación como
    `fallida` con el motivo, que es lo que permite reintentar a mano
    (`CU-STD-008` E1).

    :param a_que: ``solicitud=`` o ``reserva=``, exactamente una. Lo
        sostiene la restricción `un_aviso_cuelga_de_exactamente_una_cosa`.
    """
    mensaje = EmailMultiAlternatives(subject=asunto, body=texto, to=[destino])
    mensaje.attach_alternative(html, "text/html")

    try:
        entregados = mensaje.send(fail_silently=False)
        if not entregados:
            raise RuntimeError("el backend de correo no entregó el mensaje")
        estado, detalle = Notificacion.Estado.ENVIADA, ""
    except Exception as exc:  # noqa: BLE001 — cualquier fallo del transporte
        logger.exception("No se pudo entregar el aviso «%s» a %s", tipo, destino)
        estado, detalle = Notificacion.Estado.FALLIDA, str(exc)

    return Notificacion.objects.create(
        destinatario=destinatario,
        tipo=tipo,
        estado=estado,
        detalle_error=detalle,
        # La dirección **usada**, no la que tenga la ficha al leerla: es
        # lo único que contesta «¿a qué buzón salió?» un mes después.
        destino=destino,
        # Lo deja el backend de Resend; con `locmem` no hay acuse y
        # queda vacío, que es información correcta y no un hueco.
        referencia_externa=str(getattr(mensaje, "acuse_proveedor", "") or "")[:120],
        **a_que,
    )


def avisar_resultado(solicitud: Solicitud) -> Notificacion:
    """Manda el correo del desenlace y lo deja registrado (`CU-STD-008`).

    Se llama **fuera** de la transacción del dictamen: si corriera
    dentro, una notificación fallida escrita y luego revertida dejaría el
    dictamen sin rastro de que el aviso no salió.
    """
    tipo = TIPO_POR_ESTADO.get(solicitud.estado)
    if tipo is None:
        raise ValueError(
            f"Una solicitud {solicitud.estado} no tiene resultado que avisar."
        )

    # A quién: el correo de contacto de la ficha, que puede no ser el de
    # acceso —la cuenta personal de quien tramita frente al buzón
    # comercial de la editorial—. Si la ficha no lo trae, la cuenta.
    persona = solicitud.registro.persona
    destino = solicitud.datos_editorial.get("correo_electronico") or persona.correo

    asunto, parrafos = _cuerpo(solicitud)
    texto, html = _maquetar(
        asunto, parrafos, url_absoluta(url_publica("ferias:elegir")), "Entrar a FILEY"
    )
    return _entregar(
        destinatario=persona,
        destino=destino,
        asunto=asunto,
        texto=texto,
        html=html,
        tipo=tipo,
        solicitud=solicitud,
    )


# ── CU-STD-026 y 027 · los dos umbrales ───────────────────────


def avisar_confirmacion(reserva: Reserva) -> Notificacion:
    """La reserva cubrió el anticipo y quedó confirmada (`CU-STD-026`).

    Lo que el correo tiene que dejar claro son las tres cosas que
    cambian para quien lo recibe: **sus espacios ya son suyos**, el
    plazo de treinta días dejó de correr (`RN-03` se apagó, `RN-12` ya
    no le apunta) y lo que queda por pagar tiene otra fecha.
    """
    espacios = _espacios_de(reserva)
    asunto = "Tu reserva de espacios quedó confirmada"
    parrafos = [
        f"Recibimos el anticipo de {reserva.editorial.nombre}: la reserva de "
        f"{espacios} quedó confirmada.",
        "Esos espacios ya están apartados a tu nombre y el plazo de los "
        "primeros días dejó de correr.",
    ]
    if reserva.monto_pendiente > 0:
        pendiente = f"Queda un saldo de ${reserva.monto_pendiente} por cubrir"
        if reserva.fecha_corte_pago_total:
            pendiente += (
                f", con fecha límite el "
                f"{_en_espanol(reserva.fecha_corte_pago_total)}"
            )
        parrafos.append(pendiente + ".")
    return _avisar_de_la_reserva(
        reserva, Notificacion.Tipo.RESERVA_CONFIRMADA, asunto, parrafos
    )


def avisar_liquidacion(reserva: Reserva) -> Notificacion:
    """La reserva quedó liquidada al 100% (`CU-STD-027`).

    No pide nada: es el único correo del dominio que solo confirma. Por
    eso dice lo que se pagó y lo que sigue —montar—, y no repite
    instrucciones de pago que ya no sirven.
    """
    asunto = "Tu reserva está liquidada"
    parrafos = [
        f"Quedó cubierto el total de ${reserva.monto_total} de la reserva de "
        f"{reserva.editorial.nombre}.",
        f"Tus espacios ({_espacios_de(reserva)}) están confirmados y pagados. "
        "No queda nada pendiente por este concepto.",
        "Te escribiremos con los detalles del montaje conforme se acerque la "
        "feria.",
    ]
    return _avisar_de_la_reserva(
        reserva, Notificacion.Tipo.RESERVA_PAGADA, asunto, parrafos
    )


# ── CU-STD-024 y 025 · el plazo que venció ────────────────────


def avisar_posible_cancelacion(reserva: Reserva) -> Notificacion:
    """El plazo del anticipo venció sin cubrirse (`CU-STD-025`).

    **No dice que la reserva se canceló, porque no se canceló.** `RN-12`:
    vencer no libera nada — el sistema notifica y espera la decisión de
    una persona. Decir aquí «tu reserva fue cancelada» sería mentir y,
    peor, empujar a alguien a dejar de pagar algo que todavía es suyo.

    Lo que sí lleva es la cifra que decide si se paga hoy: **cuánto falta
    para el anticipo**, que no es el saldo (`CU-STD-014` paso 2).
    """
    falta = max(reserva.anticipo - reserva.monto_abonado, Decimal("0.00"))
    asunto = "Tu reserva de espacios necesita un pago para seguir en pie"
    parrafos = [
        f"El {_en_espanol(timezone.localtime(reserva.fecha_vencimiento_anticipo))} "
        f"venció el plazo para cubrir el anticipo de la reserva de "
        f"{reserva.editorial.nombre}, y todavía no lo recibimos.",
        f"Lo que apartaste —{_claves_de(reserva)}— sigue a tu nombre, pero "
        "la reserva puede cancelarse.",
        f"Para regularizarla faltan ${falta}. Regístralos en tu cuenta en "
        "cuanto hagas el pago, o escríbenos si necesitas más tiempo: se "
        "puede ampliar el plazo.",
    ]
    return _avisar_de_la_reserva(
        reserva, Notificacion.Tipo.POSIBLE_CANCELACION, asunto, parrafos
    )


def avisar_vencimiento_al_equipo(reserva: Reserva, administrador) -> Notificacion:
    """Una reserva venció y hay que decidir qué hacer (`CU-STD-024`).

    Es el único aviso del dominio que **no** va al aplicante. Va a quien
    administra porque `RN-12` escala el vencimiento a una persona: el
    sistema no cancela por su cuenta, así que sin este correo una reserva
    vencida se queda ocupando espacios hasta que alguien mire la lista.

    Lleva las cuatro cifras del paso 2 —editorial, fecha vencida, total y
    abonado— porque son las que deciden entre cancelar y prorrogar sin
    tener que abrir nada.
    """
    asunto = f"Reserva vencida · {reserva.editorial.nombre}"
    parrafos = [
        f"La reserva de {reserva.editorial.nombre} venció el "
        f"{_en_espanol(timezone.localtime(reserva.fecha_vencimiento_anticipo))} "
        "sin cubrir el anticipo.",
        f"Total ${reserva.monto_total} · abonado ${reserva.monto_abonado} · "
        f"anticipo requerido ${reserva.anticipo}.",
        f"Lo apartado —{_claves_de(reserva)}— sigue ocupado: vencer no libera "
        "nada. Hay que resolverla, cancelándola o dándole una prórroga.",
    ]
    texto, html = _maquetar(
        asunto, parrafos, _url_de_la_reserva(reserva), "Abrir la reserva"
    )
    return _entregar(
        destinatario=administrador,
        destino=administrador.correo,
        asunto=asunto,
        texto=texto,
        html=html,
        tipo=Notificacion.Tipo.RESERVA_VENCIDA,
        reserva=reserva,
    )


# ── CU-STD-035 A1 · la reserva que se cancela ─────────────────


def avisar_cancelacion(reserva: Reserva) -> Notificacion:
    """La reserva se canceló y sus espacios volvieron al mapa.

    Es el aviso de la única acción irreversible del dominio (`RN-11`), y
    por eso es el único que **no ofrece una salida dentro del sistema**:
    lo que queda es hablar con la feria. Decir «vuelve a reservar» sería
    prometer unos espacios que ya están de vuelta en el mapa y que puede
    haber tomado alguien más.

    El motivo va si lo hay: sin él, quien lo recibe solo sabe que perdió
    su lugar.
    """
    asunto = "Tu reserva de espacios fue cancelada"
    parrafos = [
        f"La reserva de {reserva.editorial.nombre} en «"
        f"{reserva.registro.convocatoria.nombre}» quedó cancelada.",
        f"Los espacios que tenías apartados —{_claves_de(reserva)}— vuelven "
        "a estar disponibles para otras editoriales.",
    ]
    if reserva.motivo_cancelacion:
        parrafos.append(f"Motivo: {reserva.motivo_cancelacion}")
    if reserva.monto_abonado > 0:
        # Hay dinero validado de por medio. El sistema no sabe qué se
        # acordó con esa cantidad, así que no lo inventa: lo dice y manda
        # a hablar con alguien.
        parrafos.append(
            f"Tienes ${reserva.monto_abonado} abonados a esta reserva. "
            "Escríbenos para resolver qué hacer con ese saldo."
        )
    parrafos.append(
        "Si crees que fue un error, contéstanos a este correo y lo revisamos."
    )
    return _avisar_de_la_reserva(
        reserva, Notificacion.Tipo.RESERVA_CANCELADA, asunto, parrafos
    )


def _avisar_de_la_reserva(
    reserva: Reserva, tipo: str, asunto: str, parrafos: list[str]
) -> Notificacion:
    """Lo común a los dos: a quién, a dónde enlaza y el sobre.

    A quién sigue la misma regla que el aviso de la solicitud: el correo
    de contacto de la editorial —que puede ser un buzón comercial— y, si
    no lo tiene, la cuenta de quien tramita.
    """
    persona = reserva.registro.persona
    destino = reserva.editorial.correo_electronico or persona.correo
    texto, html = _maquetar(
        asunto, parrafos, _url_de_la_cuenta(reserva), "Ver mi reserva"
    )
    return _entregar(
        destinatario=persona,
        destino=destino,
        asunto=asunto,
        texto=texto,
        html=html,
        tipo=tipo,
        reserva=reserva,
    )


def _espacios_de(reserva: Reserva) -> str:
    """«el espacio 24B», «los espacios 24B, 25B y 26B» — como se dicen."""
    claves = [linea.stand.clave for linea in reserva.lineas.all()]
    if not claves:
        return "tus espacios"
    if len(claves) == 1:
        return f"el espacio {claves[0]}"
    return "los espacios " + ", ".join(claves[:-1]) + f" y {claves[-1]}"


def _claves_de(reserva: Reserva) -> str:
    """Las claves a secas, para meterlas entre guiones en una frase."""
    return ", ".join(linea.stand.clave for linea in reserva.lineas.all()) or "—"


MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)


def _en_espanol(fecha) -> str:
    """`3 de noviembre de 2027`. Sin depender del `LANGUAGE_CODE` activo."""
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


def _url_de_la_cuenta(reserva: Reserva) -> str:
    """La dirección completa de «Mi reserva», para un correo."""
    return url_de_esta_feria(
        "stands:cuenta", convocatoria_id=reserva.registro.convocatoria_id
    )


def _url_de_la_reserva(reserva: Reserva) -> str:
    """La dirección de A4, para el correo de quien administra."""
    return url_de_esta_feria("stands:detalle_reserva", reserva_id=reserva.pk)
