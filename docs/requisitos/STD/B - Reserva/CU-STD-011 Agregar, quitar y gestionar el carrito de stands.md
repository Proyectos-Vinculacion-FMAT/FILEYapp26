---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - stands
fecha: 2026-06-19
id: CU-STD-011
dominio: STD
reglas_de_negocio:
  - RN-01
  - RN-09
---
# CU-STD-011 Agregar, quitar y gestionar el carrito de stands

## Objetivo

La editorial arma su selección de stands en un carrito —agregando y quitando espacios— y ve el subtotal estimado antes de formalizar la reserva.

## Alcance

Componente de Stands — módulo de Reserva. El carrito es una **selección de trabajo**: no aparta ni bloquea los stands; estos se protegen solo al confirmar la reserva (CU-STD-012). No hay límite en la cantidad de stands.

## Actores

### Actor principal

- Usuario (editorial / entidad expositora)

## Disparador

El usuario agrega un stand al carrito desde su detalle (CU-STD-010), o abre su carrito para gestionarlo.

## Precondiciones

- El usuario tiene sesión iniciada y está habilitado para reservar (RN-16).
- La editorial no tiene una reserva activa (se permite una sola reserva por editorial; agregar más stands a una reserva existente se considera ampliación, fuera de alcance).

## Postcondiciones

### En éxito

- El carrito refleja los stands seleccionados y el subtotal estimado vigente.

### En fallo

- El carrito no se modifica; se informa la causa (stand no disponible).

## Flujo principal

1. El usuario agrega un stand disponible al carrito.
2. El sistema incorpora el stand y recalcula el subtotal estimado (suma de m² × costo por m² de cada stand, RN-01).
3. El usuario puede quitar stands o seguir agregando.
4. El sistema mantiene actualizada la lista de stands y el subtotal.
5. Cuando el usuario está conforme, continúa a formalizar la reserva (CU-STD-012).

## Flujos alternos

### A1. Quitar un stand del carrito

1. En el paso 3 el usuario quita un stand de su selección.
2. El sistema actualiza la lista y recalcula el subtotal, y el flujo continúa en el paso 4.

## Flujos de excepción

### E1. El stand dejó de estar disponible

1. Al agregar un stand (paso 1) o al revisar el carrito, el stand ya fue reservado por otra editorial y aparece como no disponible (RN-09).
2. El sistema impide agregarlo —o lo marca como no disponible si ya estaba en el carrito— e informa al usuario para que ajuste su selección.

## Datos relevantes

### Entradas

- Stands seleccionados (agregar/quitar).

### Salidas

- Carrito con la lista de stands y el subtotal estimado.

> [!note] Supuesto de diseño
> El carrito se modela como una selección temporal del usuario, sin persistencia comprometida entre sesiones ni apartado de stands. Confirmar con el equipo si debe persistir.
