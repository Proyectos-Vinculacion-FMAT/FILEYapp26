"""
Modelos del Core Ferias (FER) — la capa **global**.

Aquí vive lo que responde preguntas que cruzan ediciones: qué ferias
existen y quién administra cada una. El contenido de una feria
—convocatorias, propuestas, stands— **no** está aquí: vive en
``apps/convocatorias`` y en los dominios verticales, dentro del schema
de su feria (`ADR-0003`).

Que `FER` esté partido en dos apps de Django no es un capricho de
organización: ``django-tenants`` separa por **app**, no por modelo. Una
app listada a la vez en ``SHARED_APPS`` y en ``TENANT_APPS`` duplicaría
*todas* sus tablas en *todos* los schemas, y tendríamos una copia de
``Feria`` dentro de cada feria.
"""

import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django_tenants.models import DomainMixin, TenantMixin

# El slug es el prefijo de la URL (`/f/2027/`) y la raíz del nombre del
# schema. Se restringe a minúsculas, dígitos y guiones interiores para
# que quepa en ambos sitios sin escaparlo.
SLUG_VALIDO = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")

# `schema_name` de PostgreSQL tiene un tope duro de 63 caracteres, y el
# prefijo `feria_` gasta 6.
LARGO_MAX_SLUG = 57


def validar_slug(valor: str) -> None:
    if not SLUG_VALIDO.match(valor or ""):
        raise ValidationError(
            "El slug solo admite minúsculas, dígitos y guiones interiores "
            "(p. ej. «2027» o «2027-otono»)."
        )
    if len(valor) > LARGO_MAX_SLUG:
        raise ValidationError(
            f"El slug no puede pasar de {LARGO_MAX_SLUG} caracteres: con el "
            "prefijo «feria_» tiene que caber en el tope de 63 de PostgreSQL."
        )


def schema_de(slug: str) -> str:
    """`"2027-otono"` → `"feria_2027_otono"`.

    El guion se cambia por guion bajo porque un identificador con guion
    obliga a ir entrecomillado en cada `SET search_path` y cada `CREATE
    TABLE`. Es una fuente de errores que no compra nada.
    """
    return "feria_" + slug.replace("-", "_")


class FeriaRealesManager(models.Manager):
    """Las ediciones de verdad, sin la fila de sistema.

    Ver la advertencia sobre la fila `public` en ``Feria``.
    """

    def get_queryset(self):
        return super().get_queryset().exclude(schema_name="public")


class Feria(TenantMixin):
    """Una edición de la feria (`CU-FER-001`). Vive en `public`.

    Crear una fila aquí **no es insertar un registro**: ``TenantMixin.save()``
    crea el schema y le aplica las migraciones de los dominios de
    contenido. Si eso falla, la propia librería borra lo que creó y
    re-lanza — que es lo que exige CU-FER-001 E2.

    .. warning:: Una de estas filas **no es una feria**

       ``TenantSubfolderMiddleware`` resuelve toda petición que no
       empiece por ``/f/`` haciendo ``Feria.objects.get(schema_name="public")``,
       y responde 404 si no la encuentra. Así que existe una fila de
       sistema, creada por la migración ``0002``, que no representa
       ninguna edición.

       Por eso ``objects`` **no puede filtrarla** —la librería la busca
       ahí— y existe ``Feria.reales`` aparte. **Todo listado de ferias
       usa ``reales``**; usar ``objects`` saca una feria fantasma en la
       pantalla de alguien, que es el error fácil de cometer aquí.
    """

    class Estado(models.TextChoices):
        EN_PREPARACION = "en_preparacion", "En preparación"
        ACTIVA = "activa", "Activa"
        ARCHIVADA = "archivada", "Archivada"

    nombre = models.CharField(max_length=120, help_text="P. ej. «FILEY 2027».")
    edicion = models.CharField(
        max_length=20,
        blank=True,
        help_text="Ordinal de la edición, p. ej. «XIV». Sale en constancias y programa.",
    )
    slug = models.SlugField(
        max_length=LARGO_MAX_SLUG,
        unique=True,
        validators=[validar_slug],
        help_text="Prefijo de la URL (/f/2027/) y raíz del schema. No cambia nunca.",
    )
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.EN_PREPARACION
    )
    sede = models.CharField(
        max_length=180,
        blank=True,
        help_text="Recinto de la edición entera, no el salón de cada cosa.",
    )
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    # `True`: al guardar una feria nueva se crea su schema y se migra.
    # Es lo que convierte el alta en una operación completa.
    auto_create_schema = True
    # `False`, y a propósito: borrar la fila NO debe tirar el schema con
    # todo el contenido de una edición. Para eso hay que pedirlo
    # explícitamente con `delete(force_drop=True)`.
    auto_drop_schema = False

    objects = models.Manager()
    reales = FeriaRealesManager()

    class Meta:
        verbose_name = "feria"
        verbose_name_plural = "ferias"
        ordering = ["-creada_en"]
        default_manager_name = "objects"

    def __str__(self):
        return self.nombre

    @property
    def es_la_de_sistema(self) -> bool:
        return self.schema_name == "public"

    @property
    def url(self) -> str:
        return f"/f/{self.slug}/"


class Domain(DomainMixin):
    """Mecánica de ``django-tenants``. No es un dominio.

    En modo subfolder la librería busca la feria por el segmento de URL
    usando este modelo, así que ``domain`` guarda **el slug** (`2027`),
    no un nombre de host. El nombre del modelo y del campo vienen de la
    librería y no se pueden cambiar.

    Duplica el valor de ``Feria.slug``. No se unifican porque son cosas
    distintas: ``slug`` es del modelo de dominio, ``Domain`` es del
    mecanismo de ruteo. El servicio de alta es el único sitio que
    escribe los dos, y hay una prueba que verifica que no divergen.
    """

    class Meta(DomainMixin.Meta):
        verbose_name = "slug de ruteo"
        verbose_name_plural = "slugs de ruteo"


class AdminFeria(models.Model):
    """Quién administra una feria, y cuál de ellos es su dueño.

    Vive en `public` porque relaciona dos entidades globales. Es lo que
    sustituye a ``RolPermiso``: el permiso se otorga **por feria**, no
    por módulo, y no hay nivel de solo lectura (`ADR-0004`).
    """

    feria = models.ForeignKey(
        Feria, on_delete=models.CASCADE, related_name="administradores"
    )
    # `ferias_admin` no es un nombre cualquiera: es lo que permite que
    # `Persona.es_administrativa` pregunte `self.ferias_admin.exists()`
    # sin que `registros` importe `ferias`. Las dependencias van en una
    # sola dirección (regla 4 de CLAUDE.md).
    persona = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ferias_admin",
    )
    es_dueno = models.BooleanField(
        default=False,
        help_text="El dueño es el único que da de alta administradores y convocatorias.",
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accesos_concedidos",
        help_text="Nulo en el dueño: lo designó el operador desde fuera de la feria.",
    )

    class Meta:
        verbose_name = "acceso a feria"
        verbose_name_plural = "accesos a ferias"
        ordering = ["-es_dueno", "creado_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["feria", "persona"], name="acceso_unico_por_feria_y_persona"
            ),
            # "Como mucho un dueño por feria". El "al menos uno" no es
            # expresable en la base —una feria se crea con su dueño en
            # la misma operación— y lo garantiza `servicios/altas.py`.
            models.UniqueConstraint(
                fields=["feria"],
                condition=Q(es_dueno=True),
                name="un_solo_dueno_por_feria",
            ),
        ]

    def __str__(self):
        papel = "dueño" if self.es_dueno else "administrador"
        return f"{self.persona} · {self.feria} ({papel})"
