"""
Deja el monolito listo para mirar `EVT` con los ojos, en local.

No es un `seed` de producción ni una fábrica de pruebas: es el atajo para
levantar la pantalla y verla, que es lo único que ni `pytest` ni
`manage.py check` contestan —si algo se ve mal, se ve mal aunque todas
las pruebas pasen—.

    python manage.py escenario_local

Es idempotente: correrlo dos veces no duplica nada. Lo que deja:

* una feria **activa** con slug `2027` (una recién creada nace
  `en_preparacion` y no la ve nadie de fuera);
* una convocatoria de eventos **abierta**, con su configuración de folio
  creada por el callback de `ADR-0006`;
* una cuenta de participante para entrar por OTP.

El código del OTP no sale por correo si no hay `RESEND_API_KEY`: arranca
el servidor con el backend de consola y el código se imprime ahí.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.ferias.models import Feria
from apps.ferias.servicios import altas as altas_de_feria
from apps.registros.models import Persona

SLUG = "2027"
CORREO_PARTICIPANTE = "laura@ejemplo.com"
CORREO_DUENO = "ana@uady.mx"


class Command(BaseCommand):
    help = "Feria, convocatoria de eventos y cuenta para probar EVT a mano."

    def handle(self, *args, **opciones):
        feria = self._feria()
        convocatoria = self._convocatoria(feria)
        persona = self._participante()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Escenario listo."))
        self.stdout.write("")
        self.stdout.write(f"  Catálogo de la feria   {feria.url}")
        self.stdout.write(
            f"  Formulario de propuesta {feria.url.rstrip('/')}"
            f"/eventos/{convocatoria.pk}/propuesta/"
        )
        self.stdout.write("")
        self.stdout.write(f"  Entrar como participante  {CORREO_PARTICIPANTE}")
        self.stdout.write(f"  Dueña de la feria         {CORREO_DUENO}")
        self.stdout.write("")
        self.stdout.write(
            "  El código del OTP se imprime en la consola del servidor si lo\n"
            "  levantas con EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend"
        )

    # ── Las piezas ───────────────────────────────────────────

    def _feria(self) -> Feria:
        feria = Feria.reales.filter(slug=SLUG).first()
        if feria is None:
            self.stdout.write("Creando la feria (esto migra su schema)…")
            feria = altas_de_feria.crear_feria(
                nombre="FILEY 2027",
                slug=SLUG,
                correo_dueno=CORREO_DUENO,
                nombre_dueno="Ana",
                primer_apellido_dueno="Pech",
                enviar_aviso=False,
                verbosity=0,
            ).feria

        # Una feria recién creada nace `en_preparacion` y el participante
        # solo ve las `activa`: sin esto, entrar diría que no hay ninguna
        # edición abierta, que es el síntoma que despista.
        if feria.estado != Feria.Estado.ACTIVA:
            feria.estado = Feria.Estado.ACTIVA
            feria.save(update_fields=["estado"])
            self.stdout.write("Feria activada.")
        return feria

    def _convocatoria(self, feria: Feria) -> Convocatoria:
        with schema_context(feria.schema_name):
            convocatoria = Convocatoria.objects.filter(
                tipo=TipoConvocatoria.EVT
            ).first()
            if convocatoria is None:
                from apps.convocatorias.servicios import altas

                convocatoria = altas.crear_convocatoria(
                    tipo=TipoConvocatoria.EVT,
                    nombre="Actividades FILEY 2027",
                ).convocatoria
                self.stdout.write("Convocatoria de eventos creada.")

            # Nace en `borrador`, y es `estado` —no las fechas— lo que abre
            # la puerta (`CU-FER-008`).
            if convocatoria.estado != Convocatoria.Estado.ABIERTA:
                convocatoria.estado = Convocatoria.Estado.ABIERTA
                convocatoria.save(update_fields=["estado"])
                self.stdout.write("Convocatoria abierta.")
            return convocatoria

    @transaction.atomic
    def _participante(self) -> Persona:
        persona = Persona.objects.filter(correo=CORREO_PARTICIPANTE).first()
        if persona is None:
            persona = Persona.objects.create_user(
                correo=CORREO_PARTICIPANTE,
                nombre="Laura",
                primer_apellido="Peniche",
                segundo_apellido="Uc",
                telefono="9994567890",
            )
            self.stdout.write("Cuenta de participante creada.")

        # Para que la precarga de la pantalla tenga algo que precargar.
        cambios = {}
        if not persona.pais:
            cambios["pais"] = "MX"
        if not persona.entidad:
            cambios["entidad"] = "YUC"
        if not persona.ciudad:
            cambios["ciudad"] = "Mérida"
        if cambios:
            for campo, valor in cambios.items():
                setattr(persona, campo, valor)
            persona.save(update_fields=list(cambios))
        return persona
