"""
Accesos de una feria — las pantallas del **dueño** (`CU-FER-003`, `CU-FER-004`).

Estas viven **dentro** de `/f/<slug>/`, al revés que las de `views.py`.
La separación en dos módulos no es estética: es la que hace visible el
límite que más muerde en este proyecto —dentro de una feria el urlconf
activo es otro, así que `{% url 'registros:salir' %}` revienta y
`{% url 'ferias:elegir' %}` no existe—. Ver `comun/urls.py`.

Lo que se administra aquí (``AdminFeria``) vive en el schema `public`,
no en el de la feria. Se puede consultar desde dentro porque
``django-tenants`` deja el `search_path` en ``[feria_x, public]``: es
justo el caso para el que la capa global existe.

Las vistas son delgadas y **no comprueban permisos por su cuenta**: eso
lo hace ``requiere_dueno_feria``, que es la misma comprobación que usa
el resto del sistema (regla 2 de CLAUDE.md).
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import DarAccesoForm
from .models import AdminFeria
from .permisos import requiere_dueno_feria
from .servicios import accesos as servicio


def _panel(peticion, formulario):
    """El contenido de la pantalla, para las dos salidas que la pintan."""
    return {
        "feria": peticion.tenant,
        "accesos": servicio.administradores_de(peticion.tenant),
        "form": formulario,
        "zona_admin": True,
    }


@requiere_dueno_feria
@require_http_methods(["GET", "POST"])
def panel_accesos(peticion):
    """Quién administra mi feria, y el alta de uno nuevo (`CU-FER-003`).

    Una sola dirección para la lista y el alta: son el paso 2 y el paso
    3 del mismo caso de uso, y partirlas en dos pantallas obligaría a ir
    y volver para comprobar lo que ya se estaba mirando.

    En éxito redirige en vez de responder al POST (patrón
    *post/redirect/get*): así recargar la página no reintenta el alta.
    En error re-renderiza con el formulario ligado, que es lo que
    conserva lo escrito.
    """
    if peticion.method == "GET":
        return render(peticion, "ferias/accesos.html", _panel(peticion, DarAccesoForm()))

    formulario = DarAccesoForm(peticion.POST)
    if not formulario.is_valid():
        return render(peticion, "ferias/accesos.html", _panel(peticion, formulario))

    try:
        resultado = servicio.dar_acceso(
            feria=peticion.tenant,
            concedido_por=peticion.user,
            **formulario.cleaned_data,
        )
    except servicio.AccesoRechazado as exc:
        # E4 (feria archivada). No es un error del formulario —lo que se
        # escribió está bien—, así que se dice arriba y no bajo un campo.
        messages.error(peticion, str(exc))
        return render(peticion, "ferias/accesos.html", _panel(peticion, formulario))

    if resultado.ya_tenia_acceso:
        # E2. No es un fallo: el estado que el dueño quería ya se
        # cumple, y decirlo así evita que lo intente otra vez.
        messages.warning(
            peticion,
            f"{resultado.persona.correo} ya administraba esta feria. "
            "No se creó nada nuevo ni se le volvió a avisar.",
        )
    elif resultado.aviso_enviado:
        messages.success(
            peticion,
            f"{resultado.persona.nombre_completo or resultado.persona.correo} "
            "ya administra esta feria. Le avisamos por correo.",
        )
    else:
        # E3: el acceso vale igual; lo único que falta es el aviso.
        messages.warning(
            peticion,
            f"{resultado.persona.correo} ya administra esta feria, pero no "
            "pudimos enviarle el correo de aviso. Puede entrar igual: "
            "compártele la dirección de esta edición.",
        )

    return redirect("accesos:panel")


@requiere_dueno_feria
@require_http_methods(["GET", "POST"])
def retirar_acceso(peticion, acceso_id):
    """Quitarle el acceso a alguien, con confirmación (`CU-FER-004`).

    El GET pinta la confirmación y el POST la ejecuta. Son dos pasos y
    no un botón directo porque retirar un acceso **se parece a borrar
    una cuenta**, y no lo es: la confirmación existe sobre todo para
    decir lo que *no* pasa (paso 4 del caso de uso).

    El acceso se busca acotado a ``peticion.tenant``. Sin ese filtro, un
    identificador de otra feria daría un acceso ajeno: `AdminFeria` es
    global, así que la feria no la pone la conexión — la ponemos aquí.
    """
    acceso = get_object_or_404(
        AdminFeria.objects.select_related("persona", "feria"),
        pk=acceso_id,
        feria=peticion.tenant,
    )

    if peticion.method == "GET":
        return render(
            peticion,
            "ferias/retirar_acceso.html",
            {"feria": peticion.tenant, "acceso": acceso, "zona_admin": True},
        )

    try:
        persona = servicio.retirar_acceso(acceso=acceso)
    except servicio.AccesoRechazado as exc:
        # E2: retirar al dueño. La pantalla no ofrece el botón, así que
        # llegar aquí es un POST fabricado a mano — o el dueño abrió la
        # confirmación de otro y alguien transfirió la propiedad entre
        # medias.
        messages.error(peticion, str(exc))
        return redirect("accesos:panel")

    messages.success(
        peticion,
        f"{persona.nombre_completo or persona.correo} ya no administra esta "
        "feria. Su cuenta sigue activa y conserva sus otras ediciones.",
    )
    return redirect("accesos:panel")
