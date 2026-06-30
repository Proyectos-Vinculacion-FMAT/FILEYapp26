---
estado: propuesta
version: 0.5
tags:
  - tipo/indice
  - dom/vis
fecha: 2026-06-24
fecha_actualizacion: 2026-06-29
---
# CU-VIS — Índice de casos de uso (Visitas escolares)

Inventario preliminar de casos de uso del dominio **Visitas escolares** (`VIS`): propuesta
de la escuela/institución, revisión de esa propuesta, catálogo y reserva de talleres para
armar el itinerario, y administración de las visitas ya aceptadas. Basado en la necesidad
documental original de FILEY —
[Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>)—,
confirmada por Elvira como su necesidad principal en la
[Junta 2 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md>)
y homologada en alcance con la
[Junta 3 con Equipo de desarrollo](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md>).
Solo títulos y objetivo; la redacción detallada (flujo principal, alternos y excepciones) se
completará tras la revisión con el profesor. Las notas y la evidencia que sustenta cada CU se
concentran al final de este índice.

**Actores:** Aplicante · Participante · Administrador · Sistema.

## A. Aplicación

- [CU-VIS-001 Registrar la propuesta de visita escolar (datos de la escuela y del contacto)](<A - Aplicación/CU-VIS-001 Registrar la propuesta de visita escolar (datos de la escuela y del contacto).md>)
- [CU-VIS-002 Editar la propuesta dentro de la ventana de modificación](<A - Aplicación/CU-VIS-002 Editar la propuesta dentro de la ventana de modificación.md>)
- [CU-VIS-003 Consultar mi propuesta y su estado](<A - Aplicación/CU-VIS-003 Consultar mi propuesta y su estado.md>)

## C. Catálogo y reserva de talleres

- [CU-VIS-010 Consultar el catálogo de talleres disponibles, filtrado por nivel educativo, día y turno](<C - Catálogo y reserva de talleres/CU-VIS-010 Consultar el catálogo de talleres disponibles, filtrado por nivel educativo, día y turno.md>)
- [CU-VIS-011 Validar que el cupo restante del taller cubra la cantidad de visitantes](<C - Catálogo y reserva de talleres/CU-VIS-011 Validar que el cupo restante del taller cubra la cantidad de visitantes.md>)
- [CU-VIS-012 Reservar uno o varios talleres del catálogo para armar el itinerario de la visita](<C - Catálogo y reserva de talleres/CU-VIS-012 Reservar uno o varios talleres del catálogo para armar el itinerario de la visita.md>)
- [CU-VIS-013 Consultar el itinerario armado de mi visita (talleres reservados, cupo garantizado)](<C - Catálogo y reserva de talleres/CU-VIS-013 Consultar el itinerario armado de mi visita (talleres reservados, cupo garantizado).md>)
- [CU-VIS-014 Quitar un taller reservado del itinerario (liberar el cupo)](<C - Catálogo y reserva de talleres/CU-VIS-014 Quitar un taller reservado del itinerario (liberar el cupo).md>)

## B. Herramientas de Administración

- [CU-VIS-004 Consultar la lista de propuestas, filtrable](<B - Herramientas de Administración/CU-VIS-004 Consultar la lista de propuestas, filtrable.md>)
- [CU-VIS-005 Revisar el detalle de una propuesta](<B - Herramientas de Administración/CU-VIS-005 Revisar el detalle de una propuesta.md>)
- [CU-VIS-006 Aceptar una propuesta](<B - Herramientas de Administración/CU-VIS-006 Aceptar una propuesta.md>)
- [CU-VIS-007 Solicitar cambios a una propuesta](<B - Herramientas de Administración/CU-VIS-007 Solicitar cambios a una propuesta.md>)
- [CU-VIS-008 Rechazar una propuesta](<B - Herramientas de Administración/CU-VIS-008 Rechazar una propuesta.md>)
- [CU-VIS-009 Notificar el resultado de la propuesta al Aplicante](<B - Herramientas de Administración/CU-VIS-009 Notificar el resultado de la propuesta al Aplicante.md>)
- [CU-VIS-015 Consultar la lista de visitas escolares aceptadas, filtrable](<B - Herramientas de Administración/CU-VIS-015 Consultar la lista de visitas escolares aceptadas, filtrable.md>)
- [CU-VIS-016 Ver el detalle de una visita escolar](<B - Herramientas de Administración/CU-VIS-016 Ver el detalle de una visita escolar.md>)
- [CU-VIS-017 Quitar manualmente una visita de un taller](<B - Herramientas de Administración/CU-VIS-017 Quitar manualmente una visita de un taller.md>)

---

## Notas y aclaraciones

> [!note] Qué es una visita escolar
> Confirmado en alcance en la Junta 3. La **visita escolar** es un trámite de registro
> aparte: no es un evento ni una solicitud a una actividad, sino el itinerario que un
> representante de una institución arma seleccionando actividades infantiles/juveniles y
> reservando cupo para asistir con las personas que representa. Es, sin embargo, un **tipo
> de propuesta** más dentro del sistema homologado de Convocatorias `[REG]`: sigue el mismo
> ciclo Pendiente a revisión → Aceptada/Solicitud de cambios/Rechazada, y la aceptación
> convierte al Aplicante en Participante.

<!-- -->

> [!info] Sobre la evidencia de este dominio
> A diferencia de `PRG`/`SAL`, la Junta 3 no granuló ajuste por ajuste de `VIS` (ver
> [§5.3](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#53-vis>):
> "implementar con campos mínimos hasta objetivo"). La evidencia principal de este dominio
> es, por tanto, anterior a Junta 3: el documento entregado por FILEY
> [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>)
> y la necesidad #1 de Elvira recogida en la
> [Junta 2 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md>).
> El [Análisis de archivos proporcionados](<../../soporte/extraido/Analisis de archivos proporcionados.md>)
> (sección 2.1, roce R1) documenta que el equipo había marcado esta necesidad como "fuera de
> scope" antes de Junta 3, pese a que ya estaba entregada por escrito.

<!-- -->

> [!success] Resuelto en la Junta 3 con organizadores FILEY
>
> - **Detalle del formulario para aplicantes:** confirmado. Además de los datos generales y la
>   cantidad de visitantes (CU-VIS-001), la escuela/institución declara: clave de centro de
>   trabajo (CCT), si es pública o privada (para que FILEY evalúe apoyo de transporte interno),
>   ubicación (Mérida / municipio cercano / otro estado), turno (matutino/vespertino), nivel
>   educativo (primaria/secundaria/preparatoria; universidad cuenta como público general) —
>   **un registro/propuesta distinto por nivel educativo** si la escuela comparte niveles—,
>   un representante obligatorio por cada grupo en que se divida la visita, y un campo libre
>   para detalles (alumnos de más, niños con capacidades especiales). Contacto: puede ser
>   maestro directo o padre de familia, con su teléfono y el de la institución. Ver
>   [CU-VIS-001](<A - Aplicación/CU-VIS-001 Registrar la propuesta de visita escolar (datos de la escuela y del contacto).md>)
>   y [RSM - Junta 3 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>).
> - **Entrega del itinerario:** se envía por correo de forma automática a ambos contactos
>   (institución y representante registrante), junto con reglamento y carta de
>   confirmación/bienvenida. **Ya hay un ejemplo real** de la carta de confirmación (precisión
>   2026-06-29, ver
>   [extraído](<../../soporte/extraido/Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Carta%20de%20confirmaci%C3%B3n.%20SECUNDARIA%20EDMUNDO%20VILLALVA%20RODR%C3%8DGUEZ.md>)):
>   encabezado con fecha/lugar, destinatario (responsable de inscripción de la institución),
>   y por cada actividad asignada su tipo, título, fecha y hora, salón/sala y el **cupo total**
>   del espacio asignado (no la cantidad de visitantes de esa escuela). Cierra con instrucción
>   de llegar 10 min antes y firma "Equipo de vinculación FILEY". También hay un ejemplo íntegro
>   del [reglamento de 16 reglas](<../../soporte/extraido/Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Reglamento%20visitas%20escolares%20FILEY%202026.md>)
>   que se anexa al mismo correo. **Sigue pendiente solo el membrete/diseño oficial** final —
>   ya no es bloqueante de contenido, solo de plantilla visual.
> - **Política de cupo de talleres:** resuelta — selección **libre por asiento**, sin candados
>   ni combinaciones prefijadas (se descarta "un taller por escuela" y también "sala de cine o
>   3 talleres de 35"). Única regla vigente: máximo 105 alumnos por visita. Ver
>   [CU-VIS-012](<C - Catálogo y reserva de talleres/CU-VIS-012 Reservar uno o varios talleres del catálogo para armar el itinerario de la visita.md>).
> - **CU-VIS-004 a CU-VIS-009 (revisión y dictamen):** se mantienen como CUs propios de `VIS`, en
>   la sección **B. Herramientas de Administración**, con su propio panel visible solo para
>   administradores. La revisión **no** se absorbe en `REG`: cada dominio (`STD`, `VIS`, `EVT` y
>   `TAL`) tiene su propio panel de revisión y de notificaciones — `REG` solo aporta la captura
>   (el formulario). Ver [README.md](<../README.md#relación-entre-dominios>).

## Pendientes

- **Validación previa a reservar:** se entiende que habrá *alguna* validación o aprobación
  antes de que una visita escolar pueda reservar talleres, pero **no se sabe cuál exactamente**.
  El "al momento" de la fuente describe que la escuela elige en el momento en que tiene la
  capacidad de hacerlo (eliminando el ida y vuelta de correos con la coordinación), no que no
  exista validación. **Pendiente confirmar en la próxima junta.**
- **Mecanismo de "horario final"** (precisión 2026-06-29): confirmado que `VIS` solo consume
  un catálogo de horario **final**, nunca preliminar (ver CU-VIS-010 y la sección 2.6 de
  `Modelo de datos - Visitas escolares.md`), pero no está definido cómo una Programación de
  `PRG` pasa de preliminar a final — afecta también a `PRG/Modelo de datos - Programación.md`.

## Artefactos relacionados

- [`Modelo de datos - Visitas escolares.md`](<Modelo de datos - Visitas escolares.md>) — entidades y datos que el sistema almacena, antes (PropuestaVisita) y después (Visita/ReservaTaller) de la aceptación.

## Concentrado de evidencias

- CU-VIS-001: [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) (hoy la coordinación captura estos datos vía *forms*/*autocrat*, que alimenta una ficha técnica y un Excel-base de datos); confirmado en alcance en [Junta 3 §5.3](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#53-vis>) y glosario [§2.8](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#28-visitas-escolares-vis>). Captura además la **cantidad de alumnos/visitantes**, dato obligatorio que la fuente lista explícitamente ("la cantidad de alumnos que reservarán su asistencia"). **Regla dura [RN-VIS-001]:** máximo **105** alumnos por propuesta (no por escuela en general); resuelta en la [RSM - Junta 3 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>). Precisión (Elvira, 2026-06-29): listas cerradas reales de Estado/Municipio, "cargo del responsable", "Multigrado" como nivel educativo y Folio/fecha de recepción asignados por FILEY — ver el [Google Form real](<../../soporte/extraido/Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Ficha%20escolar.%20Secundaria%20_EDMUNDO%20VILLALVA%20RODRIGUEZ_.md>) y la nota dentro del CU.

- CU-VIS-002: ciclo genérico de propuesta (*Solicitud de cambios* → el Aplicante edita y reenvía) del [Junta 3 §2.2 Registros](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#22-registros-reg>); la visita escolar sigue ese mismo ciclo según la nota de alcance de este índice.

- CU-VIS-003: [Junta 3 §4.2 Aplicante, punto 2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#42-aplicante-std-evt-tal-vis>) ("Consultar la lista de sus propuestas enviadas").

- CU-VIS-004: [Junta 3 §4.1 Administrador — Revisar y resolver propuestas, punto 1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>); necesidad operativa en [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) (la coordinación obtiene la información de cada escuela interesada para poder agendarla).

- CU-VIS-005: [Junta 3 §4.1, punto 2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- CU-VIS-006: [Junta 3 §4.1, punto 3 (Aceptada)](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>) y diagrama de estados de la propuesta en [§2.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#21-actores>).

- CU-VIS-007: [Junta 3 §4.1, punto 3 (Solicitud de cambios)](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- CU-VIS-008: [Junta 3 §4.1, punto 3 (Rechazada)](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- CU-VIS-009: glosario de *Notificación* en [Junta 3 §2.2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#22-registros-reg>); necesidad explícita en [Junta 2 con organizadores FILEY — Necesidades del sistema](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#necesidades-del-sistema>) ("Enviar correos de confirmación a las escuelas registradas") y en [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) ("recibir un correo de confirmación automático con la información previamente seleccionada").

- CU-VIS-010: [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) ("que la escuela pueda visualizar los talleres disponibles, con los días y horarios... así como la descripción del evento"); necesidad #1 de Elvira en [Junta 2 con organizadores FILEY — Necesidades del sistema](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#necesidades-del-sistema>) (pasar la responsabilidad de elegir el taller a la escuela, validando aforo y nivel educativo); acción confirmada en [Junta 3 §4.3 Participante, tipo visita VIS](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#43-participante>).

- CU-VIS-011: [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) ("Una vez que la actividad llegue al cupo máximo aparezca... Cupo lleno, No disponible"); glosario de *Cupo* en [Junta 3 §2.8](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#28-visitas-escolares-vis>).

- CU-VIS-012: [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) (candados: una sala de cine para 105 alumnos o 3 talleres de 35 para los mismos 105 espacios; preferencia de visitar el mismo día); política de un taller por escuela pendiente desde [Junta 2 con organizadores FILEY — Pendientes por definir](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#pendientes-por-definir>); acción confirmada en [Junta 3 §4.3](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#43-participante>).

- CU-VIS-013: glosario de *Itinerario* en [Junta 3 §2.8](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#28-visitas-escolares-vis>); [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) ("al momento sepan ya su itinerario... esto les ayuda a gestionar con antelación su transporte y su calendario de actividades").

- CU-VIS-014: simétrico a CU-VIS-012, sobre el mismo glosario de *Cupo*/*Itinerario* en [Junta 3 §2.8](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#28-visitas-escolares-vis>). Se acota como **autocorrección del Participante** (quitar un taller elegido por error) **antes de generar el itinerario final**. La baja por cancelación imprevista la realiza la coordinación en CU-VIS-017.

- CU-VIS-015: necesidad de la coordinación de ubicar qué escuela va a qué taller, en [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) ("es primordial ubicar qué escuela va a qué taller/actividad"); patrón homólogo a la administración de propuestas en [Junta 3 §4.1 — Revisar y resolver propuestas](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>). Incluye la **numeralia** (suma total de alumnos/visitantes) que la fuente pide para saber automáticamente cuántas personas visitarán la FILEY.

- CU-VIS-016: mismo origen que CU-VIS-015; capacidades por espacio (Ek Balam, salas de cine, Gran Foro) detalladas en [Junta 2 con organizadores FILEY — Espacios disponibles](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#espacios-disponibles>) y en [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>).

- CU-VIS-017: [Junta 2 con organizadores FILEY — Pendientes por definir](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#pendientes-por-definir>) (manejo de cupos a discreción de la coordinación). Complementa a CU-VIS-014: aquella es la autocorrección del Participante; esta es la baja administrativa por cancelación imprevista.
