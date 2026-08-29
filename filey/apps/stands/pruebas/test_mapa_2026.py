"""
El mapa de FILEY 2026, derivado del plano en papel.

`apps/stands/mapas/filey-2026.json` es la entrada de `CU-STD-039` y el
mapa con el que se va a construir y probar toda la fase de reserva. Sale
de medir un PDF de Photoshop (ver `scripts/derivar-mapa/README.md`), así
que **no es un dato escrito a mano que alguien revisó**: es el resultado
de un proceso, y lo que se comprueba aquí es que ese resultado siga
siendo consistente.

Ninguna de estas pruebas toca la base. Miran el archivo, porque los tres
errores que un mapa mal derivado comete —dos espacios pisándose, una
clave repetida, un número que se perdió— no dan síntoma hasta que alguien
reserva un stand y descubre que ya era de otro.

.. note:: El archivo está en el formato del componente de mapa

   `grid` / `stands` / `decorations`, con las claves en inglés, que es
   lo que `event-stand-map` lee y lo que su editor produce en `saveMap`
   (`ADR-0008`). Es la única parte del sistema donde las claves no van en
   español, y es a propósito: traducirlas obligaría a hacerlo en los dos
   sentidos justo en el camino donde un error enseña a un aplicante quién
   reservó qué.

.. warning:: Lo que estas pruebas **no** pueden comprobar

   Que el número de cada caja sea el que dice el plano. Eso se leyó
   mirando, y contrastarlo pide el PDF al lado. Lo que sí se defiende es
   que la numeración esté completa y sin repetir, que es donde un error
   de lectura se delata solo.
"""

import json
from pathlib import Path

import pytest

MAPA = Path(__file__).resolve().parents[1] / "mapas" / "filey-2026.json"

#: Lo que mide el espacio tipo del plano, en metros. Es el ancla de toda
#: la derivación: sale del precio que dio el cliente —15 000 el básico,
#: a 2 500 el metro— y con él la escala hace que todas las cajas caigan
#: en múltiplos enteros de metro.
BASICO = (3, 2)


@pytest.fixture(scope="module")
def mapa():
    return json.loads(MAPA.read_text(encoding="utf-8"))


def _rects(espacio):
    """Los rectángulos de una forma, sea simple o irregular.

    Las claves son las de `event-stand-map/docs/bridge_protocol.md`
    —`col`/`row`/`w`/`h`— porque el archivo se escribe en el formato que
    ese componente lee y que su editor produce (`ADR-0008`).
    """
    return espacio.get("rects") or [espacio]


def _celdas(espacio):
    return {
        (c, f)
        for r in _rects(espacio)
        for c in range(r["col"], r["col"] + r["w"])
        for f in range(r["row"], r["row"] + r["h"])
    }


def _superficie(espacio):
    return sum(r["w"] * r["h"] for r in _rects(espacio))


# ── Que no haya dos espacios en el mismo sitio ────────────────


def test_ningun_stand_pisa_a_otro(mapa):
    """El error que no da síntoma hasta que dos editoriales reservan.

    Se comprueba celda a celda y no por rectángulo envolvente: los tres
    stands en L (62, 97, 109) tienen el hueco de la L ocupado por sus
    vecinos, así que con envolventes esta prueba fallaría estando bien.
    """
    ocupadas = {}
    for stand in mapa["stands"]:
        for celda in _celdas(stand):
            otro = ocupadas.get(celda)
            assert otro is None, (
                f"los stands {otro} y {stand['id']} se pisan en {celda}"
            )
            ocupadas[celda] = stand["id"]


def test_ningun_stand_se_sale_de_la_reticula(mapa):
    cols, filas = mapa["grid"]["cols"], mapa["grid"]["rows"]
    for espacio in mapa["stands"] + mapa["decorations"]:
        for r in _rects(espacio):
            assert 0 <= r["col"] and r["col"] + r["w"] <= cols
            assert 0 <= r["row"] and r["row"] + r["h"] <= filas


def test_las_decoraciones_no_pisan_a_los_stands(mapa):
    """Una sala de la feria encima de un espacio vendible es un mapa roto."""
    de_stands = {c for s in mapa["stands"] for c in _celdas(s)}
    for deco in mapa["decorations"]:
        choque = _celdas(deco) & de_stands
        assert not choque, f"«{deco['label']}» pisa un stand en {sorted(choque)[:3]}"


# ── Que la numeración esté entera ─────────────────────────────


def test_ninguna_clave_se_repite(mapa):
    claves = [s["id"] for s in mapa["stands"]]
    assert len(claves) == len(set(claves))


def test_estan_los_141_numeros_del_plano(mapa):
    """El plano numera del 1 al 141 sin huecos; si falta uno, se leyó mal."""
    numeros = {
        int("".join(c for c in s["id"] if c.isdigit())) for s in mapa["stands"]
    }

    assert numeros == set(range(1, 142))


def test_las_variantes_con_letra_son_las_del_plano(mapa):
    """Diez espacios se subdividieron y llevan letra."""
    con_letra = sorted(s["id"] for s in mapa["stands"] if not s["id"].isdigit())

    assert con_letra == [
        "1A", "1B", "24A", "24B", "25A", "25B", "2A", "46A", "54A", "55A",
    ]


# ── Que la escala sea la que se dijo ──────────────────────────


def test_el_espacio_tipo_es_el_basico_de_la_convocatoria(mapa):
    """3 × 2 m, que a 2 500 el metro son los 15 000 del básico.

    Es la medida de la que cuelga toda la derivación. Si dejara de ser la
    más repetida, la escala se movió y **todos** los precios cambiaron.
    """
    ancho, alto = BASICO
    basicos = [s for s in mapa["stands"] if s.get("w") == ancho and s.get("h") == alto]

    assert len(basicos) > len(mapa["stands"]) / 3, "el 3×2 ya no es el espacio tipo"
    assert _superficie(basicos[0]) == 6


def test_todos_los_lados_son_metros_enteros(mapa):
    """Con `metros_por_celda = 1.0`, media celda no existe.

    Que las 161 formas del plano cayeran a la vez en metros enteros es lo
    que confirmó la escala; si una dejara de hacerlo, se derivó mal.
    """
    assert mapa["grid"]["meters_per_cell"] == 1.0
    for espacio in mapa["stands"] + mapa["decorations"]:
        for r in _rects(espacio):
            assert isinstance(r["w"], int) and r["w"] >= 1
            assert isinstance(r["h"], int) and r["h"] >= 1


def test_los_irregulares_declaran_su_forma_y_no_un_rectangulo(mapa):
    """El contrato: o el rectángulo simple, o `rects`. Nunca los dos.

    Sin esto, un stand en L pasaría por su envolvente y se cobraría el
    hueco de la L, que es de sus vecinos.
    """
    irregulares = [s for s in mapa["stands"] if s.get("rects")]

    assert {s["id"] for s in irregulares} == {"62", "97", "109"}
    for stand in irregulares:
        # El contrato es excluyente: o el rectángulo simple, o `rects`.
        assert "w" not in stand and "h" not in stand
        assert len(stand["rects"]) >= 2


# ── Que sirva para lo que viene ───────────────────────────────


def test_todo_espacio_nace_disponible(mapa):
    """Una convocatoria nueva no tiene nada reservado (`RN-10`).

    Los ocupantes de 2026 van aparte, en `ocupante_2026`, y no se
    importan: son quién estuvo, no quién está.
    """
    assert {s["status"] for s in mapa["stands"]} == {"disponible"}


def test_los_ocupantes_de_2026_no_se_confunden_con_el_estado(mapa):
    con_ocupante = [s for s in mapa["stands"] if "ocupante_2026" in s]

    assert len(con_ocupante) == 16
    assert all(s["status"] == "disponible" for s in con_ocupante)


def test_la_superficie_vendible_da_el_ingreso_esperado(mapa):
    """A 2 500 el m², el mapa entero son unos 6.5 millones.

    No es una regla de negocio: es una cifra de referencia. Si un cambio
    la mueve de golpe, algo se derivó distinto y hay que mirar por qué.
    """
    m2 = sum(_superficie(s) for s in mapa["stands"])

    assert m2 == 2628
    assert m2 * 2500 == 6_570_000
