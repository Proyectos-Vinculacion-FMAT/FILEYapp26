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
from django.utils.html import format_html

from .models import AdminFeria, Domain, Feria, validar_slug
from .servicios import accesos, altas


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

    # ── Transferir la propiedad (solo al editar) ──────────────
    # Se pide por correo y no con un desplegable de personas por lo
    # mismo que el alta: la lista crece con cada participante del
    # sistema, y quien recibe una feria puede no tener cuenta todavía.
    correo_nuevo_dueno = forms.EmailField(
        label="Transferir la propiedad a",
        required=False,
        help_text=(
            "Correo de quien pasa a ser dueño. El dueño actual **no pierde el "
            "acceso**: se queda como administrador. Déjalo vacío para no cambiar nada."
        ),
    )
    nombre_nuevo_dueno = forms.CharField(
        label="Nombre", required=False, help_text="Solo si la cuenta es nueva."
    )
    apellido_nuevo_dueno = forms.CharField(label="Primer apellido", required=False)

    class Meta:
        model = Feria
        fields = [
            "nombre", "slug", "edicion", "sede", "fecha_inicio", "fecha_fin",
            "pie_entidad", "pie_dependencia", "pie_contacto",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.es_alta = self.instance.pk is None
        if self.es_alta:
            # En una feria que no existe no hay propiedad que transferir:
            # su dueño se designa en el alta, más abajo.
            for campo in (
                "correo_nuevo_dueno",
                "nombre_nuevo_dueno",
                "apellido_nuevo_dueno",
            ):
                self.fields.pop(campo)
        else:
            # Los campos del alta no reaparecen al editar: designar al
            # dueño y **transferir** la propiedad son cosas distintas, y
            # un mismo campo para las dos deja al operador sin saber si
            # está creando algo o quitándoselo a alguien.
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
    list_display = ("nombre", "slug", "edicion", "estado", "operar", "creada_en")
    list_filter = ("estado",)
    search_fields = ("nombre", "slug", "sede")
    ordering = ("-creada_en",)

    @admin.display(description="Operar la edición")
    def operar(self, obj):
        """Las puertas hacia dentro de esta feria.

        Sin esto, entrar a una edición desde aquí es escribir su URL a
        mano: el listado conoce todas las ferias y no enlazaba a ninguna.
        Es la única forma que tiene el operador de la plataforma de
        llegar a las ediciones que no administra —y desde `ADR-0005` las
        alcanza todas, sin tener fila en `AdminFeria`—.

        Los tres enlaces son los tres sitios distintos de una feria:
        su contenido (el admin de la edición, donde se dan de alta las
        convocatorias), sus accesos (CU-FER-003 / CU-FER-004) y lo que
        ve el público.
        """
        return format_html(
            '<a href="{url}django-admin/">Contenido</a> · '
            '<a href="{url}accesos/">Accesos</a> · '
            '<a href="{url}">Catálogo</a>',
            url=obj.url,
        )

    @admin.display(description="Dueño actual")
    def dueno_actual(self, obj):
        """Quién la tiene hoy.

        Sale junto al campo de transferencia y no solo en el inline de
        abajo: la pregunta que se hace antes de traspasar una feria es
        «¿a quién se la estoy quitando?», y tenerla que buscar en otra
        parte de la misma pantalla es como se traspasa la equivocada.
        """
        acceso = obj.administradores.filter(es_dueno=True).select_related(
            "persona"
        ).first()
        if acceso is None:
            return "— (sin dueño)"
        return str(acceso.persona)

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
        return ("slug", "schema_name", "creada_en", "operar", "dueno_actual")

    def get_fieldsets(self, request, obj=None):
        de_la_feria = ["nombre", "slug", "edicion", "sede", "fecha_inicio", "fecha_fin"]
        if obj is not None:
            return [
                ("La edición", {"fields": de_la_feria + ["estado"]}),
                (
                    "Entrar a esta edición",
                    {
                        "fields": ["operar"],
                        "description": (
                            "El contenido de una feria no se administra desde aquí: "
                            "vive en su propio schema y se opera desde dentro de ella. "
                            "Un superusuario alcanza cualquier edición, administre o "
                            "no (ADR-0005)."
                        ),
                    },
                ),
                (
                    "Su dueño",
                    {
                        "fields": [
                            "dueno_actual",
                            "correo_nuevo_dueno",
                            "nombre_nuevo_dueno",
                            "apellido_nuevo_dueno",
                        ],
                        "description": (
                            "Transferir la propiedad es del operador de la "
                            "plataforma (ADR-0005): es la salida de una edición "
                            "cuyo dueño abandona el proyecto, porque retirarle el "
                            "acceso la dejaría sin nadie que pueda administrarla."
                        ),
                    },
                ),
                (
                    "Pie de página",
                    {
                        "fields": ["pie_entidad", "pie_dependencia", "pie_contacto"],
                        "classes": ["collapse"],
                        "description": (
                            "Lo que sale al fondo de todas las pantallas de esta "
                            "edición. Cada campo que se deje en blanco hereda el de "
                            "la plataforma (PIE_ENTIDAD, PIE_DEPENDENCIA y "
                            "PIE_CONTACTO del entorno), así que en blanco no "
                            "significa un pie vacío."
                        ),
                    },
                ),
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
            correo = (form.cleaned_data.get("correo_nuevo_dueno") or "").strip()
            if correo:
                self._transferir(request, obj, form, correo)
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

    def _transferir(self, request, feria, form, correo):
        """Pasa la propiedad, y lo dice.

        La escritura es del servicio y no de aquí: la misma regla tiene
        que valer desde una consola, y el estado intermedio —una feria
        sin dueño— solo es seguro dentro de su transacción (regla 3).
        """
        datos = form.cleaned_data
        try:
            resultado = accesos.transferir_propiedad(
                feria=feria,
                correo=correo,
                nombre=datos.get("nombre_nuevo_dueno", ""),
                primer_apellido=datos.get("apellido_nuevo_dueno", ""),
                transferida_por=request.user,
            )
        except accesos.AccesoRechazado as exc:
            raise ValidationError(str(exc)) from exc

        if resultado.anterior == resultado.persona:
            self.message_user(
                request,
                f"{resultado.persona} ya era el dueño de «{feria.nombre}»: "
                "no se cambió nada.",
                level="INFO",
            )
            return

        antes = str(resultado.anterior) if resultado.anterior else "nadie"
        self.message_user(
            request,
            f"«{feria.nombre}» pasó de {antes} a {resultado.persona}, que ahora "
            "es su dueño. El anterior conserva su acceso como administrador.",
            level="SUCCESS",
        )
        if resultado.error_aviso:
            self.message_user(
                request,
                f"La transferencia se hizo, pero el aviso a "
                f"{resultado.persona.correo} no se pudo enviar: "
                f"{resultado.error_aviso}",
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
