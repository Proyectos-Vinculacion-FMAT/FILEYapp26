---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVT-006
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-006 Consultar la lista de propuestas recibidas, filtrable por tipo, estado y categoría

## Objetivo

El administrador obtiene un panorama de las propuestas recibidas en la edición, filtrable por tipo de actividad, estado y categoría, para priorizar y dar seguimiento a su revisión continua semana a semana.

## Alcance

Módulo EVE — vista de consulta del administrador. El detalle y el dictamen de cada propuesta se cubren en CU-EVT-007 y CU-EVT-008. No cubre la notificación de resultados (CU-EVT-012).

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

El administrador abre la sección de Propuestas del panel del módulo EVE.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.

## Postcondiciones

### En éxito

- Se muestra la lista de propuestas de la edición activa según los filtros aplicados.

### En fallo

- No se muestra la lista; se informa la condición (sin resultados o error de consulta).

## Flujo principal

1. El administrador abre la sección de Propuestas.
2. El sistema muestra las propuestas de la edición activa con: folio, nombre de la actividad, proponente, tipo de actividad, categoría, estado (`pendiente` / `cambios_solicitados` / `aceptada` / `rechazada`) y fecha de registro.
3. El administrador aplica filtros por tipo de actividad, estado y/o categoría, o busca por texto (folio, proponente o título).
4. El sistema actualiza la lista conforme a los filtros.
5. El administrador selecciona una propuesta para ver su detalle (CU-EVT-007).

## Flujos alternos

### A1. Lista sin filtros

1. En el paso 3, el administrador no aplica ningún filtro.
2. El sistema muestra todas las propuestas de la edición activa y el flujo continúa en el paso 5.

## Flujos de excepción

### E1. Sin propuestas que cumplan el filtro

1. En el paso 4, ninguna propuesta cumple los criterios seleccionados.
2. El sistema muestra la lista vacía con un aviso y mantiene los filtros para ajustarlos.

## Datos relevantes

### Entradas

- Criterios de filtrado: tipo de actividad, estado, categoría y/o texto de búsqueda.

### Salidas

- Lista de propuestas con folio, actividad, proponente, tipo, categoría, estado y fecha de registro.
