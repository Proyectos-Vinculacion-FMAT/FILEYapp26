---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/prg
fecha: 2026-06-24
id: CU-PRG-003
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
# CU-PRG-003 Editar la asignación (sala u horario) de una actividad ya programada

> [!note] Editar = mover (Junta 3)
> Editar no redimensiona ni crea bloques: es **mover** la actividad entre los bloques fijos
> de horario ya existentes, o entre salas. La duración y los bloques en sí no se modifican
> para acomodar una actividad puntual.

## Objetivo

Permitir al Administrador mover una actividad ya programada a otra sala o a otro(s) bloque(s) de horario, sin perder su condición de Aceptada.

## Alcance

Aplica a actividades `EVT`/`TAL` que ya tienen sala y bloque(s) de horario asignados. No incluye redimensionar bloques ni editar la actividad misma (datos del formulario).

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador elige mover una actividad ya programada a otra sala o bloque.

## Precondiciones

- La actividad está programada (tiene sala y bloque(s) asignados).

## Postcondiciones

### En éxito

- La actividad queda asignada a la nueva sala y/o bloque(s); los bloques que ocupaba antes quedan libres.

### En fallo

- La actividad conserva su asignación original.

## Flujo principal

1. El Administrador elige una actividad ya programada y selecciona la nueva sala y/o bloque(s) de horario.
2. El sistema valida que los bloques destino estén disponibles para esa sala, igual que en CU-PRG-002 [RN-XXX-001].
3. El sistema libera los bloques que la actividad ocupaba y la asigna a los nuevos.
4. El sistema confirma el movimiento al Administrador.

## Flujos de excepción

### E1. Choque de horario en el destino

1. El bloque o sala destino ya está ocupado por otra actividad.
2. El sistema marca la alerta de empalme (no bloquea el movimiento, ver CU-PRG-002 E1), pero el solapamiento debe resolverse antes de guardar el programa.

[RN-XXX-001]: #
