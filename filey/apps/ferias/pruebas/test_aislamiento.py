"""
Aislamiento por schema — el riesgo principal que ADR-0003 acepta.

El ADR lo dice sin rodeos: si el `search_path` se queda apuntando a la
feria equivocada, **se sirven datos cruzados sin ningún error visible**.
No hay excepción, no hay log, no hay 500: una consulta devuelve de más y
parece correcta.

Por eso estas pruebas no comprueban que "el aislamiento funciona" en
abstracto, sino los tres caminos concretos por los que se rompería:

1. Una consulta sin filtro desde otra feria.
2. Dos peticiones seguidas sobre la **misma conexión** reutilizada.
3. Un hilo que no nace de una petición HTTP (hoy existe uno: el envío
   del OTP).
"""

import threading

import pytest
from django.db import connection, connections
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria, TipoConvocatoria

pytestmark = pytest.mark.django_db


def _crear_convocatoria(nombre, tipo=TipoConvocatoria.STD):
    return Convocatoria.objects.create(
        tipo=tipo, nombre=nombre, estado=Convocatoria.Estado.ABIERTA
    )


# ── 1. La consulta sin filtro ─────────────────────────────────


def test_una_feria_no_ve_las_convocatorias_de_otra(feria_2027, feria_2028):
    """La consulta **no lleva `WHERE feria_id`**, y aun así no cruza.

    Es exactamente lo que compra ADR-0003: el aislamiento no depende de
    que quien escriba la consulta se acuerde de filtrar.
    """
    with schema_context(feria_2027.schema_name):
        _crear_convocatoria("Stands 2027")
        _crear_convocatoria("Eventos 2027", TipoConvocatoria.EVT)
        assert Convocatoria.objects.count() == 2

    with schema_context(feria_2028.schema_name):
        assert Convocatoria.objects.count() == 0


def test_dos_ferias_pueden_tener_convocatorias_con_el_mismo_nombre(
    feria_2027, feria_2028
):
    """No compiten por unicidad: son tablas distintas, no filas distintas."""
    for feria in (feria_2027, feria_2028):
        with schema_context(feria.schema_name):
            _crear_convocatoria("Convocatoria de Stands")

    for feria in (feria_2027, feria_2028):
        with schema_context(feria.schema_name):
            assert Convocatoria.objects.count() == 1


def test_el_schema_de_contenido_no_tiene_las_tablas_globales(feria_2027):
    """`Persona` y `Feria` viven en `public`, una sola vez.

    Si aparecieran dentro del schema de una feria, cada edición tendría
    su propia copia de las cuentas — y el correo dejaría de ser único en
    todo el sistema, que es lo que ADR-0003 promete no romper.
    """
    with connection.cursor() as cur:
        cur.execute(
            "select tablename from pg_tables where schemaname = %s",
            [feria_2027.schema_name],
        )
        tablas = {fila[0] for fila in cur.fetchall()}

    assert "convocatorias_convocatoria" in tablas
    assert not {t for t in tablas if t.startswith("registros_")}
    assert not {t for t in tablas if t.startswith("ferias_")}


# ── 2. La conexión reutilizada ────────────────────────────────


def test_el_schema_no_se_filtra_entre_peticiones(client, feria_2027, feria_2028):
    """Dos peticiones seguidas sobre la misma conexión, a ferias distintas.

    Es el fallo que el ADR nombra como el más caro: una conexión que se
    queda apuntando a la feria anterior. `TenantSubfolderMiddleware` lo
    evita empezando **cada** petición con `set_schema_to_public()`.
    """
    with schema_context(feria_2027.schema_name):
        _crear_convocatoria("Solo en 2027")

    cuerpo_2027 = client.get(feria_2027.url).content.decode()
    assert "Solo en 2027" in cuerpo_2027

    cuerpo_2028 = client.get(feria_2028.url).content.decode()
    assert "Solo en 2027" not in cuerpo_2028
    assert "Todavía no hay convocatorias" in cuerpo_2028

    # Y de vuelta: no es que la segunda petición "apague" la primera.
    assert "Solo en 2027" in client.get(feria_2027.url).content.decode()


def test_una_ruta_publica_no_arrastra_el_schema_de_la_feria_anterior(
    client, feria_2027
):
    """Tras entrar a una feria, `/acceso/` tiene que volver a `public`."""
    client.get(feria_2027.url)

    respuesta = client.get("/acceso/")

    assert respuesta.status_code == 200
    assert connection.schema_name == "public"


def test_un_slug_inexistente_da_404_y_no_datos_de_otra_feria(client, feria_2027):
    assert client.get("/f/2099/").status_code == 404


# ── 3. El hilo que no nace de una petición ────────────────────


def test_un_hilo_de_fondo_no_hereda_el_schema_de_una_feria(feria_2027):
    """El envío del OTP corre en su propio hilo (`services/otp.py`).

    Un hilo abre su propia conexión, y esa conexión nace en `public`. Si
    heredara el `search_path` de la feria en curso, el OTP se guardaría
    o se buscaría en el schema equivocado — y como `SesionOTP` vive en
    `public`, ni siquiera existiría la tabla ahí.
    """
    visto = {}

    def _mirar():
        try:
            visto["schema"] = connections["default"].schema_name
        finally:
            connections.close_all()

    with schema_context(feria_2027.schema_name):
        assert connection.schema_name == feria_2027.schema_name
        hilo = threading.Thread(target=_mirar)
        hilo.start()
        hilo.join()

    assert visto["schema"] == "public"
