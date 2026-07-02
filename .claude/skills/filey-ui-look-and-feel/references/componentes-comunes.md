# Componentes comunes — prototipo/common/styles-base.css

Todos los componentes de esta lista están definidos en `prototipo/common/styles-base.css`
y están disponibles en **todos los dominios** (REG, EVT, VIS, TAL) sin importar nada extra.
Para componentes exclusivos de VIS, ver `componentes-vis.md`.

---

## Estructura de página

- `.proto-bar` / `.proto-bar-inner` — barra superior de aviso de prototipo (letras pequeñas, fondo amarillo pálido). Lista los pasos del flujo; el paso actual va en `<b>`. Ver patrón exacto en `REG/index.html`.
- `.topbar` / `.topbar-inner` — header sticky azul institucional con borde dorado inferior. Añadir `.is-admin` al `.topbar` para variante administrador (fondo más oscuro, texto "Administración").
- `.brand` / `.brand-text` — logo tipográfico FILEY + nombre de módulo.
- `.page` — contenedor centrado `max-width: var(--maxw)` (1120 px).
- `.page-narrow` — igual pero 760 px (para formularios).
- `.page-wide` — igual pero sin restricción de ancho (para catálogos / grids amplios).
- `.breadcrumb` — migas de pan en gris.
- `.page-head` — bloque `h1` + párrafo de subtítulo.
- `.footer` / `.footer-inner` — pie de página azul institucional con borde dorado superior.

---

## Login (pantallas de acceso y registro)

- `.auth-wrap` — grid de 2 columnas (1.05fr / 0.95fr); colapsa a 1 en móvil y oculta `.auth-hero`.
- `.auth-hero` — mitad izquierda, degradado azul + acento dorado radial. Modificador `.is-vis` para variante verde de VIS (banner de visitas).
- `.auth-form` / `.auth-card` — mitad derecha, fondo blanco, formulario centrado (máx. 380 px).
- `.auth-foot` — texto pequeño debajo del formulario.
- `.otp-row` / `.otp-meta` — fila de casillas de código OTP.
- `.user-chip` / `.avatar` — chip de usuario en topnav. Añadir `.is-admin` al `.avatar` para fondo dorado.

---

## Tarjetas de convocatoria

- `.conv-grid` — grid de 3 columnas, colapsa a 1 en móvil.
- `.conv-card` — tarjeta con hover (`translateY(-3px)` + sombra). Clase extra `.is-closed` para convocatorias cerradas (se atenúan, no se ocultan).
- `.conv-banner` — header de color con degradado. Variantes ya definidas:
  - `.banner-stand` — azul
  - `.banner-infantil` — verde
  - `.banner-eventos` — dorado
  - `.banner-visitas` — verde oscuro (para VIS)
  - Para convocatoria nueva: añadir `.banner-{dom}` con gradiente de 2 tokens existentes.
- `.conv-body` — descripción + `.conv-dates`.
- `.conv-foot` — pie con botón de acción.

---

## Bloques tipo bento numerados

- `.section-card` — contenedor de sección de formulario o info.
- `.section-head` — cabecera: `.num` (círculo numerado) + `h3` + `p` opcional.
- `.section-body` — contenido de la sección.
- Patrón: `.section-card > .section-head (.num + h3 + p?) + .section-body`

---

## Botones

`.btn` (base) + modificador:

| Clase | Apariencia | Uso |
|-------|-----------|-----|
| `.btn-primary` | Azul institucional, texto blanco | Acción principal en fondo blanco |
| `.btn-gold` | Dorado, texto azul oscuro | Acción destacada |
| `.btn-ghost` | Outline gris, fondo blanco | Acciones secundarias |
| `.btn-special` | Fondo blanco, hover dorado | Sobre fondo azul oscuro (ej. `.cta-bar`) |
| `.btn-danger` | Rojo, texto blanco | Acciones destructivas |
| `.btn-sm` | Tamaño reducido | Botones inline en tablas o tarjetas |
| `.btn-lg` | Tamaño grande | CTA principal de página |
| `.btn-block` | Ancho completo | Formularios de una columna |

---

## Badges de estado

`.badge` + variante:

| Clase | Color | Significado |
|-------|-------|------------|
| `.badge-open` | Verde (`--ok-*`) | Convocatoria / propuesta abierta |
| `.badge-closed` | Gris | Cerrada |
| `.badge-soon` | Azul | Próximamente |
| `.badge-pending` | Ámbar (`--warn-*`) | Pendiente de revisión |
| `.badge-accepted` | Verde | Aceptada / confirmada |
| `.badge-rejected` | Rojo (`--err-*`) | Rechazada |
| `.badge-changes` | Naranja | Solicitud de cambios |

Para un estado nuevo: mapear a los tokens `--ok-*` / `--warn-*` / `--err-*`, nunca hex suelto.

---

## Avisos / notas

`.note` + variante (todas con ícono en `.ico` + texto):

| Clase | Color | Uso |
|-------|-------|-----|
| `.note-info` | Azul claro | Información contextual |
| `.note-warn` | Ámbar | Advertencia no bloqueante |
| `.note-gold` | Dorado | Recomendación o tip |
| `.note-green` | Verde | Confirmación o estado positivo |
| `.note-err` | Rojo claro | Error o estado crítico |

---

## Pantallas de información de convocatoria

- `.info-hero` — banner dorado de presentación de una convocatoria específica.
- `.dl-dates` — lista de fechas importantes.
- `.cupos` / `.cupo` — barra de progreso de cupos disponibles.
- `.req-list` — checklist de requisitos.
- `.types-row` / `.type-pill` — píldoras de tipo de participante.
- `.cta-bar` — barra de llamada a la acción sobre fondo azul oscuro al final de pantalla de info.

---

## Tablas

- `.table` — tabla estándar (header gris mayúsculas, hover azul claro en filas).

---

## Confirmación y folios

- `.confirm-card` — tarjeta de confirmación de registro exitoso.
- `.folio-box` — folio destacado (tipografía grande, fondo azul claro).
- `.closed-overlay` — overlay sobre convocatorias cerradas.

---

## Formularios (elementos base)

Todos los `<input>`, `<select>`, `<textarea>` heredan estilos de `common/`. Patrones adicionales:
- `.select-wrap` — wrapper con caret SVG vía `mask-image` en `::after`. El caret está embebido como data-URI en `common/styles-base.css`.
- `.form-row` / `.form-col` — layout de campos en fila.
- `.field-group` — grupo de label + input.
- `.total-label` / `.total-value` — resumen numérico (ej. total de alumnos).
