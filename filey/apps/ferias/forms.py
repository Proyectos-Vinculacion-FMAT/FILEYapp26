"""
Formularios del Core Ferias.

Como en `apps/registros/forms.py`: aquí solo vive la validación de
**forma** del dato. Si el correo ya tiene acceso, si la feria está
archivada o si la cuenta hay que crearla son reglas de negocio y viven
en `servicios/accesos.py`, donde se pueden llamar sin pasar por HTTP.
"""

from django import forms


class DarAccesoForm(forms.Form):
    """CU-FER-003, paso 3: a quién le doy acceso a mi feria.

    El nombre y el apellido son opcionales **a propósito**: lo normal es
    dar acceso a alguien que ya tiene cuenta en FILEY —fue proponente, o
    administra otra edición— y entonces sus datos ya están y no se
    tocan (A1). Solo hacen falta si la cuenta hay que crearla, y el
    dueño no tiene forma de saber de antemano cuál de los dos casos es.
    """

    correo = forms.EmailField(
        label="Correo electrónico",
        error_messages={
            "required": "Escribe el correo de la persona.",
            "invalid": "Ese correo no parece válido.",
        },
    )
    nombre = forms.CharField(label="Nombre(s)", max_length=80, required=False)
    primer_apellido = forms.CharField(
        label="Primer apellido", max_length=80, required=False
    )

    def clean_correo(self):
        return self.cleaned_data["correo"].strip().lower()

    def clean_nombre(self):
        return self.cleaned_data["nombre"].strip()

    def clean_primer_apellido(self):
        return self.cleaned_data["primer_apellido"].strip()
