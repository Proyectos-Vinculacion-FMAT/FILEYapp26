"""
Los adjuntos que sobreviven a un envío rechazado (`CU-EVT-002`).

Un ``<input type="file">`` **no se puede repoblar**: ningún navegador
deja que una página le ponga un archivo, y con razón —si pudiera,
cualquier sitio subiría lo que quisiera del disco de quien lo visita—.
Así que un envío rechazado por un campo de texto se llevaba por delante
los adjuntos, y quien lo sufría tenía que volver a buscarlos sin entender
por qué solo se habían perdido ésos.

Este módulo es la cola que lo evita. Cuatro operaciones y ninguna
decisión de pantalla: qué se enseña lo decide la plantilla, y cuándo se
llama, la vista.

.. note:: Por qué el tope es seis

   No es «tres intentos de historial»: es **margen sobre el formulario
   más grande**. Hoy el que más pide son dos adjuntos, pero el tope está
   puesto para uno de cuatro sin que nadie se quede sin sus archivos
   precargados. Los vigentes nunca se desalojan (ver `_desalojar`), así
   que seis significa «los cuatro que hagan falta, más dos de sobra».

   El tope existe porque cada archivo pesa hasta 10 MB
   (`comun/almacenamiento.py`) y **el historial no lo mira nadie**: lo
   único que se usa de verdad es el último de cada tipo. Sin tope, unas
   cuantas personas indecisas llenarían el disco del contenedor con
   versiones de una portada.

.. warning:: La cola es de la **sesión**, no de la persona

   `EVT` no guarda borradores de solicitud: o se envía, o no hay nada. Un
   adjunto suelto solo significa algo mientras dure el rato en que
   alguien está llenando el formulario. Por eso este dominio **no tiene
   política de días** —eso es de `STD`, donde los plazos son del
   negocio—: lo que le pone caducidad a una fila es la sesión que la
   creó.

   Se vacía en cuanto deja de hacer falta, y son cuatro momentos:

   1. **Al enviarse la propuesta.** Los archivos pasan a ser `Documento`
      y aquí ya no hay nada que recuperar.
   2. **Al salir del formulario** hacia el listado o el catálogo.
   3. **Al cerrar sesión**, por la señal ``user_logged_out``.
   4. **Al aparecer con otra sesión.** Volver mañana no ofrece los
      archivos de ayer: ofrecerlos sería un borrador a medias.

   Lo único que no alcanza ninguno de los cuatro es cerrar la pestaña y
   no volver nunca. De eso se encarga `manage.py barrida_espera`, cuyo
   criterio tampoco es una fecha: borra las filas **cuya sesión ya no
   existe**.
"""

import logging
from pathlib import PurePosixPath

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import DatabaseError, transaction

from apps.convocatorias.models import Convocatoria

from ..models import ArchivoEnEspera

logger = logging.getLogger(__name__)


def _tope() -> int:
    """Cuántos se guardan. Se lee al llamar y no al importar.

    Así una prueba puede bajarlo con ``settings.EVT_MAX_ARCHIVOS_EN_ESPERA
    = 2`` y ejercitar el desalojo sin subir siete archivos.
    """
    return getattr(settings, "EVT_MAX_ARCHIVOS_EN_ESPERA", 6)


def de(convocatoria: Convocatoria, persona, session_key: str = ""):
    """Lo que hay en espera, de lo más nuevo a lo más viejo.

    :param session_key: si se da, solo lo subido **en esa sesión**. Sin
        él, todo lo de esa persona en esa convocatoria — que es lo que
        necesitan las operaciones de limpieza, no las de pantalla.
    """
    if persona is None or not getattr(persona, "is_authenticated", False):
        return ArchivoEnEspera.objects.none()
    filas = ArchivoEnEspera.objects.filter(convocatoria=convocatoria, persona=persona)
    return filas.filter(session_key=session_key) if session_key else filas


def vigentes(convocatoria: Convocatoria, persona, session_key: str = "") -> dict:
    """El último de cada tipo, que es lo que llena el formulario.

    :returns: ``{tipo_documento: ArchivoEnEspera}``. Vacío si no hay
        sesión o no se ha subido nada.

    De los seis que caben, en un formulario solo se usan uno o dos. Los
    demás son historial que nadie pidió y que la cola acabará desalojando;
    quedarse con el último de cada tipo es lo que hace que «volver a
    subirlo» signifique «sustituirlo».
    """
    ultimo_por_tipo = {}
    # El orden del modelo es del más nuevo al más viejo, así que el
    # primero de cada tipo gana y los siguientes no lo pisan.
    for archivo in de(convocatoria, persona, session_key):
        ultimo_por_tipo.setdefault(archivo.tipo_documento, archivo)
    return ultimo_por_tipo


@transaction.atomic
def guardar(convocatoria: Convocatoria, persona, documentos, session_key: str) -> int:
    """Mete en la cola los archivos que llegaron, y desaloja los viejos.

    :param documentos: iterable de ``(tipo_documento, archivo)``, tal
        como lo devuelve ``ActividadForm.documentos()``. Los huecos se
        ignoran: en un envío rechazado es normal que solo llegue uno.
    :param session_key: la sesión que los sube. Es lo que les pone
        caducidad — ver el aviso de arriba.
    :returns: cuántos se guardaron.

    Se llama **solo cuando el envío falló**. Si hubiera salido bien, los
    archivos ya serían `Documento` y meterlos aquí sería duplicar cada
    adjunto del sistema en disco.
    """
    # Antes de nada, lo de sesiones anteriores de esta misma persona: no
    # se le va a ofrecer nunca —`vigentes` filtra por sesión— y ocuparía
    # sitio en la cola desalojando a lo de ahora.
    olvidar_otras_sesiones(convocatoria, persona, session_key)

    guardados = 0
    for tipo_documento, archivo in documentos:
        if not archivo:
            continue
        ArchivoEnEspera.objects.create(
            convocatoria=convocatoria,
            persona=persona,
            tipo_documento=tipo_documento,
            archivo=archivo,
            nombre_original=getattr(archivo, "name", "")[:255],
            session_key=session_key,
        )
        guardados += 1

    if guardados:
        _desalojar(convocatoria, persona, session_key)
    return guardados


def olvidar_otras_sesiones(convocatoria: Convocatoria, persona, session_key: str) -> int:
    """Borra lo que esa persona dejó en **otras** sesiones.

    Es el cuarto momento de limpieza del aviso de arriba, y el que hace
    verdadera la frase «no se guardan borradores»: aparecer con otra
    sesión es empezar de cero, no continuar lo de ayer.
    """
    borrados = 0
    otras = de(convocatoria, persona).exclude(session_key=session_key)
    for archivo in list(otras):
        archivo.delete()
        borrados += 1
    return borrados


def _desalojar(convocatoria: Convocatoria, persona, session_key: str) -> int:
    """Deja la cola en el tope, **sin tirar nunca uno que haga falta**.

    Se desaloja del extremo viejo, pero saltándose el último de cada
    tipo. Sin esa salvedad, el tope no cumple lo que promete:

        Un formulario con cuatro adjuntos. Se suben los cuatro y el envío
        falla. Se corrige uno y se vuelve a subir: cinco filas. Otro:
        seis. Un tercero: siete, y una FIFO a secas tira la más vieja —
        que es el primer adjunto, el único que nadie ha vuelto a subir—.
        El campo se queda vacío otra vez y el formulario vuelve a
        pedirlo, que es exactamente el problema que esto vino a resolver.

    Con la salvedad, lo que queda garantizado es: caben los vigentes de
    todos los campos más lo que sobre de historial. Por eso el tope es
    seis y no cuatro — cuatro adjuntos como máximo, y margen encima
    (`settings.EVT_MAX_ARCHIVOS_EN_ESPERA`).

    Se borra fila por fila y no con ``queryset.delete()``: hace falta que
    salte la señal `post_delete` de cada una para que su archivo se vaya
    del disco, y el queryset de aquí viene de un filtro por `pk` que no
    conviene armar dos veces.
    """
    intocables = {a.pk for a in vigentes(convocatoria, persona, session_key).values()}
    # De la más nueva a la más vieja; se recorre al revés para quitar
    # primero lo que más tiempo lleva sin que nadie lo mire.
    candidatas = [
        a for a in de(convocatoria, persona, session_key) if a.pk not in intocables
    ]
    cuantas_sobran = len(intocables) + len(candidatas) - _tope()

    sobran = candidatas[len(candidatas) - cuantas_sobran :] if cuantas_sobran > 0 else []
    for archivo in sobran:
        archivo.delete()
    if sobran:
        logger.info(
            "Desalojados %s archivos en espera de la persona %s en la convocatoria %s",
            len(sobran),
            getattr(persona, "pk", None),
            convocatoria.pk,
        )
    return len(sobran)


def descartar(convocatoria: Convocatoria, persona, tipo_documento: str) -> int:
    """Quita lo guardado de **un** campo. Devuelve cuántas filas se fueron.

    Se van todas las de ese tipo y no solo la última: el historial de un
    campo que se acaba de descartar no le sirve a nadie, y dejarlo haría
    reaparecer una versión vieja en cuanto se desalojara la nueva.
    """
    borrados = 0
    for archivo in list(de(convocatoria, persona).filter(tipo_documento=tipo_documento)):
        archivo.delete()
        borrados += 1
    if borrados:
        logger.info(
            "Descartado el adjunto %s de la persona %s en la convocatoria %s",
            tipo_documento,
            getattr(persona, "pk", None),
            convocatoria.pk,
        )
    return borrados


def descartar_los_que_ya_no_caben(
    convocatoria: Convocatoria, persona, session_key: str, tipos_admitidos
) -> int:
    """Quita lo guardado que el tipo de actividad elegido ya no pide.

    :param tipos_admitidos: los `Documento.Tipo` que ese tipo de
        actividad acepta. **Vacío en los seis tipos que no piden
        adjuntos**, y entonces se va todo.
    :returns: cuántas filas se fueron.

    Alguien elige «presentación de libro», sube la portada y el retrato,
    y después cambia a «charla». La charla no pide adjuntos: esos dos
    archivos ya no tienen dónde enseñarse ni campo al que volver, así que
    no son nada — ocupan disco y sitio en la cola, y reaparecerían si esa
    persona volviera a libro, que es justo lo que la política de «no se
    guardan borradores» no quiere.

    .. note:: Se decide por el tipo **elegido ahora**, no por el anterior

       El servidor no sabe de qué tipo se viene: cada petición trae solo
       el tipo actual. Y no hace falta saberlo — la pregunta correcta no
       es «¿cambió de tipo?» sino «¿cabe este archivo en lo que hay
       elegido?». Guardar el tipo anterior en la sesión para compararlo
       sería un estado más que mantener y una forma más de que se
       desincronice.
    """
    admitidos = set(tipos_admitidos)
    sobran = de(convocatoria, persona, session_key).exclude(
        tipo_documento__in=admitidos
    )
    borrados = 0
    for archivo in list(sobran):
        archivo.delete()
        borrados += 1
    if borrados:
        logger.info(
            "Descartados %s adjuntos que el tipo elegido ya no pide "
            "(persona %s, convocatoria %s)",
            borrados,
            getattr(persona, "pk", None),
            convocatoria.pk,
        )
    return borrados


def limpiar(convocatoria: Convocatoria, persona) -> int:
    """Vacía la cola de esa persona. Devuelve cuántas filas se fueron.

    Se llama al enviar con éxito y al salir del formulario. Es idempotente
    a propósito: la pantalla de salida no sabe si había algo que limpiar,
    y preguntarlo antes sería una consulta de más en cada visita al
    catálogo.
    """
    borrados = 0
    for archivo in list(de(convocatoria, persona)):
        archivo.delete()
        borrados += 1
    if borrados:
        logger.info(
            "Vaciada la espera de la persona %s en la convocatoria %s (%s archivos)",
            getattr(persona, "pk", None),
            convocatoria.pk,
            borrados,
        )
    return borrados


def limpiar_la_feria(persona) -> int:
    """Vacía la espera de esa persona en **todas** las convocatorias.

    Es lo que hace falta al salir al catálogo: desde ahí no se sabe de
    qué convocatoria venía, y una feria puede tener más de una de
    eventos. Salir al catálogo es salir de todas.

    Aislado como el de `limpiar_toda_la_plataforma`, y por lo mismo: el
    catálogo es la portada de la feria, y un fallo aquí abortaría la
    transacción de la petición y tumbaría la pantalla entera por una
    limpieza de temporales.
    """
    if persona is None or not getattr(persona, "is_authenticated", False):
        return 0
    return _vaciar_de_esta_feria(persona)


def limpiar_toda_la_plataforma(persona) -> int:
    """Vacía la espera de esa persona en **todas las ferias**.

    Es lo que hace falta al cerrar sesión, que ocurre fuera de toda feria
    —el urlconf público— y por tanto sin schema donde buscar. Hay que
    entrar en cada uno: `ArchivoEnEspera` vive en el de cada edición y
    una consulta desde `public` no ve nada (`ADR-0003`).
    """
    if persona is None or not getattr(persona, "is_authenticated", False):
        return 0

    from django_tenants.utils import schema_context

    from apps.ferias.models import Feria

    borrados = 0
    # `reales` y no `objects`: la fila de `public` no es una feria, y
    # entrar en su schema a buscar tablas de `EVT` reventaría.
    for feria in Feria.reales.all():
        with schema_context(feria.schema_name):
            borrados += _vaciar_de_esta_feria(persona)
    return borrados


def _vaciar_de_esta_feria(persona) -> int:
    """Borra lo de esa persona en el schema activo, **aislado del resto**.

    .. warning:: El `atomic()` no es por atomicidad: es un punto de rescate

       En PostgreSQL, una consulta que falla **aborta la transacción
       entera**: todo lo que venga después responde
       ``InFailedSqlTransaction`` hasta que alguien haga rollback. Un
       ``try/except`` alrededor no lo deshace — atrapa la excepción de
       Python y deja la transacción rota igual.

       Eso rompió el cierre de sesión: este barrido corre desde
       ``user_logged_out``, un schema no tenía la tabla —una feria creada
       sin migrar `EVT`—, la consulta abortó la transacción, y el
       ``logout()`` que venía justo después no pudo ni borrar la fila de
       la sesión. Nadie podía cerrar sesión, y el log solo decía que no se
       había podido vaciar unos temporales.

       Con `atomic()` el fallo revierte hasta este savepoint y la
       transacción de fuera sigue viva. Va **por feria** y no alrededor
       del bucle para que un schema en mal estado no se lleve por delante
       la limpieza de los demás.
    """
    borrados = 0
    try:
        with transaction.atomic():
            for archivo in list(ArchivoEnEspera.objects.filter(persona=persona)):
                archivo.delete()
                borrados += 1
    except DatabaseError:
        # Que una feria no tenga la tabla no es motivo para que nadie
        # pueda cerrar sesión. Se anota y se sigue con la siguiente.
        logger.exception(
            "No se pudo vaciar la espera de adjuntos en un schema de EVT"
        )
        return 0
    return borrados


def adoptar(en_espera: ArchivoEnEspera):
    """El contenido del archivo, listo para colgar de un `Documento`.

    Se devuelve el contenido y **no la fila**: el servicio de alta crea el
    `Documento` con él, y al guardarlo Django lo escribe otra vez pasando
    por `upload_to`, así que acaba en la carpeta de los adjuntos de verdad
    y no en la de espera. Cuesta una copia y a cambio el disco se puede
    leer: lo que está en `en-espera/` es siempre provisional.

    .. warning:: Se lee entero y se cierra, y no es una preferencia

       Devolver un `File` sobre el fichero abierto —que es lo natural—
       deja un descriptor vivo. Justo después, enviar bien vacía la cola y
       la señal `post_delete` intenta borrar ese mismo fichero:

       - En Linux se puede borrar un archivo abierto, así que **pasa**.
       - En Windows revienta con ``PermissionError: [WinError 32]``.

       Es la asimetría de `filey-render` §8 en su forma más cara: código
       de producción que funciona en el despliegue y falla en la máquina
       de quien lo escribe. Con el contenido en memoria no hay descriptor
       que estorbe, y caben de sobra: el tope por archivo son 10 MB
       (`comun/almacenamiento.py`) y un envío trae dos como mucho.
    """
    with en_espera.archivo.open("rb") as abierto:
        contenido = abierto.read()
    # El nombre importa: de él saca `CarpetaDeLaFeria` la extensión con la
    # que se guarda. Sin `nombre_original` se cae al del disco, que es un
    # UUID pero conserva la extensión.
    nombre = en_espera.nombre_original or PurePosixPath(en_espera.archivo.name).name
    return ContentFile(contenido, name=nombre)
