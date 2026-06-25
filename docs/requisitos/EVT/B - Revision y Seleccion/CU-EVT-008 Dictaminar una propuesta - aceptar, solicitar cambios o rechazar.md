---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVT-008
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-008 Dictaminar una propuesta: aceptar, solicitar cambios o rechazar

## Objetivo

El administrador resuelve una propuesta emitiendo uno de tres dictámenes —aceptar, solicitar cambios o rechazar— dejando registro de la decisión para que el proceso avance hacia la programación o la notificación de resultados.

## Alcance

Módulo EVE — dictamen de propuesta. Absorbe el rechazo con motivo (flujo alterno A2) y el cambio de dictamen ya emitido (flujo alterno A3). La notificación de aceptaciones y rechazos al proponente se realiza en lote (CU-EVT-012); la solicitud de cambios sí se notifica de inmediato. No cubre la asignación de sala y horario (módulo C).

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

Desde el detalle de una propuesta (CU-EVT-007), el administrador decide emitir su dictamen.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.
- La propuesta está en estado `pendiente` (o `cambios_solicitados`, si el proponente aún no responde y el administrador decide resolverla directamente).

## Postcondiciones

### En éxito

- La propuesta queda en estado `aceptada`, `cambios_solicitados` o `rechazada`, con su fecha de revisión y el administrador que la revisó (`revisado_por`).
- Si fue **aceptada**: el sistema asigna el prefijo de `categoria` (`literaria` / `academica`), crea una `Actividad` en estado `sin_horario` vinculada a la propuesta y la deja pendiente de notificación en lote (`resultado_notificado = false`).
- Si fue **cambios solicitados**: se registra el `mensaje_cambios_solicitados` y el sistema notifica de inmediato al proponente por correo.
- Si fue **rechazada**: se registra el `motivo_rechazo` y la propuesta queda pendiente de notificación en lote (`resultado_notificado = false`).

### En fallo

- La propuesta permanece sin cambios en su estado actual.

## Flujo principal (Aceptar)

1. En el detalle de la propuesta, el administrador elige "Aceptar".
2. El sistema presenta una segunda pantalla de confirmación que solicita clasificar la propuesta como `literaria` o `academica`, sugiriendo una opción a partir de la dependencia o institución del proponente.
3. El administrador confirma la clasificación y la aceptación.
4. El sistema compone el valor final de `categoria` combinando el prefijo elegido (`literaria` / `academica`) con el sufijo ya derivado en el envío (`_uady` / `_externo`).
5. El sistema cambia la propuesta a `aceptada`, registra la fecha de revisión y el revisor.
6. El sistema crea una `Actividad` en estado `sin_horario`, copiando nombre, organiza, tipo de actividad y edición desde la propuesta.
7. El sistema marca la propuesta como pendiente de notificación (`resultado_notificado = false`) para incluirla en el siguiente lote (CU-EVT-012).
8. El sistema confirma al administrador que la propuesta fue aceptada.

## Flujos alternos

### A1. Solicitar cambios

1. En el detalle de la propuesta, el administrador elige "Solicitar cambios".
2. El sistema solicita el `mensaje_cambios_solicitados` (campo de texto obligatorio) indicando qué debe corregir el proponente.
3. El administrador redacta el mensaje y confirma.
4. El sistema cambia la propuesta a `cambios_solicitados` y registra la fecha de revisión y el revisor.
5. El sistema notifica de inmediato al proponente por correo, para que pueda corregir y reenviar (CU-EVT-004) antes del cierre de la convocatoria.
6. El administrador puede solicitar cambios cuantas veces sea necesario sobre la misma propuesta; él determina cuándo la información es suficiente.

### A2. Rechazar

1. En el detalle de la propuesta, el administrador elige "Rechazar".
2. El sistema solicita el `motivo_rechazo` (campo de texto obligatorio).
3. El administrador redacta el motivo y confirma.
4. El sistema cambia la propuesta a `rechazada`, registra la fecha de revisión y el revisor.
5. El sistema marca la propuesta como pendiente de notificación (`resultado_notificado = false`) para incluirla en el siguiente lote.

### A3. Cambiar un dictamen ya emitido (re-dictamen)

1. El administrador abre una propuesta cuyo dictamen ya fue emitido (`aceptada` o `rechazada`) y elige cambiarlo.
2. El sistema verifica que el administrador tiene permiso para re-dictaminar; si no lo tiene, deniega la acción (ver E2).
3. El sistema solicita doble verificación de la acción.
4. Si el cambio pasa de `aceptada` a `rechazada`, el sistema exige obligatoriamente el `motivo_rechazo`.
5. El administrador confirma.
6. El sistema aplica el nuevo dictamen y, si la propuesta ya había sido notificada antes (`fecha_resultado_notificado` no nula), restablece `resultado_notificado = false` para que el cambio se comunique como **actualización** en el siguiente lote.
7. Si el cambio implica pasar de `aceptada` a otro estado, el sistema marca la `Actividad` asociada como `cancelada`.

## Flujos de excepción

### E1. Cupo de la categoría alcanzado al aceptar

1. En el paso 4 (Aceptar), el sistema detecta que la categoría ya alcanzó su cupo configurado.
2. El sistema advierte al administrador del cupo alcanzado, pero **no bloquea** la aceptación (permite mantener propuestas en reserva ante posibles bajas).
3. El administrador decide confirmar o cancelar la aceptación.

### E2. Sin permiso para re-dictaminar

1. En el paso 2 de A3, el sistema detecta que el administrador no tiene permiso para cambiar un dictamen ya emitido.
2. El sistema deniega la acción y muestra el dictamen vigente sin alterarlo.

### E3. Motivo o mensaje obligatorio faltante

1. Al solicitar cambios (A1) o rechazar (A2/A3), el administrador deja en blanco el campo de texto obligatorio.
2. El sistema impide registrar el dictamen y resalta el campo como obligatorio.
3. El administrador completa el texto y reintenta.

## Datos relevantes

### Entradas

- Identificador o folio de la propuesta.
- Decisión de dictamen (aceptar / solicitar cambios / rechazar).
- Clasificación `literaria` / `academica` (al aceptar).
- `mensaje_cambios_solicitados` (al solicitar cambios) o `motivo_rechazo` (al rechazar).

### Salidas

- Propuesta en estado `aceptada` (con `Actividad` creada en `sin_horario`), `cambios_solicitados` (con notificación inmediata) o `rechazada`.
- Fecha de revisión y revisor registrados.
