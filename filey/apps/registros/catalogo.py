"""
Catálogo temporal de convocatorias/módulos para las pantallas
posteriores al login (convocatorias del participante y selección
de módulo del administrador, CU-REG-006).

REG no es dueño de este contenido: cuando los dominios EVT/TAL/
STD/VIS tengan su propio backend, cada uno expondrá su estado de
convocatoria y esto se reemplazará por una consulta real. Se
centraliza aquí para que el frontend sea 100 % data-driven.
"""

from .models import Modulo

# Tarjetas del portal del participante (convocatorias.html del prototipo)
CONVOCATORIAS_PARTICIPANTE = [
    {
        "modulo": Modulo.STD,
        "titulo": "Convocatoria de Stands",
        "descripcion": (
            "Renta de espacios y stands para editoriales, distribuidores "
            "y expositores comerciales."
        ),
        "icono": "🏬",
        "banner": "stand",
        "estado": "cerrada",
        "fechas": "Cierra el 30 de abril de 2027",
        "navegable": True,
    },
    
    {
        "modulo": Modulo.TAL,
        "titulo": "Actividades Infantiles / Juveniles",
        "descripcion": (
            "Talleres, cuentacuentos y visitas escolares del programa "
            "infantil y juvenil (VIDA)."
        ),
        "icono": "🎨",
        "banner": "infantil",
        "estado": "abierta",
        "fechas": "Cierra el 15 de agosto de 2027",
        "navegable": False,  # "Próximamente" en el prototipo
    },
    {
        "modulo": Modulo.EVT,
        "titulo": "Actividades FILEY (Eventos)",
        "descripcion": (
            "Conversatorios, conferencias, charlas, mesas redondas, "
            "presentaciones de libro/revista y más."
        ),
        "icono": "🎤",
        "banner": "eventos",
        "estado": "abierta",
        "fechas": "Cierra el 31 de agosto de 2027",
        "navegable": True,
    },
    {
        "modulo": Modulo.VIS,
        "titulo": "Visitas Escolares",
        "descripcion": (
            "Registra tu institución educativa, reserva talleres del "
            "programa VIDA y recibe tu carta de confirmación."
        ),
        "icono": "🚌",
        "banner": "visitas",
        "estado": "abierta",
        "fechas": "Cierra el 31 de agosto de 2027",
        "navegable": True,
    },
]

# Tarjetas del panel administrativo (admin-convocatorias.html del prototipo)
MODULOS_ADMIN = [
    {
        "modulo": Modulo.STD,
        "titulo": "Convocatoria de Stands",
        "descripcion": (
            "Renta de espacios y stands para editoriales, distribuidores "
            "y expositores comerciales."
        ),
        "icono": "🏬",
        "banner": "stand",
        "estado": "activo",
        "fechas": "Convocatoria abierta · cierra el 31 de agosto de 2027",
        "navegable": True,
    },
    {
        "modulo": Modulo.TAL,
        "titulo": "Actividades Infantiles / Juveniles",
        "descripcion": (
            "Talleres, cuentacuentos y actividades del programa infantil "
            "y juvenil (TAL)."
        ),
        "icono": "🎨",
        "banner": "infantil",
        "estado": "proximamente",
        "fechas": "Panel en construcción",
        "navegable": False,
    },
    {
        "modulo": Modulo.EVT,
        "titulo": "Actividades FILEY (Eventos)",
        "descripcion": (
            "Revisa y dictamina propuestas de conversatorios, conferencias, "
            "charlas y presentaciones de libro."
        ),
        "icono": "🎤",
        "banner": "eventos",
        "estado": "activo",
        "fechas": "Convocatoria abierta · cierra el 31 de agosto de 2027",
        "navegable": True,
    },
    {
        "modulo": Modulo.VIS,
        "titulo": "Visitas Escolares",
        "descripcion": (
            "Revisa propuestas de visita escolar, acepta o solicita cambios, "
            "y supervisa las reservaciones de talleres."
        ),
        "icono": "🚌",
        "banner": "visitas",
        "estado": "activo",
        "fechas": "Convocatoria abierta · cierra el 31 de agosto de 2027",
        "navegable": True,
    },
]
