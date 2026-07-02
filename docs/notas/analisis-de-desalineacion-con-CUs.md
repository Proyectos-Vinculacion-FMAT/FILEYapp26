---
tipo: analisis
fecha: 2026-07-02
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

---

## A. Aplicación (Aplicante)

### CU-VIS-001 — Registrar la propuesta ↔ `formulario-vis.html`

**Estado: 🟡 Media (una omisión y una inconsistencia de campo):**

**Qué cubre el prototipo correctamente:**

- Sección 1 (Responsable): nombre, cargo (Director/Docente/Prefecto), correo y
  teléfono pre-rellenados desde la cuenta. ✔
- Sección 2 (Institución): nombre, CCT, sector, turno, nivel, estado (lista
  cerrada Yucatán/Campeche/Quintana Roo), municipio (lista cerrada con Otro…),
  director(a), dirección, teléfono y correo de institución. ✔
- Sección 3 (Grupos): hasta 3 bloques dinámicos con grado, cantidad (max 35) y
  representante por grupo. Contador `total / 105` con aviso de exceso. ✔
- Nivel educativo: incluye Multigrado. ✔

**Brechas:**

| #   | Brecha                                                                                                                                                                                                                                                                                                                                                                                                                               | Origen CU                              | Severidad  |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------- | ---------- |
| A1  | El prototipo incluye "Preescolar" en el selector de nivel educativo (`<option>Preescolar</option>`). El CU no contempla ese nivel: los niveles confirmados son primaria, secundaria, preparatoria, universidad y multigrado. Universidad corre como "público general", no como visita escolar estándar.                                                                                                                              | CU-VIS-001 nota de campos (Junta 3)    | 🟡         |
| A2  | El campo "Municipio" no incluye "Cansahcab" en el prototipo. La lista del CU cita: Mérida, Tizimín, Cenotillo, Espita, Buctzotz, Cansahcab, Otro. El prototipo omite Cansahcab.                                                                                                                                                                                                                                                      | CU-VIS-001 precisión Elvira 2026-06-29 | 🟡         |
| A3  | El CU distingue entre el correo del **responsable** (quien llena el registro, ej. docente) y el correo de **la institución**. El prototipo los captura correctamente en secciones separadas. Pero la sección 1 pre-rellena el teléfono del responsable desde la cuenta; el CU no menciona esa limitación — es una decisión de diseño correcta pero no anotada. Sin brecha funcional, solo un recordatorio de documentar la decisión. | CU-VIS-001 datos de contacto           | 🟢         |
| A4  | El CU cita que el folio y la fecha de recepción los asigna FILEY al recibir el registro. El prototipo los muestra en `confirmacion-vis.html` (folio VIS-2027-001) pero **no** en el formulario mismo. Alineado.                                                                                                                                                                                                                      | CU-VIS-001 precisión Elvira            | 🟢         |

---

### CU-VIS-002 — Editar la propuesta ↔ prototipo

**Estado: 🔴 Alta (sin pantalla propia):**

El CU define que el Aplicante puede editar y reenviar la propuesta mientras
esté en *Pendiente a revisión* o en *Solicitud de cambios*.

El prototipo **no tiene pantalla de edición para el Aplicante**. `mi-visita.html`
(y su clon `mis-visitas.html`) muestra los datos como **solo-lectura** y ofrece
únicamente acciones sobre reservaciones (quitar talleres). No hay botón "Editar
datos del registro" ni flujo que lleve al formulario en modo edición.

La pantalla `admin-escuela-edit.html` existe para el Administrador pero no para
el Aplicante. El flujo de *Solicitud de cambios → Aplicante edita* no está
prototipado en el lado del usuario.

**Acción necesaria:** agregar `editar-vis.html` (o habilitar `formulario-vis.html`
en modo edición) con estado de propuesta visible y botón "Reenviar" — al menos
como pantalla esqueleto para el flujo.

---

### CU-VIS-003 — Consultar mi propuesta y su estado ↔ `mi-visita.html` / `mis-visitas.html`

**Estado: 🟡 Media (el estado de revisión no se muestra explícitamente):**

El prototipo muestra los datos del registro y las reservaciones activas, pero
**no muestra el estado de revisión de la propuesta** (Pendiente · Aceptada ·
Solicitud de cambios · Rechazada).

`mi-visita.html` asume implícitamente que la propuesta ya está aceptada (muestra
reservaciones activas y ofrece ir al catálogo). No hay badge de estado ni aviso
de "Tu propuesta está pendiente de revisión / tienes una solicitud de cambios".

Los estados de `CU-VIS-003` mapean directamente a los badges del sistema
(`.badge-pending`, `.badge-accepted`, `.badge-changes`, `.badge-rejected`), que
ya existen en `styles.css`, pero ninguno aparece en esta pantalla.

**Acción necesaria:** agregar un bloque de estado prominente en la parte superior
de `mi-visita.html` (o en el panel lateral "Resumen") con el badge correspondiente
y, cuando sea "Solicitud de cambios", el enlace a la pantalla de edición (A2 arriba).

> [!note] `mis-visitas.html` vs `mi-visita.html`
> Existen dos archivos con contenido idéntico. El prototipo del paso 8 apunta a
> `mis-visitas.html` desde `formulario-vis.html` y a `mi-visita.html` desde el
> topnav. Hay que consolidarlos o diferenciarlos (lista de propuestas vs detalle).

---

## B. Herramientas de Administración

### CU-VIS-004 — Consultar lista de propuestas ↔ `admin-propuestas.html`

**Estado: 🔴 Alta (pantalla combinada con CU-VIS-015–017, filtros incompletos):**

`admin-propuestas.html` mezcla las propuestas y las visitas aceptadas en una sola
tabla bajo el título "Visitas escolares registradas". El CU-VIS-004 es
específicamente la **lista de propuestas pendientes de dictamen** (filtrable por
estado de revisión), mientras que CU-VIS-015 es la **lista de visitas aceptadas**.

**Brechas:**

| #   | Brecha                                                                                                                                                                                                                                                                                                     | Severidad  |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| B1  | La tabla en `admin-propuestas.html` solo muestra visitas ya aceptadas (con reservaciones). No hay propuestas en estado *Pendiente a revisión* ni *Solicitud de cambios* ni *Rechazada*. El CU-VIS-004 exige poder filtrar por esos estados.                                                                | 🔴         |
| B2  | No hay filtro por **estado de revisión** (Pendiente/Aceptada/Solicitud de cambios/Rechazada) en `admin-propuestas.html`. Los filtros visibles son: buscar escuela, día de visita y nivel educativo — suficientes para CU-VIS-015 pero incompletos para CU-VIS-004.                                         | 🔴         |
| B3  | La columna proto-bar etiqueta la pantalla como `CU-VIS-004…008 / 015…017`, lo que confirma que se intenta cubrir todo en una sola vista. Esta consolidación es válida como atajo de prototipo, pero hay que aclarar en la validación que en producción probablemente serán pestañas o secciones separadas. | 🟡         |

---

### CU-VIS-005 — Revisar el detalle ↔ panel expandible en `admin-propuestas.html`

**Estado: 🟡 Media (detalle visible pero falta la acción de dictamen explícita):**

El detalle inline (fila expandida) muestra ficha de representante, datos de
institución y reservaciones activas. Es suficiente para revisar la propuesta.

Sin embargo, **no hay ningún flujo de dictamen** (botones Aceptar / Solicitar
cambios / Rechazar) en `admin-propuestas.html`. El panel de detalle solo tiene:
"🗓️ Editar itinerario", "✕ Cancelar todas las reservaciones" y "✎ Editar datos
/ grupos". Estos botones son acciones post-aceptación (CU-VIS-016/017), no
acciones de revisión (CU-VIS-005 → CU-VIS-006/007/008).

**Acción necesaria:** agregar botones de dictamen al panel de detalle o crear
una pantalla separada `admin-revisar.html` que muestre la ficha completa con
los tres botones de resolución.

---

### CU-VIS-006, 007, 008 — Aceptar / Solicitar cambios / Rechazar ↔ prototipo

**Estado: 🔴 Alta (ninguno está prototipado):**

No existe ninguna pantalla ni interacción que represente:

- La confirmación de "Aceptar" con la notificación al Aplicante (CU-VIS-006).
- El formulario de "Solicitar cambios" con campo de motivo/observaciones
  (CU-VIS-007).
- El formulario de "Rechazar" con campo de motivo (CU-VIS-008).

Estos tres CUs son el corazón del flujo de revisión y son completamente oscuros
en el prototipo actual. La acción "✕ Cancelar todas las reservaciones" que
aparece en el panel no corresponde a ninguno de ellos (es CU-VIS-017).

**Acción necesaria:** al menos mostrar un modal o pantalla de confirmación para
cada una de estas tres acciones, con el campo de texto de motivo (CU-VIS-007 y
008) y el resultado esperado visible.

---

### CU-VIS-009 — Notificar el resultado ↔ prototipo

**Estado: 🔴 Alta (no existe representación del correo ni de la notificación):**

La notificación automática al Aplicante no tiene ninguna representación visual
en el prototipo. En contraste, `itinerario.html` sí muestra un `.note-green`
que confirma el envío del correo de itinerario ("Enviamos tu itinerario,
la carta de bienvenida y el reglamento…"), pero el correo de dictamen (aceptado/
rechazado/cambios) no tiene equivalente.

`itinerario-admin.html` tiene un botón "Notificar por correo" — eso cubre el
envío manual del itinerario por el admin, no la notificación automática del
sistema al Aplicante que define CU-VIS-009.

**Acción necesaria:** agregar en el flujo de dictamen (o como pantalla separada
tipo confirmación) un mensaje que muestre qué se enviará al Aplicante, coherente
con CU-VIS-009.

---

### CU-VIS-015 — Lista de visitas aceptadas ↔ `admin-visitas.html`

**Estado: 🟢 Bien cubierto (con matiz menor):**

`admin-visitas.html` muestra la tabla de visitas aceptadas con filtros por
escuela, taller y día. Incluye la numeralia (total de alumnos, escuelas aceptadas,
talleres reservados). Alineado con el objetivo del CU.

**Matiz:** el CU menciona filtrar por escuela, taller y fecha; el prototipo
los tiene. La "suma total de alumnos/visitantes" (numeralia) aparece en el
bloque `.vis-stats` (2,915 alumnos). Alineado. 🟢

---

### CU-VIS-016 — Ver el detalle de una visita ↔ `admin-visitas.html` (detalle inline) y `admin-escuela.html`

**Estado: 🟡 Media (problema de rotulación de CU en pantallas):**

`admin-escuela.html` está rotulado en su proto-bar como "A3. Registrar escuela
(CU-VIS-016)" pero su contenido es en realidad un **formulario de alta manual**,
no la vista de detalle de una visita existente. CU-VIS-016 describe ver el
detalle de una visita ya aceptada (datos de la escuela, itinerario, cupos que
ocupa). Ese contenido está cubierto por el panel expandible de `admin-visitas.html`,
no por `admin-escuela.html`.

`admin-escuela-edit.html` también se rotula como "CU-VIS-016" pero es la edición
de datos — más cercana al flujo de CU-VIS-017 (gestión de reservaciones) o a
un CU adicional de edición de datos.

**Acción necesaria:** corregir los rótulos del proto-bar:

- `admin-escuela.html` → CU-VIS-nuevo (registro manual por admin, no numerado aún).
- `admin-escuela-edit.html` → CU-VIS-016/017.
- El detalle real de CU-VIS-016 ya lo cubre `admin-visitas.html`.

---

### CU-VIS-017 — Quitar manualmente una visita de un taller ↔ `admin-visitas.html`

**Estado: 🟡 Media (la acción existe pero está ambigua):**

En `admin-visitas.html` existe el botón "✕ Quitar de un taller (baja)" y la
nota azul "Baja por cancelación imprevista (CU-VIS-017)". Bien.

Sin embargo, el botón no tiene un flujo secundario que muestre **de qué taller
específico** se quita la visita. Con múltiples reservaciones activas (Ciencia
divertida — G1, Taller de ilustración — G3, Dibujo con luz — G1 G3), el botón
"Quitar de un taller" es ambiguo: ¿cuál taller? ¿cuál grupo?

**Acción necesaria:** el botón debería abrir un selector (modal o pantalla) que
liste los talleres activos de esa visita y permita elegir cuál quitar, con
confirmación. Actualmente el prototipo no tiene ese paso intermedio.

En `admin-propuestas.html` también aparece "✕ Cancelar todas las reservaciones"
pero ese botón es distinto de CU-VIS-017 (CU-VIS-017 es *quitar de un taller*,
no cancelar todo).

---

## C. Catálogo y Reserva de Talleres (Participante)

### CU-VIS-010 — Consultar el catálogo ↔ `reservar.html` / `admin-reservar.html`

**Estado: 🟡 Media (filtros incompletos; la pantalla delega en `app.js`)**

`reservar.html` tiene el selector de turno (Matutino/Vespertino) y el selector
de día (prev/next). El CU exige filtrar por **nivel educativo, día y turno**.

**Brechas:**

| #   | Brecha                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Severidad  |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| C1  | No hay filtro de nivel educativo aplicado. La nota en `reservar.html` dice "El catálogo muestra los talleres del nivel de tu propuesta — Primaria", pero **el catálogo muestra todos los talleres sin excepción**; la nota es incorrecta. El CU exige filtrar por nivel educativo de forma explícita.                                                                                                                                                            | 🔴         |
| C2  | El grid de horario (`vis-horario-wrap`) se genera completamente por `app.js`. El HTML estático no muestra ningún taller de ejemplo en el código fuente; depende 100% de JS para renderizar. Esto hace el prototipo difícil de validar sin ejecutar el código.                                                                                                                                                                                                    | 🟡         |
| C3  | CU-VIS-010 distingue entre talleres de `TAL` (cupo limitado) y casos excepcionales de `EVT` (cupo ilimitado). El prototipo no diferencia visualmente ambos tipos. La nota en `reservar.html` menciona "actividades de acceso libre" como excepción, que es el proxy correcto, pero no queda claro de dónde viene esa categoría.                                                                                                                                  | 🟡         |
| C4  | **Discrepancia de nomenclatura de nivel educativo:** el formulario de propuesta (`formulario-vis.html`) captura `Primaria` como una única opción; el catálogo usa píldoras `Primaria alta` y `Primaria baja` como categorías separadas. No hay mapeo definido. Una escuela registrada como "Primaria" no puede saber qué talleres del catálogo corresponden a su grupo. Esta brecha afecta tanto al filtro del catálogo (C1) como al modelo de datos subyacente. | 🔴         |

---

### CU-VIS-011 — Validar cupo ↔ `reservar.html`

**Estado: 🟡 Media (la regla existe en texto pero no hay representación visual del estado de cupo lleno):**

La nota final en `reservar.html` menciona: "Al confirmar, el sistema valida en
tiempo real que los cupos no hayan sido tomados por otra escuela mientras
armabas tu itinerario." Eso cubre la validación post-confirmación.

El CU dice que cuando el cupo es insuficiente, el sistema no permite la reserva
y el Participante regresa al catálogo. En el grid de horario no hay representación
de un taller "cupo lleno" ni de la diferencia entre cupo disponible y cupo
insuficiente para el grupo elegido. Eso está en `app.js` (no en el HTML estático).

**Importante:** el CU especifica que la validación es por **cantidad asignada a
ese taller** (no el total del grupo), y que el grupo puede repartirse. La nota
en `reservar.html` no explica esta granularidad.

---

### CU-VIS-012 — Reservar talleres ↔ `reservar.html`

**Estado: 🟢 Bien cubierto (política resuelta, lógica en JS):**

La cabecera de selección muestra los grupos y sus alumnos. La nota sobre
selección libre por asiento está reflejada en el mensaje informativo inferior.
La política de "selección libre por asiento, sin candados" (Junta 3) se
menciona implícitamente. El flujo de asignar grupo → confirmar está descrito
aunque depende de `app.js` para la interacción.

**Matiz menor:** el prototipo introduce una regla nueva ("un mismo grupo no puede
reservar dos talleres en el mismo bloque") que no está documentada en CU-VIS-012.
Puede ser válida, pero no está en el CU ni en el índice. Requiere confirmación.

---

### CU-VIS-013 — Consultar el itinerario ↔ `itinerario.html`

**Estado: 🟢 Bien cubierto:**

`itinerario.html` muestra la lista de talleres reservados (fecha-hora, nombre,
sala, grupos asignados). El Resumen lateral incluye folio, institución, nivel,
grupos, talleres reservados y día de visita. El botón "Confirmar y recibir por
correo" dispara la nota de confirmación de envío. Bien alineado con el CU.

La distinción "antes de generar el itinerario final" (editable) vs. "después de
confirmar" (solo admin puede cambiar) está sugerida por el botón "Seguir editando"
y la nota de advertencia lateral ("si necesitas dar de baja una actividad por
cancelación imprevista, contacta a la coordinación"). Alineado.

---

### CU-VIS-014 — Quitar un taller del itinerario ↔ `itinerario.html` / `mi-visita.html`

**Estado: 🟢 Bien cubierto (con matiz de granularidad de grupo):**

`itinerario.html` tiene botón "Quitar" por ítem de taller. `mi-visita.html`
tiene tanto "Quitar taller" (quita todos los grupos de esa actividad) como
los badges G1/G3 clicables (quita solo ese grupo). Hay una nota de ayuda que
lo explica. Alineado con la intención de autocorrección del Participante.

**Matiz:** la acción de quitar un grupo individual (clic en badge) está
en `mi-visita.html` pero no en `itinerario.html`, donde solo existe "Quitar"
(taller completo). La consistencia entre ambas pantallas podría confundir.

---

## Resumen ejecutivo de brechas

| CU         | Pantalla                             | Severidad  | Acción principal                                                                                               |
| ---------- | ------------------------------------ | ---------- | -------------------------------------------------------------------------------------------------------------- |
| CU-VIS-001 | `formulario-vis.html`                | 🟡         | Quitar "Preescolar"; agregar "Cansahcab"                                                                       |
| CU-VIS-002 | —                                    | 🔴         | Crear pantalla de edición para el Aplicante                                                                    |
| CU-VIS-003 | `mi-visita.html`                     | 🟡         | Mostrar badge de estado de revisión prominente                                                                 |
| CU-VIS-004 | `admin-propuestas.html`              | 🔴         | Agregar filtro por estado; mostrar propuestas pendientes                                                       |
| CU-VIS-005 | `admin-propuestas.html`              | 🟡         | Agregar acciones de dictamen al panel de detalle                                                               |
| CU-VIS-006 | —                                    | 🔴         | Sin prototipo; crear flujo de aceptación                                                                       |
| CU-VIS-007 | —                                    | 🔴         | Sin prototipo; crear flujo de solicitud de cambios                                                             |
| CU-VIS-008 | —                                    | 🔴         | Sin prototipo; crear flujo de rechazo                                                                          |
| CU-VIS-009 | —                                    | 🔴         | Sin prototipo; mostrar confirmación de notificación                                                            |
| CU-VIS-010 | `reservar.html`                      | 🔴         | Eliminar nota falsa de filtrado; implementar filtro real + resolver discrepancia Primaria / Primaria alta-baja |
| CU-VIS-011 | `reservar.html`                      | 🟡         | Mostrar estado visual de cupo lleno en grid                                                                    |
| CU-VIS-012 | `reservar.html`                      | 🟢         | Revisar regla "un grupo por bloque" (no documentada en CU)                                                     |
| CU-VIS-013 | `itinerario.html`                    | 🟢         | Alineado                                                                                                       |
| CU-VIS-014 | `itinerario.html` + `mi-visita.html` | 🟢         | Homogeneizar quitar-por-grupo entre pantallas                                                                  |
| CU-VIS-015 | `admin-visitas.html`                 | 🟢         | Alineado                                                                                                       |
| CU-VIS-016 | `admin-visitas.html` (inline)        | 🟡         | Corregir rótulos de proto-bar en `admin-escuela.html`                                                          |
| CU-VIS-017 | `admin-visitas.html`                 | 🟡         | Agregar selector de taller específico antes de la baja                                                         |

**Brechas críticas (5 pantallas faltantes o flujos ausentes):**
CU-VIS-002 (edición del Aplicante) · CU-VIS-006 (aceptar) · CU-VIS-007
(solicitar cambios) · CU-VIS-008 (rechazar) · CU-VIS-009 (notificación).
Todas corresponden al flujo de dictamen que está completamente oscuro en el
lado del administrador.
