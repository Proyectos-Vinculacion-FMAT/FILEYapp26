"""
Alta de una feria y designación de su dueño (`CU-FER-001`).

Toda la lógica vive aquí y no en el admin ni en el comando: los dos son
envoltorios que llaman a `crear_feria`. Es la regla 3 de CLAUDE.md —si
algo no se puede ejecutar desde `manage.py` sin pasar por HTTP, está en
el lugar equivocado— y aquí además es lo que garantiza que dar de alta
una feria desde `/django-admin/` y darla de alta por consola hagan
exactamente lo mismo.
"""

import logging
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.registros.models import Persona

from ..models import AdminFeria, Domain, Feria, schema_de, validar_slug
from . import avisos

logger = logging.getLogger(__name__)


class AltaRechazada(Exception):
    """El alta no se puede intentar: el slug es inválido o ya está en uso."""


@dataclass
class ResultadoAlta:
    feria: Feria
    dueno: Persona
    cuenta_creada: bool
    aviso_enviado: bool
    error_aviso: str = ""


def crear_feria(
    *,
    nombre: str,
    slug: str,
    correo_dueno: str,
    nombre_dueno: str = "",
    primer_apellido_dueno: str = "",
    segundo_apellido_dueno: str = "",
    edicion: str = "",
    sede: str = "",
    fecha_inicio=None,
    fecha_fin=None,
    enviar_aviso: bool = True,
    verbosity: int = 1,
) -> ResultadoAlta:
    """Crea la feria, su schema migrado y su dueño. O no crea nada.

    Pasos 2-8 del flujo principal de CU-FER-001.
    """
    slug = (slug or "").strip().lower()
    correo_dueno = (correo_dueno or "").strip().lower()

    # ── E1: el slug es inválido o ya está tomado ──────────────
    try:
        validar_slug(slug)
    except ValidationError as exc:
        raise AltaRechazada(" ".join(exc.messages)) from exc

    if not correo_dueno:
        raise AltaRechazada("Hace falta el correo de quien será dueño de la feria.")

    schema = schema_de(slug)
    if Feria.objects.filter(slug=slug).exists():
        raise AltaRechazada(f"Ya existe una feria con el slug «{slug}».")
    if Feria.objects.filter(schema_name=schema).exists():
        raise AltaRechazada(f"Ya existe una feria sobre el schema «{schema}».")

    # ── Paso 3-5: la feria y su schema ────────────────────────
    #
    # Deliberadamente FUERA de `transaction.atomic`. `save()` dispara
    # `create_schema()`, que ejecuta migraciones —y las migraciones
    # manejan sus propias transacciones—. Envolverlas en un bloque
    # atómico exterior es justo lo que `django-tenants` desaconseja.
    #
    # Lo que E1 exige («o existen los tres, o no existe ninguno») se
    # consigue compensando a mano: la librería ya deshace el schema si
    # falla al crearlo, y el `except` de abajo deshace la feria si falla
    # cualquier paso posterior.
    feria = Feria(
        nombre=nombre,
        slug=slug,
        schema_name=schema,
        edicion=edicion,
        sede=sede,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado=Feria.Estado.EN_PREPARACION,
    )
    # `verbosity` llega hasta el `migrate` que corre por dentro: la
    # consola quiere ver qué se aplicó, las pruebas no.
    feria.save(verbosity=verbosity)  # crea el schema y lo migra
    logger.info("Feria %s creada sobre el schema %s", slug, schema)

    try:
        with transaction.atomic():
            # El slug de ruteo: es lo que `TenantSubfolderMiddleware`
            # busca para resolver `/f/<slug>/`. Sin esta fila la feria
            # existe pero es inalcanzable.
            Domain.objects.create(domain=slug, tenant=feria, is_primary=True)

            # ── Paso 6 / A1: la cuenta puede existir ya ───────
            # Si existe se reutiliza **sin tocar sus datos**: es la misma
            # persona que ya usa el sistema en otras ferias, y el alta de
            # una feria no es el sitio para corregirle el nombre.
            dueno = Persona.objects.filter(correo=correo_dueno).first()
            cuenta_creada = dueno is None
            if cuenta_creada:
                dueno = Persona.objects.create_user(
                    correo=correo_dueno,
                    nombre=nombre_dueno,
                    primer_apellido=primer_apellido_dueno,
                    segundo_apellido=segundo_apellido_dueno,
                )

            # ── Paso 7: el dueño ──────────────────────────────
            # `creado_por` nulo: no se lo dio nadie de dentro de la
            # feria, lo designó el operador desde fuera de toda feria.
            AdminFeria.objects.create(
                feria=feria, persona=dueno, es_dueno=True, creado_por=None
            )
    except Exception:
        # E2: no se deja una feria a medias. Una feria registrada pero
        # sin dueño o sin slug de ruteo es peor que no tenerla: aparece
        # en los listados y no se puede entrar a ella.
        logger.exception("Alta de la feria %s deshecha", slug)
        feria.delete(force_drop=True)
        raise

    # ── Paso 8 / E3: el aviso ─────────────────────────────────
    # Un fallo de correo NO deshace el alta: la feria, su schema y su
    # dueño ya son válidos y la persona puede entrar en cuanto conozca
    # la dirección. Mismo criterio que CU-REG-005; distinto de
    # CU-REG-002 E3, donde el correo *es* la credencial.
    aviso_enviado = False
    error_aviso = ""
    if enviar_aviso:
        try:
            avisos.avisar_dueno_de_feria(feria, dueno)
            aviso_enviado = True
        except avisos.AvisoFallido as exc:
            error_aviso = str(exc)

    return ResultadoAlta(
        feria=feria,
        dueno=dueno,
        cuenta_creada=cuenta_creada,
        aviso_enviado=aviso_enviado,
        error_aviso=error_aviso,
    )
