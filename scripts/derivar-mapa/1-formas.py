"""
Saca la **forma** de cada caja azul del plano, no su rectángulo envolvente.

El plano tiene stands en L —62 y 109 son los claros: una banda ancha al
fondo con un retorno por la derecha—, y con el envolvente esos se comían
a sus vecinos: el hueco de la L contiene otros dos stands enteros.

Así que cada componente sale descompuesto en la lista de rectángulos cuya
unión es su forma, que es exactamente lo que `Stand.rectangulos` guarda
(§3.5 del modelo de datos). Un stand rectangular da un rectángulo y usa
`ancho_celdas`/`alto_celdas`; uno en L da dos.
"""

import json
import sys
from collections import defaultdict

AZUL = (21, 96, 158)
TOLERANCIA = 60


def leer_ppm(ruta):
    with open(ruta, "rb") as f:
        datos = f.read()
    campos, i = [], 2
    while len(campos) < 3:
        while datos[i : i + 1].isspace():
            i += 1
        if datos[i : i + 1] == b"#":
            while datos[i : i + 1] != b"\n":
                i += 1
            continue
        j = i
        while not datos[j : j + 1].isspace():
            j += 1
        campos.append(int(datos[i:j]))
        i = j
    return campos[0], campos[1], datos[i + 1 :]


def corridas(ancho, alto, pix):
    r, g, b = AZUL
    por_fila = []
    for y in range(alto):
        base = y * ancho * 3
        tramos, inicio = [], None
        for x in range(ancho):
            p = base + x * 3
            azul = (
                abs(pix[p] - r) < TOLERANCIA
                and abs(pix[p + 1] - g) < TOLERANCIA
                and abs(pix[p + 2] - b) < TOLERANCIA
            )
            if azul and inicio is None:
                inicio = x
            elif not azul and inicio is not None:
                tramos.append((inicio, x - 1))
                inicio = None
        if inicio is not None:
            tramos.append((inicio, ancho - 1))
        por_fila.append(tramos)
    return por_fila


def componentes(por_fila):
    padre = {}

    def raiz(a):
        while padre[a] != a:
            padre[a] = padre[padre[a]]
            a = padre[a]
        return a

    def unir(a, b):
        ra, rb = raiz(a), raiz(b)
        if ra != rb:
            padre[max(ra, rb)] = min(ra, rb)

    etiquetadas, previos, siguiente = [], [], 0
    for y, tramos in enumerate(por_fila):
        actuales = []
        for x0, x1 in tramos:
            mio = siguiente
            siguiente += 1
            padre[mio] = mio
            for px0, px1, pid in previos:
                if px0 <= x1 and x0 <= px1:
                    unir(mio, pid)
            actuales.append((x0, x1, mio))
        etiquetadas.append(actuales)
        previos = actuales

    # Componente → {y: [(x0, x1), ...]}
    por_comp = defaultdict(lambda: defaultdict(list))
    for y, actuales in enumerate(etiquetadas):
        for x0, x1, i in actuales:
            por_comp[raiz(i)][y].append((x0, x1))
    return por_comp


def rectangulos(filas_del_comp, tol=4):
    """Bandas de filas con la misma envolvente → un rectángulo por banda.

    Se toma **el mínimo y el máximo x de cada fila**, no sus tramos: eso
    rellena los huecos que deja el texto blanco de dentro de la caja, que
    de otro modo partía cada fila en cinco trozos y convertía un stand
    rectangular en veinte rectángulos.

    Rellenar por fila no borra la forma que sí importa. Las cajas
    irregulares de este plano (62, 109) son cóncavas **en vertical** —una
    banda ancha arriba y un pie estrecho abajo—, y eso son dos bandas con
    envolventes distintas, que es justo lo que se busca. Una caja con un
    agujero de verdad sí se perdería; en este plano no hay ninguna.
    """
    envolvente = {
        y: (min(a for a, _ in tr), max(b for _, b in tr))
        for y, tr in filas_del_comp.items()
    }
    bandas = []
    for y in sorted(envolvente):
        x0, x1 = envolvente[y]
        if bandas:
            _, by0, by1, bx0, bx1 = bandas[-1]
            if abs(x0 - bx0) <= tol and abs(x1 - bx1) <= tol and y - by1 <= 1:
                bandas[-1][2] = y
                continue
        bandas.append([None, y, y, x0, x1])

    # Una banda de pocos píxeles es el diente de sierra del antialias en
    # el borde de la caja, no un escalón de su forma.
    rects = [
        (x0, y0, x1 - x0 + 1, y1 - y0 + 1)
        for _, y0, y1, x0, x1 in bandas
        if y1 - y0 >= 5 and x1 - x0 >= 5
    ]
    return rects


def main(ruta, area_minima=800):
    ancho, alto, pix = leer_ppm(ruta)
    print(f"# imagen {ancho}x{alto}", file=sys.stderr)
    salida = []
    for comp, filas in componentes(corridas(ancho, alto, pix)).items():
        area = sum(x1 - x0 + 1 for tr in filas.values() for x0, x1 in tr)
        if area < area_minima:
            continue
        rects = rectangulos(filas)
        if not rects:
            continue
        x0 = min(r[0] for r in rects)
        y0 = min(r[1] for r in rects)
        salida.append({"x": x0, "y": y0, "area": area, "rects": rects})
    salida.sort(key=lambda c: (c["y"], c["x"]))
    print(f"# {len(salida)} componentes", file=sys.stderr)
    print(
        f"# irregulares (más de un rectángulo): "
        f"{sum(1 for c in salida if len(c['rects']) > 1)}",
        file=sys.stderr,
    )
    json.dump(salida, sys.stdout, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
