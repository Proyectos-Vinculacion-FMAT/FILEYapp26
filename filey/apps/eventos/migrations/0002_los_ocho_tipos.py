"""
Siembra el catálogo de tipos de actividad.

Son ocho filas fijas (§2.5 del modelo de datos), no datos que alguien dé
de alta: cada una tiene su propia tabla `Actividad_*` y su propio
formulario. Van en una migración y no en un comando porque una feria
recién creada tiene que poder recibir propuestas sin que nadie se acuerde
de ejecutar nada — `migrate_schemas` corre esto en cada schema nuevo.

El orden es el del selector del prototipo, que es el que la Coordinación
lee de arriba abajo, no el alfabético.
"""

from django.db import migrations

TIPOS = [
    ("conversatorio", 1),
    ("conferencia", 2),
    ("charla", 3),
    ("mesa_redonda", 4),
    ("presentacion_libro", 5),
    ("presentacion_revista", 6),
    ("lectura_obra", 7),
    ("encuentro", 8),
]


def sembrar(apps, schema_editor):
    Catalogo = apps.get_model("eventos", "CatalogoActividades")
    for nombre, orden in TIPOS:
        # `update_or_create` y no `create`: si la migración se vuelve a
        # aplicar sobre un schema que ya los tiene, corregir el orden es
        # lo correcto; reventar por clave duplicada, no.
        Catalogo.objects.update_or_create(nombre=nombre, defaults={"orden": orden})


def retirar(apps, schema_editor):
    """Solo borra los tipos que nadie usa.

    Una actividad protege su tipo (`on_delete=PROTECT`), así que revertir
    esta migración con propuestas ya capturadas debe fallar ruidosamente
    en vez de arrastrarlas.
    """
    Catalogo = apps.get_model("eventos", "CatalogoActividades")
    Catalogo.objects.filter(nombre__in=[n for n, _ in TIPOS]).delete()


class Migration(migrations.Migration):
    dependencies = [("eventos", "0001_initial")]

    operations = [migrations.RunPython(sembrar, retirar)]
