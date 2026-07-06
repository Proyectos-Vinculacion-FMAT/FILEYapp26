---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-036
modulo: D. Confirmación y estados
actor_principal: Administrador
requisitos_relacionados: []
dependencias:
  - CU-STD-029
---
# CU-STD-036 Modificar la fecha de corte o bloqueo de una reserva

## Descripción

El administrador gestiona de forma individualizada la fecha límite para el pago del 100% de una reserva, extendiéndola en casos particulares. Esta fecha controla el último gran corte antes del evento.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada.
- La reserva se encuentra en estado `Confirmada` (50% abonado).

## Disparador

El administrador requiere otorgar más tiempo a un expositor en particular para liquidar su saldo y selecciona la opción de edición en el detalle de la reserva.

## Flujo principal

1. El administrador ingresa a la vista de detalle de una reserva confirmada (A4).
2. El administrador selecciona la acción "Modificar fecha de corte total".
3. El sistema muestra la `fecha_corte_pago_total` actual asignada a la reserva (la cual pudo heredarse de los `ParametrosSistema`).
4. El administrador selecciona una nueva fecha desde el selector.
5. El administrador confirma la acción.
6. El sistema actualiza el registro de la `Reserva` con la nueva fecha de corte.
7. El sistema guarda la acción en la `Bitacora`.
8. La vista se recarga mostrando la nueva fecha, de modo que el sistema de alertas (que podría evaluar futuros vencimientos) respete esta nueva holgura.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

> [!note] Opcional
> Sin excepciones relevantes.

## Postcondiciones

- **Éxito:** La fecha se actualiza y la reserva extiende su plazo de liquidación total sin disparar alertas prematuras.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-13:** La fecha de corte para el 100% se gestiona caso por caso por el administrador (aunque parta de una base general).
