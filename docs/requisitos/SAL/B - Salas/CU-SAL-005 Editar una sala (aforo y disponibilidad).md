---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/sal
fecha: 2026-06-24
id: CU-SAL-005
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
# CU-SAL-005 Editar una sala (aforo y disponibilidad)

> [!question] Decisión pendiente — CRUD de bloques de horario
> Este CU edita el aforo y la disponibilidad (días y horas) de la sala, pero no su CRUD de
> **bloques de horario**: aún no se decide si esa CRUD vive en `SAL` o en `PRG` (ver D2 en la
> [Junta 3 con Equipo de desarrollo](<../../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d2--dominio-del-crud-de-bloques-de-horario-prg--sal>)).

## Objetivo

Permitir al Administrador actualizar el nombre, el aforo y la disponibilidad (qué días y a qué horas se puede utilizar) de una sala.

## Alcance

Aplica a salas existentes dentro de un salón. No incluye el CRUD de bloques de horario (ver decisión pendiente).

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador elige editar una sala desde la pantalla de salas y salones (CU-SAL-007).

## Precondiciones

- La sala existe dentro de un salón del catálogo compartido.

## Postcondiciones

### En éxito

- El aforo y/o la disponibilidad de la sala quedan actualizados.

### En fallo

- La sala conserva sus datos previos.

## Flujo principal

1. El Administrador elige una sala y abre su edición.
2. El Administrador modifica el aforo y/o la disponibilidad de la sala.
3. El sistema valida los datos modificados.
4. El sistema guarda los cambios.

## Flujos de excepción

### E1. Reducción que deja sin cabida a actividades ya programadas

1. El nuevo aforo o disponibilidad ya no cubre actividades que tiene programadas esa sala.
2. El sistema advierte al Administrador antes de guardar el cambio.
