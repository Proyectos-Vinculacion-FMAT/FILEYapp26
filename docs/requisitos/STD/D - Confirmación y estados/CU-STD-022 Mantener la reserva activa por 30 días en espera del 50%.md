---
estado: propuesta
version: 0.1
tags:
  - caso-de-uso
  - stands
fecha: 2026-06-22
id: CU-STD-022
modulo: D. Confirmación y estados
actor_principal: Sistema
requisitos_relacionados: []
dependencias:
  - CU-STD-012
  - CU-STD-025
  - CU-STD-026
---
# CU-STD-022 Mantener la reserva activa por 30 días en espera del anticipo

## Descripción

El sistema calcula y asigna la fecha límite inicial para que el usuario cubra su anticipo, permitiendo que la reserva se mantenga vigente. Si el plazo expira sin alcanzar el monto requerido, el sistema levanta las alertas correspondientes.

## Actores

- **Actor principal:** Sistema

## Precondiciones

- Se ha creado una nueva reserva en estado `Por confirmar`.

## Disparador

Creación exitosa de la reserva, o una prórroga otorgada por el administrador (modificación manual de la fecha límite).

## Flujo principal

1. Al crearse la reserva (CU-STD-012), el sistema lee el parámetro de plazo (30 días por defecto) desde `ParametrosSistema`.
2. El sistema calcula la `fecha_vencimiento_anticipo` sumando los días a la fecha actual y la guarda en la entidad `Reserva` (RN-03).
3. Diariamente (o mediante una tarea programada), el sistema monitorea todas las reservas en estado `Por confirmar`.
4. Cuando el sistema detecta que la fecha actual ha superado la `fecha_vencimiento_anticipo` de una reserva, verifica el `monto_abonado`.
5. Si el saldo abonado es menor al 50% requerido, la reserva pasa a considerarse "vencida".
6. El sistema dispara la notificación al administrador (CU-STD-025) y la advertencia al usuario (CU-STD-026).
7. La reserva se mantiene en el sistema, pero requiere intervención del administrador para ser cancelada o prorrogada.

## Flujos alternativos

### A1. Anticipo cubierto antes del plazo

1. En el paso 4, el sistema detecta que el `monto_abonado` ya es igual o mayor al anticipo del 50%.
2. El sistema omite las notificaciones de vencimiento, ya que la reserva fue previamente bloqueada y pasada a `Confirmada` (CU-STD-029).

## Excepciones

> [!note] Opcional
> Sin excepciones relevantes.

## Postcondiciones

- **Éxito:** Las reservas que expiran sin pagar son notificadas para su gestión administrativa; el sistema no libera stands de forma autónoma.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-03:** La reserva permanece activa 30 días a partir de su creación, en espera del 50%.
- **RN-12:** Al vencer los 30 días sin haberse cubierto el 50%, el sistema no libera ni cancela la reserva: notifica y espera decisión del administrador.
