---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-19
id: CU-STD-006
dominio: STD
reglas_de_negocio:
  - RN-16
---
# CU-STD-006 Aceptar o rechazar una aplicación

## Objetivo

El administrador resuelve una aplicación pendiente, ya sea aceptándola (habilitando a la editorial para reservar stands y determinando elegibilidad a descuento) o rechazándola (invalidándola de forma definitiva, aunque permitiendo crear una nueva).

## Alcance

Componente de Stands — módulo de Aplicación. Aceptar habilita a la editorial para reservar. Rechazar invalida la aplicación de forma directa, sin pedir motivo.

## Actores

### Actor principal

- Administrador (coordinador del showfloor)

## Disparador

El administrador decide aceptar o rechazar la aplicación desde su detalle (CU-STD-005).

## Precondiciones

- El administrador tiene sesión iniciada con rol de administrador.
- La aplicación está en estado `pendiente`.

## Postcondiciones

### En éxito

- La aplicación pasa a estado `aceptada` o `rechazada`, con su fecha de revisión y el administrador que la revisó.
- Si es aceptada: la editorial queda habilitada para reservar stands (RN-16).
- Si es rechazada: la aplicación queda invalidada para su continuidad.
- Se solicita la notificación del resultado al usuario (CU-STD-008).

### En fallo

- La aplicación permanece sin cambios en su estado actual.

## Flujo principal (Aceptar)

1. En el detalle de la aplicación, el administrador elige "Aceptar".
2. El sistema solicita confirmación de la acción.
3. El administrador confirma.
4. El sistema cambia la aplicación a `aceptada` y registra la fecha de revisión y el revisor.
5. El sistema habilita a la editorial para reservar stands (RN-16).
6. El sistema dispara la notificación del resultado al usuario (CU-STD-008).
7. El sistema confirma al administrador que la aplicación fue aceptada.

## Flujos alternos



### A2. Rechazar aplicación

1. En el detalle de la aplicación, el administrador elige "Rechazar".
2. El sistema cambia la aplicación a `rechazada` y registra la fecha de revisión y el revisor (es una acción directa, sin requerir motivo).
3. El sistema dispara la notificación del resultado al usuario (CU-STD-008).
4. El sistema confirma al administrador que la aplicación fue rechazada.

## Flujos de excepción

### E1. La aplicación ya no está pendiente

1. Al intentar realizar la acción (aceptar o rechazar), el sistema detecta que la aplicación ya fue resuelta (p. ej. por otro administrador).
2. El sistema impide la acción y muestra su estado vigente.

## Datos relevantes

### Entradas

- Identificador de la aplicación.
- Decisión de resolución (aceptar o rechazar).
- Resolución de aceptación o rechazo.

### Salidas

- Aplicación en estado `aceptada` (con elegibilidad y habilitación) o `rechazada` (invalidada).
