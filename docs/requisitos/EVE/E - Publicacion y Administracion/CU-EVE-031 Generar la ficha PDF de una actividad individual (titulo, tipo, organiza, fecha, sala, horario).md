---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVE-031
dominio: EVE
reglas_de_negocio: []
---
# CU-EVE-031 Generar la ficha PDF de una actividad individual (título, tipo, organiza, fecha, sala, horario)

## Objetivo

Obtener una ficha PDF de una actividad individual con sus datos esenciales, para compartirla o difundirla de forma puntual sin exportar todo el programa.

## Alcance

Módulo EVE — generación de ficha individual. Produce un PDF de una sola actividad. No cubre la exportación del programa completo (CU-EVE-030) ni el detalle interactivo en la cartelera (CU-EVE-033).

## Actores

### Actor principal

- Visitante o Administrador (quien solicita la ficha)

### Actores secundarios

- Sistema (genera el documento).

## Disparador

El actor solicita la ficha PDF desde el detalle de una actividad.

## Precondiciones

- La actividad existe y, si la solicita un visitante, pertenece a una versión publicada del programa.

## Postcondiciones

### En éxito

- Se genera y entrega un PDF con los datos de la actividad.

### En fallo

- No se genera el PDF; el sistema informa el motivo.

## Flujo principal

1. El actor solicita "Generar ficha PDF" desde el detalle de una actividad.
2. El sistema recopila los datos de la actividad: título, tipo, organiza, fecha, sala (o stand) y horario.
3. El sistema genera el documento PDF con esos datos.
4. El sistema entrega el archivo para su descarga.

## Flujos alternos

### A1. Actividad de presentación de libro/revista

1. En el paso 2, la actividad es una presentación de libro o revista.
2. El sistema incluye en la ficha los datos adicionales de la publicación (título de la publicación, autores/editores y portada) cuando están disponibles.
3. El flujo continúa en el paso 3.

## Flujos de excepción

### E1. Actividad sin horario asignado

1. En el paso 2, la actividad aún no tiene sala u horario asignado.
2. El sistema genera la ficha indicando "horario por confirmar" en los campos faltantes, o informa que la ficha no está disponible hasta su programación, según la política de publicación vigente.

## Datos relevantes

### Entradas

- Identificador de la actividad.

### Salidas

- Ficha PDF de la actividad (título, tipo, organiza, fecha, sala y horario).
