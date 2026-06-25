---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/prg
fecha: 2026-06-24
id: CU-PRG-008
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
# CU-PRG-008 Notificar al Participante su fecha, sala y horario asignados (segunda notificación)

## Objetivo

Comunicar al Participante la fecha, sala y horario que se le asignaron, como segunda notificación posterior a la de aceptación, y dejar constancia de su envío.

## Alcance

Aplica a actividades `EVT`/`TAL` ya Aceptadas (el actor ya es Participante, no Aplicante). La notificación se envía por correo y queda también disponible dentro del sistema.

## Actores

### Actor principal

- Sistema

## Disparador

El Administrador guarda el programa preliminar (ver CU-PRG-002).

## Precondiciones

- El programa preliminar fue guardado y no tiene solapamientos sin resolver (CU-PRG-002 E1).

## Postcondiciones

### En éxito

- El Participante recibe la notificación por correo y dentro del sistema, y queda registro de su envío.

### En fallo

- El envío falla y queda registrado para reintento; el guardado del programa no se revierte.

## Flujo principal

1. El Administrador guarda el programa preliminar.
2. El sistema dispara, para cada actividad incluida, una notificación al Participante con su fecha, sala y horario asignados.
3. El sistema envía la notificación por correo y la deja disponible dentro del sistema.
4. El sistema registra el envío de la notificación (para deslinde).

## Flujos de excepción

### E1. Reprogramación posterior

1. El Administrador mueve o quita una actividad ya notificada (CU-PRG-003/CU-PRG-004).
2. El sistema no reenvía automáticamente la notificación; queda a criterio del Administrador volver a guardar el programa para disparar una nueva notificación.
