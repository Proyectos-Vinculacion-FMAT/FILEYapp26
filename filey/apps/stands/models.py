"""
Stands — venta de espacios del showfloor (`STD`, capa por feria).

Vive **dentro del schema de cada feria** (`ADR-0003`), así que ninguna
tabla de aquí lleva `feria_id`: la edición es el schema en el que la
conexión está mirando, no una columna. Rediseñar el showfloor de 2028 no
toca nada de 2027.

La cadena entera del dominio, de fuera hacia dentro::

    Persona → RegistroConvocatoria → Solicitud → Editorial → Reserva

Las dos primeras son de otros dominios —`REG` y `FER`—; `STD` empieza en
`Solicitud`. Ni `Reserva` ni `Movimiento` necesitan saber a qué
convocatoria pertenecen: llegan a ella por la solicitud.

Esta fase construye el expediente y su dictamen (`CU-STD-001` a `008`).
El mapa, la reserva y el pago llegan después.
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone

from apps.convocatorias.models import Convocatoria, RegistroConvocatoria
from apps.registros.paises import PAISES
from comun.almacenamiento import CarpetaDeLaFeria, DocumentoAdmisible
from comun.validadores import telefono as validar_telefono


class Giro(models.TextChoices):
    """A qué se dedica la editorial. Viene de la Ficha de Registro.

    Son **solo estos tres**, y es una decisión, no un descuido. Las bases
    de participación admiten además "instituciones de educación superior,
    librerías, asociaciones civiles y dependencias gubernamentales", así
    que los dos documentos se contradicen. Se le hace caso a la ficha
    (decisión del equipo, 2026-08-28): es el formulario que la gente
    llena y firma, mientras que las bases describen **quién puede
    participar**, no cómo se clasifica.

    Una universidad sí puede exponer; al llenar la ficha elige el giro
    que más se le parezca. Si eso resulta incómodo, la salida es añadir
    una opción aquí, no volver a abrir la contradicción.
    """

    EDITOR = "editor", "Editor"
    LIBRERO = "librero", "Librero"
    DISTRIBUIDOR = "distribuidor", "Distribuidor"


#: Qué exhibe la editorial. Los seis de la Ficha de Registro, p. 2.
MATERIALES = [
    "Libro",
    "Audiolibro",
    "Revista",
    "Material didáctico",
    "Libros electrónicos",
    "Otro",
]

#: Sobre qué. Las 61 de la Ficha de Registro, p. 2, en su orden.
#:
#: Contrastadas contra la ficha y dadas por buenas el 2026-08-28. Hizo
#: falta mirarlas: la ficha es un escaneo sin capa de texto, así que
#: estas 61 se transcribieron leyendo la imagen columna por columna, y
#: una lista así de larga leída de un escaneo es donde se esconde una
#: errata.
#:
#: .. note:: Dos correcciones sobre el papel
#:
#:    La ficha impresa trae «Braile» y «Sofware», y repite «Pintura» dos
#:    veces en la tercera columna. Aquí van escritas bien y sin repetir:
#:    son erratas del formato, no temáticas distintas.
TEMATICAS = [
    "Administración",
    "Agronomía",
    "Antropología",
    "Arquitectura",
    "Arte",
    "Astronomía",
    "Autoayuda",
    "Biografías",
    "Braille",
    "Ciencias sociales",
    "Ciencia y tecnologías",
    "Cine",
    "Cocina",
    "Comics",
    "Comercio",
    "Computación",
    "Comunicación",
    "Contabilidad",
    "Deporte",
    "Derecho",
    "Diccionario/Enciclopedia",
    "Discapacidad intelectual",
    "Discapacidad motriz",
    "Discapacidad psíquica",
    "Discapacidad sensorial y de comunicación",
    "Diseño",
    "Ecología",
    "Economía",
    "Educación",
    "Enfermería",
    "Espiritualidad",
    "Filosofía",
    "Física",
    "Geografía",
    "Historia",
    "Idiomas",
    "Infantil",
    "Ingeniería",
    "Lingüísticas",
    "Literatura",
    "Matemáticas",
    "Medicina",
    "Multimedia",
    "Música",
    "Ordenadores",
    "Pedagogía",
    "Pintura",
    "Poesía",
    "Política",
    "Psicología",
    "Química",
    "Religión",
    "Sexualidad",
    "Sociología",
    "Software",
    "Teatro",
    "Textos editoriales",
    "Turismo",
    "Veterinaria",
    "Video",
    "Otros",
]


def _validar_opciones(valores, permitidas, campo):
    """Que una lista multivalor solo traiga opciones del catálogo.

    Se comprueba en `clean()` y no con un `CheckConstraint` porque lo que
    se guarda es JSON: PostgreSQL podría validarlo, pero la expresión
    sería ilegible y habría que reescribirla cada vez que el catálogo
    crezca.
    """
    if not isinstance(valores, list):
        raise ValidationError({campo: "Se esperaba una lista de opciones."})
    desconocidas = [v for v in valores if v not in permitidas]
    if desconocidas:
        raise ValidationError(
            {campo: f"No están en el catálogo: {', '.join(map(str, desconocidas))}."}
        )


class Editorial(models.Model):
    """La ficha de registro de quien quiere exponer.

    **Una por persona y por feria, en los dos sentidos** (`RN-21`). Es un
    `OneToOne` de verdad y no una convención: representar a otras casas
    editoras no se modela con una segunda `Editorial` sino con
    `SelloEditorial` y su carta de representación (`RN-17`).

    .. note:: Se vuelve a llenar cada edición, y es lo correcto

       Una editorial que expone en 2027 y en 2028 tiene **dos** filas
       —una en cada schema— y **una sola** `Persona` detrás. La ficha
       cambia entre ediciones: domicilio, directores, número de sellos.
       Lo que no cambia —quién es la persona— no se duplica.
    """

    persona = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="editorial",
        help_text="Quién presenta y administra esta editorial en esta feria.",
    )
    nombre = models.CharField(
        "nombre de la editorial",
        max_length=200,
        # Mismo mínimo que `Convocatoria.nombre`, y por lo mismo: es lo
        # que identifica a la editorial en todas las pantallas, y un
        # nombre de una letra es una tecla suelta, no una editorial.
        validators=[MinLengthValidator(3)],
    )

    # ── Domicilio ─────────────────────────────────────────────
    domicilio_calle = models.CharField("calle", max_length=160)
    domicilio_numero = models.CharField("número", max_length=40)
    domicilio_colonia = models.CharField("colonia", max_length=120)
    cp = models.CharField("código postal", max_length=10)
    municipio = models.CharField("municipio", max_length=120)
    estado = models.CharField("estado", max_length=120)
    # El **código** de dos letras, no el nombre — igual que `Persona.pais`
    # y por el mismo motivo que explica `registros/paises.py`: el nombre
    # de un país cambia y se escribe de varias formas, el código no.
    # Guardarlos igual es además lo que permite proponer por omisión el
    # país de la cuenta.
    pais = models.CharField("país", max_length=2, choices=PAISES, default="MX")

    # ── Contactos ─────────────────────────────────────────────
    # Los cuatro cargos que pide la Ficha de Registro. Solo el general es
    # obligatorio: una editorial pequeña no tiene los cuatro puestos, y
    # exigirlos dejaría fuera a quien sí puede exponer.
    director_general_nombre = models.CharField("director general", max_length=160)
    director_general_email = models.EmailField("correo del director general")
    director_comercial_nombre = models.CharField(
        "director comercial", max_length=160, blank=True
    )
    director_comercial_email = models.EmailField(
        "correo del director comercial", blank=True
    )
    director_editorial_nombre = models.CharField(
        "director editorial", max_length=160, blank=True
    )
    director_editorial_email = models.EmailField(
        "correo del director editorial", blank=True
    )
    director_promocion_nombre = models.CharField(
        "director de promoción", max_length=160, blank=True
    )
    director_promocion_email = models.EmailField(
        "correo del director de promoción", blank=True
    )

    responsable_stand = models.CharField("responsable del stand", max_length=160)
    giro = models.CharField("giro", max_length=12, choices=Giro.choices)
    # La ficha pide «clave lada + número» en los dos. Sin validar, el
    # campo aceptaba cualquier texto y nadie se enteraba hasta que
    # alguien intentaba llamar.
    telefono_oficina = models.CharField(
        "teléfono de oficina",
        max_length=20,
        blank=True,
        validators=[validar_telefono],
    )
    telefono_celular = models.CharField(
        "teléfono celular", max_length=20, validators=[validar_telefono]
    )
    # **No es el correo de acceso.** Ese vive en `Persona` y puede ser
    # otro: la cuenta personal de quien tramita frente al buzón comercial
    # de la editorial.
    correo_electronico = models.EmailField("correo de contacto")

    # ── El stand ──────────────────────────────────────────────
    nombre_antepecho = models.CharField(
        "nombre en el antepecho",
        max_length=120,
        help_text=(
            "Se rotula tal como lo escribas. Cambiarlo después de que se "
            "imprima tiene un costo que corre por tu cuenta."
        ),
    )
    num_personas_atienden = models.PositiveSmallIntegerField(
        "personas que atienden el stand",
        default=1,
        # `PositiveSmallIntegerField` admite el cero, y un stand que no
        # atiende nadie no es un stand.
        validators=[MinValueValidator(1)],
    )
    total_sellos = models.PositiveSmallIntegerField("total de sellos", default=0)
    cantidad_libros_aprox = models.PositiveIntegerField(
        "cantidad aproximada de libros", default=0
    )
    cantidad_titulos_aprox = models.PositiveIntegerField(
        "cantidad aproximada de títulos", default=0
    )

    # Multivalor. JSON y no una tabla aparte porque son catálogos
    # cerrados y cortos que solo se leen enteros: una tabla añadiría dos
    # `JOIN` para no responder ninguna pregunta que hoy se haga.
    materiales = models.JSONField("materiales que exhibe", default=list, blank=True)
    # Lo que la ficha llama «Otro (especificar)». Sin esto, marcar «Otro»
    # no dice nada: el administrador ve que hay algo más y no qué.
    materiales_otro = models.CharField("¿qué otro material?", max_length=160, blank=True)
    tematicas = models.JSONField("temáticas", default=list, blank=True)
    tematicas_otra = models.CharField("¿qué otra temática?", max_length=160, blank=True)

    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "editorial"
        verbose_name_plural = "editoriales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()
        _validar_opciones(self.materiales, MATERIALES, "materiales")
        _validar_opciones(self.tematicas, TEMATICAS, "tematicas")

    @property
    def domicilio(self) -> str:
        """El domicilio en una línea, para pantallas y correos."""
        calle = f"{self.domicilio_calle} {self.domicilio_numero}".strip()
        partes = [
            calle,
            self.domicilio_colonia,
            self.cp,
            self.municipio,
            self.estado,
            self.get_pais_display(),
        ]
        return ", ".join(p for p in partes if p)


class SelloEditorial(models.Model):
    """Un fondo editorial que la editorial representa (`RN-17`).

    Es la forma correcta de decir "represento a otras casas": una
    `Editorial` por persona (`RN-21`), y los representados como sellos,
    cada uno con su carta de representación en `Documento`.
    """

    editorial = models.ForeignKey(
        Editorial, on_delete=models.CASCADE, related_name="sellos"
    )
    nombre = models.CharField(max_length=200)

    class Meta:
        verbose_name = "sello editorial"
        verbose_name_plural = "sellos editoriales"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["editorial", "nombre"],
                name="un_sello_no_se_declara_dos_veces",
            ),
        ]

    def __str__(self):
        return self.nombre

    @property
    def carta(self):
        """Su carta de representación, si la subió (`RN-17`).

        Es una y no varias: la carta autoriza a representar **a este
        sello**. Se guarda como `Documento` y no como un `FileField`
        propio para que herede lo que ya tienen los demás adjuntos — la
        lista blanca de extensiones y la vista de entrega con permisos.
        """
        return self.cartas.first()


class Solicitud(models.Model):
    """Aplicar a ser expositor (`CU-STD-001`).

    Es lo que una persona *hace* al registrarse a una convocatoria de
    stands, y por eso el enganche con `FER` está aquí y no en
    `Editorial`: quien se inscribe a una convocatoria es una persona, no
    una empresa, y `Editorial` es un expediente que se llena una vez por
    feria y se puede corregir después del cierre.

    .. important:: Es una **fotografía**, no una vista de la editorial
       (`RN-22`)

       ``datos_editorial`` y ``sellos`` guardan una copia de lo que se
       envió. Corregir la ficha después **no** reescribe lo que el
       administrador dictaminó. ``editorial`` se conserva para saber de
       quién es el expediente y para las pantallas de administración.

    .. warning:: La invariante que la base de datos **no** puede sostener

       ``registro`` es una clave foránea real, pero el ``tipo`` que
       decide que este expediente es de stands vive un salto más allá, en
       `Convocatoria`. Nada en el esquema impide colgar esta solicitud de
       un registro de una convocatoria de eventos.

       Se comprueba en ``servicios/solicitudes.py``, que pide el registro
       a `FER` declarando el tipo que espera, y hay prueba. Ver
       `ADR-0006`.
    """

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente de revisión"
        ACEPTADA = "aceptada", "Aceptada"
        RECHAZADA = "rechazada", "Rechazada"
        CAMBIOS_SOLICITADOS = "cambios_solicitados", "Cambios solicitados"

    #: Los dos estados en los que una solicitud sigue en juego. De un
    #: registro cuelgan N solicitudes con **como mucho una viva**
    #: (`RN-22`), y eso lo sostiene una restricción única parcial.
    VIVOS = (Estado.PENDIENTE, Estado.CAMBIOS_SOLICITADOS)

    registro = models.ForeignKey(
        RegistroConvocatoria,
        on_delete=models.PROTECT,
        related_name="solicitudes_stands",
        help_text="La inscripción de esta persona a esta convocatoria (FER).",
    )
    editorial = models.ForeignKey(
        Editorial, on_delete=models.PROTECT, related_name="solicitudes"
    )

    # La fotografía. Se escribe una vez, al enviar, y no se vuelve a
    # tocar: es lo que el administrador dictamina.
    datos_editorial = models.JSONField(default=dict, editable=False)
    sellos = models.JSONField(default=list, editable=False)

    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    # La ficha se firma bajo «RECONOZCO Y ACEPTO LAS BASES DE
    # PARTICIPACIÓN». Va en la solicitud y no en la editorial porque se
    # aceptan las bases **de esta convocatoria**, en el momento de
    # enviar: es parte de la fotografía, no de la ficha.
    bases_aceptadas = models.BooleanField("aceptó las bases", default=False)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="solicitudes_stands_revisadas",
    )
    # Motivo del rechazo o detalle de los cambios pedidos. Obligatorio al
    # solicitar cambios (`CU-STD-007` E1) y opcional al rechazar, que es
    # una acción directa (`CU-STD-006` A2).
    motivo_peticion = models.TextField("motivo o cambios pedidos", blank=True)

    class Meta:
        verbose_name = "solicitud"
        verbose_name_plural = "solicitudes"
        ordering = ["-fecha_envio"]
        constraints = [
            # `RN-22`: de un registro cuelgan todas las solicitudes de esa
            # persona a esa convocatoria, con **como mucho una viva**.
            # Tras un rechazo se puede volver a aplicar; mientras haya una
            # pendiente o con cambios pedidos, no.
            #
            # Es parcial —solo sobre los dos estados vivos— y por eso hace
            # falta PostgreSQL. Comprobarlo solo en el servicio dejaría
            # pasar dos envíos simultáneos.
            models.UniqueConstraint(
                fields=["registro"],
                condition=Q(estado__in=("pendiente", "cambios_solicitados")),
                name="una_solicitud_viva_por_registro",
            ),
            # Una solicitud resuelta dice quién la resolvió y cuándo. Sin
            # esto, un dictamen a medias —estado cambiado, revisor
            # vacío— se vería idéntico a uno bueno en la lista.
            models.CheckConstraint(
                condition=(
                    Q(estado__in=("pendiente", "cambios_solicitados"))
                    | Q(fecha_revision__isnull=False)
                ),
                name="una_solicitud_resuelta_tiene_fecha_de_revision",
            ),
        ]

    def __str__(self):
        return f"Solicitud de {self.editorial.nombre} ({self.get_estado_display()})"

    @property
    def esta_viva(self) -> bool:
        """Si todavía está en juego: pendiente o con cambios pedidos."""
        return self.estado in self.VIVOS

    @property
    def se_puede_dictaminar(self) -> bool:
        """Solo una `pendiente` se acepta, se rechaza o se devuelve.

        Una que ya se dictaminó no se vuelve a dictaminar (`CU-STD-006`
        E1, `CU-STD-007` E2): quien la abrió pudo hacerlo antes de que
        otro administrador la resolviera.
        """
        return self.estado == self.Estado.PENDIENTE


class Documento(models.Model):
    """Un archivo adjunto a un expediente.

    .. note:: Desviación deliberada del modelo de datos (§3.4)

       El documento describe ``entidad_tipo`` / ``entidad_id``, una
       referencia polimórfica. Aquí son **claves foráneas reales,
       anulables, con una restricción que exige exactamente una**.

       El motivo es el mismo por el que `ADR-0006` descartó
       `RouterSolicitudes`: una referencia polimórfica no la puede
       validar la base, y una fila puede apuntar a una tabla que no toca
       sin que nada lo impida. Con una feria por schema hay además un
       agravante — un `ContentType` dice "app.modelo", y ese par
       significaría una fila distinta en cada edición.

       **El comprobante de pago no añadió aquí una cuarta rama**, al
       revés de lo que esta nota anticipaba. Un comprobante sigue siendo
       un documento **de su editorial** —cuelga de `editorial` como los
       demás— y quien lo señala es `Movimiento.comprobante`, en la otra
       dirección. Así `RN-15` cabe en una restricción de la base y esta
       restricción no se afloja para admitir un documento suelto.
    """

    class Tipo(models.TextChoices):
        CONSTANCIA_FISCAL = "constancia_fiscal", "Constancia de situación fiscal"
        LISTA_TITULOS = "lista_titulos", "Lista de títulos"
        CARTA_REPRESENTACION = "carta_representacion", "Carta de representación"
        COMPROBANTE_PAGO = "comprobante_pago", "Comprobante de pago"
        DOC_ABONO = "doc_abono", "Documento de abono"
        OTRO = "otro", "Otro"

    tipo = models.CharField(max_length=24, choices=Tipo.choices)
    archivo = models.FileField(
        upload_to=CarpetaDeLaFeria("documentos"),
        # Lista blanca de extensiones y tope de tamaño. La lista blanca no
        # es celo: estos archivos se entregan **desde nuestro propio
        # origen** (`servicios/archivos.py`), así que un `.html` subido y
        # servido en línea sería XSS almacenado con nuestras cookies
        # detrás.
        validators=[DocumentoAdmisible()],
    )
    # Lo que la persona llamó al archivo. El nombre real es un UUID
    # (`ADR-0007`), así que sin esto no habría cómo decirle cuál subió.
    nombre_original = models.CharField(
        "nombre original del archivo", max_length=255, blank=True
    )
    fecha_carga = models.DateTimeField(auto_now_add=True)

    editorial = models.ForeignKey(
        Editorial,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documentos",
    )
    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documentos",
    )
    # De qué sello es la carta de representación. Es un dato **de más**,
    # no una tercera rama de la restricción: la carta de un sello sigue
    # siendo un documento de su editorial, y `editorial` sigue puesto.
    # Sin esto, tres cartas de tres sellos serían tres archivos que nadie
    # puede decir a cuál corresponde (`RN-17`).
    sello = models.ForeignKey(
        "SelloEditorial",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cartas",
    )

    class Meta:
        verbose_name = "documento"
        verbose_name_plural = "documentos"
        ordering = ["-fecha_carga"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(editorial__isnull=False, solicitud__isnull=True)
                    | Q(editorial__isnull=True, solicitud__isnull=False)
                ),
                name="un_documento_cuelga_de_exactamente_una_entidad",
            ),
            # Solo una carta de representación apunta a un sello. Sin
            # esto, una constancia fiscal podría quedar colgada de un
            # sello y desaparecer al quitarlo.
            models.CheckConstraint(
                condition=(
                    Q(sello__isnull=True) | Q(tipo="carta_representacion")
                ),
                name="solo_una_carta_cuelga_de_un_sello",
            ),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.nombre_original or self.archivo.name}"


@receiver(post_delete, sender=Documento)
def _borrar_el_archivo_del_documento(sender, instance, **kwargs):
    """Al borrar la fila, se borra también el archivo (`ADR-0007`).

    Django **no** lo hace desde la 1.3, y con razón: en un `rollback` la
    fila vuelve y el archivo ya no. Aquí se acepta ese riesgo porque lo
    que se acumula si no son constancias fiscales y comprobantes de pago
    de personas identificadas, que se quedarían en el disco —o en el
    bucket— sin ninguna fila que los explique ni nadie que se acuerde de
    ellos. Un archivo de menos tras un rollback es un adjunto que hay que
    volver a subir; un archivo de más es un dato personal huérfano.

    Va como señal y no en `Documento.delete()` porque el borrado real
    ocurre casi siempre en lote —reemplazar la constancia al reenviar,
    quitar un sello con su carta— y un `.delete()` de queryset **no**
    llama al método del modelo. Las señales sí las emite.

    `save=False`: la fila ya no existe, no hay nada que volver a guardar.
    """
    if instance.archivo:
        instance.archivo.delete(save=False)


class ConfiguracionSistema(models.Model):
    """Precios y plazos de **una** convocatoria de stands (`CU-STD-034`).

    Una fila por convocatoria, no una por feria: desde el 2026-08-25 una
    edición puede abrir una convocatoria general y otra para un pabellón
    concreto, con precios distintos. Cualquier consulta que diga "el
    costo por m² de la feria" está mal escrita — es el de **esta**
    convocatoria.

    La crea el alta de la convocatoria, por el callback que esta app
    inscribe en el registro de módulos (`CU-FER-005` paso 6). Nace con
    valores por omisión y el dueño de la feria los ajusta antes de abrir.

    .. note:: Las fechas de apertura y cierre **no** están aquí

       Quién puede enviar una solicitud y hasta cuándo lo decide
       `Convocatoria` (`FER`). Aquí vive lo específico de stands:
       precios, porcentajes, plazos de pago y datos bancarios.
       ``fecha_limite_pronto_pago`` sí se queda: es una regla de cobro,
       no la vigencia de la convocatoria.

    .. warning:: El nombre dice "Sistema" y no es del sistema

       Es de una convocatoria. El nombre viene del renombrado del
       2026-08-25 y se aplica tal cual; homologarlo con el
       `ParametrosConvocatoria` de `EVT` está registrado como
       inconsistencia I-12.
    """

    convocatoria = models.OneToOneField(
        Convocatoria, on_delete=models.CASCADE, related_name="configuracion_stands"
    )
    costo_m2 = models.DecimalField(
        "costo por m²",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    porcentaje_anticipo = models.PositiveSmallIntegerField(
        "porcentaje de anticipo",
        default=50,
        help_text="Cuánto hay que abonar para confirmar la reserva (RN-02).",
    )
    plazo_reserva_dias = models.PositiveSmallIntegerField(
        "plazo de la reserva (días)",
        default=30,
        help_text="Vigencia de una reserva en espera del anticipo (RN-03).",
        # Cero días vencería la reserva en el mismo instante de crearla.
        validators=[MinValueValidator(1)],
    )
    descuento_pronto_pago = models.PositiveSmallIntegerField(
        "descuento por pronto pago (%)",
        default=10,
        help_text="10% por omisión, configurable (RN-04).",
    )
    # Una fecha de la convocatoria, igual para todos, no un contador por
    # reserva (`RN-04`): quien reserva tarde tiene menos días.
    fecha_limite_pronto_pago = models.DateField(
        "fecha límite del pronto pago", null=True, blank=True
    )
    instrucciones_pago = models.TextField(
        blank=True, help_text="Banco, cuenta, CLABE, sucursal y referencia."
    )

    class Meta:
        verbose_name = "configuración de la convocatoria"
        verbose_name_plural = "configuraciones de convocatoria"
        constraints = [
            models.CheckConstraint(
                condition=Q(porcentaje_anticipo__lte=100),
                name="el_anticipo_no_pasa_del_100",
            ),
            models.CheckConstraint(
                condition=Q(descuento_pronto_pago__lte=100),
                name="el_pronto_pago_no_pasa_del_100",
            ),
        ]

    def __str__(self):
        return f"Configuración de {self.convocatoria.nombre}"


class Notificacion(models.Model):
    """Que se le avisó algo a alguien, y si el correo salió.

    La tabla es de `STD` y el **envío** no: quien entrega es
    `apps/notificaciones`, como todo el correo del proyecto. Es el mismo
    reparto que la bitácora — el registro es del dominio, el mecanismo es
    compartido.

    Vive en el schema de la feria porque ``solicitud`` apunta a una fila
    de **esta** edición.

    .. note:: ``estado`` dice lo que contestó el envío, no lo que hizo el
       buzón

       ``enviada`` significa que el proveedor aceptó el mensaje;
       ``fallida``, que no se pudo entregar. Que la persona lo lea, o que
       su servidor lo rebote horas después, queda fuera del alcance.
    """

    class Tipo(models.TextChoices):
        APLICACION_ACEPTADA = "aplicacion_aceptada", "Solicitud aceptada"
        APLICACION_RECHAZADA = "aplicacion_rechazada", "Solicitud rechazada"
        APLICACION_CAMBIOS = "aplicacion_cambios", "Cambios solicitados"
        RESERVA_CONFIRMADA = "reserva_confirmada", "Reserva confirmada"
        RESERVA_PAGADA = "reserva_pagada", "Reserva pagada"
        POSIBLE_CANCELACION = "posible_cancelacion", "Posible cancelación"
        RESERVA_CANCELADA = "reserva_cancelada", "Reserva cancelada"

    class Estado(models.TextChoices):
        ENVIADA = "enviada", "Enviada"
        FALLIDA = "fallida", "Fallida"

    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="notificaciones_stands",
    )
    tipo = models.CharField(max_length=24, choices=Tipo.choices)
    estado = models.CharField(max_length=8, choices=Estado.choices)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    # A qué se refiere. Clave foránea real por lo mismo que en
    # `Documento`. `reserva` se añade en la fase de reserva, y con ella
    # la restricción de que haya exactamente una.
    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notificaciones",
    )
    # Qué salió mal, cuando `estado` es `fallida`. Es lo que el
    # administrador necesita para reintentar a mano (`CU-STD-008` E1).
    detalle_error = models.TextField("detalle del error", blank=True)

    class Meta:
        verbose_name = "notificación"
        verbose_name_plural = "notificaciones"
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"{self.get_tipo_display()} → {self.destinatario}"


# ══ El mapa del showfloor ═════════════════════════════════════
#
# Lo que sigue es la retícula sobre la que se dibuja el recinto y lo que
# hay encima: los espacios que se venden y lo que no se vende pero se
# dibuja igual. Es lo que `CU-STD-009`, `010`, `032` y `037`/`038`
# necesitan, y de donde `Reserva` sacará el precio (`RN-01`).


class MapaShowfloor(models.Model):
    """La retícula del showfloor de **una** convocatoria (`RN-19`).

    Una fila por convocatoria de stands: rediseñar el mapa de 2028 no
    toca nada de 2027 porque viven en schemas distintos, y dos
    convocatorias de la misma feria —una general y otra de un pabellón—
    tienen cada una el suyo.

    .. note:: `salon` vive aquí y no en `ConfiguracionSistema`

       Es un dato del **mapa**, no de las condiciones económicas de la
       convocatoria. `ConfiguracionSistema` se queda con lo que es:
       precios, porcentajes, plazos y datos bancarios.
    """

    convocatoria = models.OneToOneField(
        Convocatoria, on_delete=models.CASCADE, related_name="mapa_showfloor"
    )
    salon = models.CharField(
        "salón", max_length=160, help_text="Recinto donde se monta este showfloor."
    )
    columnas = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    filas = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    # Lo que convierte la forma dibujada en superficie real, y por tanto
    # en precio (`RN-01`). Si la retícula no es lo bastante fina para
    # expresar las medidas reales, no hay forma de arreglarlo después sin
    # volver a dibujar: un stand de 3 × 2.5 m no cabe en una retícula de
    # un metro por celda, y con 0.5 sí.
    metros_por_celda = models.DecimalField(
        "metros por celda",
        max_digits=4,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    # Presentación pura: cuántos píxeles mide el lado de una celda al
    # dibujar. **No entra en ningún cálculo.**
    tamano_celda = models.PositiveSmallIntegerField(
        "tamaño de la celda (px)", default=12, validators=[MinValueValidator(1)]
    )
    importado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "mapa del showfloor"
        verbose_name_plural = "mapas del showfloor"

    def __str__(self):
        return f"Mapa de {self.convocatoria.nombre} ({self.salon})"

    @property
    def metros_cuadrados_vendibles(self) -> Decimal:
        return sum(
            (s.metros_cuadrados for s in self.stands.all()), start=Decimal("0")
        )


class Stand(models.Model):
    """Un espacio del showfloor: lo que se reserva y se cobra.

    Cuelga del mapa y no de la convocatoria. El modelo de datos (§3.5)
    describe un `convocatoria_id`, y sería **una segunda fuente para lo
    mismo**: el mapa ya es uno por convocatoria (`RN-19`), así que la
    convocatoria de un stand es la de su mapa. Con las dos columnas, el
    día que discreparan no habría forma de saber cuál manda.

    .. note:: `metros_cuadrados` es derivado, no una columna

       Sale de la forma en la retícula y de `MapaShowfloor.metros_por_celda`.
       Con la superficie almacenada **y** dibujada habría dos fuentes para
       la misma cifra, y el día que discreparan —alguien mueve un stand y
       no toca el número— el mapa y la factura dirían cosas distintas sin
       que nadie se entere. Lo que sí queda congelado es
       `Reserva.monto_total` (`RN-01`).
    """

    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        RESERVADO = "reservado", "Reservado"
        OCUPADO = "ocupado", "Ocupado"

    #: Lo que ve el aplicante. `Reservado` y `Ocupado` le llegan
    #: colapsados en uno solo (`RN-09`): saber cuál de los dos es no le
    #: sirve para nada y sí dice quién va ganando el reparto del recinto.
    LIBRES = (Estado.DISPONIBLE,)

    mapa = models.ForeignKey(
        MapaShowfloor, on_delete=models.CASCADE, related_name="stands"
    )
    clave = models.CharField(
        "clave", max_length=20, validators=[MinLengthValidator(1)]
    )
    etiqueta = models.CharField(
        "etiqueta",
        max_length=60,
        help_text="Lo que se pinta dentro de la caja en el mapa.",
    )
    # Descriptiva: **no fija precio**. Dentro de una convocatoria todos
    # los stands se cobran al mismo `costo_m2` (`RN-01`), así que dos
    # zonas solo pueden diferir por su tamaño. Sirve para agrupar y
    # filtrar. Pabellones a tarifas distintas son convocatorias distintas.
    zona = models.CharField("zona", max_length=80, blank=True)

    # Esquina superior izquierda, en celdas. En un stand irregular es la
    # de su envolvente, y sirve para ordenar y para centrar la vista.
    col = models.PositiveSmallIntegerField()
    fila = models.PositiveSmallIntegerField()
    # Nulos en un stand de forma irregular, que usa `rectangulos`.
    ancho_celdas = models.PositiveSmallIntegerField(null=True, blank=True)
    alto_celdas = models.PositiveSmallIntegerField(null=True, blank=True)
    #: Formas en L o en T: los rectángulos en celdas cuya unión es el
    #: stand. Hacen falta de verdad — el mapa de 2026 tiene tres.
    rectangulos = models.JSONField(null=True, blank=True)

    estado = models.CharField(
        max_length=12, choices=Estado.choices, default=Estado.DISPONIBLE
    )
    incluye = models.TextField(
        "qué incluye",
        blank=True,
        help_text="Estructura, contactos, exhibidores, mobiliario…",
    )

    class Meta:
        verbose_name = "stand"
        verbose_name_plural = "stands"
        ordering = ["fila", "col"]
        constraints = [
            models.UniqueConstraint(
                fields=["mapa", "clave"], name="una_clave_por_mapa"
            ),
            # O rectangular con sus dos medidas, o irregular con su lista.
            # Ni las tres cosas ni ninguna: sin esto, un stand sin forma
            # mide cero metros y se cobra a cero (`RN-01`).
            models.CheckConstraint(
                condition=(
                    Q(
                        ancho_celdas__isnull=False,
                        alto_celdas__isnull=False,
                        rectangulos__isnull=True,
                    )
                    | Q(
                        ancho_celdas__isnull=True,
                        alto_celdas__isnull=True,
                        rectangulos__isnull=False,
                    )
                ),
                name="un_stand_es_rectangular_o_irregular",
            ),
        ]

    def __str__(self):
        return self.clave

    @property
    def formas(self) -> list[dict]:
        """Los rectángulos que componen el stand, sea de la forma que sea.

        Existe para que nadie tenga que preguntar si es irregular antes
        de medirlo o de dibujarlo. Es el único sitio donde se mira
        `rectangulos`.
        """
        if self.rectangulos:
            return self.rectangulos
        return [
            {
                "col": self.col,
                "fila": self.fila,
                "ancho_celdas": self.ancho_celdas,
                "alto_celdas": self.alto_celdas,
            }
        ]

    @property
    def celdas(self) -> set[tuple[int, int]]:
        """Qué celdas ocupa. Es lo que detecta que dos stands se pisan."""
        return {
            (c, f)
            for r in self.formas
            for c in range(r["col"], r["col"] + r["ancho_celdas"])
            for f in range(r["fila"], r["fila"] + r["alto_celdas"])
        }

    @property
    def metros_cuadrados(self) -> Decimal:
        """La superficie, derivada de la forma y de la retícula.

        Se cuentan **celdas**, no se multiplican anchos: un stand en L no
        es su envolvente, y cobrarle el hueco sería cobrarle el espacio
        de sus vecinos.
        """
        lado = self.mapa.metros_por_celda
        return len(self.celdas) * lado * lado

    def precio(self, costo_m2: Decimal) -> Decimal:
        """`m² × costo_m2` (`RN-01`).

        Recibe el costo en vez de ir a buscarlo para no hacer una
        consulta por stand al pintar un mapa de 151.
        """
        return self.metros_cuadrados * costo_m2

    @property
    def esta_libre(self) -> bool:
        return self.estado in self.LIBRES


class DecoracionMapa(models.Model):
    """Lo que se dibuja en el mapa y **no** es un stand.

    Escenarios, salas, bodegas, accesos, rótulos del recinto. No se
    reserva, no tiene precio y no participa en ninguna regla de negocio —
    pero sin ella el mapa son cajas flotando y nadie se ubica.

    Es una entidad y no un campo JSON del mapa porque el administrador
    las edita desde el mismo editor que los stands (`CU-STD-033`), y un
    rótulo mal puesto se corrige tan a menudo como un stand. Guardarlas
    como un blob haría que cualquier corrección reescribiera el mapa
    entero.
    """

    class Tipo(models.TextChoices):
        RECTANGULO = "rectangulo", "Rectángulo"
        TEXTO = "texto", "Texto"

    mapa = models.ForeignKey(
        MapaShowfloor, on_delete=models.CASCADE, related_name="decoraciones"
    )
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    col = models.PositiveSmallIntegerField()
    fila = models.PositiveSmallIntegerField()
    # Nulos cuando `tipo = texto`: un rótulo no tiene superficie.
    ancho_celdas = models.PositiveSmallIntegerField(null=True, blank=True)
    alto_celdas = models.PositiveSmallIntegerField(null=True, blank=True)
    color = models.CharField(max_length=20, blank=True)
    etiqueta = models.CharField(max_length=120)

    class Meta:
        verbose_name = "decoración del mapa"
        verbose_name_plural = "decoraciones del mapa"
        ordering = ["fila", "col"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(tipo="texto", ancho_celdas__isnull=True, alto_celdas__isnull=True)
                    | Q(
                        tipo="rectangulo",
                        ancho_celdas__isnull=False,
                        alto_celdas__isnull=False,
                    )
                ),
                name="un_rectangulo_tiene_medidas_y_un_texto_no",
            ),
        ]

    def __str__(self):
        return self.etiqueta


# ══ La reserva ════════════════════════════════════════════════


class Reserva(models.Model):
    """Los espacios que una editorial aparta, y lo que cuestan.

    Cuelga de `RegistroConvocatoria` igual que `Solicitud`, y por lo
    mismo: es lo que da a la vez la persona y **de qué convocatoria** es
    la reserva (`RN-19`). `editorial` va además porque es quien debe el
    dinero — el mismo par que ya tiene `Solicitud`.

    .. important:: `monto_total` se congela frente al precio, no frente
       a los descuentos

       ======================================== ==================
       Cambia el `costo_m2` de la convocatoria  **No** se recalcula
       Cambia la forma de un stand              **No** se recalcula
       Se consolida o vence el pronto pago      **Sí**, al momento
       Se aplica o se retira un especial        **Sí**, al momento
       ======================================== ==================

       Un cambio de tarifa no debe alcanzar a quien ya aceptó un precio
       (`RN-01`), pero un descuento **es** una modificación deliberada de
       lo que esa reserva cuesta.
    """

    class Estado(models.TextChoices):
        POR_CONFIRMAR = "por_confirmar", "Por confirmar"
        CONFIRMADA = "confirmada", "Confirmada"
        PAGADA = "pagada", "Pagada"
        CANCELADA = "cancelada", "Cancelada"

    #: Las que siguen ocupando espacio. Solo `cancelada` cierra
    #: (`RN-11`): una vencida **no** libera sus stands, escala al
    #: administrador (`RN-12`).
    VIVAS = (Estado.POR_CONFIRMAR, Estado.CONFIRMADA, Estado.PAGADA)

    registro = models.ForeignKey(
        RegistroConvocatoria, on_delete=models.PROTECT, related_name="reservas"
    )
    editorial = models.ForeignKey(
        Editorial, on_delete=models.PROTECT, related_name="reservas"
    )
    estado = models.CharField(
        max_length=14, choices=Estado.choices, default=Estado.POR_CONFIRMAR
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # `fecha_creacion` + `plazo_reserva_dias` (`RN-03`). Se guarda en vez
    # de calcularse al vuelo porque el plazo es configurable: cambiarlo
    # en la convocatoria movería la fecha de vencimiento de las reservas
    # que ya estaban corriendo.
    fecha_vencimiento_anticipo = models.DateTimeField("vencimiento del anticipo")
    fecha_corte_pago_total = models.DateTimeField(
        "corte del pago total", null=True, blank=True
    )
    #: El total **con los descuentos ya aplicados**, congelado al
    #: reservar con el `costo_m2` de ese momento (`RN-01`).
    monto_total = models.DecimalField(
        "monto total",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        verbose_name = "reserva"
        verbose_name_plural = "reservas"
        ordering = ["-fecha_creacion"]
        constraints = [
            # `RN-23`: una editorial lleva **una** reserva por
            # convocatoria. El expediente es uno —una editorial, un
            # dictamen, un contrato, una cuenta por pagar— y dos reservas
            # vivas partirían el saldo en dos cuentas que nadie sabría
            # cuál pagar primero.
            #
            # Va sobre `registro` y no sobre `editorial`: el registro ya
            # dice **persona y convocatoria**, así que la misma editorial
            # puede tener la suya en la convocatoria general y otra en la
            # de pabellón, que son ferias distintas del mismo salón.
            #
            # Es un índice parcial: solo cuenta lo vivo (`RN-11`). Una
            # cancelada no estorba, que es lo que permite volver a
            # empezar tras cancelar.
            models.UniqueConstraint(
                fields=["registro"],
                condition=Q(estado__in=("por_confirmar", "confirmada", "pagada")),
                name="una_reserva_viva_por_registro",
            ),
        ]

    def __str__(self):
        return f"Reserva de {self.editorial} ({self.get_estado_display()})"

    # ── El dinero ────────────────────────────────────────────

    @property
    def monto_abonado(self) -> Decimal:
        """Lo cubierto por movimientos **validados**.

        Solo los validados: lo que el aplicante registra es una
        declaración con un papel adjunto, y hasta que alguien comprueba
        que el dinero llegó al banco no es dinero (`CU-STD-018` paso 7).
        Contar los pendientes confirmaría reservas que nadie pagó.
        """
        total = self.movimientos.filter(
            estado=Movimiento.Estado.VALIDADO
        ).aggregate(models.Sum("monto"))["monto__sum"]
        return total or Decimal("0.00")

    @property
    def monto_pendiente(self) -> Decimal:
        return self.monto_total - self.monto_abonado

    @property
    def configuracion(self):
        """La configuración de **su** convocatoria, leída de la base.

        Con `self.registro.convocatoria.configuracion_stands` bastaría,
        pero ese descriptor cachea la fila en la instancia: quien acabe
        de cambiar el porcentaje de anticipo seguiría viendo el de antes,
        y de aquí sale una cifra que alguien va a pagar.
        """
        return ConfiguracionSistema.objects.get(
            convocatoria_id=self.registro.convocatoria_id
        )

    @property
    def anticipo(self) -> Decimal:
        """El porcentaje de anticipo sobre el total **con descuento**.

        `RN-02`: del total ya descontado y no del bruto. El porcentaje
        sale de la convocatoria — 50 es su valor por omisión, no una
        constante del sistema.
        """
        porcentaje = self.configuracion.porcentaje_anticipo
        return (self.monto_total * porcentaje / 100).quantize(Decimal("0.01"))

    @property
    def esta_vencida(self) -> bool:
        """Pasó el plazo sin cubrir el anticipo (`RN-03`, `RN-12`).

        **Vencer no cancela**: la reserva sigue viva y sus stands siguen
        ocupados. Lo que hace es escalar al administrador, que es quien
        decide cancelar o prorrogar (`CU-STD-035`).
        """
        return (
            self.estado == self.Estado.POR_CONFIRMAR
            and timezone.now() > self.fecha_vencimiento_anticipo
        )


class ReservaStand(models.Model):
    """Qué stands entran en qué reserva. Tabla de unión, y nada más.

    .. warning:: No guarda ni m² ni precio, y es deliberado

       **Se gana** que no haya dos fuentes para la misma cifra: los m²
       salen de la forma del stand y el precio de `costo_m2`. **Se
       pierde** el desglose histórico por línea — si alguien corrige el
       mapa o cambia la tarifa, el desglose se recalcula con los valores
       nuevos y deja de cuadrar con lo que la editorial aceptó.

       Lo que sí queda congelado es `Reserva.monto_total`, así que el
       importe cobrado no cambia: lo que cambia es **cómo se explica**.
       El riesgo pasa de "cobramos otra cifra" a "el desglose no cuadra
       con el total".

       **Condición para que se sostenga:** ningún servicio debe reescribir
       `monto_total` de una reserva que no esté `por_confirmar`.
    """

    reserva = models.ForeignKey(
        Reserva, on_delete=models.CASCADE, related_name="lineas"
    )
    stand = models.ForeignKey(
        Stand, on_delete=models.PROTECT, related_name="lineas_de_reserva"
    )

    class Meta:
        verbose_name = "stand de la reserva"
        verbose_name_plural = "stands de la reserva"
        ordering = ["stand__fila", "stand__col"]
        constraints = [
            models.UniqueConstraint(
                fields=["reserva", "stand"], name="un_stand_una_vez_por_reserva"
            ),
        ]

    def __str__(self):
        return self.stand.clave


class DescuentoAplicado(models.Model):
    """Un descuento sobre una reserva (`RN-04` a `RN-07`).

    Los dos tipos **se acumulan y se aplican en secuencia**, no sumando
    porcentajes: 10% y 15% dan un 23.5% efectivo, no un 25%. Cualquier
    consulta que sume las dos filas para enseñar "el descuento total" da
    un número que no es el que se cobra.
    """

    class Tipo(models.TextChoices):
        PRONTO_PAGO = "pronto_pago", "Pronto pago"
        ESPECIAL = "especial", "Especial"

    #: El orden en que se aplican. El pronto pago primero, que es el que
    #: el expositor ya conocía al reservar. El total no depende del orden
    #: —la multiplicación es conmutativa— pero el desglose sí se lee.
    ORDEN = (Tipo.PRONTO_PAGO, Tipo.ESPECIAL)

    reserva = models.ForeignKey(
        Reserva, on_delete=models.CASCADE, related_name="descuentos"
    )
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    # Se copia por fila al aplicarse: es lo que permite reconstruir el
    # desglose aunque después cambie la configuración de la convocatoria.
    porcentaje = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    motivo = models.CharField(max_length=200, blank=True)
    # Nulo cuando lo aplica el sistema: el pronto pago es automático
    # (`CU-STD-023`), y ponerle una persona sería atribuirle una decisión
    # que no tomó.
    aplicado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="descuentos_aplicados",
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "descuento aplicado"
        verbose_name_plural = "descuentos aplicados"
        ordering = ["tipo"]
        constraints = [
            # `RN-05`. Vive en la base y no en la pantalla: dos
            # administradores aplicando un especial a la vez, o el barrido
            # del pronto pago corriendo dos veces, insertarían dos filas y
            # el total saldría mal.
            models.UniqueConstraint(
                fields=["reserva", "tipo"], name="un_descuento_de_cada_tipo"
            ),
            models.CheckConstraint(
                condition=(Q(tipo="pronto_pago") | ~Q(motivo="")),
                name="un_descuento_especial_lleva_motivo",
            ),
            models.CheckConstraint(
                condition=Q(porcentaje__lte=100),
                name="un_descuento_no_pasa_del_100",
            ),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} {self.porcentaje}%"


class Movimiento(models.Model):
    """Un abono a una reserva, con su comprobante (`CU-STD-016`, `019`).

    Nada suma al saldo hasta que alguien lo **valida** (`CU-STD-018`): lo
    que el aplicante registra es una declaración con un papel adjunto, y
    quien administra comprueba fuera del sistema que el dinero llegó de
    verdad al banco. Por eso `Reserva.monto_abonado` cuenta solo los
    `validado`, y por eso esta tabla guarda quién validó y cuándo.

    .. note:: No se admite efectivo (`RN-08`)

       Los tres métodos dejan rastro bancario, que es lo que hace
       comprobable el paso 4 de `CU-STD-018`. Un abono en efectivo no se
       puede validar contra nada.
    """

    class Metodo(models.TextChoices):
        TRANSFERENCIA = "transferencia", "Transferencia"
        DEPOSITO = "deposito", "Depósito"
        CHEQUE = "cheque", "Cheque"

    class Origen(models.TextChoices):
        APLICANTE = "aplicante", "Lo registró el aplicante"
        ADMIN_MANUAL = "admin_manual", "Lo registró la administración"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente_validacion", "Pendiente de validación"
        VALIDADO = "validado", "Validado"
        RECHAZADO = "rechazado", "Rechazado"

    reserva = models.ForeignKey(
        Reserva, on_delete=models.PROTECT, related_name="movimientos"
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    metodo = models.CharField("método de pago", max_length=14, choices=Metodo.choices)
    origen = models.CharField(max_length=12, choices=Origen.choices)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    # El papel del banco. Va aquí y no como una vuelta desde `Documento`
    # porque así `RN-15` —un abono manual exige comprobante— cabe en una
    # restricción de la base en vez de en una comprobación que se puede
    # olvidar.
    comprobante = models.ForeignKey(
        Documento,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimientos",
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimientos_registrados",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    validado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimientos_validados",
    )
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    # `CU-STD-018` A1 paso 3: el motivo es opcional al rechazar. Lo que no
    # es opcional es que el aplicante lo vea en su historial
    # (`CU-STD-017`), y sin motivo solo verá que se rechazó.
    motivo_rechazo = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "movimiento"
        verbose_name_plural = "movimientos"
        ordering = ["-fecha_registro"]
        constraints = [
            # `RN-15`: todo abono manual del administrador lleva
            # documento. En la base y no en el formulario a propósito —
            # la regla dice "sin comprobante no se registra el abono", y
            # un `manage.py shell` también es un sitio desde el que se
            # registran abonos.
            models.CheckConstraint(
                condition=(
                    Q(origen="aplicante") | Q(comprobante__isnull=False)
                ),
                name="un_abono_manual_lleva_comprobante",
            ),
            # Un movimiento resuelto dice quién y cuándo. Sin esto, uno
            # validado sin fecha pasaría por bueno y nadie podría decir
            # quién lo dio por bueno.
            models.CheckConstraint(
                condition=(
                    Q(estado="pendiente_validacion")
                    | Q(fecha_validacion__isnull=False, validado_por__isnull=False)
                ),
                name="un_movimiento_resuelto_dice_quien_y_cuando",
            ),
        ]

    def __str__(self):
        return f"{self.get_metodo_display()} de ${self.monto} ({self.get_estado_display()})"

    @property
    def esta_validado(self) -> bool:
        return self.estado == self.Estado.VALIDADO
