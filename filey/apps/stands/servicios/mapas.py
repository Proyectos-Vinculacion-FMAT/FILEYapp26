"""
Cargar el showfloor de una convocatoria (`CU-STD-039`).

El sistema **no dibuja mapas**: recibe uno hecho fuera, lo traduce a
filas, y a partir de ahí lo vuelve a generar él (`CU-STD-037`, `038`).
Eso es lo que convierte el mapa en un dato del sistema en vez de un
archivo suelto del que nadie sabe qué versión está viva.

.. note:: Qué formato se lee

   `filey-mapa/1`, que es el que produce `scripts/derivar-mapa/` y en el
   que está el mapa de 2026. `CU-STD-039` menciona además las claves del
   componente de mapa (`grid`, `stands`, `decorations`); ese archivo no
   existe en el repositorio, así que se lee lo que sí hay. El campo
   `formato` está justo para poder añadir el otro lector el día que
   aparezca sin tocar nada de lo de aquí.

.. important:: Tres campos se aceptan y se tiran

   ============== =========================================================
   `estado`       Lo produce el sistema: un stand nace `Disponible` y
                  cambia al reservarse (`RN-10`). Importarlo dejaría
                  escrito que un espacio está reservado sin que exista la
                  reserva que lo respalda.
   `precio`       Se deriva de la superficie y del `costo_m2` de la
                  convocatoria (`RN-01`).
   `ocupante_2026` Es quién estuvo, no quién está.
   ============== =========================================================
"""

import logging
from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.servicios import registros

from ..models import DecoracionMapa, MapaShowfloor, Stand

logger = logging.getLogger(__name__)

FORMATO = "filey-mapa/1"


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
    *, convocatoria: Convocatoria, datos: dict, confirmado: bool = False
) -> Resumen:
    """Deja el mapa del archivo como el de esta convocatoria.

    Todo o nada: se valida el archivo **entero** antes de escribir una
    sola fila (`E2`). Un mapa importado a medias es peor que no importarlo
    — se ve igual que uno bueno y le faltan espacios que nadie echa de
    menos hasta que alguien pregunta por el suyo.

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

    formato = datos.get("formato")
    if formato != FORMATO:
        raise ImportacionRechazada(
            f"Formato «{formato or 'sin declarar'}»; esto lee «{FORMATO}»."
        )

    mapa = _validar_reticula(datos.get("mapa"))
    stands = _validar_stands(datos.get("stands"), mapa)
    decoraciones = _validar_decoraciones(datos.get("decoraciones") or [], mapa)
    return mapa, stands, decoraciones


def _entero(valor, campo: str, minimo: int = 0) -> int:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < minimo:
        raise ImportacionRechazada(
            f"`{campo}` tiene que ser un entero ≥ {minimo}; llegó {valor!r}."
        )
    return valor


def _validar_reticula(mapa) -> dict:
    if not isinstance(mapa, dict):
        raise ImportacionRechazada("Falta la retícula (`mapa`).")
    salon = (mapa.get("salon") or "").strip()
    if not salon:
        raise ImportacionRechazada("La retícula no dice en qué salón se monta.")
    try:
        metros = Decimal(str(mapa.get("metros_por_celda", "1")))
    except (ArithmeticError, ValueError):
        raise ImportacionRechazada(
            f"`metros_por_celda` no es un número: {mapa.get('metros_por_celda')!r}."
        ) from None
    if metros <= 0:
        raise ImportacionRechazada("`metros_por_celda` tiene que ser mayor que cero.")
    return {
        "salon": salon[:160],
        "columnas": _entero(mapa.get("columnas"), "mapa.columnas", 1),
        "filas": _entero(mapa.get("filas"), "mapa.filas", 1),
        "metros_por_celda": metros,
        "tamano_celda": _entero(mapa.get("tamano_celda", 12), "mapa.tamano_celda", 1),
    }


def _rectangulos_de(entrada: dict, donde: str) -> list[dict]:
    """La forma, sea rectangular o irregular, ya comprobada."""
    crudos = entrada.get("rectangulos")
    if crudos is None:
        crudos = [
            {
                "col": entrada.get("col"),
                "fila": entrada.get("fila"),
                "ancho_celdas": entrada.get("ancho_celdas"),
                "alto_celdas": entrada.get("alto_celdas"),
            }
        ]
    elif not isinstance(crudos, list) or not crudos:
        raise ImportacionRechazada(f"{donde}: `rectangulos` está vacío o no es lista.")

    limpios = []
    for i, r in enumerate(crudos):
        if not isinstance(r, dict):
            raise ImportacionRechazada(f"{donde}: el rectángulo {i} no es un objeto.")
        limpios.append(
            {
                "col": _entero(r.get("col"), f"{donde}.col"),
                "fila": _entero(r.get("fila"), f"{donde}.fila"),
                "ancho_celdas": _entero(r.get("ancho_celdas"), f"{donde}.ancho", 1),
                "alto_celdas": _entero(r.get("alto_celdas"), f"{donde}.alto", 1),
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
        clave = str(s.get("clave") or "").strip()
        if not clave:
            raise ImportacionRechazada(f"El espacio {i} no tiene clave.")
        if clave in claves:
            raise ImportacionRechazada(f"La clave «{clave}» aparece dos veces.")
        claves.add(clave)

        donde = f"El espacio «{clave}»"
        rects = _rectangulos_de(s, donde)
        _dentro_de(rects, mapa, donde)

        # Que dos espacios no se pisen. Se comprueba **celda a celda** y
        # no por envolvente: un stand en L tiene el hueco de la L ocupado
        # por sus vecinos, y con envolventes esto rechazaría un mapa
        # correcto.
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
                "etiqueta": str(s.get("etiqueta") or clave)[:60],
                "zona": str(s.get("zona") or "")[:80],
                "incluye": str(s.get("incluye") or ""),
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
        raise ImportacionRechazada("`decoraciones` tiene que ser una lista.")

    limpias = []
    for i, d in enumerate(decoraciones):
        if not isinstance(d, dict):
            raise ImportacionRechazada(f"La decoración {i} no es un objeto.")
        etiqueta = str(d.get("etiqueta") or "").strip()
        if not etiqueta:
            raise ImportacionRechazada(f"La decoración {i} no tiene rótulo.")

        donde = f"La decoración «{etiqueta}»"
        tipo = d.get("tipo") or DecoracionMapa.Tipo.RECTANGULO
        if tipo not in DecoracionMapa.Tipo.values:
            raise ImportacionRechazada(f"{donde}: tipo «{tipo}» desconocido.")

        fila = {
            "tipo": tipo,
            "etiqueta": etiqueta[:120],
            "color": str(d.get("color") or "")[:20],
            "col": _entero(d.get("col"), f"{donde}.col"),
            "fila": _entero(d.get("fila"), f"{donde}.fila"),
            "ancho_celdas": None,
            "alto_celdas": None,
        }
        if tipo == DecoracionMapa.Tipo.RECTANGULO:
            fila["ancho_celdas"] = _entero(d.get("ancho_celdas"), f"{donde}.ancho", 1)
            fila["alto_celdas"] = _entero(d.get("alto_celdas"), f"{donde}.alto", 1)
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
