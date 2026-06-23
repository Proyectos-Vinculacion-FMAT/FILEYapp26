---
estado: propuesta
version: 0.02
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-20
id: CU-EVE-008
dominio: EVT
responsable: Juan Manuel Hernandez Miranda
issue_relacionado: PSD-XX
pr_relacionado: "#XX"
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-EVE-008 Ver el detalle de una propuesta (datos del proponente, descripción y adjuntos)

## Objetivo

Describir el resultado de valor que obtiene el actor al ejecutar este caso de uso.

## Alcance

Indicar el límite del sistema o subsistema al que aplica este caso de uso.

## Actores

### Actor principal

- Administrador

### Actores secundarios

> [!note] Opcional
> Usar solo si participan actores de apoyo además del principal. Eliminar esta sección si no aplica.

## Disparador

Evento que inicia el caso de uso.

## Precondiciones

- Condición 1

## Postcondiciones

### En éxito

- Resultado esperado si el flujo termina correctamente

### En fallo

- Estado resultante si el flujo no puede completarse

## Flujo principal

> [!note] Referencias a reglas de negocio
> La cita `[RN-EVE-NNN]` en un paso es opcional: úsala solo cuando el paso se apoye en una regla de negocio declarada en `reglas_de_negocio` (frontmatter). Elimínala si el paso no depende de ninguna.

1. El actor realiza la acción inicial.
2. El sistema valida la condición correspondiente.
3. El sistema ejecuta la acción principal.
4. El sistema confirma el resultado al actor.

## Flujos alternos

> [!note] Opcional
> Usar solo si existen variaciones válidas que se desvían del flujo principal. Eliminar esta sección si no aplica.

### A1. Nombre del flujo alterno

1. Condición que desvía del flujo principal.
2. El sistema responde de forma alternativa.
3. El flujo termina o regresa al paso N del flujo principal.

## Flujos de excepción

> [!tip]
> Debe existir al menos una excepción (E1). Las excepciones adicionales (E2, E3, ...) son opcionales.

### E1. Nombre de la excepción

1. Ocurre una condición inválida o error.
2. El sistema detiene, rechaza o compensa la operación.
3. Se informa el motivo al actor.

## Datos relevantes

> [!note] Opcional
> Usar solo si conviene detallar entradas y salidas del caso de uso. Eliminar esta sección si no aplica.

### Entradas

- Solicitud de operación
- Parámetros de entrada requeridos

### Salidas

- Resultado de la operación
