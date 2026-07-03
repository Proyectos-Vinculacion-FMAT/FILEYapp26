---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/sal
fecha: 2026-06-24
id: CU-SAL-007
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
# CU-SAL-007 Consultar el catálogo único global de salas y salones

> [!note] Una sola pantalla, une CU-SAL-008 (Junta 3)
> Solo los Administradores ven la lista de salones y salas. El CRUD completo —crear salón,
> agregar sala, editar propiedades, eliminar— y la consulta del detalle de una sala (aforo y
> disponibilidad) viven en **esta misma pantalla**; el sistema no redirige a pantallas
> distintas. Esta CU absorbe a la antigua CU-SAL-008.

<!-- -->

> [!note] Precisión interna (2026-06-29) — catálogo único global, no "compartido"
> No son dos catálogos que se comparten entre sí: es **un solo catálogo global**. Lo consumen
> por igual los paneles de programación de `EVT` y de `TAL` (vía `PRG`) al momento de asignar
> sala a una actividad, sin importar si esa sala se usó antes para un taller o para un evento.

## Objetivo

Permitir a cualquier Administrador consultar el catálogo único y global de salas y salones —y, desde la misma pantalla, dar de alta salones y salas y editar sus propiedades— para coordinar el uso de los espacios.

## Alcance

Aplica al catálogo único global, visible para todos los Administradores y consumido por igual desde los paneles de `EVT` y `TAL` al programar, sin distinción de panel. No aplica a stands.

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador abre la pantalla de salas y salones.

## Precondiciones

- Ninguna; la pantalla siempre muestra el estado actual del catálogo, aunque esté vacío.

## Postcondiciones

### En éxito

- Se muestra la lista de salones con sus salas, incluyendo para cada sala su aforo y disponibilidad, junto con las acciones de alta/edición/eliminación (CU-SAL-001 a CU-SAL-006).

### En fallo

- No aplica: la consulta no tiene un flujo de fallo propio más allá de un catálogo vacío.

## Flujo principal

1. El Administrador abre la pantalla de salas y salones.
2. El sistema muestra todos los salones del catálogo único global, cada uno con sus salas.
3. El Administrador selecciona una sala para ver su detalle (aforo y disponibilidad).
4. Desde la misma pantalla, el Administrador puede crear, editar o eliminar salones y salas (CU-SAL-001 a CU-SAL-006) sin salir de ella.

## Flujos de excepción

### E1. Catálogo vacío

1. Aún no existe ningún salón en el catálogo.
2. El sistema muestra la pantalla vacía con la opción de crear el primer salón (CU-SAL-001).
