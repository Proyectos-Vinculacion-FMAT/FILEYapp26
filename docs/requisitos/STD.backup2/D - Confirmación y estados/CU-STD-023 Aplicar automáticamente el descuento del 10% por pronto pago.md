---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-023
modulo: D. Confirmación y estados
actor_principal: Sistema
requisitos_relacionados: []
dependencias:
  - CU-STD-018
  - CU-STD-019
---
# CU-STD-023 Aplicar automáticamente el descuento del 10% por pronto pago

## Descripción

El sistema consolida el descuento por pronto pago si la editorial liquida el monto total con descuento antes de la fecha límite establecida. Si la fecha expira sin que se haya liquidado, el sistema retira la oferta y ajusta el monto pendiente al precio regular.

## Actores

- **Actor principal:** Sistema

## Precondiciones

- La reserva tiene un saldo pendiente y se encuentra dentro de la fecha límite de pronto pago.

## Disparador

Validación de un abono (CU-STD-018 o CU-STD-019) o ejecución de la revisión diaria de vencimientos del sistema.

## Flujo principal

1. El sistema realiza una evaluación de la reserva (activada por un nuevo abono o por rutina diaria).
2. El sistema compara la fecha actual con la `fecha_limite_pronto_pago` global configurada en `ParametrosSistema`.
3. Si la fecha vigente aún es válida para el pronto pago, el sistema verifica si el `monto_abonado` es igual o mayor al monto total menos el 10%.
4. Al cumplirse la condición, el sistema registra definitivamente el descuento en la entidad `DescuentoAplicado` con tipo `pronto_pago` y el porcentaje (10%).
5. El sistema recalcula el total, establece que la reserva está cubierta al 100% y dispara el cambio de estado a Pagada (CU-STD-030).
6. El caso de uso termina.

## Flujos alternativos

### A1. Vencimiento del plazo de pronto pago sin liquidar

1. En el paso 3, el sistema (mediante rutina diaria) detecta que la `fecha_limite_pronto_pago` ha expirado y la reserva no alcanzó el 100% del pago reducido.
2. El sistema retira de la vista del aplicante el aviso del beneficio de pronto pago.
3. El sistema recalcula el `monto_pendiente` considerando el 100% del costo original de los stands (sin descuento).
4. El caso de uso termina.

## Excepciones

> [!note] Opcional
> Sin excepciones relevantes.

## Postcondiciones

- **Éxito:** El descuento queda consolidado de manera permanente y la reserva se marca como pagada, o bien, el beneficio expira y la reserva vuelve a su costo normal.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-04:** Descuento del 10% por pronto pago si se liquida antes de una fecha límite; se aplica automáticamente.
