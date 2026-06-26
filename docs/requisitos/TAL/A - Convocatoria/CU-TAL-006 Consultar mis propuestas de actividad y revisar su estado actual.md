---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - talleres
fecha: 2026-06-25
id: CU-TAL-006
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-006 Consultar mis propuestas de actividad y revisar su estado actual

> Borrador inicial (título y descripción). Inspirado en CU-EVT-005, pero **sin estados de
> dictamen** (en TAL no hay revisión propuesta-por-propuesta como con Hipólito).

## Objetivo

El tallerista consulta todas sus propuestas de actividad infantil/juvenil registradas en la edición activa para confirmar que quedaron correctamente registradas (folio y datos) y, en su momento, ver si su participación fue confirmada por la coordinación.

## Alcance

Módulo de Talleres (TAL) — vista de seguimiento del tallerista. Muestra únicamente las propuestas asociadas a la cuenta con sesión activa en la convocatoria infantil/juvenil. No incluye estados de dictamen (`aceptada` / `cambios_solicitados` / `rechazada`) porque ese proceso no existe en esta convocatoria; la confirmación de participación se notifica por correo. No cubre la edición de propuestas (CU-TAL-005).

## Actores

### Actor principal

- Tallerista

## Disparador

El tallerista desea conocer el estado actual de sus propuestas enviadas.

## Precondiciones

- El tallerista tiene al menos una propuesta enviada (CU-TAL-003).
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
4. El tallerista puede seleccionar una propuesta para ver su detalle completo (datos capturados en CU-TAL-002).
5. El caso de uso termina.

## Estados visibles para el tallerista

| Estado | Cuándo aparece | Descripción |
|--------|---------------|-------------|
| `registrada` | Desde el envío (CU-TAL-003) hasta que la coordinación asigne fechas | La propuesta fue recibida correctamente. La coordinación la tiene en revisión. |
| `programada` | Cuando la coordinación (Elvira) asigna sala y horario en el sistema | La propuesta fue seleccionada e incluida en el programa; el tallerista ve sus fechas y lugares asignados. |

> [!important] Sin dictamen explícito en el sistema
> En la convocatoria de Elvira no existe un estado `aceptada` / `rechazada` / `cambios_solicitados`
> visible para el tallerista, a diferencia de la convocatoria de Hipólito (EVT). La selección de
> propuestas (~50 de ~300 recibidas) la realiza Elvira de forma manual fuera del sistema. La
> transición a `programada` ocurre cuando la coordinación asigna fechas en la fase de programación
> (fuera del alcance de registro; ver CUs de programación TAL). Los talleristas **no seleccionados**
> no recibirán una notificación de rechazo a través del sistema; la coordinación puede comunicarlo
> por correo de forma directa.

## Flujos alternos

### FA-1: El tallerista no tiene propuestas enviadas

2a. El sistema muestra un mensaje indicando que no hay propuestas registradas y ofrece la opción de iniciar el registro (CU-TAL-002).

### FA-2: La convocatoria está cerrada

3a. El sistema muestra las propuestas con el estado que tenían al cierre, indicando que la convocatoria ya no está activa.

## Flujos de excepción

### FE-1: Error de conexión

2a. El sistema muestra un mensaje de error y permite reintentar.

## Datos relevantes

- **Folio de registro:** identificador único asignado al enviar (CU-TAL-003).
- **Estado `programada`:** incluye las fechas, turnos y sala/espacio asignados; lo actualiza la coordinación en la fase de programación, no el tallerista.
- Este CU no permite editar la propuesta (ver CU-TAL-005).
