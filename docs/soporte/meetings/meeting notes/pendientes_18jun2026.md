# Pendientes y próximos pasos — Reunión 18 de junio de 2026

> Derivado de: `archivos_de_contexto_exterior/FILEP app.docx`

---

## Preguntas que quedaron sin respuesta

### Para preguntarle a Hipólito (pueden mandarse por mensaje)

**1. ¿Se acumulan los descuentos de pronto pago y local?**

- Hipólito y el contador tenían posiciones contrarias en una reunión anterior.
- El contador quería que se acumulen; Hipólito no estaba seguro.
- Impacto: si se acumulan, el sistema debe aplicar pronto pago (10%) + local (15%) = 25% total. Si no, debe aplicar solo uno u otro.
- *Responsable de preguntar: Edgar o Isaac.*

**2. ¿Qué datos necesita la cartelera?**

- La cartelera son los eventos externos alrededor de Filey (no el programa formal).
- Hoy Hipólito los recibe por correo y los agrega manualmente al impreso.
- No hay un formato definido. ¿Usa los mismos campos que una actividad del programa general? ¿O tiene su propio formulario más sencillo?
- *Responsable de preguntar: Juan Manuel.*

**3. ¿Cuáles son exactamente los tipos de actividad del programa general?**

- Los documentos oficiales mencionan 8 tipos formales: Conversatorio, Conferencia, Charla, Mesa redonda, Presentación de libro, Presentación de revista, Lectura de obra, Encuentro.
- El tipo "Encuentro" no quedó completamente claro en los documentos revisados — ¿cuál es su formulario específico?
- Además, el programa impreso real usa tipos que no están en el formulario (Cuentacuentos, Plática, Curso, Concierto) — ¿el sistema debe permitir agregar tipos de forma abierta?
- *Responsable de preguntar: Juan Manuel.*

**4. ¿Cómo funciona el campo de autor en Presentación de libro?**

- El formulario real pide indicar si el autor participará (sí/no), y si hay varios autores, cuáles sí estarán presentes.
- ¿Cómo se maneja si hay hasta 5 autores distintos para un mismo libro?
- *Responsable de preguntar: Juan Manuel.*

**5. ¿El lugar de una actividad puede ser un stand?**

- En el programa impreso 2026 hay actividades que ocurren en stands de editoriales (ej. "stand de Casa Editorial-UADY").
- ¿Esto sigue siendo el caso en 2027? Si sí, el campo "lugar" debe poder apuntar tanto a un salón del catálogo como a un stand del módulo de espacios.
- *Responsable de preguntar: Juan Manuel.*

---

### Para resolver entre Juan Manuel e Isaac (trabajo offline)

**6. ¿Qué campos del formulario de evento son comunes y cuáles son específicos por módulo?**

- Se acordó que el core de registro de eventos es compartido.
- Necesitan sentarse a definir exactamente qué va en el formulario base y qué se bifurca por tipo/categoría.

**7. ¿Un único catálogo de salas o separado por módulo?**

- Edgar propuso un único catálogo compartido entre Hipólito y Elvira.
- Necesitan confirmar internamente cómo lo van a modelar: ¿una sola tabla de espacios con un campo de "módulo" o tablas separadas?

---

### Para resolver internamente (equipo de desarrollo)

**8. ¿Qué pasa cuando una escuela se registra varias veces con personas distintas para meter más alumnos?**

- Este problema fue identificado en la reunión de programa académico/escolar anterior.
- No hay una solución decidida. ¿Se valida por clave de centro de trabajo (CCT)? ¿Por nombre de institución? ¿Se limita el aforo por institución?

**9. ¿Cómo se manejan las constancias de participación para actividades grupales?**

- Para actividades individuales es simple: una constancia por persona.
- Para actividades grupales (mesas redondas, congresos): ¿una constancia por institución o por cada participante?
- ¿Quién captura los nombres de los participantes individuales si hay más de uno?

**10. ¿El registro de actualización de propuesta de taller (editar después de enviada) va en esta fase?**

- Isaac lo tenía en sus requisitos, pero Edgar lo cuestionó.
- Hay que decidir si se incluye o se deja para una fase posterior.

---

## Tareas del equipo antes del lunes 22 de junio

### Tarea de Isaac

- [ ] Revisar el trabajo de Juan Manuel y entender cómo sus módulos se solapan.
- [ ] Reorganizar sus requisitos alrededor de los 3 cores (Registros / Programas / Salas).
- [ ] Homologar el formato de sus documentos con el estilo de Hugo (índice de casos de uso numerados).
- [ ] Desarrollar mejor el flujo completo de **visita escolar** — es el punto más incompleto.

### Tarea de Juan Manuel

- [ ] Revisar el trabajo de Isaac y entender cómo sus módulos se solapan.
- [ ] Reorganizar sus requisitos alrededor de los 3 cores (Registros / Programas / Salas).
- [ ] Homologar el formato con el estilo de Hugo.
- [ ] Preparar preguntas específicas sobre la cartelera y los tipos de actividad para hacerle a Hipólito.

### Tarea de Hugo

- [ ] Revisar si en la sección de administración tiene contemplado el catálogo de stands para que Isaac y Juan Manuel lo puedan referenciar.
- [ ] Dar a conocer a los demás cómo organizó sus casos de uso para que lo repliquen.

---

## Reunión del lunes 22 de junio de 2026

- **Hora**: 9:00 am
- **Lugar**: Femat (presencial, en pizarra)
- **Objetivo**:
  1. Consolidar la lista total de requisitos de los 3 módulos.
  2. Hacer una priorización: qué va para agosto (entrega al cliente) y qué queda para después.
  3. Definir bloques de entrega (A, B, C...) con estimaciones de tiempo.
  4. Edgar quería tener ya "un oráculo que nos diga si nos va a alcanzar la vida" — es decir, un conteo de requisitos y una priorización clara.

---

## Contexto importante para el lunes

Edgar señaló esto al final de la reunión:

> *"La cantidad de requisitos es considerable... no todos los necesitamos para agosto. Entonces si necesitamos ahí planear. Si los manejamos por bloques lo más similares posibles, no tenemos que explicarle mucho al cliente. Tenemos que presentarle a FILEY: mira, así lo vamos a organizar, esto vamos a liberar ahora, y esto en este momento, y todo esto nos va a llevar los próximos 5 o 6 meses."*

Esto significa que la reunión del lunes no es para seguir levantando requisitos — es para **priorizar y estimar**, con la lista ya (razonablemente) completa en mano.


## pendientes de la parte de los cores

1. publicoObjetivoContenidos está vacío — hay que preguntarle a Hipólito cuáles son las opciones (o si es texto libre).
2. visitaEscolar es especulativo — no hay formulario real confirmado con Elvira. Antes de modelarlo en BD hay que validarlo.
3. Faltan los CUs de visitaEscolar — no están en el MD. Hay que agregarlos (probablemente como dominio VIS con sus propios CUs).
4. El core de programacion está pendiente — solo tiene andamiaje. Los CUs de asignación de horario, vista de calendario, exportación, etc. no existen todavía.
5. El CRUD de salas/salones está pendiente — solo declarado, sin detalle.
6. Faltan CUs para la fase de confirmación — CU-EVT-002 cubre "editar dentro de la ventana", pero no hay CU para "confirmar que recibí mi asignación de horario" (el acuse de recibo que Hipólito necesita para deslinde). Eso
   pertenecería al core de programacion.
