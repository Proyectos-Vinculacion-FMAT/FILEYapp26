<!-- GENERADO por prototipo/scripts/gen-inventario.sh — no editar a mano. -->
# Inventario CSS del prototipo

Regenerar con `./prototipo/scripts/gen-inventario.sh` tras cualquier cambio en un `styles.css`.
Fuente: `prototipo/common/styles-base.css` + `prototipo/{DOM}/styles.css`.

**78 tokens · 393 definiciones de clase · 39 sin uso detectado en HTML/JS.**

## Cómo usar este archivo

1. Antes de escribir CSS, busca aquí la clase o el token. Si existe, reúsalo.
2. Columna **capa**: `common` = todos los dominios; `REG`/`EVT`/`VIS` = solo ese dominio.
3. Columna **usada en**: dominios donde aparece en HTML/JS. `—` = definida pero sin uso
   (candidata a borrarse).
4. Una clase listada dos veces (`common` + un dominio) es un **override intencional**, no un duplicado.
   Solo es candidata a **promover** a `common` si su única definición está en una capa de dominio
   y la columna *usada en* nombra dos o más dominios.
5. Este índice reemplaza leer los `.css` completos. Ábrelos solo cuando necesites las reglas exactas.

## Tokens

| token | capa | valor |
| --- | --- | --- |
| `--color-blanco` | common | `#FFFFFF` |
| `--color-azul-link-enfoque` | common | `#C8D7E3` |
| `--color-azul-institucional` | common | `#01457C` |
| `--color-azul-texto` | common | `#00437C` |
| `--color-azul-institucional-enfoque` | common | `#013763` |
| `--color-azul-degradado-claro` | common | `#01497B` |
| `--color-azul-degradado-oscuro` | common | `#151A30` |
| `--color-dorado-encabezado` | common | `#C99213` |
| `--color-dorado-700` | common | `#B3810F` |
| `--color-dorado-800` | common | `#9C700B` |
| `--color-dorado-degradado-oscuro` | common | `#6E4D03` |
| `--color-negro` | common | `#000000` |
| `--font-filey` | common | `"Open Sans", "Segoe UI", "Helvetica Neue", A…` |
| `--radio-card` | common | `13px` |
| `--radio-btn` | common | `16px` |
| `--radio-pill` | common | `30px` |
| `--sombra-card` | common | `0 4px 4px rgba(0, 0, 0, 0.25)` |
| `--color-morado` | common | `#955FF2` |
| `--color-magenta-oscuro` | common | `#70124C` |
| `--color-verde-lima` | common | `#99BA15` |
| `--color-verde-700` | common | `#839F10` |
| `--color-verde-800` | common | `#6C840B` |
| `--color-verde-degradado-oscuro` | common | `#3F4E00` |
| `--color-rojo` | common | `#CC311D` |
| `--color-rojo-700` | common | `#912111` |
| `--color-rojo-800` | common | `#73190B` |
| `--color-rojo-degradado-oscuro` | common | `#551104` |
| `--tinta` | common | `#1b2330` |
| `--gris-700` | common | `#3f4a5a` |
| `--gris-500` | common | `#6b7686` |
| `--gris-300` | common | `#c8d0db` |
| `--gris-200` | common | `#e2e7ee` |
| `--gris-100` | common | `#eef1f6` |
| `--gris-050` | common | `#f7f9fc` |
| `--ok-600` | common | `#1d8a4e` |
| `--ok-050` | common | `#e7f6ee` |
| `--warn-600` | common | `#b8860b` |
| `--warn-050` | common | `#fdf6e3` |
| `--oro-200` | common | `#f1e3b0` |
| `--oro-050` | common | `#fbf6e6` |
| `--err-600` | common | `var(--color-rojo)` |
| `--err-050` | common | `#fbeae8` |
| `--radio` | common | `12px` |
| `--radio-sm` | common | `8px` |
| `--sombra-sm` | common | `0 1px 2px rgba(16, 36, 64, .08), 0 1px 3px r…` |
| `--sombra-md` | common | `0 6px 18px rgba(16, 36, 64, .10)` |
| `--sombra-lg` | common | `0 18px 50px rgba(16, 36, 64, .18)` |
| `--maxw` | common | `1120px` |
| `--azul-600` | common | `#0a6fc2` |
| `--azul-100` | common | `#e6f0fa` |
| `--azul-050` | common | `#f3f8fd` |
| `--caret-svg` | common | `url("data:image/svg+xml,%3Csvg xmlns='http:/…` |
| `--ok-200` | EVT | `#c9e5d3` |
| `--err-200` | EVT | `#eecac5` |
| `--color-azul-texto` | VIS | `#00437C;             /* alias explícito par…` |
| `--color-dorado-degradado-oscuro` | VIS | `#6E4D03; /* dorado profundo para bordes de d…` |
| `--vis-dia-btn-size` | VIS | `16px;               /* altura de los botones…` |
| `--vis-abierta-bg` | VIS | `rgba(123, 186, 21, 0.5)` |
| `--vis-abierta-dot` | VIS | `#174E00` |
| `--vis-cerrada-bg` | VIS | `rgba(151, 151, 151, 0.5)` |
| `--vis-cerrada-dot` | VIS | `#535353` |
| `--vis-grad-radial` | VIS | `radial-gradient(50% 50% at 50% 50%, var(--co…` |
| `--vis-grad-lineal` | VIS | `linear-gradient(90deg, var(--color-verde-lim…` |
| `--vis-grad-sala` | VIS | `linear-gradient(90deg, rgba(153, 186, 21, 0.…` |
| `--vis-cupos-vacio` | VIS | `#D9D9D9` |
| `--vis-cupos-lleno` | VIS | `#797979` |
| `--vis-cupos-grad` | VIS | `linear-gradient(78.51deg, var(--color-morado…` |
| `--vis-badge-bg` | VIS | `linear-gradient(78.51deg, rgba(149, 95, 242,…` |
| `--vis-descanso-bg` | VIS | `rgba(204, 49, 29, 0.5)` |
| `--vis-nivel-preescolar` | VIS | `rgba(255, 170, 0, 0.55)` |
| `--vis-nivel-prim-alta` | VIS | `rgba(149, 95, 242, 0.5)` |
| `--vis-nivel-prim-baja` | VIS | `rgba(95, 169, 242, 0.5)` |
| `--vis-nivel-secundaria` | VIS | `rgba(240, 95, 242, 0.5)` |
| `--vis-nivel-preparatoria` | VIS | `rgba(60, 147, 10, 0.5)` |
| `--vis-nivel-universidad` | VIS | `rgba(228, 0, 57, 0.5)` |
| `--vis-cerrado-bg` | VIS | `rgba(115, 25, 11, 0.5)` |
| `--vis-sin-taller-bg` | VIS | `rgba(26, 26, 26, 0.5)` |
| `--vis-icon-btn-size` | VIS | `14px` |

## Componentes

| clase | capa | línea | usada en |
| --- | --- | --- | --- |
| `.topbar` | common | 94 | EVT, REG, VIS |
| `.topbar-inner` | common | 102 | EVT, REG, VIS |
| `.home` | common | 110 | EVT, REG, VIS |
| `.logo` | common | 113 | EVT, REG, VIS |
| `.brand-text` | common | 114 | EVT, REG, VIS |
| `.topnav` | common | 118 | EVT, REG, VIS |
| `.user-chip` | common | 122 | EVT, REG, VIS |
| `.avatar` | common | 130 | EVT, REG, VIS |
| `.is-admin` | common | 137 | REG, VIS |
| `.page` | common | 141 | EVT, REG, VIS |
| `.page-narrow` | common | 142 | EVT, VIS |
| `.page-wide` | common | 143 | VIS |
| `.breadcrumb` | common | 145 | EVT, VIS |
| `.page-head` | common | 149 | EVT, REG, VIS |
| `.auth-wrap` | common | 154 | EVT, REG |
| `.auth-hero` | common | 159 | EVT, REG |
| `.logo-lg` | common | 167 | EVT, REG |
| `.pills` | common | 170 | EVT, REG |
| `.auth-form` | common | 175 | EVT, REG |
| `.auth-card` | common | 180 | EVT, REG |
| `.sub` | common | 182 | EVT, REG |
| `.auth-foot` | common | 183 | EVT, REG |
| `.otp-row` | common | 186 | REG |
| `.otp-meta` | common | 193 | REG |
| `.field` | common | 196 | EVT, REG, VIS |
| `.hint` | common | 198 | EVT, REG |
| `.req` | common | 199 | EVT, REG, VIS |
| `.opt` | common | 200 | EVT, REG, VIS |
| `.select-wrap` | common | 217 | VIS |
| `.is-open` | common | 245 | VIS |
| `.field-prefill` | common | 256 | EVT, VIS |
| `.tag-auto` | common | 257 | EVT, VIS |
| `.grid-2` | common | 263 | EVT, VIS |
| `.grid-3` | common | 264 | VIS |
| `.radio-row` | common | 266 | EVT, REG |
| `.file-mock` | common | 270 | EVT, REG |
| `.ico` | common | 276 | EVT, REG, VIS |
| `.txt` | common | 277 | EVT, REG, VIS |
| `.multi-input` | common | 281 | EVT, REG |
| `.card` | common | 284 | EVT, VIS |
| `.card-pad` | common | 288 | EVT, VIS |
| `.section-card` | common | 290 | EVT, VIS |
| `.section-head` | common | 291 | EVT, VIS |
| `.num` | common | 296 | EVT, VIS |
| `.section-body` | common | 303 | EVT, VIS |
| `.btn` | common | 305 | EVT, REG, VIS |
| `.btn-primary` | common | 312 | EVT, REG, VIS |
| `.btn-gold` | common | 314 | EVT, REG, VIS |
| `.btn-green` | common | 316 | VIS |
| `.btn-ghost` | common | 318 | EVT, REG, VIS |
| `.btn-special` | common | 322 | EVT, VIS |
| `.btn-block` | common | 324 | EVT, REG |
| `.btn-lg` | common | 325 | EVT, REG, VIS |
| `.form-actions` | common | 327 | EVT, VIS |
| `.spacer` | common | 331 | EVT, VIS |
| `.conv-grid` | common | 334 | EVT, REG |
| `.conv-card` | common | 335 | EVT, REG |
| `.is-closed` | common | 341 | REG |
| `.conv-banner` | common | 342 | EVT, REG |
| `.banner-stand` | common | 348 | EVT, REG |
| `.banner-infantil` | common | 349 | EVT, REG |
| `.banner-eventos` | common | 350 | EVT, REG |
| `.banner-visitas` | common | 351 | EVT, REG |
| `.conv-body` | common | 352 | EVT, REG |
| `.conv-dates` | common | 354 | EVT, REG |
| `.conv-foot` | common | 355 | EVT, REG |
| `.badge` | common | 357 | EVT, REG |
| `.badge-open` | common | 363 | EVT, REG |
| `.badge-closed` | common | 364 | REG |
| `.badge-soon` | common | 365 | REG |
| `.badge-pending` | common | 366 | EVT |
| `.badge-accepted` | common | 367 | EVT |
| `.badge-rejected` | common | 368 | EVT |
| `.badge-changes` | common | 369 | EVT |
| `.info-hero` | common | 372 | EVT |
| `.info-grid` | common | 382 | EVT, VIS |
| `.dl-dates` | common | 384 | EVT |
| `.row` | common | 385 | EVT |
| `.dot` | common | 392 | EVT, REG, VIS, common |
| `.cupos` | common | 394 | EVT |
| `.cupo` | common | 395 | EVT |
| `.top` | common | 398 | EVT |
| `.bar` | common | 401 | EVT, VIS |
| `.full` | common | 403 | EVT |
| `.req-list` | common | 405 | EVT |
| `.ck` | common | 407 | EVT |
| `.types-row` | common | 409 | EVT |
| `.type-pill` | common | 410 | EVT |
| `.cta-bar` | common | 412 | EVT, VIS |
| `.table` | common | 421 | EVT |
| `.folio` | common | 425 | EVT, VIS |
| `.confirm-card` | common | 428 | EVT, VIS |
| `.check` | common | 429 | EVT, VIS |
| `.folio-box` | common | 435 | EVT, VIS |
| `.note` | common | 444 | EVT, REG, VIS |
| `.note-info` | common | 449 | EVT, REG, VIS |
| `.note-warn` | common | 450 | EVT, REG, VIS |
| `.note-gold` | common | 451 | EVT, REG |
| `.closed-overlay` | common | 453 | REG |
| `.proto-bar` | common | 460 | EVT, REG, VIS |
| `.proto-bar-inner` | common | 464 | EVT, REG, VIS |
| `.sep` | common | 467 | EVT, REG, VIS |
| `.footer` | common | 471 | EVT, REG, VIS |
| `.footer-inner` | common | 475 | EVT, REG, VIS |
| `.auth-hero` | REG | 8 | EVT, REG |
| `.logo-lg` | REG | 8 | EVT, REG |
| `.is-admin` | REG | 14 | REG, VIS |
| `.pills` | REG | 30 | EVT, REG |
| `.btn` | REG | 38 | EVT, REG, VIS |
| `.field` | REG | 46 | EVT, REG, VIS |
| `.is-invalid` | REG | 46 | REG, VIS |
| `.msg-error` | REG | 50 | REG |
| `.otp-estado` | REG | 58 | REG |
| `.err` | REG | 65 | REG |
| `.otp-row` | REG | 67 | REG |
| `.error` | REG | 67 | REG |
| `.otp-cooldown` | REG | 78 | REG |
| `.admin-body` | EVT | 17 | EVT |
| `.sidebar` | EVT | 19 | EVT |
| `.side-section` | EVT | 28 | EVT |
| `.side-nav` | EVT | 30 | EVT |
| `.side-link` | EVT | 31 | EVT |
| `.ico` | EVT | 38 | EVT, REG, VIS |
| `.active` | EVT | 39 | EVT |
| `.is-disabled` | EVT | 43 | — |
| `.admin-main` | EVT | 46 | EVT |
| `.admin-toolbar` | EVT | 47 | EVT |
| `.menu-btn` | EVT | 51 | EVT |
| `.crumb` | EVT | 56 | EVT |
| `.admin-content` | EVT | 57 | EVT |
| `.topbar` | EVT | 60 | EVT, REG, VIS |
| `.admin` | EVT | 60 | EVT |
| `.topbar-inner` | EVT | 60 | EVT, REG, VIS |
| `.chip-modulo` | EVT | 61 | — |
| `.chips` | EVT | 68 | EVT |
| `.chip` | EVT | 69 | EVT, REG |
| `.is-active` | EVT | 75 | EVT, REG, VIS |
| `.count` | EVT | 76 | EVT |
| `.toolbar-row` | EVT | 79 | EVT |
| `.searchbox` | EVT | 80 | EVT |
| `.stat-grid` | EVT | 90 | EVT |
| `.stat-card` | EVT | 91 | EVT |
| `.k` | EVT | 95 | EVT |
| `.v` | EVT | 96 | EVT |
| `.foot` | EVT | 97 | EVT |
| `.accent-blue` | EVT | 98 | EVT |
| `.accent-gold` | EVT | 99 | EVT |
| `.accent-ok` | EVT | 100 | EVT |
| `.accent-warn` | EVT | 101 | EVT |
| `.accent-err` | EVT | 102 | EVT |
| `.btn-row` | EVT | 105 | EVT |
| `.link-arrow` | EVT | 106 | EVT |
| `.modal-back` | EVT | 109 | EVT |
| `.modal` | EVT | 114 | EVT |
| `.modal-head` | EVT | 118 | EVT |
| `.modal-body` | EVT | 121 | EVT |
| `.modal-foot` | EVT | 122 | EVT |
| `.cal-wrap` | EVT | 125 | EVT |
| `.cal-side` | EVT | 126 | EVT |
| `.cal-panel` | EVT | 127 | EVT |
| `.cal-main` | EVT | 130 | EVT |
| `.cal-toolbar` | EVT | 131 | EVT |
| `.month` | EVT | 132 | EVT |
| `.cal-nav` | EVT | 133 | EVT |
| `.cal-grid` | EVT | 136 | EVT |
| `.dow` | EVT | 137 | EVT |
| `.cal-cell` | EVT | 138 | — |
| `.num` | EVT | 140 | EVT, VIS |
| `.out` | EVT | 141 | — |
| `.today` | EVT | 142 | — |
| `.cal-event` | EVT | 144 | — |
| `.ev-apertura` | EVT | 149 | EVT |
| `.ev-cierre` | EVT | 150 | EVT |
| `.ev-notif` | EVT | 151 | EVT |
| `.ev-ajustes` | EVT | 152 | EVT |
| `.ev-asignacion` | EVT | 153 | EVT |
| `.ev-constancias` | EVT | 154 | EVT |
| `.date-list` | EVT | 157 | EVT |
| `.date-item` | EVT | 158 | EVT |
| `.swatch` | EVT | 159 | EVT |
| `.lbl` | EVT | 160 | EVT |
| `.val` | EVT | 161 | — |
| `.sched` | EVT | 165 | EVT |
| `.time-col` | EVT | 169 | EVT |
| `.slot` | EVT | 170 | EVT |
| `.act` | EVT | 171 | EVT |
| `.clash` | EVT | 177 | EVT |
| `.free` | EVT | 178 | EVT |
| `.rep-badge` | EVT | 181 | EVT |
| `.salon-th` | EVT | 187 | — |
| `.sala-th` | EVT | 188 | — |
| `.aforo-badge` | EVT | 189 | — |
| `.mock-banner` | EVT | 197 | EVT |
| `.prg-layout` | EVT | 207 | EVT |
| `.rail` | EVT | 210 | EVT |
| `.hint` | EVT | 212 | EVT, REG |
| `.rail-item` | EVT | 213 | EVT |
| `.is-selected` | EVT | 219 | EVT |
| `.grip` | EVT | 220 | EVT |
| `.r-body` | EVT | 221 | EVT |
| `.rail-empty` | EVT | 223 | EVT |
| `.modal-wide` | EVT | 226 | EVT |
| `.evt-dialog` | EVT | 227 | EVT |
| `.evt-form` | EVT | 228 | EVT |
| `.evt-row` | EVT | 229 | EVT |
| `.ic` | EVT | 231 | EVT |
| `.f` | EVT | 232 | EVT |
| `.big` | EVT | 234 | EVT |
| `.evt-preview` | EVT | 237 | EVT |
| `.pv-head` | EVT | 238 | EVT |
| `.nav` | EVT | 239 | EVT |
| `.day-mini` | EVT | 241 | EVT |
| `.drow` | EVT | 242 | EVT |
| `.dh` | EVT | 244 | EVT |
| `.dcell` | EVT | 245 | EVT |
| `.ev-block` | EVT | 246 | EVT |
| `.grab-dot` | EVT | 250 | EVT |
| `.top` | EVT | 251 | EVT |
| `.bot` | EVT | 252 | EVT |
| `.taken` | EVT | 253 | — |
| `.mini-act` | EVT | 253 | — |
| `.pv-foot` | EVT | 254 | EVT |
| `.banner-infantil` | VIS | 43 | EVT, REG |
| `.btn-green` | VIS | 46 | VIS |
| `.auth-hero` | VIS | 50 | EVT, REG |
| `.is-vis` | VIS | 50 | VIS |
| `.section-card` | VIS | 57 | EVT, VIS |
| `.section-head` | VIS | 57 | EVT, VIS |
| `.num` | VIS | 57 | EVT, VIS |
| `.btn-danger` | VIS | 60 | VIS |
| `.btn-sm` | VIS | 62 | VIS |
| `.note-green` | VIS | 65 | VIS |
| `.note-err` | VIS | 66 | VIS |
| `.vis-estado` | VIS | 76 | — |
| `.vis-estado__dot` | VIS | 81 | — |
| `.vis-estado--abierta` | VIS | 82 | — |
| `.vis-estado--cerrada` | VIS | 84 | — |
| `.vis-banner` | VIS | 88 | VIS |
| `.vis-banner__badge` | VIS | 94 | VIS |
| `.vis-banner__badge-dot` | VIS | 100 | VIS |
| `.vis-banner__badge-label` | VIS | 101 | VIS |
| `.vis-banner__title` | VIS | 102 | VIS |
| `.vis-banner__desc` | VIS | 103 | VIS |
| `.vis-bento-layout` | VIS | 106 | VIS |
| `.vis-bento-left` | VIS | 107 | VIS |
| `.vis-bento-right` | VIS | 108 | VIS |
| `.vis-bento` | VIS | 110 | VIS |
| `.vis-bento__header` | VIS | 115 | VIS |
| `.vis-bento__num` | VIS | 119 | VIS |
| `.vis-bento__title` | VIS | 124 | VIS |
| `.vis-bento__body` | VIS | 125 | VIS |
| `.vis-bento__list` | VIS | 126 | VIS |
| `.vis-bento__item` | VIS | 127 | VIS |
| `.vis-bento__kv` | VIS | 130 | VIS |
| `.vis-bento__kv-label` | VIS | 135 | VIS |
| `.vis-bento__kv-value` | VIS | 136 | VIS |
| `.vis-cupo` | VIS | 139 | VIS |
| `.vis-cupo__row` | VIS | 141 | VIS |
| `.vis-cupo__dia` | VIS | 142 | VIS |
| `.vis-cupo__count` | VIS | 143 | VIS |
| `.vis-cupo__nota` | VIS | 144 | VIS |
| `.vis-cupo__bar-bg` | VIS | 145 | VIS |
| `.vis-cupo__bar-fill` | VIS | 146 | VIS |
| `.vis-cupo__bar-fill--magenta` | VIS | 147 | VIS |
| `.vis-cupo__bar-fill--lleno` | VIS | 148 | VIS |
| `.vis-tabla-wrap` | VIS | 151 | VIS |
| `.vis-tabla` | VIS | 152 | VIS |
| `.vis-row` | VIS | 159 | VIS |
| `.folio` | VIS | 160 | EVT, VIS |
| `.vis-tabla__toggle` | VIS | 161 | VIS |
| `.vis-tabla__toggle-icon` | VIS | 167 | VIS |
| `.is-open` | VIS | 169 | VIS |
| `.vis-tabla__row-detail` | VIS | 171 | VIS |
| `.vis-tabla-detail` | VIS | 175 | VIS |
| `.vis-tabla-detail__inner` | VIS | 176 | VIS |
| `.vis-ficha` | VIS | 179 | VIS |
| `.vis-ficha__section` | VIS | 180 | VIS |
| `.vis-ficha__grid` | VIS | 181 | VIS |
| `.vis-ficha__key` | VIS | 182 | VIS |
| `.vis-ficha__value` | VIS | 183 | VIS |
| `.vis-detail-actions` | VIS | 186 | VIS |
| `.vis-itinerario-btn__pill` | VIS | 189 | VIS |
| `.vis-grupos-row` | VIS | 198 | VIS |
| `.vis-grupo-card` | VIS | 199 | VIS |
| `.vis-grupo-card__header` | VIS | 200 | VIS |
| `.vis-grupo-card__body` | VIS | 201 | VIS |
| `.vis-grupo-card__vacio` | VIS | 202 | VIS |
| `.vis-grupo-card__talleres` | VIS | 203 | VIS |
| `.vis-grupo-card__taller-info` | VIS | 205 | VIS |
| `.vis-icon-btn` | VIS | 211 | VIS |
| `.vis-sel-header` | VIS | 227 | VIS |
| `.vis-sel-header__instituto` | VIS | 232 | VIS |
| `.vis-horario-container` | VIS | 236 | VIS |
| `.vis-horario-header` | VIS | 237 | VIS |
| `.vis-turno-selector` | VIS | 238 | VIS |
| `.vis-turno-selector__label` | VIS | 239 | VIS |
| `.vis-turno-dropdown` | VIS | 240 | VIS |
| `.vis-dia-selector` | VIS | 241 | VIS |
| `.vis-dia-selector__text` | VIS | 242 | VIS |
| `.vis-dia-btn` | VIS | 243 | VIS |
| `.vis-horario-wrap` | VIS | 252 | VIS |
| `.vis-horario-area` | VIS | 253 | VIS |
| `.is-active` | VIS | 254 | EVT, REG, VIS |
| `.vis-horario-tiempos` | VIS | 255 | VIS |
| `.vis-horario-tiempo` | VIS | 256 | VIS |
| `.vis-horario-tiempo--sala` | VIS | 257 | VIS |
| `.vis-horario-fila` | VIS | 259 | VIS |
| `.vis-horario-celda` | VIS | 261 | VIS |
| `.vis-horario-celda__nombre` | VIS | 268 | VIS |
| `.vis-horario-celda__meta` | VIS | 269 | VIS |
| `.vis-horario-celda__cupos` | VIS | 270 | VIS |
| `.vis-nivel` | VIS | 271 | VIS |
| `.vis-nivel--preescolar` | VIS | 272 | VIS |
| `.vis-nivel--primaria-alta` | VIS | 273 | — |
| `.vis-nivel--primaria-baja` | VIS | 274 | — |
| `.vis-nivel--secundaria` | VIS | 275 | — |
| `.vis-nivel--preparatoria` | VIS | 276 | — |
| `.vis-nivel--universidad` | VIS | 277 | — |
| `.vis-horario-celda--sala-label` | VIS | 278 | VIS |
| `.vis-horario-celda--llena` | VIS | 280 | VIS |
| `.vis-horario-celda--sin-taller` | VIS | 282 | VIS |
| `.vis-horario-celda--cerrado` | VIS | 282 | VIS |
| `.vis-horario-celda--libre` | VIS | 286 | VIS |
| `.vis-bloque-label` | VIS | 287 | VIS |
| `.vis-celda-badges` | VIS | 292 | — |
| `.vis-grupo-badge` | VIS | 293 | VIS |
| `.vis-grupo-selector` | VIS | 302 | — |
| `.vis-grupo-selector__head` | VIS | 307 | VIS |
| `.vis-grupo-selector__title` | VIS | 308 | VIS |
| `.vis-grupo-selector__item` | VIS | 309 | VIS |
| `.vis-radio` | VIS | 311 | VIS |
| `.vis-radio--selected` | VIS | 313 | — |
| `.vis-todos-btn` | VIS | 314 | VIS |
| `.vis-reserva-bar` | VIS | 318 | VIS |
| `.txt` | VIS | 323 | EVT, REG, VIS |
| `.vis-itin-list` | VIS | 328 | — |
| `.vis-itin-item` | VIS | 329 | — |
| `.vis-itin-item__day` | VIS | 330 | — |
| `.vis-itin-item__main` | VIS | 331 | — |
| `.vis-itin-item__groups` | VIS | 334 | — |
| `.vis-stats` | VIS | 337 | — |
| `.vis-stat` | VIS | 338 | — |
| `.vis-filters` | VIS | 343 | VIS |
| `.field` | VIS | 344 | EVT, REG, VIS |
| `.grupo-block` | VIS | 348 | VIS |
| `.grupo-block__head` | VIS | 349 | VIS |
| `.grupo-remove` | VIS | 351 | VIS |
| `.total-box` | VIS | 353 | VIS |
| `.over` | VIS | 355 | VIS |
| `.vis-grado-hint` | VIS | 359 | — |
| `.vis-grado-hint--alta` | VIS | 361 | — |
| `.vis-grado-hint--baja` | VIS | 362 | — |
| `.is-invalid` | VIS | 365 | REG, VIS |
| `.field__err` | VIS | 368 | VIS |
| `.vis-baja-panel` | VIS | 372 | — |
| `.vis-baja-panel__title` | VIS | 377 | — |
| `.vis-baja-options` | VIS | 378 | — |
| `.vis-adm-nav` | VIS | 385 | — |
| `.vis-adm-nav__trigger` | VIS | 386 | VIS |
| `.vis-adm-nav__panel` | VIS | 395 | VIS |
| `.vis-adm-nav__brand` | VIS | 402 | VIS |
| `.vis-adm-nav__list` | VIS | 405 | VIS |
| `.vis-adm-nav__item` | VIS | 406 | — |
| `.ico` | VIS | 413 | EVT, REG, VIS |
| `.vis-stat-card` | VIS | 416 | VIS |
| `.vis-stat-card__num` | VIS | 420 | VIS |
| `.vis-stat-card__prog` | VIS | 423 | VIS |
| `.vis-stat-card__prog-head` | VIS | 424 | VIS |
| `.vis-stat-card__bar` | VIS | 427 | VIS |
| `.vis-stat-card__bar-fill` | VIS | 428 | VIS |
| `.vis-dash-grid` | VIS | 431 | VIS |
| `.vis-dash-card` | VIS | 432 | VIS |
| `.vis-dash-card__title` | VIS | 433 | VIS |
| `.vis-dash-card__sub` | VIS | 434 | VIS |
| `.vis-dash-kpis` | VIS | 435 | VIS |
| `.vis-kpi` | VIS | 436 | VIS |
| `.vis-tabs` | VIS | 441 | VIS |
| `.vis-tabs__tab` | VIS | 442 | VIS |
| `.vis-barchart` | VIS | 451 | VIS |
| `.bar` | VIS | 452 | EVT, VIS |
| `.bar-label` | VIS | 454 | VIS |
| `.bar-value` | VIS | 455 | VIS |
| `.axis` | VIS | 456 | VIS |
| `.vis-nivel-meter` | VIS | 459 | VIS |
| `.vis-nivel-meter__head` | VIS | 461 | VIS |
| `.vis-nivel-meter__bar` | VIS | 464 | VIS |
| `.vis-nivel-meter__fill` | VIS | 465 | VIS |
| `.vis-asist-celda` | VIS | 468 | VIS |
| `.vis-asist-celda__vacio` | VIS | 470 | VIS |
| `.vis-asist-escuela` | VIS | 471 | VIS |
| `.vis-cfg-estado` | VIS | 475 | VIS |
| `.is-abierta` | VIS | 477 | VIS |
| `.is-cerrada` | VIS | 478 | VIS |
