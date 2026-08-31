"""
Transferir la propiedad de una feria.

Es la salida de una edición cuyo dueño abandona el proyecto: retirarle
el acceso no se puede (`CU-FER-004` E2, dejaría la feria sin nadie que
pueda administrarla), así que la única forma de sacarlo era pasarle
antes la feria a otra persona. Hoy la ejecuta el operador de la
plataforma desde `/django-admin/` (`ADR-0005`); el caso de uso del
propio dueño sigue pendiente.

Lo que se defiende aquí es el **paso intermedio**: entre soltar al dueño
anterior y marcar al nuevo, la feria está sin dueño —y con los dos
marcados violaría `un_solo_dueno_por_feria`—. Si eso no va en una
transacción, un fallo a media operación deja una edición que nadie puede
administrar.
"""

import pytest
from django.core import mail

from apps.registros.models import Persona

from ..models import AdminFeria
from ..servicios import accesos
from .fabricas import feria_sin_schema

pytestmark = pytest.mark.django_db


@pytest.fixture
def con_dueno():
    """Una feria y la persona que la tiene hoy."""
    feria = feria_sin_schema(nombre="FILEY 2027", slug="2027")
    ana = Persona.objects.create_user(correo="ana@filey.org", nombre="Ana")
    AdminFeria.objects.create(feria=feria, persona=ana, es_dueno=True)
    return feria, ana


def _dueno_de(feria) -> Persona | None:
    acceso = AdminFeria.objects.filter(feria=feria, es_dueno=True).first()
    return acceso.persona if acceso else None


# ── El traspaso ───────────────────────────────────────────────


def test_la_feria_cambia_de_dueno(con_dueno):
    feria, ana = con_dueno
    beto = Persona.objects.create_user(correo="beto@filey.org", nombre="Beto")

    resultado = accesos.transferir_propiedad(feria=feria, correo=beto.correo)

    assert _dueno_de(feria) == beto
    assert resultado.anterior == ana


def test_el_dueno_anterior_conserva_su_acceso(con_dueno):
    """No se le retira: quien montó la edición sigue conociéndola, y
    dejarlo fuera obligaría a darle acceso otra vez a continuación."""
    feria, ana = con_dueno
    Persona.objects.create_user(correo="beto@filey.org", nombre="Beto")

    accesos.transferir_propiedad(feria=feria, correo="beto@filey.org")

    anterior = AdminFeria.objects.get(feria=feria, persona=ana)
    assert anterior.es_dueno is False


def test_nunca_quedan_dos_duenos(con_dueno):
    """El invariante que la base sostiene con un índice único parcial."""
    feria, _ = con_dueno
    Persona.objects.create_user(correo="beto@filey.org", nombre="Beto")

    accesos.transferir_propiedad(feria=feria, correo="beto@filey.org")

    assert AdminFeria.objects.filter(feria=feria, es_dueno=True).count() == 1


def test_se_le_puede_pasar_a_quien_ya_administraba(con_dueno):
    """No se duplica su fila: se promueve la que ya tiene."""
    feria, _ = con_dueno
    beto = Persona.objects.create_user(correo="beto@filey.org", nombre="Beto")
    AdminFeria.objects.create(feria=feria, persona=beto, es_dueno=False)

    accesos.transferir_propiedad(feria=feria, correo=beto.correo)

    assert AdminFeria.objects.filter(feria=feria, persona=beto).count() == 1
    assert _dueno_de(feria) == beto


def test_se_le_puede_pasar_a_quien_no_tiene_cuenta(con_dueno):
    feria, _ = con_dueno

    resultado = accesos.transferir_propiedad(
        feria=feria, correo="nueva@filey.org", nombre="Nueva", primer_apellido="Cuenta"
    )

    assert resultado.cuenta_creada is True
    assert _dueno_de(feria).correo == "nueva@filey.org"


def test_pasarsela_a_quien_ya_la_tiene_no_cambia_nada(con_dueno):
    """Se devuelve tal cual en vez de rechazar: el resultado que pedían
    ya se cumple, y un error obligaría a la pantalla a distinguir un caso
    que no cambia nada."""
    feria, ana = con_dueno

    resultado = accesos.transferir_propiedad(feria=feria, correo=ana.correo)

    assert resultado.anterior == resultado.persona == ana
    assert AdminFeria.objects.filter(feria=feria).count() == 1


def test_sin_correo_no_se_toca_nada(con_dueno):
    feria, ana = con_dueno

    with pytest.raises(accesos.AccesoRechazado):
        accesos.transferir_propiedad(feria=feria, correo="  ")

    assert _dueno_de(feria) == ana


# ── El aviso ──────────────────────────────────────────────────


def test_se_avisa_a_quien_recibe_la_feria(con_dueno):
    feria, _ = con_dueno
    Persona.objects.create_user(correo="beto@filey.org", nombre="Beto")

    accesos.transferir_propiedad(feria=feria, correo="beto@filey.org")

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["beto@filey.org"]


def test_un_correo_que_falla_no_deshace_la_transferencia(con_dueno, monkeypatch):
    """La propiedad ya cambió y quien la recibe entra en cuanto conozca
    la dirección. Mismo criterio que `dar_acceso`."""
    feria, _ = con_dueno
    beto = Persona.objects.create_user(correo="beto@filey.org", nombre="Beto")

    def revienta(*args, **kwargs):
        raise accesos.avisos.AvisoFallido("el proveedor no contestó")

    monkeypatch.setattr(accesos.avisos, "avisar_dueno_de_feria", revienta)

    resultado = accesos.transferir_propiedad(feria=feria, correo=beto.correo)

    assert _dueno_de(feria) == beto
    assert resultado.aviso_enviado is False
    assert "no contestó" in resultado.error_aviso
