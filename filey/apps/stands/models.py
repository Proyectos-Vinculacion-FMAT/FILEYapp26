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
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from apps.convocatorias.models import Convocatoria, RegistroConvocatoria
from apps.registros.paises import PAISES
from comun.almacenamiento import CarpetaDeLaFeria, DocumentoAdmisible


class Giro(models.TextChoices):
    """A qué se dedica la editorial. Viene de la Ficha de Registro."""

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

#: Sobre qué. Las 59 de la Ficha de Registro, p. 2, en su orden.
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
    nombre = models.CharField("nombre de la editorial", max_length=200)

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
    telefono_oficina = models.CharField(
        "teléfono de oficina", max_length=20, blank=True
    )
    telefono_celular = models.CharField("teléfono celular", max_length=20)
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
        "personas que atienden el stand", default=1
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

       ``movimiento`` se añade en la fase de pago, con su columna y su
       hueco en la restricción.
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
