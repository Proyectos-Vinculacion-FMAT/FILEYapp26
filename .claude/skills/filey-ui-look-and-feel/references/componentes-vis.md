# Componentes VIS — prototipo/VIS/styles.css

Todos los componentes de esta lista están definidos en `prototipo/VIS/styles.css`
(que extiende `common/styles-base.css`). Solo aplican a pantallas de Visitas Escolares.
Para componentes compartidos a todos los dominios, ver `componentes-comunes.md`.

---

## Tokens VIS (`:root` en `VIS/styles.css`)

| Token | Valor | Uso |
| ----- | ----- | --- |
| `--vis-dia-btn-size` | `16px` | Altura de los botones prev/next día |
| `--vis-abierta-bg` / `--vis-abierta-dot` | Verde semitransparente / verde oscuro | Pill de estado "Abierta" |
| `--vis-cerrada-bg` / `--vis-cerrada-dot` | Gris semitransparente / gris oscuro | Pill de estado "Cerrada" |
| `--vis-grad-radial` / `--vis-grad-lineal` | Degradados verde lima → verde oscuro | Fondos de banner y cabeceras |
| `--vis-grad-sala` | Degradado verde muy tenue | Fondo de celdas en el catálogo |
| `--vis-cupos-vacio` / `--vis-cupos-lleno` | Gris claro / gris medio | Barra de cupos vacía / llena |
| `--vis-cupos-grad` | Degradado magenta–morado | Barra de cupos disponibles |
| `--vis-badge-bg` | Degradado magenta semitransparente | Badge de estado en el banner |
| `--vis-descanso-bg` | Rojo semitransparente | Celda de "Descanso" en el catálogo |
| `--vis-nivel-prim-alta/baja/secundaria/preparatoria/universidad` | Colores semitransparentes | Píldoras de nivel educativo |
| `--vis-cerrado-bg` / `--vis-sin-taller-bg` | Rojo oscuro / negro semitransparente | Celdas bloqueadas |

---

## Modificadores de componentes comunes

Estos modificadores se aplican sobre componentes de `common/`:

- `.auth-hero.is-vis` — hero verde para el flujo de visitas (reemplaza el degradado azul).
- `.section-card.is-vis` — el `.num` del encabezado bento usa verde en vez de azul.
- `.btn-danger` — variante roja de `.btn` para acciones destructivas.
- `.btn-sm` — variante pequeña de `.btn` (`padding: 8px 14px`, `font-size: 13px`).
- `.note-green` — nota con fondo verde claro (confirmación/estado positivo).
- `.note-err` — nota con fondo rojo claro (error crítico).
- `.banner-infantil` — override del degradado de `common/` para usar tokens VIS.

---

## Pills de estado de convocatoria

```html
<span class="vis-estado vis-estado--abierta">
  <span class="vis-estado__dot"></span> Abierta
</span>
```

| Clase | Apariencia |
| ----- | ---------- |
| `.vis-estado--abierta` | Verde semitransparente, texto verde oscuro |
| `.vis-estado--cerrada` | Gris semitransparente, texto gris oscuro |

---

## Banner principal VIS

```html
<div class="vis-banner">
  <div class="vis-banner__badge">
    <span class="vis-banner__badge-dot"></span>
    <span class="vis-banner__badge-label">Convocatoria abierta</span>
  </div>
  <h1 class="vis-banner__title">Visitas escolares FILEY 2027</h1>
  <p class="vis-banner__desc">Descripción…</p>
</div>
```

Fondo: degradado lineal verde lima → verde oscuro. Usa tokens `--vis-grad-lineal` y `--vis-badge-bg`.

---

## Layout bento de convocatoria

```html
<div class="vis-bento-layout">
  <div class="vis-bento-left">
    <div class="vis-bento">
      <div class="vis-bento__header">
        <span class="vis-bento__num">1</span>
        <h3 class="vis-bento__title">Requisitos</h3>
      </div>
      <div class="vis-bento__body">
        <ul class="vis-bento__list">
          <li class="vis-bento__item">…</li>
        </ul>
        <!-- o filas clave-valor: -->
        <div class="vis-bento__kv">
          <span class="vis-bento__kv-label">Fecha límite</span>
          <span class="vis-bento__kv-value">15 feb 2027</span>
        </div>
      </div>
    </div>
  </div>
  <div class="vis-bento-right"><!-- cupos --></div>
</div>
```

- `.vis-bento__num` — círculo verde (usa `--color-verde-700`), igual al `.num` de `.section-head` pero con `.is-vis`.
- `.vis-bento-left` / `.vis-bento-right` — grid 1.6fr / 1fr.

---

## Barras de cupos

```html
<div class="vis-cupo">
  <div class="vis-cupo__row">
    <span class="vis-cupo__dia">Lunes 14</span>
    <span class="vis-cupo__count">42 / 105 grupos</span>
  </div>
  <div class="vis-cupo__bar-bg">
    <div class="vis-cupo__bar-fill vis-cupo__bar-fill--magenta" style="width:40%"></div>
  </div>
</div>
```

Variantes de fill: `--magenta` (degradado morado, cupos disponibles), `--lleno` (gris, sin cupo).

---

## Tabla de administración

```html
<div class="vis-tabla-wrap">
  <table class="vis-tabla">
    <thead><tr><th>Folio</th><th>Institución</th><th>Estado</th></tr></thead>
    <tbody>
      <tr class="vis-row">
        <td class="folio">VIS-2027-001</td>
        <td>Benito Juárez García</td>
        <td><span class="badge badge-pending">Pendiente</span></td>
      </tr>
      <tr class="vis-row">
        <td colspan="3">
          <button class="vis-tabla__toggle is-open">
            Ver detalle <span class="vis-tabla__toggle-icon"><svg>…</svg></span>
          </button>
        </td>
      </tr>
      <tr class="vis-tabla__row-detail is-open">
        <td colspan="3">
          <div class="vis-tabla-detail">
            <div class="vis-tabla-detail__inner">
              <div class="vis-ficha">…</div>
              <div class="vis-detail-actions">…</div>
            </div>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

El toggle abre/cierra la fila de detalle. Clase `is-open` en `.vis-tabla__toggle` rota el caret e invierte el color. Clase `is-open` en `.vis-tabla__row-detail` la hace `display: table-row`.

---

## Ficha de datos (dentro del detalle de tabla)

```html
<div class="vis-ficha">
  <p class="vis-ficha__section">Responsable</p>
  <div class="vis-ficha__grid">
    <span class="vis-ficha__key">Nombre</span>
    <span class="vis-ficha__value">Benito Juárez García</span>
    <span class="vis-ficha__key">Cargo</span>
    <span class="vis-ficha__value">Director</span>
  </div>
</div>
```

Fondo dorado muy tenue (`--oro-050`), borde `--oro-200`. Grid de dos columnas: label gris + valor azul bold.

---

## Tarjetas de grupo

```html
<div class="vis-grupos-row">
  <div class="vis-grupo-card">
    <div class="vis-grupo-card__header">Grupo 1 — G1</div>
    <div class="vis-grupo-card__body">
      <span>Grado: Sexto</span>
      <span>Visitantes: 35</span>
      <span>Responsable: …</span>
      <span>Talleres reservados: 3</span>
    </div>
  </div>
</div>
```

Header dorado, cuerpo blanco con datos en columna. Usadas tanto en la cabecera de selección del catálogo (`.vis-sel-header`) como en la ficha de la propuesta.

---

## Cabecera de selección del catálogo

```html
<div class="vis-sel-header">
  <p class="vis-sel-header__instituto">Benito Juárez García · Primaria</p>
  <div class="vis-grupo-card">…</div>
  <!-- más grupo-cards -->
</div>
```

Fondo `--color-azul-texto`, borde inferior grueso dorado, border-radius arriba. Se continúa con `.vis-horario-container` debajo (borde-radius abajo).

---

## Grid de horario / catálogo

```html
<div class="vis-horario-container">
  <div class="vis-horario-header">
    <div class="vis-turno-selector">
      <span class="vis-turno-selector__label">Turno</span>
      <div class="select-wrap">
        <select class="vis-turno-dropdown" id="turno-select">
          <option value="matutino">Matutino</option>
          <option value="vespertino">Vespertino</option>
        </select>
      </div>
    </div>
    <div class="vis-dia-selector">
      <button type="button" class="vis-dia-btn" aria-label="Día anterior" disabled>
        <svg viewBox="0 0 26 30" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
          <path d="M0.999998 16.2926C-0.333335 15.5228 -0.333333 13.5983 1 12.8285L22.75 0.271127C24.0833 -0.498673 25.75 0.463579 25.75 2.00318V27.1179C25.75 28.6575 24.0833 29.6198 22.75 28.85L0.999998 16.2926Z"/>
        </svg>
      </button>
      <span class="vis-dia-selector__text">14 de marzo de 2028</span>
      <button type="button" class="vis-dia-btn" aria-label="Día siguiente">
        <svg viewBox="0 0 26 30" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
          <path d="M24.75 12.8285C26.0833 13.5983 26.0833 15.5228 24.75 16.2926L3 28.85C1.66666 29.6198 0 28.6575 0 27.1179V2.00318C0 0.463576 1.66667 -0.498672 3 0.271129L24.75 12.8285Z"/>
        </svg>
      </button>
    </div>
  </div>
  <div class="vis-horario-wrap" id="horario-wrap">
    <!-- app.js inyecta .vis-horario-area[data-turno].is-active con filas -->
  </div>
</div>
```

**SVGs de prev/next:** usar siempre `<svg viewBox="0 0 26 30" fill="currentColor">` inline sin atributos `width`/`height`. El CSS controla el tamaño con el ratio derivado del `viewBox` (26/30):

```css
.vis-dia-btn svg { display: block; height: var(--vis-dia-btn-size); width: calc(var(--vis-dia-btn-size) * 26 / 30); }
```

**Estructura de área (generada por app.js):**

```html
<div class="vis-horario-area is-active" data-turno="matutino">
  <div class="vis-horario-tiempos">
    <div class="vis-horario-tiempo vis-horario-tiempo--sala">Sala</div>
    <div class="vis-horario-tiempo">09:00 – 10:00</div>
    …
  </div>
  <div class="vis-horario-fila">
    <div class="vis-horario-celda vis-horario-celda--sala-label">Sala A</div>
    <div class="vis-horario-celda">
      <span class="vis-horario-celda__nombre">Nombre del taller</span>
      <div class="vis-horario-celda__meta">
        <span class="vis-nivel vis-nivel--primaria-alta">Primaria alta</span>
        <span class="vis-horario-celda__cupos">18 cupos</span>
      </div>
      <div class="vis-celda-badges">
        <span class="vis-grupo-badge">G1</span>
      </div>
    </div>
    <div class="vis-horario-celda vis-horario-celda--sin-taller">
      <span class="vis-bloque-label">—</span>
    </div>
  </div>
</div>
```

**Modificadores de celda:** `--sala-label` (etiqueta de sala), `--llena` (sin cupo), `--sin-taller` (bloque vacío), `--cerrado` (bloqueado), `--libre` (acceso libre).

---

## Barra de reserva (sticky)

```html
<div class="vis-reserva-bar">
  <div class="txt">
    <strong><span id="reserva-count">0</span> talleres en tu itinerario</strong>
    <span id="reserva-detalle">Asigna grupos…</span>
  </div>
  <a class="btn btn-gold btn-lg" href="itinerario.html">Ver / confirmar itinerario →</a>
</div>
```

Fondo `--color-azul-degradado-oscuro`, sticky bottom. El botón usa `.btn-gold` (usuario) o `.btn-gold` (admin); el color lo distingue el contexto.

---

## Itinerario confirmado

```html
<div class="vis-itin-list">
  <div class="vis-itin-item">
    <div class="vis-itin-item__day">Lunes 14</div>
    <div class="vis-itin-item__main">
      <strong>Taller de robótica</strong>
      <span>10:00 – 11:00 · Sala A · 35 alumnos</span>
    </div>
    <div class="vis-itin-item__groups">
      <span class="vis-grupo-badge">G1</span>
      <span class="vis-grupo-badge">G2</span>
    </div>
  </div>
</div>
```

---

## Numeralia de administración

```html
<div class="vis-stats">
  <div class="vis-stat">
    <strong>42</strong>
    <span>Propuestas</span>
  </div>
</div>
```

Grid de 4 columnas (colapsa a 2 en móvil). Número grande en azul institucional.

---

## Barra de filtros (admin)

```html
<div class="vis-filters">
  <div class="field">
    <label for="f-estado">Estado</label>
    <div class="select-wrap"><select id="f-estado">…</select></div>
  </div>
  <div class="field">
    <label for="f-nivel">Nivel</label>
    <div class="select-wrap"><select id="f-nivel">…</select></div>
  </div>
  <button class="btn btn-ghost">Filtrar</button>
</div>
```

---

## Bloques de grupo (formulario de propuesta)

```html
<div class="grupo-block" id="grupo-1">
  <div class="grupo-block__head">
    <strong>Grupo 1</strong>
    <button type="button" class="grupo-remove">Eliminar grupo</button>
  </div>
  <!-- campos del grupo: select grado, input alumnos, input responsable -->
</div>

<div class="total-box" id="total-alumnos">
  Total de alumnos: <strong id="total-count">35</strong> / 105
</div>
```

`.total-box.over` — estado de error cuando se supera el límite de 105 alumnos (fondo rojo claro).

---

## Píldoras de nivel educativo

```html
<span class="vis-nivel vis-nivel--primaria-alta">Primaria alta</span>
```

| Clase | Color |
| ----- | ----- |
| `.vis-nivel--primaria-alta` | Morado semitransparente |
| `.vis-nivel--primaria-baja` | Azul claro semitransparente |
| `.vis-nivel--secundaria` | Magenta semitransparente |
| `.vis-nivel--preparatoria` | Verde semitransparente |
| `.vis-nivel--universidad` | Rojo semitransparente |
