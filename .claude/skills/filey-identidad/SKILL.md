---
name: filey-identidad
description: Identidad visual de FILEY/UADY — qué color, tipografía, radio, sombra o espaciado corresponde; qué significa cada color de estado; el acento visual de cada dominio (REG, EVT, VIS, STD, TAL); y el contraste mínimo. Úsalo antes de elegir cualquier valor visual, en cualquier stack (HTML estático, plantillas Django, Angular). No dice cómo se comporta la pantalla ni dónde vive el CSS.
---

# FILEY — identidad visual

Este skill responde **¿qué se ve y por qué?**. Los otros tres:

| Necesitas | Skill |
| --- | --- |
| Cuántos pasos, campos u opciones; cuándo se revela cada cosa; cómo se redacta | `filey-ux` |
| Saber si una clase ya existe, en qué capa va el CSS, cómo no duplicar | `filey-ui-componentes` |
| Convertir eso en una plantilla servida (Django) o en un HTML del prototipo | `filey-render` |

Regla: **este archivo decide valores y reglas; nunca lista clases CSS.** El inventario de clases vive en `filey-ui-componentes`.

---

## 1. Paleta: rol de cada color

El azul y el dorado de FILEY están **verificados contra la marca real** (ver [references/identidad-institucional.md](references/identidad-institucional.md)). No se ajustan "a ojo".

| Rol | Token | Cuándo |
| --- | --- | --- |
| Identidad primaria | `--color-azul-institucional` `#01457C` | Barras, encabezados, acciones primarias, fondos profundos |
| Texto sobre claro | `--color-azul-texto` `#00437C` | Títulos y texto enfático; **no** para párrafos largos (usa `--tinta`) |
| Estado presionado/foco | `--color-azul-institucional-enfoque` | `:hover`/`:active` de superficies azules, sidebars |
| Acento institucional | `--color-dorado-encabezado` `#C99213` | Realce, no acción. Un solo elemento dorado por pantalla |
| Texto/fondo neutro | `--tinta`, `--gris-700/500/300/200/100/050`, `--color-blanco` | Todo lo demás |

**Prohibido:** hex suelto en una regla. Si el color no existe como token, se añade el token primero. Lo verifica `./prototipo/scripts/check-ui.sh` (E3).

### Acento por dominio

Cada convocatoria tiene un color que la identifica en toda la app — el usuario debe reconocer en qué módulo está sin leer el título.

| Dominio | Acento | Degradado de banner |
| --- | --- | --- |
| REG (acceso, convocatorias) | Azul institucional | — (es el chasis, no un módulo) |
| STD (stands/expositores) | Azul | `--color-azul-degradado-claro` → `--color-azul-degradado-oscuro` |
| EVT (eventos/actividades) | Dorado | `--color-dorado-encabezado` → `--color-dorado-700` |
| VIS (visitas escolares) | Verde lima | `--color-verde-700` → `--color-verde-degradado-oscuro` |
| TAL (infantil/juvenil) | Verde bosque | ⚠ hoy hex suelto `#1d8a4e`→`#0a6b53`; tokenizar al implementar TAL |

> [!warning] VIS y TAL usan dos verdes distintos
> No es un error a "corregir" unificándolos: son dos convocatorias distintas que conviven en la misma pantalla de REG. Pero **sí** hay que tokenizar el de TAL antes de usarlo en más de un lugar.

---

## 2. Tipografía

- Familia: `--font-filey` (Open Sans → Segoe UI → Helvetica Neue → Arial). **Sin webfont de red**: el prototipo corre en `file://` y la app debe funcionar sin CDN. Si se pide igualar tipografía exacta de filey.org, es decisión del usuario, no del agente.
- Escala en uso: 26px (título de banner) · 20px · 15–16px (cuerpo) · 13–14px (secundario) · 12px (metadatos, mayúsculas).
- Pesos: 800 títulos de banner · 700 encabezados y etiquetas · 600 énfasis · 400 cuerpo.
- Mayúsculas + `letter-spacing: .5px` solo en etiquetas cortas (badges, encabezados de columna). Nunca en frases.

## 3. Forma

| Uso | Token |
| --- | --- |
| Tarjetas, contenedores, tablas | `--radio` (12px) |
| Inputs, botones, chips | `--radio-sm` (8px) |
| Elevación de reposo | `--sombra-sm` |
| Elemento destacado / hover de tarjeta | `--sombra-md` |
| Modal, overlay | `--sombra-lg` |

> [!danger] Tokens muertos — no usar
> `--radio-card`, `--radio-btn`, `--radio-pill` y `--sombra-card` están definidos en `:root` pero tienen **cero usos** en todo el repo. Vienen del export de Figma y nunca se adoptaron. No los uses; están marcados para borrarse.

## 4. Color de estado (semántica, no decoración)

| Significado | Tokens | Se usa en |
| --- | --- | --- |
| Éxito / aceptado / abierto | `--ok-600` texto, `--ok-050` fondo, `--ok-200` borde | Badges, notas, barras de confirmación |
| Atención / pendiente / por vencer | `--warn-600`, `--warn-050`, `--oro-200` | Plazos, revisión en curso |
| Error / rechazado / cerrado | `--err-600`, `--err-050`, `--err-200` | Validación, dictamen negativo |

Regla: **un estado nunca se comunica solo con color.** Siempre color + texto (y en tablas, además, posición o ícono). Daltonismo y capturas en blanco y negro son casos reales en este proyecto (los organizadores imprimen listados).

## 5. Contraste

Mínimo WCAG **AA**: 4.5:1 texto normal, 3:1 texto ≥18px o ≥14px bold, 3:1 bordes de control.

Combinaciones ya validadas: `--color-azul-institucional` sobre blanco · blanco sobre `--color-azul-institucional` · `--tinta` sobre `--gris-050`.
Combinación a evitar: `--color-dorado-encabezado` como **texto** sobre blanco (2.9:1). El dorado va como fondo o borde, con texto oscuro encima.

---

## 6. Lo que ya no vive aquí

Las **leyes de UX** —cuántas opciones, cuántos campos, qué tamaño tiene una acción primaria— y
el **tono de los textos de UI** se mudaron a `filey-ux` el 2026-09-02. No es un movimiento de
orden: este skill se carga cuando alguien pregunta «¿qué color va aquí?», y esas reglas hacen
falta antes, al decidir qué se enseña.

## 7. Antes de dar por buena una decisión visual

- [ ] El valor sale de un token existente; si es nuevo, tiene nombre semántico (no `--azul-2`)
- [ ] El estado se comunica con color **y** texto
- [ ] El contraste cumple AA
- [ ] El acento corresponde al dominio de la pantalla
- [ ] `./prototipo/scripts/check-ui.sh` en verde

Lo de cuántas opciones y campos caben lo comprueba el checklist de `filey-ux` §7.
