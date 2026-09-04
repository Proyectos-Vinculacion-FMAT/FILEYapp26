"""
Lo que la revisión necesita saber (`CU-EVT-007`, `CU-EVT-008`, `CU-EVT-011`).

La cola de propuestas, sus filtros y sus conteos. Está en un servicio y
no en la vista por la regla de siempre: el filtro va en la consulta —lo
que no se pide no llega a la respuesta— y un comando de `manage.py` que
quiera contar propuestas por estado tiene que poder hacerlo sin pasar por
HTTP.

Ninguna consulta de aquí filtra por feria, y no es un olvido: la feria es
el schema en el que la conexión está mirando (`ADR-0003`). Lo que sí se
filtra siempre es la **convocatoria**, porque una edición puede abrir más
de una convocatoria de eventos y cada una es una cola distinta.
"""

import re
from dataclasses import dataclass

from django.db.models import Count, Q

from apps.convocatorias.models import Convocatoria

from ..models import Solicitud

#: Con qué se entra a la cola completa antes de tocar nada.
RELACIONES = (
    "registro",
    "registro__persona",
    "registro__convocatoria",
    "registro__convocatoria__configuracion_eventos",
    "actividad",
    "actividad__tipo",
    "revisado_por",
)


def de_la_convocatoria(convocatoria: Convocatoria):
    """Todas sus propuestas, con lo que la lista y el detalle van a pedir.

    El ``select_related`` incluye la configuración de la convocatoria
    porque **el folio la necesita**: `Solicitud.folio` compone el prefijo
    leyéndola, así que sin traerla la lista dispara una consulta por fila
    solo para pintar la primera columna.
    """
    return Solicitud.objects.filter(
        registro__convocatoria=convocatoria
    ).select_related(*RELACIONES)


def cola(
    convocatoria: Convocatoria,
    *,
    estado: str = "",
    tipo: str = "",
    categoria: str = "",
    busqueda: str = "",
):
    """Las propuestas que cumplen los filtros (`CU-EVT-007`, pasos 3 y 4).

    Los cuatro filtros son independientes y se acumulan; ninguno es
    obligatorio, que es el `A1` —sin filtros salen todas—. Un valor que no
    esté en su conjunto cerrado **se ignora** en vez de dar error: llega
    de la barra de direcciones, así que es entrada de usuario y lo
    razonable es enseñar de más, no romper.
    """
    filas = de_la_convocatoria(convocatoria)
    if estado in Solicitud.Estado.values:
        filas = filas.filter(estado=estado)
    if tipo:
        filas = filas.filter(actividad__tipo__nombre=tipo)
    if categoria in Solicitud.Categoria.values:
        filas = filas.filter(categoria=categoria)
    if busqueda:
        filas = filas.filter(_donde_buscar(busqueda))
    return filas


def _donde_buscar(texto: str) -> Q:
    """Folio, proponente o título (`CU-EVT-007`, paso 3).

    «Proponente» son las dos cosas que la lista enseña en esa columna: la
    persona y la institución que representa. Buscar solo por una deja sin
    encontrar justamente la fila que se está mirando.

    El **folio no es una columna**: se compone como ``EVE-24`` a partir
    del id (§2.4). Así que buscarlo es sacarle el número — quien teclea
    «EVE-24», «eve 24» o «24» quiere la misma propuesta— y comparar contra
    la clave. Sin esto, el buscador que el caso de uso pide por folio no
    encontraría nunca nada, porque no hay contra qué comparar.
    """
    donde = (
        Q(titulo_actividad__icontains=texto)
        | Q(institucion__icontains=texto)
        | Q(registro__persona__nombre__icontains=texto)
        | Q(registro__persona__primer_apellido__icontains=texto)
        | Q(registro__persona__segundo_apellido__icontains=texto)
    )
    digitos = re.search(r"\d+", texto)
    if digitos:
        donde |= Q(pk=int(digitos.group()))
    return donde


def conteos_por_estado(convocatoria: Convocatoria) -> dict:
    """``{estado: cuántas}`` sobre **todas** las propuestas de la convocatoria.

    Sin filtrar, y es deliberado: un chip que dijera "Rechazadas 0" solo
    porque hay otro filtro puesto no sirve para navegar entre estados, que
    es justamente para lo que está.
    """
    return {
        fila["estado"]: fila["n"]
        for fila in Solicitud.objects.filter(registro__convocatoria=convocatoria)
        .values("estado")
        .annotate(n=Count("id"))
    }


def resumen(convocatoria: Convocatoria) -> dict:
    """Cuántas hay de cada cosa (`CU-EVT-011`).

    Son cuatro números y no los cinco estados, porque responden a una
    pregunta distinta de la de los chips. Los chips son para **navegar** y
    por eso hay uno por estado; esto es para **saber cómo va la
    convocatoria**, y ahí «pendiente» y «cambios solicitados» son lo
    mismo: propuestas que siguen esperando algo del comité.

    Se calcula del mismo diccionario que los chips para que los dos no
    puedan discrepar: dos consultas parecidas divergen en cuanto alguien
    toca una.
    """
    conteos = conteos_por_estado(convocatoria)
    por_revisar = sum(
        conteos.get(estado, 0) for estado in Solicitud.PENDIENTES_DE_RESOLVER
    )
    return {
        "recibidas": sum(conteos.values()),
        "por_revisar": por_revisar,
        "aceptadas": conteos.get(Solicitud.Estado.ACEPTADA, 0),
        "rechazadas": conteos.get(Solicitud.Estado.RECHAZADA, 0),
        "conteos": conteos,
    }


@dataclass(frozen=True)
class PersonaDeLaActividad:
    """Una persona de la ficha del tipo, ya lista para pintar.

    ``participa`` es ``None`` cuando el tipo no hace esa pregunta: solo
    los dos de publicación la hacen, una casilla por autor o editor
    (§2.7). ``None`` y no ``False`` porque «no se preguntó» y «dijo que
    no» son cosas distintas, y la pantalla las enseña distinto.

    ``campo_semblanza`` es el nombre de la columna en la tabla del tipo
    —``semblanza_autor_2``—. Se expone porque la corrección del
    administrador (`servicios/edicion.py`) escribe justo ahí, y sin él
    habría que volver a deducirlo recorriendo los campos por segunda vez
    con la misma heurística. Una sola función sabe cómo se llaman.
    """

    rol: str
    nombre: str
    semblanza: str
    participa: bool | None
    campo_semblanza: str = ""


#: Cómo empieza el `verbose_name` que arma `models.nombre_de`. Se recorta
#: para quedarse con el rol —«presentador 1»— en vez de repetir «nombre
#: del» en cada renglón de la ficha.
_PREFIJO_DEL_ROTULO = "nombre del "


def personas_de(actividad) -> list[PersonaDeLaActividad]:
    """Quiénes salen en esta actividad, sea cual sea su tipo.

    Las ocho tablas `Actividad_*` enumeran sus columnas una por una y no
    comparten base abstracta —es deliberado (§2.7)—, así que no hay un
    campo común que recorrer. Lo que sí comparten es la **forma del
    nombre** que les da la fábrica de `models.py`: por cada persona hay un
    ``nombre_<quien>_<n>``, su ``semblanza_<quien>_<n>``, y a veces un
    ``<quien>_<n>_participa``.

    Se recorre esa forma en vez de escribir ocho bloques en la plantilla,
    que es lo que haría falta si no: el detalle de una propuesta enseña lo
    mismo para los ocho tipos y solo cambian los rótulos.

    El rol sale del ``verbose_name`` del campo y no de su nombre en
    Python, y esa diferencia importa: en una presentación de libro los
    campos se llaman ``nombre_participante_1`` pero son los
    **presentadores**, y es lo que hay que leer en pantalla.

    Las que no tienen nada escrito no salen: son los huecos opcionales del
    formulario, y pintarlos vacíos alargaría la ficha con renglones que no
    dicen nada.
    """
    if actividad is None:
        return []
    detalle = actividad.detalle
    personas = []
    for campo in detalle._meta.get_fields():
        nombre_del_campo = getattr(campo, "name", "")
        if not nombre_del_campo.startswith("nombre_"):
            continue
        quien = nombre_del_campo.removeprefix("nombre_")
        # `nombre_editorial` y `nombre_organizador_*` empiezan igual y no
        # son personas de la ficha: lo que las distingue es que nadie
        # escribió una semblanza para ellas.
        if not hasattr(detalle, f"semblanza_{quien}"):
            continue
        valor = getattr(detalle, nombre_del_campo, "")
        if not valor:
            continue
        rotulo = str(getattr(campo, "verbose_name", quien))
        personas.append(
            PersonaDeLaActividad(
                rol=rotulo.removeprefix(_PREFIJO_DEL_ROTULO).capitalize(),
                nombre=valor,
                semblanza=getattr(detalle, f"semblanza_{quien}", ""),
                participa=getattr(detalle, f"{quien}_participa", None),
                campo_semblanza=f"semblanza_{quien}",
            )
        )
    return personas


def documentos_de(solicitud: Solicitud):
    """Los adjuntos de esa propuesta (`CU-EVT-008`, paso 4).

    Cuelgan de la actividad y no de la solicitud (§2.8), así que hay que
    bajar un salto. Devuelve vacío —y no revienta— cuando la propuesta
    todavía no tiene actividad: no debería pasar, las crea la misma
    transacción del envío, pero el detalle de una propuesta no es el sitio
    donde enterarse de eso.
    """
    actividad = getattr(solicitud, "actividad", None)
    if actividad is None:
        return []
    return actividad.documentos.all()
