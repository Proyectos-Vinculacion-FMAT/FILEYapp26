"""
Los formularios de `STD`.

Aquí solo vive lo que es de un formulario: qué campos se piden, cómo se
pintan y qué se rechaza antes de tocar la base. **Ninguna regla de
negocio** — si la convocatoria admite solicitudes, si ya hay una viva, si
se puede dictaminar — vive en `servicios/`, que es a quien llaman estos
formularios y también un comando de `manage.py`.
"""

from datetime import datetime, time
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.registros.paises import opciones as opciones_de_pais
from comun.almacenamiento import DocumentoAdmisible
from comun import validadores
from comun.validadores import validar_cp

from .models import (
    MATERIALES,
    TEMATICAS,
    ConfiguracionSistema,
    Documento,
    Editorial,
    Movimiento,
)


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
    # El domicilio de la editorial no es el de la persona, pero empieza
    # igual de menudo: quien tramita desde Mérida registra una editorial
    # yucateca. Se **propone**, no se impone —como el resto de
    # `DE_LA_CUENTA`, solo entra en la ficha en blanco y se puede
    # cambiar—, y las dos quedan vacías en una cuenta de fuera de México
    # porque ahí nunca se preguntaron (`CU-REG-001`).
    "estado": "estado_nombre",
    "municipio": "ciudad",
}


#: Cómo va cada dato, dicho antes de que alguien se equivoque.
#:
#: Se llenan en `__init__` y no en el modelo porque son ayuda **de
#: pantalla**: el modelo describe el dato, no cómo se teclea. Y solo las
#: que aportan algo — «Escribe el nombre» debajo de «Nombre» no aporta.
AYUDAS = {
    "nombre": "Como aparece en tu constancia de situación fiscal.",
    "cp": validadores.AYUDA_CP,
    "telefono_celular": validadores.AYUDA_TELEFONO,
    "telefono_oficina": validadores.AYUDA_TELEFONO,
    "correo_electronico": (
        "Por aquí te avisamos del dictamen. Puede ser distinto al de tu cuenta."
    ),
    "director_general_email": "Ejemplo: direccion@editorial.mx",
    "director_comercial_email": "Ejemplo: ventas@editorial.mx",
    "director_editorial_email": "Ejemplo: edicion@editorial.mx",
    "director_promocion_email": "Ejemplo: prensa@editorial.mx",
    "responsable_stand": "Quién estará al frente durante la feria.",
    "num_personas_atienden": "Al menos una.",
    "cantidad_libros_aprox": "Un aproximado basta; puedes poner 0 si aún no lo sabes.",
    "cantidad_titulos_aprox": "Títulos distintos, no ejemplares.",
    "domicilio_numero": "Exterior y, si aplica, interior.",
    "materiales_otro": "Solo si marcaste «Otro» arriba.",
    "tematicas_otra": "Solo si marcaste «Otros» arriba.",
}


class MarcaLosInvalidos:
    """Pinta de rojo el campo que falló, y se lo dice a quien no ve.

    Django no marca el control: pone el error debajo y deja la caja igual
    que las demás. En un formulario de treinta campos eso obliga a
    recorrerlo entero buscando de dónde salió el mensaje.

    Se hace en `add_error` —y no en `__init__`— porque hasta que la
    validación no corre no se sabe qué falló. `aria-invalid` va con la
    clase: el color no es información para quien usa un lector de
    pantalla, ni para quien no distingue el rojo.
    """

    def add_error(self, field, error):
        """Marca **todo lo que haya fallado**, no solo lo que llega aquí.

        Mirar el `field` del argumento parecía suficiente y no lo es: los
        errores que vienen de los validadores del **modelo** llegan en un
        solo `add_error(None, {...})` con un diccionario dentro, que
        Django reparte por su cuenta sin volver a pasar por aquí. Con la
        versión ingenua, `telefono_celular` —cuya regla vive en el
        modelo— nunca se marcaba, y el fallo era mudo: el mensaje salía
        debajo y la caja se quedaba igual que las demás.

        Recorrer los errores ya acumulados cubre los dos caminos y
        cualquier tercero que Django añada.
        """
        super().add_error(field, error)
        for nombre in self._errors or {}:
            if nombre not in self.fields:
                continue
            widget = self.fields[nombre].widget
            clases = widget.attrs.get("class", "")
            if "is-invalid" not in clases:
                widget.attrs["class"] = f"{clases} is-invalid".strip()


class EditorialForm(MarcaLosInvalidos, forms.ModelForm):
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
            # `pattern` y `title` salen de `comun/validadores.py`: el
            # navegador avisa antes de enviar con **la misma regla** que
            # el servidor comprueba después. Sin eso serían dos reglas
            # parecidas en dos idiomas, y divergirían.
            "telefono_oficina": forms.TextInput(
                attrs={
                    "placeholder": "999 123 4567",
                    "pattern": validadores.PATRON_TELEFONO,
                    "title": validadores.AYUDA_TELEFONO,
                    "inputmode": "tel",
                }
            ),
            "telefono_celular": forms.TextInput(
                attrs={
                    "placeholder": "999 123 4567",
                    "pattern": validadores.PATRON_TELEFONO,
                    "title": validadores.AYUDA_TELEFONO,
                    "inputmode": "tel",
                }
            ),
            "correo_electronico": forms.EmailInput(
                attrs={"placeholder": "contacto@editorial.mx"}
            ),
            "cp": forms.TextInput(
                attrs={
                    "placeholder": "97000",
                    "pattern": validadores.PATRON_CP,
                    "title": validadores.AYUDA_CP,
                    "inputmode": "numeric",
                }
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

        # Cómo se escribe cada dato, en los campos donde hay algo que
        # decir. **No en todos**: una ayuda debajo de cada una de las
        # treinta cajas es ruido, y el ruido deja de leerse justo en las
        # que sí importan.
        for campo, ayuda in AYUDAS.items():
            self.fields[campo].help_text = ayuda

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


class SellosForm(MarcaLosInvalidos, forms.Form):
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


class DocumentoForm(MarcaLosInvalidos, forms.Form):
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


class BasesForm(MarcaLosInvalidos, forms.Form):
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


class DictamenForm(MarcaLosInvalidos, forms.Form):
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


class AbonoForm(MarcaLosInvalidos, forms.Form):
    """El abono que reporta quien reserva (`CU-STD-016`).

    Es una **declaración con un papel adjunto**, no un cobro: aquí no se
    mueve dinero ni se toca el saldo. Lo que llega queda pendiente hasta
    que alguien lo compruebe contra el banco (`CU-STD-018`), y eso lo
    dice la pantalla al lado del botón.

    Lo que este formulario **no** comprueba es que el monto quepa en lo
    pendiente: esa es `CU-STD-016` E2 y vive en `servicios/pagos.py`,
    porque depende de los abonos ya validados y tiene que valer también
    desde un comando de `manage.py`.
    """

    monto = forms.DecimalField(
        label="Monto del pago",
        min_value=Decimal("0.01"),
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
        error_messages={
            "min_value": "El monto tiene que ser mayor que cero.",
        },
    )
    metodo = forms.ChoiceField(
        label="Método de pago",
        # `RN-08`: los tres dejan rastro bancario, que es lo que hace
        # comprobable la validación. El efectivo no está y no es un
        # olvido — no se puede validar contra nada.
        choices=Movimiento.Metodo.choices,
        widget=forms.RadioSelect,
    )
    # Obligatorio, como en el prototipo: sin el papel del banco no hay
    # nada que comprobar, y el abono se quedaría pendiente para siempre.
    # El servicio solo lo exige en los abonos que registra la
    # administración (`RN-15`) — ahí es la base la que lo sostiene; aquí
    # es la pantalla, porque es el único camino por el que llega.
    comprobante = forms.FileField(
        label="Comprobante de pago",
        required=True,
        help_text="El recibo del banco: transferencia, depósito o cheque.",
        validators=[DocumentoAdmisible()],
        error_messages={
            "required": (
                "Adjunta el comprobante. Sin él no podemos validar tu pago."
            )
        },
    )


class AbonoManualForm(AbonoForm):
    """El abono que asienta la administración (`CU-STD-019`).

    Los mismos tres campos que el del expositor, con otro texto: quien lo
    llena ya vio el dinero en el estado de cuenta, así que aquí el
    comprobante no es «tu recibo» sino el respaldo de una decisión — y es
    obligatorio por `RN-15`, no por costumbre.

    Nace validado y mueve el saldo en el acto, y eso se dice en la
    pantalla: es la diferencia con el otro formulario y no se puede
    deducir de los campos.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["monto"].label = "Monto del abono"
        self.fields["metodo"].label = "Cómo entró el dinero"
        self.fields["comprobante"].label = "Documento de respaldo"
        self.fields["comprobante"].help_text = (
            "Ficha de depósito, estado de cuenta o el oficio que autoriza "
            "el movimiento. Obligatorio (RN-15)."
        )
        self.fields["comprobante"].error_messages["required"] = (
            "Todo abono manual necesita un documento de respaldo. "
            "Adjúntalo para poder registrarlo."
        )


class DescuentoEspecialForm(MarcaLosInvalidos, forms.Form):
    """El descuento que otorga la administración (`CU-STD-020`, `RN-07`).

    **El motivo es obligatorio y el formulario no lo negocia**: es lo
    único que explica, meses después, por qué esa reserva costó menos.

    El porcentaje no tiene valor por omisión a propósito: `RN-07` dice
    que se fija caso por caso, y un número precargado es un número que
    alguien envía sin mirar.
    """

    porcentaje = forms.IntegerField(
        label="Porcentaje de descuento",
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={"step": "1", "placeholder": "15"}),
        error_messages={
            "min_value": "El porcentaje tiene que estar entre 1 y 100.",
            "max_value": "El porcentaje tiene que estar entre 1 y 100.",
        },
    )
    motivo = forms.CharField(
        label="Motivo",
        max_length=200,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": (
            "Convenio con la Secretaría de Cultura, oficio 214/2027."
        )}),
        help_text="Queda guardado con el descuento. Sé concreto: quien lo "
                  "lea dentro de un año no estuvo en la conversación.",
        error_messages={
            "required": (
                "Escribe el motivo del descuento: es dinero que la feria "
                "decide no cobrar."
            )
        },
    )


class ProrrogaForm(MarcaLosInvalidos, forms.Form):
    """Más plazo para cubrir el anticipo (`CU-STD-035`, paso 5).

    Un **día** en pantalla y un instante en la base: quien prorroga dice
    "hasta el 15", no "hasta el 15 a las 14:32". Se convierte al final de
    ese día porque «hasta el 15» incluye el 15 — con la medianoche de
    entrada, la reserva vencería la víspera de lo que se prometió.
    """

    fecha = forms.DateField(
        label="Nueva fecha límite",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        help_text="Hasta qué día tiene para cubrir el anticipo, incluido.",
        error_messages={"required": "Elige hasta cuándo se amplía el plazo."},
    )

    def clean_fecha(self):
        dia = self.cleaned_data["fecha"]
        if dia < timezone.localdate():
            raise ValidationError(
                "Esa fecha ya pasó: la reserva volvería a estar vencida hoy "
                "mismo."
            )
        return timezone.make_aware(
            datetime.combine(dia, time.max), timezone.get_current_timezone()
        )


class FechaDeCorteForm(MarcaLosInvalidos, forms.Form):
    """Hasta cuándo hay para liquidar (`CU-STD-036`, `RN-13`).

    Se puede vaciar: «sin fecha de corte» es un estado legítimo —una
    convocatoria puede no tenerla— y no un dato que se perdió.
    """

    fecha = forms.DateField(
        label="Corte del pago total",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        help_text="Déjala en blanco para quitar la fecha de corte.",
    )


class CancelacionForm(MarcaLosInvalidos, forms.Form):
    """Cerrar una reserva y devolver sus espacios (`CU-STD-035` A1).

    **La casilla no es burocracia.** Es la única acción irreversible del
    dominio y la única que libera espacios: el paso 2 del flujo pide
    confirmación explícita, y un botón suelto entre otros tres se pulsa
    por inercia.

    El motivo es opcional, como el del rechazo de un abono, y por lo
    mismo conviene: la editorial lo lee en su correo, y sin él solo sabe
    que perdió su lugar.
    """

    motivo = forms.CharField(
        label="Motivo",
        required=False,
        max_length=200,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": (
            "No cubrió el anticipo tras dos prórrogas."
        )}),
        help_text="Se le manda a la editorial y queda guardado en la reserva.",
    )
    entiendo = forms.BooleanField(
        label="Entiendo que los espacios vuelven al mapa y esto no se deshace",
        required=True,
        error_messages={
            "required": (
                "Marca la casilla para confirmar: cancelar libera los "
                "espacios y no se puede deshacer."
            )
        },
    )


class ConfiguracionForm(MarcaLosInvalidos, forms.ModelForm):
    """Los ajustes de una convocatoria de stands (`CU-STD-034`).

    Un solo formulario para las dos mitades —lo que cuesta y dónde se
    paga— porque es una sola pantalla y una sola decisión: abrir la
    venta. Partirlo obligaría a guardar dos veces para dejar la
    convocatoria operable.

    **No lleva `convocatoria`.** La fila la elige la URL, y ofrecerla
    como campo dejaría mover una configuración de una convocatoria a
    otra desde el navegador.

    Tampoco lleva `mapa_json`: importar un mapa reemplaza el showfloor
    entero y es del operador de la plataforma (`ADR-0005`), no de quien
    ajusta un precio. Vive en `/f/<slug>/django-admin/`.
    """

    class Meta:
        model = ConfiguracionSistema
        fields = [
            "costo_m2",
            "porcentaje_anticipo",
            "plazo_reserva_dias",
            "descuento_pronto_pago",
            "fecha_limite_pronto_pago",
            "fecha_corte_pago_total",
            "banco_titular",
            "banco_nombre",
            "banco_cuenta",
            "banco_clabe",
            "banco_sucursal",
            "banco_referencia",
            "instrucciones_pago",
        ]
        widgets = {
            # `type="date"` y no un calendario propio: el del navegador ya
            # sabe de meses y de bisiestos, y en el móvil abre el selector
            # nativo.
            "fecha_limite_pronto_pago": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "fecha_corte_pago_total": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "costo_m2": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "porcentaje_anticipo": forms.NumberInput(
                attrs={"min": "0", "max": "100"}
            ),
            "plazo_reserva_dias": forms.NumberInput(attrs={"min": "1"}),
            "descuento_pronto_pago": forms.NumberInput(
                attrs={"min": "0", "max": "100"}
            ),
            "instrucciones_pago": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Manda el comprobante el mismo día. Si pagas con "
                        "cheque, avísanos antes."
                    ),
                }
            ),
        }

    #: Ayudas de pantalla. Van aquí y no en el modelo por lo mismo que las
    #: de la ficha: el modelo describe el dato, no cómo se teclea.
    AYUDAS = {
        "costo_m2": "El precio base. Cada espacio cuesta esto por su superficie.",
        "porcentaje_anticipo": "Cuánto hay que cubrir para confirmar la reserva.",
        "plazo_reserva_dias": "Días que aguanta una reserva esperando el anticipo.",
        "descuento_pronto_pago": "Se aplica al reservar y se retira si vence el plazo.",
        "fecha_limite_pronto_pago": (
            "Es la misma para todos: quien reserva tarde tiene menos días."
        ),
        "fecha_corte_pago_total": (
            "La hereda cada reserva al confirmarse. Después se ajusta una "
            "por una; cambiarla aquí no mueve las que ya se confirmaron."
        ),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nombre, ayuda in self.AYUDAS.items():
            self.fields[nombre].help_text = ayuda
        # El precio nace en cero y con cero no se puede vender: se pide
        # aquí, que es la pantalla donde se pone, y no en el modelo — una
        # convocatoria recién creada tiene derecho a no tenerlo todavía.
        self.fields["costo_m2"].required = True

    def clean_costo_m2(self):
        costo = self.cleaned_data["costo_m2"]
        if costo <= 0:
            raise ValidationError(
                "Pon el costo por metro cuadrado: con cero, cada espacio "
                "saldría gratis."
            )
        return costo
