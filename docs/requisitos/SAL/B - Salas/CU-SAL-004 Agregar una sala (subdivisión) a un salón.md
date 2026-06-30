---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/sal
fecha: 2026-06-24
id: CU-SAL-004
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
# CU-SAL-004 Agregar una sala (subdivisión) a un salón

## Objetivo

Permitir al Administrador subdividir un salón agregándole una nueva sala, para reflejar las divisiones (p. ej. con mamparas) u otros espacios dentro del salón.

## Alcance

Aplica a salones ya existentes en el catálogo único global. Un salón puede tener tantas salas como el Administrador considere necesario.

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador elige agregar una sala a un salón desde la pantalla de salas y salones (CU-SAL-007).

## Precondiciones

- El salón existe en el catálogo único global.

## Postcondiciones

### En éxito

- La nueva sala queda creada dentro del salón, con su nombre y aforo definidos por el Administrador.

### En fallo

- No se crea la sala.

## Flujo principal

1. El Administrador elige un salón y solicita agregarle una sala.
2. El Administrador captura el nombre y el aforo de la nueva sala.
3. El sistema valida los datos.
4. El sistema crea la sala dentro del salón.
5. El sistema confirma la creación.

## Flujos de excepción

### E1. Nombre de sala duplicado dentro del salón

1. El nombre de la nueva sala coincide con el de otra sala del mismo salón.
2. El sistema rechaza la creación e informa el motivo al Administrador.
