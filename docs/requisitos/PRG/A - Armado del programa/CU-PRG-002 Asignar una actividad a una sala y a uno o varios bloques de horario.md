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
# CU-PRG-002 Asignar una actividad a una sala y a uno o varios bloques de horario

## Objetivo

Permitir al Administrador colocar una actividad Aceptada en una sala y en uno o varios bloques de horario disponibles, construyendo el programa de su panel. Lo que se programa hacia la sala es la **actividad**, no al revés; la fecha, sala y horario los asigna el Administrador, no el Aplicante/Participante.

> [!note] Absorbe CU-PRG-005 y CU-PRG-007 (Junta 3)
> Asignar es el caso de uso único: poder repetir la asignación de una misma actividad y
> validar la disponibilidad de la sala son capacidades de este mismo caso de uso, no CUs
> aparte.

## Alcance

Aplica a actividades `EVT`/`TAL` ya Aceptadas, listadas desde CU-PRG-001. Las actividades se programan **una a una**, no en lote. No valida aforo de grupos visitantes (responsabilidad de `VIS`).

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador selecciona, desde la lista de CU-PRG-001, una actividad pendiente de programar.

## Precondiciones

- La actividad está Aceptada y pertenece al panel del Administrador.
- Existen bloques de horario configurados en al menos una sala.

## Postcondiciones

### En éxito

- La actividad queda asignada a una sala y a uno o varios bloques de horario completos y consecutivos. Si necesita más tiempo del que cubre un bloque, ocupa también el siguiente bloque disponible en su totalidad.

### En fallo

- La actividad permanece sin asignar (o con su asignación previa) y no se guarda ningún cambio.

## Flujo principal

1. El Administrador elige una actividad pendiente de la lista de su panel (CU-PRG-001).
2. El Administrador elige una sala y uno o varios bloques de horario disponibles para esa sala.
3. El sistema valida que ninguno de los bloques elegidos esté ya ocupado por otra actividad en esa sala [RN-XXX-001].
4. El sistema asigna la actividad a la sala y a los bloques elegidos.
5. El sistema confirma la asignación al Administrador.

## Flujos alternos

### A1. Repetir la asignación (solo programa de talleres)

1. El Administrador, sobre una actividad ya asignada, elige programarla nuevamente en otro día, sala o bloque para llenar huecos del programa de talleres.
2. El sistema repite los pasos 2–5 del flujo principal para la nueva ocasión.
3. El sistema permite consultar, para esa actividad, cuántas veces, cuándo y dónde fue programada.

## Flujos de excepción

### E1. Choque de horario en la sala

1. Dos o más actividades intentan ocupar el mismo bloque de una misma sala, aunque sus horas de inicio o cierre no se solapen exactamente.
2. El sistema marca una alerta de empalme sobre las actividades afectadas, pero **no bloquea** la asignación.
3. El empalme debe resolverse —reprogramando alguna de las actividades afectadas— antes de poder guardar el programa preliminar y disparar la notificación a los participantes (ver CU-PRG-008).

[RN-XXX-001]: #
