---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-031
modulo: E. Administración
actor_principal: Administrador
requisitos_relacionados: []
dependencias:
  - CU-STD-032
---
# CU-STD-031 Consultar la lista de todas las reservas, filtrable

## Descripción

El administrador accede a un listado maestro que contiene todas las reservas del evento, con la capacidad de buscar, filtrar por estado, y detectar fácilmente aquellas reservas que tienen saldos pendientes, próximos vencimientos o notificaciones de vencimiento.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada y permisos para gestionar stands.

## Disparador

El administrador selecciona la opción de "Reservas" en el menú de navegación (vista A3).

## Flujo principal

1. El administrador ingresa a la sección de reservas.
2. El sistema recupera todas las reservas asociadas al evento vigente.
3. El sistema muestra una tabla o listado con columnas clave: Identificador de reserva, Editorial, Estado (`Por confirmar`, `Confirmada`, `Pagada`, `Cancelada`), Stands ocupados, Monto total y Saldo pendiente.
4. El sistema resalta visualmente las reservas vencidas (ver CU-STD-025) para priorizar su atención.
5. El administrador utiliza los controles de búsqueda (por nombre de editorial) o filtros (por estado) para localizar un registro en específico.
6. El administrador selecciona una reserva para ver su detalle (CU-STD-032).
7. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Lista vacía
1. En el paso 2, el sistema detecta que aún no hay reservas creadas para el evento.
2. El sistema muestra un mensaje indicando que no se encontraron reservas.

## Postcondiciones

- **Éxito:** El administrador localiza exitosamente la reserva objetivo.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-11:** Solo existen cuatro estados para las reservas.
- **RN-12:** Las reservas vencidas requieren la intervención manual del administrador y deben ser fácilmente detectables.
