---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVE-032
dominio: EVE
reglas_de_negocio: []
---
# CU-EVE-032 Mostrar la cartelera pública filtrable por categoría o sección para visitantes

## Objetivo

El visitante consulta la cartelera pública de actividades de la feria, pudiendo filtrarla por categoría o sección, para planear a cuáles asistir.

## Alcance

Módulo EVE — cartelera pública. Muestra únicamente actividades de la versión publicada del programa (CU-EVE-029). Es de acceso público y de solo lectura. El detalle de cada actividad se cubre en CU-EVE-033.

## Actores

### Actor principal

- Visitante (público general)

### Actores secundarios

- Sistema (compone y presenta la cartelera).

## Disparador

El visitante abre la cartelera pública de la feria.

## Precondiciones

- Existe una versión del programa publicada para la edición vigente.

## Postcondiciones

### En éxito

- Se muestra la cartelera con las actividades publicadas según los filtros aplicados.

### En fallo

- No se muestra la cartelera; se informa que el programa aún no está disponible.

## Flujo principal

1. El visitante abre la cartelera pública.
2. El sistema muestra las actividades de la versión publicada con: título, tipo, fecha, sala y horario.
3. El visitante aplica filtros por categoría o sección (y, opcionalmente, por día), o busca por texto.
4. El sistema actualiza la cartelera conforme a los filtros.
5. El visitante selecciona una actividad para ver su detalle (CU-EVE-033).

## Flujos alternos

### A1. Cartelera sin filtros

1. En el paso 3, el visitante no aplica filtros.
2. El sistema muestra todas las actividades publicadas y el flujo continúa en el paso 5.

### A2. Actividades informativas sin horario

1. En el paso 2, existen actividades publicadas como informativas (`en_cartelera_informal`).
2. El sistema las muestra en una sección informativa, indicando que su horario está por confirmar.

## Flujos de excepción

### E1. Programa aún no publicado

1. En el paso 1, no existe ninguna versión publicada para la edición vigente.
2. El sistema informa que el programa aún no está disponible y no muestra cartelera.

### E2. Sin resultados para el filtro

1. En el paso 4, ninguna actividad cumple los filtros aplicados.
2. El sistema muestra la cartelera vacía con un aviso y mantiene los filtros para ajustarlos.

## Datos relevantes

### Entradas

- Criterios de filtrado: categoría, sección, día y/o texto de búsqueda.

### Salidas

- Cartelera pública con título, tipo, fecha, sala y horario de cada actividad publicada.
