"""
Lo que hace falta para tener una solicitud de stands en pie.

Vive aparte porque montarla cuesta cinco piezas de tres dominios
—persona, feria, convocatoria, editorial, registro— y repetir eso en cada
prueba escondería lo que cada una está mirando.
"""

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.registros.models import Persona
from apps.stands.models import Editorial

FICHA = {
    "nombre": "Ediciones del Mayab",
    "domicilio_calle": "Calle 60",
    "domicilio_numero": "480",
    "domicilio_colonia": "Centro",
    "cp": "97000",
    "municipio": "Mérida",
    "estado": "Yucatán",
    "pais": "México",
    "director_general_nombre": "Ana Pech",
    "director_general_email": "ana@mayab.mx",
    "responsable_stand": "Ana Pech",
    "giro": "editor",
    "telefono_celular": "9991112233",
    "correo_electronico": "contacto@mayab.mx",
    "nombre_antepecho": "Ediciones del Mayab",
    "num_personas_atienden": 2,
    "cantidad_libros_aprox": 400,
    "cantidad_titulos_aprox": 120,
    "materiales": ["Libro", "Revista"],
    "tematicas": ["Literatura", "Infantil"],
}


def persona(correo="ana@ejemplo.com", nombre="Ana"):
    return Persona.objects.create_user(
        correo=correo, nombre=nombre, primer_apellido="Pech"
    )


def convocatoria(
    nombre="Stands 2027",
    estado=Convocatoria.Estado.ABIERTA,
    tipo=TipoConvocatoria.STD,
):
    """Una convocatoria sin pasar por el servicio de alta.

    Se crea directa a propósito: las pruebas que miran el callback de
    configuración lo llaman ellas, y las demás no tienen por qué
    arrastrar una configuración que no usan.
    """
    return Convocatoria.objects.create(tipo=tipo, nombre=nombre, estado=estado)


def editorial(de_persona, **cambios):
    datos = {**FICHA, **cambios}
    ficha = Editorial.objects.create(persona=de_persona, **datos)
    return ficha


def envio(*, con_documentos=True, **extra):
    """Un POST completo y válido del formulario de U1.

    Existe para que una prueba diga **solo lo que está mirando**. El
    formulario tiene treinta campos y crece con cada cosa que la ficha
    oficial pide; sin esto, añadir un campo obligatorio rompe una docena
    de pruebas que no tenían nada que ver.

    :param con_documentos: a ``False`` omite los adjuntos obligatorios,
        que es lo que hace falta para probar E1.
    """
    datos = {
        **FICHA,
        "materiales": ["Libro"],
        "tematicas": ["Literatura"],
        # La casilla de «acepto las bases»: sin ella no se envía, igual
        # que la ficha en papel no vale sin firma.
        "acepto": "on",
    }
    if con_documentos:
        datos["constancia_fiscal"] = SimpleUploadedFile("csf.pdf", b"%PDF")
        datos["lista_titulos"] = SimpleUploadedFile("titulos.pdf", b"%PDF")
    return {**datos, **extra}
