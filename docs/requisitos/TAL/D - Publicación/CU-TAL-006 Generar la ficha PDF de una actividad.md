---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/tal
fecha: 2026-06-29
id: CU-TAL-006
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-006 Generar la ficha PDF de una actividad

## Objetivo

Obtener una ficha PDF de una actividad de taller con sus datos esenciales, para compartirla o difundirla de forma puntual sin exportar todo el programa.

## Alcance

Módulo de Talleres (TAL) — generación de ficha individual. Produce un PDF de una sola actividad. No cubre la exportación del programa completo; para exportar el programa completo a Excel/Word ver CU-PRG-011 en `PRG/CU-PRG Índice.md`.

## Actores

### Actor principal

- Tallerista o Administrador (quien solicita la ficha)

### Actores secundarios

- Sistema (genera el documento).

## Disparador

El actor solicita la ficha PDF desde el detalle de una actividad.

## Precondiciones

- La actividad existe y, si la solicita un tercero, pertenece al catálogo final publicado (ver nota "VIS solo consume horario final" en `CU-TAL Índice.md`).

## Postcondiciones

### En éxito

- Se genera y entrega un PDF con los datos de la actividad.

### En fallo

- No se genera el PDF; el sistema informa el motivo.

## Flujo principal

1. El actor solicita "Generar ficha PDF" desde el detalle de una actividad.
2. El sistema recopila los datos de la actividad: nombre del evento, tipo de actividad, organiza, público meta, fecha, sala y horario.
3. El sistema genera el documento PDF con esos datos.
4. El sistema entrega el archivo para su descarga.

## Flujos alternos

### A1. Actividad con datos de presentación (autor, presentador o editorial)

1. En el paso 2, la actividad tiene registrados datos de presentación (autor(a)/autores, quien presenta/participa o editorial).
2. El sistema incluye esos datos adicionales en la ficha cuando están disponibles.
3. El flujo continúa en el paso 3.

## Flujos de excepción

### E1. Actividad sin horario asignado

1. En el paso 2, la actividad aún no tiene sala u horario asignado (final).
2. El sistema genera la ficha indicando "horario por confirmar" en los campos faltantes, o informa que la ficha no está disponible hasta su programación final, según la política de publicación vigente.

## Datos relevantes

### Entradas

- Identificador de la actividad.

### Salidas

- Ficha PDF de la actividad (nombre del evento, tipo, organiza, público meta, fecha, sala y horario).
