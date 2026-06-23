---
estado: propuesta
version: 0.1
tags:
  - modelo-de-datos
  - eventos
fecha: 2026-06-20
---
# Modelo de datos — Eventos generales (EVE)

> Modelo **conceptual**: identifica las entidades y los datos que el sistema debe
> almacenar para el dominio de Eventos Generales (programa de Hipólito), sin comprometer
> aún tipos de base de datos, índices ni claves físicas.
> Las relaciones se describen en la sección 3.

> [!note]
> Las entidades **Persona**, **RolPermiso**, **SesionOTP**, **EdicionFeria**, **BloqueHorario**,
> **ProgramaMaestro**, **Sala** y **ReservaSala** viven en los **Cores** y se referencian aquí.
> en el docuemtno cores para su definición completa.

---

## 1. Resumen de entidades

| Entidad                | Propósito                                                                       |
| ---------------------- | -------------------------------------------------------------------------------- |
| Proponente             | Perfil de la persona/institución que propone una actividad para el programa.    |
| TipoActividad          | Catálogo de los tipos formales de actividad (Conversatorio, Conferencia, etc.). |
| Propuesta              | Solicitud enviada por un proponente durante la convocatoria.                     |
| PropuestaAdjunto       | Archivos adjuntos de soporte de una propuesta (semblanza, imagen, etc.).         |
| Actividad              | Actividad aprobada, con datos validados por Hipólito.                           |
| ProgramacionActividad  | Asignación de sala, fecha y bloque de horario a una actividad.                  |
| SesionActividad        | Sesión individual cuando una actividad se repite en múltiples fechas.          |
| ConfirmacionProponente | Registro de que el proponente confirmó su horario asignado.                     |
| NotificacionLote       | Envío masivo de notificaciones (aceptación/rechazo en un solo lote).           |
| ParametrosConvocatoria | Fechas clave y configuración de la convocatoria por edición.                   |
| BitacoraEVE            | Registro de cambios excepcionales (cambios de horario fuera de ventana, etc.).   |

---

## 2. Detalle de entidades y atributos

### 2.1 Proponente

> Extiende la entidad `Persona` del Core Registros con los datos específicos del dominio EVE.

| Atributo          | Descripción                                                        |
| ----------------- | ------------------------------------------------------------------- |
| id                | Identificador único.                                               |
| persona_id        | FK → Persona (Core Registros).                                     |
| tipo_participante | `externo` / `uady` / `artístico` (categorías del programa). |
| institucion       | Nombre de la institución u organización que representa.           |
| cargo             | Cargo o rol dentro de su institución.                              |
| es_recurrente     | Booleano — si ya participó en ediciones anteriores.               |

### 2.2 TipoActividad

> Catálogo administrable. No puede quedar fijo en código porque nuevos tipos se agregan internamente (Cuentacuentos, Plática, Concierto, etc. además de los 8 del formulario público).

| Atributo                 | Descripción                                                                                       |
| ------------------------ | -------------------------------------------------------------------------------------------------- |
| id                       | Identificador único.                                                                              |
| nombre                   | Ej. "Conversatorio", "Presentación de libro", "Cuentacuentos".                                    |
| origen                   | `convocatoria_publica` / `interno` — si aparece en el formulario público o solo uso interno. |
| duracion_bloques_default | Número de bloques estándar que ocupa por defecto (1 o 2).                                        |
| requiere_adjunto         | Booleano — si el formulario exige un adjunto obligatorio.                                         |
| requiere_ejemplar_fisico | Booleano — aplica a Presentación de libro/revista (deben enviar ejemplar físico a FILEY).       |
| activo                   | Booleano.                                                                                          |

### 2.3 Propuesta

> La solicitud enviada durante la convocatoria. Es el equivalente de `Aplicacion` en STD.

| Atributo                 | Descripción                                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------------------ |
| id                       | Identificador único.                                                                                  |
| folio                    | Número de folio visible para el proponente.                                                           |
| edicion_id               | FK → EdicionFeria (Core Programas).                                                                   |
| proponente_id            | FK → Proponente.                                                                                      |
| tipo_actividad_id        | FK → TipoActividad.                                                                                   |
| nombre_actividad         | Título de la actividad propuesta.                                                                     |
| organiza                 | Nombre del/los organizador(es).                                                                        |
| descripcion              | Descripción o resumen de la actividad.                                                                |
| categoria                | `literaria_uady` / `literaria_externa` / `academica_uady` / `academica_externa`.               |
| fecha_registro           | Fecha de envío de la propuesta.                                                                       |
| estado                   | `pendiente` / `aceptada` / `rechazada` / `en_negociacion`.                                     |
| fecha_revision           | Fecha en que Hipólito tomó la decisión.                                                             |
| revisado_por             | FK → Persona (admin).                                                                                 |
| motivo_rechazo           | Texto (si fue rechazada).                                                                              |
| es_interno               | Booleano — si es una actividad interna sin convocatoria pública (ej. arte visual).                   |
| ejemplar_fisico_recibido | Booleano — Hipólito marca si ya recibió el ejemplar físico (para presentaciones de libro/revista). |

#### Sub-campos para Presentación de libro

Cuando `tipo_actividad` = Presentación de libro, se capturan campos adicionales:

| Atributo                  | Descripción                                                   |
| ------------------------- | -------------------------------------------------------------- |
| libro_titulo              | Título del libro.                                             |
| libro_autor               | Nombre(s) del autor o autores.                                 |
| libro_sinopsis            | Sinopsis del libro.                                            |
| libro_portada_url         | URL de la imagen de portada (adjunto).                         |
| autor_presente            | Booleano — si el autor participará presencialmente.          |
| autores_presentes_detalle | Texto libre si hay varios autores, indicando cuáles estarán. |

> [!note]
> Estos campos sostienen el estado `en_negociacion` (RFH-08): una propuesta de autor puede estar aceptada conceptualmente pero el autor aún no confirma su presencia.

### 2.4 PropuestaAdjunto

> Archivos de soporte de una propuesta (equivalente a `Documento` en STD pero específico de EVE).

| Atributo     | Descripción                                                        |
| ------------ | ------------------------------------------------------------------- |
| id           | Identificador único.                                               |
| propuesta_id | FK → Propuesta.                                                    |
| tipo         | `semblanza` / `imagen_libro` / `programa_interno` / `otro`. |
| archivo_url  | Ubicación del archivo almacenado.                                  |
| fecha_carga  | Fecha de carga.                                                     |

### 2.5 Actividad

> La actividad ya aprobada, con datos listos para calendarización. Se crea a partir de una `Propuesta` aceptada (o se registra directamente para actividades internas).

| Atributo              | Descripción                                                                          |
| --------------------- | ------------------------------------------------------------------------------------- |
| id                    | Identificador único.                                                                 |
| propuesta_id          | FK → Propuesta (nulo si es actividad interna sin propuesta pública).                |
| edicion_id            | FK → EdicionFeria.                                                                   |
| tipo_actividad_id     | FK → TipoActividad.                                                                  |
| nombre                | Nombre final (puede diferir del nombre propuesto tras negociación).                  |
| organiza              | Organizador final.                                                                    |
| es_apta_juvenil       | Booleano — Hipólito la marca si puede aparecer en catálogo escolar/juvenil.        |
| en_cartelera_informal | Booleano — si aparece solo en cartelera informativa (sin horario fijo comprometido). |
| estado                | `sin_horario` / `programada` / `confirmada` / `definitiva` / `cancelada`.   |

### 2.6 ProgramacionActividad

> La asignación concreta de sala + fecha + bloque a una actividad. Una actividad puede tener múltiples programaciones si se repite (vía `SesionActividad`).

| Atributo            | Descripción                                                                      |
| ------------------- | --------------------------------------------------------------------------------- |
| id                  | Identificador único.                                                             |
| actividad_id        | FK → Actividad.                                                                  |
| sala_id             | FK → Sala (Core Salas). Si el evento ocurre en un stand, ver `stand_id`.       |
| stand_id            | FK → Stand del dominio STD (nulo si ocurre en sala del catálogo). Cubre RFH-33. |
| bloque_id           | FK → BloqueHorario (Core Programas).                                             |
| num_sesion          | Número de sesión (1, 2, 3…) para actividades con múltiples sesiones.          |
| bloques_extra       | Número de bloques adicionales si la actividad dura más de un bloque estándar.  |
| programa_maestro_id | FK → ProgramaMaestro (a qué versión del programa pertenece).                   |
| estado              | `tentativa` / `notificada` / `confirmada_por_proponente` / `cerrada`.     |

### 2.7 SesionActividad

> Permite que una actividad se repita en varias fechas/horarios sin duplicar su registro.

| Atributo          | Descripción                                                                                                        |
| ----------------- | ------------------------------------------------------------------------------------------------------------------- |
| id                | Identificador único.                                                                                               |
| actividad_id      | FK → Actividad.                                                                                                    |
| programacion_id   | FK → ProgramacionActividad.                                                                                        |
| num_sesion        | Número de esta sesión.                                                                                            |
| motivo_repeticion | Texto libre — razón por la que se repite (tallerista con disponibilidad amplia, necesidad de llenar hueco, etc.). |

### 2.8 ConfirmacionProponente

> Registro de que el proponente recibió y confirmó su horario asignado. Funciona como acuse de recibido.

| Atributo           | Descripción                                                     |
| ------------------ | ---------------------------------------------------------------- |
| id                 | Identificador único.                                            |
| programacion_id    | FK → ProgramacionActividad.                                     |
| proponente_id      | FK → Proponente.                                                |
| fecha_notificacion | Fecha en que se envió la notificación de horario.              |
| fecha_confirmacion | Fecha en que el proponente confirmó (nulo si aún no confirma). |
| solicito_cambio    | Booleano — si dentro de la ventana solicitó un cambio.         |
| detalle_cambio     | Texto libre (si solicitó cambio, qué pidió).                  |

### 2.9 NotificacionLote

> Hipólito no notifica propuesta por propuesta; lo hace en un solo lote cuando termina su revisión.

| Atributo       | Descripción                                                                     |
| -------------- | -------------------------------------------------------------------------------- |
| id             | Identificador único.                                                            |
| edicion_id     | FK → EdicionFeria.                                                              |
| tipo           | `seleccion` (aceptadas/rechazadas) / `horario` (asignación de sala y hora). |
| fecha_envio    | Fecha del envío masivo.                                                         |
| enviado_por    | FK → Persona (admin).                                                           |
| total_enviadas | Número de notificaciones del lote.                                              |
| estado         | `enviada` / `fallida_parcial`.                                               |

### 2.10 ParametrosConvocatoria

> Fechas clave configurables por edición. Cambian cada año — no pueden quedar fijas en código.

| Atributo                        | Descripción                                                               |
| ------------------------------- | -------------------------------------------------------------------------- |
| edicion_id                      | FK → EdicionFeria (clave primaria compuesta).                             |
| fecha_apertura_convocatoria     | Fecha de lanzamiento de la convocatoria pública.                          |
| fecha_cierre_convocatoria       | Fecha y hora de cierre de recepción de propuestas.                        |
| fecha_notificacion_seleccion    | Fecha en que se enviará el lote de selección.                            |
| fecha_cierre_ajustes_proponente | Fecha límite para que el proponente solicite cambios de horario.          |
| fecha_asignacion_horario        | Fecha a partir de la cual los proponentes verán su sala y hora asignadas. |
| fecha_constancias               | Fecha a partir de la cual los proponentes pueden descargar su constancia.  |
| cupo_literario_uady             | Número máximo de actividades Literarias-UADY.                            |
| cupo_literario_externo          | Número máximo de actividades Literarias-Externas.                        |
| cupo_academico_uady             | Número máximo de actividades Académicas-UADY.                           |
| cupo_academico_externo          | Número máximo de actividades Académicas-Externas.                       |

### 2.11 BitacoraEVE

> Registro de auditoría de cambios excepcionales (cambios de horario fuera de la ventana normal, cambios manuales del admin, etc.).

| Atributo     | Descripción                                                                       |
| ------------ | ---------------------------------------------------------------------------------- |
| id           | Identificador único.                                                              |
| persona_id   | FK → Persona (quién ejecutó la acción).                                        |
| accion       | Descripción de la acción (ej. "cambio_horario_excepcional", "anexo_taller_tal"). |
| entidad_tipo | Entidad afectada (`Actividad`, `ProgramacionActividad`, etc.).                 |
| entidad_id   | ID de la entidad afectada.                                                         |
| detalle      | Descripción del cambio (de → a).                                                 |
| motivo       | Razón registrada por el admin.                                                    |
| fecha        | Marca de tiempo.                                                                   |

---

## 3. Relaciones principales

- **Persona** (Core) 1—1 **Proponente** (EVE).
- **Proponente** 1—N **Propuesta** (una persona puede enviar varias propuestas en la misma edición).
- **EdicionFeria** (Core) 1—N **Propuesta**; 1—N **Actividad**; 1—1 **ParametrosConvocatoria**.
- **Propuesta** 0/1—1 **Actividad** (solo si fue aceptada; o la actividad se crea directamente si es interna).
- **Propuesta** 1—N **PropuestaAdjunto**.
- **Actividad** 1—N **ProgramacionActividad**.
- **ProgramacionActividad** 1—N **SesionActividad** (para actividades multi-sesión).
- **ProgramacionActividad** 1—1 **ConfirmacionProponente** (por cada programación que se notifica).
- **ProgramacionActividad** N—1 **Sala** (Core Salas) o N—1 **Stand** (STD, para RFH-33).
- **ProgramacionActividad** N—1 **BloqueHorario** (Core Programas).
- **ProgramaMaestro** (Core) 1—N **ProgramacionActividad**.

---

## 4. Mapa entidad → caso de uso (trazabilidad)

| Entidad                                 | Casos de uso relacionados                                  |
| --------------------------------------- | ---------------------------------------------------------- |
| Proponente                              | CU-EVE-002, CU-EVE-003                                     |
| TipoActividad                           | CU-EVE-031                                                 |
| Propuesta / PropuestaAdjunto            | CU-EVE-002 a CU-EVE-009, CU-EVE-013                        |
| Actividad                               | CU-EVE-008, CU-EVE-010, CU-EVE-011, CU-EVE-025, CU-EVE-026 |
| ProgramacionActividad / SesionActividad | CU-EVE-014 a CU-EVE-018, CU-EVE-025                        |
| ConfirmacionProponente                  | CU-EVE-019, CU-EVE-020, CU-EVE-021                         |
| NotificacionLote                        | CU-EVE-012, CU-EVE-019                                     |
| ParametrosConvocatoria                  | CU-EVE-001, CU-EVE-005, CU-EVE-023                         |
| BitacoraEVE                             | CU-EVE-022, CU-EVE-032                                     |

---

## 5. Temas abiertos del modelo

- Confirmar si `Propuesta` guarda snapshot de los datos del proponente o solo referencia a `Proponente`.
- Confirmar si el campo `categoria` (literaria/académica × uady/externa) vive en la Propuesta o en TipoActividad.
- Definir si la ventana de ajustes del proponente (RFH-18) aplica a **todos** los tipos de actividad o solo a algunos.
- Confirmar si `ParametrosConvocatoria.cupo_X` son por tipo de actividad o por categoría cruzada.
- Pendiente: qué datos mínimos se capturan de los eventos artísticos que Hipólito registra internamente (sin convocatoria pública).
