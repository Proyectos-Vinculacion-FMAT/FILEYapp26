"""
Le pone nombre a cada forma y escribe el JSON del mapa.

Es el único paso que **no se puede automatizar**: los números del plano
son texto blanco dentro de una caja azul, y leerlos pide OCR o pide
mirar. Se miró, y el resultado está aquí escrito a mano — islote por
islote, en orden de lectura— para que cualquiera pueda contrastarlo
contra el PDF sin volver a ejecutar nada.

La tabla se indexa por la **forma** y su posición, no por un número de
orden: si mañana la extracción cambia y una caja se parte o se funde, la
clave deja de encontrarse y el script falla en vez de asignar el número
de otro stand a la caja equivocada.
"""

import json
import sys
from pathlib import Path

# ── Qué es cada forma ─────────────────────────────────────────
#
# Clave: (col, fila, ancho, alto) de su **primer** rectángulo, que es el
# de arriba a la izquierda. Valor: la clave del stand, o una tupla
# ("deco", etiqueta) para lo que no se vende.
#
# El orden de este diccionario es el del plano leído de arriba abajo y de
# izquierda a derecha, agrupado por islote, para poder seguirlo con el
# PDF al lado.

DECO = "deco"

ASIGNACION = {
    # ── Franja de arriba, contra la zona de carga ──
    (127, 0, 7, 4): "132",
    (134, 0, 7, 4): "133",
    (141, 0, 5, 4): "134",
    (147, 0, 5, 4): "135",
    (152, 0, 12, 4): "136",
    # ── Bloque de la izquierda: servicios de la feria ──
    (0, 4, 3, 2): (DECO, "Seguridad"),
    (3, 4, 3, 2): (DECO, "Limpieza"),
    (6, 4, 14, 2): (DECO, "Bodega de expositores"),
    (20, 10, 12, 12): (DECO, "Sala Hernán Lara Zavala"),
    (7, 22, 4, 18): (DECO, "Oficina FILEY"),
    (11, 22, 4, 6): "123",
    (11, 28, 4, 6): "122",
    (11, 34, 4, 6): "121",
    # ── Esquina superior derecha ──
    (129, 8, 3, 3): "138",
    (132, 8, 3, 3): "139",
    (135, 8, 3, 3): "140",
    (129, 11, 9, 3): "137",
    (143, 8, 9, 6): "141",
    (156, 11, 5, 1): (DECO, "Módulo de información"),
    # ── Primera fila de stands, bajo los sanitarios ──
    (38, 10, 6, 3): (DECO, "Botiquín"),
    (38, 13, 6, 3): "124",
    (44, 10, 12, 6): "125",
    (56, 10, 6, 6): "126",
    (62, 10, 8, 6): "127",
    (76, 11, 10, 6): "128",
    (87, 11, 10, 6): "129",
    (102, 11, 8, 6): "130",
    (110, 11, 15, 6): "131",
    # ── Banda 85-109 ──
    (38, 20, 6, 2): "88",
    (44, 20, 3, 2): "89",
    (47, 20, 3, 2): "90",
    (38, 22, 6, 2): "85",
    (44, 22, 3, 2): "86",
    (47, 22, 3, 2): "87",
    (56, 20, 3, 2): "92",
    (59, 20, 9, 4): "93",
    (56, 22, 3, 2): "91",
    (74, 20, 6, 2): "95",
    (80, 20, 3, 2): "96",
    (83, 20, 3, 2): "97",  # en L: el pie baja por la izquierda
    (74, 22, 6, 2): "94",
    (92, 20, 6, 2): "100",
    (98, 20, 3, 2): "101",
    (101, 20, 3, 2): "102",
    (92, 22, 6, 2): "98",
    (98, 22, 6, 2): "99",
    (111, 20, 12, 2): "106",
    (111, 22, 3, 2): "103",
    (114, 22, 6, 2): "104",
    (120, 22, 3, 2): "105",
    (129, 20, 12, 4): "107",
    (147, 20, 12, 2): "109",  # en L
    (147, 22, 9, 2): "108",
    # ── Columna del muro derecho ──
    (165, 25, 2, 6): "110",
    (165, 31, 2, 6): "111",
    (165, 37, 2, 12): "112",
    # ── Banda 63-84 y los grandes ──
    (20, 28, 5, 4): "118",
    (25, 28, 4, 4): "119",
    (29, 28, 3, 4): "120",
    (38, 28, 9, 4): "63",
    (47, 28, 3, 2): "65",
    (47, 30, 3, 2): "64",
    (56, 28, 3, 4): "66",
    (59, 28, 9, 4): "67",
    (75, 29, 12, 10): "68",
    (92, 29, 12, 10): "69",
    (111, 29, 12, 10): "70",
    (129, 29, 6, 10): "71",
    (135, 29, 6, 4): "72",
    (135, 33, 6, 6): "73",
    (147, 28, 6, 2): "83",
    (153, 28, 6, 2): "84",
    (147, 30, 3, 2): "79",
    (150, 30, 3, 2): "80",
    (153, 30, 3, 2): "81",
    (156, 30, 3, 2): "82",
    # ── Banda 55-78 y 113-117 ──
    (20, 36, 6, 4): "113",
    (26, 36, 3, 2): "116",
    (29, 36, 3, 2): "117",
    (26, 38, 3, 2): "114",
    (29, 38, 3, 2): "115",
    (38, 36, 6, 2): "57",
    (44, 36, 3, 2): "58",
    (47, 36, 3, 2): "59",
    (38, 38, 3, 2): "55",
    (41, 38, 3, 2): "55A",
    (44, 38, 6, 2): "56",
    (56, 36, 12, 2): "62",  # en L
    (56, 38, 3, 2): "60",
    (59, 38, 3, 2): "61",
    (147, 36, 9, 2): "77",
    (156, 36, 3, 4): "78",
    (147, 38, 3, 2): "74",
    (150, 38, 3, 2): "75",
    (153, 38, 3, 2): "76",
    # ── Banda 24-54 ──
    (7, 42, 8, 15): (DECO, "Prensa FILEY-UADY"),
    (38, 43, 3, 2): "25",
    (41, 43, 3, 2): "25A",
    (44, 43, 3, 2): "25B",
    (47, 43, 3, 2): "26",
    (38, 45, 3, 2): "24",
    (41, 45, 3, 2): "24A",
    (44, 45, 6, 2): "24B",
    (56, 43, 3, 2): "29",
    (59, 43, 3, 2): "30",
    (62, 43, 6, 4): "31",
    (56, 45, 3, 2): "27",
    (59, 45, 3, 2): "28",
    (75, 43, 12, 2): "34",
    (75, 45, 6, 2): "32",
    (81, 45, 6, 2): "33",
    (92, 43, 6, 2): "38",
    (98, 43, 6, 2): "39",
    (92, 45, 6, 2): "35",
    (98, 45, 3, 2): "36",
    (101, 45, 3, 2): "37",
    (111, 43, 6, 2): "43",
    (117, 43, 6, 2): "44",
    (111, 45, 6, 2): "40",
    (117, 45, 3, 2): "41",
    (120, 45, 3, 2): "42",
    (129, 43, 3, 2): "46",
    (132, 43, 3, 2): "46A",
    (135, 43, 6, 2): "47",
    (129, 45, 12, 2): "45",
    (147, 43, 3, 2): "51",
    (150, 43, 3, 2): "52",
    (153, 43, 3, 2): "53",
    (156, 43, 3, 2): "54",
    (147, 45, 3, 2): "48",
    (150, 45, 3, 2): "49",
    (153, 45, 3, 2): "50",
    (156, 45, 3, 2): "54A",
    # ── Última banda, contra los accesos del sur ──
    (20, 45, 12, 12): (DECO, "Sala Effy Luz Vázquez"),
    (38, 51, 9, 4): "1",
    (47, 51, 3, 2): "1B",
    (47, 53, 3, 2): "1A",
    (56, 51, 12, 4): "2",
    (75, 51, 3, 2): "4",
    (78, 51, 3, 2): "5",
    (81, 51, 3, 2): "6",
    (84, 51, 3, 4): "7",
    (75, 53, 6, 2): "2A",
    (81, 53, 3, 2): "3",
    (92, 51, 3, 2): "12",
    (95, 51, 3, 2): "13",
    (98, 51, 3, 2): "14",
    (101, 51, 3, 2): "15",
    (92, 53, 3, 2): "8",
    (95, 53, 3, 2): "9",
    (98, 53, 3, 2): "10",
    (101, 53, 3, 2): "11",
    (111, 51, 3, 2): "19",
    (114, 51, 3, 2): "20",
    (117, 51, 3, 2): "21",
    (120, 51, 3, 2): "22",
    (111, 53, 3, 2): "16",
    (114, 53, 3, 2): "17",
    (117, 53, 6, 2): "18",
    (129, 51, 12, 4): "23",
    (153, 51, 12, 8): (DECO, "Sala José Emilio Pacheco"),
}

#: Quién ocupaba cada espacio en 2026, según lo rotulado en el plano.
#:
#: **No se importa**: una convocatoria nueva nace con todo disponible, y
#: pintar «SANBORNS» sobre un espacio libre sería mentir. Va en el JSON
#: porque el plano es el único registro de quién estuvo dónde, y perderlo
#: al convertirlo a datos sería tirar información que nadie tiene en otro
#: sitio.
OCUPANTES_2026 = {
    "68": "Grupo Planeta",
    "69": "Universidad Autónoma de Yucatán",
    "70": "Penguin Random House",
    "71": "Delfín Editorial",
    "93": "Librerías Gandhi",
    "125": "Fondo de Cultura Económica",
    "126": "SEDECULTA",
    "127": "La Jornada Maya",
    "128": "Ayuntamiento de Mérida",
    "129": "Sanborns",
    "130": "Comunicación Institucional",
    "131": "SEGEY",
    "133": "Novedades",
    "136": "Océano",
    "137": "VR Editoras",
    "141": "UABC",
}


def main(ruta_celdas, salida):
    celdas = json.load(open(ruta_celdas))

    stands, decoraciones, sin_asignar = [], [], []
    usadas = set()
    for forma in celdas:
        primero = forma["rects"][0]
        clave_pos = (
            primero["col"],
            primero["fila"],
            primero["ancho_celdas"],
            primero["alto_celdas"],
        )
        if clave_pos not in ASIGNACION:
            sin_asignar.append(clave_pos)
            continue
        usadas.add(clave_pos)
        que = ASIGNACION[clave_pos]

        if isinstance(que, tuple):
            decoraciones.append(
                {
                    "tipo": "rectangulo",
                    "col": primero["col"],
                    "fila": primero["fila"],
                    "ancho_celdas": max(
                        r["col"] + r["ancho_celdas"] for r in forma["rects"]
                    )
                    - min(r["col"] for r in forma["rects"]),
                    "alto_celdas": max(
                        r["fila"] + r["alto_celdas"] for r in forma["rects"]
                    )
                    - min(r["fila"] for r in forma["rects"]),
                    "etiqueta": que[1],
                }
            )
            continue

        stand = {"clave": que, "etiqueta": que, "estado": "Disponible"}
        if len(forma["rects"]) == 1:
            stand.update(
                col=primero["col"],
                fila=primero["fila"],
                ancho_celdas=primero["ancho_celdas"],
                alto_celdas=primero["alto_celdas"],
            )
        else:
            # Irregular: la forma son sus rectángulos, y los cuatro
            # campos de arriba van nulos (§3.5 del modelo de datos).
            stand.update(
                col=min(r["col"] for r in forma["rects"]),
                fila=min(r["fila"] for r in forma["rects"]),
                ancho_celdas=None,
                alto_celdas=None,
                rectangulos=forma["rects"],
            )
        if que in OCUPANTES_2026:
            stand["ocupante_2026"] = OCUPANTES_2026[que]
        stands.append(stand)

    faltan = set(ASIGNACION) - usadas
    if sin_asignar or faltan:
        for p in sin_asignar:
            print(f"! forma sin asignar: {p}", file=sys.stderr)
        for p in sorted(faltan):
            print(f"! asignación que no casó con ninguna forma: {p}", file=sys.stderr)
        raise SystemExit("la asignación y la extracción no coinciden")

    _comprobar(stands)

    cols = max(
        (r["col"] + r["ancho_celdas"] for s in stands for r in _rects(s)),
        default=0,
    )
    fils = max(
        (r["fila"] + r["alto_celdas"] for s in stands for r in _rects(s)), default=0
    )
    for d in decoraciones:
        cols = max(cols, d["col"] + d["ancho_celdas"])
        fils = max(fils, d["fila"] + d["alto_celdas"])

    mapa = {
        "formato": "filey-mapa/1",
        "origen": (
            "Derivado de «Plano FILEY 2026 Salón Chichén Itzá.pdf» "
            "(docs/soporte/documentos proporcionados por FILEY/…). "
            "Ver scripts/derivar-mapa/README.md."
        ),
        "mapa": {
            "salon": "Salón Chichén Itzá",
            "columnas": cols,
            "filas": fils,
            "metros_por_celda": 1.0,
            "tamano_celda": 12,
        },
        "stands": sorted(stands, key=_orden),
        "decoraciones": decoraciones,
    }
    Path(salida).write_text(
        json.dumps(mapa, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    m2 = sum(
        sum(r["ancho_celdas"] * r["alto_celdas"] for r in _rects(s)) for s in stands
    )
    print(
        f"{len(stands)} stands ({m2} m² vendibles), "
        f"{len(decoraciones)} decoraciones, retícula {cols}x{fils} m",
        file=sys.stderr,
    )


def _rects(stand):
    if stand.get("rectangulos"):
        return stand["rectangulos"]
    return [stand]


def _orden(stand):
    """Numérico donde se pueda: `2` antes que `10`, y `2` antes que `2A`."""
    clave = stand["clave"]
    numero = int("".join(c for c in clave if c.isdigit()))
    letra = "".join(c for c in clave if c.isalpha())
    return (numero, letra)


def _comprobar(stands):
    """Los tres errores que un mapa mal derivado comete en silencio."""
    claves = [s["clave"] for s in stands]
    repetidas = {c for c in claves if claves.count(c) > 1}
    if repetidas:
        raise SystemExit(f"claves repetidas: {sorted(repetidas)}")

    numeros = {int("".join(c for c in k if c.isdigit())) for k in claves}
    huecos = sorted(set(range(1, max(numeros) + 1)) - numeros)
    if huecos:
        raise SystemExit(f"faltan números del plano: {huecos}")

    for s in stands:
        for r in _rects(s):
            if r["ancho_celdas"] < 1 or r["alto_celdas"] < 1:
                raise SystemExit(f"{s['clave']} tiene un lado de cero")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
