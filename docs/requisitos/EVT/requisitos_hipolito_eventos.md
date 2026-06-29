# Requisitos — Programa General / Eventos (parte de Hipólito)

## Convocatoria y recepción de propuestas

**RFH-01 — Convocatoria pública de propuestas del Programa General** *(↔ RF-32)*
El sistema debe permitir abrir un periodo de recepción de propuestas de actividades con fecha de apertura y cierre configurables. **Confirmado con el formulario real** : los tipos formales son Conversatorio, Conferencia, Charla, Mesa redonda, Presentación de libro, Presentación de revista, Lectura de obra y Encuentro, con **duración máxima de 50 minutos** cada uno. Congresos/coloquios/simposios son un caso especial gestionado aparte por Hipólito (no pasan por este formulario público — ver RFH-15). Es una de las únicas dos convocatorias públicas de toda la feria (la otra es la de talleres), así que conviene diseñarla como un módulo reutilizable, no como algo hecho a la medida solo para este caso.

**RFH-02 — Formulario de propuesta con múltiples actividades por proponente**
Una misma persona/institución debe poder registrar más de una propuesta mientras la convocatoria esté abierta, sin tener que volver a capturar sus datos básicos en cada una.

**RFH-03 — Adjuntos en la propuesta**
El formulario debe aceptar archivos adjuntos (PDF, JPG, PNG) como material de soporte de la propuesta (ej. semblanza, imagen del libro, programa interno del congreso).

**RFH-04 — Concentrado exportable de propuestas recibidas** *(↔ RF-04 / mismo patron "Excel" visto en talleres)*
El sistema debe poder generar un concentrado (tipo hoja de cálculo) de todas las propuestas recibidas, con columnas de estado editables, equivalente al Excel que hoy genera el formulario y que Hipólito complementa a mano. **Confirmado con `Base Registro de Propuestas FILEY 2027.xlsx`:** las columnas reales son ID, fecha de registro, nombre del contacto, cargo, dependencia/institución, correo, celular, tipo de actividad, nombre de la actividad, organiza(n), local o nacional (solo propuestas externas), estatus, fecha de participación, hora de participación, sala/salón.

**RFH-04.1 — Categorización cruzada de propuestas**
Las propuestas deben poder clasificarse en al menos dos ejes simultáneos: Literaria vs. Académica, e Interna-UADY vs. Externa/pública (visto en las 4 hojas reales del Excel: "Literarias UADY", "Actividades Literarias", "Académicas UADY", "Actividades Académicas"). El contador de cupo en vivo (RFH-05) debe poder desagregarse por estas categorías, no solo dar un total global — así lo hace hoy la hoja "Conteo" del Excel real.

## Revisión y selección

**RFH-05 — Revisión incremental con cupo visible en tiempo real** *(↔ RF-33)*
El administrador debe poder revisar las propuestas conforme llegan (no solo al cierre de la convocatoria) y ver en todo momento cuántos espacios/horarios totales le quedan disponibles frente a los ya aceptados. Hoy lo hace mentalmente comparando el total de espacios contra el número de propuestas que le llegan.

**RFH-06 — Aceptación en dos fases: decisión y asignación de horario por separado**
Al aceptar una propuesta, el sistema debe permitir notificar la aceptación **sin** asignar todavía fecha, salón ni hora — la asignación de horario debe poder ocurrir en un paso posterior e independiente. Esto es intencional: le da al coordinador margen para mover piezas del programa antes de comprometer un horario específico.

**RFH-07 — Notificación automática de aceptación/rechazo**
Cada decisión (aceptada/rechazada) debe disparar una notificación automática por correo y reflejarse en el sistema para que el proponente la consulte, sin que el coordinador tenga que escribir el correo manualmente.

**RFH-08 — Estado especial "en negociación" para autores/editoriales**
Debe existir un estado de propuesta distinto al flujo normal de aceptar/rechazar, pensado para autores invitados y editoriales, donde la confirmación es gradual y no tiene una fecha límite tan estricta (no hay cobro de por medio, por lo que no hay presión de "fecha límite de pago" como sí existe en stands).

**RFH-09 — Versión de trabajo iterable del programa**
El coordinador necesita poder armar y rearmar el acomodo del programa varias veces antes de considerarlo definitivo (mencionó explícitamente hacer una primera, segunda y tercera revisión). El sistema no debe forzar a publicar o notificar en cada ajuste intermedio — solo cuando el coordinador decida que esa versión ya está lista.

## Asignación de horario y salón

**RFH-10 — Catálogo administrable de salones y salas del Programa General** *(↔ RF-36)*
Debe existir un catálogo de salones/salas (nombre, capacidad, tipo de uso) administrable por el coordinador. Los nombres cambian cada edición (las salas se nombran cada año según una figura literaria/académica), así que no pueden quedar fijos en el código ni en datos semilla permanentes. **Confirmado con documentos reales:** la edición 2027 usa Salón Uxmal 3, Salón Uxmal 4 y Salón Dzibilchaltún (los "3 salones"), más Sala Fernando del Paso, Sala Fernando Espejo y Sala Antonia Jiménez Trava dentro del Salón Chichén Itzá (las "3 salas"); el programa 2026 además usa Uxmal 1 ("Gran Foro", 600 personas) y al menos una sala de cine — el catálogo no debe limitarse a 6 espacios fijos.

**RFH-10.1 — Catálogo de espacios compartido entre módulos**
El catálogo de salones de Hipólito debe ser consultable (no solo administrable por él) desde el módulo de Talleres/Escolar, ya que esa coordinación reserva espacios del Programa General (ej. Uxmal 1) cuando necesita audiencia para sus propios eventos (confirmado en `Software para agendar escuelas.docx`). No debe modelarse como un catálogo aislado.

**RFH-11 — Vista de calendario de disponibilidad** *(↔ RF-34)*
La asignación de horario/salón debe apoyarse en una vista tipo calendario (similar a Outlook/Google Calendar) que muestre qué bloques están libres y cuáles ocupados, para evitar duplicar horarios sin darse cuenta.

**RFH-12 — Bloques de horario configurables por tipo de actividad**
El sistema debe poder generar por defecto bloques de duración estándar (ej. 1 hora, con un colchón interno de ~15 minutos entre actividades) configurables, distintos para cada tipo de actividad (conferencias/mesas vs. presentaciones con firma vs. funciones de cine).

**RFH-13 — Soporte de actividades de duración no estándar / multi-bloque**
El coordinador debe poder asignar a una actividad una duración que ocupe más de un bloque estándar (ej. una firma de libro de 1.5–2 horas, o un congreso que reserva un bloque completo de varias horas) sin que el sistema pierda o rompa la información de horario/salón de esa actividad. Es el riesgo técnico que el propio Hipólito señaló de forma explícita.

**RFH-14 — Colchón/buffer configurable entre actividades**
El sistema debe permitir reservar un tiempo de transición entre actividades consecutivas en el mismo salón (hoy ~15 minutos) que no se publica en el programa pero sí bloquea ese tiempo para evitar choques de montaje/desmontaje.

**RFH-15 — Reserva de bloque extendido para eventos de varias sesiones**
Para congresos, coloquios o simposios que se manejan como un solo bloque grande (ej. de 9am a 2pm) con su propia sub-agenda interna, el sistema debe permitir reservar ese bloque como una sola unidad en el programa formal, sin necesidad de modelar el detalle interno de cada sub-sesión.

**RFH-16 — Distinción entre "programa formal" y "cartelera"**
El sistema debe poder marcar ciertas actividades como visibles únicamente en una "cartelera" informativa (listado más informal, sin el mismo nivel de detalle de horario exacto) en vez del programa formal con horario fijo — Hipólito ya hace esta distinción manualmente hoy para casos que no quiere comprometer a un horario exacto.

## Confirmación y cambios

**RFH-17 — Confirmación explícita del proponente con acuse de recibido** *(↔ RF-35)*
Una vez asignado horario/salón, el proponente debe recibir la asignación y confirmarla explícitamente en el sistema. Esto le da al coordinador evidencia de que la información fue comunicada y aceptada, ante posibles reclamos posteriores.

**RFH-18 — Ventana acotada de ajustes del programa (solo el coordinador)**
El coordinador dispone de un periodo configurable para hacer ajustes de horario, salón y, excepcionalmente, fecha (en ese último caso revisando con el involucrado). **Los proponentes no tienen opción de solicitar cambios de horario en el sistema** — solo pueden confirmar asistencia o indicar incomparecencia. Si un proponente necesita un ajuste, lo gestiona fuera del sistema (por correo u otro medio) y el coordinador es quien efectúa el cambio internamente. **Fechas oficiales confirmadas** (`Convocatoria para Actividades FILEY 2027.pdf`): aviso de propuestas seleccionadas el 13 de noviembre (con fecha de participación, aún sin hora/salón); ventana de ajustes del coordinador hasta el 7 de diciembre a las 16:00 horas; asignación de hora y sala/salón visible a partir del 22 de enero. *(Aclarado con Hipólito — 27-Jun-2026)*

**RFH-19 — Registro de excepciones de cambio de horario fuera de la ventana normal**
Para casos especiales (ej. una solicitud de alto nivel que llega fuera de la ventana de cambios), el sistema debe permitir que el coordinador haga el ajuste manualmente, pero dejando constancia de que fue un caso excepcional y quién lo autorizó.

**RFH-20 — Cierre definitivo de modificaciones**
A partir de una fecha límite configurable (oficialmente el 7 de diciembre a las 16:00 horas), el sistema debe impedir cualquier modificación adicional al programa ya confirmado, salvo por la vía de excepción de RFH-19. El envío de constancias de participación ocurre después, en una fecha separada (oficialmente el 26 de abril).

## Exportación y trabajo manual

**RFH-21 — Exportación editable del programa maestro**
El coordinador debe poder exportar el programa completo (o un subconjunto) a un formato editable (Excel, Word o PDF) para hacer ajustes manuales finales antes de entregarlo para aprobación. El sistema no debe ser una caja cerrada que impida este paso de "pulido final" que hoy es parte de su flujo de trabajo real.

**RFH-22 — Generación automática de ficha en PDF por actividad** *(↔ RF-42)*
El sistema debe poder generar en PDF la ficha de cada actividad programada (título, tipo, organiza, fecha, salón, horario), reemplazando la plantilla de Word con macro que usa actualmente.

**RFH-22.1 — Constancias de participación descargables**
El sistema debe permitir que cada proponente descargue su constancia de participación desde su cuenta, a partir de una fecha configurable posterior al cierre de la feria (oficialmente el 26 de abril). El propio documento oficial contempla un plan B: si esto resulta complicado de implementar, las constancias pueden enviarse por correo electrónico en su lugar — no es un requisito rígido.

## Publicación pública

**RFH-23 — Publicación progresiva del programa**
El sistema debe permitir publicar el programa de forma incremental, antes de tener el 100% de la información confirmada (ej. mostrar "propuesta aceptada, título por confirmar" y completarlo después), en vez de esperar a tener todo cerrado como ocurre hoy con el programa impreso.

**RFH-24 — Agenda pública filtrable por sección/categoría** *(↔ RF-46)*
Los visitantes deben poder navegar el programa filtrando por sección/categoría (ej. literatura, congresos, homenajes), siguiendo como referencia explícita la app de la FIL de Guadalajara que Hipólito mencionó.

**RFH-25 — Ficha de detalle con sinopsis (caso autores/libros)**
Para actividades de autor/presentación de libro, la ficha de detalle pública debe poder incluir sinopsis del libro y datos del autor, a diferencia del resto de actividades que solo requieren título, tipo y organizador.

**RFH-26 — Agendar / descartar actividades en agenda personal**
El visitante debe poder agregar una actividad a su agenda personal o descartarla (ícono de "basura"), y el sistema debe recordar esa selección si vuelve a entrar.

**RFH-27 — Generación automática de cartelera y señalización**
El sistema debe poder generar automáticamente el material de señalización/cartelera a partir de los datos ya cargados, sin depender de que un diseñador gráfico lo arme a mano cada vez (hoy es un cuello de botella real: solo tienen un diseñador para todo).

## Identidad, permisos y comunicación

**RFH-28 — Registro único de tipo "convocatoria FILEY" con bifurcación por tipo de actividad** *(↔ RF-28 / RF-32)*
El registro de un proponente debe iniciar con datos básicos comunes y luego mostrar solo los campos específicos según el tipo de actividad elegido — es la misma idea que propuso el propio Hipólito como su forma ideal de registro.

**RFH-29 — Permisos diferenciados: editor, colaborador y supervisor de solo lectura** *(↔ RF-31, con un matiz nuevo)*
El sistema debe distinguir al menos tres niveles de acceso sobre el Programa General: el coordinador (edita todo lo de su área), colaboradores que le ayudan a capturar/editar información (alcance limitado), y un rol de supervisor ("la maestra") que únicamente puede visualizar sin editar.

**RFH-30 — Notificaciones desde dominio institucional** *(↔ RF-44)*
Las notificaciones automáticas del Programa General deben enviarse desde una cuenta del dominio institucional (filey.org), independientemente de que el coordinador siga usando su correo personal para responder manualmente.

**RFH-31 — Registro interno no público para áreas sin convocatoria abierta** *(↔ RF-43)*
Actividades de coordinaciones que comparten espacio con el Programa General pero no tienen convocatoria pública (ej. arte visual) deben poder registrarse internamente, sin URL pública, solo para control y contabilidad.

## Hallazgos de los documentos reales (no estaban en el audio)

**RFH-32 — Catálogo de tipo de actividad extensible**
El campo "tipo de actividad" no debe ser una lista cerrada a los 8 tipos del formulario público. El programa impreso real usa además tipos curados internamente por FILEY-UADY sin pasar por convocatoria pública (Cuentacuentos, Plática, Curso, Multidisciplinario, Concierto). El sistema debe permitir que un administrador agregue actividades de cualquier tipo directamente, sin que pasen por el flujo de propuesta/revisión.

**RFH-33 — Lugar de una actividad puede ser un stand del módulo de Espacios**
Confirmado en el programa impreso 2026: algunas presentaciones de libro ocurren en el stand de una editorial ("Chichén Itzá, stand de Casa Editorial-UADY") en vez de en un salón del catálogo de Hipólito. El campo "lugar/salón" de una actividad debe poder referenciar también un stand del módulo de Espacios, no solo el catálogo propio de salones.

**RFH-34 — Estado de participación presencial del autor**
Para "Presentación de libro", el formulario real pide indicar explícitamente si el autor participará en la actividad (sí/no) y, si hay varios autores, cuáles sí estarán presentes. Es el campo concreto que sostiene el estado "en negociación" de RFH-08 — debe quedar como un dato propio de la propuesta, no solo como una nota libre.

**RFH-35 — Registro de envío de ejemplar físico**
Para presentaciones de libro/revista, el formulario real exige enviar un ejemplar físico a las oficinas de FILEY como requisito obligatorio. Es un paso fuera del sistema, pero el coordinador debe poder marcar en la propuesta si ya se recibió el ejemplar, ya que es una condición real para confirmar la actividad.

## No funcionales

**RNFH-01 — Fechas clave configurables específicas del Programa General** *(↔ RNF-15)*
Apertura/cierre de convocatoria, fecha límite de primeras respuestas, ventana de modificación y cierre definitivo deben ser fechas configurables por edición, independientes de las fechas de stands y de talleres/escolar. **Fechas oficiales de referencia (edición 2027):** 10 de agosto (lanzamiento), 2 de octubre 16:00 (cierre de convocatoria), 13 de noviembre (aviso de selección), 7 de diciembre 16:00 (cierre de ajustes), 22 de enero (asignación de hora/salón), 26 de abril (constancias) — no deben quedar fijas en código, cambian cada edición.

**RNFH-02 — Resiliencia ante actividades atípicas**
El sistema no debe perder, sobrescribir ni romper la asignación de horario/salón de una actividad cuando su duración no coincide con los bloques estándar configurados. Es un requisito de robustez señalado explícitamente como una preocupación real, no hipotética.

**RNFH-03 — Auditoría de cambios de horario excepcionales**
Todo cambio de horario hecho fuera de la ventana normal de modificaciones (RFH-19) debe quedar registrado con fecha, quién lo autorizó y motivo, para poder explicar después por qué una actividad se movió fuera del proceso estándar.

**RNFH-04 — Consistencia de identidad entre módulos** *(↔ RF-29)*
El sistema debe poder cruzar, por correo y/o teléfono, si una persona registrada en el Programa General también tiene actividad programada en el módulo de Talleres/Escolar, para detectar conflictos de horario entre ambos módulos antes de que ocurran.

---

## Tabla de equivalencia con el documento maestro

Para cuando se integre esta parte al documento general (`docs/requisitos_ideas.md`):

| Este documento                                | Documento maestro | Relación                                                                                                                                                               |
| --------------------------------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RFH-01 a RFH-04                               | RF-32             | Esta versión es más granular (separa convocatoria, formulario, adjuntos y concentrado en piezas independientes)                                                       |
| RFH-05 a RFH-09                               | RF-33             | Agrega el matiz de aceptación en dos fases y el estado especial de autores, no capturado antes                                                                         |
| RFH-10                                        | RF-36             | Equivalente directo                                                                                                                                                     |
| RFH-11 a RFH-16                               | RF-34             | Esta versión agrega manejo de duración no estándar, colchones y distinción cartelera/programa formal                                                                |
| RFH-17 a RFH-20                               | RF-35             | Agrega el matiz de excepciones registradas y cierre definitivo con fecha dura                                                                                           |
| RFH-21, RFH-22                                | RF-42             | RFH-21 (exportación editable) es nuevo, no estaba capturado antes                                                                                                      |
| RFH-23 a RFH-27                               | RF-45, RF-46      | Agrega publicación progresiva y ficha con sinopsis, no capturados antes                                                                                                |
| RFH-28                                        | RF-28             | Equivalente directo, confirmado independientemente por Hipólito                                                                                                        |
| RFH-29                                        | RF-31             | Agrega el rol explícito de "solo lectura" para supervisor                                                                                                              |
| RFH-30                                        | RF-44             | Equivalente directo                                                                                                                                                     |
| RFH-31                                        | RF-43             | Equivalente directo                                                                                                                                                     |
| RNFH-01                                       | RNF-15            | Equivalente directo                                                                                                                                                     |
| RNFH-02, RNFH-03                              | —                | Nuevos, no estaban capturados en el documento maestro                                                                                                                   |
| RNFH-04                                       | RF-29             | Equivalente directo                                                                                                                                                     |
| RFH-04.1, RFH-10.1, RFH-32 a RFH-35, RFH-22.1 | —                | Nuevos, detectados al revisar los documentos reales de la feria (ver `docs/resumen_archivos_contexto_exterior.md`), no estaban en el audio ni en el documento maestro |
