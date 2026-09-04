---
estado: aceptada
version: "1.0"
tags:
  - tipo/adr
  - dom/evt
  - tema/arquitectura
  - tema/seguridad
fecha: 2026-09-03
id: ADR-0010
responsable: Isaac Ortiz
supersede:
reemplazado_por:
---
# ADR-0010. Un archivo propio se puede ver dentro de la pantalla que lo pide

## Estado

`Aceptado` — 2026-09-03. Afina `ADR-0007`, no lo reemplaza: la regla de que ningún archivo
tiene URL sigue intacta, y lo que cambia es **con qué cabeceras sale** de la vista que ya
decidía quién puede verlo.

## Contexto

`ADR-0007` dejó los archivos fuera de toda URL: `MEDIA_URL` no está montada en ningún urlconf,
y cada módulo los entrega por una vista que primero comprueba quién pregunta. Esa vista los
sirve con tres cabeceras de defensa en profundidad:

```
X-Content-Type-Options: nosniff
Content-Security-Policy: sandbox; default-src 'none'
Cache-Control: private, no-store
```

Y por encima, el proyecto manda `X-Frame-Options: DENY` para **todo** lo que sale de Django.

Al construir `CU-EVT-003` —la pantalla donde quien propone consulta lo que envió— apareció una
necesidad que ninguna pantalla anterior había tenido: **ver el adjunto sin salir de la
pantalla**. La razón es concreta y no es estética. Los adjuntos de una propuesta son la portada
de un libro y el retrato de quien lo escribió; la pregunta que trae quien abre esa pantalla es
«¿subí la portada que era?», y un nombre de archivo no la contesta —dos versiones de la misma
imagen se llaman igual, y `IMG_4471.jpg` no distingue nada—.

Con las imágenes no hubo problema: un `<img>` no es un marco. Con los PDF sí, y **las dos
cabeceras fallan de la peor forma posible**:

- `X-Frame-Options: DENY` impide que el navegador pinte la respuesta dentro de un marco, **aunque
  el marco sea de la misma página que la pidió**.
- El `sandbox` sin tokens deja el documento en un **origen opaco**, y el visor de PDF integrado
  del navegador trata un documento de origen opaco como contenido ajeno y se niega a pintarlo.

Ninguna de las dos produce un error visible: sale un rectángulo en blanco. Quien lo viera
buscaría el fallo en el archivo, en la ruta o en el permiso, que es donde no está.

Las fuerzas en juego:

- **Estas cabeceras protegen de cosas reales.** `X-Frame-Options` corta el *clickjacking*: un
  sitio ajeno que embebe FILEY invisible sobre un cebo y cosecha clics con la sesión de quien
  cae. El `sandbox` es la red por si un archivo se colara disfrazado por la lista blanca.
- **La lista blanca ya excluye lo ejecutable.** `comun/almacenamiento.py` no admite `.html` ni
  `.svg`, que son los dos formatos con los que un archivo subido podría traer `<script>`.
- **Lo que se decida aquí lo repiten los demás módulos.** `STD` tiene la misma figura en la
  constancia fiscal de una editorial, y `TAL` y `VIS` la tendrán. Una excepción hecha a mano en
  `EVT` se copiaría cinco veces sin que nadie revisara el porqué.
- **La alternativa de no depender del navegador existe y cuesta.** Empaquetar PDF.js son ~1 MB
  de JavaScript versionado en el repositorio, que además hay que mantener al día.

## Opciones consideradas

### Opción A: relajar lo mínimo de cada cabecera, y solo en la vista de entrega

`X-Frame-Options: SAMEORIGIN` con el decorador de Django sobre esa vista, y
`Content-Security-Policy: sandbox allow-same-origin`.

- **A favor:**
  - `SAMEORIGIN` **cierra el clickjacking igual que `DENY`**: un sitio ajeno no es nuestro
    origen, así que su marco sigue bloqueado. Lo único que se permite es FILEY dentro de FILEY.
  - `allow-same-origin` **no habilita ejecución**. Sigue sin `allow-scripts`, `allow-forms`,
    `allow-popups` ni `allow-top-navigation`. Sin scripts no hay forma de leer nada del origen
    que se acaba de recuperar, que es el único riesgo que ese token podría abrir.
  - Va en la vista, con un decorador, así que **las demás pantallas conservan `DENY`**. La
    excepción es visible en el punto exacto donde aplica.
  - Cuesta dos líneas y ninguna dependencia.
- **En contra:**
  - Es una excepción, y las excepciones se copian sin releer el motivo. Se mitiga con este ADR
    y con una prueba que fija las tres cabeceras.
  - Depende del visor del navegador: cuál se use y cómo se vea no lo controlamos.

### Opción B: empaquetar PDF.js y pintar el documento nosotros

- **A favor:**
  - Ninguna cabecera cambia: el PDF se descarga por `fetch` y se dibuja en un `<canvas>`.
  - Control total de la apariencia, igual en todos los navegadores.
- **En contra:**
  - ~1 MB de JavaScript versionado en el repositorio (`ADR-0007`, regla 6: nada de CDN), que
    hay que actualizar cuando salgan sus parches de seguridad.
  - **Cambia el riesgo de sitio, no lo elimina.** Un visor propio interpreta el archivo con
    nuestro código en nuestro origen; el del navegador lo hace en un proceso aislado que no
    mantenemos nosotros.
  - Sería la pieza más pesada del proyecto después del build de Godot, para una pantalla que se
    abre unas cuantas veces por convocatoria.

### Opción C: dejarlo como está y abrir siempre en otra pestaña

- **A favor:**
  - Cero cambios de seguridad. Es lo que ya funcionaba.
- **En contra:**
  - No contesta la pregunta que trae quien abre la pantalla: comparar lo que subió con lo que
    quería subir obliga a saltar de pestaña y volver, con la propuesta perdida de vista.
  - Deja el sistema con dos comportamientos distintos para la misma acción —la imagen se ve
    dentro, el PDF no— sin ninguna razón que quien lo use pueda deducir.

## Decisión

**Un archivo propio se puede ver dentro de la pantalla que lo pide, en el dominio que lo
necesite.** La vista de entrega de `EVT` sale con `X-Frame-Options: SAMEORIGIN` y
`Content-Security-Policy: sandbox allow-same-origin`. **`STD` no cambia en nada**, y ningún
dominio hereda esto por compartir el módulo de entrega.

### 1. La excepción vive en la vista, no en los ajustes

`X_FRAME_OPTIONS = "DENY"` sigue siendo el valor del proyecto. La vista de entrega de cada
módulo lleva `@xframe_options_sameorigin`. Poner `SAMEORIGIN` en `settings.py` habría relajado
de paso todas las pantallas, que no lo necesitan y que no tienen por qué embeberse en ninguna
parte.

### 2. La política la declara **cada dominio**, no el módulo compartido

Y esto no es una preferencia de diseño: se aprendió dos veces el mismo día, en dos ramas que no
se veían. Las dos extrajeron la entrega de archivos de `STD` a `comun/` —para que `EVT` pudiera
reusarla sin importar de otro vertical (regla 4)—, y una de las dos se llevó la cabecera con
ella. Resultado: relajar el `sandbox` para el visor de `EVT` se lo relajó de paso a las
constancias fiscales y los comprobantes de pago de `STD`, que no lo habían pedido, no lo
necesitaban y no se enteraron — su prueba decía `"sandbox" in cabecera`, y eso lo cumplen las
dos políticas.

**Compartir el transporte es correcto; compartir la política no.** Cómo salen los bytes no es
de ningún dominio; con qué permisos, sí. Así que `comun/archivos.py::entregar` recibe la
cabecera por parámetro con `CSP_ESTRICTA` de fábrica, y cada dominio declara la suya al lado de
su `puede_ver`: `EVT` envuelve la función con `CSP_DEL_VISOR` y `STD` la llama tal cual, con lo
que conserva `sandbox; default-src 'none'` exactamente como estaba.

Las necesidades de un dominio no se le presumen a otro porque compartan una función.

### 3. `allow-same-origin` es el único token que se añade, y solo en `EVT`

Y se añade **por escrito**: cualquier otro token del `sandbox` —`allow-scripts` sobre todo—
está fuera. Una prueba lo fija por su ausencia, no solo por lo que sí está:

```python
assert "allow-same-origin" in csp
assert "allow-scripts" not in csp
```

Sin `allow-scripts`, recuperar el origen no sirve para leer nada: no hay nada que lo lea.

### 4. Lo que protege de verdad no cambia

La lista blanca de `comun/almacenamiento.py` —sin `.html` ni `.svg`— y el `nosniff` siguen
siendo la pareja que impide que un archivo subido se interprete como documento ejecutable. El
`sandbox` era, y sigue siendo, la tercera capa.

### 5. Solo se incrusta lo que un navegador pinta

Hoy, imágenes y PDF. Un `.docx` o un `.odt` de la lista blanca se quedan como enlace: prometer
un visor que saldría en blanco es peor que mandar a otra pestaña. Quién es qué lo decide una
propiedad del modelo por la extensión de lo guardado, no por el nombre que traía el archivo.

### 6. El acceso no cambia en absoluto

Estas cabeceras dicen **dónde se puede pintar** un archivo, no **quién lo puede pedir**. Lo
segundo sigue donde estaba: la vista pregunta a `servicios/archivos.py::puede_ver` antes de
entregar nada, y responde 404 —nunca 403— cuando la respuesta es que no.

## Consecuencias

- **Positivas:**
  - La pantalla contesta la pregunta que la gente trae, sin salto de pestaña.
  - El patrón queda escrito una vez para los cinco módulos que van a repetirlo.
  - El clickjacking sigue cerrado, y el `sandbox` sigue sin permitir ejecución.
- **Negativas / riesgos aceptados:**
  - Hay una excepción de seguridad en el sistema, y las excepciones se copian. Se mitiga con
    este ADR, con el aviso en `comun/archivos.py` y con dos pruebas que fijan la cabecera
    **exacta** de cada dominio — la de `STD` con un `==`, porque un `in` fue justamente lo que
    dejó pasar el contagio.
  - Cómo se ve un PDF depende del visor del navegador, que no controlamos. Si alguno no lo
    pinta, el `<object>` enseña su contenido de respaldo con el enlace de siempre.
  - Con `ALMACENAMIENTO=s3` **estas cabeceras no las ponemos nosotros**: la vista redirige a una
    URL firmada del bucket y ahí manda lo que el bucket tenga guardado. El visor podría dejar de
    funcionar el día que se active S3, sin que nadie toque código.
- **Qué queda descartado por esta decisión:** empaquetar un visor de PDF propio. Si algún día
  hiciera falta —anotar sobre el documento, marca de agua, un visor idéntico en todas partes—,
  eso es otro ADR y otra decisión.

## Referencias

- [`ADR-0007`](<0007-los-archivos-empiezan-en-disco.md>) — de dónde viene la regla de que ningún
  archivo tiene URL, y las cabeceras que se afinan aquí.
- [`CU-EVT-003`](<../requisitos/EVT/A - Convocatoria/CU-EVT-003 Consultar mis propuestas y revisar su estado actual.md>)
  — el caso de uso que lo obligó.
- `filey/comun/archivos.py` y `filey/apps/eventos/views.py::documento` — dónde vive.
