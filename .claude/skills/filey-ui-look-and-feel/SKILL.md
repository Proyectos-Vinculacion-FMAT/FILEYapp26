---
name: filey-ui-look-and-feel
description: Usa este skill cuando generes, edites o revises pantallas HTML/CSS/JS estáticas de prototipos FILEY/UADY (por ejemplo dentro de "prototipo/REG - EVT" o un prototipo nuevo del mismo tipo) y necesites mantener consistencia visual con la identidad institucional FILEY/UADY: pantallas de login, tarjetas de convocatoria, bloques tipo bento numerados, botones, badges de estado, tablas, avisos de prototipo. No cubre generación de componentes Angular de prototipo/STD ni prototipo/common/ (ver sección de alcance).
---

# FILEY/UADY — look & feel para prototipos HTML

## Fuente de verdad (en este orden)

1. **Layout y tokens canónicos:** `prototipo/REG - EVT/styles.css` (variables en `:root`) y las páginas `.html` ya existentes ahí. Si una pantalla nueva se parece a una existente, copia su estructura en vez de inventar una nueva.
2. **Identidad de marca real**, curada una sola vez a partir de filey.org / uady.mx / matematicas.uady.mx: [references/identidad-institucional.md](references/identidad-institucional.md). No vuelvas a hacer scraping de esos sitios en cada tarea — actualiza ese archivo solo si el usuario lo pide explícitamente (los sitios pueden rediseñarse).
3. **Inventario de componentes reutilizables** con sus clases exactas: [references/componentes.md](references/componentes.md).

## Alcance

Este skill cubre **prototipos HTML/CSS/JS estáticos** (como `prototipo/REG - EVT`). NO genera ni modifica componentes Angular de `prototipo/STD` ni toca `prototipo/common/` — la unificación de tokens compartidos entre ambos stacks es una tarea aparte, todavía pendiente (hay una divergencia conocida de paleta/tipografía/radio entre `REG - EVT/styles.css` y `STD/src/styles.scss`). Si la tarea pide tocar STD o common/, detente y avísale al usuario en vez de improvisar la unificación.

## Reglas no negociables

1. Reusa las variables CSS de `:root` en `styles.css`. Nunca metas un hex nuevo suelto en una regla; si de verdad falta un token, agrégalo a `:root` con nombre semántico (sigue el patrón de `--azul-institucional`, `--dorado-encabezado`, etc.) y di para qué sirve.
2. Conserva, sin reinventar su estructura, estos 4 patrones (detalle de clases en `references/componentes.md`):
   - Login con mitad flyer / mitad campos: `.auth-wrap` → `.auth-hero` + `.auth-form`.
   - Tarjeta de convocatoria con header de color + cuerpo + pie: `.conv-card` → `.conv-banner` / `.conv-body` / `.conv-foot`.
   - Bloques tipo bento numerados que guían el orden al usuario: `.section-card > .section-head .num`.
   - Barra superior en letras pequeñas con el aviso de "esto es un prototipo": `.proto-bar`.
3. Botones: usa `.btn` + un modificador existente (`.btn-primary`, `.btn-gold`, `.btn-ghost`, `.btn-special`). No crees estilos de botón inline nuevos.
4. Hipervínculos: en fondo claro, el color de link por default ya está cubierto por `a { color: var(--azul-700) }`. En fondo azul oscuro usa `var(--link-azul-fondo)` con hover `var(--link-azul-fondo-enfoque)` — nunca un link blanco sin un estado de hover distinguible.
5. Estados (badges): usa `.badge` + variante existente (`-open/-closed/-soon/-pending/-accepted/-rejected/-changes`). Si necesitas un estado nuevo, mapéalo a los tokens `--ok-*` / `--warn-*` / `--err-*`, no inventes un color.
6. Responsive: respeta el único breakpoint ya definido (`@media (max-width: 920px)`) y el mismo patrón de colapso (el hero de login se oculta, los grids pasan a 1 columna).

## Checklist antes de dar por terminada una pantalla nueva

- [ ] ¿Solo usa variables de `:root`, ninguna hex suelta en las reglas nuevas?
- [ ] ¿El radio de borde es `var(--radio)` (cards) o `var(--radio-sm)` (inputs/botones), no un valor arbitrario?
- [ ] ¿Las sombras son `var(--sombra-sm/md/lg)`, no `box-shadow` inventado?
- [ ] Si hay tarjetas: ¿tienen banner/header + body + foot, igual que `.conv-card`?
- [ ] Si hay secciones de formulario o de info: ¿usan encabezado numerado (`.section-head .num`) en vez de un `<h3>` suelto?
- [ ] ¿Se agregó/actualizó `.proto-bar` con el paso correspondiente del flujo del prototipo?
- [ ] ¿El aviso de "esto es una demo" vive en `.proto-bar` o `.note`, no como prosa suelta en el body?
