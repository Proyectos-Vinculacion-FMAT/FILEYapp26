---
name: filey-ui-look-and-feel
description: Usa este skill cuando generes, edites o revises pantallas HTML/CSS/JS estáticas de cualquier prototipo FILEY/UADY (REG, EVT, VIS, TAL) y necesites mantener consistencia visual con la identidad institucional: login, tarjetas de convocatoria, bento numerado, botones, badges, catálogos, formularios, paneles de admin. No cubre componentes Angular de prototipo/STD.
---

# FILEY/UADY — look & feel para prototipos HTML

## Estructura de archivos por dominio

Cada dominio sigue este layout. Leerlo antes de crear o mover cualquier archivo:

```
prototipo/{DOM}/
  aplicantes/          ← HTMLs usados exclusivamente por aplicantes (usuarios normales)
  administradores/     ← HTMLs usados exclusivamente por administradores
  styles.css           ← CSS ÚNICO del dominio, compartido para ambos roles
  *.html               ← HTMLs usados por AMBOS roles (raro; solo si aplica)
```

**Reglas de enrutado de HTMLs:**

| ¿Quién usa la pantalla? | Dónde va el `.html` |
| ----------------------- | ------------------- |
| Solo aplicantes | `{DOM}/aplicantes/{pantalla}.html` |
| Solo administradores | `{DOM}/administradores/{pantalla}.html` |
| Ambos roles | `{DOM}/{pantalla}.html` |

**Reglas de CSS:**

- El CSS del dominio **siempre** vive en `{DOM}/styles.css`. Nunca en `{DOM}/administradores/` ni en `{DOM}/aplicantes/`.
- Los nombres de componentes dentro del CSS pueden indicar el rol si ese componente solo lo usa uno de los dos (`--evt-admin-sidebar`, `.vis-admin-stats`). El archivo en sí no se subcarpetea.
- **Deuda técnica conocida:** `EVT/administradores/admin.css` viola esta política — es CSS dentro de una subcarpeta de rol. El contenido debe migrarse a `EVT/styles.css` cuando se refactorice EVT.

---

## Arquitectura CSS (capas)

Los prototipos tienen **dos capas de CSS**. Siempre leer en este orden:

| Capa | Archivo | Qué contiene |
| ---- | ------- | ------------ |
| 1 — Base compartida | `prototipo/common/styles-base.css` | Tokens globales (`:root`), topbar, auth, layout, forms, cards, botones, badges, notas, footer, responsive. Aplica a **todos** los dominios. |
| 2 — Específico de dominio | `prototipo/{DOM}/styles.css` | `@import '../common/styles-base.css'` + tokens y componentes propios del dominio. Cubre pantallas de aplicantes Y administradores. |

**Tabla por tipo de pantalla:**

| Pantalla | CSS a cargar |
| -------- | ------------ |
| Login / acceso (REG) | `common/styles-base.css` ← vía `REG/styles.css` |
| Convocatorias usuario (EVT) | `common/styles-base.css` ← vía `EVT/styles.css` |
| Panel admin EVT *(legacy)* | `EVT/administradores/admin.css` (también carga `EVT/styles.css`; deuda técnica) |
| Cualquier pantalla VIS (aplicante o admin) | `VIS/styles.css` |
| TAL (futuro) | `TAL/styles.css` (crear con solo el import) |

Si la tarea pide tocar `prototipo/STD` o `prototipo/common/` de forma que afecte a todos los dominios simultáneamente, avisa al usuario antes de proceder.

---

## Fuentes de referencia

1. **Base canónica:** `prototipo/common/styles-base.css` — tokens en `:root`, todos los componentes compartidos. Si una pantalla nueva se parece a una existente, copia su estructura en vez de inventar una nueva.
2. **Componentes comunes** (en `common/`): [references/componentes-comunes.md](references/componentes-comunes.md)
3. **Componentes VIS** (en `VIS/styles.css`): [references/componentes-vis.md](references/componentes-vis.md)
4. **Identidad institucional** (paleta, tipografía, marca): [references/identidad-institucional.md](references/identidad-institucional.md). No vuelvas a hacer scraping de filey.org — actualiza ese archivo solo si el usuario lo pide.

---

## Reglas no negociables

### Tokens CSS

1. Usa variables de `common/styles-base.css`. Nunca escribas un hex suelto en una regla. Los nombres correctos usan el prefijo `--color-`:
   - `--color-azul-institucional`, `--color-dorado-encabezado`, `--color-blanco`, etc.
   - Tokens semánticos: `--ok-*`, `--warn-*`, `--err-*`, `--radio`, `--radio-sm`, `--sombra-sm/md/lg`
2. Si falta un token, agrégalo en `:root` del `styles.css` del dominio (no en `common/`) con nombre semántico. Para VIS usa prefijo `--vis-*`.
3. **Bug conocido en `EVT/administradores/admin.css`:** ese archivo usa `--blanco`, `--azul-institucional`, `--azul-800`, `--azul-900` (sin prefijo `--color-`). Esos tokens no existen en `common/`. No propagues esos nombres en código nuevo; usa los correctos de `common/`.

### Componentes

4. Conserva estos 4 patrones sin reinventar su estructura:
   - Login: `.auth-wrap` → `.auth-hero` + `.auth-form`
   - Tarjeta de convocatoria: `.conv-card` → `.conv-banner` + `.conv-body` + `.conv-foot`
   - Bento numerado: `.section-card > .section-head (.num + h3) + .section-body`
   - Aviso de prototipo: `.proto-bar > .proto-bar-inner`
5. Botones: `.btn` + modificador existente (`.btn-primary`, `.btn-gold`, `.btn-ghost`, `.btn-special`, `.btn-danger`, `.btn-sm`). Sin estilos de botón inline.
6. Badges de estado: `.badge` + variante existente (`-open/-closed/-soon/-pending/-accepted/-rejected/-changes`). Para estados nuevos, mapea a tokens `--ok-*`/`--warn-*`/`--err-*`.
7. Links: fondo claro → `a { color: var(--color-azul-700) }` (ya definido en common). Fondo azul oscuro → `var(--link-azul-fondo)`. Nunca un link sin hover distinguible.
8. Responsive: un solo breakpoint en `@media (max-width: 920px)` — el hero de login se oculta, los grids colapsan a 1 columna.

### SVGs

9. Los archivos SVG en `common/assets/` **no deben tener `width`/`height` en el elemento `<svg>`**. Solo `viewBox` + `fill="currentColor"`. El tamaño lo fija CSS.
10. Para controlar el tamaño de un SVG de ícono: leer el `viewBox` del archivo (`viewBox="0 0 W H"`), definir un token para el eje controlador y calcular el otro con `calc()` usando el ratio W/H extraído del `viewBox`:
    ```css
    /* 1. Definir token (en :root del styles.css del dominio) */
    --mi-icono-size: 16px;

    /* 2. Aplicar — W y H son los valores del viewBox del SVG */
    .mi-elemento svg { display: block; height: var(--mi-icono-size); width: calc(var(--mi-icono-size) * W / H); }
    ```
    Ejemplo real (prev/next día, `viewBox="0 0 26 30"`):
    ```css
    --vis-dia-btn-size: 16px;
    .vis-dia-btn svg { display: block; height: var(--vis-dia-btn-size); width: calc(var(--vis-dia-btn-size) * 26 / 30); }
    ```
    Este tratamiento aplica a **cualquier SVG** que deba escalarse. No usar `width: auto` — el `calc()` explícito documenta el ratio y funciona de forma inequívoca en todos los contextos de layout.
11. Para SVGs usados con `mask-image` (patrón del caret), embeber como data-URI en un token CSS en `common/styles-base.css`. No hacer `fetch` de un `.svg` externo desde CSS (falla en `file://`).
12. No duplicar SVGs en carpetas de dominio; todos los assets compartidos viven en `common/assets/`. Mover un SVG a `{DOMINIO}/assets/` solo si tiene variante visual exclusiva del dominio que no puede resolverse con `fill="currentColor"`.

---

## Reglas de migración de componentes entre capas

Antes de añadir CSS, decide dónde va:

```
¿Lo usarán 2 o más dominios?
  Sí → Layer 1: common/styles-base.css (nombre genérico, sin prefijo de dominio)
  No → Layer 2: {DOMINIO}/styles.css (prefijo --{dom}- o .{dom}-)

¿Es variación de un componente ya en common/?
  Solo token diferente → añadir modificador (.is-vis, .banner-visitas) en common/ o en Layer 2
  Layout diferente    → componente nuevo en Layer 2

¿Solo lo usa admin o solo lo usa un aplicante?
  CSS igualmente en {DOM}/styles.css; solo el nombre de la clase puede indicarlo
  (ej. .vis-admin-stats, .evt-admin-sidebar)
```

**Promover (dominio → common):** cuando el mismo componente aparece en dos `styles.css` de dominios distintos con CSS casi idéntico.

**Degradar (common → dominio):** cuando una clase de `common/` solo aparece en HTMLs de un dominio y usa tokens propios de ese dominio. Verificar con `grep -r "nombre-clase" prototipo/` antes de degradar.

**SVGs:** misma lógica — en `common/assets/` si es compartido; en `{DOMINIO}/assets/` solo si es exclusivo.

---

## Añadir un dominio nuevo

1. Crear la estructura de carpetas:
   ```
   prototipo/{DOM}/
     aplicantes/        ← carpeta vacía; aquí irán los HTMLs de aplicantes
     administradores/   ← carpeta vacía; aquí irán los HTMLs de administradores
     styles.css         ← único CSS del dominio (ambos roles)
   ```
2. `styles.css` inicial:
   ```css
   @import '../common/styles-base.css';
   ```
3. Si el dominio tiene color de acento propio, añadir tokens `--{dom}-*` en `:root` dentro de `styles.css`.
4. Si la pantalla de convocatorias de REG muestra una tarjeta de este dominio, añadir `.banner-{dom}` en `common/styles-base.css`.
5. Crear `references/componentes-{dom}.md` al final del desarrollo (ver `componentes-vis.md` como plantilla).
6. No crear CSS en `administradores/` ni en `aplicantes/`. Si un componente solo lo usa admin, nombrarlo con prefijo indicativo (`.{dom}-admin-*`) pero dentro de `{DOM}/styles.css`.

---

## Checklist antes de dar por terminada una pantalla nueva

### Para cualquier dominio

- [ ] Solo variables de `:root`, ningún hex suelto en reglas nuevas
- [ ] Radio de borde: `var(--radio)` (cards) o `var(--radio-sm)` (inputs/botones)
- [ ] Sombras: `var(--sombra-sm/md/lg)`
- [ ] `.proto-bar` actualizado con el paso del flujo correspondiente
- [ ] Avisos contextuales en `.note` (no como prosa suelta en el body)
- [ ] Sin tokens de nombre incorrecto (`--blanco`, `--azul-800`, etc.)

### Adicional para pantallas VIS

- [ ] Tokens verdes usan `--color-verde-*` (common) o `--vis-*` (VIS/styles.css)
- [ ] Banner de convocatoria: `.vis-banner` (no `.conv-card`)
- [ ] Secciones de info: `.vis-bento` + `.vis-bento__num` (verde, no azul)
- [ ] Fichas de datos: `.vis-ficha > .vis-ficha__grid`
- [ ] Grupos: `.vis-grupo-card` dentro de `.vis-grupos-row`
- [ ] Catálogo: `.vis-horario-container > .vis-horario-header + .vis-horario-wrap`
- [ ] SVGs de prev/next-day: inline `<svg viewBox="0 0 26 30" fill="currentColor">` sin `width`/`height` en el elemento; tamaño vía CSS: `height: var(--vis-dia-btn-size); width: calc(var(--vis-dia-btn-size) * 26 / 30)`

### Adicional para pantallas admin EVT (legacy — deuda técnica)

- [ ] Shell: `.admin-body > .sidebar + .admin-main`
- [ ] Filtros: `.chip` + `.is-active` (no `.badge`)
- [ ] Modales: `.modal > .modal-head + .modal-body + .modal-foot`
- [ ] Stat-cards: `.stat-card` + `.accent-{color}`
- [ ] Tokens usados son los de `common/` (no los del bug de `admin.css`)
