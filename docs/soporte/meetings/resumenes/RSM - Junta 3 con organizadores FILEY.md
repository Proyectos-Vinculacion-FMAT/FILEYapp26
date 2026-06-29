---
tags:
  - tipo/junta-resumen
  - tema/cliente
  - tema/descubrimiento
  - tema/equipo-desarrollo
  - tema/arquitectura
  - tema/formularios
  - tema/trazabilidad
  - dom/vis
  - dom/tal
  - dom/evt
  - dom/reg
  - dom/prg
  - dom/sal
  - dom/std
estado: borrador
version: "1.0"
fecha: 2026-06-25
fecha_actualizacion: 2026-06-25
Asistentes:
  - "Organizadora de Talleres: Elvira"
  - "Equipo de desarrollo: Profesor Edgar Cambranes"
  - "Equipo de desarrollo: Isaac Ortiz"
  - "Equipo de desarrollo: Juan Manuel Miranda"
---

# Junta 3 con organizadores FILEY

## Contexto

Tercera junta de descubrimiento con organizadores FILEY, centrada en el área de Elvira: el detalle del registro de visitas escolares (datos de la escuela, cupos, documentación) y las constancias de participación. Al final de la sesión se tuvo un bloque aislado solo con el equipo de desarrollo, en el que se resolvieron tres decisiones de arquitectura que habían quedado abiertas en la [Junta 3 con Equipo de desarrollo](<RSM - Junta 3 con Equipo de desarrollo.md#6-decisiones-pendientes>) (D1, D2 y D3).

> [!warning] Sin transcripción
> Esta junta no tiene grabación ni transcripción asociada. El contenido proviene de notas manuales tomadas durante la sesión; por eso no hay marcadores `[hh:mm:ss]` de referencia, a diferencia de las Juntas 1 y 2.

## Roles y coordinación entre organizadores

- Cada organizador (Hipólito, Elvira, José Avilés) tiene su propio registro de lo que le llega.
- Hipólito le comenta a Elvira qué actividades tiene para jóvenes, pero él se encarga de programarlas; Elvira es quien se ocupa del público.
- El maestro José Avilés, encargado de actividades artísticas, también puede tener talleres para niños — igual que con Hipólito, Elvira solo se encarga de llenar los cupos, no de organizarlos.
- Riesgo de cruce: a veces se mete a la convocatoria una actividad de talleres que a la vez participa en un evento de Hipólito, y pueden quedar agendados el mismo día a la misma hora.

## Visitas escolares — datos del registro

Datos que captura la propuesta de una escuela/institución:

- **Contacto:** puede ser un maestro directo o un padre/madre de familia; da su teléfono y el contacto de la persona. Los datos de la institución incluyen el correo de la escuela.
- **Pública o privada:** con este dato FILEY evalúa internamente si puede apoyar a la escuela con el transporte (las escuelas públicas requieren ese apoyo).
- **Turno:** matutino o vespertino.
- **Clave de centro de trabajo (CCT).**
- **Ubicación:** si la escuela está en Mérida o en algún municipio cercano; también interesa si es de Yucatán o de algún estado vecino.
- **Nivel educativo:** primaria, secundaria, preparatoria y, en algunas ocasiones, universidad (estas últimas cuentan como público general). **Un registro (propuesta) distinto por nivel educativo**, en caso de que la escuela tenga niveles educativos compartidos.
- **Grupo responsable por grado:** cada grado tiene un grupo responsable.
- **Representante por grupo:** se pide un representante por cada grupo en los que se divide una visita escolar. Es obligatorio que lo indiquen, pero la validación de que esa persona en efecto exista/asista es un control interno de FILEY, no del sistema.
- **Campo libre:** la propuesta tiene un campo libre donde la escuela indica detalles como alumnos de más o niños con capacidades especiales.

## Visitas escolares — cupos y espacios

- Las escuelas normalmente tienen grupos de 35 (+5 o -3 alumnos).
- La cantidad de personas que entran a un taller solo cuenta a los niños: los representantes no reservan cupo.
- El cupo máximo de un taller es de 35. La responsabilidad de fragmentar los grupos para no exceder ese cupo es de la escuela — la idea no es llenar exactamente esos 35 lugares, sino evitar que un taller se quede en cero asistentes.
- Si una escuela se fragmenta mucho, como máximo terminaría repartida entre 6 salones, porque ese es el total de salones disponibles para talleres.
- La Ludoteca (sala 9°, la sala extra) es un comodín: un área de lectura o descanso que puede tener actividades o no.
- Límite de reservado por escuela para las salas de cine: cada sala tiene entre 120 y 130 asientos, hasta 150 alumnos como máximo rebosando.
- JUDEMS es el área deportiva de la UADY (espacio adicional mencionado para posibles actividades).

> [!success] Precisión de seguimiento — selección libre por asiento
> Tras revisar el impacto de esta junta en la documentación de `VIS`, Elvira precisó que la selección de talleres ahora es **libre por asiento**: la escuela decide cómo dividir sus grupos y a qué actividades entrar, con cuántos alumnos en cada una. Ya no hay candados ni combinaciones de cupo prefijadas (se descarta el esquema anterior de "una sala de cine o 3 talleres de 35"). Las únicas reglas vigentes son el **máximo de 105 alumnos por visita escolar** y que **cada nivel educativo es un registro/propuesta distinto** (ver sección anterior).

## Visitas escolares — documentación e itinerario

- Se envía un documento oficial con el itinerario, en hoja membretada y formato oficial, con todos los datos de la visita. Esto sirve para que se lo sellen en su centro de trabajo y para hacer la reservación más formal.
- Hace falta la plantilla de ese documento — sigue siendo el bloqueante para implementarlo.
- El paquete de documentos incluye también el reglamento y una carta de confirmación y bienvenida (que incluye el punto de la feria donde se espera a la escuela).
- El paquete completo se envía a ambos correos: el de la institución y el de la persona que registró a la escuela.

> [!success] Precisión de seguimiento — canal confirmado
> Se confirma que el envío de este paquete es **por correo, de forma automática**, a ambos contactos.

## Constancias de participación

- Hoy las constancias de participación se hacen de manera manual.
- Se pueden generar y enviar de manera automática, pero originalmente se entendía que esto requería que los registros tuvieran los datos de los participantes capturados de forma correcta.

> [!success] Precisión de seguimiento — automatización incondicional
> Se precisó que las constancias **se automatizarán siempre**, independientemente de si los nombres capturados por los registrantes son correctos. Solo se necesita la plantilla. El diseño (texto, imagen de fondo y campos a rellenar) será **hardcodeado** y de generación automática, no configurable.

## Sesión aislada con el equipo de desarrollo

Se tuvo una parte de la junta de manera aislada con los desarrolladores, en la que se acordaron los siguientes puntos. Resuelven D1, D2 y D3, dejadas abiertas en la [Junta 3 con Equipo de desarrollo](<RSM - Junta 3 con Equipo de desarrollo.md#6-decisiones-pendientes>).

### Convocatorias `[REG]` — D1 resuelta

- La herramienta de convocatorias es hardcodeada; por ahora el CRUD (armador de formularios) está fuera de alcance.
- `REG` se está trabajando en otra rama (Juan Manuel Miranda); sus cambios se coordinan por separado.

### Notificaciones — D3 resuelta

- Las notificaciones son por apartado: el usuario, después de registrarse, tiene distintas opciones de registro de convocatoria. En esas puede agregar un registro nuevo o revisar el estado de los que ya ha mandado.
- Una barra de notificaciones transversal queda descartada por el momento.
- Las notificaciones se miran por módulo.

> [!success] Precisión de seguimiento — paneles por dominio
> La revisión de propuestas de `EVT` y `TAL` pertenece a su propio dominio, no a `REG`: cada uno debe tener su propio panel de revisión (visible solo para administradores), igual que ya ocurre con `STD` y `VIS`. Las notificaciones de esa revisión también son por panel, consistente con el punto anterior. Aparte de los paneles de revisión, habrá paneles de programación: uno para `EVT` y otro para `TAL`.

### Bloques de horario — D2 resuelta

- Se quitan las creaciones de bloques horarios: queda hardcodeado por panel.
  - Panel de eventos de contenidos: bloques fijos de 1:15.
  - Panel de talleres: bloques fijos de 50 minutos.

> [!success] Precisión de seguimiento — duración exacta y ubicación
> El panel de talleres usa bloques de **1 hora**, compuestos de 50 minutos de actividad + 10 minutos de descanso entre sesión (no 50 minutos netos). Además, los bloques de horario no se configuran en las salas: al crear una sala, esta no tiene ningún horario relacionado. Es el panel de programación (de eventos o de talleres) el que define en qué bloques se divide el horario, según el panel en el que se esté programando.

### STD y visitas escolares — comportamiento especial

- Debido a cómo se manejará el aspecto de los registros de manera modular, `STD` se comportará de manera especial, y probablemente las visitas escolares también. Sin más detalle por ahora.

## Pendientes por definir

- Detallar en qué consiste el comportamiento especial de `STD` (y probablemente `VIS`) mencionado arriba.
- Plantilla del documento oficial de itinerario membretado (bloqueante para CU-VIS).
- Plantilla de las constancias de participación (bloqueante; diseño y campos ya definidos como hardcodeados).

## Documentos relacionados

- [Junta 2 con organizadores FILEY](<RSM - Junta 2 con organizadores FILEY.md>)
- [Junta 3 con Equipo de desarrollo](<RSM - Junta 3 con Equipo de desarrollo.md>)
- [requisitos/VIS/CU-VIS Índice.md](<../../../requisitos/VIS/CU-VIS Índice.md>)
- [requisitos/PRG/CU-PRG Índice.md](<../../../requisitos/PRG/CU-PRG Índice.md>)
- [requisitos/SAL/CU-SAL Índice.md](<../../../requisitos/SAL/CU-SAL Índice.md>)
- [requisitos/README.md](<../../../requisitos/README.md>)
