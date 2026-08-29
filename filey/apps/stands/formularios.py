"""
Los formularios de `STD`.

Aquí solo vive lo que es de un formulario: qué campos se piden, cómo se
pintan y qué se rechaza antes de tocar la base. **Ninguna regla de
negocio** — si la convocatoria admite solicitudes, si ya hay una viva, si
se puede dictaminar — vive en `servicios/`, que es a quien llaman estos
formularios y también un comando de `manage.py`.
"""

from django import forms
from django.core.exceptions import ValidationError

from apps.registros.paises import opciones as opciones_de_pais
from comun.almacenamiento import DocumentoAdmisible
from comun.validadores import validar_cp

from .models import MATERIALES, TEMATICAS, Documento, Editorial


#: Cuántos sellos caben. El tope es del formulario, no del dominio: una
#: editorial puede representar a más, y el día que haga falta se sube.
MAXIMO_SELLOS = 10

#: Qué campo de la ficha se propone con qué dato de la cuenta.
#:
#: La ficha vuelve a pedir tres datos que la persona ya escribió al darse
#: de alta. Proponerlos ahorra tecleo, pero sobre todo evita el error de
#: escribir mal el propio correo justo en el campo por el que le vamos a
#: avisar del dictamen.
#:
#: Son **propuestas, no copias**: los tres pueden ser legítimamente
#: distintos —la cuenta personal de quien tramita frente al buzón
#: comercial de la editorial— y por eso se rellena `initial` y no el
#: valor guardado. Quien llena la ficha manda.
DE_LA_CUENTA = {
    "responsable_stand": "nombre_completo",
    "correo_electronico": "correo",
    "telefono_celular": "telefono",
}


class EditorialForm(forms.ModelForm):
    """La Ficha de Registro para Expositores (`CU-STD-001` paso 2).

    Es larga porque la ficha lo es. Lo que sí se decide aquí es **qué es
    obligatorio**: el director general y el celular sí; los otros tres
    cargos no, porque una editorial pequeña no los tiene y exigirlos
    dejaría fuera a quien puede exponer perfectamente.
    """

    materiales = forms.MultipleChoiceField(
        choices=[(m, m) for m in MATERIALES],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="¿Qué vas a exhibir?",
    )
    tematicas = forms.MultipleChoiceField(
        choices=[(t, t) for t in TEMATICAS],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="¿De qué temas?",
        help_text="Marca todas las que manejes. Ayudan a que el público te encuentre.",
    )
    class Meta:
        model = Editorial
        exclude = ["persona", "total_sellos", "creada_en", "actualizada_en"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"placeholder": "Razón social o nombre comercial"}
            ),
            "nombre_antepecho": forms.TextInput(
                attrs={"placeholder": "Ediciones del Mayab"}
            ),
            "telefono_oficina": forms.TextInput(attrs={"placeholder": "999 123 4567"}),
            "telefono_celular": forms.TextInput(attrs={"placeholder": "999 123 4567"}),
            "correo_electronico": forms.EmailInput(
                attrs={"placeholder": "contacto@editorial.mx"}
            ),
            "materiales_otro": forms.TextInput(
                attrs={"placeholder": "Solo si marcaste «Otro» arriba"}
            ),
            "tematicas_otra": forms.TextInput(
                attrs={"placeholder": "Solo si marcaste «Otros» arriba"}
            ),
        }

    def __init__(self, *args, persona=None, **kwargs):
        """
        :param persona: quién llena el formulario. Se usa para ordenar
            el desplegable de países, proponer el suyo por omisión y
            prellenar lo que la cuenta ya sabe (`DE_LA_CUENTA`). El
            formulario funciona igual sin ella: solo llega en blanco.
        """
        super().__init__(*args, **kwargs)
        # `total_sellos` no se pide: se deriva de cuántos sellos se
        # declaren (ver `servicios/solicitudes.py::guardar_editorial`).
        # Preguntarlo daría dos fuentes para el mismo número.
        for campo in ("director_comercial_email", "director_editorial_email",
                      "director_promocion_email", "telefono_oficina"):
            self.fields[campo].required = False

        # El país de la cuenta va arriba y viene marcado. Escribirlo a
        # mano en un campo de texto era la vía rápida a tener «Mexico»,
        # «MEX» y «méxico» conviviendo en la misma columna.
        suyo = (getattr(persona, "pais", "") or "").upper() or None
        self.fields["pais"].choices = opciones_de_pais(suyo)
        if not self.initial.get("pais") and not self.instance.pk:
            self.initial["pais"] = suyo or "MX"

        # Las etiquetas de los campos que llegaron de la cuenta, para que
        # la pantalla pueda decirlo. Vacía si no se propuso nada.
        self.prellenado = self._proponer_de_la_cuenta(persona)

    def _proponer_de_la_cuenta(self, persona) -> list[str]:
        """Rellena `initial` con lo que la cuenta ya sabe.

        Solo en la ficha en blanco. Con una ficha guardada la fuente es
        la ficha: si se repropusiera lo de la cuenta, quien cambiara su
        teléfono personal se encontraría cambiado el de la editorial sin
        haberlo tocado.

        Con el formulario ligado tampoco corre: ahí lo que se pinta es lo
        que se envió, y anunciar un prellenado que no se ve confunde.

        :returns: las etiquetas de los campos que se propusieron.
        """
        if persona is None or self.is_bound or self.instance.pk:
            return []

        propuestos = []
        for campo, atributo in DE_LA_CUENTA.items():
            valor = (getattr(persona, atributo, "") or "").strip()
            # Una cuenta técnica puede no tener teléfono (`blank=True`),
            # y un `initial` explícito de quien llame manda sobre esto.
            if valor and not self.initial.get(campo):
                self.initial[campo] = valor
                # En minúscula: Django capitaliza la etiqueta para
                # ponerla encima de la caja, y estas van dentro de una
                # frase, donde «Correo de contacto» a media línea se lee
                # como un error de mecanografía.
                etiqueta = self.fields[campo].label
                propuestos.append(etiqueta[:1].lower() + etiqueta[1:])
        return propuestos

    @property
    def prellenado_texto(self) -> str:
        """Los campos propuestos, enumerados como se dicen en voz alta.

        La coma y la «y» se arman aquí y no en la plantilla porque no hay
        filtro que las ponga; la frase que los envuelve sí es de la
        plantilla, que es de quien son las palabras.
        """
        if not self.prellenado:
            return ""
        *primeros, ultimo = self.prellenado
        return f"{', '.join(primeros)} y {ultimo}" if primeros else ultimo

    def clean(self):
        """Marcar «Otro» sin decir cuál no dice nada.

        Es la única validación cruzada de la ficha: el resto de campos se
        valida solo. Va aquí y no en el modelo porque lo que relaciona a
        los dos campos es la casilla, que es cosa del formulario.
        """
        datos = super().clean()

        # El código postal se valida **contra el país**, así que no puede
        # ser un validador del campo: necesita los dos valores ya
        # limpios. Cinco dígitos en México; fuera, algo razonable.
        try:
            validar_cp(datos.get("cp"), datos.get("pais"))
        except ValidationError as exc:
            self.add_error("cp", exc)

        for lista, texto, marca in (
            ("materiales", "materiales_otro", "Otro"),
            ("tematicas", "tematicas_otra", "Otros"),
        ):
            marcado = marca in (datos.get(lista) or [])
            escrito = (datos.get(texto) or "").strip()
            if marcado and not escrito:
                self.add_error(texto, "Dinos cuál, para que quien revise lo entienda.")
            if escrito and not marcado:
                datos[lista] = [*(datos.get(lista) or []), marca]
        return datos


class SellosForm(forms.Form):
    """Los sellos que la editorial representa, con su carta (`RN-17`).

    Cada fila es un nombre y el archivo que autoriza a representarlo. Van
    juntos y no en dos listas paralelas porque la carta es **de un
    sello**: separarlas dejaría tres archivos que nadie puede decir a
    cuál corresponden.

    Un formulario suelto y no un `formset` porque lo que se guarda es una
    lista corta y sin identidad propia; el `formset` traería gestión de
    `DELETE`, de orden y de `id` para nada.

    .. note:: Las diez filas se pintan **siempre**, y es la regla 6

       Sin JavaScript no hay forma de añadir una fila, así que el
       servidor manda las diez y el navegador enseña las que hacen falta.
       Sin Alpine se ven las diez y el formulario funciona igual: los
       nombres vacíos se descartan al guardar.
    """

    def __init__(self, *args, sellos_actuales=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actuales = list(sellos_actuales or [])
        for i in range(MAXIMO_SELLOS):
            self.fields[f"sello_{i}"] = forms.CharField(
                required=False,
                max_length=200,
                min_length=2,
                label=f"Sello {i + 1}",
                initial=self.actuales[i] if i < len(self.actuales) else "",
            )
            self.fields[f"carta_{i}"] = forms.FileField(
                required=False,
                label="Su carta de representación",
                help_text=(
                    "Con membrete del representado y firma de un ejecutivo "
                    "facultado."
                ),
                validators=[DocumentoAdmisible()],
            )

    @property
    def filas(self):
        """Las diez filas, para que la plantilla no arme nombres a mano."""
        return [
            (self[f"sello_{i}"], self[f"carta_{i}"]) for i in range(MAXIMO_SELLOS)
        ]

    @property
    def visibles_al_cargar(self) -> int:
        """Cuántas filas enseña Alpine de entrada.

        Las que ya tienen sello más una en blanco, y nunca menos de una:
        una pantalla que arranca sin ninguna caja no invita a escribir.

        **Ligado se cuenta lo enviado, no lo guardado.** Si se contaran
        los sellos guardados, un envío rechazado por otro campo volvía con
        una sola fila visible: los cinco sellos que la persona acababa de
        escribir seguían en el formulario y se enviaban otra vez, pero
        `x-show` los escondía y no había forma ni de verlos ni de
        borrarlos. Los que añadió en esta sesión no están guardados
        todavía, así que solo la propia respuesta sabe cuántos son.
        """
        if self.is_bound:
            llenos = sum(
                1
                for i in range(MAXIMO_SELLOS)
                if (self.data.get(f"sello_{i}") or "").strip()
            )
        else:
            llenos = len(self.actuales)
        return max(1, min(llenos + 1, MAXIMO_SELLOS))

    def declarados(self) -> list[tuple[str, object]]:
        """Los sellos escritos, sin vacíos y sin repetir, con su carta.

        Se descarta la carta de una fila sin nombre: un archivo sin sello
        al que pertenecer no autoriza nada.
        """
        vistos: dict[str, object] = {}
        for i in range(MAXIMO_SELLOS):
            nombre = (self.cleaned_data.get(f"sello_{i}") or "").strip()
            if not nombre or nombre in vistos:
                continue
            vistos[nombre] = self.cleaned_data.get(f"carta_{i}")
        return list(vistos.items())


class DocumentoForm(forms.Form):
    """Los adjuntos de la solicitud (`CU-STD-001` paso 3).

    La constancia fiscal y la lista de títulos son obligatorias la
    primera vez; al reenviar tras una petición de cambios no, porque las
    que ya se subieron siguen ahí y volver a pedirlas obligaría a
    recargar todo por corregir un teléfono (`CU-STD-002` A1).
    """

    # El mismo validador que el `FileField` del modelo, y hace falta en
    # los dos sitios: `Documento.objects.create()` **no** llama a
    # `full_clean()`, así que el del modelo solo protege al shell y al
    # admin. El del formulario es el que ve lo que llega de verdad, y
    # además convierte el rechazo en un error bajo el campo en vez de en
    # un 500.
    constancia_fiscal = forms.FileField(
        required=True,
        label="Constancia de situación fiscal",
        help_text="La necesitamos para poder facturarte.",
        validators=[DocumentoAdmisible()],
    )
    lista_titulos = forms.FileField(
        required=True,
        label="Lista de títulos",
        help_text=(
            "Los que traerás para exponer y vender. Sirve para referenciarte "
            "cuando el público pregunte por un título."
        ),
        validators=[DocumentoAdmisible()],
    )
    def __init__(self, *args, ya_hay_documentos=False, **kwargs):
        super().__init__(*args, **kwargs)
        if ya_hay_documentos:
            self.fields["constancia_fiscal"].required = False
            self.fields["lista_titulos"].required = False

    #: Qué tipo de `Documento` es cada campo. Las cartas de
    #: representación no están: cada una cuelga de su sello y las maneja
    #: `SellosForm`.
    TIPOS = {
        "constancia_fiscal": Documento.Tipo.CONSTANCIA_FISCAL,
        "lista_titulos": Documento.Tipo.LISTA_TITULOS,
    }


class BasesForm(forms.Form):
    """La firma de la ficha, en versión web (Ficha de Registro, p. 2).

    En papel es una línea bajo «RECONOZCO Y ACEPTO LAS BASES DE
    PARTICIPACIÓN», firmada por el responsable del stand. Aquí es una
    casilla obligatoria, y el nombre de quien firma ya lo trae la ficha
    en `responsable_stand`.
    """

    acepto = forms.BooleanField(
        required=True,
        label="Acepto las bases de participación",
        error_messages={
            "required": "Marca la casilla para poder enviar tu solicitud."
        },
    )


class DictamenForm(forms.Form):
    """Aceptar, rechazar o pedir cambios (`CU-STD-006`, `CU-STD-007`).

    Un solo formulario para las tres acciones porque las tres salen del
    mismo botón del detalle y comparten el motivo. Cuál se ejecuta lo
    decide `accion`, y que el motivo sea obligatorio al pedir cambios lo
    decide el servicio — no este formulario, para que un comando de
    `manage.py` no se salte la regla.
    """

    accion = forms.ChoiceField(
        choices=[
            ("aceptar", "Aceptar"),
            ("rechazar", "Rechazar"),
            ("cambios", "Solicitar cambios"),
        ]
    )
    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Falta la constancia fiscal vigente…",
            }
        ),
        label="Qué hace falta",
        help_text="Se le manda tal cual por correo. Sé concreto.",
    )
