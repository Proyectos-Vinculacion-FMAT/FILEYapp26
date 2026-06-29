---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-036
modulo: E. Administración
actor_principal: Administrador
requisitos_relacionados: []
dependencias: []
---
# CU-STD-036 Corregir o editar un espacio del mapa (p. ej. por ampliación)

## Descripción

El administrador ajusta las propiedades físicas y económicas de un stand en el mapa (como sus dimensiones, precio base o lo que incluye), comúnmente necesario cuando dos stands físicos se fusionan o se reacomodan muros divisorios a petición de un cliente, sin afectar el resto del diseño del evento.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada.
- El administrador está en la vista del mapa (A8).

## Disparador

El administrador identifica la necesidad de ajustar las propiedades de un stand y selecciona la acción "Editar stand".

## Flujo principal

1. En la vista del mapa (A8), el administrador selecciona un stand y oprime "Editar" (vista A9).
2. El sistema abre un formulario prellenado con los datos del `Stand` (clave, ancho, largo, qué incluye).
3. El administrador modifica las dimensiones (p. ej., aumenta el ancho porque se removió una división).
4. El sistema recalcula la superficie (m²) y el administrador decide si respeta el costo por m² global o asigna un precio manual exclusivo para este stand.
5. El administrador guarda los cambios.
6. El sistema actualiza la entidad `Stand`.
7. El sistema guarda la acción en la `Bitacora`.
8. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Editar un stand ya reservado
1. En el paso 1, el stand seleccionado ya está vinculado a una reserva (`Reservado` u `Ocupado`).
2. El sistema permite editar los datos físicos para que el mapa sea preciso, pero **no** altera retroactivamente el monto de la reserva existente (debido a que se congeló mediante `precio_snapshot` y `metros_cuadrados_snapshot` en la `ReservaStand`, RN-01).

## Postcondiciones

- **Éxito:** Las características del stand se actualizan para futuras reservas o precisión visual.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-01:** Las reservas ya creadas guardan una fotografía (snapshot) del precio y dimensiones; editar el stand base no modifica cobros ya realizados.
