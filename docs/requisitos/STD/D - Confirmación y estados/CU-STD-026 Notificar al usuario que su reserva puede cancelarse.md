---
estado: propuesta
version: 0.1
tags:
  - caso-de-uso
  - stands
fecha: 2026-06-22
id: CU-STD-026
modulo: D. Confirmación y estados
actor_principal: Sistema
requisitos_relacionados: []
dependencias:
  - CU-STD-022
---
# CU-STD-026 Notificar al usuario que su reserva puede cancelarse

## Descripción

El sistema advierte al expositor, mediante un correo y un banner en su portal, que su reserva ha expirado por falta del pago de anticipo y se encuentra en riesgo de cancelación.

## Actores

- **Actor principal:** Sistema

## Precondiciones

- Una reserva superó su `fecha_vencimiento_anticipo` sin alcanzar el 50% del pago (condición evaluada en CU-STD-022).

## Disparador

El sistema detecta el vencimiento del plazo como parte de su revisión temporal (CU-STD-022).

## Flujo principal

1. El sistema identifica la reserva como "vencida".
2. El sistema redacta un correo electrónico dirigido al correo de contacto de la editorial, informando que el plazo de 30 días concluyó y su reserva corre riesgo de ser liberada.
3. El correo incluye instrucciones para regularizar la situación de inmediato o contactar a la organización.
4. El sistema envía el correo a través de la plataforma.
5. El sistema guarda un registro en la entidad `Notificacion` vinculada a la reserva y a la cuenta del usuario.
6. El sistema activa un banner o aviso en la vista de "Mi reserva" (U5) advirtiendo sobre el vencimiento, el cual el usuario verá al iniciar sesión (CU-STD-014).
7. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Fallo en el envío de correo
1. En el paso 4, el servicio de correo electrónico falla.
2. El sistema marca la notificación como `fallida` y reintenta posteriormente. El banner en la plataforma web (paso 6) funciona independientemente y asegura la comunicación.

## Postcondiciones

- **Éxito:** El usuario es debidamente avisado del riesgo de perder sus stands.
- **Fallo:** Si el correo falla, la advertencia persistirá dentro del portal.

## Reglas de negocio relacionadas

- **RN-12:** Notificar tanto al usuario como al administrador sobre la expiración del plazo, antes de tomar medidas destructivas (cancelación).
