"""
Alta manual de cuentas administrativas (CU-REG-005, versión sin UI).

Mientras no exista pantalla de gestión de usuarios, los
administradores se dan de alta con este comando. Al crear el
permiso se avisa por correo a la persona con el enlace al panel;
el OTP en sí se emite cuando entra al login administrativo
(decisión 2026-07-22 del CU-REG-005).

Uso:
    python manage.py alta_admin hipolito@filey.org --nombre "Hipólito C." --modulo "*"
    python manage.py alta_admin elvira@filey.org --nombre "Elvira" --modulo TAL --nivel edicion
    python manage.py alta_admin elvira@filey.org --solo-aviso   # reenviar el correo
"""

from django.core.management.base import BaseCommand, CommandError

from apps.registros.models import Modulo, NivelPermiso, Persona, RolPermiso
from apps.registros.services import notificaciones


class Command(BaseCommand):
    help = "Da de alta una cuenta administrativa y su permiso de módulo (CU-REG-005)."

    def add_arguments(self, parser):
        parser.add_argument("correo", help="Correo con el que entrará al panel admin")
        parser.add_argument("--nombre", default="", help="Nombre completo")
        parser.add_argument("--telefono", default="", help="Teléfono (opcional)")
        parser.add_argument(
            "--modulo",
            default=Modulo.TODOS.value,
            choices=[m.value for m in Modulo],
            help='Módulo administrable: EVT, TAL, STD, VIS o "*" (todos; default)',
        )
        parser.add_argument(
            "--nivel",
            default=NivelPermiso.EDICION.value,
            choices=[n.value for n in NivelPermiso],
            help="Nivel del permiso: lectura o edicion (default)",
        )
        parser.add_argument(
            "--sin-aviso",
            action="store_true",
            help="No enviar el correo de aviso (útil en altas masivas)",
        )
        parser.add_argument(
            "--solo-aviso",
            action="store_true",
            help="Reenviar el aviso a una cuenta ya dada de alta, sin tocar permisos",
        )

    def handle(self, *args, **opciones):
        correo = opciones["correo"].lower().strip()

        # Reenvío manual: no se toca nada, solo se repite el correo.
        if opciones["solo_aviso"]:
            persona = Persona.objects.filter(correo=correo).first()
            if persona is None:
                raise CommandError(f"No existe ninguna cuenta con el correo {correo}.")
            if not persona.es_administrativa:
                raise CommandError(
                    f"{correo} no tiene permisos administrativos. "
                    "Dala de alta primero con --modulo."
                )
            self._avisar(persona, obligatorio=True)
            return

        # Paso 5: crear la Persona o reutilizarla (A1: ya era externa).
        persona = Persona.objects.filter(correo=correo).first()
        if persona is None:
            persona = Persona.objects.create_user(
                correo=correo,
                nombre_completo=opciones["nombre"],
                telefono=opciones["telefono"],
            )
            self.stdout.write(f"Persona creada: {correo}")
        else:
            self.stdout.write(f"Persona existente reutilizada: {correo}")
            if opciones["nombre"] and not persona.nombre_completo:
                persona.nombre_completo = opciones["nombre"]
                persona.save(update_fields=["nombre_completo"])

        # Paso 6 / E1: crear el RolPermiso o actualizar el nivel.
        rol, creado = RolPermiso.objects.update_or_create(
            persona=persona,
            modulo=opciones["modulo"],
            defaults={"nivel": opciones["nivel"]},
        )
        if not creado and rol.nivel != opciones["nivel"]:
            raise CommandError("No se pudo actualizar el nivel del permiso.")

        accion = "creado" if creado else "actualizado"
        self.stdout.write(
            self.style.SUCCESS(
                f"Permiso {accion}: {rol.modulo} ({rol.nivel}). "
                "Cuenta lista para iniciar sesión por OTP en el acceso administrativo."
            )
        )

        # Solo en el alta real: repetir el comando para cambiar el
        # nivel no debe volver a escribirle a la persona.
        if opciones["sin_aviso"]:
            self.stdout.write("Aviso omitido (--sin-aviso).")
        elif creado:
            self._avisar(persona)
        else:
            self.stdout.write(
                "El permiso ya existía: no se reenvía el aviso "
                "(usa --solo-aviso si quieres repetirlo)."
            )

    def _avisar(self, persona, *, obligatorio=False):
        """Envía el aviso de alta.

        Un fallo de correo no invalida el alta —el permiso ya está
        en la base y la persona puede entrar igual—, así que salvo
        que el aviso sea el objetivo del comando, solo se advierte.
        """
        try:
            notificaciones.avisar_alta_admin(persona)
        except notificaciones.AvisoFallido as exc:
            if obligatorio:
                raise CommandError(f"No se pudo enviar el aviso: {exc}") from exc
            self.stdout.write(
                self.style.WARNING(
                    f"El permiso quedó guardado, pero el aviso a {persona.correo} "
                    f"no se pudo enviar.\n  Detalle: {exc}\n"
                    f"  Reenvíalo con: manage.py alta_admin {persona.correo} --solo-aviso"
                )
            )
            return
        self.stdout.write(self.style.SUCCESS(f"Aviso enviado a {persona.correo}."))
