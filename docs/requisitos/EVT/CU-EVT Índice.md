---
estado: propuesta
version: 0.6
tags:
  - tipo/indice
  - dom/evt
fecha: 2026-06-20
fecha_actualizacion: 2026-06-29
---
# CU-EVT — Índice de casos de uso (Eventos generales / Programa general)

Inventario de casos de uso del dominio **Eventos Generales** (`EVT`): la convocatoria del **programa general** que administra **Hipólito**, desde la apertura de la convocatoria hasta el dictamen, la notificación de resultados, el cierre y la publicación. Las notas, los ajustes de homologación y la evidencia que sustenta cada CU se concentran al final de este índice.

**Actores:** Aplicante (persona/institución que propone una actividad) · Administrador (Hipólito y su equipo) · Sistema (procesos automáticos y temporizados).

## A. Convocatoria

- [CU-EVT-001 Configurar la convocatoria](<A - Convocatoria/CU-EVT-001 Configurar la convocatoria.md>)
- [CU-EVT-002 Registro de la propuesta de la actividad](<A - Convocatoria/CU-EVT-002 Registro de la propuesta de la actividad.md>)
- [CU-EVT-003 Consultar mis propuestas y revisar su estado actual](<A - Convocatoria/CU-EVT-003 Consultar mis propuestas y revisar su estado actual.md>)

## B. Revisión y Selección

- [CU-EVT-004 Editar una propuesta en respuesta a una solicitud de cambios del administrador](<B - Revisión y Selección/CU-EVT-004 Editar una propuesta en respuesta a una solicitud de cambios del administrador.md>)

## C. Cierre y Constancias

- [CU-EVT-005 Descargar constancia de participación](<C - Cierre y Constancias/CU-EVT-005 Descargar constancia de participación.md>)

## D. Publicación

- [CU-EVT-006 Generar la ficha PDF de una actividad individual](<D - Publicación/CU-EVT-006 Generar la ficha PDF de una actividad individual.md>)

## E. Herramientas de Administración

- [CU-EVT-007 Consultar la lista de propuestas, filtrable](<E - Herramientas de Administración/CU-EVT-007 Consultar la lista de propuestas, filtrable.md>)
- [CU-EVT-008 Revisar el detalle de una propuesta](<E - Herramientas de Administración/CU-EVT-008 Revisar el detalle de una propuesta.md>)
- [CU-EVT-009 Dictaminar una propuesta](<E - Herramientas de Administración/CU-EVT-009 Dictaminar una propuesta.md>)
- [CU-EVT-010 Enviar notificaciones de resultado en lote](<E - Herramientas de Administración/CU-EVT-010 Enviar notificaciones de resultado en lote.md>)
- [CU-EVT-011 Visualizar el número de propuestas por estado](<E - Herramientas de Administración/CU-EVT-011 Visualizar el número de propuestas por estado.md>)
- [CU-EVT-012 Marcar la recepción del ejemplar físico enviado por el aplicante](<E - Herramientas de Administración/CU-EVT-012 Marcar la recepción del ejemplar físico enviado por el aplicante.md>)

---

## Notas y aclaraciones

> [!note] Dominio paralelo
> La convocatoria de **actividades infantiles y juveniles** que administra **Elvira** es un
> dominio aparte: ver `TAL/CU-TAL Índice.md`. `TAL` sigue el mismo ciclo de dictamen que `EVT`
> (propuesta → aceptar / solicitar cambios / rechazar), con la diferencia de que las actividades
> de `TAL` no se clasifican por categoría.

<!-- -->

> [!note] La sala y el horario los asigna `PRG`, desde el mismo panel de `EVT`
> La programación no tiene pantalla aparte: una vez que el Administrador acepta una propuesta
> en el panel de `EVT`, el botón **"Revisar"** se reemplaza por **"Programar"** en ese mismo
> renglón (dispara CU-PRG-002). Los CUs de asignación, edición y eliminación de programaciones
> pertenecen a `PRG` (ver [`PRG/CU-PRG Índice.md`](<../PRG/CU-PRG Índice.md>)). El catálogo
> de salas/salones que `PRG` consulta al programar es el catálogo único global de `SAL`
> (ver `SAL/CU-SAL Índice.md`).

<!-- -->

> [!note] Identidad
> Los casos de uso de **identidad** (registro de Aplicante, acceso OTP) dependen del Core
> Registros: ver `REG/CU-REG Índice.md` — CU-REG-001, CU-REG-002 (usuarios externos).

## Ajustes de homologación (2026-06-29)

> [!note] Traído de la rama `main-juan` y reestructurado
> Estos CUs se redactaron en otra rama con número y carpeta inconsistentes entre sí. Se
> renumeraron a la secuencia final 001–012, se corrigieron `id`/encabezado/referencias cruzadas,
> y se normalizaron `tags` y `estado` a la convención del repositorio.

- **CU-EVT-003** (Editar propuesta tras solicitud de cambios) se **mueve a la sección A (Convocatoria)**: acción autogestionada del Aplicante, antes ubicada junto a las herramientas de administración.
- **"Enviar la propuesta" (002.1)** se **absorbe en CU-EVT-002**: llenar y enviar es un solo CU.
- **"Rechazar una propuesta con motivo registrado"** se **absorbe en CU-EVT-009** como flujo alterno A2.
- **"Marcar una propuesta como 'en negociación'"** se **pospone a v2**.
- La numeración de CUs es solo de conteo y no se reutiliza ni se recorre tras estas fusiones/bajas.

## Pendientes (alcance no redactado todavía)

- Exportación del programa completo y detalle interactivo en cartelera pública — la exportación a Excel/Word ya la cubre `PRG` (CU-PRG-011); falta decidir si la cartelera pública es un CU propio de `EVT` o se unifica con la visualización de `PRG` (CU-PRG-010).
- Catálogo administrable de `TipoActividad` (alta de tipos internos sin convocatoria pública, p. ej. artísticos).
- Publicación progresiva del programa y agenda personal del visitante (RFH-23 a RFH-26 en `requisitos_hipolito_eventos.md`).
- Auditoría de cambios excepcionales de horario fuera de ventana (`BitacoraEVE`) — depende de si ese registro vive en `EVT` o en `PRG`.

## Artefactos relacionados

- [`Modelo de datos - Eventos.md`](<Modelo de datos - Eventos.md>) — entidades y datos que el sistema almacena.
- [`Proceso de alto nivel - Eventos.md`](<Proceso de alto nivel - Eventos.md>) — diagrama del flujo de punta a punta.
