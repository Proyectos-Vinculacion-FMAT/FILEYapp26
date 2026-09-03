"""
El almacén de estáticos, con el build de Godot fuera del manifiesto.

En producción los estáticos se sirven versionados por hash: `filey.css`
se copia como `filey.a1b2c3.css` y el navegador puede cachearlo para
siempre. Para casi todo es exactamente lo que se quiere.

Para el mapa **no**, y el fallo es de los que solo aparecen desplegados:

- El build de `event-stand-map` es un `index.js` que carga `index.wasm` y
  `index.pck` **por su nombre literal**, escrito dentro del propio
  JavaScript por el exportador de Godot.
- Con el manifiesto, esos dos archivos se copian como `index.<hash>.wasm`
  e `index.<hash>.pck`. El `index.js` sigue pidiendo los de antes.
- Resultado: dos 404 y un canvas en blanco, **solo en producción**. En
  desarrollo no pasa, porque ahí el almacén es el plano.

Así que el directorio del mapa se queda sin hashear y sin post-procesar.
Se paga con que el navegador pueda servir un build viejo de su caché tras
una reexportación; la contrapartida es el mapa cargando, y el build
cambia una vez por edición, no una vez por despliegue.

.. note:: Cómo invalidar el caché tras reexportar

   Cambiando el `?v=` que la plantilla del mapa le pone al `src` del
   `<iframe>` — ver `apps/stands/templates/stands/mapa.html`. Es un
   número a mano, y es a propósito: un hash automático es justo lo que no
   puede haber aquí.
"""

from whitenoise.storage import CompressedManifestStaticFilesStorage


class EstaticosFiley(CompressedManifestStaticFilesStorage):
    """Versiona por hash todo menos lo que no lo tolera."""

    #: Prefijos que se copian con su nombre tal cual. Van con la barra
    #: final para que un futuro `mapas.css` —que sí puede hashearse— no
    #: caiga aquí por empezar igual.
    SIN_HASH = ("mapa/",)

    def _es_intocable(self, nombre: str) -> bool:
        return nombre.replace("\\", "/").startswith(self.SIN_HASH)

    def hashed_name(self, name, content=None, filename=None):
        if self._es_intocable(name):
            return name
        return super().hashed_name(name, content, filename)

    def post_process(self, paths, dry_run=False, **options):
        """Saca el mapa del post-proceso, pero **no del manifiesto**.

        Dos cosas, y la segunda es la que se olvida:

        1. No basta con no hashearlo: el post-proceso también **reescribe
           referencias dentro** de los `.js`, y el `index.js` de Godot es
           280 KB de código generado que no hay que tocar.
        2. Aun así tiene que **estar en el manifiesto**, apuntándose a sí
           mismo. `{% static %}` lo consulta, y un archivo ausente no
           degrada a servir el original: revienta con
           ``Missing staticfiles manifest entry``. La página del mapa
           dejaría de cargar entera, y otra vez **solo en producción**.
        """
        intocables = {
            nombre: paths[nombre] for nombre in paths if self._es_intocable(nombre)
        }
        procesables = {
            nombre: ruta for nombre, ruta in paths.items() if nombre not in intocables
        }

        yield from super().post_process(procesables, dry_run, **options)

        if not dry_run:
            # El manifiesto ya se guardó con lo procesado; se le añaden
            # los intocables apuntándose a sí mismos y se vuelve a
            # guardar. `hashed_files` es lo que `save_manifest` escribe.
            self.hashed_files.update({nombre: nombre for nombre in intocables})
            self.save_manifest()

        # Se anuncian como copiados y sin procesar, que es lo que son.
        # Omitirlos del todo haría que `collectstatic` no los mencionara
        # y nadie notaría si un día dejaran de copiarse.
        for nombre in intocables:
            yield nombre, nombre, False


# > [!warning] `runserver` sirve los estáticos con `Last-Modified` y sin
# > ninguna directiva de caché
#
# Sin directiva, el navegador aplica caché heurística: se guarda el
# archivo un rato por su cuenta, sin preguntar, y sigue ejecutando la
# versión anterior aunque ya haya cambiado en disco. El síntoma hace
# perder una tarde —se corrige algo en el JS, se recarga, y la pantalla
# sigue haciendo lo de antes—.
#
# **Un middleware no puede arreglarlo**: `StaticFilesHandler.__call__`
# sirve las rutas bajo `STATIC_URL` antes de entrar a la cadena, así que
# ninguna respuesta de estático pasa por ella. Se intentó y se retiró.
#
# Mientras se trabaja, lo que funciona es tener abiertas las herramientas
# del navegador con «Disable cache» marcado, o recargar con Ctrl+F5. En
# producción no existe el problema: los estáticos van con hash en el
# nombre y cachearlos para siempre es justo lo que se quiere.
