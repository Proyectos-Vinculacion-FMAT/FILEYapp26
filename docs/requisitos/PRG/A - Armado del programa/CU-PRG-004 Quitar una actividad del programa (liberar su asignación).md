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
# CU-PRG-004 Quitar una actividad del programa (liberar su asignación)

## Objetivo

Permitir al Administrador retirar una actividad del programa, liberando la sala y el/los bloque(s) de horario que ocupaba para reasignarlos a otra actividad.

## Alcance

Aplica a actividades `EVT`/`TAL` ya programadas. Quitar no rechaza ni desacepta la actividad: solo libera su asignación de sala/horario.

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador elige quitar una actividad ya programada.

## Precondiciones

- La actividad está programada (tiene sala y bloque(s) asignados).

## Postcondiciones

### En éxito

- La actividad regresa a estado **pendiente** (vuelve a aparecer en CU-PRG-001 sin sala ni horario) y se le eliminan los campos de hora de inicio y fin. Los bloques que ocupaba quedan libres para otra asignación.

### En fallo

- La actividad conserva su asignación original.

## Flujo principal

1. El Administrador elige una actividad programada y selecciona "quitar del programa".
2. El sistema libera la sala y el/los bloque(s) que ocupaba la actividad.
3. El sistema elimina los campos de hora de inicio y fin de la actividad y la marca como pendiente.
4. El sistema confirma al Administrador que la actividad quedó disponible para reprogramarse.

## Flujos de excepción

### E1. Actividad ya notificada al participante

1. La actividad que se quiere quitar ya fue incluida en una notificación de programa preliminar (CU-PRG-008) enviada al Participante.
2. El sistema permite quitarla igualmente, pero advierte al Administrador que deberá reprogramarla y, si aplica, volver a notificar al Participante.
