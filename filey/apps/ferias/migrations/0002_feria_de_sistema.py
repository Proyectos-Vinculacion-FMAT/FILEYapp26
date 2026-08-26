"""
Crea la fila `Feria` del schema `public` — la que no es una feria.

`TenantSubfolderMiddleware` resuelve **toda** petición que no empiece por
`/f/` haciendo `Feria.objects.get(schema_name="public")`, y responde 404
si no la encuentra. O sea: sin esta fila, la pantalla de acceso, el alta
de cuenta y `/django-admin/` devuelven 404 — el sistema entero deja de
responder fuera de las ferias.

Es una verruga de la librería, no una entidad del modelo de datos. Se
crea aquí, en una migración, para que aparezca sola en cualquier base
—desarrollo, pruebas, producción— y nadie tenga que acordarse de ella.

No lleva fila `Domain`: sin ella no hay ningún slug que la alcance por
`/f/…`, así que no es navegable.
"""

from django.db import migrations

SLUG_SISTEMA = "_sistema"


def crear_feria_de_sistema(apps, schema_editor):
    # `apps.get_model` devuelve el modelo *histórico*, que es un
    # `models.Model` pelado sin el `save()` de `TenantMixin`. Por eso
    # esto no intenta crear ningún schema: `public` ya existe, y aquí
    # solo se inserta la fila que el middleware espera encontrar.
    Feria = apps.get_model("ferias", "Feria")
    Feria.objects.update_or_create(
        schema_name="public",
        defaults={
            # El nombre lleva paréntesis a propósito: si alguna vez se
            # cuela en una pantalla, se ve que no es una edición.
            "nombre": "(sistema)",
            "slug": SLUG_SISTEMA,
            "estado": "activa",
        },
    )


def borrar_feria_de_sistema(apps, schema_editor):
    Feria = apps.get_model("ferias", "Feria")
    Feria.objects.filter(schema_name="public").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ferias", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_feria_de_sistema, borrar_feria_de_sistema),
    ]
