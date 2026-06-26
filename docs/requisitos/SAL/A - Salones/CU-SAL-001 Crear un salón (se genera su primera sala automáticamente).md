---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/sal
fecha: 2026-06-24
id: CU-SAL-001
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
# CU-SAL-001 Crear un salón (se genera su primera sala automáticamente)

## Objetivo

Permitir al Administrador dar de alta un salón en el catálogo compartido de espacios; al crearlo, el sistema genera automáticamente su primera sala.

## Alcance

Aplica al catálogo compartido de salas y salones, gestionado desde la pantalla única de CU-SAL-007. No aplica a stands.

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador solicita crear un salón desde la pantalla de salas y salones.

## Precondiciones

- El Administrador tiene acceso a la pantalla de salas y salones (CU-SAL-007).

## Postcondiciones

### En éxito

- El salón queda creado en el catálogo compartido, con una sala generada automáticamente como primera sala.

### En fallo

- No se crea el salón; se informa el motivo al Administrador.

## Flujo principal

1. El Administrador abre la opción de crear salón desde la pantalla de salas y salones (CU-SAL-007).
2. El Administrador captura los datos del salón (nombre).
3. El sistema valida que los datos requeridos estén completos.
4. El sistema crea el salón y genera automáticamente su primera sala.
5. El sistema confirma la creación y la muestra en el catálogo compartido.

## Flujos de excepción

### E1. Nombre de salón duplicado

1. El nombre del salón ya existe en el catálogo.
2. El sistema rechaza la creación e informa el motivo al Administrador.
