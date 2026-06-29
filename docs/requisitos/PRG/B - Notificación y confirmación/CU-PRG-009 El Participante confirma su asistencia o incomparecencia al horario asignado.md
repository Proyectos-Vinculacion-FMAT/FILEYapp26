---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/prg
fecha: 2026-06-24
id: CU-PRG-009
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
# CU-PRG-009 El Participante confirma su asistencia o incomparecencia al horario asignado

> [!success] D3 resuelta — notificaciones por módulo
> Este caso de uso implica un método de visualización de las notificaciones de las
> actividades del Participante. La Junta 3 con organizadores FILEY descartó la bandeja
> transversal: las notificaciones se consultan **por módulo/panel** (PRG en este caso), no en
> un concentrado único entre dominios (ver
> [Junta 3 con Equipo de desarrollo](<../../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d3--modelo-de-notificaciones-reg--prg>)
> y [RSM - Junta 3 con organizadores FILEY](<../../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>)).

<!-- -->

> [!note] La reprogramación se negocia fuera del sistema
> Si el Participante rechaza, el sistema solo registra el rechazo y su motivo (texto libre); no
> hay un hilo de mensajes dentro del sistema para negociar una nueva fecha. Esa comunicación es
> **interna** entre el Administrador y el Participante (correo, teléfono, etc.), fuera del
> alcance del sistema. El resultado de esa negociación, si la hay, se refleja moviendo la
> programación (CU-PRG-003) y volviendo a notificar (CU-PRG-008).

## Objetivo

Permitir al Participante, para cada programación asignada de una actividad, aceptarla o rechazarla.

## Alcance

Aplica a actividades `EVT`/`TAL` con al menos una programación ya notificada (CU-PRG-008). La aceptación o el rechazo son **por programación**: si la actividad tiene varias programaciones (CU-PRG-002 A1), el Participante responde cada una por separado, nunca en bloque. Si el Administrador edita una programación ya respondida (CU-PRG-003) y vuelve a notificar, el Participante debe aceptarla o rechazarla de nuevo.

## Actores

### Actor principal

- Participante

## Disparador

El Participante recibe la notificación de su fecha, sala y horario asignados (CU-PRG-008) y accede a su método de visualización de notificaciones.

## Precondiciones

- Existe al menos una programación notificada al Participante, pendiente de su aceptación o rechazo.

## Postcondiciones

### En éxito

- Queda registrada la aceptación o el rechazo de esa programación, y se notifica al Administrador.

### En fallo

- La programación permanece sin respuesta.

## Flujo principal

1. El Participante consulta sus programaciones notificadas pendientes de responder.
2. El Participante elige una programación y la acepta.
3. El sistema registra la aceptación y notifica al Administrador.

## Flujos alternos

### A1. Rechazar la programación asignada

1. El Participante elige una programación y la rechaza.
2. El Participante puede indicar, en un campo de texto libre, el motivo del rechazo.
3. El sistema registra el rechazo con su motivo (si lo hubo) y notifica al Administrador, quien decide si reprograma esa actividad (ver nota de reprogramación fuera del sistema, arriba).

## Flujos de excepción

### E1. Ventana de confirmación vencida

1. El Participante intenta aceptar o rechazar fuera del plazo habilitado.
2. El sistema rechaza el cambio e informa al Participante que contacte al Administrador.
