---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-19
id: CU-STD-010
dominio: STD
reglas_de_negocio:
  - RN-01
  - RN-09
---
# CU-STD-010 Consultar el detalle de un stand (dimensiones y precio por m²)

## Objetivo

La editorial consulta el detalle de un stand disponible —dimensiones, superficie, precio y qué incluye— para decidir si lo agrega a su selección.

## Alcance

Componente de Stands — módulo de Reserva. Vista de detalle del aplicante, abierta desde el mapa (CU-STD-009). El precio mostrado es el del stand individual; los descuentos aplican sobre el total de la reserva (CU-STD-012).

## Actores

### Actor principal

- Aplicante (editorial / entidad expositora)

## Disparador

El aplicante selecciona un stand disponible en el mapa.

## Precondiciones

- El aplicante tiene sesión iniciada y está habilitado para reservar (RN-16).
- El stand existe en el mapa del evento.

## Postcondiciones

### En éxito

- Se muestra el detalle del stand y, si está disponible, la opción de agregarlo al carrito (CU-STD-011).

### En fallo

- No se muestra el detalle o no se ofrece agregarlo (stand no disponible).

## Flujo principal

1. El aplicante selecciona un stand en el mapa.
2. El sistema muestra la clave del stand, sus dimensiones (ancho y largo), su superficie en metros cuadrados y qué incluye (estructura, contactos, exhibidores, etc.).
3. El sistema muestra el precio del stand, calculado como metros cuadrados × costo por m² (RN-01).
4. Si el stand está disponible, el aplicante lo agrega al carrito (CU-STD-011).

## Flujos alternos

> [!note] Opcional
> Sin flujos alternos relevantes.

## Flujos de excepción

### E1. Stand no disponible

1. En el paso 2 el stand está marcado como no disponible (Reservado u Ocupado, RN-09).
2. El sistema muestra el detalle en modo informativo, sin ofrecer la opción de agregarlo al carrito.

## Datos relevantes

### Entradas

- Identificador del stand.

### Salidas

- Detalle del stand: clave, dimensiones, m², qué incluye y precio calculado.
