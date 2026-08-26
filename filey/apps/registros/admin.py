
"""Admin de Django — herramienta interna del equipo de desarrollo.

(No confundir con el "panel administrativo FILEY", que son las
pantallas de /admin/. Esto vive en /django-admin/ y es solo para
inspeccionar datos.)
"""

from django.contrib import admin

from .models import Persona, SesionOTP


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    # `nombre_completo` es una propiedad derivada, no una columna: sirve
    # para mostrar (`list_display`) pero no para buscar ni filtrar, que
    # se traducen a SQL. La búsqueda va sobre los tres campos reales.
    list_display = (
        "correo",
        "nombre_completo",
        "telefono",
        "pais",
        "estado",
        "ultimo_acceso",
    )
    search_fields = (
        "correo",
        "nombre",
        "primer_apellido",
        "segundo_apellido",
        "telefono",
    )
    list_filter = ("estado", "pais")
    ordering = ("primer_apellido", "segundo_apellido", "nombre")
    readonly_fields = ("fecha_registro", "ultimo_acceso")
    exclude = ("password",)


@admin.register(SesionOTP)
class SesionOTPAdmin(admin.ModelAdmin):
    list_display = ("persona", "creado_en", "expira_en", "usado", "intentos")
    list_filter = ("usado",)
    readonly_fields = ("codigo_hash",)
