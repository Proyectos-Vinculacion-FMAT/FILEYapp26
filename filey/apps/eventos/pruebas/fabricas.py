"""
Lo que hace falta para tener una propuesta de eventos en pie.

Vive aparte porque montarla cuesta piezas de tres dominios —persona,
feria, convocatoria, registro— y repetir eso en cada prueba escondería lo
que cada una está mirando.

Todo lo que toca tablas de `EVT` hay que llamarlo **dentro** de un
``schema_context``: sus tablas viven en el schema de la feria y no existen
en `public` (`ADR-0003`).
"""

from apps.convocatorias.models import Convocatoria, RegistroConvocatoria, TipoConvocatoria
from apps.registros.models import Persona

from ..models import CatalogoActividades, Solicitud

#: Los campos comunes a los ocho tipos, con valores que pasan validación.
PROPUESTA = {
    "institucion": "Editorial La Nave",
    "cargo": "Coordinadora editorial",
    "es_uady": False,
    "titulo_actividad": "El mar que nos habita",
    "nombre_organizador_organizacion": "Editorial La Nave",
    "nombre_moderador": "",
    "publico_objetivo": ["publico_general", "academico"],
    "sinopsis": "Una conversación sobre la memoria del puerto.",
    "requiere_constancia": True,
    "comentarios": "",
    "bases_aceptadas": True,
}


def persona(correo="laura@ejemplo.com", nombre="Laura"):
    return Persona.objects.create_user(
        correo=correo, nombre=nombre, primer_apellido="Peniche"
    )


def convocatoria(
    nombre="Actividades FILEY 2027",
    estado=Convocatoria.Estado.ABIERTA,
    tipo=TipoConvocatoria.EVT,
):
    """Una convocatoria sin pasar por el servicio de alta.

    Directa a propósito: las pruebas que miran el callback de
    configuración lo llaman ellas, y las demás no tienen por qué
    arrastrar una configuración que no usan.
    """
    return Convocatoria.objects.create(tipo=tipo, nombre=nombre, estado=estado)


def registro(de_persona, a_convocatoria):
    return RegistroConvocatoria.objects.create(
        persona=de_persona, convocatoria=a_convocatoria
    )


def tipo(nombre):
    """Un tipo del catálogo, que siembra la migración `0002`."""
    return CatalogoActividades.objects.get(nombre=nombre)


def solicitud(en_registro, **cambios):
    return Solicitud.objects.create(registro=en_registro, **{**PROPUESTA, **cambios})
