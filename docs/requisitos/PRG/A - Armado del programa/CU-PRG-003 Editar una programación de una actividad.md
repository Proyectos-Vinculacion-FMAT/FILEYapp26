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
# CU-PRG-003 Editar una programación de una actividad

> [!note] Editar = mover (Junta 3)
> Editar no redimensiona ni crea bloques: es **mover** una programación existente entre los
> bloques fijos de horario ya existentes, o entre salas. La duración y los bloques en sí no se
> modifican para acomodar una actividad puntual.

<!-- -->

> [!note] Guardado implícito y notificación a discreción
> Igual que en CU-PRG-002, mover una programación queda guardado de inmediato: no hay un paso
> aparte de "guardar el programa". Si esa actividad ya había sido notificada al Participante
> (CU-PRG-008), el botón de notificar se vuelve a habilitar para ella —la notificación es por
> actividad, no por cada programación suya— y el Participante deberá aceptar o rechazar de
> nuevo la programación editada (CU-PRG-009) una vez que el Administrador decida notificar.

## Objetivo

Permitir al Administrador mover una programación existente de una actividad a otra sala o a otro(s) bloque(s) de horario, sin perder su condición de Aceptada.

## Alcance

Aplica a actividades `EVT`/`TAL` que ya tienen al menos una programación (sala y bloque(s) asignados). Si la actividad tiene varias programaciones (CU-PRG-002 A1), esta edición mueve una de ellas a la vez. No incluye redimensionar bloques ni editar la actividad misma (datos del formulario).

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador elige mover una programación existente de una actividad a otra sala o bloque.

## Precondiciones

- La actividad tiene al menos una programación (sala y bloque(s) asignados).

## Postcondiciones

### En éxito

- La programación queda con la nueva sala y/o bloque(s); los bloques que ocupaba antes quedan libres. El cambio queda guardado de inmediato.

### En fallo

- La programación conserva su sala y bloque(s) originales.

## Flujo principal

1. El Administrador elige una programación existente de una actividad y selecciona la nueva sala y/o bloque(s) de horario.
2. El sistema valida que los bloques destino estén disponibles para esa sala, igual que en CU-PRG-002 [RN-XXX-001].
3. El sistema libera los bloques que esa programación ocupaba y la mueve a los nuevos, guardando el cambio de inmediato.
4. El sistema confirma el movimiento al Administrador y, si la actividad ya había sido notificada, vuelve a habilitar su botón de notificar (CU-PRG-008).

## Flujos de excepción

### E1. Choque de horario en el destino

1. El bloque o sala destino ya está ocupado por otra actividad.
2. El sistema marca la alerta de empalme (no bloquea el movimiento ni su guardado, ver CU-PRG-002 E1), pero el solapamiento debe resolverse antes de que el Administrador pueda notificar a los participantes afectados.

[RN-XXX-001]: #
