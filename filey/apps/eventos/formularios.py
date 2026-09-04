"""
Los formularios de `EVT` — la captura de una propuesta (`CU-EVT-002`).

Aquí solo vive lo que es de un formulario: qué campos se piden, cómo se
pintan y qué se rechaza antes de tocar la base. **Ninguna regla de
negocio** —si la convocatoria admite envíos, si el registro corresponde
al tipo— vive en `servicios/`, que es a quien llaman estas clases y
también un comando de `manage.py`.

Son diez: uno con lo común a los ocho tipos, uno por tipo, y el del
dictamen (`CU-EVT-009`), que es el único del lado del administrador y por
eso vive al final, detrás de su propia cabecera. No hay un
formulario gigante con todo dentro porque los campos de un tipo son
obligatorios **solo si es el tipo elegido**, y expresar eso en un único
`clean()` acaba en una escalera de condicionales que nadie puede leer.

.. note:: La captura en cascada, del lado del servidor

   El prototipo abre la semblanza cuando el nombre tiene algo escrito, y
   no deja agregar a la siguiente persona hasta que la anterior está
   completa. Eso es comodidad de la pantalla; lo que impide de verdad que
   se guarde media persona o un hueco entre la 1 y la 3 es
   `validar_personas`, que corre aquí. Sin ella, un POST a mano dejaría
   `nombre_autor_3` con `nombre_autor_2` vacío, y las columnas del modelo
   dejarían de significar «los autores, en orden».
"""

from dataclasses import dataclass

from django import forms
from django.core.validators import FileExtensionValidator, MaxLengthValidator

from .models import (
    MAX_SINOPSIS,
    MAX_SINOPSIS_PUBLICACION,
    ActividadCharla,
    ActividadConferencia,
    ActividadConversatorio,
    ActividadEncuentro,
    ActividadLecturaObra,
    ActividadMesaRedonda,
    ActividadPresentacionLibro,
    ActividadPresentacionRevista,
    CatalogoActividades,
    Documento,
    PublicoObjetivo,
    Solicitud,
)

#: Renglones que ocupa un campo largo al abrirse. Django pinta diez por
#: omisión, y con eso una semblanza sola llena la pantalla y esconde lo
#: que viene detrás. Cinco caben sin empujar el resto, y el campo se
#: puede estirar —`resize: vertical`— si hace falta más.
RENGLONES = 5


def acortar_areas(formulario):
    """Deja los campos largos en `RENGLONES` renglones."""
    for campo in formulario.fields.values():
        if isinstance(campo.widget, forms.Textarea):
            campo.widget.attrs["rows"] = RENGLONES


#: Extensiones que se admiten para cada adjunto. Es lo que dice la
#: convocatoria en papel; la lista blanca de seguridad, que es otra cosa
#: y más amplia, la aplica `DocumentoAdmisible` al guardar (`ADR-0007`).
IMAGEN = ["jpg", "jpeg", "png"]
IMAGEN_O_PDF = ["jpg", "jpeg", "png", "pdf"]


# ── Cómo declara un tipo su orden de captura ─────────────────
#
# El orden **no lo decide la plantilla**: lo declara cada formulario, y es
# el del diagrama del modelo (`erDiagram - Captura de solicitudes.mmd`).
# Que esté aquí y no en el HTML es lo que permite compararlo con el
# diagrama sin abrir una plantilla, y lo que evita que Django y el
# prototipo se separen otra vez.
#
# Los **adjuntos no entran en `orden`**: van siempre al final, después de
# la sinopsis, y por eso se declaran aparte en `adjuntos`.


@dataclass(frozen=True)
class Campo:
    """Un campo suelto del tipo, por su nombre."""

    nombre: str


@dataclass(frozen=True)
class Personas:
    """Una lista de personas: su prefijo de columna, su tope y su rótulo."""

    prefijo: str
    maximo: int
    etiqueta: str


# ── La cascada de personas ───────────────────────────────────


def validar_personas(formulario, *, prefijo: str, maximo: int, etiqueta: str):
    """Que las personas capturadas sean 1..n seguidas y completas.

    Tres cosas, y las tres dejan datos que luego no significan nada:

    1. **La primera es obligatoria.** Una actividad sin nadie no es una
       actividad.
    2. **Nombre y semblanza van juntos.** Media persona no se puede
       imprimir en un programa ni mandar a un comité.
    3. **Sin huecos.** `nombre_autor_3` con el 2 vacío rompe la promesa
       de que las columnas son «los autores, en orden», que es de lo que
       depende cualquier listado que las recorra.
    """
    datos = formulario.cleaned_data
    visto_vacio = False

    for n in range(1, maximo + 1):
        campo_nombre = f"nombre_{prefijo}_{n}"
        campo_semblanza = f"semblanza_{prefijo}_{n}"
        nombre = (datos.get(campo_nombre) or "").strip()
        semblanza = (datos.get(campo_semblanza) or "").strip()

        if not nombre and not semblanza:
            visto_vacio = True
            continue

        if visto_vacio:
            formulario.add_error(
                campo_nombre,
                f"Completa {etiqueta} anterior antes de este: no puede quedar "
                "un hueco en medio.",
            )
            continue

        if not nombre:
            formulario.add_error(campo_nombre, f"Escribe el nombre de {etiqueta}.")
        if not semblanza:
            formulario.add_error(
                campo_semblanza, f"Escribe la semblanza de {etiqueta}."
            )


# ── Lo común a los ocho tipos ────────────────────────────────


class SolicitudForm(forms.ModelForm):
    """Los datos que no dependen del tipo de actividad (§2.4).

    Lo que el aplicante **no** captura aquí —su nombre, correo, teléfono,
    país, entidad y ciudad— sale de su cuenta y no viaja en el POST: la
    pantalla lo enseña, pero quien manda es `request.user` (paso 2 del
    CU). Institución y cargo sí, porque se piden por solicitud: la misma
    persona puede proponer representando a instituciones distintas.
    """

    publico_objetivo = forms.MultipleChoiceField(
        label="Público al que va dirigido",
        choices=PublicoObjetivo.choices,
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": "Elige al menos un público."},
    )
    bases_aceptadas = forms.BooleanField(
        label="Acepto las bases y condiciones",
        error_messages={
            "required": "Debes aceptar las bases y condiciones para enviar tu propuesta."
        },
    )

    class Meta:
        model = Solicitud
        fields = [
            "institucion",
            "cargo",
            "es_uady",
            "titulo_actividad",
            "nombre_organizador_organizacion",
            "nombre_moderador",
            "publico_objetivo",
            "sinopsis",
            "requiere_constancia",
            "comentarios",
            "bases_aceptadas",
        ]
        # Django compone el rótulo del nombre de la columna y le sale
        # «Titulo actividad», sin acento y sin artículo. Los que salen
        # bien vienen del `verbose_name` del modelo y no se repiten aquí.
        labels = {
            "titulo_actividad": "Título de la actividad",
            "sinopsis": "Sinopsis de la actividad",
            # Una casilla, no un sí/no que haya que contestar: sin marcar
            # ya es una respuesta —no la necesito— y por eso no lleva
            # asterisco. La duda de «¿contestó o se le olvidó?» no existe
            # cuando la opción por omisión es la inofensiva.
            "requiere_constancia": "Necesito constancia de participación",
        }
        error_messages = {
            "institucion": {"required": "Escribe la dependencia o institución."},
            "titulo_actividad": {"required": "Escribe el título de la actividad."},
            "nombre_organizador_organizacion": {"required": "Escribe quién organiza."},
            "sinopsis": {"required": "Escribe la sinopsis de la actividad."},
        }

    def __init__(self, *args, es_publicacion: bool = False, **kwargs):
        """
        :param es_publicacion: si el tipo elegido es libro o revista. Solo
            cambia el tope de la sinopsis: la de un libro pide más
            espacio que la de una charla, y así lo pedía ya la
            convocatoria en papel. La columna admite el tope mayor; quien
            acota a los demás es este formulario, para no obligar a una
            migración el día que cambie.
        """
        super().__init__(*args, **kwargs)
        tope = MAX_SINOPSIS_PUBLICACION if es_publicacion else MAX_SINOPSIS
        # Cambiar `max_length` a secas no basta: el validador se construye
        # con el campo, a partir del tope de la columna (el mayor de los
        # dos). Hay que sustituirlo, o el tope corto no se aplicaría y
        # solo se vería en el `maxlength` del HTML —que un POST a mano
        # ignora—.
        campo = self.fields["sinopsis"]
        campo.max_length = tope
        campo.validators = [
            v for v in campo.validators if not isinstance(v, MaxLengthValidator)
        ]
        campo.validators.append(MaxLengthValidator(tope))
        campo.widget.attrs["maxlength"] = tope
        campo.label = (
            "Sinopsis de la publicación" if es_publicacion else "Sinopsis de la actividad"
        )
        acortar_areas(self)

    def clean_publico_objetivo(self):
        # Se guarda como lista, no como texto separado por comas: filtrar
        # por público es entonces un `contains` y no recorrer una cadena.
        return list(self.cleaned_data["publico_objetivo"])


def exigir_presentador(formulario, *, prefijo: str, maximo: int, quienes: str):
    """Que la actividad no se quede sin nadie delante.

    En una presentación, quien la sostiene es cualquiera de dos cosas: un
    autor —o editor— que asista, o un presentador. Basta con uno de los
    dos, y sobra pedir el segundo:

    ==================================== ==========================
    Al menos un autor marcado como que   Los presentadores son
    asiste                               opcionales
    Ninguno asiste                       Hace falta al menos un
                                         presentador
    ==================================== ==========================

    Solo cuentan los que se capturaron: la casilla sin marcar de un autor
    que no existe no dice nada. Y solo cuenta la marca, no el nombre: un
    autor cuyo nombre está escrito pero que no asiste no sostiene nada.
    """
    datos = formulario.cleaned_data
    alguno_asiste = any(
        (datos.get(f"nombre_{prefijo}_{n}") or "").strip()
        and datos.get(f"{prefijo}_{n}_participa")
        for n in range(1, maximo + 1)
    )
    if not alguno_asiste and not (datos.get("nombre_participante_1") or "").strip():
        formulario.add_error(
            "nombre_participante_1",
            f"Nadie de {quienes} estará presente: hace falta al menos un "
            "presentador, o la actividad se queda sin nadie delante.",
        )


# ── Un formulario por tipo ───────────────────────────────────


class ActividadForm(forms.ModelForm):
    """Base de los ocho. No declara campos: solo el trato común.

    ``solicitud`` y ``tipo`` no se piden nunca: los pone el servicio, que
    es quien sabe de qué convocatoria y de quién es esta propuesta.
    """

    #: El orden de captura del tipo, calcado del diagrama del modelo.
    #: Cada subclase lo declara con `Campo` y `Personas`.
    orden = ()

    def __init__(self, *args, en_espera=None, **kwargs):
        """
        :param en_espera: ``{tipo_documento: ArchivoEnEspera}`` con lo que
            esa persona ya subió y no llegó a enviarse
            (`servicios/en_espera.py`). Lo que hace aquí es **quitar el
            obligatorio** a los adjuntos que ya tienen algo guardado.

            Sin esto, el archivo se conservaría pero el formulario lo
            seguiría pidiendo, y el segundo intento fallaría por el mismo
            campo que el primero — que es exactamente el problema que
            esto viene a resolver.
        """
        super().__init__(*args, **kwargs)
        acortar_areas(self)
        self.en_espera = en_espera or {}
        for nombre, tipo_documento in self.TIPO_POR_ADJUNTO.items():
            if tipo_documento in self.en_espera and nombre in self.fields:
                self.fields[nombre].required = False

    #: Los adjuntos que pide, por nombre de campo. Van al final de la
    #: pantalla, después de la sinopsis, no en el sitio que les tocaría
    #: por el diagrama.
    adjuntos = ()

    @property
    def personas(self):
        """Las listas de personas del tipo, sacadas de `orden`.

        Se deriva y no se declara aparte para que no puedan discrepar: si
        una lista está en el orden, se valida; si se valida, se pinta.
        """
        return tuple(x for x in self.orden if isinstance(x, Personas))

    def clean(self):
        datos = super().clean()
        for lista in self.personas:
            validar_personas(
                self,
                prefijo=lista.prefijo,
                maximo=lista.maximo,
                etiqueta=lista.etiqueta,
            )
        return datos

    #: Qué `Documento.Tipo` corresponde a cada campo de archivo. Los seis
    #: tipos que no piden adjuntos lo dejan vacío. Se declara aquí y no
    #: se deduce del nombre del campo porque el nombre es de la pantalla
    #: y el tipo es del modelo: `portada_libro` y `portada_revista` son
    #: dos campos y dos tipos, pero `retrato_autor` es el mismo nombre
    #: para los dos.
    TIPO_POR_ADJUNTO: dict = {}

    def documentos(self):
        """Los adjuntos de este envío, como ``(tipo, archivo)``.

        Devuelve **lo que llegó ahora**, no lo que hay en espera. Quien
        decide cuál de los dos usa es `views.py`, que es donde se sabe si
        el envío salió bien: al fallar, esto es lo que se mete en la cola;
        al ir bien, esto es lo que se completa con lo guardado.

        Vacío en los seis tipos que no llevan ninguno.
        """
        return tuple(
            (tipo_documento, self.cleaned_data.get(nombre))
            for nombre, tipo_documento in self.TIPO_POR_ADJUNTO.items()
        )


    # ── Cómo se agrupa esto en pantalla ──────────────────────
    #
    # El nombre y la semblanza de una persona se pintan juntos, y en
    # libro y revista además su casilla de participación. Agruparlos es
    # del formulario y no de la plantilla porque quien sabe cuántas
    # personas admite el tipo es esta clase: la plantilla solo recorre.

    def bloques(self):
        """Lo propio del tipo, en el orden que declara `orden`.

        Devuelve piezas ya listas para la plantilla, que solo recorre y
        pinta. Los adjuntos **no salen aquí**: van al final de la
        pantalla, con `campos_adjuntos`.
        """
        for pieza in self.orden:
            if isinstance(pieza, Campo):
                yield {"clase": "campo", "campo": self[pieza.nombre]}
            else:
                yield {"clase": "personas", "grupo": self._grupo(pieza)}

    def _grupo(self, lista):
        """Una lista de personas con sus filas, en orden."""
        filas = []
        for n in range(1, lista.maximo + 1):
            campo_participa = f"{lista.prefijo}_{n}_participa"
            filas.append(
                {
                    "n": n,
                    "etiqueta": f"{lista.etiqueta} {n}".capitalize(),
                    "nombre": self[f"nombre_{lista.prefijo}_{n}"],
                    "semblanza": self[f"semblanza_{lista.prefijo}_{n}"],
                    "participa": (
                        self[campo_participa]
                        if campo_participa in self.fields
                        else None
                    ),
                }
            )
        return {
            "prefijo": lista.prefijo,
            "maximo": lista.maximo,
            "singular": lista.etiqueta,
            "filas": filas,
        }

    def campos_adjuntos(self):
        """Los archivos que pide el tipo, cada uno con lo que ya se guardó.

        Devuelve ``[{"campo": BoundField, "guardado": ArchivoEnEspera|None}]``
        y no solo los campos, para que la plantilla no tenga que buscar
        en un diccionario por una clave variable — que en el lenguaje de
        plantillas de Django no se puede sin un filtro propio.

        Es el mismo trato que `bloques`: quien sabe cómo se agrupa esto
        es el formulario; la plantilla recorre y pinta.
        """
        return [
            {
                "campo": self[nombre],
                "guardado": self.en_espera.get(self.TIPO_POR_ADJUNTO.get(nombre)),
            }
            for nombre in self.adjuntos
        ]


class ConversatorioForm(ActividadForm):
    orden = (Personas("participante", 3, "el participante"),)

    class Meta:
        model = ActividadConversatorio
        exclude = ["solicitud", "tipo"]


class MesaRedondaForm(ActividadForm):
    orden = (Personas("participante", 3, "el participante"),)

    class Meta:
        model = ActividadMesaRedonda
        exclude = ["solicitud", "tipo"]


class ConferenciaForm(ActividadForm):
    orden = (Personas("participante", 2, "quien imparte"),)

    class Meta:
        model = ActividadConferencia
        exclude = ["solicitud", "tipo"]


class CharlaForm(ActividadForm):
    orden = (Personas("participante", 2, "quien imparte"),)

    class Meta:
        model = ActividadCharla
        exclude = ["solicitud", "tipo"]


class LecturaObraForm(ActividadForm):
    orden = (Personas("participante", 2, "quien imparte"),)

    class Meta:
        model = ActividadLecturaObra
        exclude = ["solicitud", "tipo"]


class EncuentroForm(ActividadForm):
    orden = (Personas("participante", 2, "quien imparte"),)

    class Meta:
        model = ActividadEncuentro
        exclude = ["solicitud", "tipo"]


class PresentacionLibroForm(ActividadForm):
    """`A1` del CU: además de los autores, pide archivos y ejemplar físico.

    Los presentadores son opcionales —los dos—, así que su cascada solo
    exige que no queden a medias ni con hueco, no que exista el primero.
    """

    # Calcado de `Actividad_PresentacionLibro` en el diagrama: título de la
    # publicación, rol del proponente, los autores con su casilla, los
    # presentadores y al final la editorial.
    orden = (
        Campo("titulo_publicacion"),
        Campo("tipo_presentador"),
        Personas("autor", 5, "el autor"),
        Personas("participante", 2, "el presentador"),
        Campo("nombre_editorial"),
    )
    adjuntos = ("retrato_autor", "portada_libro")
    TIPO_POR_ADJUNTO = {
        "retrato_autor": Documento.Tipo.RETRATO_AUTOR,
        "portada_libro": Documento.Tipo.PORTADA_LIBRO,
    }

    retrato_autor = forms.FileField(
        label="Fotografía del autor/a en alta resolución",
        help_text="JPG o PNG.",
        validators=[FileExtensionValidator(IMAGEN, message="La fotografía tiene que ser JPG o PNG.")],
        error_messages={"required": "Adjunta la fotografía del autor/a."},
    )
    portada_libro = forms.FileField(
        label="Portada del libro en alta resolución",
        help_text="JPG o PDF.",
        validators=[FileExtensionValidator(IMAGEN_O_PDF, message="La portada tiene que ser JPG, PNG o PDF.")],
        error_messages={"required": "Adjunta la portada del libro."},
    )

    class Meta:
        model = ActividadPresentacionLibro
        exclude = ["solicitud", "tipo"]

    def clean(self):
        datos = super().clean()
        # El primer autor es obligatorio; los presentadores no lo son
        # **salvo** que algún autor falte. La cascada de `ActividadForm` ya
        # exige que ninguna persona quede a medias.
        if not (datos.get("nombre_autor_1") or "").strip():
            self.add_error("nombre_autor_1", "Escribe el nombre del autor/a.")
        exigir_presentador(self, prefijo="autor", maximo=5, quienes="los autores")
        return datos




class PresentacionRevistaForm(ActividadForm):
    """`A1` del CU, con editores en vez de autores y una sola portada."""

    # Calcado de `Actividad_PresentacionRevista` en el diagrama.
    orden = (
        Campo("titulo_publicacion"),
        Campo("tipo_presentador"),
        Personas("editor", 2, "el editor"),
        Personas("participante", 2, "el presentador"),
        Campo("nombre_editorial"),
    )
    adjuntos = ("portada_revista",)
    TIPO_POR_ADJUNTO = {"portada_revista": Documento.Tipo.PORTADA_REVISTA}

    portada_revista = forms.FileField(
        label="Portada de la revista en alta resolución",
        help_text="JPG o PDF.",
        validators=[FileExtensionValidator(IMAGEN_O_PDF, message="La portada tiene que ser JPG, PNG o PDF.")],
        error_messages={"required": "Adjunta la portada de la revista."},
    )

    class Meta:
        model = ActividadPresentacionRevista
        exclude = ["solicitud", "tipo"]

    def clean(self):
        datos = super().clean()
        if not (datos.get("nombre_editor_1") or "").strip():
            self.add_error("nombre_editor_1", "Escribe el nombre del editor/a.")
        exigir_presentador(self, prefijo="editor", maximo=2, quienes="los editores")
        return datos




#: Qué formulario corresponde a cada tipo del catálogo. Es el gemelo de
#: `MODELO_POR_TIPO`, y la prueba que los compara es lo que impide que
#: uno crezca sin el otro.
FORMULARIO_POR_TIPO = {
    CatalogoActividades.Nombre.CONVERSATORIO: ConversatorioForm,
    CatalogoActividades.Nombre.MESA_REDONDA: MesaRedondaForm,
    CatalogoActividades.Nombre.CONFERENCIA: ConferenciaForm,
    CatalogoActividades.Nombre.CHARLA: CharlaForm,
    CatalogoActividades.Nombre.LECTURA_OBRA: LecturaObraForm,
    CatalogoActividades.Nombre.ENCUENTRO: EncuentroForm,
    CatalogoActividades.Nombre.PRESENTACION_LIBRO: PresentacionLibroForm,
    CatalogoActividades.Nombre.PRESENTACION_REVISTA: PresentacionRevistaForm,
}


# ── El lado del administrador (`CU-EVT-009`) ─────────────────


class DictamenForm(forms.Form):
    """Aceptar, solicitar cambios o rechazar una propuesta.

    Un solo formulario para las tres acciones porque las tres salen del
    mismo panel del detalle y comparten el campo de texto. Cuál se ejecuta
    lo decide ``accion``.

    **Lo que este formulario no comprueba** es que el texto esté lleno
    cuando hace falta, ni que la clasificación venga al aceptar: eso lo
    decide `servicios/dictamen.py`. Es la `E3` del caso de uso, y vive
    allí para que un comando de `manage.py` no se la pueda saltar —si la
    regla estuviera aquí, solo la cumpliría quien pase por HTTP—.
    """

    accion = forms.ChoiceField(
        choices=[
            ("aceptar", "Aceptar"),
            ("cambios", "Solicitar cambios"),
            ("rechazar", "Rechazar"),
        ]
    )
    categoria = forms.ChoiceField(
        choices=Solicitud.Categoria.choices,
        required=False,
        label="Clasificación",
        help_text="Es lo que hace contable la propuesta frente a la meta "
        "de la convocatoria.",
    )
    #: Casilla y no un sí/no explícito: **no marcada ya es una respuesta**
    #: —no es de la UADY— y es la que corresponde a la mayoría. La
    #: pantalla la trae premarcada con lo que declaró quien propuso
    #: (`Solicitud.uady_sugerido`), que es lo que el §3.1 llama validar o
    #: corregir la autodeclaración.
    es_uady_confirmado = forms.BooleanField(
        required=False,
        label="Pertenece a la UADY",
    )
    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": RENGLONES,
                "placeholder": "Falta la semblanza de un participante y "
                "precisar la duración estimada…",
            }
        ),
        label="Qué debe corregir, o por qué se rechaza",
        help_text="Se le manda tal cual. Sé concreto.",
    )
    #: La «doble verificación» que pide `A3` paso 3 al cambiar un dictamen
    #: ya emitido. Solo la pinta la pantalla cuando la propuesta ya está
    #: resuelta; en el caso normal ni aparece, porque pedir confirmación
    #: para el trabajo de todos los días la convierte en un reflejo y deja
    #: de proteger de nada.
    confirmar = forms.BooleanField(
        required=False,
        label="Entiendo que esto cambia un resultado ya emitido",
    )
