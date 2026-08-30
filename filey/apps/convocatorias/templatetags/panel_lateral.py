"""
La barra lateral del panel de administración.

Es chasis, como `{% topbar %}`: la pantalla no la maqueta ni le pasa sus
enlaces, los deduce el tag. Que una pantalla nueva de administración no
tenga que enumerar la navegación es lo que impide que dos paneles del
mismo sistema ofrezcan menús distintos.

.. note:: Por qué vive en `apps/convocatorias` y no en `apps/ferias`

   Las secciones de un módulo salen del registro (`ADR-0006`), que es de
   `apps/convocatorias`. Ponerlo en `apps/ferias` obligaría a que
   `ferias` importara `convocatorias`, y `convocatorias` ya importa
   `ferias`: sería un círculo, que es justo lo que prohíbe la regla 4.

.. note:: Persistente, no un cajón que se abre

   Sigue al prototipo de `STD` —el proyecto Angular,
   `core/layout/admin-layout.component.ts`—, que usa un `mat-sidenav` en
   ``mode="side" opened``: fija, empujando el contenido, con un botón que
   la alterna. Se replican sus medidas (240 px de barra, 48 px de tira) y
   su estado activo.

   Lo único que **no** se replica es su `cerrarSiMovil()`: en pantalla
   chica esto no es un cajón sino una tira horizontal, porque un cajón
   necesita JavaScript para existir y la regla 6 no lo admite para la
   navegación. Por lo mismo se descartó la barra de `VIS` del prototipo
   estático, que la inyecta `app.js`.
"""

from django import template
from django.urls import NoReverseMatch, reverse

from comun.urls import url_publica

from .. import modulos

register = template.Library()


def _resolver(nombre: str, *args) -> str | None:
    """La URL, o ``None`` si esa ruta no está montada en este urlconf.

    Se traga el `NoReverseMatch` por lo mismo que el catálogo: un módulo
    inscrito cuyas rutas no están montadas no debe tumbar la pantalla
    entera, y una entrada de menos se nota; un error 500, también, pero
    peor.
    """
    try:
        return reverse(nombre, args=args)
    except NoReverseMatch:
        return None


def _entrada(etiqueta, icono, url, rutas, vista_actual, *, planeada=False):
    """Una entrada del menú, o ``None`` si no hay nada que enseñar.

    :param rutas: los **nombres** de ruta que esta entrada representa —el
        suyo y los de las pantallas que cuelgan de ella—.
    :param vista_actual: el nombre de la vista que se está pintando.
    :param planeada: la sección existe en el plan del módulo y su
        pantalla no. Se pinta apagada y sin enlace, en vez de omitirla:
        el menú enseña así la forma completa del módulo y nadie busca por
        todo el panel dónde se validan los pagos.

    .. note:: Se compara por nombre de ruta, no por camino

       Comparar caminos por prefijo parecía suficiente y no lo es: la URL
       del catálogo es la raíz de la feria, y **todo** lo de dentro
       empieza por ella — con lo que "Convocatorias" salía marcada en
       cada pantalla del panel. El nombre de la vista es exacto y no
       depende de cómo estén anidadas las URLs.
    """
    if url is None and not planeada:
        return None
    return {
        "etiqueta": etiqueta,
        "icono": icono,
        "url": url,
        "planeada": planeada,
        "activa": bool(url) and vista_actual in rutas,
    }


def _grupo(titulo, entradas) -> dict | None:
    entradas = [e for e in entradas if e is not None]
    return {"titulo": titulo, "entradas": entradas} if entradas else None


@register.inclusion_tag("componentes/barra_lateral.html", takes_context=True)
def barra_lateral(context):
    """Los grupos de navegación del panel, ya resueltos.

    Dos grupos, y el orden dice de qué se está hablando: primero lo de la
    **feria** —que existe en todas las pantallas de administración— y
    después lo del **módulo**, que solo aparece dentro de una
    convocatoria.
    """
    peticion = context.get("request")
    convocatoria = context.get("convocatoria")
    feria = getattr(peticion, "tenant", None)
    resolucion = getattr(peticion, "resolver_match", None)
    vista_actual = resolucion.view_name if resolucion is not None else ""

    # **Solo la salida hacia el catálogo.** El panel de una convocatoria
    # habla de esa convocatoria y de nada más: los accesos de la feria
    # —quién puede administrarla— son de otro nivel, y ofrecerlos aquí
    # invita a confundir "administrar esta convocatoria" con "administrar
    # esta feria", que son permisos distintos (`ADR-0004`).
    de_la_feria = [
        _entrada(
            "Convocatorias",
            "🗂️",
            _resolver("convocatorias:catalogo"),
            ("convocatorias:catalogo",),
            vista_actual,
        ),
    ]

    grupos = [_grupo(feria.nombre if feria else "Esta feria", de_la_feria)]

    if convocatoria is not None:
        modulo = modulos.modulo_de(convocatoria.tipo)
        if modulo is not None:
            grupos.append(
                _grupo(
                    modulo.etiqueta,
                    [
                        _entrada(
                            seccion.etiqueta,
                            seccion.icono,
                            _resolver(seccion.ruta, convocatoria.pk)
                            if seccion.ruta
                            else None,
                            (seccion.ruta, *seccion.tambien),
                            vista_actual,
                            planeada=seccion.ruta is None,
                        )
                        for seccion in modulo.secciones_panel
                    ],
                )
            )

    return {
        "grupos": [g for g in grupos if g is not None],
        "convocatoria": convocatoria,
        # Salir de la feria hacia "mis ferias" — la única forma de cambiar
        # de edición sin volver atrás con el navegador.
        "url_mis_ferias": url_publica("ferias:mis_ferias"),
    }
