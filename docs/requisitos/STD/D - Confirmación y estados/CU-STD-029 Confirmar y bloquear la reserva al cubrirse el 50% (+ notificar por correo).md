---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-029
modulo: D. Confirmación y estados
actor_principal: Sistema
requisitos_relacionados: []
dependencias:
  - CU-STD-018
  - CU-STD-019
---
# CU-STD-029 Confirmar y bloquear la reserva al cubrirse el 50% (+ notificar)

## Descripción

El sistema formaliza la posesión de los stands (cambiando el estado a Confirmada) en el momento en que detecta que los abonos validados por el administrador alcanzan la cuota mínima del 50%, y notifica al usuario del éxito de la transacción.

## Actores

- **Actor principal:** Sistema

## Precondiciones

- La reserva se encontraba en estado `Por confirmar`.
- El administrador acaba de validar un abono (CU-STD-018) o registrar uno manual (CU-STD-019), o bien aplicó un descuento especial (CU-STD-020) que bajó el precio total.

## Disparador

El saldo abonado acumulado (`monto_abonado`) se iguala o supera al 50% del `monto_total` (con descuentos aplicados).

## Flujo principal

1. Durante la reevaluación del saldo, el sistema detecta que se alcanzó el umbral del anticipo (50%).
2. El sistema cambia el estado de la entidad `Reserva` de `Por confirmar` a `Confirmada` (RN-13).
3. El sistema elimina la restricción de vencimiento temporal (desactiva el contador de 30 días, si seguía activo).
4. El sistema hereda y asigna la `fecha_corte_pago_total` desde los parámetros globales (si estuviera definida).
5. El sistema redacta y envía un correo electrónico al expositor informando que su reserva ha sido confirmada formalmente.
6. El sistema crea el registro en la entidad `Notificacion`.
7. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

> [!note] Opcional
> Sin excepciones relevantes. Si el correo falla, se marca en bitácora pero el estado de la reserva sí se confirma.

## Postcondiciones

- **Éxito:** La reserva queda asegurada hasta su fecha final de corte.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-13:** Al cubrir el 50%, la reserva pasa a Confirmada y se bloquea hasta la fecha de corte para pago total.
