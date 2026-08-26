"""
Retira `RolPermiso`. Lo sustituye `AdminFeria` (`apps/ferias`).

`RolPermiso` quedó derogado en el modelo de datos el 2026-08-21
(ADR-0004: el acceso administrativo se otorga **por feria**, no por
módulo, y no hay nivel de solo lectura). Seguía vivo en el código hasta
hoy; esto lo retira también de la base.

> [!warning] Es irreversible en la práctica
> Revertirla recrea la tabla **vacía**. Los permisos que hubiera no se
> pueden reconstruir desde `AdminFeria`, y tampoco al revés: la
> equivalencia entre los dos modelos no es uno a uno —«administrador de
> EVT» pasa a administrar la feria entera, y «solo lectura» no tiene
> equivalente—. La tabla de equivalencia está en
> `REG/Modelo de datos - Registros` §2.2.
>
> En este despliegue la conversión no hace falta: los únicos permisos
> existentes son los del superusuario técnico, que entra por
> `/django-admin/` y no los necesita.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registros", "0003_persona_nombre_en_tres_campos_y_pais"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="rolpermiso",
            name="unico_permiso_por_modulo",
        ),
        migrations.DeleteModel(name="RolPermiso"),
    ]
