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
# CU-STD-007 Solicitar cambios a una aplicación

## Objetivo

El administrador devuelve una aplicación pendiente indicando los motivos o cambios requeridos, para que la editorial pueda corregirla y reenviarla sin iniciar desde cero.

## Alcance

Componente de Stands — módulo de Aplicación. La petición de cambios es obligatoria y habilita el reenvío de la misma aplicación por parte del usuario (CU-STD-002).

## Actores

### Actor principal

- Administrador (coordinador del showfloor)

## Disparador

El administrador decide solicitar cambios a la aplicación desde su detalle (CU-STD-005).

## Precondiciones

- El administrador tiene sesión iniciada con rol de administrador.
- La aplicación está en estado `pendiente`.

## Postcondiciones

### En éxito

- La aplicación pasa a estado `cambios_solicitados`, con el motivo/petición, la fecha de revisión y el administrador que la revisó.
- Se solicita la notificación del resultado al usuario (CU-STD-008).
- La editorial podrá editar y reenviar la aplicación (CU-STD-002).

### En fallo

- La aplicación permanece sin cambios en su estado actual.

## Flujo principal

1. En el detalle de la aplicación, el administrador elige "Solicitar cambios".
2. El sistema solicita el motivo o detalle de los cambios requeridos.
3. El administrador captura el motivo y confirma.
4. El sistema cambia la aplicación a `cambios_solicitados` y registra la petición de cambios, la fecha de revisión y el revisor.
5. El sistema dispara la notificación del resultado al usuario (CU-STD-008).
6. El sistema confirma al administrador que los cambios fueron solicitados.

## Flujos alternos

> [!note] Opcional
> Sin flujos alternos relevantes.

## Flujos de excepción

### E1. Motivo de cambios vacío

1. En el paso 3 el administrador intenta confirmar sin capturar un motivo.
2. El sistema impide la acción y solicita el motivo.

### E2. La aplicación ya no está pendiente

1. En el paso 1 o 4 el sistema detecta que la aplicación ya fue resuelta (p. ej. por otro administrador).
2. El sistema impide solicitar cambios nuevamente y muestra su estado vigente.

## Datos relevantes

### Entradas

- Identificador de la aplicación.
- Motivo o detalle de los cambios solicitados (obligatorio).

### Salidas

- Aplicación en estado `cambios_solicitados` con su motivo registrado.
