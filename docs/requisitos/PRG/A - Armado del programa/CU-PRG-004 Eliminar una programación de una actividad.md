---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/prg
fecha: 2026-06-24
id: CU-PRG-004
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
# CU-PRG-004 Eliminar una programación de una actividad

## Objetivo

Permitir al Administrador eliminar una programación de una actividad, liberando la sala y el/los bloque(s) de horario que ocupaba para reasignarlos a otra actividad.

## Alcance

Aplica a actividades `EVT`/`TAL` con al menos una programación. Eliminar no rechaza ni desacepta la actividad: solo libera la sala/horario de esa programación. Si la actividad tenía varias programaciones (CU-PRG-002 A1), las demás no se ven afectadas.

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador elige eliminar una programación existente de una actividad.

## Precondiciones

- La actividad tiene al menos una programación (sala y bloque(s) asignados).

## Postcondiciones

### En éxito

- Se elimina esa programación (se le quitan sala, bloque(s) y horas de inicio/fin) y sus bloques quedan libres para otra programación. Si era la única programación de la actividad, esta regresa a estado **pendiente** (vuelve a aparecer en CU-PRG-001 sin sala ni horario); si tenía otras, esas conservan su sala y bloque(s) sin cambios.

### En fallo

- La programación conserva su sala y bloque(s) originales.

## Flujo principal

1. El Administrador elige una programación existente de una actividad y selecciona "eliminar programación".
2. El sistema libera la sala y el/los bloque(s) que ocupaba esa programación.
3. El sistema elimina los campos de hora de inicio y fin de esa programación; si era la única que tenía la actividad, la marca como pendiente.
4. El sistema confirma al Administrador que la sala y el/los bloque(s) quedaron disponibles para otra programación.

## Flujos de excepción

### E1. Programación ya notificada al participante

1. La programación que se quiere eliminar ya fue incluida en una notificación (CU-PRG-008) enviada al Participante.
2. El sistema permite eliminarla igualmente, pero advierte al Administrador que la actividad quedará con un cambio pendiente de notificar: deberá reprogramarla y, a su discreción, volver a notificar al Participante (el botón de notificar se habilita de nuevo en cuanto haya un cambio real en el horario de esa actividad).
