"""
Cargar el showfloor de una convocatoria (`CU-STD-039`).

El sistema **no dibuja mapas**: recibe uno hecho fuera, lo traduce a
filas, y a partir de ahí lo vuelve a generar él (`CU-STD-037`, `038`).
Eso es lo que convierte el mapa en un dato del sistema en vez de un
archivo suelto del que nadie sabe qué versión está viva.

.. note:: Se lee el formato del componente de mapa

   `grid` / `stands` / `decorations`, el que describe
   `docs/bridge_protocol.md` de `event-stand-map` (`ADR-0008`). Es el
   mismo que el editor produce en su mensaje `saveMap`, así que lo que
   salga del editor entra por aquí sin traducción.

   .. warning:: Reimportar un `saveMap` **pierde dos campos**

      `salon` y `includes` son de FILEY y no del contrato: el canvas no
      los conoce, así que su `to_dict()` no los devuelve. Un mapa que
      salga del editor y vuelva por aquí deja el recinto en «Sin
      especificar» y borra el «qué incluye» de los 151 espacios, sin
      protestar.

      Hoy no puede pasar —el editor está fuera de alcance por
      `CU-STD-039`—, y el día que entre hay que resolverlo antes:
      conservando los valores que ya tenía cada `Stand` en vez de
      reemplazarlos, o llevando los dos campos fuera del mapa.

   Las claves van **en inglés** y es la única parte del sistema donde
   eso pasa. No es un descuido de la regla 7: es un formato de
   intercambio con un componente externo, y renombrarlo obligaría a
   traducir en los dos sentidos justo en el camino donde un error
   enseña a un aplicante quién reservó qué.

.. important:: Tres campos se aceptan y se tiran

   ================ =======================================================
   `status`         Lo produce el sistema: un stand nace `disponible` y
                    cambia al reservarse (`RN-10`). Importarlo dejaría
                    escrito que un espacio está reservado sin que exista
                    la reserva que lo respalda.
   `price`          Se deriva de la superficie y del `costo_m2` de la
                    convocatoria (`RN-01`).
   `dimensions_text` La superficie sale de la forma y de
                    `meters_per_cell`.
   ================ =======================================================

   Los tres se aceptan sin protestar —vienen en el formato del
   componente— y no se guardan. Al volver a generar el JSON salen
   calculados.
"""

import logging
import re
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.servicios import registros

from ..models import BitacoraSTD, DecoracionMapa, MapaShowfloor, Stand
from . import bitacora

logger = logging.getLogger(__name__)

#: Cuántas celdas mide el lado de una celda al dibujar, si el archivo no
#: lo dice. Es presentación pura y no entra en ningún cálculo.
CELDA_POR_OMISION = 32

#: Qué puede llevar la clave de un espacio. Es estrecho a propósito: la
#: clave va **dentro de una URL** y la compone también el JavaScript del
#: mapa, sin escaparla. Las del plano de 2026 —`24B`, `55A`, `109`— caben
#: de sobra.
CLAVE_ADMISIBLE = re.compile(r"^[\w-]+$", re.UNICODE)


class ImportacionRechazada(Exception):
    """El archivo no se puede cargar. El mensaje dice qué falla y dónde."""


class HayStandsReservados(ImportacionRechazada):
    """Un stand del mapa actual pertenece a una reserva (`CU-STD-039` E1).

    Tiene excepción propia porque **no hay confirmación que lo permita**,
    al revés que reemplazar un mapa cualquiera: borrar un stand reservado
    deja una reserva apuntando a un espacio que ya no existe, y con
    dinero abonado detrás.
    """


@dataclass(frozen=True)
class Resumen:
    """Lo que se cargó, para decirlo (`CU-STD-039` paso 7)."""

    stands: int
    decoraciones: int
    metros_cuadrados: Decimal
    reemplazo: bool

    def __str__(self):
        verbo = "Reemplazado" if self.reemplazo else "Cargado"
        return (
            f"{verbo}: {self.stands} espacios ({self.metros_cuadrados:.0f} m² "
            f"vendibles) y {self.decoraciones} decoraciones."
        )


def importar(
    *,
    convocatoria: Convocatoria,
    datos: dict,
    confirmado: bool = False,
    persona=None,
) -> Resumen:
    """Deja el mapa del archivo como el de esta convocatoria.

    Todo o nada: se valida el archivo **entero** antes de escribir una
    sola fila (`E2`). Un mapa importado a medias es peor que no importarlo
    — se ve igual que uno bueno y le faltan espacios que nadie echa de
    menos hasta que alguien pregunta por el suyo.

    :param persona: quién lo importa, para la bitácora. ``None`` desde
        `manage.py importar_mapa`, y ahí es la verdad: no lo hizo ninguna
        sesión. Desde el admin llega `peticion.user`.
    :param confirmado: hace falta en `True` para reemplazar un mapa que ya
        existía (`A1`). Sin él se rechaza diciendo cuántos stands se iban
        a llevar por delante; es un borrado de decenas de filas y no debe
        poder ocurrir por un clic de más.
    :raises ImportacionRechazada: y no se escribe nada.
    """
    if convocatoria.tipo != TipoConvocatoria.STD:
        raise ImportacionRechazada(
            f"«{convocatoria.nombre}» es una convocatoria {convocatoria.tipo}; "
            "un showfloor es de una de stands."
        )

    # `E3`: una edición archivada se consulta, no se remonta. Es la misma
    # guarda que usa el envío de solicitudes, y por eso se pregunta a
    # `FER` en vez de mirar el estado aquí.
    try:
        registros.exigir_edicion_operable()
    except registros.RegistroRechazado as exc:
        raise ImportacionRechazada(str(exc)) from exc

    mapa_datos, stands, decoraciones = _validar(datos)

    anterior = MapaShowfloor.objects.filter(convocatoria=convocatoria).first()
    if anterior is not None:
        _exigir_que_ninguno_este_reservado(anterior)
        if not confirmado:
            raise ImportacionRechazada(
                f"«{convocatoria.nombre}» ya tiene un mapa con "
                f"{anterior.stands.count()} espacios. Reemplazarlo los borra "
                "todos; hay que confirmarlo."
            )

    with transaction.atomic():
        if anterior is not None:
            anterior.delete()
        mapa = MapaShowfloor.objects.create(convocatoria=convocatoria, **mapa_datos)
        Stand.objects.bulk_create(
            [Stand(mapa=mapa, **s) for s in stands]
        )
        DecoracionMapa.objects.bulk_create(
            [DecoracionMapa(mapa=mapa, **d) for d in decoraciones]
        )

    resumen = Resumen(
        stands=len(stands),
        decoraciones=len(decoraciones),
        metros_cuadrados=mapa.metros_cuadrados_vendibles,
        reemplazo=anterior is not None,
    )
    logger.info(
        "Mapa importado en la convocatoria «%s»: %s", convocatoria.nombre, resumen
    )
    # Reemplazar un mapa borra decenas de filas y cambia el recinto que
    # todo el mundo está mirando. Es la operación más destructiva del
    # dominio y la única que no deja rastro en ninguna fila: las viejas
    # ya no existen.
    bitacora.anotar(
        persona=persona,
        accion=BitacoraSTD.Accion.MAPA_IMPORTADO,
        objeto=mapa,
        stands=resumen.stands,
        decoraciones=resumen.decoraciones,
        metros_cuadrados=str(resumen.metros_cuadrados),
        reemplazo=resumen.reemplazo,
    )
    return resumen


def _exigir_que_ninguno_este_reservado(mapa: MapaShowfloor) -> None:
    """`E1`. Hoy no puede pasar; en cuanto exista `Reserva`, sí.

    Se escribe ahora y no cuando llegue la reserva porque el orden real
    de los hechos es el contrario: primero se importa un mapa, después se
    reserva, y el día que alguien reimporte encima de reservas vivas esto
    ya tiene que estar. Mientras `Reserva` no exista, mira el estado del
    stand, que es lo que la reserva mueve (`RN-10`).
    """
    tomados = list(
        mapa.stands.exclude(estado=Stand.Estado.DISPONIBLE).values_list(
            "clave", flat=True
        )[:10]
    )
    if tomados:
        raise HayStandsReservados(
            "No se puede reemplazar el mapa: "
            f"{', '.join(tomados)} ya no están disponibles. "
            "Hay que resolver esas reservas antes (CU-STD-035)."
        )


# ── La validación del archivo ─────────────────────────────────
#
# Devuelve datos limpios en vez de comprobar y volver a leer: así el
# `importar` de arriba no vuelve a tocar el diccionario crudo, y cualquier
# campo que el archivo traiga de más se queda fuera por construcción.


def _validar(datos: dict) -> tuple[dict, list[dict], list[dict]]:
    if not isinstance(datos, dict):
        raise ImportacionRechazada("El archivo no es un objeto JSON.")

    mapa = _validar_reticula(datos.get("grid"))
    stands = _validar_stands(datos.get("stands"), mapa)
    decoraciones = _validar_decoraciones(datos.get("decorations") or [], mapa)
    return mapa, stands, decoraciones


def _entero(valor, campo: str, minimo: int = 0) -> int:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < minimo:
        raise ImportacionRechazada(
            f"`{campo}` tiene que ser un entero ≥ {minimo}; llegó {valor!r}."
        )
    return valor


def _validar_reticula(grid) -> dict:
    """`grid` → los campos de `MapaShowfloor`.

    `salon` no está en el contrato del componente —al canvas le da igual
    en qué recinto se monta— y aquí sí hace falta, así que se admite
    fuera de `grid`, en la raíz del archivo, y se le pone un valor
    genérico si no viene. Rechazar por eso dejaría un mapa correcto sin
    poder cargarse por un rótulo.
    """
    if not isinstance(grid, dict):
        raise ImportacionRechazada("Falta la retícula (`grid`).")
    try:
        metros = Decimal(str(grid.get("meters_per_cell", "1")))
    except (ArithmeticError, ValueError):
        raise ImportacionRechazada(
            f"`meters_per_cell` no es un número: {grid.get('meters_per_cell')!r}."
        ) from None
    if metros <= 0:
        raise ImportacionRechazada("`meters_per_cell` tiene que ser mayor que cero.")
    return {
        "salon": str(grid.get("salon") or "Sin especificar")[:160],
        "columnas": _entero(grid.get("cols"), "grid.cols", 1),
        "filas": _entero(grid.get("rows"), "grid.rows", 1),
        "metros_por_celda": metros,
        "tamano_celda": _entero(
            grid.get("cell_size", CELDA_POR_OMISION), "grid.cell_size", 1
        ),
    }


def _rectangulos_de(entrada: dict, donde: str) -> list[dict]:
    """La forma, en las claves **del dominio**.

    Aquí se cruza la frontera: entra `col`/`row`/`w`/`h` del contrato y
    sale `col`/`fila`/`ancho_celdas`/`alto_celdas`, que es lo que guarda
    `Stand`. Es el único sitio del sistema donde se traduce, y por eso
    está en una sola función.
    """
    crudos = entrada.get("rects")
    if crudos is None:
        crudos = [entrada]
    elif not isinstance(crudos, list) or not crudos:
        raise ImportacionRechazada(f"{donde}: `rects` está vacío o no es lista.")

    limpios = []
    for i, r in enumerate(crudos):
        if not isinstance(r, dict):
            raise ImportacionRechazada(f"{donde}: el rectángulo {i} no es un objeto.")
        limpios.append(
            {
                "col": _entero(r.get("col"), f"{donde}.col"),
                "fila": _entero(r.get("row"), f"{donde}.row"),
                "ancho_celdas": _entero(r.get("w"), f"{donde}.w", 1),
                "alto_celdas": _entero(r.get("h"), f"{donde}.h", 1),
            }
        )
    return limpios


def _dentro_de(rects: list[dict], mapa: dict, donde: str) -> None:
    for r in rects:
        if (
            r["col"] + r["ancho_celdas"] > mapa["columnas"]
            or r["fila"] + r["alto_celdas"] > mapa["filas"]
        ):
            raise ImportacionRechazada(
                f"{donde} se sale de la retícula de "
                f"{mapa['columnas']}×{mapa['filas']}."
            )


def _validar_stands(stands, mapa: dict) -> list[dict]:
    if not isinstance(stands, list) or not stands:
        raise ImportacionRechazada("El archivo no trae ningún espacio.")

    limpios, claves, ocupadas = [], set(), {}
    for i, s in enumerate(stands):
        if not isinstance(s, dict):
            raise ImportacionRechazada(f"El espacio {i} no es un objeto.")
        clave = str(s.get("id") or "").strip()
        if not clave:
            raise ImportacionRechazada(f"El espacio {i} no tiene `id`.")
        # La clave **viaja dentro de una URL** —`…/mapa/<clave>/`— y la
        # arma también el JavaScript de la tarjeta del mapa, que no la
        # escapa. Una con `/`, `?` o `#` deja un enlace que no resuelve o
        # que apunta a otra parte, y el mapa se ve perfecto hasta que
        # alguien pulsa ese espacio.
        if not CLAVE_ADMISIBLE.match(clave):
            raise ImportacionRechazada(
                f"El `id` «{clave}» no sirve como clave: solo letras, "
                "números, guion y guion bajo."
            )
        if clave in claves:
            raise ImportacionRechazada(f"El `id` «{clave}» aparece dos veces.")
        claves.add(clave)

        donde = f"El espacio «{clave}»"
        rects = _rectangulos_de(s, donde)
        _dentro_de(rects, mapa, donde)

        # Que dos espacios no se pisen. Se comprueba **celda a celda** y
        # no por envolvente: un stand en L tiene el hueco de la L ocupado
        # por sus vecinos, y con envolventes esto rechazaría un mapa
        # correcto. El de 2026 tiene tres.
        for r in rects:
            for c in range(r["col"], r["col"] + r["ancho_celdas"]):
                for f in range(r["fila"], r["fila"] + r["alto_celdas"]):
                    otro = ocupadas.get((c, f))
                    if otro is not None:
                        raise ImportacionRechazada(
                            f"«{clave}» y «{otro}» se pisan en la celda ({c}, {f})."
                        )
                    ocupadas[(c, f)] = clave

        irregular = len(rects) > 1
        limpios.append(
            {
                "clave": clave[:20],
                "etiqueta": str(s.get("label") or clave)[:60],
                "zona": str(s.get("zone") or "")[:80],
                "incluye": str(s.get("includes") or ""),
                "col": min(r["col"] for r in rects),
                "fila": min(r["fila"] for r in rects),
                "ancho_celdas": None if irregular else rects[0]["ancho_celdas"],
                "alto_celdas": None if irregular else rects[0]["alto_celdas"],
                "rectangulos": rects if irregular else None,
                # `RN-10`: nace disponible, diga lo que diga el archivo.
                "estado": Stand.Estado.DISPONIBLE,
            }
        )
    return limpios


def _validar_decoraciones(decoraciones, mapa: dict) -> list[dict]:
    if not isinstance(decoraciones, list):
        raise ImportacionRechazada("`decorations` tiene que ser una lista.")

    #: `rect` y `text` en el contrato; `rectangulo` y `texto` en el modelo.
    TIPOS = {
        "rect": DecoracionMapa.Tipo.RECTANGULO,
        "text": DecoracionMapa.Tipo.TEXTO,
    }

    limpias = []
    for i, d in enumerate(decoraciones):
        if not isinstance(d, dict):
            raise ImportacionRechazada(f"La decoración {i} no es un objeto.")
        tipo_crudo = d.get("type") or "rect"
        if tipo_crudo not in TIPOS:
            raise ImportacionRechazada(f"La decoración {i}: tipo «{tipo_crudo}» desconocido.")
        tipo = TIPOS[tipo_crudo]

        # Un rectángulo se rotula con `label` y un texto con `text`: son
        # dos claves distintas en el contrato para el mismo campo aquí.
        etiqueta = str(
            (d.get("text") if tipo == DecoracionMapa.Tipo.TEXTO else d.get("label"))
            or ""
        ).strip()
        if not etiqueta:
            raise ImportacionRechazada(f"La decoración {i} no tiene rótulo.")

        donde = f"La decoración «{etiqueta}»"
        fila = {
            "tipo": tipo,
            "etiqueta": etiqueta[:120],
            "color": str(d.get("color") or "")[:20],
            "col": _entero(d.get("col"), f"{donde}.col"),
            "fila": _entero(d.get("row"), f"{donde}.row"),
            "ancho_celdas": None,
            "alto_celdas": None,
        }
        if tipo == DecoracionMapa.Tipo.RECTANGULO:
            fila["ancho_celdas"] = _entero(d.get("w"), f"{donde}.w", 1)
            fila["alto_celdas"] = _entero(d.get("h"), f"{donde}.h", 1)
            _dentro_de([fila], mapa, donde)
        elif fila["col"] >= mapa["columnas"] or fila["fila"] >= mapa["filas"]:
            raise ImportacionRechazada(f"{donde} se sale de la retícula.")
        limpias.append(fila)
    return limpias


def mapa_de(convocatoria: Convocatoria) -> MapaShowfloor | None:
    """El mapa de esta convocatoria, o ``None`` si todavía no tiene.

    ``None`` **no es un error**: una convocatoria recién creada no tiene
    mapa, y eso es `E2` de `CU-STD-009` —"el mapa no está disponible por
    el momento"—, no una pantalla rota.
    """
    return (
        MapaShowfloor.objects.filter(convocatoria=convocatoria)
        .prefetch_related("stands", "decoraciones")
        .first()
    )
