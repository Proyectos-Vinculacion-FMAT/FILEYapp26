"""
Admin de Django para el Core Ferias.

Aquí es donde el equipo técnico da de alta una edición y designa a su
dueño (`CU-FER-001`). No confundir con el "panel FILEY" (`/admin/…`),
que es para los administradores de una feria; esto vive en
`/django-admin/` y opera el sistema que las contiene.

> El formulario **no guarda el modelo**: llama a
> `servicios/altas.py::crear_feria`, el mismo servicio que usa
> `manage.py alta_feria`. Si el admin escribiera la fila por su cuenta,
> crear una feria desde aquí y crearla por consola dejarían estados
> distintos — y una de las dos rutas se quedaría sin schema.
"""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import AdminFeria, Domain, Feria, validar_slug
from .servicios import altas


class FeriaForm(forms.ModelForm):
    """Formulario de alta: la feria **y** su dueño en un solo paso.

    Van juntos porque una feria sin dueño no se puede crear (CU-FER-001):
    nadie podría dar de alta a sus administradores ni abrir sus
    convocatorias. Dejarlo en dos pantallas permitiría guardar el estado
    intermedio que el caso de uso prohíbe.
    """

    correo_dueno = forms.EmailField(
        label="Correo del dueño",
        required=False,
        help_text="Si ya tiene cuenta se reutiliza tal cual, sin tocar sus datos.",
    )
    nombre_dueno = forms.CharField(
        label="Nombre del dueño", required=False, help_text="Solo si la cuenta es nueva."
    )
    apellido_dueno = forms.CharField(label="Primer apellido del dueño", required=False)
    enviar_aviso = forms.BooleanField(
        label="Avisar por correo",
        required=False,
        initial=True,
        help_text="Desmárcalo al preparar ediciones con antelación (CU-FER-001, A2).",
    )

    class Meta:
        model = Feria
        fields = ["nombre", "slug", "edicion", "sede", "fecha_inicio", "fecha_fin"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.es_alta = self.instance.pk is None
        if not self.es_alta:
            # Editar una feria existente no toca a su dueño: para eso
            # está CU-FER-004, que es del dueño, no del equipo técnico.
            for campo in ("correo_dueno", "nombre_dueno", "apellido_dueno", "enviar_aviso"):
                self.fields.pop(campo)

    def clean_slug(self):
        slug = (self.cleaned_data["slug"] or "").strip().lower()
        # E1: se valida aquí, y no solo en el servicio, para que el error
        # salga en su campo y no como un 500.
        validar_slug(slug)
        return slug

    def clean(self):
        datos = super().clean()
        if self.es_alta and not datos.get("correo_dueno"):
            self.add_error(
                "correo_dueno",
                "Una feria no se puede crear sin dueño: nadie podría dar de "
                "alta a sus administradores ni abrir sus convocatorias.",
            )
        slug = datos.get("slug")
        if self.es_alta and slug and Feria.objects.filter(slug=slug).exists():
            self.add_error("slug", f"Ya existe una feria con el slug «{slug}».")
        return datos


class AdminFeriaInline(admin.TabularInline):
    """Quién administra esta feria. Solo lectura, a propósito.

    Dar de alta y retirar administradores es del **dueño** desde el panel
    FILEY (CU-FER-003, CU-FER-004), no del equipo técnico desde aquí. Se
    muestra para poder responder "¿quién tiene acceso?" sin consultar la
    base a mano.
    """

    model = AdminFeria
    extra = 0
    can_delete = False
    fields = ("persona", "es_dueno", "creado_por", "creado_en")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Feria)
class FeriaAdmin(admin.ModelAdmin):
    form = FeriaForm
    inlines = [AdminFeriaInline]
    list_display = ("nombre", "slug", "edicion", "estado", "schema_name", "creada_en")
    list_filter = ("estado",)
    search_fields = ("nombre", "slug", "sede")
    ordering = ("-creada_en",)

    def get_queryset(self, request):
        """Oculta la fila de sistema.

        `Feria.objects` la incluye porque `django-tenants` la busca ahí
        (ver el modelo); una pantalla que liste ferias usa `reales`.
        """
        return Feria.reales.all()

    def get_inlines(self, request, obj=None):
        """Nada de inline en el alta.

        En una feria que todavía no existe la lista de administradores
        no puede decir nada, y en cambio sí mete en el formulario los
        campos ocultos del formset — que es ruido en la pantalla donde
        menos falta hace.
        """
        return [] if obj is None else self.inlines

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        # El slug determina el prefijo de la URL y el nombre del schema.
        # Cambiarlo rompería todos los enlaces ya compartidos y dejaría
        # el schema huérfano (CU-FER-001, E1).
        return ("slug", "schema_name", "creada_en")

    def get_fieldsets(self, request, obj=None):
        de_la_feria = ["nombre", "slug", "edicion", "sede", "fecha_inicio", "fecha_fin"]
        if obj is not None:
            return [
                ("La edición", {"fields": de_la_feria + ["estado"]}),
                ("Infraestructura", {"fields": ["schema_name", "creada_en"]}),
            ]
        return [
            ("La edición", {"fields": de_la_feria}),
            (
                "Su dueño",
                {
                    "fields": ["correo_dueno", "nombre_dueno", "apellido_dueno", "enviar_aviso"],
                    "description": (
                        "El dueño es la única persona que puede dar de alta a los "
                        "demás administradores de esta feria y abrir o cerrar sus "
                        "convocatorias."
                    ),
                },
            ),
        ]

    def save_model(self, request, obj, form, change):
        if change:
            obj.save()
            return

        datos = form.cleaned_data
        # Guardar una feria nueva es crear su schema y migrarlo, así que
        # esta petición tarda segundos. Es aceptable: pasa una vez al año.
        #
        # Un fallo de infraestructura (E2) sube como 500 a propósito. El
        # servicio ya deshizo lo que hubiera creado, y quien usa esta
        # pantalla es el equipo técnico: una traza real le sirve más que
        # un mensaje amable que esconda por qué falló la migración.
        try:
            resultado = altas.crear_feria(
                nombre=datos["nombre"],
                slug=datos["slug"],
                correo_dueno=datos["correo_dueno"],
                nombre_dueno=datos.get("nombre_dueno", ""),
                primer_apellido_dueno=datos.get("apellido_dueno", ""),
                edicion=datos.get("edicion", ""),
                sede=datos.get("sede", ""),
                fecha_inicio=datos.get("fecha_inicio"),
                fecha_fin=datos.get("fecha_fin"),
                enviar_aviso=datos.get("enviar_aviso", True),
            )
        except altas.AltaRechazada as exc:
            raise ValidationError(str(exc)) from exc

        # El admin sigue trabajando con `obj` después de esto (el registro
        # del log, el redirect, los inlines), y quien tiene los datos
        # reales —empezando por la clave primaria— es la feria que creó
        # el servicio. Se copian sobre `obj` en vez de devolver otra
        # instancia porque la firma de `save_model` no permite eso.
        obj.__dict__.update(resultado.feria.__dict__)

        if resultado.error_aviso:
            # E3: el alta es válida; solo no salió el correo.
            self.message_user(
                request,
                f"La feria quedó creada, pero el aviso a {resultado.dueno.correo} "
                f"no se pudo enviar: {resultado.error_aviso}",
                level="WARNING",
            )

    def has_delete_permission(self, request, obj=None):
        """Nunca desde aquí.

        Con `auto_drop_schema=False` un borrado dejaría el schema
        huérfano —con todo el contenido dentro y sin nada que lo
        referencie—; con `True`, un botón rojo de esta pantalla tiraría
        una edición entera. Ninguna de las dos es aceptable: se borra por
        consola, donde hay que escribir lo que se está haciendo.
        """
        return False


@admin.register(AdminFeria)
class AdminFeriaAdmin(admin.ModelAdmin):
    """Accesos a ferias — la vía de emergencia del equipo técnico.

    Lo normal es que el dueño dé de alta a sus administradores desde el
    panel FILEY (CU-FER-003). Esto existe para el caso que ese flujo no
    cubre: una feria cuyo dueño se fue, que hasta que exista la
    transferencia de propiedad solo se desatasca desde fuera.
    """

    list_display = ("feria", "persona", "es_dueno", "creado_por", "creado_en")
    list_filter = ("es_dueno", "feria")
    search_fields = ("persona__correo", "feria__nombre", "feria__slug")
    autocomplete_fields = ("feria", "persona", "creado_por")


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """El slug de ruteo de cada feria.

    Se registra solo para poder diagnosticar: si una feria existe pero
    `/f/<slug>/` da 404, es que le falta esta fila. No se edita a mano —
    la escribe el servicio de alta junto con `Feria.slug`, y los dos
    tienen que decir lo mismo.
    """

    list_display = ("domain", "tenant", "is_primary")
    readonly_fields = ("domain", "tenant", "is_primary")

    def has_add_permission(self, request):
        return False
