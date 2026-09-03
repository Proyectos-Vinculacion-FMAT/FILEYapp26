---
name: filey-render
description: Cómo una pantalla de FILEY llega al navegador — el monolito Django real bajo filey/ (config, comun, plantillas, estaticos, apps por dominio), capas models/services/views, herencia de plantillas y layouts, parciales, htmx y Alpine servidos localmente, permisos por decorador, y el procedimiento para portar una pantalla del prototipo. Úsalo al crear o editar plantillas, vistas, URLs, estáticos, servicios de dominio, o cualquier HTML del prototipo. Cubre los dos renderizadores que hoy coexisten.
---

# FILEY — del componente a la pantalla servida

Este skill responde **¿cómo llega al navegador?**. Los otros dos:

| Necesitas | Skill |
| --- | --- |
| Elegir color, radio, sombra | `filey-identidad` |
| Cuántos pasos, campos u opciones; qué se revela y cuándo; cómo se redacta | `filey-ux` |
| Saber si una clase existe y en qué capa vive el CSS | `filey-ui-componentes` |

## 0. Autoridad: qué manda sobre este skill

En orden. Si algo aquí contradice una fuente superior, **gana la fuente superior** y este
archivo está desactualizado:

1. **`docs/adr/`** — un ADR en estado `Aceptado` no se contradice sin escribir uno que lo
   reemplace. ADR-0001: monolito Django. ADR-0002: la migración desde DRF+JWT+Angular ya
   se ejecutó.
2. **`CLAUDE.md` de la rama donde vive el código** — trae la estructura de capas, la regla
   de dependencias entre apps y el estado actual.
3. **`README.md` de la raíz** — el flujo de CI/CD: qué rama recibe qué, cuándo se abre un PR.
   No es arquitectura, pero condiciona cuándo este skill considera terminado un trabajo — ver
   §10.
4. Este skill, que resume lo anterior y añade el puente con el prototipo.

## 1. ¿Qué renderizador aplica?

Míralo por la ruta del archivo. **No asumas** — hoy coexisten los dos.

| El archivo está en… | Renderizador | Referencia |
| --- | --- | --- |
| `prototipo/` | HTML estático sobre `file://` + pseudo-backend `db.js` | [references/renderer-estatico.md](references/renderer-estatico.md) |
| `filey/` | Monolito Django | [references/renderer-django.md](references/renderer-django.md) |

Errores típicos por confundirlos: `{% static %}` en un HTML del prototipo (sale literal) o
rutas relativas `../styles.css` en una plantilla Django (rompen porque la URL no corresponde
a la profundidad de carpetas).

---

## 2. Estructura real

El proyecto Django **no está en la raíz del repo**: cuelga de `filey/`, y `manage.py` está
en `filey/manage.py`. Los nombres son en español, de forma consistente.

```
filey/
  config/            settings, DOS urlconfs (públicas + de feria), wsgi/asgi
  comun/             transversal, de ningún dominio (htmx.py, limites.py, urls.py)
  plantillas/        base.html + layouts/ + componentes/  ← esqueleto compartido
  estaticos/         css/ js/ img/  (htmx.min.js y alpine.min.js versionados aquí)
  apps/<dominio>/
    models.py                    datos + invariantes  (fat models)
    services/ o servicios/       reglas de negocio, un módulo por área
    views.py                     traduce HTTP ↔ servicio  (thin views)
    urls.py                      rutas de la app
    permisos.py                  decoradores de acceso (registros Y ferias, cada una las suyas)
    templates/<dominio>/         pantallas del dominio
      parciales/                 fragmentos que devuelve htmx
    pruebas/                     tests (pytest), no `tests.py`
```

Cada feria vive en su propio schema de PostgreSQL (ADR-0003, `django-tenants`): una app va en
`SHARED_APPS` (una sola copia, schema `public`) o en `TENANT_APPS` (una copia por feria). El
detalle completo —los dos urlconfs, cómo se resuelve el schema, las trampas verificadas— está
en [references/renderer-django.md](references/renderer-django.md).

`apps/registros/` es la app de referencia y la base del sistema: identidad (`Persona`),
sesión y permisos. **Las dependencias van en una sola dirección** — los dominios verticales
(`eventos`, `talleres`, `stands`, `visitas`) importan de `registros`, nunca al revés, y
nunca entre hermanos de forma circular.

**Regla dura:** la lógica de negocio no vive en `views.py` ni en una plantilla. Si una regla
no se puede llamar desde un comando de `manage.py` sin pasar por HTTP, está en el lugar
equivocado: va a `services/`.

> [!note] Solo hay una estructura Django válida
> `main-isaac` tuvo un `config/` + `apps/` + `frontend/` en la raíz del repo, creado antes de
> conocer `filey/`. Se eliminó el 2026-08-11. Si vuelves a ver algo así fuera de `filey/`, es
> un error: no lo extiendas.

### Plantillas: híbrido, no centralizado

`DIRS = [BASE_DIR / "plantillas"]` **y** `APP_DIRS = True`. Cada una tiene su papel:

| Va en | Qué |
| --- | --- |
| `plantillas/base.html` | `<head>`, carga de htmx/Alpine, `hx-headers` con el CSRF |
| `plantillas/layouts/acceso.html` | Pantallas de acceso: panel de identidad + tarjeta |
| `plantillas/layouts/panel.html` | Todo lo posterior al login: barra superior y pie |
| `plantillas/componentes/` | Piezas compartidas entre módulos (avisos) |
| `apps/<dom>/templates/<dom>/` | Las pantallas del dominio |
| `apps/<dom>/templates/<dom>/parciales/` | Fragmentos que devuelve htmx |

Una pantalla nueva casi nunca extiende `base.html` directo: extiende un layout.
La variante administrativa **no es otra plantilla** — se pasa por contexto
(`es_admin`, `zona_admin`).

### Rol: decorador, no carpeta

En el prototipo el rol lo indica la carpeta (`aplicantes/` vs `administradores/`).
En Django **no**: las plantillas del dominio son planas y el rol se resuelve con

- el prefijo de URL (`/admin/acceso/` fuera de una feria; `/f/<slug>/accesos/` dentro), y
- los decoradores: `@requiere_participante` / `@requiere_admin` de
  `apps/registros/permisos.py` para lo de fuera de una feria, `@requiere_admin_feria` /
  `@requiere_dueno_feria` de `apps/ferias/permisos.py` para lo de dentro (ADR-0004).

**Ya no existe** un permiso por módulo (`requiere_modulo`, `NivelPermiso`, `RolPermiso`): se
derogó el 2026-08-21 y se retiró del código el mismo mes. El acceso administrativo se otorga
por feria completa, no por módulo — ver la nota de `apps/registros/permisos.py`.

Ningún módulo implementa su propia autenticación: la importa de `registros` (identidad, fuera
de toda feria) o de `ferias` (permiso dentro de una feria), nunca la suya propia.

---

## 3. Las dos reglas de frontend del monolito

1. **Toda pantalla funciona sin JavaScript.** La vista responde página completa o fragmento
   según `HX-Request`. htmx mejora la experiencia; no es requisito para usar el sistema.
2. **Nada se carga de un CDN.** htmx y Alpine viven en `estaticos/js/`. El sistema tiene que
   levantar sin salida a internet, y nadie puede cambiar por su cuenta el JS que servimos.

## 4. htmx: los ayudantes ya existen

No escribas cabeceras a mano. `comun/htmx.py` expone cuatro funciones:

| Función | Para qué |
| --- | --- |
| `es_htmx(peticion)` | Decidir si devuelves página completa o fragmento |
| `redirigir(peticion, destino)` | Navegar: htmx no sigue un 302, necesita `HX-Redirect` |
| `disparar(respuesta, evento, detalle)` | Avisar a Alpine de algo que solo el servidor sabe, sin re-renderizar y perder su estado |
| `reintentar_en(respuesta, segundos)` | `Retry-After` en cool-downs, lockouts y 429 |

Patrón de vista:

```python
@require_http_methods(["GET", "POST"])
def codigo(peticion):
    ...
    plantilla = "registros/parciales/estado_otp.html" if es_htmx(peticion) else "registros/codigo.html"
    return render(peticion, plantilla, contexto)
```

El markup del fragmento existe **una sola vez** y sirve para la página completa y para el
swap. Ese es el contrato entre lo visual y el renderizador.

## 5. Contrato vista ↔ plantilla

Una vista expone **nombres de dominio, no de presentación**: `propuestas`, `cupo_restante`,
`puede_dictaminar` — no `filas`, `color_badge`, `texto_boton`. La decisión de qué clase CSS
corresponde a un estado se toma en la plantilla o en un `templatetags/`, nunca devolviendo
`"badge-accepted"` desde la vista.

Todo partial documenta en un `{% comment %}` inicial qué contexto espera — son los que se
reusan sin ver la vista. `{# … #}` es de **una sola línea**; multilínea se imprime en el HTML.

## 6. CSS: hay una copia, y ya derivó

`filey/estaticos/css/filey.css` nació como **copia a mano** de `prototipo/common/styles-base.css`
+ `prototipo/REG/styles.css`, con los mismos nombres de token. Ya no es solo eso: con `STD`
portado va por 1576 líneas contra las 571 de esas dos hojas, así que la mayor parte de su
contenido ya no tiene original en el prototipo. Sigue siendo una segunda fuente, y esto es lo
que no coincide (recalculado 2026-09-01, con `STD` ya dentro):

- **9 tokens de `common` no están en `filey.css`.** Solo **5** son deuda —`--color-magenta-oscuro`,
  `--color-morado`, `--color-rojo-700`, `--color-rojo-800`, `--color-rojo-degradado-oscuro`—; los
  otros 4 (`--radio-btn`, `--radio-card`, `--radio-pill`, `--sombra-card`) están muertos también
  en el prototipo (`filey-identidad` §3), así que su ausencia es correcta.
- **Los tokens de dominio no cuentan como deriva.** `VIS` define 28 en su propia hoja y `EVT` 2
  (`--ok-200`, `--err-200`); ninguno tiene por qué estar en `filey.css` mientras ese dominio no
  se porte. Antes de dar una ausencia por deuda, mira en el inventario a qué capa pertenece.
- **3 tokens viven solo en `filey.css`.** `--alto-topbar` y `--alto-etiqueta` son suyos —los usa
  el chasis servido— y no deben bajar al prototipo. `--azul-300` sí es deriva, pero al revés:
  ahí está definido y usado, y en el prototipo es una **referencia rota** (`check-ui.sh` E1).
- **Ninguna referencia rota en `filey.css`**: cero `var()` sin definición de su lado.
- **2 hex sueltos, y están en los dos lados** —no es que el prototipo ya los haya tokenizado—:
  `#aab3c0` en el placeholder de los inputs y el degradado `#1d8a4e`/`#0a6b53` de
  `.banner-infantil`. Es deuda compartida; en el prototipo la cuenta `check-ui.sh` (E3).
- ~~La regla de los controles de texto iba **detrás**~~ — corregida el 2026-08-29. La copia
  enumeraba `text`, `email`, `tel` y `select`, y el prototipo además `number` y `textarea`; un
  `<input type="number">` caía en el estilo de fábrica del navegador y salía angosto al lado de
  uno de texto. **No solo derivan los tokens: también las reglas**, y ésta no se veía hasta que
  una pantalla mezcló los dos tipos en la misma tarjeta (la configuración de la convocatoria).
  `date` y `search` se añadieron ahí y **siguen sin estar** en el prototipo, que no tiene campos
  nativos de esos.

**Regla mientras las dos existan:** al tocar un token o un componente compartido en el
prototipo, propágalo a `filey.css` en el mismo cambio; y al portar una pantalla, copia al
`filey.css` solo lo que esa pantalla usa, con el nombre de token idéntico. Nunca inventes un
nombre distinto para el mismo valor: eso es lo que vuelve irreconciliables las dos hojas.
`./prototipo/scripts/gen-inventario.sh` da la lista autoritativa de tokens del prototipo.

## 7. Portar una pantalla del prototipo

1. Localiza el HTML en `prototipo/{DOM}/{rol}/` y **no lo leas completo**: `grep -n` las
   secciones que necesitas (protocolo de lectura en `filey-ui-componentes`).
2. Crea `filey/apps/<dominio>/templates/<dominio>/<pantalla>.html` extendiendo
   `layouts/panel.html` (o `layouts/acceso.html` si es de acceso).
3. Copia solo el contenido propio de la pantalla: `<head>`, barra superior y pie los da el layout.
4. Sustituye:
   - `href="otra.html"` → `{% url 'dominio:vista' %}`
   - `src="../../common/assets/x.svg"` → `{% static 'img/x.svg' %}` (y copia el asset a `estaticos/img/`)
   - datos de `db.js` → contexto que arma un `services/`
   - `<script>` de re-render → htmx contra un `parciales/_x.html`
5. El CSS que la pantalla necesite y no esté en `filey.css`, cópialo con el mismo nombre de
   token y clase. Si venía en un `<style>` embebido del prototipo, esa es la ocasión de
   bajarlo a la hoja.
6. La regla de negocio va a `services/`, no a la vista.
7. La pantalla del prototipo se queda como estaba hasta que el dominio entero esté portado.

### Lo que se separa en silencio entre los dos

§6 cubre la deriva del **CSS**. Esta es la del **comportamiento**, que no la caza ningún script
y salió entera de portar `CU-EVT-002`: cada punto de abajo divergió de verdad y hubo que
volver.

| Qué | Por qué se separa |
| --- | --- |
| **Orden de los campos** | En el prototipo lo fija el orden del generador; en Django, la plantilla. Nada los ata |
| **Alto de los `<textarea>`** | Django pinta `rows="10"` por omisión y el navegador 2. Los dos son un accidente, no una decisión |
| **Cuántas secciones** | Agrupar por tabla (Django) no es lo mismo que agrupar por lo que la persona percibe como una cosa (prototipo) |
| **Radio contra casilla** | Un `BooleanField` de Django sale casilla; un sí/no explícito sale radio. Cambia si hay asterisco |
| **Valores por omisión** | `checked` en el prototipo y `default=` en el modelo se escriben en sitios distintos |
| **Texto de ejemplo** | Es del prototipo **y solo del prototipo**: acelera la demo y no puede llegar al programa |
| **Rótulos** | Django los compone del nombre de la columna y salen sin acento («Titulo actividad») |

Al portar, la pregunta no es «¿se ve parecido?» sino **«¿qué de esto lo decidió alguien y qué lo
decidió el valor por omisión de la herramienta?»**. Lo segundo es lo que diverge.

Y al revés: si el prototipo es la especificación visual, un arreglo que se encuentre al portar
—un selector de más, un desplazamiento que tapa el encabezado— **vuelve al prototipo en el mismo
cambio**. Si no, la próxima vez que alguien lo mire, el defecto sigue ahí y parece que Django
es el que está mal.

## 8. Una prueba corre en Windows y en Linux, o no sirve

Se desarrolla en Windows y se despliega en Linux (Render). Una prueba que solo pasa en uno de
los dos es peor que no tenerla: da luz verde en un lado y ruido en el otro, y quien la escribió
no es quien la ve fallar.

**Nunca afirmes sobre una ruta compuesta.** `os.path.join`, `os.path.split`, `str(tmp_path)` y
`__file__` devuelven el separador del sistema: contrabarra en Windows, diagonal en Linux. Si el
valor bajo prueba pasó por alguno de ellos, la cadena literal no es comparable.

| En vez de | Escribe |
| --- | --- |
| `assert ruta.startswith("css/x")` | `assert PurePath(ruta).parts == ("css", "x")` |
| Comparar la salida cruda de una API | Normaliza como lo hace la propia librería |
| `open("/tmp/x")` | `tmp_path / "x"` (la fixture de pytest) |
| Comparar una salida multilínea como una sola cadena | Compara con `salida.splitlines()` |

> [!note] Normaliza con la función de la librería, no con un `replace` a mano
> `comun/pruebas/test_estaticos.py::test_lo_demas_si_se_versiona` fue el caso real.
> `HashedFilesMixin.hashed_name` arma el nombre con `os.path.join`, así que en Windows devuelve
> `css\prueba.<hash>.css`. La prueba afirmaba `startswith("css/prueba.")` y fallaba **solo en
> Windows**.
>
> El arreglo no fue un `.replace()` en la prueba, sino llamar a `almacen.clean_name(...)` — la
> misma función con la que Django envuelve a todos los consumidores de `hashed_name`. Así la
> prueba ejercita el camino real: `hashed_name` es el **único** punto que Django deja sin
> normalizar, y afirmar ahí era afirmar en la capa equivocada.
>
> Y antes de declarar frágil una prueba, **recorre la cadena entera**. `FileField` también
> arma su ruta con `os.path.normpath`, pero `FileSystemStorage._save` la normaliza antes de
> devolverla, así que `archivo.name` trae diagonales en las dos plataformas y afirmar sobre él
> es seguro. Medir en un paso intermedio es el mismo error, al revés.
>
> No hubo que tocar código de producción, y ese es el olor a buscar: si para que una prueba
> pase en las dos plataformas hay que cambiar el programa, lo más probable es que la prueba
> esté mirando el nivel que no toca.

Tres cosas más que separan los dos entornos:

- **Linux distingue mayúsculas.** `{% extends "Layouts/panel.html" %}` funciona en Windows y da
  500 en Render. La prueba que la cubra tiene que existir; el sistema de archivos no te avisa.
- **Nada de rutas absolutas escritas a mano** (`C:\...` ni `/tmp/...`): `tmp_path`, `tmpdir` o
  `settings.MEDIA_ROOT` apuntado a una temporal.
- **Los finales de línea.** Si comparas contra un archivo del repo, léelo en texto y compara por
  líneas — `.gitattributes` fija LF en los `.sh`, pero no en todo.

## 9. Checklist

```bash
cd filey && python manage.py check && python manage.py runserver
cd filey && pytest                 # las pruebas viven en apps/<dom>/pruebas/
./prototipo/scripts/check-ui.sh    # aplica al prototipo
```

- [ ] La plantilla extiende un layout, no repite `<head>` ni el chasis
- [ ] Cero rutas relativas: `{% url %}` y `{% static %}`
- [ ] La vista es delgada; la regla de negocio está en `services/`
- [ ] El acceso está protegido por decorador (`registros.permisos` fuera de una feria,
      `ferias.permisos` dentro), no por la carpeta ni por un permiso por módulo
- [ ] La pantalla funciona con JavaScript desactivado
- [ ] Ningún `<script src="https://…">`
- [ ] Los tokens usados existen con el mismo nombre en el prototipo
- [ ] Comentarios multilínea con `{% comment %}`
- [ ] Ninguna prueba afirma sobre una ruta compuesta ni sobre un absoluto escrito a mano (§8)
- [ ] El CU completo está cubierto —flujo principal y los alternos/excepción documentados—,
      no solo la pantalla feliz (ver §10 antes de abrir el PR)

## 10. Cuándo el trabajo está listo para PR

El flujo de CI/CD vive en [`README.md`](../../../README.md) de la raíz del repo: rama personal
→ PR a `develop` (pruebas de integración) → PR a `QA` (pruebas de aceptación) → PR a `main`
(producción), con deploy automático a Render en cada etapa. Lo que este skill necesita que
tengas presente **antes de abrir el primer PR**, no después:

- **Una feature es un CU** (o un grupo cohesivo de CUs que no tiene sentido separar — p. ej.
  "llenar el formulario" y "enviarlo" si un mismo CU ya los integra). No es una pantalla suelta
  ni un modelo sin las vistas que lo usan.
- **El PR a `develop` solo se levanta con la feature completa en su totalidad.** El README lo
  dice explícito: no hay PRs de "avance parcial" que se completan después en `develop` — eso
  es exactamente lo que este flujo evita, porque `develop` ya se despliega a Render(dev) y las
  pruebas de integración asumen que lo que llegó ahí funciona de punta a punta.
  "Completo" para este skill significa: modelo + `services/` + vistas + plantillas + permisos
  + pruebas del CU, cubriendo su flujo principal y sus alternos/excepción documentados —no
  basta con que la pantalla se vea, tiene que sostener el caso de uso.
- **Un PR, una feature.** Si mientras implementas un CU descubres que necesitas tocar algo de
  otro (p. ej. un campo que `registros` no tenía), ese cambio va en su propio commit con su
  propia razón, pero el PR sigue representando una sola feature — no la conviertas en un PR
  de varias cosas a la vez porque coincidieron en tiempo.
- **Si `develop` o `QA` rechazan la feature, la corrección vuelve a tu rama personal** y sube
  por el mismo camino (PR a `develop`, luego a `QA` de nuevo) — nunca se parchea directo en
  `develop`/`QA`/`main`.
- Antes de abrir el PR, corre el checklist de §9 completo, no solo la parte que tocaste.
