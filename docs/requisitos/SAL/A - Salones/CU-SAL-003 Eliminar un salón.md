---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/sal
fecha: 2026-06-24
id: CU-SAL-003
dominio: SAL
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
# CU-SAL-003 Eliminar un salón

## Objetivo

Permitir al Administrador eliminar un salón del catálogo compartido de espacios.

## Alcance

Aplica solo a salones cuyas salas no tengan actividades programadas. Eliminar un salón elimina también todas sus salas.

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador elige eliminar un salón desde la pantalla de salas y salones (CU-SAL-007).

## Precondiciones

- El salón existe en el catálogo compartido.

## Postcondiciones

### En éxito

- El salón y todas sus salas dejan de estar disponibles en el catálogo compartido.

### En fallo

- El salón permanece en el catálogo, sin cambios.

## Flujo principal

1. El Administrador elige un salón del catálogo y solicita eliminarlo.
2. El sistema valida que ninguna de sus salas tenga actividades programadas [RN-XXX-001].
3. El sistema elimina el salón junto con todas sus salas.
4. El sistema confirma la eliminación.

## Flujos de excepción

### E1. Salón con actividades programadas

1. Alguna sala del salón tiene actividades programadas (ver CU-PRG-002).
2. El sistema rechaza la eliminación e informa al Administrador que debe reprogramar o quitar esas actividades primero (ver CU-PRG-004).

[RN-XXX-001]: #
