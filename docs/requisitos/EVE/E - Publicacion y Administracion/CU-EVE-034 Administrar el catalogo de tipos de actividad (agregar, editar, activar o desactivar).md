---
estado: DE ISSAC RECHAZAD
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVE-034
dominio: EVE
reglas_de_negocio: []
---
# CU-EVE-034 Administrar el catálogo de tipos de actividad (agregar, editar, activar o desactivar)

## Objetivo

El administrador mantiene el catálogo de tipos de actividad —agregando, editando, activando o desactivando entradas— para que el formulario de propuestas y la clasificación interna reflejen los tipos vigentes de cada edición.

## Alcance

Módulo EVE — administración del catálogo `TipoActividad`. Cubre los tipos del formulario público y los de uso interno. La desactivación no elimina datos históricos: los tipos en uso se conservan para no romper las propuestas y actividades existentes.

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

El administrador necesita agregar un nuevo tipo de actividad o modificar/retirar uno existente.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.

## Postcondiciones

### En éxito

- El catálogo `TipoActividad` queda actualizado (alta, edición o cambio de estado `activo`).

### En fallo

- El catálogo permanece sin cambios.

## Flujo principal

1. El administrador abre la administración del catálogo de tipos de actividad.
2. El sistema lista los tipos existentes con: nombre, origen (`convocatoria_publica` / `interno`), duración por defecto en bloques, si requiere adjunto, si requiere ejemplar físico y estado `activo`.
3. El administrador elige una acción: agregar, editar o activar/desactivar un tipo.
4. El sistema solicita o muestra los datos del tipo según la acción.
5. El administrador captura los cambios y confirma.
6. El sistema valida los datos y guarda el cambio en el catálogo.
7. El sistema confirma la operación.

## Flujos alternos

### A1. Agregar un nuevo tipo de actividad

1. En el paso 3, el administrador elige "Agregar".
2. El administrador captura nombre, origen, duración por defecto, si requiere adjunto y si requiere ejemplar físico, dejándolo `activo`.
3. El flujo continúa en el paso 6.

### A2. Desactivar un tipo en uso

1. En el paso 3, el administrador desactiva un tipo que ya tiene propuestas o actividades asociadas.
2. El sistema cambia el tipo a `activo = false`, de modo que deja de ofrecerse en nuevos formularios pero conserva los registros históricos asociados.
3. El flujo continúa en el paso 7.

## Flujos de excepción

### E1. Nombre de tipo duplicado

1. En el paso 6, el sistema detecta que el nombre del tipo ya existe en el catálogo.
2. El sistema impide guardar y solicita un nombre distinto.

### E2. Intento de eliminar un tipo en uso

1. El administrador intenta eliminar (no desactivar) un tipo con propuestas o actividades asociadas.
2. El sistema impide la eliminación para preservar la integridad histórica y ofrece, en su lugar, desactivarlo (A2).

## Datos relevantes

### Entradas

- Datos del tipo de actividad: nombre, origen, duración por defecto en bloques, requiere adjunto, requiere ejemplar físico, estado `activo`.

### Salidas

- Catálogo `TipoActividad` actualizado.
