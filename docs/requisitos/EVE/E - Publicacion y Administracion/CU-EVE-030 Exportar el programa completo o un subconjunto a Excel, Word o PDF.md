---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVE-030
dominio: EVE
reglas_de_negocio: []
---
# CU-EVE-030 Exportar el programa completo o un subconjunto a Excel, Word o PDF

## Objetivo

El administrador exporta el programa —completo o un subconjunto filtrado— a Excel, Word o PDF, para trabajarlo fuera del sistema, compartirlo con su editor o entregarlo para diseño y difusión.

## Alcance

Módulo EVE — exportación del programa. Genera un archivo descargable a partir de los datos del programa. No publica la cartelera pública (CU-EVE-029) ni genera la ficha individual de una actividad (CU-EVE-031).

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

El administrador necesita una versión del programa en un formato de archivo para trabajo externo.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.
- Existe al menos una actividad en el programa de la edición activa.

## Postcondiciones

### En éxito

- Se genera y descarga un archivo en el formato elegido (Excel, Word o PDF) con el contenido seleccionado.

### En fallo

- No se genera el archivo; el sistema informa el motivo.

## Flujo principal

1. El administrador abre la opción de exportar programa.
2. El sistema permite definir el alcance: programa completo o un subconjunto por filtros (categoría, sección, tipo de actividad, día o sala).
3. El administrador elige el formato de salida: Excel, Word o PDF.
4. El administrador confirma la exportación.
5. El sistema genera el archivo con las actividades que cumplen el alcance, incluyendo sus datos de programación (actividad, tipo, organiza, fecha, sala y horario).
6. El sistema entrega el archivo para su descarga.

## Flujos alternos

### A1. Exportar un subconjunto filtrado

1. En el paso 2, el administrador aplica filtros para acotar el contenido.
2. El sistema exporta únicamente las actividades que cumplen los filtros y el flujo continúa en el paso 3.

## Flujos de excepción

### E1. Sin actividades en el alcance seleccionado

1. En el paso 5, ninguna actividad cumple el alcance o los filtros definidos.
2. El sistema informa que no hay contenido que exportar y no genera el archivo.

## Datos relevantes

### Entradas

- Alcance de exportación (completo o filtros).
- Formato de salida (Excel / Word / PDF).

### Salidas

- Archivo del programa en el formato elegido, listo para descarga.
