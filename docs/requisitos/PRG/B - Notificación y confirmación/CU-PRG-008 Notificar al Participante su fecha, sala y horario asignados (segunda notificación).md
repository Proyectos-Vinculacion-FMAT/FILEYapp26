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

> [!note] Notificar es una acción a discreción del Administrador, no un guardado
> No existe un botón de "guardar el programa" que dispare la notificación (ver CU-PRG-002).
> Programar, mover o eliminar una programación (CU-PRG-002 a CU-PRG-004) queda guardado de
> inmediato; notificar es una acción aparte que el Administrador decide ejecutar cuando lo
> considere oportuno, actividad por actividad o de forma masiva (ver A1).

## Objetivo

Comunicar al Participante la fecha, sala y horario que se le asignaron, como segunda notificación posterior a la de aceptación, y dejar constancia de su envío.

## Alcance

Aplica a actividades `EVT`/`TAL` ya Aceptadas (el actor ya es Participante, no Aplicante) con al menos una programación pendiente de notificar. La notificación es **por actividad, no por programación individual**: si la actividad tiene varias programaciones (CU-PRG-002 A1), todas sus fechas/horarios vigentes se incluyen en una sola notificación de esa actividad. Se envía por correo y queda también disponible dentro del sistema.

## Actores

### Actor principal

- Sistema

### Actores secundarios

- Administrador: decide cuándo disparar la notificación.

## Disparador

El Administrador elige notificar una actividad (o varias, ver A1) desde su panel.

## Precondiciones

- La actividad tiene al menos una programación y su botón de notificar está habilitado: existe una asignación nueva o editada que aún no se notificó.
- El programa de esa actividad no tiene solapamientos sin resolver (CU-PRG-002 E1).

## Postcondiciones

### En éxito

- El Participante recibe la notificación por correo y dentro del sistema, y queda registro de su envío. El botón de notificar de esa actividad se deshabilita hasta que vuelva a haber un cambio de horario sin notificar.

### En fallo

- El envío falla y queda registrado para reintento; las programaciones de la actividad no se revierten.

## Flujo principal

1. El Administrador elige notificar una actividad con programación pendiente de notificar.
2. El sistema dispara una notificación al Participante con todas las fechas, salas y horarios vigentes de esa actividad.
3. El sistema envía la notificación por correo y la deja disponible dentro del sistema.
4. El sistema registra el envío de la notificación (para deslinde) y deshabilita el botón de notificar de esa actividad hasta el próximo cambio de horario.

## Flujos alternos

### A1. Notificación masiva

1. El Administrador, desde el listado de su panel, elige notificar en una sola acción a todos los participantes cuyas actividades tengan programación pendiente de notificar (asignada por primera vez o editada).
2. El sistema repite los pasos 2–4 del flujo principal para cada una de esas actividades.

## Flujos de excepción

### E1. Reprogramación posterior

1. El Administrador mueve o elimina una programación de una actividad ya notificada (CU-PRG-003/CU-PRG-004).
2. El sistema no reenvía automáticamente la notificación: vuelve a habilitar el botón de notificar de esa actividad y queda a discreción del Administrador decidir cuándo notificar el cambio.
