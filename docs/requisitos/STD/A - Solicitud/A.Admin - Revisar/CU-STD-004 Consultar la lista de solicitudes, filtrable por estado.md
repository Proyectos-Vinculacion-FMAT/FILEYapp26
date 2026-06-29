---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-19
id: CU-STD-004
dominio: STD
reglas_de_negocio: []
---
# CU-STD-004 Consultar la lista de solicitudes, filtrable por estado

## Objetivo

El administrador obtiene un panorama de las solicitudes recibidas, filtrable por estado, para priorizar y dar seguimiento a su revisión.

## Alcance

Componente de Stands — módulo de Solicitud. Vista de consulta del administrador; el detalle y la resolución de cada solicitud se cubren en CU-STD-005, CU-STD-006 y CU-STD-007.

## Actores

### Actor principal

- Administrador (coordinador del showfloor)

## Disparador

El administrador abre la sección de Solicitudes del panel.

## Precondiciones

- El administrador tiene sesión iniciada con rol de administrador.

## Postcondiciones

### En éxito

- Se muestra la lista de solicitudes del evento según los filtros aplicados.

### En fallo

- No se muestra la lista; se informa la condición (sin resultados o error de consulta).

## Flujo principal

1. El administrador abre la sección de Solicitudes.
2. El sistema muestra las solicitudes del evento con su estado (`pendiente` / `aceptada` / `rechazada` / `cambios_solicitados`), la editorial y la fecha de envío.
3. El administrador aplica filtros (estado y/o búsqueda por editorial).
4. El sistema actualiza la lista conforme a los filtros.
5. El administrador selecciona una solicitud para ver su detalle (CU-STD-005).

## Flujos alternos

### A1. Lista sin filtros

1. En el paso 3 el administrador no aplica ningún filtro.
2. El sistema muestra todas las solicitudes del evento y el flujo continúa en el paso 5.

## Flujos de excepción

### E1. Sin solicitudes que cumplan el filtro

1. En el paso 4 ninguna solicitud cumple los criterios seleccionados.
2. El sistema muestra la lista vacía con un aviso y mantiene los filtros para ajustarlos.

## Datos relevantes

### Entradas

- Criterios de filtrado: estado y/o texto de búsqueda por editorial.

### Salidas

- Lista de solicitudes con estado, editorial y fecha de envío.
