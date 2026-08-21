"""
Modelos del Core Registros (REG).

Entidades definidas por los CU-REG-001…006:

- ``Persona``   — la cuenta única del sistema (externos y administrativos).
- ``RolPermiso`` — lo que distingue a un administrador: tener al menos uno.
- ``SesionOTP`` — código de un solo uso, guardado hasheado (CU-REG-002).
"""

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class Modulo(models.TextChoices):
    """Módulos administrables del sistema FILEY."""

    EVT = "EVT", "Actividades FILEY (Eventos)"
    TAL = "TAL", "Actividades Infantiles/Juveniles"
    STD = "STD", "Stands"
    VIS = "VIS", "Visitas Escolares"
    TODOS = "*", "Todos los módulos (administrador general)"


class NivelPermiso(models.TextChoices):
    LECTURA = "lectura", "Solo lectura"
    EDICION = "edicion", "Edición"


# Los niveles se acumulan: quien puede editar también puede leer. El
# orden se declara aquí, una sola vez, para que ningún módulo lo
# reinvente al comprobar permisos.
FUERZA_NIVEL = {NivelPermiso.LECTURA: 1, NivelPermiso.EDICION: 2}


class PersonaManager(BaseUserManager):
    """Manager del usuario. No hay contraseñas: el acceso es por OTP."""

    use_in_migrations = True

    def create_user(self, correo, nombre_completo="", telefono="", **extra):
        if not correo:
            raise ValueError("El correo es obligatorio")
        persona = self.model(
            correo=self.normalize_email(correo).lower(),
            nombre_completo=nombre_completo,
            telefono=telefono,
            **extra,
        )
        persona.set_unusable_password()  # login únicamente por OTP
        persona.save(using=self._db)
        return persona

    def create_superuser(self, correo, password=None, **extra):
        """Superusuario del admin de Django (uso interno del equipo)."""
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        persona = self.model(correo=self.normalize_email(correo).lower(), **extra)
        if password:
            persona.set_password(password)
        else:
            persona.set_unusable_password()
        persona.save(using=self._db)
        return persona


class Persona(AbstractBaseUser, PermissionsMixin):
    """Cuenta única del sistema (CU-REG-001).

    Integra el sistema de roles/permisos de Django vía
    ``PermissionsMixin`` (groups, user_permissions, is_superuser);
    los permisos de negocio por módulo viven en ``RolPermiso``.
    """

    class Estado(models.TextChoices):
        ACTIVA = "activa", "Activa"
        INACTIVA = "inactiva", "Inactiva"

    correo = models.EmailField(unique=True)
    nombre_completo = models.CharField(max_length=180)
    telefono = models.CharField(max_length=20, blank=True)
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ACTIVA
    )
    fecha_registro = models.DateTimeField(default=timezone.now)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    # Integración con el admin de Django (no es el "admin FILEY")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = PersonaManager()

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "persona"
        verbose_name_plural = "personas"

    def __str__(self):
        return self.correo

    @property
    def es_administrativa(self):
        """Un administrador es quien tiene al menos un RolPermiso (CU-REG-003)."""
        return self.roles.exists()

    def modulos_administrables(self):
        """Módulos a los que puede entrar en el panel admin (CU-REG-006)."""
        roles = list(self.roles.all())
        if any(r.modulo == Modulo.TODOS for r in roles):
            return [m for m in Modulo if m != Modulo.TODOS]
        return [Modulo(r.modulo) for r in roles]

    def puede_administrar(self, modulo, nivel=NivelPermiso.LECTURA) -> bool:
        """¿Tiene permiso sobre este módulo, al menos con este nivel?

        Es la pregunta que hará cada módulo de dominio (EVT, TAL, STD,
        VIS) antes de dejar entrar a una pantalla suya, a través de
        ``permisos.requiere_modulo``. Vive en el modelo —y no en cada
        vista— porque la respuesta depende solo de los datos de la
        cuenta: el rol ``*`` cubre todos los módulos, y ``edicion``
        cubre también lo que solo pide ``lectura``.
        """
        requerido = FUERZA_NIVEL[NivelPermiso(nivel)]
        modulo = Modulo(modulo).value
        for rol in self.roles.all():
            if rol.modulo in (modulo, Modulo.TODOS):
                if FUERZA_NIVEL[NivelPermiso(rol.nivel)] >= requerido:
                    return True
        return False


class RolPermiso(models.Model):
    """Permiso de módulo de una cuenta administrativa (CU-REG-005)."""

    persona = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="roles"
    )
    modulo = models.CharField(max_length=3, choices=Modulo.choices)
    nivel = models.CharField(
        max_length=10, choices=NivelPermiso.choices, default=NivelPermiso.EDICION
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "rol/permiso"
        verbose_name_plural = "roles/permisos"
        constraints = [
            # E1 de CU-REG-005: no duplicar permiso del mismo módulo
            models.UniqueConstraint(
                fields=["persona", "modulo"], name="unico_permiso_por_modulo"
            )
        ]

    def __str__(self):
        return f"{self.persona} · {self.modulo} ({self.nivel})"


class SesionOTPQuerySet(models.QuerySet):
    def vigentes(self, persona):
        return self.filter(
            persona=persona, usado=False, expira_en__gt=timezone.now()
        )


class SesionOTP(models.Model):
    """Código de un solo uso enviado por correo (CU-REG-002 / 003).

    El código NUNCA se guarda en claro: se almacena con el mismo
    hasher que Django usa para contraseñas (PBKDF2, estándar del
    sector). ``usado=True`` lo quema; ``intentos`` acota a 3 por
    código (E1); el reenvío invalida el anterior (A1/E5).
    """

    class Canal(models.TextChoices):
        CORREO = "correo", "Correo electrónico"

    persona = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sesiones_otp"
    )
    codigo_hash = models.CharField(max_length=128)
    canal = models.CharField(
        max_length=10, choices=Canal.choices, default=Canal.CORREO
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado = models.BooleanField(default=False)
    intentos = models.PositiveSmallIntegerField(default=0)
    # Un código puede quedar `usado` por tres motivos distintos: se
    # acertó, se agotaron los intentos o lo reemplazó un reenvío. Solo
    # el primero debe limpiar el historial de fallos de la cuenta, y
    # desde fuera los tres se ven igual — de ahí este campo.
    acertado = models.BooleanField(default=False)

    objects = SesionOTPQuerySet.as_manager()

    class Meta:
        verbose_name = "sesión OTP"
        verbose_name_plural = "sesiones OTP"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"OTP {self.persona} ({'usado' if self.usado else 'vigente'})"

    # ── Operaciones sobre el código ──────────────────────────

    def establecer_codigo(self, codigo: str):
        self.codigo_hash = make_password(codigo)

    def codigo_coincide(self, codigo: str) -> bool:
        return check_password(codigo, self.codigo_hash)

    @property
    def expirado(self) -> bool:
        return timezone.now() >= self.expira_en

    @property
    def intentos_restantes(self) -> int:
        return max(settings.OTP_INTENTOS_MAX - self.intentos, 0)
