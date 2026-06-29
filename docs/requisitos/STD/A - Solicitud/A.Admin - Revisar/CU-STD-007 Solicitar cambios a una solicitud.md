---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-19
id: CU-STD-007
dominio: STD
reglas_de_negocio: []
---
# CU-STD-007 Solicitar cambios a una solicitud

## Objetivo

El administrador devuelve una solicitud pendiente indicando los motivos o cambios requeridos, para que la editorial pueda corregirla y reenviarla sin iniciar desde cero.

## Alcance

Componente de Stands — módulo de Solicitud. La petición de cambios es obligatoria y habilita el reenvío de la misma solicitud por parte del aplicante (CU-STD-002).

## Actores

### Actor principal

- Administrador (coordinador del showfloor)

## Disparador

El administrador decide solicitar cambios a la solicitud desde su detalle (CU-STD-005).

## Precondiciones

- El administrador tiene sesión iniciada con rol de administrador.
- La solicitud está en estado `pendiente`.

## Postcondiciones

### En éxito

- La solicitud pasa a estado `cambios_solicitados`, con el motivo/petición, la fecha de revisión y el administrador que la revisó.
- Se solicita la notificación del resultado al aplicante (CU-STD-008).
- La editorial podrá editar y reenviar la solicitud (CU-STD-002).

### En fallo

- La solicitud permanece sin cambios en su estado actual.

## Flujo principal

1. En el detalle de la solicitud, el administrador elige "Solicitar cambios".
2. El sistema solicita el motivo o detalle de los cambios requeridos.
3. El administrador captura el motivo y confirma.
4. El sistema cambia la solicitud a `cambios_solicitados` y registra la petición de cambios, la fecha de revisión y el revisor.
5. El sistema dispara la notificación del resultado al aplicante (CU-STD-008).
6. El sistema confirma al administrador que los cambios fueron solicitados.

## Flujos alternos

> [!note] Opcional
> Sin flujos alternos relevantes.

## Flujos de excepción

### E1. Motivo de cambios vacío

1. En el paso 3 el administrador intenta confirmar sin capturar un motivo.
2. El sistema impide la acción y solicita el motivo.

### E2. La solicitud ya no está pendiente

1. En el paso 1 o 4 el sistema detecta que la solicitud ya fue resuelta (p. ej. por otro administrador).
2. El sistema impide solicitar cambios nuevamente y muestra su estado vigente.

## Datos relevantes

### Entradas

- Identificador de la solicitud.
- Motivo o detalle de los cambios solicitados (obligatorio).

### Salidas

- Solicitud en estado `cambios_solicitados` con su motivo registrado.
