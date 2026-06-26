---
estado: propuesta
version: 0.2
tags:
  - tipo/indice
  - dom/vis
fecha: 2026-06-24
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
completará tras la revisión con el profesor. Cada CU enlaza a su archivo y, debajo, a la
evidencia que lo sustenta.

**Actores:** Aplicante · Participante · Administrador · Sistema.

> [!note]
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

## A. Aplicación

- [CU-VIS-001 Registrar la propuesta de visita escolar (datos de la escuela y del contacto)](<A - Aplicación/CU-VIS-001 Registrar la propuesta de visita escolar (datos de la escuela y del contacto).md>) — *Aplicante*
  - Evidencia: [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) (hoy la coordinación captura estos datos vía *forms*/*autocrat*, que alimenta una ficha técnica y un Excel-base de datos); confirmado en alcance en [Junta 3 §5.3](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#53-vis>) y glosario [§2.8](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#28-visitas-escolares-vis>).

- [CU-VIS-002 Editar la propuesta dentro de la ventana de modificación](<A - Aplicación/CU-VIS-002 Editar la propuesta dentro de la ventana de modificación.md>) — *Aplicante*
  - Evidencia: ciclo genérico de propuesta (*Solicitud de cambios* → el Aplicante edita y reenvía) del [Junta 3 §2.2 Registros](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#22-registros-reg>); la visita escolar sigue ese mismo ciclo según la nota de alcance de este índice.

- [CU-VIS-003 Consultar mi propuesta y su estado](<A - Aplicación/CU-VIS-003 Consultar mi propuesta y su estado.md>) — *Aplicante*
  - Evidencia: [Junta 3 §4.2 Aplicante, punto 2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#42-aplicante-std-evt-tal-vis>) ("Consultar la lista de sus propuestas enviadas").

## B. Revisión

- [CU-VIS-004 Consultar la lista de propuestas de visita escolar, filtrable por estado](<B - Revisión/CU-VIS-004 Consultar la lista de propuestas de visita escolar, filtrable por estado.md>) — *Administrador*
  - Evidencia: [Junta 3 §4.1 Administrador — Revisar y resolver propuestas, punto 1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>); necesidad operativa en [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) (la coordinación obtiene la información de cada escuela interesada para poder agendarla).

- [CU-VIS-005 Revisar el detalle de una propuesta (datos de la escuela-institución)](<B - Revisión/CU-VIS-005 Revisar el detalle de una propuesta (datos de la escuela-institución).md>) — *Administrador*
  - Evidencia: [Junta 3 §4.1, punto 2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- [CU-VIS-006 Aceptar una propuesta de visita escolar](<B - Revisión/CU-VIS-006 Aceptar una propuesta de visita escolar.md>) — *Administrador*
  - Evidencia: [Junta 3 §4.1, punto 3 (Aceptada)](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>) y diagrama de estados de la propuesta en [§2.1](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#21-actores>).

- [CU-VIS-007 Solicitar cambios a una propuesta con motivo](<B - Revisión/CU-VIS-007 Solicitar cambios a una propuesta con motivo.md>) — *Administrador*
  - Evidencia: [Junta 3 §4.1, punto 3 (Solicitud de cambios)](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- [CU-VIS-008 Rechazar una propuesta con motivo](<B - Revisión/CU-VIS-008 Rechazar una propuesta con motivo.md>) — *Administrador*
  - Evidencia: [Junta 3 §4.1, punto 3 (Rechazada)](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- [CU-VIS-009 Notificar el resultado de la propuesta al Aplicante](<B - Revisión/CU-VIS-009 Notificar el resultado de la propuesta al Aplicante.md>) — *Sistema*
  - Evidencia: glosario de *Notificación* en [Junta 3 §2.2](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#22-registros-reg>); necesidad explícita en [Junta 2 con organizadores FILEY — Necesidades del sistema](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#necesidades-del-sistema>) ("Enviar correos de confirmación a las escuelas registradas") y en [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) ("recibir un correo de confirmación automático con la información previamente seleccionada").

## C. Catálogo y reserva de talleres

- [CU-VIS-010 Consultar el catálogo de talleres disponibles, filtrado por nivel educativo, día y turno](<C - Catálogo y reserva de talleres/CU-VIS-010 Consultar el catálogo de talleres disponibles, filtrado por nivel educativo, día y turno.md>) — *Participante*
  - Evidencia: [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) ("que la escuela pueda visualizar los talleres disponibles, con los días y horarios... así como la descripción del evento"); necesidad #1 de Elvira en [Junta 2 con organizadores FILEY — Necesidades del sistema](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#necesidades-del-sistema>) (pasar la responsabilidad de elegir el taller a la escuela, validando aforo y nivel educativo); acción confirmada en [Junta 3 §4.3 Participante, tipo visita VIS](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#43-participante>).

- [CU-VIS-011 Validar que el cupo restante del taller cubra la cantidad de visitantes](<C - Catálogo y reserva de talleres/CU-VIS-011 Validar que el cupo restante del taller cubra la cantidad de visitantes.md>) — *Sistema*
  - Evidencia: [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) ("Una vez que la actividad llegue al cupo máximo aparezca... Cupo lleno, No disponible"); glosario de *Cupo* en [Junta 3 §2.8](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#28-visitas-escolares-vis>).

- [CU-VIS-012 Reservar uno o varios talleres del catálogo para armar el itinerario de la visita](<C - Catálogo y reserva de talleres/CU-VIS-012 Reservar uno o varios talleres del catálogo para armar el itinerario de la visita.md>) — *Participante*
  - Evidencia: [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) (candados: una sala de cine para 105 alumnos o 3 talleres de 35 para los mismos 105 espacios; preferencia de visitar el mismo día); política de un taller por escuela pendiente desde [Junta 2 con organizadores FILEY — Pendientes por definir](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#pendientes-por-definir>); acción confirmada en [Junta 3 §4.3](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#43-participante>).

- [CU-VIS-013 Consultar el itinerario armado de mi visita (talleres reservados, cupo garantizado)](<C - Catálogo y reserva de talleres/CU-VIS-013 Consultar el itinerario armado de mi visita (talleres reservados, cupo garantizado).md>) — *Participante*
  - Evidencia: glosario de *Itinerario* en [Junta 3 §2.8](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#28-visitas-escolares-vis>); [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) ("al momento sepan ya su itinerario... esto les ayuda a gestionar con antelación su transporte y su calendario de actividades").

- [CU-VIS-014 Quitar un taller reservado del itinerario (liberar el cupo)](<C - Catálogo y reserva de talleres/CU-VIS-014 Quitar un taller reservado del itinerario (liberar el cupo).md>) — *Participante*
  - Evidencia: simétrico a CU-VIS-012, sobre el mismo glosario de *Cupo*/*Itinerario* en [Junta 3 §2.8](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#28-visitas-escolares-vis>). Ninguna fuente revisada (ni el documento de FILEY ni las juntas) menciona explícitamente que la escuela pueda quitar un taller ya reservado — **pendiente confirmar con el cliente** si esto es una capacidad real o si solo aplica la edición dentro de ventana (CU-VIS-002).

## D. Administración

- [CU-VIS-015 Consultar la lista de visitas escolares aceptadas, filtrable](<D - Administración/CU-VIS-015 Consultar la lista de visitas escolares aceptadas, filtrable.md>) — *Administrador*
  - Evidencia: necesidad de la coordinación de ubicar qué escuela va a qué taller, en [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>) ("es primordial ubicar qué escuela va a qué taller/actividad"); patrón homólogo a la administración de propuestas en [Junta 3 §4.1 — Revisar y resolver propuestas](<../../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#41-administrador>).

- [CU-VIS-016 Ver el detalle de una visita escolar (escuela, itinerario, cupos)](<D - Administración/CU-VIS-016 Ver el detalle de una visita escolar (escuela, itinerario, cupos).md>) — *Administrador*
  - Evidencia: mismo origen que CU-VIS-015; capacidades por espacio (Ek Balam, salas de cine, Gran Foro) detalladas en [Junta 2 con organizadores FILEY — Espacios disponibles](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#espacios-disponibles>) y en [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>).

---

> [!warning] Pendientes por confirmar con el cliente
>
> - El detalle real del **formulario para aplicantes** de la convocatoria de visita escolar
>   (campos de verificación de la escuela más allá del bosquejo mínimo); el formulario hoy
>   documentado en [Software para agendar escuelas](<../../soporte/extraido/Software para agendar escuelas.md>)
>   es, según el [Análisis de archivos proporcionados](<../../soporte/extraido/Analisis de archivos proporcionados.md>)
>   (sección 2.1), una propuesta de la propia Elvira, no confirmada todavía como la oficial.
> - La política de **un taller por escuela** (o por institución), mencionada en
>   [Junta 2 con organizadores FILEY — Pendientes por definir](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#pendientes-por-definir>).
> - Si la escuela puede **quitar un taller ya reservado** (CU-VIS-014): ninguna fuente revisada lo confirma explícitamente.
> - Si CU-VIS-004 a CU-VIS-009 (revisión) terminan siendo CUs propias de `VIS` o se absorben
>   en la revisión genérica de propuestas de `REG` (ver sección 4.1 de la Junta 3), dado que
>   la visita escolar ya es un tipo de propuesta más del sistema de Convocatorias.
