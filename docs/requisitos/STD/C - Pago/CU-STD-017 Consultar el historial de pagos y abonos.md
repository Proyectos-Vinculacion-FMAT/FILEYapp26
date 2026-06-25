---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-017
modulo: C. Pago
actor_principal: Usuario
requisitos_relacionados: []
dependencias:
  - CU-STD-016
---
# CU-STD-017 Consultar el historial de pagos y abonos

## Descripción

El usuario visualiza la lista de todos los abonos o pagos que ha registrado para su reserva, incluyendo el estado de validación de cada uno (pendiente, validado o rechazado).

## Actores

- **Actor principal:** Usuario (editorial / entidad expositora)

## Precondiciones

- El usuario tiene sesión iniciada.
- Existe al menos una reserva ligada a la cuenta.

## Disparador

El usuario navega a la sección de historial de pagos dentro del portal de su reserva.

## Flujo principal

1. El usuario accede a la pestaña o sección de "Historial de pagos" (parte de la vista U6).
2. El sistema recupera todos los registros de la entidad `Movimiento` asociados a la reserva actual.
3. El sistema muestra los movimientos ordenados por fecha (del más reciente al más antiguo), detallando:
   - Fecha de registro.
   - Monto abonado.
   - Método de pago.
   - Estado actual (`pendiente_validacion`, `validado`, `rechazado`).
4. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Sin historial de movimientos
1. En el paso 2, el sistema detecta que no existen movimientos registrados para la reserva.
2. El sistema muestra un mensaje indicando que "Aún no se han registrado pagos o abonos".
3. El caso de uso termina.

## Postcondiciones

- **Éxito:** El usuario visualiza de manera clara el estado de todos los comprobantes que ha enviado.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

> [!note] Opcional
> No hay reglas de negocio específicas para la consulta, solo las que determinan los estados mostrados.
