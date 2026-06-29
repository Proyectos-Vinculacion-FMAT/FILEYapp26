---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-19
id: CU-STD-012
dominio: STD
reglas_de_negocio:
  - RN-01
  - RN-02
  - RN-03
  - RN-04
  - RN-10
  - RN-11
  - RN-16
---
# CU-STD-012 Realizar la reserva de los stands seleccionados

## Objetivo

La editorial formaliza la reserva de los stands de su carrito, obteniendo una reserva con su total, descuento y anticipo calculados, e inicia el plazo para cubrir el anticipo.

## Alcance

Componente de Stands — módulo de Reserva. Es el punto en que los stands se protegen contra doble reserva: se marcan como Reservado únicamente al confirmar (no antes). Genera una sola reserva por editorial.

## Actores

### Actor principal

- Aplicante (editorial / entidad expositora)

## Disparador

El aplicante decide formalizar la reserva desde su carrito (CU-STD-011).

## Precondiciones

- El aplicante tiene sesión iniciada y está habilitado para reservar (RN-16).
- El carrito tiene al menos un stand.
- La editorial no tiene una reserva activa (una reserva por editorial).

## Postcondiciones

### En éxito

- Se crea una reserva en estado `Por confirmar` (RN-11) asociada a la editorial y al evento, con una línea por stand y los snapshots de m² y precio.
- Cada stand reservado pasa a estado Reservado (RN-10; CU-STD-021).
- Inicia el plazo de 30 días para cubrir el anticipo del 50% (RN-03).
- Quedan calculados el total con descuento, el anticipo del 50% (RN-02) y el descuento aplicado.

### En fallo

- No se crea la reserva y los stands permanecen disponibles; se informa la causa (conflicto de disponibilidad o carrito vacío).

## Flujo principal

1. El aplicante solicita formalizar la reserva.
2. El sistema muestra el resumen: stands seleccionados, total y descuento aplicable, anticipo del 50% sobre el total con descuento (RN-02) y plazo de 30 días (RN-03).
3. El sistema calcula el total considerando el descuento del 10% por pronto pago (RN-04), y muestra una nota con el **tiempo restante** para conservar ese descuento y el **monto que aplicará** una vez vencida la fecha de pronto pago.
4. El aplicante confirma la reserva.
5. El sistema valida que todos los stands del carrito sigan disponibles.
6. El sistema crea la reserva en estado `Por confirmar`, genera una línea por stand con los snapshots de m² y precio (RN-01), marca los stands como Reservado (CU-STD-021) e inicia el plazo de 30 días (RN-03).
7. El sistema registra el descuento aplicado y calcula el anticipo del 50% (RN-02).
8. El sistema confirma la reserva al aplicante y lo dirige a las instrucciones de pago (CU-STD-015).

## Flujos alternos



## Flujos de excepción

### E1. Uno o más stands dejaron de estar disponibles

1. En el paso 5 el sistema detecta que algún stand del carrito ya fue reservado por otra editorial.
2. El sistema no crea la reserva, informa cuáles stands ya no están disponibles y los retira de la selección.
3. El aplicante ajusta su carrito y reintenta desde el paso 1 (primero en confirmar gana).

### E2. Carrito vacío

1. En el paso 1 el carrito no tiene stands.
2. El sistema impide formalizar la reserva e invita a seleccionar stands en el mapa (CU-STD-009).

## Datos relevantes

### Entradas

- Stands del carrito.


### Salidas

- Reserva en estado `Por confirmar` con líneas por stand, total con descuento, anticipo del 50% y fecha de vencimiento del anticipo.
