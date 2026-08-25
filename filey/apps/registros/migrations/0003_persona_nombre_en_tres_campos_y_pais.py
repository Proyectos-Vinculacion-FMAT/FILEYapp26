"""
Parte `Persona.nombre_completo` en tres campos y añade `pais`.

Decisión del 2026-08-25 (`REG/Modelo de datos - Registros` §2.1 y §5),
que sustituye a la de `nombres`/`apellidos` del 2026-08-19.

> [!warning] El reparto de los datos existentes es una **heurística**
> Partir un nombre escrito en un solo campo no es automatizable con
> fiabilidad: "María del Carmen Pech Uc" y "Juan Carlos Pech" tienen la
> misma forma y distinto reparto. La regla de abajo acierta en el caso
> común hispano y se equivoca en nombres compuestos y en apellidos de
> dos palabras ("De la Cruz", "Van Dyke"). `partir_nombre` imprime lo
> que decidió para cada fila —el log del despliegue es el único sitio
> donde queda constancia, porque después se borra el campo de origen— y
> lo migrado hay que revisarlo a mano.
"""

from django.db import migrations, models

# El catálogo se importa en vez de copiarse: es un módulo de datos sin
# dependencias de modelos, y copiar 200 entradas aquí las dejaría
# desincronizadas al primer país que se añada. `choices` no toca el
# schema, así que un cambio futuro en la lista solo produce un
# `AlterField` cosmético.
from apps.registros.paises import PAISES


def repartir(nombre_completo):
    """`"María del Carmen Pech Uc"` → `("María del Carmen", "Pech", "Uc")`.

    - 1 palabra  → todo es nombre de pila.
    - 2 palabras → nombre + primer apellido.
    - 3 o más    → las dos últimas son los apellidos, el resto el nombre.

    Función pura y con nombre propio para que la heurística se pueda
    probar sin montar una migración (`pruebas/test_persona.py`): es la
    única parte de este archivo que puede equivocarse en silencio.
    """
    partes = (nombre_completo or "").split()
    if len(partes) >= 3:
        return " ".join(partes[:-2]), partes[-2], partes[-1]
    if len(partes) == 2:
        return partes[0], partes[1], ""
    if partes:
        return partes[0], "", ""
    return "", "", ""


def partir_nombre(apps, schema_editor):
    """Reparte `nombre_completo` entre los tres campos nuevos.

    Imprime lo que decidió para cada fila. En un despliegue esa salida
    queda en el log de GitHub Actions, y es el único registro de qué hizo
    la heurística con los datos reales: sin ella, revisar el reparto a
    mano obliga a comparar contra un `nombre_completo` que ya se borró.
    """
    Persona = apps.get_model("registros", "Persona")
    for persona in Persona.objects.all().iterator():
        original = persona.nombre_completo
        (
            persona.nombre,
            persona.primer_apellido,
            persona.segundo_apellido,
        ) = repartir(original)
        persona.save(
            update_fields=["nombre", "primer_apellido", "segundo_apellido"]
        )
        print(
            f"  repartido: {original!r} -> nombre={persona.nombre!r} "
            f"primer_apellido={persona.primer_apellido!r} "
            f"segundo_apellido={persona.segundo_apellido!r}"
        )


def juntar_nombre(apps, schema_editor):
    """Vuelve a un solo campo, para que la migración sea reversible.

    Reunir sí es exacto —es una concatenación—, así que revertir no
    pierde nada. Lo que se pierde es volver a aplicarla: el reparto se
    recalcularía con la heurística y las correcciones manuales se irían.
    """
    Persona = apps.get_model("registros", "Persona")
    for persona in Persona.objects.all().iterator():
        partes = [
            persona.nombre,
            persona.primer_apellido,
            persona.segundo_apellido,
        ]
        persona.nombre_completo = " ".join(p for p in partes if p).strip()
        persona.save(update_fields=["nombre_completo"])


class Migration(migrations.Migration):

    dependencies = [
        ("registros", "0002_sesionotp_acertado"),
    ]

    operations = [
        # Los tres campos nacen con `default=""` porque la tabla puede
        # tener filas: primero se crean vacíos, luego se llenan, y solo
        # entonces se retira el campo viejo.
        migrations.AddField(
            model_name="persona",
            name="nombre",
            field=models.CharField(default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="persona",
            name="primer_apellido",
            field=models.CharField(default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="persona",
            name="segundo_apellido",
            field=models.CharField(blank=True, default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="persona",
            name="pais",
            field=models.CharField(
                blank=True,
                choices=PAISES,
                default="",
                max_length=2,
            ),
            preserve_default=False,
        ),
        # Sin este `AlterField` la migración no se puede revertir: al
        # deshacer el `RemoveField`, Django recrea la columna con la
        # definición que tenía —`CharField(max_length=180)`, NOT NULL y
        # sin default— y la tabla ya tiene filas, así que el rebuild
        # falla con un IntegrityError. Darle `default=""` antes de
        # retirarla es lo que hace que volver atrás funcione.
        migrations.AlterField(
            model_name="persona",
            name="nombre_completo",
            field=models.CharField(default="", max_length=180),
        ),
        migrations.RunPython(partir_nombre, juntar_nombre),
        migrations.RemoveField(model_name="persona", name="nombre_completo"),
    ]
