"""
Quién administra una feria: darlo y quitarlo (`CU-FER-003`, `CU-FER-004`).

Es la responsabilidad que `ADR-0004` le asigna al **dueño** de cada
feria, y la razón de que el dueño exista: sin ella, cualquier
administrador podría crear administradores y quién tiene acceso volvería
a diluirse.

Toda la regla vive aquí y no en la vista ni en el comando: los dos son
envoltorios: la pantalla del dueño (`views_accesos.py`) y
`manage.py alta_admin_feria`, que es la vía de emergencia. Es la regla 3
de CLAUDE.md, y aquí además es lo que garantiza que dar acceso desde la
pantalla y darlo por consola dejen exactamente el mismo estado.

.. note:: Esto NO comprueba quién llama

   Que solo el dueño pueda hacerlo lo imponen los decoradores de
   ``apps/ferias/permisos.py`` sobre las vistas — ``requiere_dueno_feria``—,
   y el comando corre en el servidor, donde ya se es operador. Un
   servicio que se pueda llamar desde ``manage.py`` no puede depender de
   que haya una petición detrás.
"""

import logging
from dataclasses import dataclass

from django.db.models import QuerySet

from apps.registros.models import Persona

from ..models import AdminFeria, Feria
from . import avisos

logger = logging.getLogger(__name__)


class AccesoRechazado(Exception):
    """La operación no se puede intentar (feria archivada, retirar al dueño…)."""


@dataclass
class ResultadoAlta:
    acceso: AdminFeria
    persona: Persona
    cuenta_creada: bool
    ya_tenia_acceso: bool
    aviso_enviado: bool = False
    error_aviso: str = ""


def administradores_de(feria: Feria) -> QuerySet[AdminFeria]:
    """Quién administra esta feria, con el dueño primero.

    Es el paso 2 de los dos casos de uso: antes de dar o quitar un
    acceso hay que ver los que hay. El orden lo pone
    ``AdminFeria.Meta.ordering`` (``-es_dueno``, ``creado_en``), así que
    el dueño encabeza la lista sin que la pantalla lo ordene.
    """
    return (
        AdminFeria.objects.filter(feria=feria)
        .select_related("persona")
        .order_by("-es_dueno", "creado_en")
    )


def dar_acceso(
    *,
    feria: Feria,
    correo: str,
    nombre: str = "",
    primer_apellido: str = "",
    segundo_apellido: str = "",
    concedido_por: Persona | None = None,
    enviar_aviso: bool = True,
) -> ResultadoAlta:
    """Da acceso administrativo a una persona sobre esta feria (`CU-FER-003`).

    Nunca crea otro dueño: ``es_dueno`` se queda en falso. La propiedad
    se asigna al crear la feria (CU-FER-001) y transferirla es un caso
    de uso que todavía no existe.
    """
    correo = (correo or "").strip().lower()
    if not correo:
        raise AccesoRechazado("Hace falta el correo de la persona.")

    # ── E4: una edición archivada se consulta, no se opera ────
    if feria.estado == Feria.Estado.ARCHIVADA:
        raise AccesoRechazado(
            f"«{feria.nombre}» está archivada: una edición cerrada ya no "
            "admite administradores nuevos."
        )

    # ── Paso 4 / A1: la cuenta puede existir ya ───────────────
    # Se reutiliza **sin tocar sus datos**: es la misma persona que ya
    # usa el sistema —como proponente, o administrando otra feria— y el
    # alta de un acceso no es el sitio para corregirle el nombre.
    persona = Persona.objects.filter(correo=correo).first()
    cuenta_creada = persona is None
    if cuenta_creada:
        persona = Persona.objects.create_user(
            correo=correo,
            nombre=nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
        )
    elif not persona.nombre and nombre:
        # Única excepción de A1: una cuenta sin nombre no se puede
        # saludar en un correo ni pintar en una lista. Si el alta lo
        # trae, se completa.
        persona.nombre = nombre
        persona.primer_apellido = persona.primer_apellido or primer_apellido
        persona.segundo_apellido = persona.segundo_apellido or segundo_apellido
        persona.save(update_fields=["nombre", "primer_apellido", "segundo_apellido"])

    # ── Paso 5 / E2: no duplicar el acceso ────────────────────
    # `get_or_create` y no un `exists()` previo: la no duplicación la
    # garantiza la restricción única de la tabla, y comprobarla antes
    # dejaría una carrera entre las dos consultas.
    acceso, creado = AdminFeria.objects.get_or_create(
        feria=feria,
        persona=persona,
        defaults={"es_dueno": False, "creado_por": concedido_por},
    )
    if not creado:
        # No se reenvía el aviso: la persona ya fue notificada en su
        # alta original, y un correo repetido se lee como un cambio que
        # no ocurrió.
        return ResultadoAlta(
            acceso=acceso,
            persona=persona,
            cuenta_creada=cuenta_creada,
            ya_tenia_acceso=True,
        )

    logger.info("Acceso a la feria %s concedido a %s", feria.slug, correo)

    # ── Paso 6 / E3: el aviso ─────────────────────────────────
    # Un fallo de correo NO deshace el alta: el acceso ya es válido y la
    # persona entra en cuanto conozca la dirección. Mismo criterio que
    # CU-FER-001 E3; distinto de CU-REG-002, donde el correo *es* la
    # credencial.
    aviso_enviado = False
    error_aviso = ""
    if enviar_aviso:
        try:
            avisos.avisar_admin_de_feria(feria, persona)
            aviso_enviado = True
        except avisos.AvisoFallido as exc:
            error_aviso = str(exc)

    return ResultadoAlta(
        acceso=acceso,
        persona=persona,
        cuenta_creada=cuenta_creada,
        ya_tenia_acceso=False,
        aviso_enviado=aviso_enviado,
        error_aviso=error_aviso,
    )


def retirar_acceso(*, acceso: AdminFeria) -> Persona:
    """Quita el acceso de una persona a esta feria (`CU-FER-004`).

    Devuelve la ``Persona`` afectada, que **sigue existiendo**: no se
    borra su cuenta, ni su historial, ni sus accesos a otras ferias.

    Se elimina la fila en vez de marcarla inactiva. El acceso a una
    feria no tiene estados —se tiene o no se tiene—, y guardar filas
    retiradas obligaría a que cada comprobación recordara filtrarlas.
    Si algún día hace falta saber quién tuvo acceso y cuándo, eso es una
    bitácora aparte, no una columna de esta tabla.
    """
    # ── E2: una feria no puede quedarse sin dueño ─────────────
    # Nadie podría volver a dar acceso a nadie, ni siquiera el operador
    # sin entrar por consola. La salida es transferir la propiedad,
    # que todavía es un caso de uso pendiente.
    if acceso.es_dueno:
        raise AccesoRechazado(
            "No se puede retirar al dueño de la feria: se quedaría sin nadie "
            "que pueda administrar sus accesos. Antes hay que transferir la "
            "propiedad."
        )

    persona = acceso.persona
    acceso.delete()
    logger.info(
        "Acceso a la feria %s retirado a %s", acceso.feria.slug, persona.correo
    )
    return persona
