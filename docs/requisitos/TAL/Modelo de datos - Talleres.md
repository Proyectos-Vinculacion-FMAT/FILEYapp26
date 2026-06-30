---
estado: propuesta
version: 0.1
tags:
  - tipo/modelo-de-datos
  - dom/tal
fecha: 2026-06-29
---
# Modelo de datos — Talleres (actividades infantiles y juveniles)

> Modelo **conceptual**: identifica las entidades y los datos que el sistema debe
> almacenar para el dominio de Talleres (convocatoria de Elvira), sin comprometer aún tipos
> de base de datos, índices ni claves físicas. Las relaciones se describen en la sección 3.

<!-- -->

> [!warning] Sustituye al modelo anterior, que en realidad era de Visitas escolares
> El archivo anterior (`Modelo de datos - Talleres (Visitas Escolares).md`, eliminado
> 2026-06-29) cubría únicamente entidades de **visitas escolares**, hoy dominio `VIS` (ver
> `VIS/Modelo de datos - Visitas escolares.md`). Este documento cubre el alcance que de verdad
> sigue siendo de `TAL`: el registro, revisión y selección de **propuestas de taller**.

<!-- -->

> [!note] Espejo de `EVT`, con dictamen confirmado (2026-06-29)
> Una versión anterior de este dominio asumía que Elvira seleccionaba manualmente y fuera del
> sistema, sin dictamen. **Corregido directamente por el cliente:** Elvira sí dictamina cada
> propuesta (aceptar / solicitar cambios / rechazar), igual que Hipólito en `EVT`. Por eso este
> modelo espeja de cerca `EVT/Modelo de datos - Eventos.md`, con las diferencias reales: sin
> categorización cruzada (literaria/académica × UADY/externa), sin adjuntos de archivo, y con
> constancia **obligatoria** para todo tallerista (no opcional como en `EVT`).

---

## 1. Resumen de entidades

| Entidad                   | Propósito                                                                               |
| ------------------------- | --------------------------------------------------------------------------------------- |
| Tallerista                | Perfil de la persona/institución que propone una actividad infantil/juvenil.            |
| TipoActividadTAL          | Catálogo de los tipos de actividad (Taller, Cuentacuentos, Plática para jóvenes, etc.). |
| PropuestaTaller           | Solicitud enviada por un tallerista durante la convocatoria.                            |
| Actividad                 | Propuesta de taller aceptada por Elvira, lista para programación en `PRG`.              |
| ParametrosConvocatoriaTAL | Fechas clave y modalidades admitidas de la convocatoria, por edición.                   |
| NotificacionLoteTAL       | Envío masivo de notificaciones de resultado (aceptadas/rechazadas en un solo lote).     |

---

## 2. Detalle de entidades y atributos

### 2.1 Tallerista

> Extiende la entidad `Persona` del Core Registros con los datos específicos de `TAL`.

| Atributo        | Descripción                                                     |
| --------------- | --------------------------------------------------------------- |
| id              | Identificador único.                                            |
| persona_id      | FK → Persona (Core Registros).                                  |
| numero_contacto | Teléfono de contacto (puede diferir del registrado en Persona). |

### 2.2 TipoActividadTAL

> Catálogo cerrado (a diferencia del de `EVT`, que es extensible con tipos internos): Taller,
> Cuentacuentos, Plática para jóvenes, Presentación de libros para niños/jóvenes, Obra/
> Presentación teatral, Proyección en cines.

| Atributo | Descripción                    |
| -------- | ------------------------------ |
| id       | Identificador único.           |
| nombre   | Ej. "Taller", "Cuentacuentos". |
| activo   | Booleano.                      |

### 2.3 PropuestaTaller

> La solicitud enviada durante la convocatoria. Equivalente a `Propuesta` en `EVT`, sin
> categorización cruzada ni adjuntos.

| Atributo                    | Descripción                                                                                                                        |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| id                          | Identificador único.                                                                                                               |
| folio                       | Número de folio visible para el tallerista.                                                                                        |
| edicion_id                  | FK → EdicionFeria (Core Programas).                                                                                                |
| tallerista_id               | FK → Tallerista.                                                                                                                   |
| tipo_actividad_id           | FK → TipoActividadTAL.                                                                                                             |
| nombre_evento               | Nombre oficial del evento/taller.                                                                                                  |
| organiza                    | Quién organiza.                                                                                                                    |
| participantes_constancia    | Texto — nombre completo de quienes recibirán constancia. **Obligatorio** (a diferencia de `EVT`, donde la constancia es opcional). |
| procedencia                 | `local` / `nacional` / `internacional`.                                                                                            |
| tema                        | Texto.                                                                                                                             |
| resena                      | Reseña breve.                                                                                                                      |
| modalidad                   | `presencial` / `virtual`.                                                                                                          |
| enlace_videoconferencia     | Obligatorio solo si `modalidad = virtual`.                                                                                         |
| autores                     | Texto libre, opcional.                                                                                                             |
| presentador                 | Nombre de quien presenta/participa.                                                                                                |
| editorial                   | Texto, opcional.                                                                                                                   |
| publico_meta                | Multivalor: `preescolar` / `primaria_baja` / `primaria_alta` / `secundaria` / `preparatoria` (mínimo uno).                         |
| sugerencia_dia_turno        | `matutino` / `vespertino`, opcional.                                                                                               |
| observaciones               | Texto libre, opcional.                                                                                                             |
| fecha_registro              | Fecha de envío.                                                                                                                    |
| estado                      | `pendiente` / `cambios_solicitados` / `aceptada` / `rechazada`.                                                                    |
| fecha_revision              | Fecha en que Elvira dictaminó.                                                                                                     |
| revisado_por                | FK → Persona (Elvira o su equipo).                                                                                                 |
| motivo_rechazo              | Texto (si fue rechazada).                                                                                                          |
| mensaje_cambios_solicitados | Texto — obligatorio cuando `estado = cambios_solicitados`.                                                                         |
| resultado_notificado        | Booleano — si el resultado vigente ya fue comunicado en un lote (CU-TAL-010).                                                      |
| fecha_resultado_notificado  | Fecha del último envío de resultado al tallerista.                                                                                 |

### 2.4 Actividad

> La propuesta ya aceptada, lista para que el panel de Elvira en `PRG` le asigne sala y
> horario. Equivalente a `Actividad` en `EVT` y a la entidad genérica del mismo nombre en
> `PRG/Modelo de datos - Programación.md`.

| Atributo          | Descripción                                                                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| id                | Identificador único.                                                                                                         |
| propuesta_id      | FK → PropuestaTaller.                                                                                                        |
| edicion_id        | FK → EdicionFeria.                                                                                                           |
| tipo_actividad_id | FK → TipoActividadTAL.                                                                                                       |
| nombre            | Nombre final del taller.                                                                                                     |
| organiza          | Organizador final.                                                                                                           |
| estado            | `sin_horario` / `programada` / `cancelada` (los estados de horario en sí —preliminar/final— viven en `Programación`, `PRG`). |

### 2.5 ParametrosConvocatoriaTAL

> Fechas y modalidades configurables por edición. **Ya no incluye "espacios disponibles"**
> (precisión 2026-06-29): los espacios son responsabilidad exclusiva del catálogo único global
> de `SAL` (ver `SAL/CU-SAL Índice.md`); este CU dejó de duplicarlo.

| Atributo                    | Descripción                                        |
| --------------------------- | -------------------------------------------------- |
| edicion_id                  | FK → EdicionFeria (clave primaria compuesta).      |
| fecha_apertura_convocatoria | Fecha de apertura de la convocatoria.              |
| fecha_cierre_convocatoria   | Fecha y hora de cierre de recepción de propuestas. |
| modalidades_admitidas       | Multivalor: `presencial` / `virtual` (mínimo una). |

### 2.6 NotificacionLoteTAL

> Equivalente a `NotificacionLote` en `EVT`. Marcado como **tentativo** (CU-TAL-010): no hay
> evidencia directa de que Elvira notifique en lote en vez de caso por caso; se extrapola por
> simetría con `EVT`.

| Atributo       | Descripción                        |
| -------------- | ---------------------------------- |
| id             | Identificador único.               |
| edicion_id     | FK → EdicionFeria.                 |
| fecha_envio    | Fecha del envío masivo.            |
| enviado_por    | FK → Persona (Elvira o su equipo). |
| total_enviadas | Número de notificaciones del lote. |
| estado         | `enviada` / `fallida_parcial`.     |

---

## 3. Relaciones principales

- **Persona** (Core) 1—1 **Tallerista**.
- **Tallerista** 1—N **PropuestaTaller** (un tallerista puede enviar varias propuestas en la misma edición).
- **EdicionFeria** (Core) 1—N **PropuestaTaller**; 1—N **Actividad**; 1—1 **ParametrosConvocatoriaTAL**.
- **PropuestaTaller** 0/1—1 **Actividad** (solo si fue `aceptada`).
- **Actividad** 1—N **Programación** (`PRG`) — fuera de este modelo, ver `PRG/Modelo de datos - Programación.md`.

---

## 4. Mapa entidad → caso de uso (trazabilidad)

| Entidad                   | Casos de uso relacionados                                              |
| ------------------------- | ---------------------------------------------------------------------- |
| Tallerista                | CU-TAL-002, CU-TAL-003                                                 |
| TipoActividadTAL          | CU-TAL-002, CU-TAL-006                                                 |
| PropuestaTaller           | CU-TAL-002 a CU-TAL-004, CU-TAL-007 a CU-TAL-010                       |
| Actividad                 | CU-TAL-005, CU-TAL-006, CU-TAL-009; y CU-PRG-002 a CU-PRG-004 en `PRG` |
| ParametrosConvocatoriaTAL | CU-TAL-001                                                             |
| NotificacionLoteTAL       | CU-TAL-010                                                             |

---

## 5. Temas abiertos del modelo

- Confirmar si Elvira notifica resultados en **lote** (como Hipólito) o **caso por caso**;
  `NotificacionLoteTAL` y CU-TAL-010 son una extrapolación por simetría, no una necesidad
  confirmada — ver advertencia en CU-TAL-010.
- Confirmar si existe una ventana de edición **posterior a la aceptación** (similar a la que
  describe la Junta 2 con organizadores FILEY para "registrantes aceptados"), separada de la
  edición por `cambios_solicitados` (CU-TAL-003) — pendiente, ver `CU-TAL Índice.md`.
- El mecanismo de "horario final" que gatilla la publicación a `VIS` vive conceptualmente en
  `PRG` (ver "Temas abiertos" en `PRG/Modelo de datos - Programación.md`), no en este modelo.

---

## Reglas de negocio relacionadas

El ciclo de dictamen (pendiente/cambios_solicitados/aceptada/rechazada), la constancia
obligatoria y la cifra real de selección (~250 de ~300 propuestas) están documentados en
`CU-TAL Índice.md` y en cada CU referenciado arriba.
