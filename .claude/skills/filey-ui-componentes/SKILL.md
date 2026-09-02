---
name: filey-ui-componentes
description: Inventario y arquitectura del CSS/markup de FILEY — qué clase o token ya existe, en qué capa vive (common vs. dominio), cuándo promover o degradar un componente, cómo escribir el mínimo CSS y HTML nuevo, y el protocolo de lectura barata para no volcar archivos completos al contexto. Úsalo al crear o editar cualquier pantalla, al añadir estilos, al dudar entre reusar y crear, o cuando una pantalla necesite un componente que quizá ya existe. Incluye reglas de SVG y el verificador check-ui.sh.
---

# FILEY — componentes, capas y economía

Este skill responde **¿con qué se construye y dónde vive?**. Los otros dos:

| Necesitas | Skill |
| --- | --- |
| Elegir un color, radio, tamaño | `filey-identidad` |
| Cuántos pasos, campos u opciones; qué se revela y cuándo | `filey-ux` |
| Convertir el markup en plantilla servida o HTML del prototipo | `filey-render` |

**Tesis única de este skill: reusar antes de escribir.** Las tres economías que persigue —
menos tokens CSS, menos markup duplicado, menos contexto consumido — fallan por la misma
causa (no saber qué ya existe) y se resuelven con el mismo artefacto: el inventario.

---

## 1. Protocolo de lectura barata

Antes de escribir una línea de CSS o markup, en este orden. **No saltes al paso 4.**

| # | Paso | Costo |
| --- | --- | --- |
| 1 | [references/inventario.md](references/inventario.md) — busca la clase o el token por nombre | ~1 lectura |
| 2 | Si aparece: abre el `.css` **en el rango de líneas** que da la columna *línea* (`offset`/`limit`) | ~30 líneas |
| 3 | Si necesitas ver el componente usado: `grep -l "nombre-clase" prototipo/` y abre **una** pantalla | 1 archivo |
| 4 | Solo si nada aplica: escribe CSS nuevo, siguiendo la sección 3 | — |

Reglas duras:

- **Nunca leas un `styles.css` completo** para "ver qué hay". Para eso está el inventario.
- **Nunca leas un HTML completo** para copiar un patrón: `grep -n` la clase y lee ±20 líneas.
- Edita con `Edit` puntual. Reescribir un archivo entero con `Write` para cambiar tres reglas
  gasta el archivo dos veces (leerlo + escribirlo) y pierde el resto del contenido de vista.
- El inventario es **generado**: si lo notas desactualizado, corre `./prototipo/scripts/gen-inventario.sh`;
  no lo edites a mano.

---

## 2. Las capas

```
prototipo/common/styles-base.css     Capa common — tokens y componentes de TODOS los dominios
prototipo/{DOM}/styles.css           Capa dominio — @import de common + lo propio del dominio
```

> [!warning] Existe una segunda copia fuera del prototipo
> El monolito Django tiene su propia hoja, `filey/estaticos/css/filey.css`: una copia a mano
> de estas dos capas, con los mismos nombres de token, que **ya derivó** (le faltan 16 tokens
> y conserva uno muerto). No es una tercera capa; es una segunda fuente que hay que mantener
> a mano. Si tocas un token o un componente compartido, propágalo. Detalle y lista de la
> deriva en el skill `filey-render`, sección 6.

Dentro del prototipo no hay tercera capa. **El CSS de un dominio vive en un único archivo**,
sin importar el rol:
nunca `{DOM}/administradores/algo.css`. Si un componente solo lo usa admin, lo indica su
**nombre** (`.vis-adm-nav`, `.evt-admin-sidebar`), no su ubicación.

Tampoco hay CSS en bloques `<style>` de un HTML. Hay 418 líneas de deuda ahí; `check-ui.sh`
las cuenta con trinquete y falla si crecen.

## 3. Dónde va un componente nuevo

```
¿Existe ya algo parecido en el inventario?
  Sí, idéntico          → reúsalo, no lo copies
  Sí, difiere solo en color/tamaño → añade un modificador (.is-x, .banner-x)
  Sí, difiere en layout → componente nuevo (sigue abajo)
  No                    → componente nuevo (sigue abajo)

¿Lo usarán 2 o más dominios?
  Sí → capa common, nombre genérico y sin prefijo de dominio
  No → capa dominio, prefijo .{dom}- en la clase y --{dom}- en los tokens
```

**Promover** (dominio → common): cuando la columna *usada en* del inventario nombra dos o más
dominios y la clase **solo** está definida en una capa de dominio. Que aparezca en `common`
*y* en un dominio no es duplicado: es un override intencional.

**Degradar** (common → dominio): cuando la columna *usada en* nombra un solo dominio y la
clase depende de tokens propios de ese dominio.

**Borrar:** columna *usada en* = `—`. Confirma con `grep -r` antes de quitarla.

## 4. Tokens CSS

1. Un token nuevo se justifica solo si el valor se repite o tiene significado semántico.
   Un color usado una vez en un solo lugar es candidato a **no** ser token — pero tampoco a
   ser hex suelto: revisa primero si un token existente sirve.
2. Nombre semántico por rol, nunca por apariencia: `--vis-cupos-lleno`, no `--gris-oscuro-2`.
3. Tokens de dominio llevan prefijo `--{dom}-` y viven en el `:root` del `styles.css` del dominio.
4. Los nombres canónicos de color llevan prefijo `--color-`. No existen `--blanco`,
   `--azul-900`, `--azul-700`, `--gris-600`, `--oro-600`, `--azul-300`, `--azul-400`:
   si los ves en el código, son referencias rotas heredadas de un `admin.css` ya borrado.

## 5. Markup

- Cero `style="..."` inline. Hay 221 de deuda, bajo trinquete: si crece, `check-ui.sh` falla.
- Una pantalla nueva **se parte de una existente parecida**, no de cero. Localízala con
  `grep -l` sobre la clase del patrón que necesitas.
- Clases de estado: `.is-active`, `.is-invalid`, `.is-admin`. No inventes sinónimos
  (`.activo`, `.selected`).

## 6. Dos trampas que ya costaron tiempo

### `[hidden]` no gana contra una clase que fija `display`

El atributo `hidden` vale `display: none` **en la hoja del navegador**, así que cualquier regla
de autor con `display` lo pisa. Pasa con `.btn` (`inline-flex`), `.grid-2` (`grid`) y cualquier
componente que declare el suyo: se pone `hidden`, no se esconde nada, y no hay error que lo
avise.

El proyecto lo resuelve con una regla **acotada al componente**, no con un `!important` global:

```css
.btn[hidden] { display: none; }
.grid-2[hidden], .grid-3[hidden] { display: none; }
```

Antes de esconder algo con `hidden`, mira en el inventario si su clase fija `display`.

### La regla amplia alcanza al hijo que no querías

`.evt-institucion input { flex: 1 }` alcanzaba también a la casilla que vive **dentro** del
rótulo: se estiraba y empujaba su propia etiqueta lejos. El síntoma se lee como un problema de
maquetación y es un selector de más.

Con hijo directo cuando el contenedor tiene controles anidados: `.evt-institucion > input`.

## 7. Pseudo-elementos

`::before` y `::after` crean una caja anónima como primer o último hijo, y **no se pintan sin
`content`** —aunque sea `content: ''`—. Sirven para tres cosas en este proyecto:

1. **Adorno que no es contenido.** El punto del `.badge`, el caret del `.select-wrap` (con
   `mask-image` y data-URI, ver §6 de este skill). Nada de esto lo lee un lector de pantalla, y
   está bien: es decoración.
2. **Agrandar el objetivo sin ensuciar el HTML.** Es la herramienta de Fitts cuando el control
   es pequeño y no se puede agrandar visualmente —una `×` de cerrar, un «Quitar»—:

   ```css
   .evt-persona__quitar { position: relative; }
   .evt-persona__quitar::after {
     content: ''; position: absolute; inset: -10px;   /* área pulsable, invisible */
   }
   ```

3. **Estado sin marcado extra.** `.check-chip input:checked + .chip::before { content: "✓ "; }`.

> [!warning] Nunca metas ahí texto que haga falta leer
> Lo que va en `content` no está en el DOM, no se puede seleccionar ni copiar, y los lectores
> de pantalla lo tratan de forma inconsistente. Un mensaje de error, un rótulo o un dato van en
> el HTML; en `content` solo lo que se pueda quitar sin perder información.

## 8. SVGs

1. Los assets viven en `prototipo/common/assets/`. Solo van a `{DOM}/assets/` si tienen
   variante visual exclusiva que `currentColor` no resuelve.
2. El elemento `<svg>` **no lleva `width` ni `height`** — solo `viewBox` y
   `fill="currentColor"`. El tamaño lo fija CSS. Lo verifica `check-ui.sh` (E2).
3. Para escalar: token para el eje controlador, el otro con `calc()` usando el ratio del
   `viewBox` (`viewBox="0 0 W H"`):

   ```css
   --vis-dia-btn-size: 16px;

   .vis-dia-btn svg {
     display: block;
     height: var(--vis-dia-btn-size);
     width: calc(var(--vis-dia-btn-size) * 26 / 30);  /* W / H del viewBox */
   }
   ```

   No uses `width: auto`: el `calc()` documenta el ratio y es inequívoco en cualquier contexto
   de layout.
4. Para `mask-image` (patrón del caret): embebe el SVG como data-URI en un token de
   `common/styles-base.css`. Un `url()` a un `.svg` externo falla en `file://`.

## 9. Responsive

Un solo breakpoint: `@media (max-width: 920px)`. Ahí el hero de login se oculta y los grids
colapsan a una columna. No introduzcas breakpoints nuevos sin una razón que no se resuelva
con `flex-wrap` o `minmax()`.

---

## 10. Añadir un dominio nuevo

1. `prototipo/{DOM}/` con subcarpetas `aplicantes/` y `administradores/` (ver `filey-render`).
2. `{DOM}/styles.css` con una sola línea: `@import '../common/styles-base.css';`
3. Tokens de acento del dominio en su `:root`, con prefijo `--{dom}-` (el color lo dicta
   `filey-identidad`).
4. Si su tarjeta aparece en la pantalla de convocatorias de REG, añade `.banner-{dom}` en
   `common/`.
5. Corre `./prototipo/scripts/gen-inventario.sh` para que el dominio entre al índice.

---

## 11. Checklist — ejecutable, no de memoria

```bash
./prototipo/scripts/gen-inventario.sh   # reindexa tras tocar cualquier styles.css
./prototipo/scripts/check-ui.sh         # E1 var() rotos · E2 svg con width/height · E3 hex suelto
                              # W1 inline · W2 clase sin CSS · W4 <style> embebido (trinquete)
```

Si bajaste deuda, fija el nuevo techo con `./prototipo/scripts/check-ui.sh --baseline` y comitea
`prototipo/scripts/.ui-baseline`.

A mano solo queda lo que un script no puede juzgar:

- [ ] La clase que usaste salió del inventario, no de la memoria
- [ ] El componente nuevo está en la capa correcta según la sección 3
- [ ] La pantalla se derivó de una existente parecida
- [ ] Nada que se esconda con `hidden` lleva una clase que fije `display` (§6)
