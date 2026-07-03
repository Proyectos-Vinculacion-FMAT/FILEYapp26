---
estado: propuesta
version: 0.2
tags:
  - tipo/caso-de-uso
  - dom/tal
fecha: 2026-06-25
id: CU-TAL-003
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-003 Consultar mis propuestas de actividad y revisar su estado actual

> [!note] Equivalente a CU-EVT-003 en la convocatoria de Hipólito
> Misma necesidad de seguimiento, y con los **mismos estados de dictamen** que `EVT`
> (corrección 2026-06-29: Elvira sí dictamina cada propuesta en el sistema — ver CU-TAL-009).

## Objetivo

El tallerista consulta todas sus propuestas de actividad infantil/juvenil registradas en la edición activa para conocer su estado de revisión y, una vez aceptadas, su programación.

## Alcance

Módulo de Talleres (TAL) — vista de seguimiento del tallerista. Muestra únicamente las propuestas asociadas a la cuenta con sesión activa en la convocatoria infantil/juvenil. No cubre la edición de propuestas (CU-TAL-004) ni el dictamen (CU-TAL-009).

## Actores

### Actor principal

- Tallerista

## Disparador

El tallerista desea conocer el estado actual de sus propuestas enviadas.

## Precondiciones

- El tallerista tiene al menos una propuesta enviada (CU-TAL-002).
- El tallerista está autenticado (CU-REG-002).

## Postcondiciones

### En éxito

El tallerista visualiza la lista de sus propuestas con su estado actual.

### En caso alternativo

No se realizan cambios en el sistema; la consulta es de solo lectura.

## Flujo principal

1. El tallerista accede a la sección "Mis propuestas" dentro del módulo de Talleres.
2. El sistema recupera todas las propuestas asociadas a la cuenta con sesión activa para la convocatoria infantil/juvenil activa o más reciente.
3. El sistema muestra una lista con: nombre del evento, tipo, folio de registro, fecha de envío y estado.
4. El sistema muestra, para cada propuesta y según su estado, la información adicional correspondiente (ver tabla de estados abajo).
5. El tallerista puede seleccionar una propuesta para ver su detalle completo (datos capturados en CU-TAL-002).

## Estados visibles para el tallerista

| Estado | Cuándo aparece | Descripción |
| --- | --- | --- |
| `pendiente` | Desde el envío (CU-TAL-002) o el reenvío (CU-TAL-004) hasta el dictamen de Elvira | La propuesta está en revisión. |
| `cambios_solicitados` | Elvira solicitó cambios (CU-TAL-009, A1) | Se muestra el mensaje de Elvira y acceso directo a CU-TAL-004. |
| `rechazada` | Elvira rechazó la propuesta (CU-TAL-009, A2) | Se muestra el motivo de rechazo registrado por Elvira. |
| `aceptada` | Elvira aceptó la propuesta (CU-TAL-009) | La propuesta se convirtió en Actividad; la sala y el horario se comunicarán en una notificación posterior (`PRG`). |
| `programada` | Cuando el panel de Elvira (`PRG`) asigna sala y horario, y ese horario queda **final** | El tallerista ve sus fechas y lugares asignados (precisión 2026-06-29: el catálogo solo se publica a `VIS` una vez que el horario es final, no mientras es preliminar). |

> [!note] Precisión (2026-06-29) — volumen real de selección
> Según [Junta 2 con organizadores FILEY](<../../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#administración-de-salas-y-talleres>): "en general se reciben alrededor de 300 propuestas de talleres y se aceptan alrededor de 250" — corrige una nota anterior que decía "~50 de ~300", cifra sin respaldo en la evidencia disponible.

## Flujos alternos

### FA-1: El tallerista no tiene propuestas enviadas

2a. El sistema muestra un mensaje indicando que no hay propuestas registradas y ofrece la opción de iniciar el registro (CU-TAL-002).

### FA-2: La convocatoria está cerrada

3a. El sistema muestra las propuestas con el estado que tenían al cierre, indicando que la convocatoria ya no está activa.

## Flujos de excepción

### FE-1: Error de conexión

2a. El sistema muestra un mensaje de error y permite reintentar.

## Datos relevantes

- **Folio de registro:** identificador único asignado al enviar (CU-TAL-002).
- **Estado `programada`:** incluye las fechas, turnos y sala asignados; lo actualiza el panel de Elvira en `PRG` (ver `PRG/CU-PRG Índice.md`), no el tallerista.
- Este CU no permite editar la propuesta (ver CU-TAL-004) ni dictaminarla (ver CU-TAL-009).
