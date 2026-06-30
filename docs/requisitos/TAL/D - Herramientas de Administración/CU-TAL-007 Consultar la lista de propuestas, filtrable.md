---
estado: propuesta
version: 0.2
tags:
  - tipo/caso-de-uso
  - dom/tal
fecha: 2026-06-29
id: CU-TAL-007
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-007 Consultar la lista de propuestas, filtrable

> [!note] Sección nueva (2026-06-29) — equivalente a CU-EVT-007
> Esta sección **B** no existía en la primera homologación de `TAL`: se asumía, por error, que
> Elvira no revisaba propuesta por propuesta. **Corregido directamente por el cliente:** Elvira
> sí revisa y dictamina cada propuesta en el sistema, igual que Hipólito en `EVT`. Ver
> "Ajustes de homologación" en `CU-TAL Índice.md`.

## Objetivo

Elvira obtiene un panorama de las propuestas de taller recibidas en la edición, filtrable por tipo de actividad y estado, para priorizar y dar seguimiento a su revisión.

## Alcance

Módulo de Talleres (TAL) — vista de consulta de Elvira. El detalle y el dictamen de cada propuesta se cubren en CU-TAL-008 y CU-TAL-009. No cubre la notificación de resultados (CU-TAL-010).

## Actores

### Actor principal

- Administrador (Elvira)

## Disparador

Elvira abre la sección de Propuestas del módulo de Talleres.

## Precondiciones

- Elvira tiene sesión iniciada con permisos del módulo TAL.

## Postcondiciones

### En éxito

- Se muestra la lista de propuestas de la edición activa según los filtros aplicados.

### En fallo

- No se muestra la lista; se informa la condición (sin resultados o error de consulta).

## Flujo principal

1. Elvira abre la sección de Propuestas.
2. El sistema muestra las propuestas de la edición activa con: folio, nombre del evento, tipo de actividad, estado (`pendiente` / `cambios_solicitados` / `aceptada` / `rechazada`) y fecha de registro. En el encabezado de la lista se muestran los totales por estado para el conjunto de resultados visible.
3. Elvira aplica filtros por tipo de actividad y/o estado, o busca por texto (folio, responsable o nombre del evento).
4. El sistema actualiza la lista conforme a los filtros.
5. Elvira selecciona una propuesta para ver su detalle (CU-TAL-008).

## Flujos alternos

### A1. Lista sin filtros

1. En el paso 3, Elvira no aplica ningún filtro.
2. El sistema muestra todas las propuestas de la edición activa y el flujo continúa en el paso 5.

## Flujos de excepción

### E1. Sin propuestas que cumplan el filtro

1. En el paso 4, ninguna propuesta cumple los criterios seleccionados.
2. El sistema muestra la lista vacía con un aviso y mantiene los filtros para ajustarlos.

## Datos relevantes

### Entradas

- Criterios de filtrado: tipo de actividad, estado y/o texto de búsqueda.

### Salidas

- Lista de propuestas con folio, evento, tipo, estado y fecha de registro.
- Resumen numérico en el encabezado: total de propuestas encontradas y desglose por estado (`pendiente`, `cambios_solicitados`, `aceptada`, `rechazada`).
