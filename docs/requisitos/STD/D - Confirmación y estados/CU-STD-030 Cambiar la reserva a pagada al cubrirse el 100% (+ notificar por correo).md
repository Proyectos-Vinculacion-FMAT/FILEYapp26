---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-030
modulo: D. Confirmación y estados
actor_principal: Sistema
requisitos_relacionados: []
dependencias:
  - CU-STD-018
  - CU-STD-019
---
# CU-STD-030 Cambiar la reserva a pagada al cubrirse el 100% (+ notificar)

## Descripción

El sistema marca el fin del ciclo de pagos de una reserva cuando los abonos validados alcanzan la totalidad del monto adeudado, notificando la liquidación final al expositor.

## Actores

- **Actor principal:** Sistema

## Precondiciones

- La reserva se encontraba en estado `Confirmada` (o `Por confirmar` si liquidó el total en un solo pago).
- El administrador validó un abono, registró uno manual o el sistema aplicó el descuento de pronto pago.

## Disparador

El saldo abonado acumulado (`monto_abonado`) iguala al `monto_total`.

## Flujo principal

1. Durante la reevaluación del saldo, el sistema detecta que el `monto_pendiente` ha llegado a cero o menos.
2. El sistema cambia el estado de la entidad `Reserva` a `Pagada` (RN-14).
3. Si los stands de la reserva estaban en estado `Reservado`, el sistema los cambia a `Ocupado` en el mapa del showfloor (RN-10). *(Nota: Ante el público general siguen viéndose como "no disponibles" según RN-09).*
4. El sistema redacta y envía un correo electrónico al expositor informándole que su saldo está liquidado al 100%.
5. El sistema crea el registro en la entidad `Notificacion`.
6. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

> [!note] Opcional
> Sin excepciones relevantes.

## Postcondiciones

- **Éxito:** La reserva concluye su ciclo comercial exitosamente.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-14:** Al cubrir el 100%, la reserva pasa a Pagada.
- **RN-10:** Estados de un stand: Disponible, Reservado, Ocupado.
