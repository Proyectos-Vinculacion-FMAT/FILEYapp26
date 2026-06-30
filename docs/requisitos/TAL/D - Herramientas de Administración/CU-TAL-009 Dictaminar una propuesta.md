---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/tal
fecha: 2026-06-29
id: CU-TAL-009
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-009 Dictaminar una propuesta

> [!warning] Corrección directa del cliente (2026-06-29)
> La primera homologación de `TAL` asumía que Elvira seleccionaba talleristas de forma manual
> y fuera del sistema, sin dictamen. **El cliente corrigió esto directamente:** Elvira sí
> revisa y dictamina cada propuesta en el sistema —aceptar, solicitar cambios o rechazar—,
> el mismo ciclo que usa Hipólito en `EVT` (ver CU-EVT-009). La diferencia real con `EVT` es
> que la propuesta aceptada **no se clasifica** por categoría (no hay literaria/académica ni
> UADY/externa en `TAL`).

## Objetivo

Elvira resuelve una propuesta de taller emitiendo uno de tres dictámenes —aceptar, solicitar cambios o rechazar— dejando registro de la decisión para que el proceso avance hacia la programación o la notificación de resultados.

## Alcance

Módulo de Talleres (TAL) — dictamen de propuesta. No cubre la asignación de sala y horario, delegada por completo a `PRG` (ver `PRG/CU-PRG Índice.md`).

## Actores

### Actor principal

- Administrador (Elvira)

## Disparador

Desde el detalle de una propuesta (CU-TAL-008), Elvira decide emitir su dictamen.

## Precondiciones

- Elvira tiene sesión iniciada con permisos del módulo TAL.
- La propuesta está en estado `pendiente`.

## Postcondiciones

### En éxito

- La propuesta queda en estado `aceptada`, `cambios_solicitados` o `rechazada`, con su fecha de revisión.
- Si fue **aceptada**: el sistema crea una `Actividad` en estado `sin_horario` vinculada a la propuesta, lista para que el panel de Elvira en `PRG` la programe.
- Si fue **cambios solicitados**: se registra el mensaje de cambios solicitados y el sistema notifica de inmediato al tallerista por correo.
- Si fue **rechazada**: se registra el motivo de rechazo.

### En fallo

- La propuesta permanece sin cambios en su estado actual.

## Flujo principal (Aceptar)

1. En el detalle de la propuesta, Elvira elige "Aceptar".
2. El sistema cambia la propuesta a `aceptada` y registra la fecha de revisión.
3. El sistema crea una `Actividad` en estado `sin_horario`, copiando nombre del evento, tipo, organiza, modalidad y participantes que recibirán constancia desde la propuesta.
4. El sistema confirma a Elvira que la propuesta fue aceptada y queda lista para programación.

## Flujos alternos

### A1. Solicitar cambios

1. En el detalle de la propuesta, Elvira elige "Solicitar cambios".
2. El sistema solicita un mensaje de texto obligatorio indicando qué debe corregir el tallerista.
3. Elvira redacta el mensaje y confirma.
4. El sistema cambia la propuesta a `cambios_solicitados` y registra la fecha de revisión.
5. El sistema notifica de inmediato al tallerista por correo, para que pueda corregir y reenviar (CU-TAL-003) antes del cierre de la convocatoria.

### A2. Rechazar

1. En el detalle de la propuesta, Elvira elige "Rechazar".
2. El sistema solicita un motivo de rechazo (texto obligatorio).
3. Elvira redacta el motivo y confirma.
4. El sistema cambia la propuesta a `rechazada` y registra la fecha de revisión.
5. El sistema marca la propuesta como pendiente de notificación para el siguiente lote (CU-TAL-010).

## Flujos de excepción

### E1. Motivo o mensaje obligatorio faltante

1. Al solicitar cambios (A1) o rechazar (A2), Elvira deja en blanco el campo de texto obligatorio.
2. El sistema impide registrar el dictamen y resalta el campo como obligatorio.
3. Elvira completa el texto y reintenta.

## Datos relevantes

### Entradas

- Identificador o folio de la propuesta.
- Decisión de dictamen (aceptar / solicitar cambios / rechazar).
- Mensaje de cambios solicitados o motivo de rechazo, según aplique.

### Salidas

- Propuesta en estado `aceptada` (con `Actividad` creada en `sin_horario`), `cambios_solicitados` (con notificación inmediata) o `rechazada`.
- Fecha de revisión registrada.
