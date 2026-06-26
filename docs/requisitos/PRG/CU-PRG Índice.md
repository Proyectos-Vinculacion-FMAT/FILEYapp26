---
estado: propuesta
version: 0.3
tags:
  - tipo/indice
  - dom/prg
fecha: 2026-06-24
---
# CU-PRG — Índice de casos de uso (Programación)

Inventario de casos de uso del dominio **Programación** (`PRG`): armado del programa a
partir de las actividades aceptadas (`EVT`/`TAL`), notificación/confirmación de la
asignación, y visibilidad/exportación. Homologado en la
[Junta 3 con Equipo de desarrollo](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md>);
la redacción detallada (flujo principal, alternos y excepciones) sigue sujeta a revisión.
Cada CU enlaza a su archivo y, debajo, a la evidencia (junta o material de FILEY) que lo
sustenta.

**Actores:** Administrador · Participante · Todos · Sistema.

> [!note]
> Son **dos programas independientes**: uno de eventos y uno de talleres. Cualquier
> Administrador puede entrar a cualquiera de los dos paneles; quién edita cuál se decide
> de manera interna, no por permisos del sistema. Solo el programa de **talleres** admite
> repetir una misma actividad para llenar huecos. La fecha, sala y horario los asigna el
> Administrador, no el Aplicante/Participante.

## A. Armado del programa

- [CU-PRG-001 Consultar lista de actividades de mi panel](<A - Armado del programa/CU-PRG-001 Consultar lista de actividades de mi panel.md>) — *Administrador*
  - Evidencia: renombre y alcance acordados en [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) ("se consultan las actividades... sin importar su estado de programación") y en [§4.1 Administrador, punto 3](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- [CU-PRG-002 Asignar una actividad a una sala y a uno o varios bloques de horario](<A - Armado del programa/CU-PRG-002 Asignar una actividad a una sala y a uno o varios bloques de horario.md>) — *Administrador*
  - Evidencia: absorbe CU-PRG-005 y CU-PRG-007 según [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) y [§4.1, puntos 4–6](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>); duración fija del bloque (1:15 hrs) con antecedente en [Junta 2 con organizadores FILEY — Horarios y bloques de actividades](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#horarios-y-bloques-de-actividades>).

- [CU-PRG-003 Editar la asignación (sala u horario) de una actividad ya programada](<A - Armado del programa/CU-PRG-003 Editar la asignación (sala u horario) de una actividad ya programada.md>) — *Administrador*
  - Evidencia: nota "editar = mover" en [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) y [§4.1, punto 7](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- [CU-PRG-004 Quitar una actividad del programa (liberar su asignación)](<A - Armado del programa/CU-PRG-004 Quitar una actividad del programa (liberar su asignación).md>) — *Administrador*
  - Evidencia: [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) y [§4.1, punto 8](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>) ("la actividad regresa a estado pendiente"). Relacionado con el hueco R5 del [Análisis de archivos proporcionados](<../../soporte/extraido/Analisis de archivos proporcionados.md>) (edición manual del calendario sin romper el vínculo con la propuesta).

## B. Notificación y confirmación de asignación

- [CU-PRG-008 Notificar al Participante su fecha, sala y horario asignados (segunda notificación)](<B - Notificación y confirmación/CU-PRG-008 Notificar al Participante su fecha, sala y horario asignados (segunda notificación).md>) — *Sistema*
  - Evidencia: [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) (reemplaza "registrante" por Participante; se dispara al guardar el programa preliminar) y [§4.1, punto 10](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>); antecedente en [Junta 2 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md>), sección "Flujo de aprobación y notificaciones" (segunda notificación con sala/horario asignado, con bitácora de envío para deslinde).

- [CU-PRG-009 El Participante confirma su asistencia o incomparecencia al horario asignado](<B - Notificación y confirmación/CU-PRG-009 El Participante confirma su asistencia o incomparecencia al horario asignado.md>) — *Participante*
  - Evidencia: [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) (confirmación por cada horario programado, no en bloque) y decisión pendiente [D3](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d3--modelo-de-notificaciones-reg--prg>); antecedente en [Junta 2 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md>), sección "Flujo de aprobación y notificaciones" (el registrante debe confirmar su disponibilidad).

## C. Visibilidad y exportación

- [CU-PRG-010 Consultar el programa publicado mediante su URL estática](<C - Visibilidad y exportación/CU-PRG-010 Consultar el programa publicado mediante su URL estática.md>) — *Todos*
  - Evidencia: unifica CU-PRG-010 y CU-PRG-012 según [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) y el glosario de *Visualización de programa* (§2.7 "Programación `[PRG]`" del mismo documento); el formato de salida (vista por salón/sala) sigue el modelo de [Programa General FILEY 2026](<../../soporte/extraido/Material para Registro de Actividades FILEY 2027/Programa General FILEY 2026.md>) (programa impreso maquetable).

- [CU-PRG-011 Exportar el programa a Excel o Word para uso interno](<C - Visibilidad y exportación/CU-PRG-011 Exportar el programa a Excel o Word para uso interno.md>) — *Administrador*
  - Evidencia: [Junta 3 §5.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#51-prg>) (ya no genera PDF; Excel/Word de uso interno) y [§4.1, punto 11](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>); formato modelo en el libro [Programación General FILEY 2027](<../../soporte/extraido/Indice.md>) (una hoja por salón, ver tabla "Programación General FILEY 2027" del índice de extraídos).

---

> [!warning] Hueco conocido (R5 del análisis de archivos)
> Estos casos de uso modelan asignar/editar/quitar actividades **aceptadas**, pero **no**
> contemplan que el Administrador agregue al calendario entradas que **no** provienen de una
> propuesta aceptada (artísticos capturados solo para control, o ajustes manuales de la
> "pulida final"). Pendiente de decidir si se añade un CU de entrada manual al programa. Ver
> R5 en el [Análisis de archivos proporcionados](<../../soporte/extraido/Analisis de archivos proporcionados.md>).

<!-- -->

> [!question] Decisión pendiente — dominio del CRUD de bloques de horario
> Aún no se decide si el CRUD de **bloques de horario** vive en `PRG` o en `SAL` (ver D2 en la
> [Junta 3 con Equipo de desarrollo](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d2--dominio-del-crud-de-bloques-de-horario-prg--sal>)).
> Mientras no se resuelva, no se modela un CU dedicado a esa CRUD; se asume embebido en
> CU-PRG-002 hasta que se decida su ubicación.

<!-- -->

> [!question] Decisión pendiente — modelo de notificaciones
> Afecta a CU-PRG-009: no está establecido si las notificaciones son **por módulo** o una
> **bandeja transversal** del lado Participante (ver D3 en la
> [Junta 3 con Equipo de desarrollo](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d3--modelo-de-notificaciones-reg--prg>)).

## Ajustes de la Junta 3 (homologación)

- **CU-PRG-005** (Programar una misma actividad en varias ocasiones) se **absorbe en CU-PRG-002**: asignar es el caso único, repetirlo es una capacidad de ese mismo caso de uso.
- **CU-PRG-006** (Validar que el aforo del grupo no supere el aforo de la sala) **sale de `PRG`**: es responsabilidad del core de Visitas escolares (`VIS`), donde se modela como validación de **cupo**.
- **CU-PRG-007** (Validar que la sala esté disponible) se **absorbe en CU-PRG-002** como regla de la asignación: la alerta de empalme no bloquea la asignación, pero sí el guardado del programa.
- **CU-PRG-012** (Consultar el programa publicado en la web app) se **unifica con CU-PRG-010**: ambos describen la misma Visualización de programa por URL estática.

La numeración de CUs es solo de conteo y no se reutiliza ni se recorre tras estas fusiones/bajas.
