"""
Catálogo temporal de convocatorias para el portal del participante.

Ya no incluye el catálogo del administrador: esa pantalla dejó de
listar módulos y pasó a listar **ferias** (CU-FER-002,
`apps/ferias/views.py`), que sí sale de datos reales.

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
