---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/sal
fecha: 2026-06-24
id: CU-SAL-006
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
# CU-SAL-006 Eliminar una sala

## Objetivo

Permitir al Administrador eliminar una sala de un salón en el catálogo único global.

## Alcance

Aplica solo a salas sin actividades programadas. No aplica a la última sala de un salón (un salón debe conservar al menos una).

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador elige eliminar una sala desde la pantalla de salas y salones (CU-SAL-007).

## Precondiciones

- La sala existe dentro de un salón del catálogo único global.

## Postcondiciones

### En éxito

- La sala deja de estar disponible en el catálogo único global.

### En fallo

- La sala permanece en el catálogo, sin cambios.

## Flujo principal

1. El Administrador elige una sala y solicita eliminarla.
2. El sistema valida que la sala no tenga actividades programadas [RN-XXX-001].
3. El sistema elimina la sala.
4. El sistema confirma la eliminación.

## Flujos de excepción

### E1. Sala con actividades programadas

1. La sala tiene actividades programadas (ver CU-PRG-002).
2. El sistema rechaza la eliminación e informa al Administrador que debe reprogramar o eliminar la programación de esas actividades primero (ver CU-PRG-004).

### E2. Última sala del salón

1. La sala que se intenta eliminar es la única sala del salón.
2. El sistema rechaza la eliminación, ya que un salón debe conservar al menos una sala (ver CU-SAL-001).

[RN-XXX-001]: #
