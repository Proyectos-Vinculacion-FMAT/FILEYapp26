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

> [!note] Restricciones de la reserva (reglas de negocio)
> Son **propiedades/restricciones** de la reserva, no flujos:
> - **Equivalencia de cupo:** una escuela ocupa sus lugares con una sala de cine (hasta su cupo) **o** repartiéndose en varios talleres pequeños (p. ej. 3 × 35 = 105). La validación de cada asignación vive en [CU-VIS-011](<CU-VIS-011 Validar que el cupo restante del taller cubra la cantidad de visitantes.md>).
> - **Mismo día (preferente):** se recomienda que las actividades del itinerario sean el mismo día.

<!-- -->

> [!warning] Contradicción a reconciliar — "un taller por escuela"
> El documento de FILEY contempla **varios talleres** por escuela (3 × 35), lo que **contradice** el pendiente de "un taller / un solo tipo de actividad por escuela" de la [Junta 2](<../../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#pendientes-por-definir>). La fuente entregada por FILEY es la versión autoritativa; queda como pregunta abierta para el cliente la política definitiva (ver [Preguntas para la siguiente sesión](<../../../soporte/meetings/meeting notes/Preguntas para la siguiente sesion.md#visitas-escolares>)). Fuente: [Software para agendar escuelas](<../../../soporte/extraido/Software para agendar escuelas.md>).

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
