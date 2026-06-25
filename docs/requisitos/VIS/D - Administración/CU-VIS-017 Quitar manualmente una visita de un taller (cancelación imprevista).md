---
estado: propuesta
version: 0.01
tags:
  - tipo/caso-de-uso
  - dom/vis
fecha: 2026-06-25
id: CU-VIS-017
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
# CU-VIS-017 Quitar manualmente una visita de un taller (cancelación imprevista)

## Objetivo

Permitir al Administrador quitar manualmente a una visita escolar de un taller ya reservado en casos de cancelación imprevista, liberando el cupo que ocupaba para que vuelva a estar disponible.

> [!note] Distinto de la autocorrección del Participante
> Esta es la **baja administrativa** posterior, a cargo de la coordinación, para casos de **cancelación imprevista** (la escuela avisa que no asistirá, un cambio de última hora, etc.). No debe confundirse con [CU-VIS-014](<../C - Catálogo y reserva de talleres/CU-VIS-014 Quitar un taller reservado del itinerario (liberar el cupo).md>), que es la autocorrección del propio Participante mientras arma su itinerario, antes de generarlo de forma final. Origen: [Junta 2 — Pendientes por definir](<../../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#pendientes-por-definir>).

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

1. El actor realiza la acción inicial.
2. El sistema valida la condición correspondiente.
3. El sistema ejecuta la acción principal.
4. El sistema confirma el resultado al actor.

## Flujos de excepción

### E1. Nombre de la excepción

1. Ocurre una condición inválida o error.
2. El sistema detiene, rechaza o compensa la operación.
3. Se informa el motivo al actor.
