---
estado: propuesta
version: 0.01
tags:
  - tipo/caso-de-uso
  - dom/vis
fecha: 2026-06-24
id: CU-VIS-011
dominio: VIS
responsable: Nombre
issue_relacionado: PSD-XX
pr_relacionado: "#XX"
reglas_de_negocio:
  - RN-XXX-001
diagramas_relacionados:
  - BPMN-XXX-001
trazabilidad:
  ddr:
    - DDR-XX
---
# CU-VIS-011 Validar que el cupo restante del taller cubra la cantidad de visitantes

## Objetivo

Asegurar que el sistema impida asignar a un taller más visitantes de los que permite su cupo restante, validando la **cantidad que se asigna a ese taller** (no el total de la visita), de modo que un grupo grande pueda repartirse entre varias actividades sin sobrepasar la capacidad de ninguna.

> [!note] Regla de negocio — restricción de la reserva (no un flujo)
> Es una **restricción/propiedad de la reserva**, no un comportamiento ni un flujo. El grupo de una escuela **puede dividirse libremente** entre varias actividades (selección libre por asiento, resuelta en la Junta 3 con organizadores FILEY — ver [CU-VIS-012](<CU-VIS-012 Reservar uno o varios talleres del catálogo para armar el itinerario de la visita.md>)): la validación es por la cantidad asignada a *cada* taller contra su cupo restante, **no** por el total del grupo contra un solo taller. Sin esta corrección, una validación "grupo completo contra un solo taller" bloquearía todo taller pequeño (p. ej. Ek Balam, cupo 35) para cualquier grupo mayor a ese cupo. El único tope agregado es el de la visita completa: **máximo 105 alumnos por visita escolar** (ver [RSM - Junta 3 con organizadores FILEY](<../../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>)). Fuente original del patrón de reparto: [Software para agendar escuelas](<../../../soporte/extraido/Software para agendar escuelas.md>) ("Cupo lleno / No disponible" al agotarse).

<!-- -->

> [!note] Precisión interna (2026-06-29) — no aplica con normalidad a los casos excepcionales de `EVT`
> Esta validación asume un **taller de `TAL`**, con aforo limitado por sala (CU-SAL-005). Los
> casos excepcionales de `EVT` que Hipólito marca como aptos para infantil/juvenil (ver
> CU-VIS-010) **no tienen límite de cupo**: para esos, el sistema no rechaza la reserva por
> cantidad de visitantes — la restricción de esta CU solo rige sobre actividades de `TAL`.

## Alcance

Indicar el límite del sistema o subsistema al que aplica este caso de uso.

## Actores

### Actor principal

- Sistema

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

1. El actor realiza la acción inicial.
2. El sistema valida la condición correspondiente.
3. El sistema ejecuta la acción principal.
4. El sistema confirma el resultado al actor.

## Flujos de excepción

### E1. Nombre de la excepción

1. Ocurre una condición inválida o error.
2. El sistema detiene, rechaza o compensa la operación.
3. Se informa el motivo al actor.
