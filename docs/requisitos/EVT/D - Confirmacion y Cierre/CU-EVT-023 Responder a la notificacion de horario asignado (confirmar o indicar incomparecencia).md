---
estado: SE VA ES DE ISSAC
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVT-023
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-023 Responder a la notificación de horario asignado (confirmar o indicar incomparecencia)

## Objetivo

El proponente responde a la notificación de la sala y horario asignados a su actividad, confirmando su asistencia o indicando que no podrá presentarse, para que el administrador tenga certeza de la disponibilidad antes de cerrar el programa.

## Alcance

Módulo EVE — respuesta del proponente a su programación. Absorbe la solicitud de cambio de horario dentro de la ventana permitida (flujo alterno A2); la negociación concreta del cambio se realiza fuera del sistema (correo) y, de proceder, la ejecuta el administrador. No cubre la asignación de horario (módulo C) ni el cambio excepcional fuera de ventana (CU-EVT-025).

## Actores

### Actor principal

- Aplicante (proponente)

## Disparador

El proponente recibe la notificación de sala y horario asignados (CU-EVT-022) y entra a la app para responder.

## Precondiciones

- El proponente tiene sesión iniciada.
- Existe una `ProgramacionActividad` notificada para su actividad, con su `ConfirmacionProponente` registrada (fecha de notificación establecida).

## Postcondiciones

### En éxito

- Si **confirma**: se registra la `fecha_confirmacion` en `ConfirmacionProponente`; la `ProgramacionActividad` pasa a `confirmada_por_proponente` y la `Actividad` a `confirmada`.
- Si **indica incomparecencia**: la `Actividad` regresa a `sin_horario`, se libera la programación y el sistema avisa al administrador para que decida.

### En fallo

- No se registra la respuesta; el proponente puede reintentar.

## Flujo principal (Confirmar)

1. El proponente abre la notificación de horario asignado.
2. El sistema muestra los datos de la programación: actividad, sala (o stand), fecha y bloque de horario.
3. El proponente confirma su asistencia.
4. El sistema registra la `fecha_confirmacion` en `ConfirmacionProponente`.
5. El sistema cambia la `ProgramacionActividad` a `confirmada_por_proponente` y la `Actividad` a `confirmada`.
6. El sistema confirma al proponente que su asistencia quedó registrada.

## Flujos alternos

### A1. Indicar incomparecencia

1. En el paso 3, el proponente indica que no podrá presentarse.
2. El sistema registra la incomparecencia en `ConfirmacionProponente`.
3. El sistema regresa la `Actividad` a `sin_horario` y libera la programación asignada.
4. El sistema notifica al administrador la incomparecencia para que decida: si es definitiva, cancelar la actividad; si es por el horario, evaluar una reprogramación (módulo C). Esa decisión queda fuera de este caso de uso.

### A2. Solicitar cambio de horario (dentro de la ventana)

1. En el paso 3, el proponente solicita un cambio de horario y la fecha actual es anterior o igual a `fecha_cierre_ajustes_proponente`.
2. El sistema registra `solicito_cambio = true` y el `detalle_cambio` en `ConfirmacionProponente`.
3. El sistema informa al proponente que su solicitud quedó registrada y que la negociación del nuevo horario continuará por correo con el administrador.
4. El cambio efectivo, de proceder, lo ejecuta el administrador fuera de este flujo (módulo C, o CU-EVT-025 si ya está fuera de ventana).

## Flujos de excepción

### E1. Solicitud de cambio fuera de la ventana de ajustes

1. En el paso 1 de A2, la fecha actual es posterior a `fecha_cierre_ajustes_proponente`.
2. El sistema informa que la ventana para solicitar cambios ya cerró y que cualquier ajuste debe gestionarse directamente con el administrador por correo (CU-EVT-025).
3. El sistema no registra una solicitud de cambio.

### E2. Programación inexistente o ya cerrada

1. En el paso 2, el sistema detecta que la programación fue retirada o el programa ya está cerrado.
2. El sistema informa la situación y no permite registrar la respuesta.

## Datos relevantes

### Entradas

- Identificador de la programación notificada.
- Respuesta del proponente (confirmar / incomparecencia / solicitar cambio) y, en su caso, el `detalle_cambio`.

### Salidas

- `ConfirmacionProponente` actualizada (confirmación, incomparecencia o solicitud de cambio).
- Estado de `Actividad` y `ProgramacionActividad` actualizado según la respuesta.
