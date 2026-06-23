# Resumen de la reunión interna — 18 de junio de 2026

> Fuente: `archivos_de_contexto_exterior/FILEP app.docx`
> Grabación: 2 horas 15 minutos (Teams, transcripción automática)
> Tipo: Revisión interna del equipo de desarrollo — cada desarrollador presenta su avance de análisis

---

## ¿Quiénes participan?

| Persona | Rol en el proyecto |
|---|---|
| **Edgar Cambranes Martinez** | Líder técnico / asesor |
| **Hugo Janssen Aguilar** | Módulo de stands y reservaciones |
| **Juan Manuel Hernandez Miranda** | Módulo de programa general (eventos para público) |
| **Isaac Alejandro Ortiz Zaldivar** | Módulo de actividades infantiles/juveniles |

Hipólito y Elvira **no están presentes** — es una reunión interna del equipo de desarrollo.

---

## Parte 1 — Hugo presenta: Módulo de Stands y Reservaciones

Hugo presentó sus **casos de uso ya documentados**. Los puntos más relevantes discutidos:

### Notificaciones y cancelaciones
- El sistema enviará notificaciones automáticas X días antes del vencimiento de una reserva. El número de días es **configurable** (se acordó usar días naturales, no hábiles).
- La **cancelación NO es automática** — el sistema solo notifica. Hipólito tiene la última palabra sobre si cancela o prorroga. Objetivo: mantener la venta de espacios al máximo posible.
- Se propuso una "bandeja de pagos atrasados" donde Hipólito puede decidir prorroga o cancelación directamente.

### Registro de pagos
- El expositor sube su comprobante + captura **monto, fecha y cuenta bancaria** (4 datos: los 3 anteriores + el comprobante adjunto).
- El admin valida y aplica el abono. El expositor puede editar si capturó mal el monto.
- Se busca trazabilidad contable: el contador puede verificar movimientos con esos 3 datos.
- El admin también puede hacer **abonos manuales** con documento adjunto (para donaciones u otras situaciones).

### Descuentos
- Un **único campo de descuento global** por reserva. No hay catálogo de descuentos.
- **Pronto pago (10%)**: automático, con fecha límite configurable. Cuando pasa la fecha, el descuento global se reduce.
- **Local (15%)**: manual, Hipólito lo activa a discreción según documentación del expositor.
- **¿Se acumulan?** Hipólito y el contador tenían posiciones contrarias — **queda pendiente confirmarlo**.
- Descuentos especiales (negociaciones específicas): se aplican manualmente al campo global, sin catálogo.

### Flujo de reserva
- La reserva dura **30 días** en espera del 50% de abono inicial.
- Si vence sin abono: Hipólito recibe notificación y decide manualmente.
- Una vez cubierto el 50%: la reserva se confirma y bloquea (estado "bloqueado/confirmado").
- Al cubrir el 100%: notificación final.

### Sellos editoriales
- Un sello editorial es la marca comercial bajo la cual una compañía publica libros (ej. Penguin Random House tiene Alfaguara, Grijalbo, Random House, etc.).
- Se incluirán como entidad en el sistema: cada editorial puede tener múltiples sellos.

### Mapa de stands
- Vista completa con todos los espacios y sus estados.
- La **edición de espacios en el mapa** queda como tarea futura no comprometida para esta fase.

---

## Parte 2 — Juan Manuel presenta: Módulo de Programa General

Juan Manuel presentó un **listado de requisitos** para el programa de eventos del público general:

### Convocatoria y propuestas
- **Apertura de convocatoria**: el sistema abre el periodo para que proponentes envíen sus actividades.
- **Formulario de propuesta**: múltiples tipos de actividades, cada uno con campos diferentes (presentación de libro, conferencia, taller, conversatorio, encuentro). El tipo "encuentro" no quedó completamente definido en los documentos revisados.
- **Semblanzas**: se acordó capturarlas como **texto en el sistema** (no PDF), para facilitar administración posterior y evitar tener que extraer texto de archivos.
- **Sinopsis**: igual, como texto. Más fácil de administrar que un adjunto.

### Revisión y selección
- Hipólito **revisa al cierre del periodo** de convocatoria, no de manera incremental antes. (Esto fue aclarado por Edgar — no hubo mención de revisiones parciales antes del deadline.)
- La asignación de horario es una **segunda fase**, después de la aceptación.

### Cartelera
- La cartelera son los eventos "externos" alrededor de Filey que no forman parte del programa formal.
- Hoy Hipólito los recibe por correo y los agrega manualmente al documento impreso.
- **Pendiente**: definir exactamente qué datos necesita la cartelera. ¿Son los mismos campos que una actividad del programa formal? ¿Cómo se distinguen en el sistema?
- Por ahora no hay formato establecido — habría que preguntarle a Hipólito.

### Confirmación del proponente
- El proponente recibe su asignación de horario y debe confirmarlo.
- Mecanismo propuesto: correo con **botones/links** de "acepto / no acepto" que llevan al sistema.
- Esto protege a Hipólito: si después hay reclamo, tiene evidencia de que fue notificado y confirmó.

### Modificaciones
- Se hacen **por fuera del sistema** (el proponente manda un correo a Hipólito). Hipólito decide.
- Hay una **fecha límite de cambios** (alrededor del 7 de diciembre según documentos oficiales).
- Hipólito puede hacer cambios excepcionales después de esa fecha, pero deben quedar registrados.

### Constancias de participación
- Posiblemente incluidas en el sistema. Requiere una **plantilla** para generarlas.
- Para actividades **individuales**: sencillo, una constancia por persona.
- Para actividades **grupales**: ¿una constancia por institución o por cada participante? No quedó claro. Va a las preguntas pendientes.

### Publicación del programa
- Por ahora solo **interna** (no pública hacia el público general).
- Herramienta para que el personal de la feria consulte en tablets/pantallas sin imprimir. La directora también puede verlo.
- Hacerlo externo (público para visitantes) requiere más trabajo — no se compromete para esta fase.

### Observaciones de Edgar sobre el trabajo de Juan Manuel
- Necesita homologar el **formato** de sus documentos con el de Hugo (índice de casos de uso numerados).
- Su descripción de "catálogo de espacios compartido entre módulos" era una referencia técnica interna (módulo de Juan Manuel + módulo de Isaac comparten salas) — hay que redactarlo de forma más clara para el cliente.
- Lo que tiene es un buen boceto; necesita explayarlo más con la plantilla de casos de uso.

---

## Parte 3 — Isaac presenta: Módulo de Actividades Infantiles/Juveniles y Talleres

Isaac presentó los **requisitos del módulo de Elvira**:

### Registro de talleristas
- El tallerista se registra con sus **datos de contacto + información del taller propuesto** en un solo formulario.
- Pendiente: definir mejor si los diferentes tipos de taller (salones de Ek Balam, sala de cine, etc.) tienen campos distintos entre sí.
- La relación con un "registro base de usuario" (correo + teléfono) quedó sin decidir explícitamente por ahora — se dejó desacoplado.

### Actualización de propuesta de taller
- Elvira puede solicitar correcciones al tallerista antes de aprobarlo.
- La persona puede editar su propuesta solo **antes de ser aprobada** y mientras la convocatoria esté abierta.
- Elvira revisa al **cierre del deadline** (no de forma incremental antes). Igual que Hipólito.

### Registro de visita escolar
- Las escuelas registran su visita: número de alumnos, nivel educativo, días que asistirán.
- Es mucho más complejo que un simple registro de "voy a ir" — cada escuela **planifica su agenda** eligiendo del catálogo de actividades disponibles.
- El sistema sugiere actividades disponibles según el día y el aforo restante.
- Pendiente: completar bien este flujo, que es el más complejo del módulo.

### Organización de talleres aprobados (Elvira)
- Vista tipo **línea de tiempo** (calendario): Elvira asigna cada taller aprobado a un espacio y horario.
- Bloques de **50 minutos + 15 de descanso** entre actividades (parametrizable).
- Aforo máximo: **105 personas** por sala (Ek Balam). El sistema muestra aforo total y restante.
- Al interactuar con un bloque en el calendario, se ven las propiedades del taller (sala, nombre, aforo).

### Cine
- Las salas de cine funcionan **solo en las mañanas**; por las tardes se usan para el programa general.
- Los registros de cine llegan a través de Hipólito, pero se coordinan hacia Elvira.
- Isaac tiene contemplado un campo de "horarios de disponibilidad" para los espacios de cine.

### Salas compartidas
- Hipólito y Elvira usan espacios **distintos en su mayoría**, pero hay casos de solapamiento (cine, Ek Balam para algún evento especial).
- Coordinan internamente. El sistema no necesita forzar una validación automática de conflictos entre módulos, pero sí debe mostrar disponibilidad compartida.

### Observaciones de Edgar sobre el trabajo de Isaac
- Necesita homologar formato con Juan Manuel.
- El requisito de "actualizar visita escolar" probablemente sobra en esta fase — primero hay que completar el registro.
- El módulo de visita escolar es mucho más complejo de lo que estaba descrito — hay que desarrollarlo mejor.

---

## Parte 4 — Decisión arquitectónica final

Al final, Edgar propuso una **organización por 3 cores** compartidos entre todos los módulos:

### Los 3 cores
| Core | Qué incluye |
|---|---|
| **1. Registros** | Todos los formularios de solicitud: stand, evento del programa general, taller, visita escolar |
| **2. Programas** | Creación y gestión del calendario: programa general (Hipólito) e infantil-juvenil (Elvira) |
| **3. Salas/Salones** | Catálogo único compartido de espacios físicos (Hipólito + Elvira lo administran conjuntamente) |

### Por qué esto importa
- **Un taller es un tipo de evento**: el core de registro de eventos debe ser el mismo para Juan Manuel e Isaac. Solo cambia la categoría y quién lo administra.
- **El programa general y el de talleres/escolar son paralelos**: misma lógica, distinto público objetivo.
- **Las salas son un recurso compartido**: un único catálogo evita duplicación y permite detectar conflictos de espacio entre módulos.

### Cita clave de Edgar
> *"El core de la recepción de eventos... un taller es un tipo de evento. Entonces pueden agregar una categoría especial de taller para taller infantil juvenil."*

### Acuerdo final
- Isaac y Juan Manuel deben **revisar el trabajo del otro** y homologar formato (tarea offline, antes del lunes).
- La reunión del **lunes 22 de junio a las 9am en Femat** será en pizarra para:
  - Consolidar la lista total de requisitos de los 3 módulos.
  - Priorizar: qué va para agosto y qué queda para después.
  - Estimar bloques de entrega.
