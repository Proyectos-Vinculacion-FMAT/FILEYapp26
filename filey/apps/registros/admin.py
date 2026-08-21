
"""Admin de Django — herramienta interna del equipo de desarrollo.

(No confundir con el "panel administrativo FILEY", que son las
pantallas de /admin/. Esto vive en /django-admin/ y es solo para
inspeccionar datos.)
"""

from django.contrib import admin

from .models import Persona, RolPermiso, SesionOTP


class RolPermisoInline(admin.TabularInline):
    model = RolPermiso
    extra = 0


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ("correo", "nombre_completo", "telefono", "estado", "ultimo_acceso")
    search_fields = ("correo", "nombre_completo", "telefono")
    list_filter = ("estado",)
    inlines = [RolPermisoInline]
    readonly_fields = ("fecha_registro", "ultimo_acceso")
    exclude = ("password",)


@admin.register(RolPermiso)
class RolPermisoAdmin(admin.ModelAdmin):
    list_display = ("persona", "modulo", "nivel", "creado_en")
    list_filter = ("modulo", "nivel")


@admin.register(SesionOTP)
class SesionOTPAdmin(admin.ModelAdmin):
    list_display = ("persona", "creado_en", "expira_en", "usado", "intentos")
    list_filter = ("usado",)
    readonly_fields = ("codigo_hash",)
