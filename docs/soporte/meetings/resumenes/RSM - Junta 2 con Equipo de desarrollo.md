---
tags:
  - juntas
  - equipo-desarrollo
  - feedback
  - requisitos
  - casos-de-uso
  - arquitectura
  - stands
  - eventos
  - talleres
estado: final
fecha: 2026-06-18
Asistentes:
  - "Equipo de desarrollo: Profesor Edgar Cambranes"
  - "Desarrollador: Hugo Janssen (Stands / Expositores)"
  - "Desarrollador: Juan Hernández (Programa General)"
  - "Desarrollador: Isaac Ortiz (Talleres / Visitas escolares)"
---
# Junta 2 con Equipo de desarrollo

## Contexto

Junta **interna del equipo de desarrollo** (sin cliente), de tipo **revisión y feedback**. Cada desarrollador presentó su borrador de casos de uso / requisitos por módulo y el Profesor Edgar los revisó, acotó el alcance y reencauzó supuestos. La junta cerró reorganizando los tres módulos en una arquitectura común.

> [!important]
> Esta nota documenta el avance y las correcciones de los borradores del equipo, no es una especificación final. Varios requisitos discutidos quedaron por **descartar, reformular o granular**, y varias dudas deben confirmarse con el cliente antes de fijarse.

---

> [!info] Trazabilidad
> Los marcadores `[hh:mm:ss]` apuntan al `start` de la intervención correspondiente en la [transcripción](<../transcripciones/Junta 2 con Equipo de desarrollo/TRS - Junta 2 con Equipo de desarrollo.md>), para poder verificar cada afirmación contra la fuente. Un rango `[hh:mm:ss–hh:mm:ss]` indica el tramo donde se discutió el tema.

## Qué se hizo

- **Hugo** presentó el índice de casos de uso del módulo de **Stands / Expositores** (ciclo de reserva, pagos, descuentos, notificaciones y herramientas de administración) más una primera propuesta de **modelo de datos**. `[00:00:03–00:33:40]`
- **Juan** presentó un listado de requisitos del módulo de **Programa General / Maestro** (convocatoria, propuestas, aceptación, asignación de horario/salón, publicación). `[00:34:42–01:12:11]`
- **Isaac** presentó un borrador de casos de uso del módulo de **Talleres / Visitas escolares**. `[01:18:04–01:45:21]`
- Entre todos se acordó una **reorganización en componentes compartidos ("cores")** que aplica a los tres módulos. `[01:46:49–02:09:00]`

## Qué se hizo bien

- El entregable de **Hugo** quedó como **referencia/estándar** del equipo: índice completo y contabilizado de casos de uso, con modelo de datos. Se tomó como base de formato para los demás. `[00:33:40]` `[01:14:16]`
- Buena decisión de **simplificación de descuentos**: en lugar de un catálogo de descuentos con comportamientos y vencimientos distintos, se acordó un **único descuento global** por reserva (pronto pago automático por fecha + local/especial a discreción del administrador). `[00:11:13–00:22:26]`
- Buen reflejo de **acotar alcance**: se distinguió de forma consistente lo que resuelve el sistema vs. lo que sigue siendo gestión manual del cliente (p. ej. prórrogas y cancelaciones las decide Hipólito, no el sistema). `[00:02:44–00:04:42]`
- Se aclaró el concepto de **sello editorial** (segmentación/marca dentro de una editorial) y se confirmó que debe modelarse. `[00:26:21–00:31:28]`

## Qué se hizo mal (a corregir)

> [!warning]
> Estos puntos requieren rehacer o eliminar requisitos antes de la segunda vuelta.

- **Mezcla de responsabilidades en un mismo caso de uso (Isaac):** "consultar" se confundió con "organizar" los talleres, y "registrar" con "actualizar". Hay que **granular** a una sola responsabilidad por requisito (CRUD separados). `[01:41:26–01:43:23]`
- **Requisitos basados en supuestos no acordados con el cliente (Isaac):** actualización de la visita escolar por la propia escuela `[01:35:18–01:38:11]`, revisión incremental antes del cierre de convocatoria `[01:28:47–01:29:55]`, y una bitácora/timeline de cambios para talleres `[01:25:26–01:27:23]`. Se **descartan o reformulan** porque no salieron de las juntas con el cliente (y algunos son justo lo que Hipólito quería evitar).
- **Requisitos "de memoria" en vez de fuente (Juan):** algunos puntos se agregaron por lo recordado de la charla y no de los documentos `[00:44:08]`; se confundió **constancia de participación** con **gafetes** `[00:54:37–00:55:05]`; un requisito ("registro único de convocatoria con bifurcaciones") quedó sin poder explicarse porque no se recordaba su origen `[01:13:05–01:14:04]`.
- **Falta de homologación entre los tres entregables:** distinto formato, nombres e índice de casos de uso. `[01:14:16–01:16:08]`
- **Falta de coordinación previa entre Isaac y Juan**, pese a que sus módulos (eventos/programa) son casi el mismo core; no revisaron el trabajo del otro. `[01:15:30]` `[01:46:49]`

## Qué se puede mejorar

- **Una sola responsabilidad por caso de uso** (separar registrar / consultar / organizar / modificar / eliminar). `[01:43:23–01:44:00]`
- **Mantener el foco**: discutir un requisito a la vez. El Profesor tuvo que reencauzar varias veces hacia "¿de qué requisito estamos hablando?". `[01:32:38]` `[01:41:26]` `[01:42:47]`
- **Anotar dudas para preguntar al cliente en lote**, en vez de inventar comportamiento cuando un punto no quedó claro en la junta con el cliente. `[01:09:18]`
- **Homologar nombres, índice y granularidad** tomando como base el formato de Hugo (numeración solo para conteo, independiente del nombre). `[01:14:16–01:15:04]`

## Nuevas directrices y para cuándo

> [!todo] Acuerdos de trabajo
> Objetivo de entrega de referencia: **agosto** (no entra todo; se debe priorizar). Horizonte de desarrollo estimado: ~5-6 meses.

- **Reorganizar los tres módulos en 3 cores compartidos** — para la reunión del lunes: `[02:04:45–02:09:00]`
  1. **Registros** — solicitudes/altas y su administración (expositor/stand, eventos, taller, visita escolar). Es lo primero que debe liberarse. `[01:54:41–01:55:13]`
  2. **Programas** — creación/gestión del programa (general y de talleres; artísticos se agregaría después si da tiempo). `[02:07:12–02:07:48]`
  3. **Salas / Salones** — CRUD único de espacios, **compartido** entre Hipólito y Elvira (visible para ambos, coordinación interna). `[02:05:16–02:06:13]`
- **Granular** todos los requisitos a una sola responsabilidad (CRUD separados). `[01:44:45–01:45:21]`
- **Isaac y Juan**: coordinarse y unificar el core de **eventos/programa** (un taller es un tipo de evento; la visita escolar es un registro aparte con su propio componente). `[01:47:20–01:48:16]`
- **Homologar el formato** de los tres entregables siguiendo el de Hugo — trabajo offline, listo para el lunes. `[01:14:16–01:16:08]`
- Tener el **listado total de requisitos con priorización** (qué entra para agosto y qué va por fases/bloques) — para el lunes. `[02:09:28–02:11:06]`
- **Omitir por ahora** el "registro de usuario base"; se separa después de los registros por actividad. `[01:51:43–01:52:30]`
- **Reunión presencial: lunes 22 de junio de 2026, 9:00, en Femat** — segunda vuelta sobre la organización en pizarra y asignación de fechas/fases. `[02:14:23–02:14:45]`

## Dudas que salieron (a confirmar con el cliente)

Se agregaron al documento de [Preguntas para la siguiente sesion](<../meeting notes/Preguntas para la siguiente sesion.md). En resumen:

- ¿Los descuentos de **pronto pago** y **local** se **acumulan** o son excluyentes? (Hipólito y el contador no coincidían). `[00:21:36–00:21:50]`
- La **cartelera** de eventos alrededor de FILEY: ¿forma parte del sistema y qué datos captura? (no hay formato definido). `[00:44:50–00:48:05]`
- **Constancias de participación**: ¿se entregan?, ¿a quién?, y ¿cómo se manejan en actividades **grupales** (paneles, mesas)? `[00:54:11–00:59:06]`
- **Formulario de convocatoria**: parece faltar una categoría/opción de tipo de actividad (¿"Encuentro"?); confirmar el catálogo completo. `[01:00:38–01:01:42]`
- **Catálogo de salas**: ¿un único catálogo compartido (Hipólito + Elvira) o separado?, y ¿con qué frecuencia realmente cruzan espacios? `[02:02:36–02:04:21]`
- ¿Por dónde se canalizan las **salas de cine** (solo mañanas, actividades escolares) y quién las registra? `[02:00:02–02:01:44]`

## Documentos relacionados

- [Preguntas para la siguiente sesion](<../meeting notes/Preguntas para la siguiente sesion.md>)
- [Junta 1 con Equipo de desarrollo](<RSM - Junta 1 con Equipo de desarrollo.md>)
- [Junta 2 con organizadores FILEY](<RSM - Junta 2 con organizadores FILEY.md>)
- [Transcripción · Junta 2 con Equipo de desarrollo](<../transcripciones/Junta 2 con Equipo de desarrollo/TRS - Junta 2 con Equipo de desarrollo.md>)
