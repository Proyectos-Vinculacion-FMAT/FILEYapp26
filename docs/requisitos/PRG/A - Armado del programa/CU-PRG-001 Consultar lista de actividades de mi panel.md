---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/prg
fecha: 2026-06-24
id: CU-PRG-001
dominio: PRG
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
# CU-PRG-001 Consultar lista de actividades de mi panel

## Objetivo

Permitir al Administrador ver las actividades (propuestas ya **Aceptadas**) de su panel —eventos o talleres—, sin importar su estado de programación (*pendiente* o *programada*), filtrando por tipo, salón y sala, para saber qué falta por programar.

## Alcance

Aplica a las actividades `EVT`/`TAL` aceptadas de uno de los dos programas (eventos o talleres). No incluye propuestas todavía en revisión ni actividades de otros dominios (`STD`, `VIS`).

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador abre la lista de actividades de su panel.

## Precondiciones

- Existe al menos una propuesta Aceptada (Actividad) en el panel consultado.

## Postcondiciones

### En éxito

- Se muestra la lista de actividades del panel, indicando para cada una su estado de programación (*pendiente* / *programada*) y, si está programada, su sala y bloque(s) de horario.

### En fallo

- No hay actividades que cumplan el filtro aplicado; se informa al Administrador sin bloquear la consulta.

## Flujo principal

1. El Administrador entra al panel (eventos o talleres) y abre la lista de actividades.
2. El sistema muestra todas las actividades Aceptadas del panel, sin importar su estado de programación.
3. El Administrador filtra la lista por tipo (evento | taller), salón o sala según lo necesite.
4. El sistema actualiza la lista según el filtro aplicado.

## Flujos de excepción

### E1. Panel sin actividades

1. El panel no tiene actividades Aceptadas.
2. El sistema muestra la lista vacía con un mensaje indicándolo.
