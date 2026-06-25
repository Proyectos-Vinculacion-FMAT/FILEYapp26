---
estado: RECHAZADO DE ISSAC
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVT-026
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-026 Cerrar definitivamente el programa: bloquear cualquier modificación posterior

## Objetivo

El administrador marca el programa de la edición como definitivo, bloqueando las modificaciones ordinarias, para congelar una versión final entregable y evitar cambios accidentales una vez concluida la programación.

## Alcance

Módulo EVE — cierre definitivo del programa. Tras el cierre solo se permiten cambios excepcionales realizados por un administrador (CU-EVT-025). El cierre es reversible mediante reapertura controlada (flujo alterno A1). No cancela ni reprograma actividades.

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

El administrador considera que el programa está listo y decide cerrarlo definitivamente.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.
- La edición activa no está ya archivada (`programa_archivado = false`).

## Postcondiciones

### En éxito

- `ParametrosConvocatoria` queda con `programa_archivado = true`, `fecha_archivado`, `archivado_por` y `motivo_archivado` registrados.
- El sistema bloquea las modificaciones ordinarias del programa; solo quedan habilitados los cambios excepcionales (CU-EVT-025).
- Las actividades en `sin_horario` o `programada` se conservan tal como están, sin cancelarse ni alterarse.

### En fallo

- El programa permanece abierto y editable.

## Flujo principal

1. El administrador selecciona "Cerrar definitivamente el programa".
2. El sistema solicita el `motivo_archivado` (campo obligatorio) y muestra una doble verificación advirtiendo que se bloquearán las modificaciones ordinarias.
3. El administrador captura el motivo y confirma la doble verificación.
4. El sistema marca `programa_archivado = true` y registra `fecha_archivado`, `archivado_por` y `motivo_archivado`.
5. El sistema bloquea las modificaciones ordinarias del programa, dejando habilitados solo los cambios excepcionales (CU-EVT-025).
6. El sistema confirma al administrador que el programa quedó cerrado definitivamente.

## Flujos alternos

### A1. Reabrir el programa cerrado (corrección de error)

1. Un administrador con permiso selecciona "Reabrir programa" sobre una edición archivada.
2. El sistema solicita doble verificación de la reapertura.
3. El administrador confirma.
4. El sistema marca `programa_archivado = false`, registra la reapertura en `BitacoraEVE` (acción, autor y marca de tiempo) y rehabilita las modificaciones ordinarias.
5. El sistema confirma la reapertura.

## Flujos de excepción

### E1. Motivo de cierre faltante

1. En el paso 3, el administrador deja el `motivo_archivado` en blanco.
2. El sistema impide cerrar el programa y resalta el motivo como obligatorio.
3. El administrador escribe el motivo y reintenta.

### E2. Programa ya cerrado

1. En el paso 1, el sistema detecta que la edición ya está archivada (`programa_archivado = true`).
2. El sistema informa que el programa ya está cerrado y ofrece, en su lugar, la opción de reapertura (A1).

## Datos relevantes

### Entradas

- `motivo_archivado` (obligatorio).
- Confirmación de doble verificación.

### Salidas

- `ParametrosConvocatoria` con el programa archivado (`programa_archivado`, `fecha_archivado`, `archivado_por`, `motivo_archivado`).
- Registro en `BitacoraEVE` en caso de reapertura.
