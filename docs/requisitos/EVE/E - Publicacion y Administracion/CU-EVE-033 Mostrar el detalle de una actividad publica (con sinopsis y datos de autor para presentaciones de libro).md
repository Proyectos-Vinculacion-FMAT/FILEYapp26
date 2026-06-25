---
estado: DE ISSAC RECHAZAD
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVE-033
dominio: EVE
reglas_de_negocio: []
---
# CU-EVE-033 Mostrar el detalle de una actividad pública (con sinopsis y datos de autor para presentaciones de libro)

## Objetivo

El visitante consulta el detalle de una actividad publicada, incluyendo su sinopsis y —en presentaciones de libro o revista— los datos del autor y la publicación, para conocerla a fondo antes de asistir.

## Alcance

Módulo EVE — vista pública de detalle de actividad. Solo muestra actividades de la versión publicada (CU-EVE-029). Es de acceso público y de solo lectura.

## Actores

### Actor principal

- Visitante (público general)

### Actores secundarios

- Sistema (compone y presenta el detalle).

## Disparador

El visitante selecciona una actividad desde la cartelera pública (CU-EVE-032).

## Precondiciones

- La actividad pertenece a una versión del programa publicada.

## Postcondiciones

### En éxito

- Se muestra el detalle público de la actividad.

### En fallo

- No se muestra el detalle; se informa que la actividad no está disponible.

## Flujo principal

1. El visitante selecciona una actividad de la cartelera.
2. El sistema muestra el detalle público: título, tipo, organiza, público al que va dirigido, sinopsis, fecha, sala (o stand) y horario.
3. El sistema muestra los participantes y, si aplica, el moderador.

## Flujos alternos

### A1. Presentación de libro o revista

1. En el paso 2, la actividad es una presentación de libro o revista.
2. El sistema muestra adicionalmente los datos de la publicación: título de la publicación, autores/editores, editorial, portada y sinopsis del libro/revista, además de quiénes participarán presencialmente.

## Flujos de excepción

### E1. Actividad no publicada o retirada

1. En el paso 1, la actividad ya no pertenece a la versión publicada (fue despublicada o modificada).
2. El sistema informa que la actividad no está disponible y sugiere volver a la cartelera.

## Datos relevantes

### Entradas

- Identificador de la actividad.

### Salidas

- Detalle público de la actividad, con datos de publicación y autor cuando corresponda.
