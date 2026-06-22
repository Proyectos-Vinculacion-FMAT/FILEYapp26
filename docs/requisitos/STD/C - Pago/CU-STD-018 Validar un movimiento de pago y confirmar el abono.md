---
estado: propuesta
version: 0.1
tags:
  - caso-de-uso
  - stands
fecha: 2026-06-22
id: CU-STD-018
modulo: C. Pago
actor_principal: Administrador
requisitos_relacionados: []
dependencias:
  - CU-STD-016
  - CU-STD-029
  - CU-STD-030
---
# CU-STD-018 Validar un movimiento de pago y confirmar el abono

## Descripción

El administrador revisa un pago enviado por el usuario, coteja el comprobante con los estados de cuenta bancarios y decide validarlo (sumándolo al saldo abonado de la reserva) o rechazarlo.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada.
- Existe al menos un movimiento en estado `pendiente_validacion`.

## Disparador

El administrador selecciona un pago pendiente para revisarlo, ya sea desde la cola global de pagos por validar (A5) o desde el detalle de una reserva específica (A4).

## Flujo principal

1. El administrador abre el detalle del movimiento en estado `pendiente_validacion`.
2. El sistema muestra los datos del pago: monto declarado, fecha de registro, método de pago y el archivo del comprobante adjunto.
3. El administrador descarga o visualiza el comprobante bancario.
4. El administrador valida fuera del sistema que el depósito se haya reflejado correctamente en la cuenta bancaria de la Universidad.
5. El administrador hace clic en la acción "Validar abono".
6. El sistema cambia el estado del movimiento a `validado`.
7. El sistema suma el monto del movimiento al campo `monto_abonado` de la `Reserva` correspondiente y recalcula el `monto_pendiente`.
8. El sistema evalúa si el nuevo saldo total activa los procesos automáticos de confirmación (CU-STD-029, si se cubre el 50%) o de liquidación total (CU-STD-030, si se cubre el 100%).
9. El caso de uso termina.

## Flujos alternativos

### A1. Rechazar el movimiento

1. En el paso 5, el administrador detecta que el comprobante es inválido, ilegible o no se refleja en la cuenta bancaria.
2. El administrador selecciona la acción "Rechazar abono".
3. El sistema solicita opcionalmente un motivo o nota de rechazo.
4. El sistema cambia el estado del movimiento a `rechazado`.
5. El monto no se suma al saldo de la reserva.
6. El caso de uso termina (el usuario podrá ver el estado de rechazo en su historial, CU-STD-017).

## Excepciones

> [!note] Opcional
> Sin excepciones relevantes.

## Postcondiciones

- **Éxito:** El abono queda en firme (`validado`) y el saldo de la reserva se actualiza. Si se alcanzan los umbrales de pago (50% o 100%), se disparan los procesos correspondientes.
- **Fallo:** El abono es rechazado y el saldo de la reserva permanece intacto.

## Reglas de negocio relacionadas

- **RN-13:** Al cubrir el 50%, la reserva pasa a Confirmada (evaluado en el paso 8).
- **RN-14:** Al cubrir el 100%, la reserva pasa a Pagada (evaluado en el paso 8).
