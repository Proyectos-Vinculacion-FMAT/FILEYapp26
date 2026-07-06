---
tipo: analisis
fecha: 2026-07-03
dominio: VIS
---

# Análisis de desalineación entre CUs de VIS y el prototipo

Cruza cada CU del índice con las pantallas de `prototipo/VIS/`. La severidad
indica qué tan urgente es resolver la brecha antes de validar el prototipo con
el cliente:

- 🔴 **Alta** — el prototipo omite algo que el CU exige como comportamiento
  visible, o lo contradice.
- 🟡 **Media** — el prototipo lo muestra parcialmente o lo simplifica de manera
  que puede confundir en la validación.
- 🟢 **Baja / sin brecha** — alineado o la diferencia es solo de wording en datos
  de ejemplo.
- ⚫ **No considerado** — fuera del scope inicial por decisión de diseño posterior a la
  redacción del CU. Se conserva en la documentación para trazabilidad y cálculo final
  de esfuerzo de implementación.

> [!note] Naturaleza del prototipo
> El prototipo es un **mockup estático**: ninguna pantalla tiene lógica de negocio
> implementada. `app.js` cubre únicamente interacciones de UI básicas (dropdowns,
> wrap-selects, navegación de día, rejilla de horario). Cualquier brecha sobre
> "filtrado en tiempo real", "validación al vuelo" o "renderizado dinámico" debe
> leerse como algo que **no se espera** del prototipo, sino del sistema final.

---

## Decisiones de diseño que modifican el análisis

Las siguientes decisiones, tomadas después de redactar los CUs originales, tienen
impacto transversal sobre varias brechas:

1. **Sin edición por parte del representante.** Una vez enviado el registro, el
   representante no puede modificar sus datos ni sus grupos, ni a iniciativa propia
   ni por solicitud del administrador. La validación de datos (teléfono, correo,
   campos obligatorios) es responsabilidad del frontend en el momento del envío.

2. **Sin flujo de dictamen.** Al eliminar la edición, el administrador no necesita
   revisar, solicitar cambios, aceptar ni rechazar registros. Los estados
   *Pendiente · Solicitud de cambios · Aceptada · Rechazada* quedan eliminados del
   dominio VIS. El administrador puede editar datos, grupos y reservaciones
   directamente y a su discreción; la comunicación con el representante se hace
   por correo electrónico.

3. **Una propuesta por representante.** Cada cuenta solo puede tener un registro
   de visita escolar activo. `mis-visitas.html` (plural) es redundante; la pantalla
   canónica es `mi-visita.html`.

4. **La selección de talleres la decide el representante.** No hay fecha de
   recepción que condicione prioridad de talleres; el representante elige
   libremente según disponibilidad de horario y día en el momento que entra al
   catálogo.

---

## A. Aplicación (Aplicante)

### CU-VIS-001 — Registrar la propuesta ↔ `formulario-vis.html`

**Estado: 🟡 Media (dos omisiones de campo; validación de frontend pendiente):**

**Qué cubre el prototipo correctamente:**

- Sección 1 (Responsable): nombre, cargo (Director/Docente/Prefecto), correo y
  teléfono pre-rellenados desde la cuenta. ✔
- Sección 2 (Institución): nombre, CCT, sector, turno, nivel, estado, municipio,
  director(a), dirección, teléfono y correo de institución. ✔
- Sección 3 (Grupos): hasta 3 bloques dinámicos con grado, cantidad (max 35) y
  representante por grupo. Contador `total / 105` con aviso de exceso. ✔
- Nivel educativo: incluye Multigrado. ✔

**Brechas:**

| # | Brecha | Origen CU | Severidad |
| --- | --- | --- | --- |
| A1 | El prototipo incluye "Preescolar" en el selector de nivel educativo. El CU no contempla ese nivel: los niveles confirmados son primaria, secundaria, preparatoria, universidad y multigrado. | CU-VIS-001 nota de campos (Junta 3) | 🟡 |
| A2 | El campo "Municipio" no incluye "Cansahcab". La lista del CU cita: Mérida, Tizimín, Cenotillo, Espita, Buctzotz, Cansahcab, Otro. | CU-VIS-001 precisión Elvira 2026-06-29 | 🟡 |
| A3 | La validación de teléfono, correo y campos obligatorios **debe ocurrir en el frontend antes del envío** (decisión de diseño: sin edición posterior). El prototipo no muestra mensajes de error ni bloqueo de envío. | Decisión de diseño | 🟡 |

> **Nota A4 (cerrada):** La fecha de recepción ya no se contempla como campo ni
> como factor de prioridad; la selección de talleres la hace el representante en
> tiempo real según disponibilidad. Sin brecha.

---

### CU-VIS-002 — Editar la propuesta ↔ prototipo

**Estado: ⚫ No considerado para el scope inicial.**

Se decidió que el representante **no puede editar** su registro ni datos de grupos,
ni espontáneamente ni por solicitud del administrador. La pantalla de edición para el aplicante no forma parte del scope inicial. El administrador es el único que puede modificar
datos, y lo hace directamente desde el panel de administración.

---

### CU-VIS-003 — Consultar mi propuesta y su estado ↔ `mi-visita.html`

**Estado: 🟡 Media (pantalla de solo-lectura correcta; flujo de re-reserva pendiente de claridad):**

Al eliminarse los estados de dictamen, `mi-visita.html` ya no necesita mostrar
un badge de *Pendiente / Aceptada / Solicitud de cambios / Rechazada*. La pantalla
como tablero de solo-lectura es el comportamiento correcto.

**Lo que queda pendiente:**

| # | Brecha | Severidad |
| --- | --- | --- |
| A5 | El flujo de **re-reserva** no está prototipado claramente. El representante puede volver al catálogo para cambiar sus reservaciones; al hacerlo, sus reservaciones anteriores se eliminan y entra al flujo de reserva como si fuera escuela nueva. `mi-visita.html` debería mostrar un aviso antes de esa acción. | 🟡 |

> **Nota sobre archivos duplicados:** `mis-visitas.html` (plural) tiene contenido
> idéntico a `mi-visita.html` y ya no tiene razón de existir dado que solo puede
> haber una propuesta por representante. Debe eliminarse.

---

## B. Herramientas de Administración

### CU-VIS-004 — Consultar lista de propuestas ↔ `admin-propuestas.html`

**Estado: ⚫ No considerado para el scope inicial — reformulado como vista general sin dictamen.**

Al no existir dictamen, no hay "propuestas pendientes de revisión" como categoría
separada. Todos los registros de visita escolar están en un único estado operativo
y se gestionan en una sola vista. `admin-propuestas.html` subsiste como la vista
general de registros, pero su semántica cambia: ya no filtra por estado de
dictamen sino que muestra todos los registros con sus datos y permite al
administrador actuar directamente sobre cualquiera.

**Brechas que quedan:**

| # | Brecha | Severidad |
| --- | --- | --- |
| B3 | La vista consolidada es ahora la arquitectura correcta, no un atajo de prototipo. Los filtros existentes (escuela, día, nivel) son suficientes para el nuevo modelo. Sin brecha estructural. | 🟢 |

---

### CU-VIS-005 — Revisar el detalle ↔ panel expandible en `admin-propuestas.html`

**Estado: 🟡 Media (detalle visible; acciones de dictamen eliminadas, acciones de edición pendientes de visibilidad):**

El panel expandible muestra la ficha correctamente. Los botones de dictamen
(Aceptar / Solicitar cambios / Rechazar) ya no son necesarios.

Las acciones que sí corresponden al administrador ("Editar datos / grupos",
"Editar itinerario") ya existen en el panel, pero deben verificarse contra el
flujo real de administración sin dictamen para asegurar que son suficientes y
que su efecto está claro (comunicación posterior por correo al representante).

---

### CU-VIS-006, 007, 008 — Aceptar / Solicitar cambios / Rechazar ↔ prototipo

**Estado: ⚫ No considerados para el scope inicial.**

El flujo de dictamen completo (aceptar, solicitar cambios, rechazar) no forma
parte del scope inicial. El administrador gestiona los
registros directamente sin un paso de aprobación formal.

---

### CU-VIS-009 — Notificar el resultado ↔ prototipo

**Estado: ⚫ No considerado para el scope inicial en su forma original.**

Al no existir dictamen, no hay resultado automático que notificar. La comunicación
del administrador con el representante (sobre cambios en datos, grupos o
reservaciones) se realiza por correo electrónico directo, fuera del sistema.

La única notificación automática que permanece es la confirmación del envío del
registro (ya prototipada en `confirmacion-vis.html`) y el envío del itinerario
final (`itinerario.html`).

---

### CU-VIS-015 — Lista de visitas aceptadas ↔ `admin-propuestas.html`

**Estado: 🟢 Bien cubierto (ahora equivalente a lista general de registros).**

Con la eliminación del dictamen, "visitas aceptadas" pasa a significar
simplemente "registros existentes". `admin-propuestas.html` cubre correctamente
esta vista con filtros por escuela, nivel educativo y día, y la numeralia de totales.

---

### CU-VIS-016 — Ver el detalle de una visita ↔ `admin-propuestas.html` y `admin-escuela.html`

**Estado: 🟡 Media (problema de rotulación en proto-bar):**

`admin-escuela.html` está rotulado como "CU-VIS-016" pero su contenido es un
formulario de alta manual por el administrador, no la vista de detalle de una
visita existente. El detalle real lo cubre el panel expandible de
`admin-propuestas.html`.

**Acción necesaria:** corregir el rótulo del proto-bar de `admin-escuela.html`
(alta manual por admin, CU sin número asignado aún) y de `admin-escuela-edit.html`
(edición de datos por admin, mapeable a CU-VIS-017 extendido).

---

### CU-VIS-017 — Quitar manualmente una visita de un taller ↔ `admin-propuestas.html`

**Estado: 🟡 Media (granularidad de taller individual no implementada; la cancelación opera a nivel de grupo):**

`admin-propuestas.html` expone botones "✕ Cancelar reservaciones G1/G2/G3" (por
grupo completo) y "✕ Cancelar todas las reservaciones" (global). No existe un
selector de taller específico: la granularidad mínima es el grupo completo, no
un taller individual. CU-VIS-017 exige liberar un taller concreto sin afectar
los demás del mismo grupo — esa granularidad no está implementada en el prototipo.

---

## C. Catálogo y Reserva de Talleres (Participante)

### CU-VIS-010 — Consultar el catálogo ↔ `reservar.html` / `admin-reservar.html`

**Estado: 🟡 Media (filtro de nivel no implementado en UI; validación a nivel de reserva pendiente de verificación en JS):**

`reservar.html` tiene selector de turno y navegación de día. El CU exige filtrar
por nivel educativo, día y turno.

**Brechas:**

| # | Brecha | Severidad |
| --- | --- | --- |
| C1 | No hay filtro de nivel educativo en la UI. La nota "El catálogo muestra los talleres del nivel de tu propuesta — Primaria" es incorrecta: el catálogo muestra todos los talleres. La restricción opera al reservar: una escuela no puede asignar un grupo a un taller cuyo nivel no coincida. **Pendiente verificar si esta validación está en `app.js`** o es solo conceptual. | 🟡 |
| C2 | El grid de horario lo genera `app.js`; el HTML estático no contiene talleres de ejemplo. Esto es coherente con la naturaleza de mockup del prototipo y no es una brecha sino una limitación conocida del formato. | 🟢 |
| C3 | El prototipo no diferencia visualmente talleres de `TAL` (cupo limitado) vs actividades de `EVT` (cupo ilimitado / acceso libre). La nota en `reservar.html` lo menciona pero no hay distinción visual en el grid. | 🟡 |
| C4 | **Discrepancia de nivel educativo:** `formulario-vis.html` captura "Primaria" como valor único; el catálogo usa "Primaria alta" y "Primaria baja" como categorías separadas. No hay mapeo definido entre ambas nomenclaturas. Esta brecha afecta la validación de nivel en la reserva (C1) y debe resolverse antes de implementar. | 🔴 |

---

### CU-VIS-011 — Validar cupo ↔ `reservar.html`

**Estado: 🟡 Media (validación post-confirmación descrita en texto; sin representación visual de cupo lleno en el mockup):**

La nota en `reservar.html` describe la validación al confirmar. En el grid no hay
representación de taller con cupo lleno (bloque visual diferenciado). Dado que el
prototipo es un mockup, esto es aceptable para la validación con el cliente siempre
que se explique verbalmente durante la sesión.

El CU especifica que la validación es por cantidad asignada al taller (no el total
del grupo) y que el grupo puede repartirse entre talleres. La nota en `reservar.html`
no explica esta granularidad.

---

### CU-VIS-012 — Reservar talleres ↔ `reservar.html`

**Estado: 🟢 Bien cubierto:**

La lógica de selección libre por asiento está descrita. El flujo de asignar grupo
y confirmar está representado.

**Matiz pendiente:** la regla "un mismo grupo no puede reservar dos talleres en el
mismo bloque" aparece en el prototipo pero no está documentada en CU-VIS-012.
Requiere confirmación del cliente.

---

### CU-VIS-013 — Consultar el itinerario ↔ `itinerario.html`

**Estado: 🟢 Bien cubierto:**

`itinerario.html` muestra lista de talleres reservados, resumen lateral y botón de
confirmación con envío por correo. Alineado con el CU.

---

### CU-VIS-014 — Quitar un taller del itinerario ↔ `itinerario.html` / `mi-visita.html`

**Estado: 🟢 Bien cubierto (con matiz de consistencia entre pantallas):**

Ambas pantallas permiten quitar talleres. `mi-visita.html` permite quitar por grupo
individual (badge clicable) además de quitar el taller completo; `itinerario.html`
solo quita el taller completo. La inconsistencia entre pantallas podría confundir,
pero es un matiz menor para el mockup.

---

## Resumen ejecutivo de brechas

| Pantalla | Acción a realizar | CU afectado | Severidad | Estado |
| --- | --- | --- | --- | --- |
| `reservar.html` | A(1) Resolver discrepancia de nomenclatura Primaria / Primaria alta-baja entre formulario y catálogo | CU-VIS-010 | 🔴 | [✅ Resuelto](#e1) |
| `formulario-vis.html` | A(2) Conservar Preescolar; añadir pill de nivel y talleres de ejemplo | CU-VIS-001 | 🟡 | [✅ Resuelto](#e2) |
| `formulario-vis.html` | A(3) Agregar "Cansahcab" a la lista de municipios | CU-VIS-001 | 🟡 | [✅ Resuelto](#e3) |
| `formulario-vis.html` | A(4) Agregar validación de frontend visible: errores en campos y bloqueo del botón "Enviar" | CU-VIS-001 | 🟡 | [✅ Resuelto](#e4) |
| `mi-visita.html` | A(5) Agregar aviso que explique el efecto de volver al catálogo (elimina reservaciones anteriores) | CU-VIS-003 | 🟡 | [✅ Resuelto](#e5) |
| `admin-propuestas.html` | A(6) Verificar que las acciones de edición directa del admin sean suficientes y estén claras sin flujo de dictamen | CU-VIS-005 | 🟡 | ⏳ Pendiente |
| `reservar.html` | A(7) Corregir nota que dice que el catálogo filtra por nivel — no filtra, la restricción opera al reservar | CU-VIS-010 | 🟡 | [✅ Resuelto](#e6) |
| `reservar.html` | A(8) Verificar si la validación de nivel al asignar un grupo a un taller está en `app.js` o es solo conceptual | CU-VIS-010 | 🟡 | [✅ Resuelto](#e7) |
| `reservar.html` | A(9) Documentar la granularidad de validación de cupo: es por cantidad asignada al taller, no el total del grupo | CU-VIS-011 | 🟡 | [✅ Resuelto](#e8) |
| `admin-propuestas.html` | A(10) Selector de taller específico eliminado con `admin-visitas.html`; cancelación opera a nivel de grupo — granularidad de taller individual pendiente | CU-VIS-017 | 🟡 | [⚠️ Cambio de enfoque](#e9) |
| `admin-escuela.html` | A(11) Corregir rótulo de proto-bar: esta pantalla es alta manual por admin, no CU-VIS-016 | CU-VIS-016 | 🟡 | [✅ Resuelto](#e10) |
| `admin-escuela-edit.html` | A(12) Corregir rótulo de proto-bar: esta pantalla es edición de datos por admin (CU-VIS-016/017) | CU-VIS-016 | 🟡 | [✅ Resuelto](#e11) |
| `mis-visitas.html` | A(13) Eliminar — redundante con `mi-visita.html`; solo existe una propuesta por representante | — | 🟡 | [✅ Resuelto](#e12) |
| `itinerario.html` | A(14) Homogeneizar quitar-por-grupo con `mi-visita.html` (opcional) | CU-VIS-014 | 🟢 | ⏳ Pendiente (opcional) |
| `reservar.html` | A(15) Confirmar con el cliente la regla "un grupo no puede reservar dos talleres en el mismo bloque" | CU-VIS-012 | 🟢 | ⏳ Pendiente cliente |
| `itinerario.html` | Alineado | CU-VIS-013 | 🟢 | 🟢 Alineado |
| `admin-propuestas.html` | Alineado — ahora equivale a lista general de registros | CU-VIS-015 | 🟢 | 🟢 Alineado |
| — | Sin acción — eliminados por decisión de diseño (sin edición ni dictamen) | CU-VIS-002, 006, 007, 008, 009 | ⚫ | ⚫ No considerado |
| — | Sin acción — reformulado: vista única de registros sin estados de dictamen | CU-VIS-004 | ⚫ | ⚫ No considerado |

---

## Concentrado de evidencias

Cada entrada cita el archivo y la línea o rango exactos de la implementación.
Los enlaces de archivo abren el recurso en la línea indicada.

### E(1)

**A(1)** — Hint de sub-nivel Primaria baja/alta junto al campo Grado

- [`app.js` · 15](</prototipo/VIS/app.js#L15>) — declaración de `GROUP_NIVEL`
- [`app.js` · 31–39](</prototipo/VIS/app.js#L31-L39>) — `GRADO_MAP` (mapeo nombre de grado → código pa/pb)
- [`app.js` · 46–57](</prototipo/VIS/app.js#L46-L57>) — función `updateGradoHint`
- [`app.js` · 59–61](</prototipo/VIS/app.js#L59-L61>) — `updateAllGradoHints` (re-pinta al cambiar nivel educativo)
- [`app.js` · 89](</prototipo/VIS/app.js#L89>) — listener en campo Grado
- [`formulario-vis.html` · 119](</prototipo/VIS/aplicantes/formulario-vis.html#L119>) — `id="nivel-educativo"` en el select de nivel
- [`formulario-vis.html` · 185](</prototipo/VIS/aplicantes/formulario-vis.html#L185>) — Grupo 1: `data-field-grado` y `.vis-grado-hint`
- [`formulario-vis.html` · 197](</prototipo/VIS/aplicantes/formulario-vis.html#L197>) — Grupo 2: `data-field-grado` y `.vis-grado-hint`
- [`formulario-vis.html` · 209](</prototipo/VIS/aplicantes/formulario-vis.html#L209>) — Grupo 3: `data-field-grado` y `.vis-grado-hint`
- [`styles.css` · 335–338](</prototipo/VIS/styles.css#L335-L338>) — estilos `.vis-grado-hint`, `--alta`, `--baja`

### E(2)

**A(2)** — Preescolar conservado; pill de nivel añadida; talleres de ejemplo creados

- [`styles.css` · 32](</prototipo/VIS/styles.css#L32>) — token `--vis-nivel-preescolar`
- [`styles.css` · 249](</prototipo/VIS/styles.css#L249>) — clase `.vis-nivel--preescolar`
- [`app.js` · 149](</prototipo/VIS/app.js#L149>) — entrada `pe: { label: 'Preescolar', cls: 'vis-nivel--preescolar' }` en `NIVEL`
- [`talleres-preescolar.html` · 1–(fin)](</prototipo/VIS/talleres-preescolar.html>) — archivo de evidencia con 3 talleres de ejemplo

### E(3)

**A(3)** — "Cansahcab" agregado a las listas de municipios

- [`formulario-vis.html` · 139](</prototipo/VIS/aplicantes/formulario-vis.html#L139>) — opción en formulario del aplicante
- [`admin-escuela.html` · 63](</prototipo/VIS/administradores/admin-escuela.html#L63>) — opción en formulario de alta manual por admin

### E(4)

**A(4)** — Validación de frontend: errores visibles + bloqueo del botón Enviar

- [`formulario-vis.html` · 99](</prototipo/VIS/aplicantes/formulario-vis.html#L99>) — `data-vis-required` en nombre de institución
- [`formulario-vis.html` · 104](</prototipo/VIS/aplicantes/formulario-vis.html#L104>) — `data-vis-required` en CCT
- [`formulario-vis.html` · 144](</prototipo/VIS/aplicantes/formulario-vis.html#L144>) — `data-vis-required` en nombre del director
- [`formulario-vis.html` · 150](</prototipo/VIS/aplicantes/formulario-vis.html#L150>) — `data-vis-required` en dirección
- [`formulario-vis.html` · 156](</prototipo/VIS/aplicantes/formulario-vis.html#L156>) — `data-vis-required` en teléfono
- [`formulario-vis.html` · 163](</prototipo/VIS/aplicantes/formulario-vis.html#L163>) — `data-vis-required` en correo
- [`formulario-vis.html` · 185–211](</prototipo/VIS/aplicantes/formulario-vis.html#L185-L211>) — `data-vis-required` en campos de cada grupo (Grado, Alumnos, Representante)
- [`formulario-vis.html` · 248](</prototipo/VIS/aplicantes/formulario-vis.html#L248>) — botón cambiado a `<button data-vis-submit data-href="...">` (ya no es `<a>`)
- [`app.js` · 514–546](</prototipo/VIS/app.js#L514-L546>) — sección `formValidation`: valida, muestra `.is-invalid`, hace scroll al primer campo vacío
- [`styles.css` · 341–345](</prototipo/VIS/styles.css#L341-L345>) — estilos `.field.is-invalid` y `.field__err`

### E(5)

**A(5)** — Aviso de re-reserva en `mi-visita.html`

- [`mi-visita.html` · 165–170](</prototipo/VIS/aplicantes/mi-visita.html#L165-L170>) — nota `note-warn` antes del botón "Editar itinerario en el catálogo"

### E(6)

**A(7)** — Nota verde corregida en `reservar.html`

- [`reservar.html` · 53–58](</prototipo/VIS/aplicantes/reservar.html#L53-L58>) — texto corregido: catálogo muestra todos los talleres; restricción de nivel opera al reservar

### E(7)

**A(8)** — Validación de nivel educativo implementada en `app.js`

- [`app.js` · 15](</prototipo/VIS/app.js#L15>) — `GROUP_NIVEL`: código de nivel asignado a cada grupo (`G1/G2/G3 → 'pa'`)
- [`app.js` · 207–212](</prototipo/VIS/app.js#L207-L212>) — `data-nivel` añadido a cada celda de taller en `cellHTML`
- [`app.js` · 354–357](</prototipo/VIS/app.js#L354-L357>) — función `nivelCategory` (pa/pb → 'primaria'; se/pr/un → su código)
- [`app.js` · 370–391](</prototipo/VIS/app.js#L370-L391>) — bloqueo cross-level y aviso sub-nivel en `tryToggle`

### E(8)

**A(9)** — Granularidad de cupo documentada en `reservar.html` y `app.js`

- [`reservar.html` · 45–51](</prototipo/VIS/aplicantes/reservar.html#L45-L51>) — descripción de página actualizada: cupo por grupo, todo el grupo o nada
- [`reservar.html` · 112–124](</prototipo/VIS/aplicantes/reservar.html#L112-L124>) — nota informativa: granularidad del cupo explicada
- [`app.js` · 321–330](</prototipo/VIS/app.js#L321-L330) — popup renombrado "Asignar grupo completo" con nota de alumnos totales por grupo

### E(9)

**A(10)** — Cancelación por grupo en `admin-propuestas.html` (reemplaza selector de taller específico)

> **Nota:** `admin-visitas.html` fue eliminado. El markup `.vis-baja-panel` que
> implementaba el selector de taller ya no existe en ningún HTML. El enfoque
> actual opera por grupo completo, no por taller individual. `bajaTaller()` en
> `app.js` y `.vis-baja-panel` en `styles.css` son ahora código muerto.

- [`admin-propuestas.html` · 121–125](</prototipo/VIS/administradores/admin-propuestas.html#L121-L125>) — panel de acciones del detalle: Editar itinerario, Cancelar todas las reservaciones, Editar datos
- [`admin-propuestas.html` · 127–152](</prototipo/VIS/administradores/admin-propuestas.html#L127-L152>) — cards de grupo con botones "✕ Cancelar reservaciones G1/G2/G3"
- [`app.js` · 552–606](</prototipo/VIS/app.js#L552-L606>) — `bajaTaller()`: código muerto; ningún HTML tiene `[data-baja-btn]` ni `.vis-baja-panel`
- [`styles.css` · 347–356](</prototipo/VIS/styles.css#L347-L356>) — estilos `.vis-baja-panel` / `.vis-baja-options` (código muerto)

### E(10)

**A(11)** — Proto-bar de `admin-escuela.html` corregido

- [`admin-escuela.html` · 25–32](</prototipo/VIS/administradores/admin-escuela.html#L25-L32>) — paso renombrado "A4. Alta manual de escuela (admin)"

### E(11)

**A(12)** — Proto-bar de `admin-escuela-edit.html` corregido

- [`admin-escuela-edit.html` · 25–33](</prototipo/VIS/administradores/admin-escuela-edit.html#L25-L33>) — paso renombrado "A4. Editar datos de escuela (CU-VIS-016/017)"

### E(12)

**A(13)** — `mis-visitas.html` eliminado

- Archivo ausente del directorio `prototipo/VIS/`; confirmado por decisión de diseño 3 de este documento (una propuesta por representante → `mi-visita.html` es la pantalla canónica)
