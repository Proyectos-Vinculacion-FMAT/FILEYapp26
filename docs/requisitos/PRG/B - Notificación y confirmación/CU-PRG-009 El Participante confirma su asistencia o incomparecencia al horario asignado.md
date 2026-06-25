---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/prg
fecha: 2026-06-24
id: CU-PRG-009
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
# CU-PRG-009 El Participante confirma su asistencia o incomparecencia al horario asignado

> [!question] Decisión pendiente — modelo de notificaciones (D3)
> Este caso de uso implica un método de visualización de las notificaciones de las
> actividades del Participante. Aún no está decidido si es una bandeja transversal a todos
> los dominios o una función por módulo (ver
> [Junta 3 con Equipo de desarrollo](<../../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d3--modelo-de-notificaciones-reg--prg>)).

## Objetivo

Permitir al Participante confirmar, para cada actividad y fecha asignada, que puede presentarse en la sala y horario que se le asignaron, o marcar su incomparecencia.

## Alcance

Aplica a actividades `EVT`/`TAL` ya programadas y notificadas (CU-PRG-008). La confirmación es **por actividad y por fecha**: si al Participante se le solicitó repetir la misma actividad varias veces, confirma cada ocasión por separado, nunca en bloque.

## Actores

### Actor principal

- Participante

## Disparador

El Participante recibe la notificación de su fecha, sala y horario asignados (CU-PRG-008) y accede a su método de visualización de notificaciones.

## Precondiciones

- Existe al menos una actividad programada y notificada al Participante, pendiente de confirmación.

## Postcondiciones

### En éxito

- Queda registrada la confirmación de asistencia o incomparecencia para esa fecha/actividad, y se notifica al Administrador.

### En fallo

- La actividad permanece sin confirmación.

## Flujo principal

1. El Participante consulta sus actividades programadas pendientes de confirmar.
2. El Participante elige una fecha/actividad y confirma su asistencia.
3. El sistema registra la confirmación y notifica al Administrador.

## Flujos alternos

### A1. Marcar incomparecencia

1. El Participante elige una fecha/actividad y marca que no podrá asistir.
2. El Participante indica el motivo: **por fecha** (el Administrador puede reprogramar esa ocasión) o **definitivo** (la actividad queda inhabilitada y ya no puede programarse).
3. El sistema registra la incomparecencia con su motivo y notifica al Administrador.

## Flujos de excepción

### E1. Ventana de confirmación vencida

1. El Participante intenta confirmar o declinar fuera del plazo habilitado.
2. El sistema rechaza el cambio e informa al Participante que contacte al Administrador.
