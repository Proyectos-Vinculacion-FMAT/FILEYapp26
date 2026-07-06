---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-029
modulo: E. Administración
actor_principal: Administrador
requisitos_relacionados: []
dependencias:
  - CU-STD-018
  - CU-STD-019
  - CU-STD-020
  - CU-STD-035
  - CU-STD-036
---
# CU-STD-029 Ver el detalle de una reserva (abonos, contacto y acciones asociadas)

## Descripción

El administrador visualiza el expediente completo de una reserva en particular. Esta vista funge como el contenedor principal desde el cual el administrador puede consultar el historial y ejecutar todas las acciones operativas relacionadas con los pagos, fechas y el estado general de la reserva.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada.
- El administrador ha seleccionado una reserva desde la lista (CU-STD-028) o desde el mapa (CU-STD-032).

## Disparador

Selección de una reserva para ver su detalle (vista A4).

## Flujo principal

1. El sistema muestra la ficha de la reserva solicitada.
2. El sistema despliega la información de la entidad `Reserva` y `Editorial` (expositor), incluyendo datos de contacto.
3. El sistema muestra los stands reservados (`ReservaStand`) con sus dimensiones y costos (snapshot original).
4. El sistema presenta el desglose financiero: monto total, descuentos aplicados (`DescuentoAplicado`), anticipo requerido, monto abonado y monto pendiente, así como las fechas clave límite y de corte.
5. El sistema lista el historial de pagos y movimientos (`Movimiento`), indicando cuáles están validados y cuáles pendientes de revisión.
6. A partir de esta vista, el administrador puede realizar distintas acciones sobre la reserva, como validar pagos (CU-STD-018), agregar abonos manuales (CU-STD-019), aplicar descuentos especiales (CU-STD-020), modificar fechas (CU-STD-036) o resolver vencimientos (CU-STD-035).
7. El administrador finaliza sus tareas y cierra el detalle o regresa al listado.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Reserva inexistente
1. El enlace o ID de la reserva buscada es inválido o la reserva fue eliminada de la base de datos (poco probable dado que solo se marcan como canceladas).
2. El sistema muestra un mensaje de error y redirige a la lista general de reservas (CU-STD-028).

## Postcondiciones

- **Éxito:** El administrador se informa sobre el estado integral de la reserva y tiene a su alcance las herramientas de gestión.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- Ninguna adicional a las reglas operativas de los casos de uso que invoca.
