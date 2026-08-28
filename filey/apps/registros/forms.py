"""
Formularios del Core Registros.

Sustituyen a los serializers de DRF: mismas validaciones, pero
renderizando y reportando errores en HTML. Aquí solo vive la validación
de **forma** del dato (que sea un correo, que el teléfono traiga 10
dígitos); las reglas de negocio —si el correo ya existe, si toca
cool-down— son de `services/`, no del formulario.
"""

from django import forms

from comun import validadores

from .paises import PAIS_POR_DEFECTO, PAISES


class IdentificarForm(forms.Form):
    """Paso 1-2 de CU-REG-001/002/003: el correo con el que se entra."""

    correo = forms.EmailField(
        label="Correo electrónico",
        error_messages={
            "required": "Escribe tu correo electrónico.",
            "invalid": "Ese correo no parece válido.",
        },
    )

    def clean_correo(self):
        return self.cleaned_data["correo"].lower().strip()


class RegistroForm(forms.Form):
    """CU-REG-001: datos que se piden la primera vez.

    El correo no viaja en el formulario: se toma del flujo guardado en
    la sesión del servidor, así que nadie puede darle la vuelta al paso
    de identificación mandando otro correo en el POST.
    """

    nombre = forms.CharField(
        label="Nombre(s)",
        max_length=80,
        min_length=2,
        error_messages={
            "required": "Escribe tu nombre.",
            "min_length": "El nombre debe tener al menos 2 caracteres.",
        },
    )
    primer_apellido = forms.CharField(
        label="Primer apellido",
        max_length=80,
        min_length=2,
        error_messages={
            "required": "Escribe tu primer apellido.",
            "min_length": "El apellido debe tener al menos 2 caracteres.",
        },
    )
    # `required=False` no es un descuido: hay personas que no tienen
    # segundo apellido y la mayoría de los participantes extranjeros usan
    # uno solo (CU-REG-001, E1). Exigirlo dejaría fuera a quien el
    # sistema quiere dentro.
    segundo_apellido = forms.CharField(
        label="Segundo apellido",
        max_length=80,
        required=False,
    )
    telefono = forms.CharField(
        label="Número telefónico",
        max_length=20,
        error_messages={"required": "Escribe tu número telefónico."},
    )
    pais = forms.ChoiceField(
        label="País",
        choices=PAISES,
        initial=PAIS_POR_DEFECTO,
        error_messages={
            "required": "Elige tu país.",
            # Un valor fuera del catálogo no llega de un formulario
            # normal: llega de un POST fabricado a mano.
            "invalid_choice": "Ese país no está en la lista.",
        },
    )

    def clean_nombre(self):
        return self.cleaned_data["nombre"].strip()

    def clean_primer_apellido(self):
        return self.cleaned_data["primer_apellido"].strip()

    def clean_segundo_apellido(self):
        return self.cleaned_data["segundo_apellido"].strip()

    def clean_telefono(self):
        """E1: teléfono de al menos 10 dígitos (`CU-REG-001`).

        Se guarda solo con dígitos para que "999 000 0000" y
        "9990000000" sean el mismo teléfono al comprobar duplicados.

        La regla no se escribe aquí: vive en `comun/validadores.py`, que
        es lo mismo que valida el campo del modelo y lo que usa `STD` en
        su ficha de expositor. Cuando estaba escrita en este método,
        `Persona.telefono` la ignoraba por completo.

        Se valida **además de** normalizar, y no basta con el validador
        del campo: esto es un `forms.Form` y no un `ModelForm`, así que
        nada del modelo corre solo.
        """
        digitos = validadores.solo_digitos(self.cleaned_data["telefono"])
        validadores.telefono(digitos)
        return digitos


class CodigoForm(forms.Form):
    """Paso 7-8: el código de 6 dígitos que llegó por correo."""

    codigo = forms.RegexField(
        label="Código de acceso",
        regex=r"^\d{6}$",
        error_messages={
            "required": "Escribe el código que te llegó por correo.",
            "invalid": "El código son 6 dígitos.",
        },
    )
