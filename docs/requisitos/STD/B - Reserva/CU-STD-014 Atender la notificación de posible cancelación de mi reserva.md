---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - stands
fecha: 2026-06-19
id: CU-STD-014
dominio: STD
reglas_de_negocio:
  - RN-12
---
# CU-STD-014 Atender la notificación de posible cancelación de mi reserva

## Objetivo

La editorial, advertida de que su reserva vencida puede cancelarse, conoce lo pendiente y actúa —registrando un pago— para conservar su reserva.

## Alcance

Componente de Stands — módulo de Reserva. La decisión final de cancelar o prorrogar la reserva vencida es del administrador (CU-STD-027); este caso de uso cubre la reacción del usuario, que se limita a regularizar su pago.

## Actores

### Actor principal

- Usuario (editorial / entidad expositora)

## Disparador

El usuario recibe el aviso (por correo y/o en "Mi reserva") de que su reserva vencida puede cancelarse.

## Precondiciones

- El usuario tiene sesión iniciada.
- La reserva está vencida sin haberse cubierto el anticipo del 50% (con abono parcial o sin abono, RN-12).
- El administrador aún no ha resuelto la reserva (cancelar o prorrogar).

## Postcondiciones

### En éxito

- El usuario queda informado del monto pendiente y la situación, y puede proceder a registrar un pago (CU-STD-016).

### En fallo

- No se muestra el detalle del aviso; se informa la causa (la reserva ya fue resuelta por el administrador).

## Flujo principal

1. El usuario abre el aviso de posible cancelación desde "Mi reserva" o desde el correo.
2. El sistema muestra el estado de la reserva, el monto pendiente para alcanzar el anticipo y la advertencia de posible cancelación (RN-12).
3. El usuario procede a registrar un pago para regularizar su reserva (CU-STD-016).

## Flujos alternos

### A1. El usuario no actúa

1. En el paso 3 el usuario no registra ningún pago.
2. La reserva permanece vencida a la espera de la resolución del administrador (cancelar o prorrogar, CU-STD-027).

## Flujos de excepción

### E1. La reserva ya fue resuelta por el administrador

1. En el paso 1 o 2 el sistema detecta que el administrador ya canceló o prorrogó la reserva.
2. El sistema muestra el estado vigente de la reserva en lugar del aviso de posible cancelación.

## Datos relevantes

### Entradas

- Reserva vencida sin haber cubierto el anticipo del 50%.

### Salidas

- Información del aviso: monto pendiente y situación de la reserva.

> [!note] Supuesto de diseño
> Se asume que la reacción del usuario se limita a pagar (CU-STD-016); no se contempla que el usuario solicite la prórroga desde el sistema. Confirmar con el equipo si debe existir una solicitud de prórroga iniciada por el usuario.
