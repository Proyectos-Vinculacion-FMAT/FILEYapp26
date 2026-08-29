"""
Importar el showfloor de una convocatoria (`CU-STD-039`).

Lo que se defiende aquí es que **un archivo malo no deje un mapa a
medias**. Un mapa importado a medias es peor que no importarlo: se ve
igual que uno bueno, y le faltan espacios que nadie echa de menos hasta
que alguien pregunta por el suyo.

La prueba grande usa el mapa real de 2026 —151 espacios derivados del
plano en papel—, no uno de juguete. Un mapa de tres cajas no habría
encontrado nunca el caso que de verdad importa: los tres stands en L,
cuyo hueco está ocupado por sus vecinos y que un detector de solapes por
rectángulo envolvente rechazaría estando bien.
"""

import json
from decimal import Decimal
from pathlib import Path

import pytest
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.ferias.models import Feria

from ..models import DecoracionMapa, MapaShowfloor, Stand
from ..servicios import mapas
from . import fabricas

pytestmark = pytest.mark.django_db

MAPA_2026 = Path(__file__).resolve().parents[1] / "mapas" / "filey-2026.json"


@pytest.fixture(scope="module")
def archivo_2026():
    return json.loads(MAPA_2026.read_text(encoding="utf-8"))


def _minimo(**cambios):
    """El archivo más pequeño que se puede importar."""
    datos = {
        "formato": "filey-mapa/1",
        "mapa": {
            "salon": "Salón de pruebas",
            "columnas": 20,
            "filas": 10,
            "metros_por_celda": 1.0,
            "tamano_celda": 12,
        },
        "stands": [
            {"clave": "A1", "etiqueta": "A1", "col": 0, "fila": 0,
             "ancho_celdas": 3, "alto_celdas": 2},
            {"clave": "A2", "etiqueta": "A2", "col": 3, "fila": 0,
             "ancho_celdas": 3, "alto_celdas": 2},
        ],
        "decoraciones": [
            {"tipo": "rectangulo", "etiqueta": "Acceso", "col": 0, "fila": 8,
             "ancho_celdas": 4, "alto_celdas": 2},
        ],
    }
    datos.update(cambios)
    return datos


# ── El mapa real ──────────────────────────────────────────────


def test_el_mapa_de_2026_entra_entero(feria_2027, archivo_2026):
    """151 espacios, tres de ellos en L, y ninguno se pisa."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()

        resumen = mapas.importar(convocatoria=conv, datos=archivo_2026)

        assert resumen.stands == 151
        assert resumen.decoraciones == 10
        assert resumen.metros_cuadrados == Decimal("2628")
        assert not resumen.reemplazo
        assert Stand.objects.count() == 151


def test_los_tres_en_l_conservan_su_forma(feria_2027, archivo_2026):
    """Y no su envolvente, que se llevaría el espacio de los vecinos."""
    with schema_context(feria_2027.schema_name):
        mapas.importar(convocatoria=fabricas.convocatoria(), datos=archivo_2026)

        irregulares = Stand.objects.filter(rectangulos__isnull=False)
        assert {s.clave for s in irregulares} == {"62", "97", "109"}

        en_l = Stand.objects.get(clave="62")
        assert en_l.ancho_celdas is None and en_l.alto_celdas is None
        # 36 m² de forma, contra los 48 que daría su envolvente de 12×4.
        assert en_l.metros_cuadrados == Decimal("36")


def test_la_superficie_da_el_precio_de_la_convocatoria(feria_2027, archivo_2026):
    """`RN-01`: el básico de 3×2 a 2 500 el metro son los 15 000."""
    with schema_context(feria_2027.schema_name):
        mapas.importar(convocatoria=fabricas.convocatoria(), datos=archivo_2026)

        basico = Stand.objects.filter(ancho_celdas=3, alto_celdas=2).first()

        assert basico.metros_cuadrados == Decimal("6")
        assert basico.precio(Decimal("2500")) == Decimal("15000")


# ── Lo que se ignora del archivo a propósito ──────────────────


def test_un_stand_nace_disponible_diga_lo_que_diga_el_archivo():
    """`RN-10`. Importar el estado dejaría escrito que algo está
    reservado sin que exista la reserva que lo respalda."""
    datos = _minimo()
    datos["stands"][0]["estado"] = "ocupado"

    limpios = mapas._validar_stands(datos["stands"], datos["mapa"])

    assert all(s["estado"] == Stand.Estado.DISPONIBLE for s in limpios)


def test_el_precio_del_archivo_no_se_guarda():
    """Se deriva de la superficie y del `costo_m2` (`RN-01`)."""
    datos = _minimo()
    datos["stands"][0]["precio"] = 999

    limpios = mapas._validar_stands(datos["stands"], datos["mapa"])

    assert "precio" not in limpios[0]


def test_el_ocupante_de_2026_no_llega_a_la_base(feria_2027, archivo_2026):
    """Es quién estuvo, no quién está."""
    with schema_context(feria_2027.schema_name):
        mapas.importar(convocatoria=fabricas.convocatoria(), datos=archivo_2026)

        planeta = Stand.objects.get(clave="68")

        assert planeta.estado == Stand.Estado.DISPONIBLE
        assert "Planeta" not in planeta.etiqueta


# ── E2 · el archivo no cumple, y no se escribe nada ───────────


@pytest.mark.parametrize(
    "romper, mensaje",
    [
        (lambda d: d.pop("formato"), "sin declarar"),
        (lambda d: d.update(formato="otra-cosa/9"), "otra-cosa/9"),
        (lambda d: d.pop("mapa"), "retícula"),
        (lambda d: d["mapa"].update(salon=""), "salón"),
        (lambda d: d["mapa"].update(columnas=0), "entero"),
        (lambda d: d["mapa"].update(metros_por_celda=0), "mayor que cero"),
        (lambda d: d.update(stands=[]), "ningún espacio"),
        (lambda d: d["stands"][1].update(clave=""), "no tiene clave"),
        (lambda d: d["stands"][1].update(clave="A1"), "dos veces"),
        (lambda d: d["stands"][1].update(col=19), "se sale"),
        (lambda d: d["stands"][1].update(col=0), "se pisan"),
        (lambda d: d["stands"][1].update(ancho_celdas=0), "entero"),
        (lambda d: d["stands"][1].update(rectangulos=[]), "vacío"),
        (lambda d: d["decoraciones"][0].update(etiqueta=""), "rótulo"),
        (lambda d: d["decoraciones"][0].update(tipo="circulo"), "desconocido"),
        (lambda d: d["decoraciones"][0].update(fila=9), "se sale"),
    ],
)
def test_un_archivo_malo_se_rechaza_diciendo_donde(feria_2027, romper, mensaje):
    datos = _minimo()
    romper(datos)

    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        with pytest.raises(mapas.ImportacionRechazada, match=mensaje):
            mapas.importar(convocatoria=conv, datos=datos)

        # Lo importante: no quedó nada a medias.
        assert not MapaShowfloor.objects.exists()
        assert not Stand.objects.exists()


def test_los_stands_en_l_no_se_toman_por_solapes(feria_2027):
    """El hueco de una L lo ocupa su vecino, y eso es correcto.

    Con detección por rectángulo envolvente esta importación fallaría
    estando bien, que es exactamente lo que le pasa al mapa de 2026.
    """
    datos = _minimo()
    datos["stands"] = [
        {
            "clave": "L",
            "etiqueta": "L",
            "rectangulos": [
                {"col": 0, "fila": 0, "ancho_celdas": 12, "alto_celdas": 2},
                {"col": 6, "fila": 2, "ancho_celdas": 6, "alto_celdas": 2},
            ],
        },
        # Justo en el hueco de la L.
        {"clave": "dentro", "etiqueta": "dentro", "col": 0, "fila": 2,
         "ancho_celdas": 6, "alto_celdas": 2},
    ]

    with schema_context(feria_2027.schema_name):
        resumen = mapas.importar(convocatoria=fabricas.convocatoria(), datos=datos)

        assert resumen.stands == 2


# ── A1 y E1 · reemplazar un mapa que ya existe ────────────────


def test_reemplazar_un_mapa_pide_confirmacion(feria_2027):
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_minimo())

        with pytest.raises(mapas.ImportacionRechazada, match="confirmarlo"):
            mapas.importar(convocatoria=conv, datos=_minimo())

        assert Stand.objects.count() == 2


def test_confirmado_el_mapa_anterior_se_reemplaza_entero(feria_2027):
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_minimo())

        otro = _minimo()
        otro["stands"] = [
            {"clave": "Z9", "etiqueta": "Z9", "col": 0, "fila": 0,
             "ancho_celdas": 3, "alto_celdas": 2}
        ]
        resumen = mapas.importar(convocatoria=conv, datos=otro, confirmado=True)

        assert resumen.reemplazo
        assert [s.clave for s in Stand.objects.all()] == ["Z9"]
        assert MapaShowfloor.objects.count() == 1


def test_no_se_reemplaza_un_mapa_con_espacios_tomados(feria_2027):
    """`E1`: borrarlos dejaría una reserva apuntando a la nada.

    Y **no hay confirmación que lo permita**, al revés que el reemplazo
    normal: detrás de un stand reservado hay dinero abonado.
    """
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_minimo())
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.RESERVADO)

        with pytest.raises(mapas.HayStandsReservados, match="A1"):
            mapas.importar(convocatoria=conv, datos=_minimo(), confirmado=True)

        assert Stand.objects.count() == 2


# ── E3 y la convocatoria equivocada ───────────────────────────


def test_una_edicion_archivada_no_recibe_mapas(feria_2027):
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        feria_2027.estado = Feria.Estado.ARCHIVADA
        feria_2027.save(update_fields=["estado"])

        with pytest.raises(mapas.ImportacionRechazada, match="archivada"):
            mapas.importar(convocatoria=conv, datos=_minimo())


def test_una_convocatoria_de_eventos_no_tiene_showfloor(feria_2027):
    with schema_context(feria_2027.schema_name):
        eventos = Convocatoria.objects.create(
            tipo=TipoConvocatoria.EVT,
            nombre="Actividades",
            estado=Convocatoria.Estado.ABIERTA,
        )

        with pytest.raises(mapas.ImportacionRechazada, match="de stands"):
            mapas.importar(convocatoria=eventos, datos=_minimo())


# ── El mapa vive en su feria y en ninguna otra ────────────────


def test_el_mapa_de_una_feria_no_se_ve_desde_otra(feria_2027, feria_2028):
    """`ADR-0003`: la edición es el schema, no una columna."""
    with schema_context(feria_2027.schema_name):
        mapas.importar(convocatoria=fabricas.convocatoria(), datos=_minimo())
        assert Stand.objects.count() == 2

    with schema_context(feria_2028.schema_name):
        assert not Stand.objects.exists()
        assert not MapaShowfloor.objects.exists()


def test_sin_mapa_no_es_un_error(feria_2027):
    """`CU-STD-009` E2: es una convocatoria recién creada, no una avería."""
    with schema_context(feria_2027.schema_name):
        assert mapas.mapa_de(fabricas.convocatoria()) is None


# ── Las invariantes que sostiene la base ──────────────────────


def test_la_base_no_admite_un_stand_sin_forma(feria_2027):
    """Mediría cero metros y se cobraría a cero (`RN-01`)."""
    from django.db.utils import IntegrityError

    with schema_context(feria_2027.schema_name):
        mapas.importar(convocatoria=fabricas.convocatoria(), datos=_minimo())
        mapa = MapaShowfloor.objects.get()

        with pytest.raises(IntegrityError):
            Stand.objects.create(
                mapa=mapa, clave="X", etiqueta="X", col=0, fila=5,
                ancho_celdas=None, alto_celdas=None, rectangulos=None,
            )


def test_la_base_no_admite_dos_stands_con_la_misma_clave(feria_2027):
    from django.db.utils import IntegrityError

    with schema_context(feria_2027.schema_name):
        mapas.importar(convocatoria=fabricas.convocatoria(), datos=_minimo())
        mapa = MapaShowfloor.objects.get()

        with pytest.raises(IntegrityError):
            Stand.objects.create(
                mapa=mapa, clave="A1", etiqueta="otro", col=0, fila=5,
                ancho_celdas=3, alto_celdas=2,
            )


def test_una_decoracion_de_texto_no_lleva_medidas(feria_2027):
    from django.db.utils import IntegrityError

    with schema_context(feria_2027.schema_name):
        mapas.importar(convocatoria=fabricas.convocatoria(), datos=_minimo())
        mapa = MapaShowfloor.objects.get()

        with pytest.raises(IntegrityError):
            DecoracionMapa.objects.create(
                mapa=mapa, tipo=DecoracionMapa.Tipo.TEXTO, etiqueta="Norte",
                col=0, fila=0, ancho_celdas=3, alto_celdas=1,
            )


# ── La pantalla del admin de la edición ───────────────────────
#
# `CU-STD-039` la pone en `/f/<slug>/django-admin/`, y con eso hereda la
# trampa de los dos sitios de admin: `MapaShowfloor` es de `TENANT_APPS`,
# así que registrarla en el admin de siempre no falla al arrancar y
# revienta con `relation "..." does not exist` la primera vez que alguien
# la abre.


def test_solo_el_operador_importa_un_mapa(client, feria_2027):
    """`is_staff` abre este admin entero, y con eso no basta.

    Importar reemplaza el showfloor de una convocatoria: es una operación
    de montaje, no de operación diaria, y hasta que exista un editor con
    vista previa el sitio correcto es la herramienta del equipo técnico
    (`ADR-0005`).
    """
    from apps.registros.models import Persona

    del_equipo = Persona.objects.create_user(
        correo="becario@filey.org", nombre="Beto", primer_apellido="Chan"
    )
    del_equipo.is_staff = True
    del_equipo.save(update_fields=["is_staff"])
    client.force_login(del_equipo)

    respuesta = client.get(
        f"{feria_2027.url}django-admin/stands/mapashowfloor/importar/"
    )

    assert respuesta.status_code == 403


def test_el_operador_importa_desde_el_admin(client, feria_2027):
    from django.core.files.uploadedfile import SimpleUploadedFile

    from apps.registros.models import Persona

    operador = Persona.objects.create_superuser(correo="raiz@filey.org", password="x")
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
    client.force_login(operador)

    respuesta = client.post(
        f"{feria_2027.url}django-admin/stands/mapashowfloor/importar/",
        {
            "convocatoria": conv.pk,
            "archivo": SimpleUploadedFile(
                "mapa.json", json.dumps(_minimo()).encode("utf-8")
            ),
        },
        follow=True,
    )

    assert respuesta.status_code == 200
    with schema_context(feria_2027.schema_name):
        assert Stand.objects.count() == 2


def test_un_archivo_que_no_es_json_lo_dice_en_el_formulario(client, feria_2027):
    """Y no como un 500: es lo que pasa al subir el PDF por error."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    from apps.registros.models import Persona

    operador = Persona.objects.create_superuser(correo="raiz@filey.org", password="x")
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
    client.force_login(operador)

    respuesta = client.post(
        f"{feria_2027.url}django-admin/stands/mapashowfloor/importar/",
        {
            "convocatoria": conv.pk,
            "archivo": SimpleUploadedFile("plano.pdf", b"%PDF-1.4 no soy json"),
        },
    )

    assert respuesta.status_code == 200
    assert "No es JSON válido" in respuesta.content.decode()
    with schema_context(feria_2027.schema_name):
        assert not Stand.objects.exists()


def test_el_error_del_servicio_llega_al_formulario(client, feria_2027):
    """Con lo capturado intacto, no como un mensaje suelto tras un salto."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    from apps.registros.models import Persona

    operador = Persona.objects.create_superuser(correo="raiz@filey.org", password="x")
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_minimo())
    client.force_login(operador)

    respuesta = client.post(
        f"{feria_2027.url}django-admin/stands/mapashowfloor/importar/",
        {
            "convocatoria": conv.pk,
            "archivo": SimpleUploadedFile(
                "mapa.json", json.dumps(_minimo()).encode("utf-8")
            ),
        },
    )

    assert "confirmarlo" in respuesta.content.decode()


def test_el_mapa_se_registra_en_el_admin_de_la_edicion():
    """La regla mecánica de `CLAUDE.md`, que no falla al arrancar.

    `apps.stands` es de `TENANT_APPS`: sus tablas viven en el schema de
    cada feria y en ninguna parte de `public`. Registrarlas en
    `admin.site` pasa el `check` y revienta con `relation "..." does not
    exist` la primera vez que alguien abre la pantalla.
    """
    from django.contrib import admin as admin_de_django

    from comun.admin_feria import admin_feria

    from ..models import DecoracionMapa, MapaShowfloor

    for modelo in (MapaShowfloor, Stand, DecoracionMapa):
        assert modelo in admin_feria._registry, modelo.__name__
        assert modelo not in admin_de_django.site._registry, modelo.__name__
