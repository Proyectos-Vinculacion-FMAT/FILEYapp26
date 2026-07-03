---
estado: propuesta
version: 0.01
tags:
  - tipo/caso-de-uso
  - dom/vis
fecha: 2026-06-24
id: CU-VIS-012
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
# CU-VIS-012 Reservar uno o varios talleres del catálogo para armar el itinerario de la visita

## Objetivo

Permitir al Participante reservar uno o varios talleres del catálogo, simultáneos o consecutivos, para armar el itinerario de su visita escolar.

> [!success] Política resuelta (Junta 3 con organizadores FILEY) — selección libre por asiento
> Elvira confirmó que la selección es **libre por asiento**: la escuela decide cómo dividir sus grupos y a qué actividades entrar, con cuántos alumnos en cada una. **Ya no hay candados ni combinaciones de cupo prefijadas** (se descarta el esquema anterior de "una sala de cine **o** 3 talleres de 35"). Las únicas reglas vigentes son:
>
> - **Máximo 105 alumnos por visita escolar.**
> - **Un registro (propuesta) distinto por nivel educativo.**
>
> Esto **reconcilia** la antigua contradicción "un taller por escuela" (pendiente de la [Junta 2](<../../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#pendientes-por-definir>)) frente al documento de FILEY: ninguna de las dos reglas previas aplica ya. La validación por taller (no por el total del grupo) sigue vigente en [CU-VIS-011](<CU-VIS-011 Validar que el cupo restante del taller cubra la cantidad de visitantes.md>). Ver [RSM - Junta 3 con organizadores FILEY](<../../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>).

## Alcance

Indicar el límite del sistema o subsistema al que aplica este caso de uso.

## Actores

### Actor principal

- Participante

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
