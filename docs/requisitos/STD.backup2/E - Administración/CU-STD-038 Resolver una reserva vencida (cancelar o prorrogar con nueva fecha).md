---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-038
modulo: D. Confirmación y estados
actor_principal: Administrador
requisitos_relacionados: []
dependencias:
  - CU-STD-032
---
# CU-STD-038 Resolver una reserva vencida (cancelar o prorrogar con nueva fecha)

## Descripción

El administrador actúa sobre una reserva que no cumplió con el pago del anticipo en el plazo estipulado, decidiendo si cancela la reserva para liberar los espacios o si otorga una prórroga estableciendo una nueva fecha de vencimiento.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada.
- Existe una reserva que ha superado su `fecha_vencimiento_anticipo` y fue marcada o notificada como vencida (estado `Por confirmar`).

## Disparador

El administrador ingresa al detalle de la reserva tras detectar la alerta visual o el correo de reserva vencida.

## Flujo principal

1. El administrador ingresa a la vista de detalle de la reserva (A4).
2. El administrador evalúa la situación (historial de pagos, comunicación externa con la editorial) y selecciona la acción "Resolver reserva vencida".
3. El sistema muestra dos opciones: "Prorrogar plazo" y "Cancelar reserva".
4. El administrador selecciona "Prorrogar plazo".
5. El sistema solicita seleccionar una nueva fecha para el `fecha_vencimiento_anticipo` a través de un calendario.
6. El administrador ingresa la nueva fecha y confirma.
7. El sistema actualiza el campo `fecha_vencimiento_anticipo`, borra la alerta visual de vencimiento y deja la reserva vigente.
8. El sistema guarda un registro de la acción en la `Bitacora`.

## Flujos alternativos

### A1. Cancelar la reserva

1. En el paso 4, el administrador selecciona "Cancelar reserva".
2. El sistema solicita confirmación advirtiendo que es una acción irreversible y solicita opcionalmente un motivo.
3. El administrador confirma.
4. El sistema cambia el estado de la `Reserva` a `Cancelada`.
5. El sistema recorre las líneas `ReservaStand` y cambia el estado de los stands vinculados en la entidad `Stand` de `Reservado` (u `Ocupado`) a `Disponible`.
6. El sistema guarda un registro en la `Bitacora` y dispara una notificación al aplicante (entidad `Notificacion`).
7. El caso de uso termina.

## Excepciones

> [!note] Opcional
> Sin excepciones relevantes.

## Postcondiciones

- **Éxito:** La reserva queda regularizada con más tiempo para pagar, o bien, es destruida de forma segura liberando los stands al mercado.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-12:** El sistema no libera reservas automáticamente; siempre dependen de la decisión humana en este caso de uso.
- **RN-11:** El único estado final de cierre es Cancelada.
