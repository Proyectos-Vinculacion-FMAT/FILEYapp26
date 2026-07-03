---
estado: propuesta
version: 0.4
tags:
  - tipo/indice
  - dom/prg
fecha: 2026-06-24
fecha_actualizacion: 2026-06-29
---
# CU-PRG — Índice de casos de uso (Programación)

Inventario de casos de uso del dominio **Programación** (`PRG`): armado del programa a
partir de las actividades aceptadas (`EVT`/`TAL`), notificación/confirmación de la
asignación, y visibilidad/exportación. Homologado en la
[Junta 3 con Equipo de desarrollo](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md>);
la redacción detallada (flujo principal, alternos y excepciones) sigue sujeta a revisión.
Las notas, los ajustes de homologación y la evidencia que sustenta cada CU se concentran al
final de este índice.

**Actores:** Administrador · Participante · Todos · Sistema.

## A. Armado del programa

- [CU-PRG-001 Consultar lista de actividades de mi panel](<A - Armado del programa/CU-PRG-001 Consultar lista de actividades de mi panel.md>)
- [CU-PRG-002 Asignar una programación a una actividad](<A - Armado del programa/CU-PRG-002 Asignar una programación a una actividad.md>)
- [CU-PRG-003 Editar una programación de una actividad](<A - Armado del programa/CU-PRG-003 Editar una programación de una actividad.md>)
- [CU-PRG-004 Eliminar una programación de una actividad](<A - Armado del programa/CU-PRG-004 Eliminar una programación de una actividad.md>)

## B. Notificación y confirmación de asignación

- [CU-PRG-008 Notificar al Participante su fecha, sala y horario asignados (segunda notificación)](<B - Notificación y confirmación/CU-PRG-008 Notificar al Participante su fecha, sala y horario asignados (segunda notificación).md>)
- [CU-PRG-009 El Participante confirma su asistencia o incomparecencia al horario asignado](<B - Notificación y confirmación/CU-PRG-009 El Participante confirma su asistencia o incomparecencia al horario asignado.md>)

## C. Visibilidad y exportación

- [CU-PRG-010 Consultar el programa publicado mediante su URL estática](<C - Visibilidad y exportación/CU-PRG-010 Consultar el programa publicado mediante su URL estática.md>)
- [CU-PRG-011 Exportar el programa a Excel o Word para uso interno](<C - Visibilidad y exportación/CU-PRG-011 Exportar el programa a Excel o Word para uso interno.md>)

---

## Notas y aclaraciones

> [!note] Dos programas independientes
> Son **dos programas independientes**: uno de eventos y uno de talleres. Cualquier
> Administrador puede entrar a cualquiera de los dos paneles; quién edita cuál se decide
> de manera interna, no por permisos del sistema. Solo el programa de **talleres** admite
> repetir una misma actividad para llenar huecos (varias **programaciones** de la misma
> actividad). La fecha, sala y horario los asigna el Administrador, no el
> Aplicante/Participante.

<!-- -->

> [!note] Precisión interna (2026-06-29) — dónde viven realmente estos CUs
> El armado del programa **no** es una pantalla aparte: vive dentro del mismo listado de
> propuestas/actividades de cada panel (`EVT` o `TAL`). Mientras la propuesta está pendiente de
> revisión, ese renglón muestra el botón **"Revisar"**; en cuanto el Administrador la Acepta, el
> mismo renglón cambia ese botón por **"Programar"** (dispara CU-PRG-002). No se puede programar
> antes de aceptar: la secuencia siempre es revisión → aceptación → programación. Cada panel
> tiene además un botón propio de **visualización del horario**, que muestra el estado actual de
> la programación (equivalente a CU-PRG-001, ya filtrado a ese panel).

<!-- -->

> [!note] Precisión interna (2026-06-29) — guardado implícito, sin botón de "guardar"
> No existe un paso de "guardar el programa preliminar": programar, mover o eliminar una
> programación (CU-PRG-002 a CU-PRG-004) queda guardado de inmediato. El programa conserva
> siempre el estado en el que se deja. Notificar al Participante (CU-PRG-008) es, por eso, una
> acción aparte y a discreción del Administrador —por actividad o de forma masiva—, no algo que
> se dispare al guardar.

<!-- -->

> [!warning] Hueco conocido (R5 del análisis de archivos)
> Estos casos de uso modelan asignar/editar/quitar actividades **aceptadas**, pero **no**
> contemplan que el Administrador agregue al calendario entradas que **no** provienen de una
> propuesta aceptada (artísticos capturados solo para control, o ajustes manuales de la
> "pulida final"). Pendiente de decidir si se añade un CU de entrada manual al programa. Ver
> R5 en el [Análisis de archivos proporcionados](<../../soporte/extraido/Analisis de archivos proporcionados.md>).
> Evidencia real de este hueco (2026-06-29): el borrador de
> [Agenda escuelas — Programa para revisión](<../../soporte/extraido/Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Agenda%20escuelas.%20Programa%20para%20revisi%C3%B3n.md>)
> incluye bloques como "Salón 6. APARTADO — Hipólito": un bloque de horario reservado/bloqueado
> para uso de otro coordinador, sin una actividad ni propuesta aceptada detrás todavía.

<!-- -->

> [!success] D2 resuelta — no hay CRUD de bloques de horario, en ningún dominio
> La Junta 3 con organizadores FILEY resolvió que los bloques de horario **no tienen CRUD** ni en
> `PRG` ni en `SAL` (ver D2 en la
> [Junta 3 con Equipo de desarrollo](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d2--dominio-del-crud-de-bloques-de-horario-prg--sal>)
> y la aclaración en [RSM - Junta 3 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>)). Quedan **hardcodeados por panel**:
> 1:15 en el panel de Eventos, 1:00 (50 min de actividad + 10 min de descanso) en el de Talleres.
> Una sala no tiene ningún horario relacionado al crearse (ver `SAL/CU-SAL Índice.md`); es el
> panel de programación el que divide el horario en esos bloques fijos según corresponda. Por
> eso CU-PRG-002 ya no tiene una precondición de "bloques configurados": los bloques son una
> propiedad fija del panel, no un dato que se cree o edite.

<!-- -->

> [!success] D3 resuelta — notificaciones por módulo, sin bandeja transversal
> Afecta a CU-PRG-009: la Junta 3 con organizadores FILEY descartó la bandeja transversal; las
> notificaciones se consultan **por módulo/panel** (ver D3 en la
> [Junta 3 con Equipo de desarrollo](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d3--modelo-de-notificaciones-reg--prg>)
> y la aclaración en [RSM - Junta 3 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>)). Esto es consistente con que la
> revisión de propuestas también vive por dominio (`EVT`, `TAL`, `STD`, `VIS`) y no en `REG`: cada
> panel de administrador tiene su propio apartado de notificaciones, visible solo para
> administradores de ese panel.

## Ajustes de la Junta 3 (homologación)

- **CU-PRG-005** (Programar una misma actividad en varias ocasiones) se **absorbe en CU-PRG-002**: asignar es el caso único, repetirlo es una capacidad de ese mismo caso de uso.
- **CU-PRG-006** (Validar que el aforo del grupo no supere el aforo de la sala) **sale de `PRG`**: es responsabilidad del core de Visitas escolares (`VIS`), donde se modela como validación de **cupo**.
- **CU-PRG-007** (Validar que la sala esté disponible) se **absorbe en CU-PRG-002** como regla de la asignación: la alerta de empalme no bloquea la asignación ni su guardado (implícito), pero sí impide notificar a los participantes afectados hasta resolverse.
- **CU-PRG-012** (Consultar el programa publicado en la web app) se **unifica con CU-PRG-010**: ambos describen la misma Visualización de programa por URL estática.

La numeración de CUs es solo de conteo y no se reutiliza ni se recorre tras estas fusiones/bajas.

## Artefactos relacionados

- [`Modelo de datos - Programación.md`](<Modelo de datos - Programación.md>) — entidades y datos que el sistema almacena (Actividad, Programación, Notificación, RespuestaProgramación).

## Concentrado de evidencias

- CU-PRG-001: renombre y alcance acordados en [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) ("se consultan las actividades... sin importar su estado de programación") y en [§4.1 Administrador, punto 3](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- CU-PRG-002: renombrado de "Asignar una actividad a una sala y a uno o varios bloques de horario" a "Asignar una programación a una actividad" (precisión interna, 2026-06-29), para nombrar directamente la acción y dejar la explicación dentro del documento; absorbe CU-PRG-005 y CU-PRG-007 según [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) y [§4.1, puntos 4–6](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>); duración fija y hardcodeada del bloque, distinta por panel — **1:15** en el panel de Eventos, **1:00** (50 min de actividad + 10 min de descanso) en el panel de Talleres — resuelto en la Junta 3 con organizadores FILEY (ver [RSM - Junta 3 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>)); antecedente en [Junta 2 con organizadores FILEY — Horarios y bloques de actividades](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#horarios-y-bloques-de-actividades>). El disparador real (botón "Programar" que reemplaza a "Revisar" tras aceptar la propuesta) y el guardado implícito (sin botón de "guardar el programa") son precisión interna, 2026-06-29 (ver Notas y aclaraciones).

- CU-PRG-003: renombrado de "Editar la asignación (sala u horario) de una actividad ya programada" a "Editar una programación de una actividad" (precisión interna, 2026-06-29); nota "editar = mover" en [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) y [§4.1, punto 7](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- CU-PRG-004: renombrado de "Quitar una actividad del programa (liberar su asignación)" a "Eliminar una programación de una actividad" (precisión interna, 2026-06-29) — ahora elimina una programación puntual de la actividad, no necesariamente todas las que tenga; [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) y [§4.1, punto 8](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>) ("la actividad regresa a estado pendiente"). Relacionado con el hueco R5 del [Análisis de archivos proporcionados](<../../soporte/extraido/Analisis de archivos proporcionados.md>) (edición manual del calendario sin romper el vínculo con la propuesta).

- CU-PRG-008: [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) (reemplaza "registrante" por Participante) y [§4.1, punto 10](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>); antecedente en [Junta 2 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md>), sección "Flujo de aprobación y notificaciones" (segunda notificación con sala/horario asignado, con bitácora de envío para deslinde). Precisión interna (2026-06-29): ya no se dispara al "guardar el programa preliminar" (no existe ese paso); es una acción a discreción del Administrador, por actividad o de forma masiva, habilitada solo cuando hay un cambio de horario sin notificar.

- CU-PRG-009: [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) (confirmación por cada horario programado, no en bloque) y decisión [D3](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d3--modelo-de-notificaciones-reg--prg>) resuelta; antecedente en [Junta 2 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md>), sección "Flujo de aprobación y notificaciones" (el registrante debe confirmar su disponibilidad). Precisión interna (2026-06-29): el rechazo admite un motivo de texto libre, y la reprogramación que pueda seguir a un rechazo se negocia fuera del sistema.

- CU-PRG-010: unifica CU-PRG-010 y CU-PRG-012 según [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) y el glosario de *Visualización de programa* (§2.7 "Programación `[PRG]`" del mismo documento); el formato de salida (vista por salón/sala) sigue el modelo de [Programa General FILEY 2026](<../../soporte/extraido/Material para Registro de Actividades FILEY 2027/Programa General FILEY 2026.md>) (programa impreso maquetable).

- CU-PRG-011: [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) (ya no genera PDF; Excel/Word de uso interno) y [§4.1, punto 11](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>); formato modelo en el libro [Programación General FILEY 2027](<../../soporte/extraido/Indice.md>) (una hoja por salón, ver tabla "Programación General FILEY 2027" del índice de extraídos).
