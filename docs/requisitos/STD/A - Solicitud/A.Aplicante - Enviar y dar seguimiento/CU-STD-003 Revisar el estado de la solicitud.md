---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-003
dominio: STD
reglas_de_negocio: []
---
# CU-STD-003 Revisar el estado de la solicitud

## Objetivo

El aplicante consulta el estado de su solicitud cuando entra al módulo de Stands, siendo dirigido automáticamente al siguiente paso según corresponda (en revisión, editarla o continuar a reserva).

## Alcance

Componente de Stands — módulo de Solicitud. Sirve como un ruteador o pantalla de seguimiento tras iniciar sesión y tener una solicitud previa.

## Actores

### Actor principal

- Aplicante (editorial / entidad expositora)

## Disparador

El aplicante entra al módulo de Stands teniendo una solicitud existente.

## Precondiciones

- El aplicante tiene sesión iniciada.
- Existe al menos una solicitud asociada a la editorial/cuenta.

## Postcondiciones

### En éxito

- El sistema rutea al aplicante a la vista correspondiente o muestra el mensaje de espera, según el estado de la solicitud.

### En fallo

- No aplica, salvo errores de sistema.

## Flujo principal

1. El aplicante intenta acceder al módulo de Stands.
2. El sistema detecta que la solicitud activa o más reciente está en estado `pendiente`.
3. El sistema muestra la pantalla con el mensaje: "Su solicitud está en proceso de revisión".
4. El caso de uso termina (el aplicante no puede realizar otra acción de reserva aún).

## Flujos alternos

### A1. Solicitud aceptada

1. En el paso 2, el sistema detecta que la solicitud está en estado `aceptada`.
2. El sistema dirige al aplicante directamente al siguiente paso (p. ej. visualizar el mapa del showfloor para iniciar su reserva, CU-STD-009).
3. El caso de uso termina.

### A2. Solicitud rechazada

1. En el paso 2, el sistema detecta que la solicitud está en estado `rechazada` (invalidación definitiva).
2. El sistema le notifica el estado y lo dirige a crear una nueva solicitud (CU-STD-001).
3. El caso de uso termina.

### A3. Solicitud con cambios solicitados

1. En el paso 2, el sistema detecta que la solicitud está en estado `cambios_solicitados`.
2. El sistema muestra la petición de cambios y lo dirige a editarla y reenviarla (CU-STD-002).
3. El caso de uso termina.

## Flujos de excepción

> [!note] Opcional
> Sin excepciones relevantes.

## Datos relevantes

### Entradas

- Estado actual de la solicitud del aplicante.

### Salidas

- Redirección a otro caso de uso o pantalla de espera con mensaje en texto.
