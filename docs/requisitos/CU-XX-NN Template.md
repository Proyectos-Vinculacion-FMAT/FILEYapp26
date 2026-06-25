---
estado: propuesta
version: 0.02
tags:
  - tipo/plantilla
fecha: 2026-06-18
id: CU-XXX-NNN
dominio: STD | TAL | REG | EVT | PRG | SAL
responsable: Nombre
issue_relacionado: PSD-XX
pr_relacionado: "#XX"
reglas_de_negocio:
  - RN-XXX-001
  - RN-YYY-002
diagramas_relacionados:
  - BPMN-XXX-001
  - ../resources/cu-xxx-001.png
trazabilidad:
  ddr:
    - DDR-XX
---
# CU-XXX-NNN Nombre breve del caso de uso

## Objetivo

Describir el resultado de valor que obtiene el actor al ejecutar este caso de uso.

## Alcance

Indicar el límite del sistema o subsistema al que aplica este caso de uso.

## Actores

### Actor principal

- Usuario / Bot / Operador / Sistema externo

### Actores secundarios

> [!note] Opcional
> Usar solo si participan actores de apoyo además del principal. Eliminar esta sección si no aplica.

- Sistema de autenticación
- Servicio de notificaciones
- Módulo de auditoría
- Sistema externo integrado

## Disparador

Evento que inicia el caso de uso.

## Precondiciones

- Condición 1
- Condición 2

## Postcondiciones

### En éxito

- Resultado esperado si el flujo termina correctamente

### En fallo

- Estado resultante si el flujo no puede completarse

## Flujo principal

> [!note] Referencias a reglas de negocio
> La cita `[RN-XXX-NNN]` en un paso es opcional: úsala solo cuando el paso se apoye en una regla de negocio declarada en `reglas_de_negocio` (frontmatter). Elimínala si el paso no depende de ninguna.

1. El actor realiza la acción inicial.
2. El sistema valida la condición correspondiente [RN-XXX-NNN].
3. El sistema ejecuta la acción principal [RN-XXX-NNN].
4. El sistema confirma el resultado al actor.

## Flujos alternos

> [!note] Opcional
> Usar solo si existen variaciones válidas que se desvían del flujo principal. Eliminar esta sección si no aplica.

### A1. Nombre del flujo alterno

1. Condición que desvía del flujo principal.
2. El sistema responde de forma alternativa [RN-XXX-NNN].
3. El flujo termina o regresa al paso N del flujo principal.

### A2. Nombre del flujo alterno

1. ...
2. ...

## Flujos de excepción

> [!tip]
> Debe existir al menos una excepción (E1). Las excepciones adicionales (E2, E3, ...) son opcionales.

### E1. Nombre de la excepción

1. Ocurre una condición inválida o error.
2. El sistema detiene, rechaza o compensa la operación [RN-XXX-NNN].
3. Se informa el motivo al actor.

### E2. Nombre de la excepción

> [!note] Opcional

1. ...
2. ...

[RN-XXX-NNN]: #

## Datos relevantes

> [!note] Opcional
> Usar solo si conviene detallar entradas y salidas del caso de uso. Eliminar esta sección si no aplica.

### Entradas

- Solicitud de operación
- Parámetros de entrada requeridos
- Criterios de filtrado (opcional)

### Salidas

- Resultado de la operación
- Detalle de respuesta (opcional)
