---
tipo: analisis
fecha: 2026-07-02
scope: skill filey-ui-look-and-feel
---

# Análisis de ajuste de la skill `filey-ui-look-and-feel`

Evaluación de qué tan bien sirve la skill para recrear el look & feel del
prototipo en **cualquier módulo** (REG, EVT, VIS, STD), incluyendo la capacidad
de entender la arquitectura CSS compartida/específica, gestionar la migración
de componentes entre capas, y manejar SVGs escalables.

---

## 1. Arquitectura real del prototipo (lo que la skill debe entender)

```text
prototipo/
  common/
    styles-base.css        ← base canónica compartida (tokens + shell + todos
    assets/                  los componentes comunes: topbar, forms, cards,
      caret.svg              botones, badges, auth, layout, tablas, notas...)
      next-day.svg
      prev-day.svg
  REG/
    styles.css             ← solo: @import '../common/styles-base.css'
  EVT/
    styles.css             ← solo: @import '../common/styles-base.css'
    administradores/
      admin.css            ← ⚠ DEUDA TÉCNICA: CSS en subcarpeta de rol, viola la
                              política (ver sección política de archivos abajo)
  VIS/
    styles.css             ← @import + ~330 líneas de tokens y componentes VIS
  STD/
    src/styles.scss        ← Angular Material — fuera de alcance de esta skill
```

**Política de estructura de archivos por dominio** (canónica, todo dominio nuevo
debe seguirla):

```text
{DOM}/
  aplicantes/      ← HTMLs usados solo por aplicantes
  administradores/ ← HTMLs usados solo por administradores
  styles.css       ← CSS ÚNICO del dominio, compartido para ambos roles
  *.html           ← HTMLs usados por ambos roles (raro)
```

- El CSS del dominio **siempre** vive en `{DOM}/styles.css`, sin importar el rol.
- Los nombres de componentes dentro del CSS pueden indicar el rol si ese componente
  solo lo usa uno de los dos (`.vis-admin-stats`, `.evt-admin-sidebar`), pero el
  archivo en sí nunca se subcarpetea por rol.
- HTMLs compartidos por ambos roles (login, pantalla de bienvenida) van en `{DOM}/`
  directamente.

La bifurcación del flujo es:

```text
REG (acceso + convocatorias)
  └── aplicantes → EVT/aplicantes · VIS/aplicantes · TAL/aplicantes · STD
  └── admin      → EVT/administradores · VIS/administradores · TAL/administradores
```

**Lo que la skill afirma vs. la realidad:**

| Afirmación de la skill                                              | Realidad                                                                                                           |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Fuente canónica: `prototipo/REG - EVT/styles.css`                   | Esa ruta **no existe**. La canónica es `prototipo/common/styles-base.css`                                          |
| "Inventario de componentes reutilizables" → solo cubre REG-EVT      | Todos los componentes comunes ya están en `common/`; VIS añade ~30 clases propias                                  |
| Menciona STD como "fuera de scope"                                  | Correcto, pero la skill no menciona que EVT tiene un sub-CSS de admin (`admin.css`) ni que VIS no lo tiene         |
| Cuatro patrones no negociables (login, conv-card, bento, proto-bar) | Los cuatro están en `common/`; la skill no sabe que en VIS el bento es distinto (`.vis-bento`, no `.section-card`) |

---

## 2. Diagnóstico por área de uso

### 2.1 Para recrear pantallas de REG o EVT (usuario)

**Estado: funciona razonablemente bien**, porque REG y EVT no añaden CSS propio.
Todo viene de `common/styles-base.css`, que la skill cubre (aunque con el nombre
incorrecto). Un agente que siga la skill producirá componentes correctos para
estas dos rutas.

**Problema latente:** si en el futuro REG o EVT necesitan sobrescrituras propias,
no existe guía en la skill sobre cómo estructurarlas. El agente podría meter
estilos directamente en `common/` en lugar de en el `styles.css` de dominio.

### 2.2 Para recrear pantallas del admin de EVT

**Estado: sin cobertura.** `EVT/administradores/admin.css` tiene ~260 líneas
propias (sidebar, modal de dictamen, calendario, rejilla de horario, chip de
filtro, stat-card con accent, diálogo de nuevo evento). La skill no menciona este
sub-CSS ni sus componentes. Un agente que cree una pantalla nueva del admin EVT
los inventará desde cero o los copiará incorrectamente.

Además, `admin.css` usa nombres de token ligeramente distintos (`--blanco`,
`--azul-institucional`, `--azul-800`, `--azul-900`) que no existen en
`common/styles-base.css`. Hay **divergencia de nombres de token entre
`admin.css` y `common/`** que la skill no detecta ni documenta.

### 2.3 Para recrear pantallas de VIS

**Estado: sin cobertura específica.** La skill trata a VIS como si fuera
idéntico a REG-EVT. `VIS/styles.css` extiende `common/` con ~30 componentes
propios que no están en ninguna referencia de la skill.

### 2.4 Para recrear pantallas de TAL o de futuras convocatorias

**Estado: depende de si el dominio tiene CSS propio o no.** La skill no tiene
ningún mecanismo para saber cuándo un dominio nuevo hereda solo de `common/` vs.
cuándo necesita CSS propio. El agente tendrá que inferirlo o preguntar.

### 2.5 Para gestionar SVGs

**Estado: deficiente.** Ver sección 4.

---

## 3. Problemas de la skill que afectan a todos los dominios

### P1 — Ruta de la fuente canónica incorrecta

La skill dice: *"Layout y tokens canónicos: `prototipo/REG - EVT/styles.css`"*.
Esa ruta no existe. El archivo correcto es `prototipo/common/styles-base.css`.
Cualquier agente que siga la instrucción literal fallará al buscar la fuente de
verdad.

### P2 — No distingue capas: `common` vs. dominio

La skill trata el CSS del prototipo como si fuera un solo archivo monolítico. No
explica la jerarquía de dos (o tres) capas:

```text
Layer 1 — common/styles-base.css    (compartido, no modificar sin justificar)
Layer 2 — {dominio}/styles.css      (específico del dominio, extiende Layer 1)
Layer 3 — {dominio}/{sub}/admin.css (sub-contexto, extiende Layer 2)
```

Sin esta distinción, un agente no sabe dónde poner un componente nuevo, y puede
contaminar `common/` con algo que solo necesita un dominio.

### P3 — No tiene reglas de migración de componentes

La skill no le dice al agente cuándo debe **promover** un componente (moverlo de
un `styles.css` de dominio a `common/`) ni cuándo debe **degradarlo** (sacarlo
de `common/` porque solo un dominio lo usa). Sin estas reglas, `common/`
acumula componentes de dominio y los `styles.css` individuales se duplican.

### P4 — Checklist solo válido para REG-EVT usuario

Las preguntas del checklist pre-entrega están orientadas a convocatorias y
formularios de REG-EVT: `.conv-card`, `.section-head .num`, `.proto-bar`.
Para VIS (catálogo, itinerario, tabla admin), un agente podría marcar todo como
✔ aunque el resultado no tenga ningún componente VIS correcto.

### P5 — El inventario de componentes mezcla "comunes" con "patrones de REG-EVT"

`references/componentes.md` lista `.auth-wrap` (común a todos), `.conv-card`
(común) y `.section-card` (común), pero también `.conv-banner` con sus variantes
(`banner-stand`, `banner-infantil`, `banner-eventos`), que son semi-específicos.
No diferencia cuáles son universales y cuáles son de dominio. Un agente que crea
una tarjeta de convocatoria VIS podría usar `.banner-visitas` (que ya existe en
`common/`) o podría crear `.vis-banner` — sin guía clara, hace cualquier cosa.

### P6 — Sin política de organización de archivos por rol

La skill no documenta dónde va un HTML nuevo según el rol que lo usa, ni que el
CSS del dominio no debe subcarpetearse. Sin esta guía, un agente puede:

- Poner HTMLs de admin en la raíz del dominio junto con los de aplicante.
- Crear un `{DOM}/administradores/styles.css` o `{DOM}/aplicantes/styles.css`
  en vez de un único `{DOM}/styles.css`.
- Copiar el patrón de `EVT/administradores/admin.css` como si fuera canónico.

**Deuda técnica de EVT:** `EVT/administradores/admin.css` viola la política porque
es CSS dentro de una subcarpeta de rol. Hasta que se refactorice, la skill debe
documentarlo explícitamente como excepción pre-política, no como patrón a replicar.

---

## 4. SVGs: problemas y propuesta

### Estado actual

| Archivo                      | Tiene `width`/`height` hardcodeados | Usa `fill="currentColor"` | Escalable via CSS |
| ---------------------------- | ----------------------------------- | ------------------------- | ----------------- |
| `common/assets/caret.svg`    | No (solo `viewBox`)                 | Sí                        | Sí ✔              |
| `common/assets/next-day.svg` | **Sí** (`width="26" height="30"`)   | Sí                        | No ✗              |
| `common/assets/prev-day.svg` | Probablemente sí (mismo origen)     | Sí                        | No ✗              |
| SVGs en `skills/.../assets/` | Varios con `width`/`height`         | Mixto                     | Mixto             |

El caret SVG usa `mask-image` (embebido como data-URI en `common/styles-base.css`),
así que su tamaño lo controlan dos valores fijos (`width: 11px; height: 6px` en
`.select-wrap::after`). Para ese patrón concreto, valores fijos son aceptables porque
el caret es un detalle de UI de tamaño invariable.

Los botones prev/next del selector de día son el **modelo correcto** para SVGs de
ícono escalables. El SVG declara solo `viewBox="0 0 26 30"` (sin `width`/`height`),
y en `VIS/styles.css`:

```css
.vis-dia-btn svg {
  display: block;
  height: var(--vis-dia-btn-size);          /* eje controlador */
  width: calc(var(--vis-dia-btn-size) * 26 / 30); /* W/H del viewBox */
}
```

Los valores `26` y `30` se leen directamente del `viewBox` del SVG. Este es el
tratamiento esperado para **todos** los SVGs de ícono: primero derivar el aspect
ratio del `viewBox`, después expresarlo en el `calc()`.

### Reglas SVG que la skill debe documentar

**Regla 1 — No poner `width`/`height` en el elemento `<svg>` de assets.**
El tamaño lo fija CSS, no el archivo. El `viewBox` es lo único obligatorio en el
`<svg>`.

```xml
<!-- ✗ Incorrecto: dimensiones hardcodeadas -->
<svg width="26" height="30" viewBox="0 0 26 30" ...>

<!-- ✔ Correcto: solo viewBox; CSS controla el tamaño -->
<svg viewBox="0 0 26 30" ...>
```

**Regla 2 — Usar `fill="currentColor"` (o `stroke="currentColor"`) para heredar
el color del contexto CSS.**
Esto permite cambiar el color del ícono con `color: var(--algún-token)` en el
padre, sin tocar el SVG.

**Regla 3 — Para controlar el tamaño de un SVG de ícono: derivar el aspect ratio
del `viewBox`, definir un token para el eje controlador (generalmente `height`),
y calcular el otro eje con `calc()`.**

Proceso:

1. Leer el `viewBox` del SVG: `viewBox="0 0 W H"` → ancho natural W, alto natural H.
2. Definir un token para el tamaño: `--mi-icono-size: 16px`.
3. Aplicar en CSS:

```css
.mi-elemento svg {
  display: block;
  height: var(--mi-icono-size);
  width: calc(var(--mi-icono-size) * W / H);
}
```

Ejemplo real (prev/next día, `viewBox="0 0 26 30"`):

```css
--vis-dia-btn-size: 16px;

.vis-dia-btn svg {
  display: block;
  height: var(--vis-dia-btn-size);
  width: calc(var(--vis-dia-btn-size) * 26 / 30);
}
```

Este tratamiento se aplica a **cualquier SVG** que deba escalarse: iconos en botones,
badges, encabezados, etc. No usar `width: auto` — el `calc()` explícito documenta
el ratio y es inequívoco en todos los contextos de layout.

**Regla 4 — Para SVGs usados como `mask-image` (patrón del caret), embeber como
data-URI en el token CSS.**
El `@import` de un `.svg` externo falla en `file://` por CORS. El patrón correcto:

```css
:root {
  --icono-caret: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'
    viewBox='0 0 826 374' fill='currentColor'%3E...%3C/svg%3E");
}
```

Y usar con `mask-image: var(--icono-caret); mask-size: contain;`. El color lo
da `background-color` de la pseudo-clase.

**Regla 5 — Para SVGs referenciados como assets (`<img src="...svg">`) en HTML,
referenciar la ruta relativa desde `common/assets/`.**
Nunca duplicar el SVG en cada carpeta de dominio.

---

## 5. Reglas de migración de componentes entre capas

La skill debe incorporar un algoritmo de decisión que el agente pueda ejecutar
antes de añadir o modificar CSS:

### ¿Dónde va un componente nuevo?

```text
¿Lo usará más de un dominio (REG, EVT, VIS, TAL)?
  Sí → va a common/styles-base.css, con nombre genérico
  No → va al styles.css del único dominio que lo usa

¿Es una variación de un componente ya en common/?
  Sí, variación por token (color/tamaño) → añadir modificador (.is-vis, .banner-visitas)
    en common/ o en el styles.css del dominio, según cuántos dominios la necesiten
  Sí, variación estructural (layout diferente) → componente nuevo en el styles.css del dominio
  No → componente nuevo en el styles.css del dominio

¿Es solo para el sub-contexto admin?
  Sí → va al sub-CSS admin (ej. EVT/administradores/admin.css), no a common/
```

### ¿Cuándo promover de dominio a `common/`?

Un componente de dominio debe moverse a `common/` cuando:

- Se necesita en un segundo dominio (regla del "segundo usuario").
- La copia en ambos dominios empieza a divergir sin motivo funcional.

Señales de que hay que promover: el agente encuentra la misma clase en dos
`styles.css` de dominio distintos con CSS casi idéntico.

### ¿Cuándo degradar de `common/` a dominio?

Un componente de `common/` debe bajarse al `styles.css` del único dominio que lo
usa cuando:

- Solo un dominio lo referencia (confirmado con `grep -r "nombre-clase" prototipo/`).
- El componente tiene dependencias de tokens de un dominio específico.

Señal de que hay que degradar: el agente descubre que una clase en `common/` solo
aparece en los HTMLs de un solo dominio y usa tokens propios de ese dominio.

### ¿Cuándo mover un SVG de `common/assets/` a un directorio de dominio?

Moverlo a `{dominio}/assets/` solo si:

- El SVG tiene variante de color o forma distinta por dominio (y no puede
  resolverse con `fill="currentColor"`).
- El SVG nunca se usa fuera de ese dominio.

En todos los demás casos, el SVG vive en `common/assets/`.

---

## 6. Mejoras propuestas a la skill

### M1 — Corregir la ruta de la fuente canónica [Alta]

Cambiar:

```text
prototipo/REG - EVT/styles.css (variables en :root)
```

por:

```text
prototipo/common/styles-base.css  ← fuente canónica para TODOS los dominios
{dominio}/styles.css              ← extensión por dominio (importa common y añade lo propio)
{dominio}/{sub}/admin.css         ← sub-contexto opcional (solo EVT lo tiene hoy)
```

### M2 — Documentar la jerarquía de capas CSS [Alta]

Añadir al inicio de la skill una tabla que muestre qué archivo leer antes de
crear cualquier pantalla:

| Tipo de pantalla                    | Leer primero             | Leer después                            |
| ----------------------------------- | ------------------------ | --------------------------------------- |
| Login / acceso (REG)                | `common/styles-base.css` | `REG/styles.css` (vacío hoy)            |
| Convocatorias usuario (EVT/usuario) | `common/styles-base.css` | `EVT/styles.css` (vacío hoy)            |
| Panel admin (EVT/admin)             | `common/styles-base.css` | `EVT/administradores/admin.css`         |
| Visitas escolares (VIS)             | `common/styles-base.css` | `VIS/styles.css`                        |
| Admin VIS                           | `common/styles-base.css` | `VIS/styles.css` (incluye clases admin) |
| STD                                 | —                        | Fuera de alcance (Angular Material)     |

### M3 — Crear `references/componentes-comunes.md` y `references/componentes-vis.md` [Alta]

Separar el inventario actual de componentes en dos archivos:

**`componentes-comunes.md`** — lo que está en `common/styles-base.css` y aplica
a todos los dominios: `.topbar`, `.auth-wrap`, `.section-card`, `.conv-card`,
`.btn-*`, `.badge-*`, `.note-*`, `.confirm-card`, `.proto-bar`, etc.

**`componentes-vis.md`** — lo que está exclusivamente en `VIS/styles.css`:  
`.vis-banner`, `.vis-bento`, `.vis-cupo`, `.vis-grupo-card`, `.vis-grupo-badge`,
`.vis-horario-*`, `.vis-itin-*`, `.vis-reserva-bar`, `.vis-ficha`, `.vis-stats`,
`.vis-tabla`, `.vis-filters`, `.grupo-block`, `.total-box`, etc.

> Cuando exista TAL, crear un `componentes-tal.md` equivalente con la misma
> estructura.

### M4 — Añadir las reglas de migración (sección 5 de este análisis) [Alta]

El agente debe saber tomar la decisión de dónde pone un componente nuevo sin
preguntar siempre. Las reglas de la sección 5 deben estar en la skill como
una sección propia.

### M5 — Añadir las reglas SVG (sección 4) [Media]

Incluir en la skill las 5 reglas de la sección 4, con énfasis en:

- No poner `width`/`height` en el `<svg>`.
- Usar `height: 1em; width: auto` en CSS para respetar el aspect ratio.
- Cómo actualizar `next-day.svg` y `prev-day.svg` para quitar los atributos hardcodeados y actualizar el CSS de VIS para usar `width: auto`.

### M6 — Dividir el checklist por tipo de pantalla [Media]

Mantener el checklist actual como "checklist REG-EVT" y añadir un "checklist VIS":

**Checklist VIS:**

- [ ] Los tokens verdes usan `--color-verde-*` (de `common/`) o `--vis-*` (de `VIS/styles.css`), no hex sueltos
- [ ] El banner de convocatoria usa `.vis-banner` (no `.conv-card`)
- [ ] Las secciones de info usan `.vis-bento` con `.vis-bento__num` (verde, no azul)
- [ ] Las fichas de datos usan `.vis-ficha > .vis-ficha__grid`
- [ ] Los grupos son `.vis-grupo-card` dentro de `.vis-grupos-row`
- [ ] El catálogo usa `.vis-horario-container > .vis-horario-header + .vis-horario-wrap`
- [ ] Los SVGs de botones prev/next son `<svg>` inline o `<img>` desde `common/assets/`, sin `width`/`height` hardcodeados en el elemento

**Checklist admin EVT:**

- [ ] El shell usa `.admin-body > .sidebar + .admin-main`
- [ ] Los chips de filtro son `.chip` + `.is-active` (no `.badge`)
- [ ] Los modales de dictamen usan `.modal > .modal-head + .modal-body + .modal-foot`
- [ ] Las stat-cards usan `.stat-card` + `.accent-{color}`
- [ ] Los tokens usados coinciden con los de `common/` (no usar `--blanco` ni `--azul-900` — esos son divergencias en `admin.css` que deben corregirse)

### M7 — Documentar la divergencia de tokens en `admin.css` [Media]

`EVT/administradores/admin.css` usa nombres de token que no existen en
`common/styles-base.css`:

| Token en `admin.css`       | Equivalente correcto en `common/`                     |
| -------------------------- | ----------------------------------------------------- |
| `--blanco`                 | `--color-blanco`                                      |
| `--azul-institucional`     | `--color-azul-institucional`                          |
| `--azul-800`, `--azul-900` | No existen; usar `--color-azul-institucional-enfoque` |
| `--azul-700`               | `--azul-600` (el más cercano en `common/`)            |
| `--oro-600`, `--oro-700`   | `--color-dorado-encabezado`, `--color-dorado-700`     |

La skill debe señalar esta divergencia como **deuda técnica conocida** y
prohibir al agente crear CSS nuevo que use los nombres incorrectos de `admin.css`.
Si el agente necesita un token que no existe en `common/`, debe añadirlo ahí
con nombre semántico antes de usarlo.

### M8 — Añadir guía para agregar un nuevo dominio [Baja]

Cuando llegue TAL (Talleres) u otro dominio, el agente debe saber qué hacer
sin invención. Añadir una mini-guía:

```markdown
## Agregar un dominio nuevo

1. Crear `prototipo/{DOMINIO}/styles.css` con la línea:
   @import '../common/styles-base.css';
2. Si el dominio tiene color de acento propio, añadir los tokens `--{dom}-*`
   en `:root` dentro de `{DOMINIO}/styles.css`.
3. Añadir variantes de `.conv-banner` y `.banner-{dom}` en `common/` si la
   tarjeta de convocatoria del dominio aparece en la pantalla compartida de
   convocatorias de REG.
4. Crear `references/componentes-{dom}.md` al final del desarrollo.
5. Si el dominio tiene pantallas de admin con layout propio (sidebar, etc.),
   crear `{DOMINIO}/{sub}/admin.css` que importa `../{DOMINIO}/styles.css`.
6. Copiar el checklist VIS como base para el checklist del nuevo dominio.
```

---

## 7. Priorización

| Mejora                                             | Impacto                                                       | Esfuerzo                   | Prioridad  |
| -------------------------------------------------- | ------------------------------------------------------------- | -------------------------- | ---------- |
| M1 — Corregir ruta canónica                        | Alto: elimina el error más grave                              | Mínimo (1 línea)           | 🔴         |
| M2 — Tabla de capas CSS                            | Alto: orienta al agente ante cualquier nueva pantalla         | Bajo (tabla + 10 líneas)   | 🔴         |
| M3 — Inventario componentes comunes / VIS          | Alto: elimina la principal causa de clases inventadas         | Medio (2 archivos)         | 🔴         |
| M4 — Reglas de migración                           | Alto: evita que `common/` se contamine o se dupliquen estilos | Bajo (lista de decisiones) | 🔴         |
| M5 — Reglas SVG                                    | Medio: evita workarounds de aspect ratio y SVGs no escalables | Bajo                       | 🟡         |
| M6 — Checklists por tipo de pantalla               | Medio: valida el resultado de forma pertinente por dominio    | Bajo                       | 🟡         |
| M7 — Documentar divergencia de tokens en admin.css | Medio: evita propagar nombres incorrectos                     | Mínimo (tabla)             | 🟡         |
| M8 — Guía para nuevo dominio                       | Bajo a corto plazo; alto cuando llegue TAL                    | Bajo                       | 🟢         |

[Alta]: <>
[Media]: <>
[Baja]: <>
