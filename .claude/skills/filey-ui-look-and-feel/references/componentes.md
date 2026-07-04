# Inventario de componentes

> **Nota:** Este archivo está supersedido por los archivos específicos.
> La fuente canónica de CSS compartido es `prototipo/common/styles-base.css` (no `prototipo/REG - EVT/styles.css`).
> El contenido de este archivo se mantiene como referencia de respaldo.
>
> - Componentes comunes (todos los dominios): [`componentes-comunes.md`](componentes-comunes.md)
> - Componentes exclusivos de VIS: [`componentes-vis.md`](componentes-vis.md)

---

## Inventario legacy — prototipo/REG - EVT

Todas las clases viven en `prototipo/common/styles-base.css` (la ruta `prototipo/REG - EVT/styles.css` ya no existe). No hay build step: es CSS plano servido directo, así que cualquier pantalla nueva solo necesita `<link rel="stylesheet" href="../common/styles-base.css">` (o el import equivalente desde el `styles.css` del dominio).

## Estructura de página

- `.proto-bar` / `.proto-bar-inner` — barra superior, letras pequeñas, lista los pasos del flujo con el paso actual implícito por la página. Ver patrón exacto en `index.html`.
- `.topbar` / `.topbar-inner` — header sticky azul institucional con borde dorado inferior, para pantallas ya autenticadas (no en login).
- `.brand` / `.brand-text` — logo + nombre "FILEY" tipográfico (placeholder de logo oficial).
- `.page` / `.page-narrow` — contenedor centrado (`max-width: var(--maxw)` = 1120px); `.page-narrow` para formularios angostos (760px).
- `.breadcrumb` — migas de pan en gris.
- `.page-head` — bloque de título + subtítulo de cada pantalla.
- `.footer` / `.footer-inner` — pie de página azul institucional con borde dorado superior.

## Login (mitad flyer / mitad campos)

- `.auth-wrap` — grid de 2 columnas (1.05fr / .95fr), colapsa a 1 columna y oculta `.auth-hero` en móvil.
- `.auth-hero` — mitad izquierda, degradado azul + acento dorado radial, contiene `.logo-lg`, `h2`, `p`, `.pills` (chips informativos).
- `.auth-form` / `.auth-card` — mitad derecha, fondo blanco, formulario centrado (máx. 380px).
- `.auth-foot` — texto pequeño debajo del formulario (ej. "¿Eres del comité organizador?").
- `.otp-row` / `.otp-meta` — casillas de código OTP.

## Tarjetas de convocatoria (cards con header + footer)

- `.conv-grid` — grid de 3 columnas, colapsa a 1 en móvil.
- `.conv-card` — tarjeta con hover (`translateY(-3px)` + sombra media). Clase extra `.is-closed` para convocatorias cerradas (no se ocultan, se atenúan).
- `.conv-banner` — header de color con degradado, ícono arriba a la derecha, título abajo. Variantes ya definidas: `.banner-stand` (azul), `.banner-infantil` (verde), `.banner-eventos` (dorado). Para una convocatoria nueva, agrega una variante `.banner-<nombre>` con degradado de 2 tokens existentes, no un color suelto.
- `.conv-body` — descripción + `.conv-dates`.
- `.conv-foot` — pie de la tarjeta, normalmente con botón de acción.

## Bloques tipo bento numerados

- `.section-card` — contenedor de una sección de formulario/info.
- `.section-head` — header de la sección con número circular (`.num`), título y descripción opcional.
- `.section-body` — contenido de la sección.
- Patrón: cada bloque de información dentro de una convocatoria o formulario debe envolver su contenido en `.section-card > .section-head (.num + h3 + p) + .section-body`, numerando en el orden que el usuario debe seguir.

## Botones

- `.btn` (base) + un modificador:
  - `.btn-primary` — azul institucional, acción principal.
  - `.btn-gold` — dorado, texto azul oscuro.
  - `.btn-ghost` — outline gris, fondo blanco.
  - `.btn-special` — para usarse sobre fondo azul (ej. dentro de `.cta-bar`): fondo blanco, hover dorado.
  - Tamaño: `.btn-lg` (grande), ancho completo: `.btn-block`.

## Badges de estado

`.badge` + variante: `.badge-open`, `.badge-closed`, `.badge-soon`, `.badge-pending`, `.badge-accepted`, `.badge-rejected`, `.badge-changes`. Todas mapean a los tokens `--ok-*` / `--warn-*` / `--err-*` / `--gris-*` / `--azul-*`.

## Avisos / notas

`.note` + variante `.note-info` (azul), `.note-warn` (ámbar), `.note-gold` (dorado) — para mensajes contextuales dentro del flujo (no para el aviso de prototipo, que va en `.proto-bar`).

## Otros patrones reutilizables

- `.info-hero` — banner dorado de presentación de una convocatoria específica (ver `convocatoria-eventos.html`).
- `.dl-dates`, `.cupos` / `.cupo` (barra de progreso de cupos), `.req-list` (checklist de requisitos), `.types-row` / `.type-pill` — bloques de la pantalla de información de convocatoria.
- `.cta-bar` — barra de llamada a la acción sobre fondo azul oscuro al final de una pantalla de info.
- `.table` — tablas (ej. `mis-propuestas.html`), header gris mayúsculas, hover azul claro en filas.
- `.confirm-card` / `.folio-box` — pantalla de confirmación con folio destacado.
- `.closed-overlay` — overlay para convocatorias cerradas.
