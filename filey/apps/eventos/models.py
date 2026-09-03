"""
Modelos de `EVT` — la captura de propuestas del programa general.

Vive **dentro del schema de cada feria** (`ADR-0003`), como el resto del
contenido: ninguna tabla de aquí lleva `feria_id` y ninguna consulta
filtra por feria.

Lo que manda sobre este archivo es
``docs/requisitos/EVT/Modelo de datos - Eventos.md`` §2. Tres cosas que
el documento describe y aquí toman una forma concreta de Django:

``RouterSolicitudes`` **no se implementa aquí.** Es `RegistroConvocatoria`
de `apps/convocatorias`, que ya existe y ya la usa `STD`: quien se
inscribe a una convocatoria es una persona, y `FER` no sabe qué cuelga de
esa inscripción (`ADR-0006`). ``Solicitud.registro`` apunta ahí.

``RouterActividades`` **tampoco tiene tabla propia**: es `Actividad`. Con
herencia multitabla, el padre ya lleva el discriminador (``tipo``), la
liga con la solicitud y el enlace polimórfico hacia la fila hija, que
Django mantiene solo y con clave foránea de verdad. Un `detalle_id`
suelto, como está dibujado en el diagrama, no lo podría garantizar.

``RouterDocumentos`` es `Documento`, y por lo mismo su referencia a la
actividad es una clave foránea normal en vez de un entero polimórfico.

.. note:: Las ocho tablas de tipo repiten columnas a propósito

   Conversatorio y Mesa redonda coinciden hoy; Conferencia, Charla,
   Lectura de obra y Encuentro también. El documento las mantiene
   separadas para que cada tipo evolucione sin arrastrar a los demás
   (§2.7), y compartir una base abstracta desharía justo eso: cambiarla
   cambiaría varias tablas a la vez. Lo que sí se comparte son las
   *fábricas* de campo de abajo, que no acoplan nada — cada tabla
   enumera sus columnas.
"""

from django.conf import settings
from django.db import models

from apps.convocatorias.models import Convocatoria, RegistroConvocatoria
from comun.almacenamiento import CarpetaDeLaFeria, DocumentoAdmisible

#: Topes de captura, en caracteres. Son los mismos que enseña el
#: prototipo (`prototipo/EVT/app.js`), y aquí viajan en el campo para que
#: el formulario los herede sin repetirlos. `TextField` los aplica al
#: validar, no en la columna: PostgreSQL guarda texto sin tope y el día
#: que suban no hace falta migración.
MAX_SEMBLANZA = 2000
MAX_SINOPSIS = 2000
#: La sinopsis de un libro o una revista pide más espacio que la de una
#: charla, y así lo pedía ya la convocatoria en papel.
MAX_SINOPSIS_PUBLICACION = 4000


# ── Fábricas de campo ────────────────────────────────────────
#
# No son una base abstracta: devuelven un campo suelto para que cada
# tabla siga enumerando sus columnas una por una. Existen para no repetir
# ocho veces el `max_length` y el `verbose_name`, no para acoplar tablas.


def nombre_de(quien: str, n: int, *, obligatorio: bool = False):
    return models.CharField(
        f"nombre del {quien} {n}", max_length=160, blank=not obligatorio
    )


def semblanza_de(quien: str, n: int, *, obligatorio: bool = False):
    return models.TextField(
        f"semblanza del {quien} {n}",
        max_length=MAX_SEMBLANZA,
        blank=not obligatorio,
    )


def participa_el(quien: str, n: int):
    """Si esa persona estará presente en la actividad.

    Una casilla por autor o editor, y no un sí/no suelto más una lista de
    nombres escrita a mano: con cinco autores, «¿el autor participará?»
    no tiene respuesta, y la lista podía nombrar a alguien que no estaba
    entre los autores capturados (cambio del 2026-08-30, §2.7).

    Nace en **falso**: que alguien estará presente en la feria es una
    afirmación que hay que hacer, no algo que se dé por supuesto y haya
    que desmarcar. Marcarla por omisión llenaría el programa de
    asistentes que nadie confirmó.
    """
    return models.BooleanField(f"{quien} {n} participa", default=False)


class PublicoObjetivo(models.TextChoices):
    """A quién va dirigida la actividad. Conjunto cerrado (§2.4)."""

    PUBLICO_GENERAL = "publico_general", "Público en general"
    ACADEMICO = "academico", "Académico"
    ESTUDIANTIL = "estudiantil", "Estudiantil"
    INFANTIL = "infantil", "Infantil"
    FAMILIAS = "familias", "Familias"


class TipoPresentador(models.TextChoices):
    """Qué es el proponente respecto a la publicación que presenta."""

    AUTOR = "autor", "Autor/a"
    EDITOR = "editor", "Editor/a"
    ANTOLOGADOR = "antologador", "Antologador/a"
    COMPILADOR = "compilador", "Compilador/a"
    COORDINADOR = "coordinador", "Coordinador/a"


class CatalogoActividades(models.Model):
    """Los ocho tipos de actividad (§2.5).

    Es una tabla y no un `TextChoices` suelto porque el conjunto —que
    sigue siendo cerrado— hay que poder listarlo y ordenarlo para la
    interfaz sin tocar código, y porque es el discriminador al que apunta
    `Actividad.tipo`.
    """

    class Nombre(models.TextChoices):
        CONVERSATORIO = "conversatorio", "Conversatorio"
        CONFERENCIA = "conferencia", "Conferencia"
        CHARLA = "charla", "Charla"
        MESA_REDONDA = "mesa_redonda", "Mesa redonda"
        PRESENTACION_LIBRO = "presentacion_libro", "Presentación de libro"
        PRESENTACION_REVISTA = "presentacion_revista", "Presentación de revista"
        LECTURA_OBRA = "lectura_obra", "Lectura de obra"
        ENCUENTRO = "encuentro", "Encuentro"

    nombre = models.CharField(max_length=25, choices=Nombre.choices, unique=True)
    #: Para ordenar el selector sin depender del alfabeto ni del id.
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "tipo de actividad"
        verbose_name_plural = "tipos de actividad"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.get_nombre_display()


class ConfiguracionConvocatoria(models.Model):
    """Lo que `EVT` necesita saber de **una** convocatoria suya (§3.6).

    Una fila por convocatoria y no una por feria: una edición podría
    abrir más de una convocatoria de eventos, y el folio de cada una
    corre por separado.

    La crea el alta de la convocatoria, por el callback que esta app
    inscribe en `ADR-0006`; no hay que darla de alta a mano.
    """

    convocatoria = models.OneToOneField(
        Convocatoria,
        on_delete=models.CASCADE,
        related_name="configuracion_eventos",
    )
    #: Lo que va delante del id en el folio visible. El folio **no se
    #: almacena** (§2.4): se compone, así que cambiar el prefijo lo
    #: cambia en todas partes a la vez y no deja dos formatos conviviendo.
    prefijo_folio = models.CharField(max_length=10, default="EVE")

    class Meta:
        verbose_name = "configuración de la convocatoria de eventos"
        verbose_name_plural = "configuraciones de convocatoria de eventos"

    def __str__(self):
        return f"Configuración de {self.convocatoria.nombre}"


class Solicitud(models.Model):
    """Una propuesta de actividad (`CU-EVT-002`).

    Guarda lo que es **común a los ocho tipos**; lo que varía cuelga de
    `Actividad`. Lo que decide el administrador —categoría, dictamen,
    programación— es de la etapa 2 y no vive aquí.

    .. warning:: La invariante que la base de datos **no** puede sostener

       ``registro`` es una clave foránea real, pero el ``tipo`` que dice
       que esta convocatoria es de eventos vive un salto más allá, en
       `Convocatoria`. Nada en el esquema impide colgar una propuesta de
       un registro de una convocatoria de stands.

       Se comprueba en ``servicios/solicitudes.py``, que le pide el
       registro a `FER` declarando el tipo que espera. Es el mismo trato
       que tiene `STD`, y por el mismo motivo (`ADR-0006`).
    """

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente de revisión"
        ACEPTADA = "aceptada", "Aceptada"
        RECHAZADA = "rechazada", "Rechazada"
        CAMBIOS_SOLICITADOS = "cambios_solicitados", "Cambios solicitados"

    registro = models.ForeignKey(
        RegistroConvocatoria,
        on_delete=models.PROTECT,
        related_name="solicitudes_eventos",
        help_text="La inscripción de esta persona a esta convocatoria (FER).",
    )

    # ── Quién propone ────────────────────────────────────────
    #
    # La institución y el cargo se piden **por solicitud** y no viven en
    # `Persona`: la misma persona puede proponer una actividad
    # representando a su universidad y otra a su editorial (§2.1).
    institucion = models.CharField("dependencia o institución", max_length=180)
    cargo = models.CharField(max_length=120, blank=True)
    #: Autodeclaración. El administrador la valida o la corrige al
    #: revisar, y es la suya la que cuenta para el conteo por categoría
    #: (§2.4). Aquí solo se guarda lo que dijo quien propone.
    es_uady = models.BooleanField("se declara parte de la UADY", default=False)

    # ── La actividad, en lo que es común a los ocho tipos ────
    titulo_actividad = models.CharField(max_length=200)
    nombre_organizador_organizacion = models.CharField("organiza", max_length=180)
    #: Uno como máximo, y sin semblanza: es quien modera, no quien
    #: participa (§2.4).
    nombre_moderador = models.CharField("moderador/a", max_length=160, blank=True)
    #: Lista de valores de `PublicoObjetivo`, al menos uno. No está
    #: normalizado —el documento lo asume así— pero se guarda como JSON y
    #: no como texto separado por comas: filtrar por público es entonces
    #: un `contains` y no recorrer una cadena.
    publico_objetivo = models.JSONField(default=list)
    sinopsis = models.TextField(max_length=MAX_SINOPSIS_PUBLICACION)
    requiere_constancia = models.BooleanField(
        "solicita constancia de participación", default=False
    )
    comentarios = models.TextField("comentarios u observaciones", blank=True)

    #: Se aceptan las bases **de esta convocatoria**, al enviar. Es parte
    #: de lo que se envió, no del perfil de quien envía.
    bases_aceptadas = models.BooleanField("aceptó las bases", default=False)

    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    fecha_de_solicitud = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "solicitud"
        verbose_name_plural = "solicitudes"
        ordering = ["-fecha_de_solicitud"]

    def __str__(self):
        return f"{self.folio} · {self.titulo_actividad}"

    @property
    def folio(self) -> str:
        """`EVE-24`. Derivado, nunca almacenado (§2.4).

        Si la convocatoria todavía no tiene configuración —no debería
        pasar, la crea su alta— cae al prefijo por defecto en vez de
        reventar: un folio es una etiqueta, no una decisión.
        """
        configuracion = getattr(
            self.registro.convocatoria, "configuracion_eventos", None
        )
        prefijo = configuracion.prefijo_folio if configuracion else "EVE"
        return f"{prefijo}-{self.pk}"

    @property
    def persona(self):
        """Quién propuso. Se llega por el registro, nunca por una FK propia."""
        return self.registro.persona


class Actividad(models.Model):
    """La actividad de una solicitud, y el enrutador hacia su tipo.

    Es la tabla padre de las ocho de `Actividad_*`. Cumple el papel que
    el documento llama `RouterActividades` (§2.6): ``tipo`` es el
    discriminador y el enlace hacia la fila hija lo mantiene Django con
    una clave foránea de verdad.

    Una fila por solicitud: una propuesta es *una* actividad.
    """

    solicitud = models.OneToOneField(
        Solicitud, on_delete=models.CASCADE, related_name="actividad"
    )
    tipo = models.ForeignKey(
        CatalogoActividades, on_delete=models.PROTECT, related_name="actividades"
    )

    class Meta:
        verbose_name = "actividad"
        verbose_name_plural = "actividades"

    def __str__(self):
        return f"{self.tipo} de {self.solicitud.titulo_actividad}"

    @property
    def detalle(self):
        """La fila hija, con los campos propios del tipo.

        El nombre del atributo que Django crea para bajar del padre al
        hijo es el del modelo en minúsculas; se resuelve por el ``tipo``
        y no probando uno por uno.
        """
        return getattr(self, MODELO_POR_TIPO[self.tipo.nombre].__name__.lower())


# ── Las ocho tablas de tipo ──────────────────────────────────


class ActividadConversatorio(Actividad):
    nombre_participante_1 = nombre_de("participante", 1, obligatorio=True)
    semblanza_participante_1 = semblanza_de("participante", 1, obligatorio=True)
    nombre_participante_2 = nombre_de("participante", 2)
    semblanza_participante_2 = semblanza_de("participante", 2)
    nombre_participante_3 = nombre_de("participante", 3)
    semblanza_participante_3 = semblanza_de("participante", 3)

    class Meta:
        verbose_name = "conversatorio"
        verbose_name_plural = "conversatorios"


class ActividadMesaRedonda(Actividad):
    nombre_participante_1 = nombre_de("participante", 1, obligatorio=True)
    semblanza_participante_1 = semblanza_de("participante", 1, obligatorio=True)
    nombre_participante_2 = nombre_de("participante", 2)
    semblanza_participante_2 = semblanza_de("participante", 2)
    nombre_participante_3 = nombre_de("participante", 3)
    semblanza_participante_3 = semblanza_de("participante", 3)

    class Meta:
        verbose_name = "mesa redonda"
        verbose_name_plural = "mesas redondas"


class ActividadConferencia(Actividad):
    nombre_participante_1 = nombre_de("participante", 1, obligatorio=True)
    semblanza_participante_1 = semblanza_de("participante", 1, obligatorio=True)
    nombre_participante_2 = nombre_de("participante", 2)
    semblanza_participante_2 = semblanza_de("participante", 2)

    class Meta:
        verbose_name = "conferencia"
        verbose_name_plural = "conferencias"


class ActividadCharla(Actividad):
    nombre_participante_1 = nombre_de("participante", 1, obligatorio=True)
    semblanza_participante_1 = semblanza_de("participante", 1, obligatorio=True)
    nombre_participante_2 = nombre_de("participante", 2)
    semblanza_participante_2 = semblanza_de("participante", 2)

    class Meta:
        verbose_name = "charla"
        verbose_name_plural = "charlas"


class ActividadLecturaObra(Actividad):
    nombre_participante_1 = nombre_de("participante", 1, obligatorio=True)
    semblanza_participante_1 = semblanza_de("participante", 1, obligatorio=True)
    nombre_participante_2 = nombre_de("participante", 2)
    semblanza_participante_2 = semblanza_de("participante", 2)

    class Meta:
        verbose_name = "lectura de obra"
        verbose_name_plural = "lecturas de obra"


class ActividadEncuentro(Actividad):
    nombre_participante_1 = nombre_de("participante", 1, obligatorio=True)
    semblanza_participante_1 = semblanza_de("participante", 1, obligatorio=True)
    nombre_participante_2 = nombre_de("participante", 2)
    semblanza_participante_2 = semblanza_de("participante", 2)

    class Meta:
        verbose_name = "encuentro"
        verbose_name_plural = "encuentros"


class ActividadPresentacionLibro(Actividad):
    """Presentación de libro. Hasta cinco autores y dos presentadores.

    La sinopsis del libro **no está aquí**: es la de la solicitud, que
    admite hasta `MAX_SINOPSIS_PUBLICACION` caracteres. Quien acota a
    `MAX_SINOPSIS` los tipos que no son publicación es el formulario, no
    la columna.
    """

    titulo_publicacion = models.CharField("título del libro", max_length=200)
    tipo_presentador = models.CharField(
        "el proponente es", max_length=15, choices=TipoPresentador.choices
    )
    nombre_editorial = models.CharField("editorial", max_length=180)

    nombre_autor_1 = nombre_de("autor", 1, obligatorio=True)
    semblanza_autor_1 = semblanza_de("autor", 1, obligatorio=True)
    autor_1_participa = participa_el("autor", 1)
    nombre_autor_2 = nombre_de("autor", 2)
    semblanza_autor_2 = semblanza_de("autor", 2)
    autor_2_participa = participa_el("autor", 2)
    nombre_autor_3 = nombre_de("autor", 3)
    semblanza_autor_3 = semblanza_de("autor", 3)
    autor_3_participa = participa_el("autor", 3)
    nombre_autor_4 = nombre_de("autor", 4)
    semblanza_autor_4 = semblanza_de("autor", 4)
    autor_4_participa = participa_el("autor", 4)
    nombre_autor_5 = nombre_de("autor", 5)
    semblanza_autor_5 = semblanza_de("autor", 5)
    autor_5_participa = participa_el("autor", 5)

    # Presentadores. Opcionales los dos.
    nombre_participante_1 = nombre_de("presentador", 1)
    semblanza_participante_1 = semblanza_de("presentador", 1)
    nombre_participante_2 = nombre_de("presentador", 2)
    semblanza_participante_2 = semblanza_de("presentador", 2)

    class Meta:
        verbose_name = "presentación de libro"
        verbose_name_plural = "presentaciones de libro"


class ActividadPresentacionRevista(Actividad):
    """Presentación de revista. Hasta dos editores y dos presentadores."""

    titulo_publicacion = models.CharField("título de la revista", max_length=200)
    tipo_presentador = models.CharField(
        "el proponente es", max_length=15, choices=TipoPresentador.choices
    )
    nombre_editorial = models.CharField("editorial", max_length=180)

    nombre_editor_1 = nombre_de("editor", 1, obligatorio=True)
    semblanza_editor_1 = semblanza_de("editor", 1, obligatorio=True)
    editor_1_participa = participa_el("editor", 1)
    nombre_editor_2 = nombre_de("editor", 2)
    semblanza_editor_2 = semblanza_de("editor", 2)
    editor_2_participa = participa_el("editor", 2)

    nombre_participante_1 = nombre_de("presentador", 1)
    semblanza_participante_1 = semblanza_de("presentador", 1)
    nombre_participante_2 = nombre_de("presentador", 2)
    semblanza_participante_2 = semblanza_de("presentador", 2)

    class Meta:
        verbose_name = "presentación de revista"
        verbose_name_plural = "presentaciones de revista"


#: Qué tabla hija corresponde a cada valor del catálogo. Es lo que usa
#: `Actividad.detalle` para bajar del padre al hijo sin probar los ocho.
MODELO_POR_TIPO = {
    CatalogoActividades.Nombre.CONVERSATORIO: ActividadConversatorio,
    CatalogoActividades.Nombre.MESA_REDONDA: ActividadMesaRedonda,
    CatalogoActividades.Nombre.CONFERENCIA: ActividadConferencia,
    CatalogoActividades.Nombre.CHARLA: ActividadCharla,
    CatalogoActividades.Nombre.LECTURA_OBRA: ActividadLecturaObra,
    CatalogoActividades.Nombre.ENCUENTRO: ActividadEncuentro,
    CatalogoActividades.Nombre.PRESENTACION_LIBRO: ActividadPresentacionLibro,
    CatalogoActividades.Nombre.PRESENTACION_REVISTA: ActividadPresentacionRevista,
}

#: Los dos tipos que además piden archivos y ejemplar físico (`A1` del
#: CU-EVT-002). Se nombran una vez, aquí.
TIPOS_DE_PUBLICACION = (
    CatalogoActividades.Nombre.PRESENTACION_LIBRO,
    CatalogoActividades.Nombre.PRESENTACION_REVISTA,
)


class Documento(models.Model):
    """Un archivo de una actividad concreta (§2.8).

    Cuelga de `Actividad` y no de la solicitud: los adjuntos son del
    tipo, no del expediente. Hoy solo los piden los dos tipos de
    publicación; que otro tipo empiece a pedirlos no necesita migración,
    solo escribir filas con su `tipo_documento`.
    """

    class Tipo(models.TextChoices):
        PORTADA_LIBRO = "portada_libro", "Portada del libro"
        PORTADA_REVISTA = "portada_revista", "Portada de la revista"
        RETRATO_AUTOR = "retrato_autor", "Fotografía del autor/a"

    actividad = models.ForeignKey(
        Actividad, on_delete=models.CASCADE, related_name="documentos"
    )
    tipo_documento = models.CharField(max_length=20, choices=Tipo.choices)
    archivo = models.FileField(
        upload_to=CarpetaDeLaFeria("eventos"),
        # Misma lista blanca y mismo tope que el resto del sistema
        # (`ADR-0007`): estos archivos se entregan desde nuestro propio
        # origen, así que un `.html` subido sería XSS almacenado.
        validators=[DocumentoAdmisible()],
    )
    #: El nombre real en disco es un UUID (`ADR-0007`); sin esto no habría
    #: cómo decirle a nadie cuál archivo subió.
    nombre_original = models.CharField(max_length=255, blank=True)
    subido_en = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="documentos_eventos",
    )

    class Meta:
        verbose_name = "documento"
        verbose_name_plural = "documentos"
        ordering = ["tipo_documento"]

    def __str__(self):
        return f"{self.get_tipo_documento_display()} de {self.actividad}"
