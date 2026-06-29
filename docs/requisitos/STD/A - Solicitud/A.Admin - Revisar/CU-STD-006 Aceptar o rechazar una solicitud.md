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
# CU-STD-006 Aceptar o rechazar una solicitud

## Objetivo

El administrador resuelve una solicitud pendiente, ya sea aceptándola (habilitando a la editorial para reservar stands y determinando elegibilidad a descuento) o rechazándola (invalidándola de forma definitiva, aunque permitiendo crear una nueva).

## Alcance

Componente de Stands — módulo de Solicitud. Aceptar habilita a la editorial para reservar. Rechazar invalida la solicitud de forma directa, sin pedir motivo.

## Actores

### Actor principal

- Administrador (coordinador del showfloor)

## Disparador

El administrador decide aceptar o rechazar la solicitud desde su detalle (CU-STD-005).

## Precondiciones

- El administrador tiene sesión iniciada con rol de administrador.
- La solicitud está en estado `pendiente`.

## Postcondiciones

### En éxito

- La solicitud pasa a estado `aceptada` o `rechazada`, con su fecha de revisión y el administrador que la revisó.
- Si es aceptada: la editorial queda habilitada para reservar stands (RN-16).
- Si es rechazada: la solicitud queda invalidada para su continuidad.
- Se solicita la notificación del resultado al aplicante (CU-STD-008).

### En fallo

- La solicitud permanece sin cambios en su estado actual.

## Flujo principal (Aceptar)

1. En el detalle de la solicitud, el administrador elige "Aceptar".
2. El sistema solicita confirmación de la acción.
3. El administrador confirma.
4. El sistema cambia la solicitud a `aceptada` y registra la fecha de revisión y el revisor.
5. El sistema habilita a la editorial para reservar stands (RN-16).
6. El sistema dispara la notificación del resultado al aplicante (CU-STD-008).
7. El sistema confirma al administrador que la solicitud fue aceptada.

## Flujos alternos



### A2. Rechazar solicitud

1. En el detalle de la solicitud, el administrador elige "Rechazar".
2. El sistema cambia la solicitud a `rechazada` y registra la fecha de revisión y el revisor (es una acción directa, sin requerir motivo).
3. El sistema dispara la notificación del resultado al aplicante (CU-STD-008).
4. El sistema confirma al administrador que la solicitud fue rechazada.

## Flujos de excepción

### E1. La solicitud ya no está pendiente

1. Al intentar realizar la acción (aceptar o rechazar), el sistema detecta que la solicitud ya fue resuelta (p. ej. por otro administrador).
2. El sistema impide la acción y muestra su estado vigente.

## Datos relevantes

### Entradas

- Identificador de la solicitud.
- Decisión de resolución (aceptar o rechazar).
- Resolución de aceptación o rechazo.

### Salidas

- Solicitud en estado `aceptada` (con elegibilidad y habilitación) o `rechazada` (invalidada).
