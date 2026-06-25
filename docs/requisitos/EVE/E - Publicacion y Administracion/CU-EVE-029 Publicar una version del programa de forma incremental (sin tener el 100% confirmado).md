---
estado: RECHAZADO DE ISSAC
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVE-029
dominio: EVE
reglas_de_negocio: []
---
# CU-EVE-029 Publicar una versión del programa de forma incremental (sin tener el 100% confirmado)

## Objetivo

El administrador publica una versión del programa para que los visitantes la consulten, sin necesidad de tener todas las actividades confirmadas, permitiendo difundir el avance de forma incremental.

## Alcance

Módulo EVE — publicación del programa. Hace visibles en la cartelera pública (CU-EVE-032) las actividades incluidas en la versión publicada. No cierra el programa (eso es CU-EVE-027) ni asigna horarios (módulo C).

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

El administrador considera que hay suficiente avance del programa y decide publicarlo o actualizar la publicación.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.
- Existe una versión del programa maestro con al menos una actividad programada.

## Postcondiciones

### En éxito

- La versión seleccionada del `ProgramaMaestro` queda marcada como `publicado`.
- Las actividades programadas de esa versión quedan visibles en la cartelera pública; las que aún no tienen horario no se publican o se muestran como informativas sin horario fijo.

### En fallo

- No cambia la visibilidad pública; la publicación anterior (si existía) se mantiene.

## Flujo principal

1. El administrador selecciona la versión del programa a publicar.
2. El sistema muestra un resumen de lo que se publicará: actividades programadas, actividades aún sin horario y total.
3. El administrador confirma la publicación.
4. El sistema marca la versión como `publicado` y expone sus actividades programadas en la cartelera pública.
5. El sistema confirma al administrador que la versión quedó publicada.

## Flujos alternos

### A1. Publicación incremental sobre una versión ya publicada

1. En el paso 1, ya existe una versión publicada previamente.
2. El administrador publica una versión más reciente con más actividades programadas.
3. El sistema reemplaza la versión visible públicamente por la nueva y el flujo continúa en el paso 4.

### A2. Incluir actividades sin horario como informativas

1. En el paso 2, el administrador opta por mostrar ciertas actividades sin horario fijo en una cartelera informativa (`en_cartelera_informal`).
2. El sistema las publica marcadas como informativas, sin comprometer sala ni horario.

## Flujos de excepción

### E1. Versión sin actividades programadas

1. En el paso 2, la versión seleccionada no tiene actividades con horario asignado.
2. El sistema advierte que no hay contenido programado que publicar y solicita confirmación antes de publicar una cartelera vacía o solo informativa.

## Datos relevantes

### Entradas

- Versión del programa maestro a publicar.
- Opción de incluir actividades informativas sin horario.

### Salidas

- Versión del `ProgramaMaestro` marcada como `publicado`.
- Cartelera pública actualizada con las actividades de la versión.
