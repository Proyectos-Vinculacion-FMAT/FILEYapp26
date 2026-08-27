"""
Permisos **dentro** de una feria (`ADR-0004`).

Aquí vive la comprobación que el middleware no puede hacer.
`TenantSubfolderMiddleware` va primero en la pila —tiene que fijar el
`search_path` antes de que nada toque la base— y eso es **antes** de
`AuthenticationMiddleware`, así que cuando corre todavía no hay
`request.user`. ADR-0003 describía el middleware como el sitio de esta
comprobación; en la práctica es este archivo.

Que estén separados no es solo una limitación técnica: hay pantallas de
feria que **son públicas**. El catálogo de convocatorias se consulta sin
cuenta a propósito (CU-FER-006, A1) — pedir sesión para mirar qué hay
convocado rompe el embudo—, así que resolver la feria y exigir permiso
tienen que ser dos decisiones distintas.

Dos decoradores, y solo dos:

- ``requiere_admin_feria`` — administra **esta** feria. Da acceso a
  todo su contenido.
- ``requiere_dueno_feria`` — además es su dueño. Reservado a dar de
  alta y retirar administradores (CU-FER-003, CU-FER-004) y a
  administrar las convocatorias (CU-FER-005, 007, 008, 009).

No hay nivel de solo lectura: ADR-0004 lo elimina a sabiendas.

Por encima de los dos pasa el **operador de la plataforma** —el
superusuario de Django—, que alcanza cualquier feria sin tener fila en
``AdminFeria`` (`ADR-0005`). No es un tercer decorador: es una respuesta
distinta a las mismas dos preguntas, y por eso vive en ``administra`` y
``tiene_alcance_de_dueno`` y no repartida por las vistas.
"""

import functools

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from comun.urls import url_publica

from .models import AdminFeria


def acceso_a(peticion):
    """La fila `AdminFeria` de quien pide sobre la feria de la URL, o None.

    La feria sale de ``peticion.tenant``, que puso el middleware al
    resolver el prefijo. No se recibe por parámetro ni se re-resuelve el
    slug: si esas dos fuentes divergieran, el permiso se comprobaría
    contra una feria y los datos saldrían de otra.

    Es pública —y no privada, como fue hasta el 2026-08-26— porque la
    usan también las pantallas que **no** exigen permiso pero enseñan
    cosas distintas según quién mire: el catálogo de convocatorias, que
    es público y sin embargo le muestra los borradores a quien
    administra la feria (CU-FER-006). Que haya una sola respuesta a
    "¿administra ésta?" es lo que impide que la pantalla y el decorador
    discrepen.

    Por eso también tolera a quien no ha iniciado sesión: esas pantallas
    la llaman antes de saber si hay alguien detrás.
    """
    feria = getattr(peticion, "tenant", None)
    if feria is None or feria.es_la_de_sistema:
        return None
    usuario = getattr(peticion, "user", None)
    if usuario is None or not usuario.is_authenticated:
        return None
    return AdminFeria.objects.filter(feria=feria, persona=usuario).first()


def es_operador(peticion) -> bool:
    """¿Es el equipo técnico? (`ADR-0005`)

    El operador de la plataforma es el superusuario de Django. Alcanza
    **todas** las ferias sin tener fila en ``AdminFeria``, que es la
    excepción que ADR-0005 abre sobre ADR-0004 para que una edición
    cuyo dueño se fue no quede inoperable.

    Se pide ``is_superuser`` y no ``is_staff`` a propósito: son dos
    techos distintos y el reparto es el de Django. ``is_staff`` abre los
    dos admin de Django —incluido el de la edición, donde se dan de alta
    las convocatorias—; ``is_superuser`` es lo único que además sustituye
    a ser dueño de la feria.
    """
    usuario = getattr(peticion, "user", None)
    return bool(
        usuario is not None
        and usuario.is_authenticated
        and usuario.is_active
        and usuario.is_superuser
    )


def administra(peticion) -> bool:
    """¿Puede operar el contenido de esta feria?

    Tiene fila en ``AdminFeria`` —dueña o no— o es el operador. Es la
    pregunta que hace ``requiere_admin_feria``, y también la que hacen
    las pantallas que no exigen permiso pero enseñan cosas distintas
    según quién mire (el catálogo, la barra superior). Que salga de una
    sola función es lo que impide que la pantalla y el decorador
    discrepen.
    """
    return acceso_a(peticion) is not None or es_operador(peticion)


def tiene_alcance_de_dueno(peticion) -> bool:
    """¿Alcanza además lo reservado al dueño?

    Accesos y convocatorias (CU-FER-003 a CU-FER-009). Lo tiene quien es
    dueño de esta feria y, desde `ADR-0005`, el operador de la
    plataforma.
    """
    acceso = acceso_a(peticion)
    return (acceso is not None and acceso.es_dueno) or es_operador(peticion)


def requiere_admin_feria(vista):
    """Panel de una feria: hay que administrar **ésta**."""

    @functools.wraps(vista)
    def envoltura(peticion, *args, **kwargs):
        if not peticion.user.is_authenticated:
            return redirect(url_publica("registros:admin_acceso"))
        if not administra(peticion):
            # Administrar otra feria no da acceso a ésta. Se dice sin
            # rodeos: quien llega aquí ya demostró su identidad, así que
            # el mensaje no revela nada que no sepa.
            raise PermissionDenied("Tu cuenta no administra esta feria.")
        return vista(peticion, *args, **kwargs)

    return envoltura


def requiere_dueno_feria(vista):
    """El dueño de la feria, o el operador de la plataforma.

    Enmienda del 2026-08-25 a ADR-0004 (qué queda reservado al dueño) y
    `ADR-0005` (que el operador también lo alcanza).
    """

    @functools.wraps(vista)
    def envoltura(peticion, *args, **kwargs):
        if not peticion.user.is_authenticated:
            return redirect(url_publica("registros:admin_acceso"))
        if tiene_alcance_de_dueno(peticion):
            return vista(peticion, *args, **kwargs)
        # Los dos mensajes se conservan separados: no es lo mismo no
        # tener nada que ver con esta feria que administrarla y toparse
        # con el techo del dueño. Quien lee el segundo sabe a quién
        # pedírselo.
        if acceso_a(peticion) is None:
            raise PermissionDenied("Tu cuenta no administra esta feria.")
        raise PermissionDenied("Solo quien es dueño de esta feria puede hacer esto.")

    return envoltura
