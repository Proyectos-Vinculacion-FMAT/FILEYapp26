"""
Dónde cae un archivo subido (`comun/almacenamiento.py`, `ADR-0007`).

Lo que se prueba aquí es difícil de arreglar más tarde: ``upload_to``
viaja dentro de las migraciones, y para cuando se note que la ruta
estaba mal habrá archivos guardados con ella. Cuatro cosas:

1. **El schema de la feria va por delante.** Sin eso, `ADR-0003` aísla
   la base y no el disco: las actas de 2027 y las de 2028 caerían en la
   misma carpeta.
2. **El nombre original no se conserva.** ``RFC_JUAN_PEREZ.pdf`` dice
   quién es antes de abrirlo, y además es adivinable.
3. **Es serializable.** Si no lo fuera, `makemigrations` reventaría el
   día que el primer `FileField` lo use, que será en la fase 2.
4. **Dos instancias iguales son iguales.** Sin ``__eq__``,
   `makemigrations` generaría un `AlterField` en cada ejecución.
"""

import pytest
from django.db import connection
from django_tenants.utils import schema_context

from ..almacenamiento import CarpetaDeLaFeria


def test_la_ruta_empieza_por_el_schema_de_la_feria(db, feria_2027):
    destino = CarpetaDeLaFeria("solicitudes")

    with schema_context(feria_2027.schema_name):
        ruta = destino(None, "acta.pdf")

    assert ruta.startswith("feria_2027/solicitudes/")


def test_cada_feria_guarda_en_su_propia_carpeta(db, feria_2027, feria_2028):
    """El aislamiento de `ADR-0003` tiene que llegar también al disco."""
    destino = CarpetaDeLaFeria("solicitudes")

    with schema_context(feria_2027.schema_name):
        en_2027 = destino(None, "acta.pdf")
    with schema_context(feria_2028.schema_name):
        en_2028 = destino(None, "acta.pdf")

    assert en_2027.split("/")[0] != en_2028.split("/")[0]


def test_el_nombre_original_no_sobrevive(db, feria_2027):
    """Trae datos personales y es adivinable."""
    destino = CarpetaDeLaFeria("documentos")

    with schema_context(feria_2027.schema_name):
        ruta = destino(None, "RFC_JUAN_PEREZ_2019.pdf")

    assert "JUAN" not in ruta.upper()
    assert ruta.endswith(".pdf")


def test_dos_archivos_con_el_mismo_nombre_no_chocan(db, feria_2027):
    destino = CarpetaDeLaFeria("documentos")

    with schema_context(feria_2027.schema_name):
        assert destino(None, "acta.pdf") != destino(None, "acta.pdf")


@pytest.mark.parametrize(
    "original, esperado",
    [
        ("acta.PDF", ".pdf"),
        ("comprobante.jpeg", ".jpeg"),
        ("sin_extension", ""),
        ("", ""),
        # Una extensión absurdamente larga se descarta en vez de
        # alargar la ruta: el nombre lo elige quien sube el archivo.
        ("acta." + "a" * 300, ""),
    ],
)
def test_la_extension_se_normaliza(db, feria_2027, original, esperado):
    destino = CarpetaDeLaFeria("documentos")

    with schema_context(feria_2027.schema_name):
        ruta = destino(None, original)

    assert ruta.endswith(esperado)
    if esperado:
        assert ruta.count(".") == 1


def test_es_serializable_en_una_migracion():
    """`upload_to` viaja dentro de las migraciones.

    Un cierre no se puede serializar, y por eso esto es una clase con
    `@deconstructible` y no una función que devuelve otra función. Si
    esta prueba falla, `makemigrations` revienta en cuanto exista el
    primer `FileField` del proyecto.
    """
    ruta, args, kwargs = CarpetaDeLaFeria("comprobantes").deconstruct()

    assert ruta == "comun.almacenamiento.CarpetaDeLaFeria"
    assert args == ("comprobantes",)
    assert kwargs == {}


def test_dos_rutas_iguales_son_iguales():
    """Sin esto, `makemigrations` generaría un `AlterField` cada vez."""
    assert CarpetaDeLaFeria("documentos") == CarpetaDeLaFeria("documentos")
    assert CarpetaDeLaFeria("documentos") != CarpetaDeLaFeria("comprobantes")


def test_fuera_de_una_feria_cae_en_public():
    """No es un uso previsto, pero tiene que dar algo y no reventar.

    Un archivo subido desde `public` no pertenece a ninguna edición. Que
    caiga bajo `public/` es preferible a que caiga junto a los de una
    feria cualquiera.
    """
    connection.set_schema_to_public()

    assert CarpetaDeLaFeria("x")(None, "a.pdf").startswith("public/")
