---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-19
id: CU-STD-013
dominio: STD
reglas_de_negocio:
  - RN-02
  - RN-04
  - RN-11
---
# CU-STD-013 Consultar el estado de mi reserva (mapa, total, abonado, pendiente, descuento)

## Objetivo

La editorial consulta el estado de su reserva —stands, montos, descuento y fechas clave— para dar seguimiento a sus pagos y plazos.

## Alcance

Componente de Stands — módulo de Reserva. Vista principal del aplicante sobre su reserva ("Mi reserva"). Incluye el aviso de posible cancelación que se atiende en CU-STD-014.

## Actores

### Actor principal

- Aplicante (editorial / entidad expositora)

## Disparador

El aplicante abre la vista de su reserva.

## Precondiciones

- El aplicante tiene sesión iniciada.
- La editorial tiene una reserva registrada.

## Postcondiciones

### En éxito

- Se muestra el estado vigente de la reserva con sus montos, descuento y fechas.

### En fallo

- No se muestra la información; se informa la causa.

## Flujo principal

1. El aplicante abre la vista de su reserva.
2. El sistema muestra los stands reservados (en mapa y/o lista), el estado de la reserva (`Por confirmar` / `Confirmada` / `Pagada` / `Cancelada`, RN-11) y el descuento aplicado.
3. El sistema muestra el total con descuento, el monto abonado, el monto pendiente y el anticipo del 50% (RN-02).
4. El sistema muestra las fechas clave: vencimiento del anticipo (30 días) y, en su caso, fecha de corte del pago total.
5. Si aplica el descuento por pronto pago aún no consolidado, el sistema muestra la nota con el tiempo restante para conservarlo y el monto que aplicará tras la fecha de pronto pago (RN-04).

## Flujos alternos

### A1. Reserva vencida con aviso de posible cancelación

1. En el paso 2, la reserva está vencida sin haberse cubierto el anticipo del 50% (con abono parcial o sin abono).
2. El sistema muestra un aviso de posible cancelación que el aplicante puede atender (CU-STD-014).
3. El flujo continúa mostrando el resto de la información.

## Flujos de excepción

### E1. La editorial no tiene reserva

1. En el paso 1 la editorial aún no ha realizado una reserva.
2. El sistema informa que no hay reserva y dirige al mapa para iniciar una (CU-STD-009).

## Datos relevantes

### Entradas

- Reserva de la editorial.

### Salidas

- Estado de la reserva: stands, total con descuento, abonado, pendiente, anticipo, descuento y fechas clave.
