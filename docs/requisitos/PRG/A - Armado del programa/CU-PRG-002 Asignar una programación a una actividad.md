---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/prg
fecha: 2026-06-24
id: CU-PRG-002
dominio: PRG
responsable: Nombre
issue_relacionado: PSD-XX
pr_relacionado: "#XX"
reglas_de_negocio:
  - RN-XXX-001
diagramas_relacionados:
  - BPMN-XXX-001
trazabilidad:
  ddr:
    - DDR-XX
---
# CU-PRG-002 Asignar una programación a una actividad

## Objetivo

Permitir al Administrador colocar una actividad Aceptada en una sala y en uno o varios bloques de horario disponibles, creándole una **programación**. Lo que se programa hacia la sala es la **actividad**, no al revés; la fecha, sala y horario los asigna el Administrador, no el Aplicante/Participante. Una misma actividad puede tener más de una programación (ver A1).

> [!note] Absorbe CU-PRG-005 y CU-PRG-007 (Junta 3)
> Asignar es el caso de uso único: poder repetir la asignación de una misma actividad y
> validar la disponibilidad de la sala son capacidades de este mismo caso de uso, no CUs
> aparte.

<!-- -->

> [!success] Bloques hardcodeados por panel (D2 resuelta, Junta 3 con organizadores FILEY)
> Los bloques de horario **no se configuran ni se crean**: una sala no tiene ningún horario
> relacionado al darse de alta (ver `SAL/CU-SAL Índice.md`). Es este panel de programación el
> que divide el horario en bloques fijos según el panel en el que se programa:
>
> - **Panel de Eventos:** bloques de **1:15**.
> - **Panel de Talleres:** bloques de **1:00** (50 min de actividad + 10 min de descanso entre sesión).
>
> Ver [RSM - Junta 3 con organizadores FILEY](<../../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>).

<!-- -->

> [!note] El disparador real es el botón "Programar" del listado de EVT/TAL
> Este CU no abre una pantalla aparte de "Programación": vive en el mismo listado de
> propuestas/actividades de cada panel (`EVT` o `TAL`). Mientras la propuesta está pendiente de
> revisión, ese renglón muestra el botón **"Revisar"**; en cuanto el Administrador la Acepta, el
> mismo renglón cambia ese botón por **"Programar"**. No existe forma de programar una actividad
> que no haya sido aceptada: la secuencia es siempre revisión → aceptación → programación. La
> lista de CU-PRG-001 es, en la práctica, ese mismo listado del panel, ya filtrado a actividades
> Aceptadas; ahí también vive el botón de visualización del estado actual de la programación.

<!-- -->

> [!note] Guardado implícito — no hay botón de "guardar el programa"
> La programación queda guardada en cuanto el Administrador la confirma; no existe un paso
> aparte de "guardar el programa preliminar". El programa conserva siempre el estado en el que
> se deja. Por eso notificar al Participante (ver CU-PRG-008) no ocurre automáticamente al
> programar: queda a discreción del Administrador decidir cuándo notificar, actividad por
> actividad o de forma masiva.

## Alcance

Aplica a actividades `EVT`/`TAL` ya Aceptadas, listadas desde CU-PRG-001. Las actividades se programan **una a una**, no en lote. No valida aforo de grupos visitantes (responsabilidad de `VIS`).

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador, sobre una actividad ya Aceptada del listado de su panel (CU-PRG-001), pulsa "Programar".

## Precondiciones

- La actividad está Aceptada y pertenece al panel del Administrador.
- Existe al menos una sala en el catálogo único global de `SAL`.

## Postcondiciones

### En éxito

- La actividad tiene una programación nueva: una sala y uno o varios bloques de horario completos y consecutivos. Si necesita más tiempo del que cubre un bloque, ocupa también el siguiente bloque disponible en su totalidad. El cambio queda guardado de inmediato y disponible para notificar (CU-PRG-008) a discreción del Administrador.

### En fallo

- La actividad permanece sin esa programación (o conserva las que ya tenía) y no se guarda ningún cambio.

## Flujo principal

1. El Administrador pulsa "Programar" sobre una actividad Aceptada del listado de su panel (CU-PRG-001).
2. El Administrador elige una sala y uno o varios bloques de horario disponibles para esa sala.
3. El sistema valida que ninguno de los bloques elegidos esté ya ocupado por otra actividad en esa sala [RN-XXX-001].
4. El sistema guarda la programación de inmediato, sin un paso aparte de "guardar".
5. El sistema confirma la programación al Administrador y habilita, para esa actividad, el botón de notificar (CU-PRG-008).

## Flujos alternos

### A1. Repetir la actividad en otra programación (solo programa de talleres)

1. El Administrador, sobre una actividad que ya tiene una o más programaciones, elige programarla nuevamente en otro día, sala o bloque para llenar huecos del programa de talleres.
2. El sistema repite los pasos 2–5 del flujo principal para la nueva programación, sin afectar las programaciones que ya tenía esa actividad.

### A2. Consulta de programación — todas las ocasiones de una actividad en una sola pantalla

1. El Administrador, sobre cualquier actividad con una o más programaciones, abre su consulta de programación.
2. El sistema muestra, en una sola instancia, todas las programaciones de esa actividad —fecha, sala, bloque(s) y su estado de notificación/confirmación— sin que el Administrador tenga que ubicarlas una por una en el calendario general.

## Flujos de excepción

### E1. Choque de horario en la sala

1. Dos o más actividades intentan ocupar el mismo bloque de una misma sala, aunque sus horas de inicio o cierre no se solapen exactamente.
2. El sistema marca una alerta de empalme sobre las actividades afectadas, pero **no bloquea** la programación ni su guardado.
3. El empalme debe resolverse —reprogramando alguna de las actividades afectadas— antes de que el Administrador pueda notificar a los participantes de esas actividades (ver CU-PRG-008).

[RN-XXX-001]: #
