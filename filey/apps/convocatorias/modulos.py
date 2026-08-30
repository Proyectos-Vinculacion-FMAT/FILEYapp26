"""
Qué app sirve cada tipo de convocatoria (`ADR-0006`).

`FER` enmarca las convocatorias; **no sabe qué hay detrás de ninguna**.
Que `tipo = STD` lleve a la pantalla de stands no puede resolverlo esta
app: `apps/convocatorias` es la mitad por feria de `FER`, y los dominios
verticales dependen de `FER` y nunca al revés (regla 4 de `CLAUDE.md`).
Escribir aquí ``reverse("stands:aplicar")`` invertiría la dependencia y,
de paso, reventaría el catálogo en cualquier despliegue donde `stands` no
esté instalado — que es el estado normal hoy.

Así que la relación se invierte: cada app vertical **se inscribe a sí
misma** al arrancar, desde su ``AppConfig.ready()``.

    # apps/stands/apps.py
    class StandsConfig(AppConfig):
        def ready(self):
            from apps.convocatorias.modulos import Modulo, registrar
            from .servicios import configuracion

            registrar(Modulo(
                tipo=TipoConvocatoria.STD,
                etiqueta="Venta de stands",
                url_aplicar="stands:aplicar",
                url_panel="stands:panel",
                crear_configuracion=configuracion.crear_por_defecto,
            ))

Este módulo define `Modulo`, `registrar` y `modulo_de`, y **no nombra a
ninguna app vertical**. Si alguna vez aparece un ``import`` de `stands`,
`eventos` o `visitas` en este archivo, el patrón está roto.

.. note:: Es estado global del proceso, y se acepta a sabiendas

   Se puebla en ``ready()`` y vive lo que vive el proceso. Es el mismo
   compromiso que el proyecto ya tiene con ``admin.site`` y con
   ``comun/admin_feria.py``. La contrapartida está escrita en el ADR: un
   módulo que se olvide de inscribirse **no da error**, sino que su
   tarjeta dice "próximamente" para siempre. Por eso cada vertical debe
   traer una prueba de que ``modulo_de(su_tipo)`` no es ``None``.
"""

from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field

from .models import TipoConvocatoria


class ModuloDuplicado(Exception):
    """Dos apps distintas dicen servir el mismo tipo de convocatoria."""


class TipoNoValido(Exception):
    """El módulo se inscribe con un tipo que `Convocatoria` no reconoce."""


@dataclass(frozen=True)
class SeccionPanel:
    """Una entrada del menú lateral del panel de un módulo.

    El módulo declara sus secciones y la barra lateral las pinta; ni
    `FER` ni la plantilla saben qué pantallas tiene `STD`, igual que no
    saben qué cuelga de un registro (`ADR-0006`).

    :param etiqueta: cómo se llama en pantalla.
    :param icono: un emoji. Es lo que usa el prototipo, y no un SVG,
        porque una barra lateral con seis iconos distintos sería seis
        assets que mantener para decir "solicitudes" y "reservas".
    :param ruta: **nombre** de la ruta, que recibe el id de la
        convocatoria. Se resuelve al pintar, no al inscribirse.
        ``None`` cuando la sección está en el plan del módulo pero su
        pantalla no existe todavía: se pinta apagada y sin enlace. Es
        deliberado — que el menú enseñe la forma completa del módulo
        evita la pregunta "¿y dónde se validan los pagos?", que hoy se
        responde buscando por todo el panel.
    """

    etiqueta: str
    icono: str
    ruta: str | None = None
    #: Otras rutas que **pertenecen** a esta sección: el detalle de una
    #: solicitud sigue siendo "Solicitudes". Se declaran por nombre y no
    #: se deducen del camino, porque un detalle no tiene por qué colgar
    #: de la URL de su listado —el de una solicitud no lleva la
    #: convocatoria a propósito, ver `apps/stands/urls.py`.
    tambien: tuple[str, ...] = ()


@dataclass(frozen=True)
class Modulo:
    """Lo que un dominio vertical declara sobre sí mismo.

    Deliberadamente corto: es el contrato entero entre `FER` y los seis
    módulos, y cada campo que se le añada lo tienen que llenar todos.

    :param tipo: valor de `TipoConvocatoria` que este módulo sirve.
    :param etiqueta: cómo se llama el módulo en pantalla, en las palabras
        del dominio ("Venta de stands", no "STD").
    :param url_aplicar: **nombre** de la ruta del formulario del módulo
        —no la URL—, que recibe el id de la convocatoria. Se resuelve con
        ``reverse`` en el momento de pintar, y no al inscribirse: durante
        ``ready()`` el urlconf todavía no está cargado.
    :param url_panel: nombre de la ruta del panel administrativo del
        módulo, si tiene. Opcional: un módulo puede existir para el
        participante antes de tener panel.
    :param secciones_panel: las entradas de su barra lateral, en el orden
        en que se usan. Vacío mientras el módulo no tenga panel. Es lo
        que hace que la barra sirva a los seis módulos sin que ninguno
        toque la plantilla.
    :param crear_configuracion: qué llamar al dar de alta una
        convocatoria de este tipo, para que nazca con su configuración
        (`CU-FER-005` paso 6). Recibe la `Convocatoria` recién creada y
        corre **dentro de la transacción del alta**: si revienta, no
        queda ni la convocatoria (E1).
    """

    tipo: str
    etiqueta: str
    url_aplicar: str
    url_panel: str | None = None
    secciones_panel: tuple[SeccionPanel, ...] = ()
    # Fuera de la comparación a propósito: lo que `registrar` vigila es
    # que dos apps distintas no se peleen un tipo, y eso se ve en la
    # etiqueta y en las rutas. Incluir el callback haría que inscribir un
    # `lambda` dos veces —dos objetos distintos con el mismo código—
    # pareciera un conflicto entre módulos.
    crear_configuracion: Callable[..., object] | None = field(
        default=None, compare=False
    )


_REGISTRO: dict[str, Modulo] = {}


def registrar(modulo: Modulo) -> Modulo:
    """Inscribe un módulo. Se llama desde ``AppConfig.ready()``.

    Falla ruidosamente en los dos casos en los que callar saldría caro:

    - Un ``tipo`` que `TipoConvocatoria` no reconoce. Sin esto, un typo
      —``"STND"``— se inscribiría sin protestar y el módulo quedaría
      inalcanzable para siempre, con la tarjeta diciendo "próximamente".
    - Dos módulos distintos peleándose el mismo tipo. Cuál gana
      dependería del orden de `INSTALLED_APPS`, que es exactamente la
      clase de dependencia que nadie quiere descubrir en producción.

    Volver a inscribir **el mismo** módulo no es error: ``ready()`` puede
    ejecutarse más de una vez en algunos arranques y eso no significa que
    nada esté mal.
    """
    if modulo.tipo not in TipoConvocatoria.values:
        raise TipoNoValido(
            f"«{modulo.tipo}» no es un tipo de convocatoria. "
            f"Los que hay: {', '.join(TipoConvocatoria.values)}."
        )

    ya_inscrito = _REGISTRO.get(modulo.tipo)
    if ya_inscrito is not None and ya_inscrito != modulo:
        raise ModuloDuplicado(
            f"El tipo {modulo.tipo} ya lo sirve «{ya_inscrito.etiqueta}» "
            f"({ya_inscrito.url_aplicar}); «{modulo.etiqueta}» no puede "
            "reclamarlo también."
        )

    _REGISTRO[modulo.tipo] = modulo
    return modulo


def modulo_de(tipo: str) -> Modulo | None:
    """El módulo que sirve ese tipo, o ``None`` si no hay ninguno.

    ``None`` **no es un error**: es el estado normal de cinco de los seis
    tipos hoy, y el catálogo es una pantalla pública que no puede caerse
    porque una convocatoria sea de un tipo que nadie sirve todavía
    (`CU-FER-006` A1). Quien pregunta degrada a "próximamente".
    """
    return _REGISTRO.get(tipo)


def modulos_registrados() -> dict[str, Modulo]:
    """Copia del registro. Para diagnóstico y para las pruebas."""
    return dict(_REGISTRO)


@contextmanager
def modulo_temporal(modulo: Modulo):
    """Inscribe un módulo solo mientras dure el bloque. **Para pruebas.**

    El registro es global al proceso, así que una prueba que inscriba un
    módulo de mentira se lo dejaría puesto a las siguientes. Existe por
    el mismo motivo que ``override_settings`` de Django, y como aquélla,
    no tiene sitio fuera de las pruebas.
    """
    anterior = _REGISTRO.get(modulo.tipo)
    _REGISTRO[modulo.tipo] = modulo
    try:
        yield modulo
    finally:
        if anterior is None:
            _REGISTRO.pop(modulo.tipo, None)
        else:
            _REGISTRO[modulo.tipo] = anterior
