---
estado: propuesta
version: 0.1
tags:
  - tipo/catalogo-cu
  - dom/evt
  - dom/tal
  - dom/prg
fecha: 2026-07-04
---
# Catálogo de casos de uso — EVT · TAL · PRG

Inventario técnico de casos de uso de los dominios **Eventos generales (`EVT`)**,
**Talleres / actividades infantiles y juveniles (`TAL`)** y **Programación (`PRG`)**,
en el mismo formato tabular que [`STD/CU-STD.csv`](STD/CU-STD.csv): cada renglón indica
el **actor**, el **id**, el **título**, las **acciones de backend** (entidad del modelo de
datos que se toca), las **vistas de frontend** y la **complejidad** estimada.

> **Alcance compartido.** Este archivo cubre los **tres módulos en un solo documento**,
> separados por sección. La última columna, **Comparte con**, marca cuando una funcionalidad
> depende de —o es consumida por— otro módulo (`STD`, `VIS`, `REG`, `SAL`). Las funcionalidades
> transversales (identidad, salas) **no se reescriben aquí**: se referencian a su módulo dueño.

## Leyenda de módulos referenciados

| Módulo | Dominio                       | Relación con EVT/TAL/PRG                                                                                                                                                                         |
| ------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `REG` | Registros (identidad)         | Alta de cuenta y acceso OTP de Proponente/Tallerista/Participante (CU-REG-001, CU-REG-002). Las notificaciones se consultan**por panel/módulo**, sin bandeja transversal.                  |
| `SAL` | Salas y salones               | Catálogo único global de salas que`PRG` consulta al programar (CU-SAL-001 a CU-SAL-007). No se edita desde EVT/TAL/PRG.                                                                       |
| `STD` | Stands                        | Referencia estructural: EVT/TAL espejan varios CU de`STD` (solicitud → dictamen → notificación). Además, una actividad puede programarse en un **stand** en vez de una sala (RFH-33). |
| `VIS` | Visitas escolares             | **Consume** el catálogo de talleres de `TAL` **solo cuando el horario de `PRG` queda final** (CU-VIS-010). Dominio propio, no parte de TAL.                                      |
| Cores   | Registros / Programas / Salas | Entidades`Persona`, `EdicionFeria`, `BloqueHorario`, `ProgramaMaestro`, `Sala`, `Stand` viven en los Cores y se referencian.                                                          |

**Complejidad:** `Alta` / `Media` / `Baja`, misma escala que `CU-STD.csv`.

## Calendario estimado de término


la **base técnica** (modelo de datos, backend base, OTP/`REG`, correos) antes de empezar los CU.
La columna **Mes término** de cada tabla indica en qué mes queda terminada cada funcionalidad —el
equivalente a las columnas `Agosto` / `Septiembre` / `Octubre` con `X` del CSV de Hugo,
consolidadas aquí en una sola columna por legibilidad.

| Mes                          | Foco del mes                                                                                             | CUs |
| ---------------------------- | -------------------------------------------------------------------------------------------------------- | :-: |
| **Julio (2.ª mitad)** | Base técnica (fuera de CU): modelo de datos, backend/frontend base, OTP, correos                        | — |
| **Agosto**             | Lado del proponente/tallerista: convocatoria, envío, seguimiento y edición de propuestas               |  8  |
| **Septiembre**         | Herramientas de administración: listas, detalle, dictamen y notificaciones (EVT+TAL) + inicio de`PRG` | 11 |
| **Octubre**            | Programación (sala/horario), confirmación, publicación del programa, fichas y constancias             | 11 |


---

## 1. EVT — Eventos generales (programa de Hipólito)

**Actores:** Aplicante/Proponente · Administrador (Hipólito y su equipo) · Sistema.

| Actor         | ID         | Título                                                 | Acciones backend                            | Vistas frontend                                                          | Complejidad | Comparte con                                                           |
| ------------- | ---------- | ------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------ | :---------: | ---------------------------------------------------------------------- |
| Administrador | CU-EVT-001 | Configurar la convocatoria                              | UPDATE ParametrosConvocatoria               | Complex form view                                                        |    Alta    | —                                                                     |
| Aplicante     | CU-EVT-002 | Registro de la propuesta de la actividad                | CREATE Propuesta / CREATE PropuestaAdjunto  | Complex form (campos dinámicos por tipo de actividad) w/ file uploading |    Alta    | `REG` (identidad); espejo de CU-STD-001                              |
| Aplicante     | CU-EVT-003 | Consultar mis propuestas y revisar su estado actual     | READ Propuesta\<List\>                      | List view + status modal                                                 |    Baja    | Espejo de CU-STD-003                                                   |
| Aplicante     | CU-EVT-004 | Editar una propuesta tras solicitud de cambios          | UPDATE Propuesta                            | Pre-filled complex form                                                  |    Alta    | Espejo de CU-STD-002                                                   |
| Aplicante     | CU-EVT-005 | Descargar constancia de participación                  | READ Actividad → PDF                       | Download button + PDF                                                    |    Media    | —                                                                     |
| Administrador | CU-EVT-006 | Generar la ficha PDF de una actividad individual        | READ Actividad → PDF                       | Button + PDF render                                                      |    Media    | —                                                                     |
| Administrador | CU-EVT-007 | Consultar la lista de propuestas, filtrable             | READ Propuesta\<List\>                      | Filterable list view                                                     |    Media    | Espejo de CU-STD-004                                                   |
| Administrador | CU-EVT-008 | Revisar el detalle de una propuesta                     | READ Propuesta / PropuestaAdjunto           | Detailed information view                                                |    Media    | Espejo de CU-STD-005                                                   |
| Administrador | CU-EVT-009 | Dictaminar una propuesta (aceptar / cambios / rechazar) | UPDATE Propuesta / CREATE Actividad         | Button + modal form (dictamen + categoría)                              |    Alta    | Espejo de CU-STD-006 y CU-STD-007;**dispara `PRG`** al aceptar |
| Sistema       | CU-EVT-010 | Enviar notificaciones de resultado en lote              | CREATE NotificacionLote / UPDATE Propuesta  | Batch confirmation modal + email                                         |    Media    | `REG`; espejo de CU-STD-008                                          |
| Administrador | CU-EVT-011 | Visualizar el número de propuestas por estado          | READ Propuesta\<count\>                     | Counter tiles / dashboard                                                |    Baja    | —                                                                     |
| Administrador | CU-EVT-012 | Marcar la recepción del ejemplar físico               | UPDATE Propuesta (ejemplar_fisico_recibido) | Toggle en lista/detalle                                                  |    Baja    | —                                                                     |

> **Programación (sala + horario) no vive en EVT.** Al aceptar una propuesta (CU-EVT-009), el
> botón **"Revisar"** del renglón se reemplaza por **"Programar"**, que dispara **CU-PRG-002**
> (ver sección 3). La asignación, edición y borrado de horarios pertenecen a `PRG`; el catálogo
> de salas es de `SAL`.

---

## 2. TAL — Actividades infantiles y juveniles (convocatoria de Elvira)

**Actores:** Tallerista · Administrador (Elvira y su equipo) · Sistema.
Espejo del ciclo de `EVT`, con diferencias: **sin categorización cruzada**, **sin adjuntos de
archivo** y **constancia obligatoria** para todo tallerista.

| Actor         | ID         | Título                                                             | Acciones backend                                    | Vistas frontend                                       | Complejidad | Comparte con                                                 |
| ------------- | ---------- | ------------------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------- | :---------: | ------------------------------------------------------------ |
| Administrador | CU-TAL-001 | Configurar la convocatoria de actividades infantiles y juveniles    | UPDATE ParametrosConvocatoriaTAL                    | Form view (fechas + modalidades)                      |    Media    | `SAL` (ya no configura espacios propios)                   |
| Tallerista    | CU-TAL-002 | Registro de los datos de la propuesta de actividad infantil/juvenil | CREATE PropuestaTaller                              | Complex form (público meta, modalidad; sin adjuntos) |    Alta    | `REG`; espejo de CU-EVT-002                                |
| Tallerista    | CU-TAL-003 | Consultar mis propuestas y revisar su estado actual                 | READ PropuestaTaller\<List\>                        | List view + status modal                              |    Baja    | Espejo de CU-EVT-003                                         |
| Tallerista    | CU-TAL-004 | Editar una propuesta tras solicitud de cambios                      | UPDATE PropuestaTaller                              | Pre-filled form                                       |    Media    | Espejo de CU-EVT-004                                         |
| Tallerista    | CU-TAL-005 | Descargar constancia de participación                              | READ Actividad → PDF                               | Download button + PDF                                 |    Media    | Espejo de CU-EVT-005 (aquí constancia**obligatoria**) |
| Administrador | CU-TAL-006 | Generar la ficha PDF de una actividad                               | READ Actividad → PDF                               | Button + PDF render                                   |    Media    | Espejo de CU-EVT-006                                         |
| Administrador | CU-TAL-007 | Consultar la lista de propuestas, filtrable                         | READ PropuestaTaller\<List\>                        | Filterable list view (con contadores por estado)      |    Media    | Espejo de CU-EVT-007 (absorbe el contador por estado)        |
| Administrador | CU-TAL-008 | Revisar el detalle de una propuesta                                 | READ PropuestaTaller                                | Detailed information view                             |    Media    | Espejo de CU-EVT-008                                         |
| Administrador | CU-TAL-009 | Dictaminar una propuesta (aceptar / cambios / rechazar)             | UPDATE PropuestaTaller / CREATE Actividad           | Button + modal form                                   |    Media    | Espejo de CU-EVT-009;**dispara `PRG`** al aceptar    |
| Sistema       | CU-TAL-010 | Enviar notificaciones de resultado en lote*(tentativo)*             | CREATE NotificacionLoteTAL / UPDATE PropuestaTaller | Batch confirmation modal + email                      |    Media    | `REG`; espejo de CU-EVT-010 (sin evidencia directa aún)   |

> **Enlace con `VIS`.** Las actividades de `TAL` aceptadas y programadas alimentan el catálogo
> de talleres que consume `VIS` (CU-VIS-010), pero **solo cuando su horario en `PRG` queda
> final**, nunca con el horario preliminar.

---

## 3. PRG — Programación (armado del programa, común a EVT y TAL)

**Actores:** Administrador · Participante · Todos/Público · Sistema.
`PRG` no tiene formulario propio de actividad: **consume** las Actividades aceptadas de `EVT` y
`TAL` y les asigna sala + horario. Son **dos programas independientes** (eventos y talleres);
solo el de talleres admite repetir una misma actividad para llenar huecos.

| Actor            | ID         | Título                                                                 | Acciones backend                             | Vistas frontend                                    | Complejidad | Comparte con                                                                                              |
| ---------------- | ---------- | ----------------------------------------------------------------------- | -------------------------------------------- | -------------------------------------------------- | :---------: | --------------------------------------------------------------------------------------------------------- |
| Administrador    | CU-PRG-001 | Consultar lista de actividades de mi panel                              | READ Actividad\<List\>                       | List / schedule view (filtrada al panel)           |    Media    | Consume`EVT` / `TAL` (Actividad)                                                                      |
| Administrador    | CU-PRG-002 | Asignar una programación a una actividad                               | CREATE Programación                         | Assignment UI (sala + bloque; guardado implícito) |    Alta    | `SAL` (catálogo de salas), `STD` (stand como espacio, RFH-33); disparado desde panel `EVT`/`TAL` |
| Administrador    | CU-PRG-003 | Editar una programación de una actividad                               | UPDATE Programación                         | Assignment UI (mover sala/bloque)                  |    Media    | `SAL`                                                                                                   |
| Administrador    | CU-PRG-004 | Eliminar una programación de una actividad                             | DELETE Programación                         | Button + confirmation modal                        |    Baja    | La actividad regresa a estado`pendiente` en `EVT`/`TAL`                                             |
| Sistema          | CU-PRG-008 | Notificar al Participante su fecha, sala y horario (2.ª notificación) | CREATE Notificación / UPDATE Programación  | Batch / individual action + email                  |    Media    | `REG` (notificación por panel)                                                                         |
| Participante     | CU-PRG-009 | Confirmar asistencia o incomparecencia al horario asignado              | CREATE RespuestaProgramación                | Confirmation view (por horario)                    |    Media    | `REG`                                                                                                   |
| Todos / Público | CU-PRG-010 | Consultar el programa publicado mediante su URL estática               | READ ProgramaMaestro (generación estática) | Static public web page (por salón/sala)           |    Alta    | Vista pública común a`EVT` y `TAL`                                                                  |
| Administrador    | CU-PRG-011 | Exportar el programa a Excel o Word para uso interno                    | READ Programación → export                 | Export button (xlsx / docx)                        |    Media    | Formato interno, una hoja por salón                                                                      |

> **Hueco conocido (R5).** `PRG` hoy solo programa Actividades que vienen de una propuesta
> **aceptada**; no contempla bloques manuales sin propuesta detrás (apartados/artísticos de
> control). Pendiente de decidir si se añade un CU de entrada manual. No hay CRUD de bloques de
> horario en ningún dominio: los bloques están **hardcodeados por panel** (1:15 en Eventos,
> 1:00 en Talleres).

---

## Resumen por módulo

| Módulo |          CUs          | Actores                                           | Depende de                         | Es consumido por                              |
| ------- | :--------------------: | ------------------------------------------------- | ---------------------------------- | --------------------------------------------- |
| `EVT` |     12 (001–012)     | Aplicante · Administrador · Sistema             | `REG`, `SAL`, `PRG`          | `PRG` (programa)                            |
| `TAL` |     10 (001–010)     | Tallerista · Administrador · Sistema            | `REG`, `SAL`, `PRG`          | `PRG` (programa), `VIS` (catálogo final) |
| `PRG` | 8 (001–004, 008–011) | Administrador · Participante · Todos · Sistema | `EVT`, `TAL`, `SAL`, `STD` | `VIS` (horario final)                       |


---

*Referencias: [`EVT/CU-EVT Índice.md`](<EVT/CU-EVT Índice.md>) ·
[`TAL/CU-TAL Índice.md`](<TAL/CU-TAL Índice.md>) ·
[`PRG/CU-PRG Índice.md`](<PRG/CU-PRG Índice.md>) · modelos de datos de cada dominio ·
formato base [`STD/CU-STD.csv`](STD/CU-STD.csv).*
