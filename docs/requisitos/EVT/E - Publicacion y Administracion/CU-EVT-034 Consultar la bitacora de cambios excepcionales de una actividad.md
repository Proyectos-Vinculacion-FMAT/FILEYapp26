---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVT-034
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-034 Consultar la bitácora de cambios excepcionales de una actividad

## Objetivo

El administrador consulta el historial de cambios excepcionales registrados sobre una actividad —quién los hizo, qué cambió, el motivo y cuándo— para auditar las decisiones tomadas fuera del flujo normal.

## Alcance

Módulo EVE — consulta de la `BitacoraEVE`. Es una vista de solo lectura. Registra los eventos generados por CU-EVT-025 (cambio de horario excepcional), CU-EVT-026 (reapertura del programa) y demás acciones excepcionales del módulo.

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

El administrador necesita revisar el historial de cambios excepcionales de una actividad.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.

## Postcondiciones

### En éxito

- Se muestran los registros de bitácora asociados a la actividad consultada.

### En fallo

- No se muestra la bitácora; se informa el error de consulta.

## Flujo principal

1. El administrador abre la bitácora de una actividad (desde su detalle o desde la sección de auditoría).
2. El sistema lista los registros de `BitacoraEVE` asociados, mostrando por cada uno: acción, detalle del cambio (de → a), motivo, persona que lo ejecutó y marca de tiempo.
3. El administrador puede ordenar o filtrar los registros por fecha o tipo de acción.
4. El sistema actualiza la lista conforme al criterio aplicado.

## Flujos alternos

### A1. Vista global de la bitácora

1. En el paso 1, el administrador abre la bitácora general en lugar de la de una actividad específica.
2. El sistema lista los registros de toda la edición y permite filtrar por entidad, acción o persona.

## Flujos de excepción

### E1. Sin registros de bitácora

1. En el paso 2, la actividad no tiene cambios excepcionales registrados.
2. El sistema informa que no hay registros de bitácora para la actividad.

## Datos relevantes

### Entradas

- Identificador de la actividad (o criterio de la vista global).
- Criterios de filtrado: fecha, tipo de acción, entidad o persona.

### Salidas

- Lista de registros de `BitacoraEVE`: acción, detalle, motivo, persona y marca de tiempo.
