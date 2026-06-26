---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-021
modulo: D. Confirmación y estados
actor_principal: Sistema
requisitos_relacionados: []
dependencias:
  - CU-STD-012
---
# CU-STD-021 Marcar los stands como reservados al crearse la reserva

## Descripción

El sistema bloquea automáticamente los espacios seleccionados por la editorial en el mapa, cambiándolos a estado `Reservado` en el mismo instante en que el usuario formaliza su carrito para crear la reserva, evitando sobreventas.

## Actores

- **Actor principal:** Sistema

## Precondiciones

- El usuario finalizó satisfactoriamente la creación de su reserva (CU-STD-012).

## Disparador

Creación exitosa de un registro en la entidad `Reserva` (con estado inicial `Por confirmar`).

## Flujo principal

1. El sistema detecta la creación de la nueva reserva.
2. El sistema identifica todas las líneas de detalle (`ReservaStand`) asociadas.
3. Por cada stand asociado, el sistema actualiza su estado en la entidad `Stand` de `Disponible` a `Reservado` (RN-10).
4. El sistema propaga la actualización al mapa general para que los espacios afectados se muestren de inmediato como "No disponibles" (RN-09) para el resto de los usuarios.
5. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

> [!note] Opcional
> Este es un proceso transaccional del sistema, si falla la base de datos se cancela la creación de la reserva por completo (rollback en CU-STD-012).

## Postcondiciones

- **Éxito:** Los stands quedan vinculados a la reserva y apartados del mercado general.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-09:** El usuario no ve los stands reservados; se le muestran como "no disponibles".
- **RN-10:** Estados de un stand: Disponible, Reservado, Ocupado.
