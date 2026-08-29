"""
Pasa las formas medidas en píxeles a una retícula de un metro.

Dentro de un islote el dibujo es exacto: el paso es 54 px por los 3 m de
ancho del stand tipo y 36 px por sus 2 m de fondo. **Entre islotes no**:
el plano se dibujó en Photoshop y los pasillos miden lo que se vio bien.

Por eso se ajusta en dos tiempos: la geometría interna de cada islote se
conserva tal cual, y solo el origen del islote se redondea al metro. El
error se va al pasillo, que es donde no importa — el ancho de un pasillo
es una decisión, no una medida.
"""

import json
import sys
from collections import defaultdict

ESCALA = 18.05  # px por metro a 300 dpi, del paso del stand tipo (54 px / 3 m)
CERCA = 14  # px: dos formas más cerca que esto son del mismo islote


def envolvente(forma):
    r = forma["rects"]
    x0 = min(a for a, _, _, _ in r)
    y0 = min(b for _, b, _, _ in r)
    x1 = max(a + w for a, _, w, _ in r)
    y1 = max(b + h for _, b, _, h in r)
    return x0, y0, x1, y1


def islotes(formas):
    padre = list(range(len(formas)))

    def raiz(a):
        while padre[a] != a:
            padre[a] = padre[padre[a]]
            a = padre[a]
        return a

    cajas = [envolvente(f) for f in formas]
    for i, (ax0, ay0, ax1, ay1) in enumerate(cajas):
        for j in range(i + 1, len(cajas)):
            bx0, by0, bx1, by1 = cajas[j]
            if max(ax0 - bx1, bx0 - ax1, 0) <= CERCA and (
                max(ay0 - by1, by0 - ay1, 0) <= CERCA
            ):
                ra, rb = raiz(i), raiz(j)
                if ra != rb:
                    padre[max(ra, rb)] = min(ra, rb)

    grupos = defaultdict(list)
    for i in range(len(formas)):
        grupos[raiz(i)].append(i)
    return list(grupos.values())


def convertir(formas):
    ox = min(envolvente(f)[0] for f in formas)
    oy = min(envolvente(f)[1] for f in formas)

    salida = []
    for n, grupo in enumerate(islotes(formas)):
        gx = min(envolvente(formas[i])[0] for i in grupo)
        gy = min(envolvente(formas[i])[1] for i in grupo)
        base_col = round((gx - ox) / ESCALA)
        base_fila = round((gy - oy) / ESCALA)
        for i in grupo:
            rects = [
                {
                    "col": base_col + round((x - gx) / ESCALA),
                    "fila": base_fila + round((y - gy) / ESCALA),
                    "ancho_celdas": max(1, round(w / ESCALA)),
                    "alto_celdas": max(1, round(h / ESCALA)),
                }
                for x, y, w, h in formas[i]["rects"]
            ]
            salida.append({"islote": n, "rects": rects, "px": formas[i]["rects"][0]})
    salida.sort(key=lambda c: (c["rects"][0]["fila"], c["rects"][0]["col"]))
    return salida


def solapan(a, b):
    for ra in a["rects"]:
        for rb in b["rects"]:
            if (
                ra["col"] < rb["col"] + rb["ancho_celdas"]
                and rb["col"] < ra["col"] + ra["ancho_celdas"]
                and ra["fila"] < rb["fila"] + rb["alto_celdas"]
                and rb["fila"] < ra["fila"] + ra["alto_celdas"]
            ):
                return True
    return False


if __name__ == "__main__":
    celdas = convertir(json.load(open(sys.argv[1])))
    choques = [
        (a["px"], b["px"])
        for i, a in enumerate(celdas)
        for b in celdas[i + 1 :]
        if solapan(a, b)
    ]
    cols = max(r["col"] + r["ancho_celdas"] for c in celdas for r in c["rects"])
    fils = max(r["fila"] + r["alto_celdas"] for c in celdas for r in c["rects"])
    print(
        f"# {len(celdas)} formas en {len(set(c['islote'] for c in celdas))} islotes; "
        f"retícula {cols} x {fils} m; {len(choques)} solapes",
        file=sys.stderr,
    )
    for a, b in choques[:10]:
        print(f"#   {a} ∩ {b}", file=sys.stderr)
    json.dump(celdas, sys.stdout, ensure_ascii=False, indent=1)
