"""
Resolver una propuesta (`CU-EVT-009`).

Las tres acciones del administrador —aceptar, solicitar cambios,
rechazar— tienen la misma forma: comprobar que la propuesta se puede
resolver, escribir el desenlace, y dejarla pendiente de comunicar. Están
juntas porque comparten esa forma y sobre todo la comprobación, que es la
que evita el fallo silencioso de dos revisores resolviendo la misma
propuesta.

Es el mismo patrón que `apps/stands/servicios/dictamen.py`, y las
diferencias con aquél son del caso de uso, no del gusto:

- **El motivo del rechazo es obligatorio.** En `STD` es opcional porque
  su CU describe el rechazo como una acción directa; aquí lo pide la `E3`
  de `CU-EVT-009` igual que el mensaje de cambios.
- **Aceptar clasifica.** No es un cambio de estado a secas: el flujo
  principal pide elegir `literaria` o `academica` y confirmar de qué
  procedencia es quien propone, y sin las dos cosas el conteo por
  categoría de §3.6 no se puede hacer.
- **Un dictamen ya emitido solo lo cambia el operador.** Ver
  `_exigir_que_se_pueda_resolver`.

.. note:: Aquí no se crea ninguna actividad

   `CU-EVT-009` paso 6 dice que aceptar «crea una `Actividad` en estado
   `sin_horario`». Ese paso está escrito contra un modelo que el
   documento de datos ya descartó: §3.1 dice explícitamente que **no
   existe tal entidad**, porque duplicaría el estado de la solicitud, y
   que «sin horario» es **derivado** —no hay filas en
   `ProgramacionActividad`—. Además `Actividad` es aquí otra cosa: el
   enrutador polimórfico que se crea al *enviar* (`ADR-0009`).

   Lo que §3.2 sí pide crear es `SolicitudesAprobadas`, y eso existe para
   que `ProgramacionActividad` tenga una clave foránea real hacia lo
   aprobado. `PRG` no está construido, así que hoy sería una tabla sin
   ningún consumidor cuyas dos columnas repiten `fecha_revision` y
   `revisado_por`. Se crea cuando llegue quien la necesita.
"""

import logging

from django.db import transaction
from django.utils import timezone

from apps.ferias.permisos import es_operador_la_cuenta

from ..models import Solicitud
from . import avisos

logger = logging.getLogger(__name__)


class DictamenRechazado(Exception):
    """La propuesta no se puede resolver así.

    Cubre las tres negativas de `CU-EVT-009`: la propuesta ya está
    resuelta y quien lo intenta no puede rehacerla (`E2`), falta el texto
    obligatorio (`E3`), o falta la clasificación al aceptar.
    """


def _exigir_que_se_pueda_resolver(solicitud: Solicitud, revisor) -> None:
    """Quién puede escribir sobre esta propuesta, y cuándo (`A3`, `E2`).

    Mientras nadie la haya resuelto, cualquiera que administre la feria
    la dictamina: es el trabajo normal de la revisión.

    Volver sobre un dictamen **ya emitido** es otra cosa. El resultado
    pudo salir ya por correo, y deshacerlo obliga a comunicar una
    corrección a alguien que ya organizó su viaje. `CU-EVT-009` `A3` pide
    comprobar un permiso para eso y `E2` niega la acción a quien no lo
    tiene; ADR-0004 no define ningún nivel intermedio entre administrar y
    ser dueño, así que el permiso es el del **operador de la plataforma**
    (`ADR-0005`): el superusuario, que es quien ya alcanza cualquier feria
    por encima de sus dueños.

    Se comprueba aquí y no en la vista a propósito. Es una regla de
    negocio, y un comando de `manage.py` que llame a `aceptar` tiene que
    toparse con ella igual que un POST.
    """
    if not solicitud.esta_dictaminada:
        return
    if es_operador_la_cuenta(revisor):
        return
    raise DictamenRechazado(
        f"Esta propuesta ya está {solicitud.get_estado_display().lower()}. "
        "Cambiar un dictamen ya emitido está reservado al equipo técnico."
    )


def _resolver(
    solicitud: Solicitud,
    *,
    estado: str,
    revisor,
    categoria: str = "",
    es_uady_confirmado: bool | None = None,
    motivo_rechazo: str = "",
    mensaje_cambios: str = "",
) -> Solicitud:
    """El tronco común de las tres acciones.

    El bloqueo de fila (``select_for_update``) es lo que hace real la
    `E2`. Sin él, dos revisores que abran la misma propuesta y pulsen a la
    vez pasan los dos la comprobación: el segundo pisa el dictamen del
    primero, sale un correo contradictorio, y nada lo señala.

    La comprobación se repite **dentro** de la transacción y sobre la fila
    recién traída, no sobre el objeto que llegó por parámetro: ése se leyó
    cuando se pintó la pantalla y puede estar contando el estado de hace
    diez minutos.
    """
    with transaction.atomic():
        actual = Solicitud.objects.select_for_update().get(pk=solicitud.pk)
        _exigir_que_se_pueda_resolver(actual, revisor)

        actual.estado = estado
        actual.fecha_revision = timezone.now()
        actual.revisado_por = revisor
        actual.categoria = categoria
        actual.es_uady_confirmado = es_uady_confirmado
        actual.motivo_rechazo = motivo_rechazo
        actual.mensaje_cambios_solicitados = mensaje_cambios
        # Postcondición de los tres flujos: el desenlace vigente queda sin
        # comunicar. En un re-dictamen esto es lo que convierte el cambio
        # en una **actualización** del siguiente lote (`A3` paso 6) — la
        # fecha del envío anterior se conserva justamente para poder
        # distinguir "todavía no le hemos dicho nada" de "le dijimos otra
        # cosa y hay que corregirla".
        actual.resultado_notificado = False
        actual.save(
            update_fields=[
                "estado",
                "fecha_revision",
                "revisado_por",
                "categoria",
                "es_uady_confirmado",
                "motivo_rechazo",
                "mensaje_cambios_solicitados",
                "resultado_notificado",
            ]
        )

    logger.info("Propuesta %s resuelta como %s", actual.pk, estado)
    # El objeto que llegó por parámetro es el que tiene la vista en la
    # mano: se le pasan los valores nuevos para que no siga enseñando los
    # de antes.
    solicitud.__dict__.update(actual.__dict__)
    return actual


def aceptar(
    solicitud: Solicitud,
    *,
    revisor,
    categoria: str,
    es_uady_confirmado: bool,
) -> Solicitud:
    """Acepta y clasifica la propuesta (flujo principal de `CU-EVT-009`).

    La clasificación no es un adorno del formulario: es lo que hace
    contable la aceptación. El conteo de §3.6 agrupa por `categoria` ×
    procedencia, así que aceptar sin las dos deja una fila que no entra en
    ningún grupo.

    ``es_uady_confirmado`` se recibe siempre, incluso cuando coincide con
    lo que declaró quien propuso: el caso de uso pide que el administrador
    **valide o corrija** la autodeclaración (§3.1), y dejar el parámetro
    opcional convertiría "no lo revisé" en "lo confirmé".

    No manda correo: las aceptaciones salen en lote (`CU-EVT-010`), y por
    eso la propuesta queda con ``resultado_notificado`` en falso.
    """
    if categoria not in Solicitud.Categoria.values:
        raise DictamenRechazado(
            "Clasifica la propuesta como literaria o académica antes de "
            "aceptarla: es lo que la hace contable frente a la meta de la "
            "convocatoria."
        )
    return _resolver(
        solicitud,
        estado=Solicitud.Estado.ACEPTADA,
        revisor=revisor,
        categoria=categoria,
        es_uady_confirmado=bool(es_uady_confirmado),
    )


def rechazar(solicitud: Solicitud, *, revisor, motivo: str) -> Solicitud:
    """Rechaza la propuesta con su motivo registrado (`A2`).

    El motivo es **obligatorio** (`E3`), a diferencia de `STD`: aquí es lo
    que se comunica en el lote de resultados, y un rechazo sin razón deja
    a quien propuso sin nada que corregir para el año siguiente.

    Tampoco manda correo, por lo mismo que `aceptar`.
    """
    motivo = (motivo or "").strip()
    if not motivo:
        raise DictamenRechazado(
            "Escribe el motivo del rechazo: es lo que la persona recibe en "
            "el lote de resultados."
        )
    return _resolver(
        solicitud,
        estado=Solicitud.Estado.RECHAZADA,
        revisor=revisor,
        motivo_rechazo=motivo,
    )


def solicitar_cambios(solicitud: Solicitud, *, revisor, mensaje: str) -> Solicitud:
    """Devuelve la propuesta para que se corrija (`A1`).

    Es el único desenlace que **se avisa de inmediato** y no en lote: la
    persona tiene que poder corregir y reenviar antes de que cierre la
    convocatoria (`CU-EVT-004`), y esperar al lote de resultados le
    quitaría justamente ese plazo.

    Se puede solicitar cambios cuantas veces haga falta sobre la misma
    propuesta (`A1` paso 6): `cambios_solicitados` no es un dictamen
    emitido —ver `Solicitud.esta_dictaminada`—, así que no topa con el
    permiso de re-dictamen.
    """
    mensaje = (mensaje or "").strip()
    if not mensaje:
        raise DictamenRechazado(
            "Escribe qué debe corregir: es literalmente el correo que va a "
            "recibir, y sin eso no sabe qué cambiar."
        )
    resuelta = _resolver(
        solicitud,
        estado=Solicitud.Estado.CAMBIOS_SOLICITADOS,
        revisor=revisor,
        mensaje_cambios=mensaje,
    )
    # El aviso va **fuera** de la transacción, y es deliberado: un correo
    # que no sale no puede deshacer una decisión que ya se tomó. Si el
    # buzón rebota queda en el log, y la propuesta sigue en
    # `cambios_solicitados`, que es lo que lee la pantalla del aplicante.
    avisos.avisar_cambios_solicitados(resuelta)
    return resuelta
