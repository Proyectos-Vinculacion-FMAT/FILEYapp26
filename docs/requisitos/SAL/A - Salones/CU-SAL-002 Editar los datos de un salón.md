---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/sal
fecha: 2026-06-24
id: CU-SAL-002
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
# CU-SAL-002 Editar los datos de un salón

## Objetivo

Permitir al Administrador actualizar los datos de un salón existente en el catálogo único global.

## Alcance

Aplica a los datos propios del salón (p. ej. nombre). No incluye editar sus salas (ver CU-SAL-005).

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador elige editar un salón desde la pantalla de salas y salones (CU-SAL-007).

## Precondiciones

- El salón existe en el catálogo único global.

## Postcondiciones

### En éxito

- Los datos del salón quedan actualizados en el catálogo único global.

### En fallo

- El salón conserva sus datos previos.

## Flujo principal

1. El Administrador elige un salón del catálogo y abre su edición.
2. El Administrador modifica los datos del salón.
3. El sistema valida los datos modificados.
4. El sistema guarda los cambios y los refleja en el catálogo único global.

## Flujos de excepción

### E1. Nombre de salón duplicado

1. El nuevo nombre coincide con el de otro salón existente.
2. El sistema rechaza el cambio e informa el motivo al Administrador.
