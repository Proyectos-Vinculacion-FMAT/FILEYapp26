---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-025
modulo: D. Confirmación y estados
actor_principal: Sistema
requisitos_relacionados: []
dependencias:
  - CU-STD-022
---
# CU-STD-025 Notificar al administrador las reservas vencidas (con o sin abono)

## Descripción

El sistema levanta una alerta y notifica al administrador cuando el plazo de 30 días de una reserva ha expirado sin que se haya cubierto el 50% del anticipo, colocándola en su cola de resolución.

## Actores

- **Actor principal:** Sistema

## Precondiciones

- Una reserva superó su `fecha_vencimiento_anticipo` sin alcanzar el 50% del pago (condición evaluada en CU-STD-022).

## Disparador

El sistema detecta el vencimiento del plazo como parte de su revisión temporal (CU-STD-022).

## Flujo principal

1. El sistema identifica la reserva como "vencida".
2. El sistema redacta un correo electrónico dirigido al administrador (coordinador del showfloor) detallando la reserva: editorial, fecha límite expirada, monto total y monto abonado actualmente (si lo hay).
3. El sistema envía el correo electrónico a través de la plataforma de notificaciones.
4. El sistema guarda un registro en la entidad `Notificacion` vinculada a la reserva, para propósitos de auditoría.
5. El sistema destaca la reserva con un indicador visual de "Vencida" en la vista de lista de reservas del administrador (A3).
6. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Fallo en el envío de correo
1. En el paso 3, el servicio de correo electrónico no responde o falla.
2. El sistema marca la notificación como `fallida` en la entidad `Notificacion` y reintenta en el próximo ciclo (o delega la visibilidad al indicador visual del paso 5).

## Postcondiciones

- **Éxito:** El administrador es advertido de la situación irregular de la reserva para tomar acción.
- **Fallo:** El sistema retiene el estado de error y reintenta enviar el correo, manteniendo la advertencia visual.

## Reglas de negocio relacionadas

- **RN-12:** Al vencer los 30 días, el sistema no libera ni cancela la reserva automáticamente, sino que requiere la notificación al administrador para su resolución.
