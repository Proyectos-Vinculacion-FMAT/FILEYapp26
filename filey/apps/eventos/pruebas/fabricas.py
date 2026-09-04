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
    """La inscripción de esa persona a esa convocatoria.

    `get_or_create` y no `create`: una persona tiene **un** registro por
    convocatoria —lo sostiene `un_registro_por_persona_y_convocatoria`—
    y de él cuelgan todas sus propuestas. Con `create`, montar dos
    propuestas de la misma persona reventaba con un `IntegrityError` que
    no tenía nada que ver con lo que la prueba estaba mirando.
    """
    creado, _ = RegistroConvocatoria.objects.get_or_create(
        persona=de_persona, convocatoria=a_convocatoria
    )
    return creado


def tipo(nombre):
    """Un tipo del catálogo, que siembra la migración `0002`."""
    return CatalogoActividades.objects.get(nombre=nombre)


def solicitud(en_registro, *, estado=None, mensaje="", motivo="", **cambios):
    """Una solicitud con su dictamen, que son columnas de la misma fila.

    :param estado: por omisión, `pendiente`.
    :param mensaje: lo que pide corregir quien revisa.
    :param motivo: por qué se rechazó.

    Los tres se pasan por separado y no en `**cambios` porque son lo que
    más se varía en una prueba: el dictamen es justo lo que distingue un
    escenario de otro.
    """
    return Solicitud.objects.create(
        registro=en_registro,
        estado=estado or Solicitud.Estado.PENDIENTE,
        mensaje_cambios_solicitados=mensaje,
        motivo_rechazo=motivo,
        **{**PROPUESTA, **cambios},
    )
