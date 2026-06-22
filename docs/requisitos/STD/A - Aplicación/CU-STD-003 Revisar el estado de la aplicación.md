---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - stands
fecha: 2026-06-22
id: CU-STD-003
dominio: STD
reglas_de_negocio: []
---
# CU-STD-003 Revisar el estado de la aplicación

## Objetivo

El usuario consulta el estado de su aplicación cuando entra al módulo de Stands, siendo dirigido automáticamente al siguiente paso según corresponda (en revisión, editarla o continuar a reserva).

## Alcance

Componente de Stands — módulo de Aplicación. Sirve como un ruteador o pantalla de seguimiento tras iniciar sesión y tener una aplicación previa.

## Actores

### Actor principal

- Usuario (editorial / entidad expositora)

## Disparador

El usuario entra al módulo de Stands teniendo una aplicación existente.

## Precondiciones

- El usuario tiene sesión iniciada.
- Existe al menos una aplicación asociada a la editorial/cuenta.

## Postcondiciones

### En éxito

- El sistema rutea al usuario a la vista correspondiente o muestra el mensaje de espera, según el estado de la aplicación.

### En fallo

- No aplica, salvo errores de sistema.

## Flujo principal

1. El usuario intenta acceder al módulo de Stands.
2. El sistema detecta que la aplicación activa o más reciente está en estado `pendiente`.
3. El sistema muestra la pantalla con el mensaje: "Su solicitud está en proceso de revisión".
4. El caso de uso termina (el usuario no puede realizar otra acción de reserva aún).

## Flujos alternos

### A1. Aplicación aceptada

1. En el paso 2, el sistema detecta que la aplicación está en estado `aceptada`.
2. El sistema dirige al usuario directamente al siguiente paso (p. ej. visualizar el mapa del showfloor para iniciar su reserva, CU-STD-009).
3. El caso de uso termina.

### A2. Aplicación rechazada

1. En el paso 2, el sistema detecta que la aplicación está en estado `rechazada` (invalidación definitiva).
2. El sistema le notifica el estado y lo dirige a crear una nueva solicitud (CU-STD-001).
3. El caso de uso termina.

### A3. Aplicación con cambios solicitados

1. En el paso 2, el sistema detecta que la aplicación está en estado `cambios_solicitados`.
2. El sistema muestra la petición de cambios y lo dirige a editarla y reenviarla (CU-STD-002).
3. El caso de uso termina.

## Flujos de excepción

> [!note] Opcional
> Sin excepciones relevantes.

## Datos relevantes

### Entradas

- Estado actual de la aplicación del usuario.

### Salidas

- Redirección a otro caso de uso o pantalla de espera con mensaje en texto.
