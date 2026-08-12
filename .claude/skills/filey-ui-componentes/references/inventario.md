<!-- GENERADO por scripts/gen-inventario.sh — no editar a mano. -->
# Inventario CSS del prototipo

Regenerar con `./scripts/gen-inventario.sh` tras cualquier cambio en un `styles.css`.
Fuente: `prototipo/common/styles-base.css` + `prototipo/{DOM}/styles.css`.

**85 tokens · 402 definiciones de clase · 41 sin uso detectado en HTML/JS.**

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
| `--color-dorado-050` | common | `#fff8e6` |
| `--color-negro` | common | `#000000` |
| `--font-filey` | common | `"Open Sans", "Segoe UI", "Helvetica Neue", A…` |
| `--color-morado` | common | `#955FF2` |
| `--color-magenta-oscuro` | common | `#70124C` |
| `--color-verde-lima` | common | `#99BA15` |
| `--color-verde-700` | common | `#839F10` |
| `--color-verde-800` | common | `#6C840B` |
| `--color-verde-degradado-oscuro` | common | `#3F4E00` |
| `--color-verde-tal` | common | `#1d8a4e` |
| `--color-verde-tal-oscuro` | common | `#0a6b53` |
| `--color-rojo` | common | `#CC311D` |
| `--color-rojo-700` | common | `#912111` |
| `--color-rojo-800` | common | `#73190B` |
| `--color-rojo-degradado-oscuro` | common | `#551104` |
| `--tinta` | common | `#1b2330` |
| `--gris-700` | common | `#3f4a5a` |
| `--gris-500` | common | `#6b7686` |
| `--gris-400` | common | `#aab3c0` |
| `--gris-300` | common | `#c8d0db` |
| `--gris-200` | common | `#e2e7ee` |
| `--gris-100` | common | `#eef1f6` |
| `--gris-050` | common | `#f7f9fc` |
| `--ok-600` | common | `#1d8a4e` |
| `--ok-200` | common | `#c9e5d3` |
| `--ok-050` | common | `#e7f6ee` |
| `--warn-800` | common | `#7a5a00` |
| `--warn-600` | common | `#b8860b` |
| `--warn-050` | common | `#fdf6e3` |
| `--oro-200` | common | `#f1e3b0` |
| `--oro-050` | common | `#fbf6e6` |
| `--err-600` | common | `var(--color-rojo)` |
| `--err-200` | common | `#eecac5` |
| `--err-100` | common | `#f7dcd8` |
| `--err-050` | common | `#fbeae8` |
| `--verde-200` | common | `#dbe6ad` |
| `--verde-050` | common | `#f3f7e3` |
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
| `--evt-constancias` | EVT | `#6b46c1;   /* morado de la tarjeta de consta…` |
| `--color-azul-texto` | VIS | `#00437C;             /* alias explícito par…` |
| `--color-dorado-degradado-oscuro` | VIS | `#6E4D03; /* dorado profundo para bordes de d…` |
| `--vis-dia-btn-size` | VIS | `16px;               /* altura de los botones…` |
| `--vis-sala-borde` | VIS | `#9db3c4;              /* separador de la col…` |
| `--vis-radio-dot` | VIS | `#9a9a9a;              /* punto interior del …` |
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
| `.topbar` | common | 106 | EVT, REG, VIS |
| `.topbar-inner` | common | 114 | EVT, REG, VIS |
| `.home` | common | 122 | EVT, REG, VIS |
| `.logo` | common | 125 | EVT, REG, VIS |
| `.brand-text` | common | 126 | EVT, REG, VIS |
| `.topnav` | common | 130 | EVT, REG, VIS |
| `.user-chip` | common | 134 | EVT, REG, VIS |
| `.avatar` | common | 142 | EVT, REG, VIS |
| `.is-admin` | common | 149 | REG, VIS |
| `.page` | common | 153 | EVT, REG, VIS |
| `.page-narrow` | common | 154 | EVT, VIS |
| `.page-wide` | common | 155 | VIS |
| `.breadcrumb` | common | 157 | EVT, VIS |
| `.page-head` | common | 161 | EVT, REG, VIS |
| `.auth-wrap` | common | 166 | EVT, REG |
| `.auth-hero` | common | 171 | EVT, REG |
| `.logo-lg` | common | 179 | EVT, REG |
| `.pills` | common | 182 | EVT, REG |
| `.auth-form` | common | 187 | EVT, REG |
| `.auth-card` | common | 192 | EVT, REG |
| `.sub` | common | 194 | EVT, REG |
| `.auth-foot` | common | 195 | EVT, REG |
| `.otp-row` | common | 198 | REG |
| `.otp-meta` | common | 205 | REG |
| `.field` | common | 208 | EVT, REG, VIS |
| `.hint` | common | 210 | EVT, REG |
| `.req` | common | 211 | EVT, REG, VIS |
| `.opt` | common | 212 | EVT, REG, VIS |
| `.select-wrap` | common | 229 | VIS |
| `.is-open` | common | 257 | VIS |
| `.field-prefill` | common | 268 | EVT, VIS |
| `.tag-auto` | common | 269 | EVT, VIS |
| `.grid-2` | common | 275 | EVT, VIS |
| `.grid-3` | common | 276 | VIS |
| `.radio-row` | common | 278 | EVT, REG |
| `.file-mock` | common | 282 | EVT, REG |
| `.ico` | common | 288 | EVT, REG, VIS |
| `.txt` | common | 289 | EVT, REG, VIS |
| `.multi-input` | common | 293 | EVT, REG |
| `.card` | common | 296 | EVT, VIS |
| `.card-pad` | common | 300 | EVT, VIS |
| `.section-card` | common | 302 | EVT, VIS |
| `.section-head` | common | 303 | EVT, VIS |
| `.num` | common | 308 | EVT, VIS |
| `.section-body` | common | 315 | EVT, VIS |
| `.btn` | common | 317 | EVT, REG, VIS |
| `.btn-primary` | common | 324 | EVT, REG, VIS |
| `.btn-gold` | common | 326 | EVT, REG, VIS |
| `.btn-green` | common | 328 | VIS |
| `.btn-ghost` | common | 330 | EVT, REG, VIS |
| `.btn-special` | common | 334 | EVT, VIS |
| `.btn-block` | common | 336 | EVT, REG |
| `.btn-lg` | common | 337 | EVT, REG, VIS |
| `.form-actions` | common | 339 | EVT, VIS |
| `.spacer` | common | 343 | EVT, VIS |
| `.conv-grid` | common | 346 | EVT, REG |
| `.conv-card` | common | 347 | EVT, REG |
| `.is-closed` | common | 353 | REG |
| `.conv-banner` | common | 354 | EVT, REG |
| `.banner-stand` | common | 360 | EVT, REG |
| `.banner-infantil` | common | 361 | EVT, REG |
| `.banner-eventos` | common | 362 | EVT, REG |
| `.banner-visitas` | common | 363 | EVT, REG |
| `.conv-body` | common | 364 | EVT, REG |
| `.conv-dates` | common | 366 | EVT, REG |
| `.conv-foot` | common | 367 | EVT, REG |
| `.badge` | common | 369 | EVT, REG |
| `.badge-open` | common | 375 | EVT, REG |
| `.badge-closed` | common | 376 | REG |
| `.badge-soon` | common | 377 | REG |
| `.badge-pending` | common | 378 | EVT |
| `.badge-accepted` | common | 379 | EVT |
| `.badge-rejected` | common | 380 | EVT |
| `.badge-changes` | common | 381 | EVT |
| `.info-hero` | common | 384 | EVT |
| `.info-grid` | common | 394 | EVT, VIS |
| `.dl-dates` | common | 396 | EVT |
| `.row` | common | 397 | EVT |
| `.dot` | common | 404 | EVT, REG, VIS, common |
| `.cupos` | common | 406 | EVT |
| `.cupo` | common | 407 | EVT |
| `.top` | common | 410 | EVT |
| `.bar` | common | 413 | EVT, VIS |
| `.full` | common | 415 | EVT |
| `.req-list` | common | 417 | EVT |
| `.ck` | common | 419 | EVT |
| `.types-row` | common | 421 | EVT |
| `.type-pill` | common | 422 | EVT |
| `.cta-bar` | common | 424 | EVT, VIS |
| `.table` | common | 433 | EVT |
| `.folio` | common | 437 | EVT, VIS |
| `.confirm-card` | common | 440 | EVT, VIS |
| `.check` | common | 441 | EVT, VIS |
| `.folio-box` | common | 447 | EVT, VIS |
| `.note` | common | 456 | EVT, REG, VIS |
| `.note-info` | common | 461 | EVT, REG, VIS |
| `.note-warn` | common | 462 | EVT, REG, VIS |
| `.note-gold` | common | 463 | EVT, REG |
| `.closed-overlay` | common | 465 | REG |
| `.proto-bar` | common | 472 | EVT, REG, VIS |
| `.proto-bar-inner` | common | 476 | EVT, REG, VIS |
| `.sep` | common | 479 | EVT, REG, VIS |
| `.footer` | common | 483 | EVT, REG, VIS |
| `.footer-inner` | common | 487 | EVT, REG, VIS |
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
| `.admin-body` | EVT | 15 | EVT |
| `.sidebar` | EVT | 17 | EVT |
| `.side-section` | EVT | 26 | EVT |
| `.side-nav` | EVT | 28 | EVT |
| `.side-link` | EVT | 29 | EVT |
| `.ico` | EVT | 36 | EVT, REG, VIS |
| `.active` | EVT | 37 | EVT |
| `.is-disabled` | EVT | 41 | — |
| `.admin-main` | EVT | 44 | EVT |
| `.admin-toolbar` | EVT | 45 | EVT |
| `.menu-btn` | EVT | 49 | EVT |
| `.crumb` | EVT | 54 | EVT |
| `.admin-content` | EVT | 55 | EVT |
| `.topbar` | EVT | 58 | EVT, REG, VIS |
| `.admin` | EVT | 58 | EVT |
| `.topbar-inner` | EVT | 58 | EVT, REG, VIS |
| `.chip-modulo` | EVT | 59 | — |
| `.chips` | EVT | 66 | EVT |
| `.chip` | EVT | 67 | EVT, REG |
| `.is-active` | EVT | 73 | EVT, REG, VIS |
| `.count` | EVT | 74 | EVT |
| `.toolbar-row` | EVT | 77 | EVT |
| `.searchbox` | EVT | 78 | EVT |
| `.stat-grid` | EVT | 88 | EVT |
| `.stat-card` | EVT | 89 | EVT |
| `.k` | EVT | 93 | EVT |
| `.v` | EVT | 94 | EVT |
| `.foot` | EVT | 95 | EVT |
| `.accent-blue` | EVT | 96 | EVT |
| `.accent-gold` | EVT | 97 | EVT |
| `.accent-ok` | EVT | 98 | EVT |
| `.accent-warn` | EVT | 99 | EVT |
| `.accent-err` | EVT | 100 | EVT |
| `.btn-row` | EVT | 103 | EVT |
| `.link-arrow` | EVT | 104 | EVT |
| `.modal-back` | EVT | 107 | EVT |
| `.modal` | EVT | 112 | EVT |
| `.modal-head` | EVT | 116 | EVT |
| `.modal-body` | EVT | 119 | EVT |
| `.modal-foot` | EVT | 120 | EVT |
| `.cal-wrap` | EVT | 123 | EVT |
| `.cal-side` | EVT | 124 | EVT |
| `.cal-panel` | EVT | 125 | EVT |
| `.cal-main` | EVT | 128 | EVT |
| `.cal-toolbar` | EVT | 129 | EVT |
| `.month` | EVT | 130 | EVT |
| `.cal-nav` | EVT | 131 | EVT |
| `.cal-grid` | EVT | 134 | EVT |
| `.dow` | EVT | 135 | EVT |
| `.cal-cell` | EVT | 136 | — |
| `.num` | EVT | 138 | EVT, VIS |
| `.out` | EVT | 139 | — |
| `.today` | EVT | 140 | — |
| `.cal-event` | EVT | 142 | — |
| `.ev-apertura` | EVT | 147 | EVT |
| `.ev-cierre` | EVT | 148 | EVT |
| `.ev-notif` | EVT | 149 | EVT |
| `.ev-ajustes` | EVT | 150 | EVT |
| `.ev-asignacion` | EVT | 151 | EVT |
| `.ev-constancias` | EVT | 152 | EVT |
| `.date-list` | EVT | 155 | EVT |
| `.date-item` | EVT | 156 | EVT |
| `.swatch` | EVT | 157 | EVT |
| `.lbl` | EVT | 158 | EVT |
| `.val` | EVT | 159 | — |
| `.sched` | EVT | 163 | EVT |
| `.time-col` | EVT | 167 | EVT |
| `.slot` | EVT | 168 | EVT |
| `.act` | EVT | 169 | EVT |
| `.clash` | EVT | 175 | EVT |
| `.free` | EVT | 176 | EVT |
| `.rep-badge` | EVT | 179 | EVT |
| `.salon-th` | EVT | 185 | — |
| `.sala-th` | EVT | 186 | — |
| `.aforo-badge` | EVT | 187 | — |
| `.mock-banner` | EVT | 195 | EVT |
| `.prg-layout` | EVT | 205 | EVT |
| `.rail` | EVT | 208 | EVT |
| `.hint` | EVT | 210 | EVT, REG |
| `.rail-item` | EVT | 211 | EVT |
| `.is-selected` | EVT | 217 | EVT |
| `.grip` | EVT | 218 | EVT |
| `.r-body` | EVT | 219 | EVT |
| `.rail-empty` | EVT | 221 | EVT |
| `.modal-wide` | EVT | 224 | EVT |
| `.evt-dialog` | EVT | 225 | EVT |
| `.evt-form` | EVT | 226 | EVT |
| `.evt-row` | EVT | 227 | EVT |
| `.ic` | EVT | 229 | EVT |
| `.f` | EVT | 230 | EVT |
| `.big` | EVT | 232 | EVT |
| `.evt-preview` | EVT | 235 | EVT |
| `.pv-head` | EVT | 236 | EVT |
| `.nav` | EVT | 237 | EVT |
| `.day-mini` | EVT | 239 | EVT |
| `.drow` | EVT | 240 | EVT |
| `.dh` | EVT | 242 | EVT |
| `.dcell` | EVT | 243 | EVT |
| `.ev-block` | EVT | 244 | EVT |
| `.grab-dot` | EVT | 248 | EVT |
| `.top` | EVT | 249 | EVT |
| `.bot` | EVT | 250 | EVT |
| `.taken` | EVT | 251 | — |
| `.mini-act` | EVT | 251 | — |
| `.pv-foot` | EVT | 252 | EVT |
| `.banner-infantil` | VIS | 45 | EVT, REG |
| `.btn-green` | VIS | 48 | VIS |
| `.auth-hero` | VIS | 52 | EVT, REG |
| `.is-vis` | VIS | 52 | VIS |
| `.section-card` | VIS | 59 | EVT, VIS |
| `.section-head` | VIS | 59 | EVT, VIS |
| `.num` | VIS | 59 | EVT, VIS |
| `.btn-danger` | VIS | 62 | VIS |
| `.btn-sm` | VIS | 64 | VIS |
| `.note-green` | VIS | 67 | VIS |
| `.note-err` | VIS | 68 | VIS |
| `.vis-estado` | VIS | 78 | — |
| `.vis-estado__dot` | VIS | 83 | — |
| `.vis-estado--abierta` | VIS | 84 | — |
| `.vis-estado--cerrada` | VIS | 86 | — |
| `.vis-banner` | VIS | 90 | VIS |
| `.vis-banner__badge` | VIS | 96 | VIS |
| `.vis-banner__badge-dot` | VIS | 102 | VIS |
| `.vis-banner__badge-label` | VIS | 103 | VIS |
| `.vis-banner__title` | VIS | 104 | VIS |
| `.vis-banner__desc` | VIS | 105 | VIS |
| `.vis-bento-layout` | VIS | 108 | VIS |
| `.vis-bento-left` | VIS | 109 | VIS |
| `.vis-bento-right` | VIS | 110 | VIS |
| `.vis-bento` | VIS | 112 | VIS |
| `.vis-bento__header` | VIS | 117 | VIS |
| `.vis-bento__num` | VIS | 121 | VIS |
| `.vis-bento__title` | VIS | 126 | VIS |
| `.vis-bento__body` | VIS | 127 | VIS |
| `.vis-bento__list` | VIS | 128 | VIS |
| `.vis-bento__item` | VIS | 129 | VIS |
| `.vis-bento__kv` | VIS | 132 | VIS |
| `.vis-bento__kv-label` | VIS | 137 | VIS |
| `.vis-bento__kv-value` | VIS | 138 | VIS |
| `.vis-cupo` | VIS | 141 | VIS |
| `.vis-cupo__row` | VIS | 143 | VIS |
| `.vis-cupo__dia` | VIS | 144 | VIS |
| `.vis-cupo__count` | VIS | 145 | VIS |
| `.vis-cupo__nota` | VIS | 146 | VIS |
| `.vis-cupo__bar-bg` | VIS | 147 | VIS |
| `.vis-cupo__bar-fill` | VIS | 148 | VIS |
| `.vis-cupo__bar-fill--magenta` | VIS | 149 | VIS |
| `.vis-cupo__bar-fill--lleno` | VIS | 150 | VIS |
| `.vis-tabla-wrap` | VIS | 153 | VIS |
| `.vis-tabla` | VIS | 154 | VIS |
| `.vis-row` | VIS | 161 | VIS |
| `.folio` | VIS | 162 | EVT, VIS |
| `.vis-tabla__toggle` | VIS | 163 | VIS |
| `.vis-tabla__toggle-icon` | VIS | 169 | VIS |
| `.is-open` | VIS | 171 | VIS |
| `.vis-tabla__row-detail` | VIS | 173 | VIS |
| `.vis-tabla-detail` | VIS | 177 | VIS |
| `.vis-tabla-detail__inner` | VIS | 178 | VIS |
| `.vis-ficha` | VIS | 181 | VIS |
| `.vis-ficha__section` | VIS | 182 | VIS |
| `.vis-ficha__grid` | VIS | 183 | VIS |
| `.vis-ficha__key` | VIS | 184 | VIS |
| `.vis-ficha__value` | VIS | 185 | VIS |
| `.vis-detail-actions` | VIS | 188 | VIS |
| `.vis-itinerario-btn__pill` | VIS | 191 | VIS |
| `.vis-grupos-row` | VIS | 200 | VIS |
| `.vis-grupo-card` | VIS | 201 | VIS |
| `.vis-grupo-card__header` | VIS | 202 | VIS |
| `.vis-grupo-card__body` | VIS | 203 | VIS |
| `.vis-grupo-card__vacio` | VIS | 204 | VIS |
| `.vis-grupo-card__talleres` | VIS | 205 | VIS |
| `.vis-grupo-card__taller-info` | VIS | 207 | VIS |
| `.vis-icon-btn` | VIS | 213 | VIS |
| `.vis-sel-header` | VIS | 229 | VIS |
| `.vis-sel-header__instituto` | VIS | 234 | VIS |
| `.vis-horario-container` | VIS | 238 | VIS |
| `.vis-horario-header` | VIS | 239 | VIS |
| `.vis-turno-selector` | VIS | 240 | VIS |
| `.vis-turno-selector__label` | VIS | 241 | VIS |
| `.vis-turno-dropdown` | VIS | 242 | VIS |
| `.vis-dia-selector` | VIS | 243 | VIS |
| `.vis-dia-selector__text` | VIS | 244 | VIS |
| `.vis-dia-btn` | VIS | 245 | VIS |
| `.vis-horario-wrap` | VIS | 254 | VIS |
| `.vis-horario-area` | VIS | 255 | VIS |
| `.is-active` | VIS | 256 | EVT, REG, VIS |
| `.vis-horario-tiempos` | VIS | 257 | VIS |
| `.vis-horario-tiempo` | VIS | 258 | VIS |
| `.vis-horario-tiempo--sala` | VIS | 259 | VIS |
| `.vis-horario-fila` | VIS | 261 | VIS |
| `.vis-horario-celda` | VIS | 263 | VIS |
| `.vis-horario-celda__nombre` | VIS | 270 | VIS |
| `.vis-horario-celda__meta` | VIS | 271 | VIS |
| `.vis-horario-celda__cupos` | VIS | 272 | VIS |
| `.vis-nivel` | VIS | 273 | VIS |
| `.vis-nivel--preescolar` | VIS | 274 | VIS |
| `.vis-nivel--primaria-alta` | VIS | 275 | — |
| `.vis-nivel--primaria-baja` | VIS | 276 | — |
| `.vis-nivel--secundaria` | VIS | 277 | — |
| `.vis-nivel--preparatoria` | VIS | 278 | — |
| `.vis-nivel--universidad` | VIS | 279 | — |
| `.vis-horario-celda--sala-label` | VIS | 280 | VIS |
| `.vis-horario-celda--llena` | VIS | 282 | VIS |
| `.vis-horario-celda--sin-taller` | VIS | 284 | VIS |
| `.vis-horario-celda--cerrado` | VIS | 284 | VIS |
| `.vis-horario-celda--libre` | VIS | 288 | VIS |
| `.vis-bloque-label` | VIS | 289 | VIS |
| `.vis-celda-badges` | VIS | 294 | — |
| `.vis-grupo-badge` | VIS | 295 | VIS |
| `.vis-grupo-selector` | VIS | 304 | — |
| `.vis-grupo-selector__head` | VIS | 310 | VIS |
| `.vis-grupo-selector__title` | VIS | 311 | VIS |
| `.vis-grupo-selector__item` | VIS | 312 | VIS |
| `.vis-grupo-selector__item-text` | VIS | 314 | VIS |
| `.vis-radio` | VIS | 315 | — |
| `.vis-radio--selected` | VIS | 317 | — |
| `.vis-todos-btn` | VIS | 318 | VIS |
| `.vis-grupo-selector__item--conflict` | VIS | 323 | — |
| `.vis-grupo-selector__actions` | VIS | 327 | VIS |
| `.btn` | VIS | 328 | EVT, REG, VIS |
| `.vis-ficha__tag` | VIS | 332 | VIS |
| `.vis-ficha__titulo` | VIS | 333 | VIS |
| `.vis-ficha__campo` | VIS | 334 | VIS |
| `.vis-ficha__resena` | VIS | 335 | VIS |
| `.vis-ficha__meta` | VIS | 336 | VIS |
| `.vis-reserva-bar` | VIS | 341 | VIS |
| `.txt` | VIS | 346 | EVT, REG, VIS |
| `.vis-itin-list` | VIS | 351 | — |
| `.vis-itin-item` | VIS | 352 | — |
| `.vis-itin-item__day` | VIS | 353 | — |
| `.vis-itin-item__main` | VIS | 354 | — |
| `.vis-itin-item__groups` | VIS | 357 | — |
| `.vis-stats` | VIS | 360 | — |
| `.vis-stat` | VIS | 361 | — |
| `.vis-filters` | VIS | 366 | VIS |
| `.field` | VIS | 367 | EVT, REG, VIS |
| `.grupo-block` | VIS | 371 | VIS |
| `.grupo-block__head` | VIS | 372 | VIS |
| `.grupo-remove` | VIS | 374 | VIS |
| `.total-box` | VIS | 376 | VIS |
| `.over` | VIS | 378 | VIS |
| `.vis-grado-hint` | VIS | 382 | — |
| `.vis-grado-hint--alta` | VIS | 384 | — |
| `.vis-grado-hint--baja` | VIS | 385 | — |
| `.is-invalid` | VIS | 388 | REG, VIS |
| `.field__err` | VIS | 391 | VIS |
| `.vis-baja-panel` | VIS | 395 | — |
| `.vis-baja-panel__title` | VIS | 400 | — |
| `.vis-baja-options` | VIS | 401 | — |
| `.vis-adm-nav` | VIS | 408 | — |
| `.vis-adm-nav__trigger` | VIS | 409 | VIS |
| `.vis-adm-nav__panel` | VIS | 418 | VIS |
| `.vis-adm-nav__brand` | VIS | 425 | VIS |
| `.vis-adm-nav__list` | VIS | 428 | VIS |
| `.vis-adm-nav__item` | VIS | 429 | — |
| `.ico` | VIS | 436 | EVT, REG, VIS |
| `.vis-stat-card` | VIS | 439 | VIS |
| `.vis-stat-card__num` | VIS | 443 | VIS |
| `.vis-stat-card__prog` | VIS | 446 | VIS |
| `.vis-stat-card__prog-head` | VIS | 447 | VIS |
| `.vis-stat-card__bar` | VIS | 450 | VIS |
| `.vis-stat-card__bar-fill` | VIS | 451 | VIS |
| `.vis-dash-grid` | VIS | 454 | VIS |
| `.vis-dash-card` | VIS | 455 | VIS |
| `.vis-dash-card__title` | VIS | 456 | VIS |
| `.vis-dash-card__sub` | VIS | 457 | VIS |
| `.vis-dash-kpis` | VIS | 458 | VIS |
| `.vis-kpi` | VIS | 459 | VIS |
| `.vis-tabs` | VIS | 464 | VIS |
| `.vis-tabs__tab` | VIS | 465 | VIS |
| `.vis-barchart` | VIS | 474 | VIS |
| `.bar` | VIS | 475 | EVT, VIS |
| `.bar-label` | VIS | 477 | VIS |
| `.bar-value` | VIS | 478 | VIS |
| `.axis` | VIS | 479 | VIS |
| `.vis-nivel-meter` | VIS | 482 | VIS |
| `.vis-nivel-meter__head` | VIS | 484 | VIS |
| `.vis-nivel-meter__bar` | VIS | 487 | VIS |
| `.vis-nivel-meter__fill` | VIS | 488 | VIS |
| `.vis-asist-celda` | VIS | 491 | VIS |
| `.vis-asist-celda__vacio` | VIS | 493 | VIS |
| `.vis-asist-escuela` | VIS | 494 | VIS |
| `.vis-cfg-estado` | VIS | 498 | VIS |
| `.is-abierta` | VIS | 500 | VIS |
| `.is-cerrada` | VIS | 501 | VIS |
