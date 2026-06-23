# Análisis de eventos: Juan Manuel + Isaac y su conexión

> Basado en la reunión del 18 de junio de 2026 (`archivos_de_contexto_exterior/FILEP app.docx`)
> Complementa lo ya documentado en `info_hipolito_eventos.md` y `resumen_programa_academico.md`

---

## Por qué Juan Manuel e Isaac están en la misma sección

Edgar lo dijo explícitamente al cierre de la reunión:

> *"Un taller es un tipo de evento. Particularmente en el caso tuyo, Isaac, y el de Juan Manuel, tendrían que estar más coordinados."*

Aunque son módulos distintos (programa general vs. actividades infantiles/juveniles), **comparten la misma arquitectura de fondo**: convocatoria → revisión → asignación → confirmación. La diferencia es el público y el administrador, no el flujo.

---

## Juan Manuel Hernandez Miranda — Programa General (eventos para el público)

### ¿Qué construye Juan Manuel?

El **Programa General** de FILEY: todos los eventos culturales y académicos dirigidos al público en general. Esto incluye presentaciones de libro, conferencias, conversatorios, mesas redondas, charlas, lecturas de obra, y encuentros. También incluye la "cartelera" — eventos externos alrededor de la feria que no son programa formal.

### Su aportación en la reunión

Juan Manuel presentó un **listado de requisitos** (no casos de uso al estilo Hugo, sino requisitos más lineales). Lo que mostró:

1. **Convocatoria pública** con flujo desde apertura hasta aceptación/rechazo.
2. **Formulario con múltiples tipos de actividad** — cada tipo tiene campos diferentes.
3. **Revisión y selección**: Hipólito acepta/rechaza. Se confirma que revisa al cierre del deadline, no incremental.
4. **Asignación de horario**: segunda fase, después de la aceptación.
5. **Catálogo de salas compartido**: Juan Manuel lo llamó "catálogo de espacios compartido entre módulos" — Edgar aclaró que eso es una referencia técnica interna (los módulos de Juan Manuel e Isaac comparten las salas), no el lenguaje que debe usarse hacia el cliente.
6. **Vista de calendario** con bloques configurables por tipo de actividad.
7. **Cartelera**: eventos externos alrededor de la feria, sin formato definido aún.
8. **Confirmación explícita del proponente**: correo con links de acepto/rechazo → llegan al sistema.
9. **Ventana acotada de cambios**: hasta fecha límite (7 de diciembre oficialmente).
10. **Constancias de participación**: para ponentes que necesitan justificar ante su institución. La parte de actividades grupales quedó sin resolver.
11. **Publicación del programa**: por ahora interna (para personal de la feria, no pública hacia visitantes).

### Lo que Edgar le señaló específicamente

- Necesita homologar el **formato** con Hugo: hacer un índice de casos de uso numerados, no solo un listado de requisitos.
- El término "módulos" en su documento era jerga técnica — al cliente hay que hablarle de "programa general" y "programa infantil/juvenil".
- La cartelera necesita que le pregunten a Hipólito qué datos requiere.
- Las constancias de participación para actividades grupales son un punto pendiente que hay que definir.

### Su relación con "eventos"

Juan Manuel **ES** el módulo de eventos en el sentido más directo. Sus actividades son los eventos del programa general. Lo que construye es:

- El flujo de **recepción de propuestas** de eventos (la convocatoria).
- El flujo de **revisión y aprobación** (por parte de Hipólito).
- La **asignación de horario y salón** a cada evento aprobado.
- La **confirmación y notificación** al proponente.
- La **publicación del programa** (interna por ahora).

El "evento" en su módulo tiene estas características:
- No cobra (a diferencia de los stands).
- Tiene un proponente que lo propone, y Hipólito lo acepta o rechaza.
- Una vez aceptado, se le asigna horario y sala.
- El proponente confirma la asignación.
- Puede solicitar cambios en una ventana acotada.

---

## Isaac Alejandro Ortiz Zaldivar — Actividades Infantiles/Juveniles y Talleres

### ¿Qué construye Isaac?

El módulo de **actividades infantiles y juveniles**: talleres impartidos por talleristas, y la gestión de visitas escolares. Lo administra **Elvira** (no Hipólito). También incluye las salas de cine (solo por las mañanas, dirigidas a escuelas).

### Su aportación en la reunión

Isaac presentó sus **requisitos** en el mismo formato que Juan Manuel (listado, no casos de uso al estilo Hugo). Lo que mostró:

1. **Registro de talleristas**: formulario con datos del tallerista + información del taller propuesto. En un solo formulario por ahora.
2. **Actualización de propuesta de taller**: el tallerista puede editar su propuesta antes de ser aprobado, mientras la convocatoria esté abierta. Elvira puede solicitar correcciones.
3. **Registro de visita escolar**: mucho más complejo de lo que el requisito describía. La escuela no solo dice "voy a ir" — planifica su agenda completa eligiendo del catálogo de talleres disponibles.
4. **Organización de talleres aprobados**: Elvira asigna espacios y horarios. Bloques de 50 minutos + 15 de descanso. Vista tipo línea de tiempo.
5. **Aforo**: máximo 105 personas por sala (Ek Balam). Elvira puede dividir grupos o completar aforos con otras escuelas.
6. **Cine**: disponible solo en las mañanas. Campo de "horarios de disponibilidad" para controlar esto.
7. **Salas compartidas**: Hipólito y Elvira coordinan internamente. El sistema debe mostrar disponibilidad compartida.

### Lo que Edgar le señaló específicamente

- El requisito de "actualizar registro de visita escolar" probablemente sobra en esta fase — primero hay que completar bien el **registro** de visita escolar.
- El módulo de visita escolar es **mucho más complejo** de lo que estaba descrito: no es solo "registro de la escuela", es "la escuela planifica su visita eligiendo actividades del catálogo". Hay que desarrollarlo mejor.
- Necesita homologar formato con Juan Manuel.

### La conexión clave de Isaac con eventos

El punto más importante de la reunión respecto a Isaac: **sus talleres son eventos**. Esto tiene consecuencias prácticas:

1. **El core de registro de eventos debe ser el mismo** para Juan Manuel e Isaac. Solo cambia la categoría (programa general vs. infantil/juvenil) y el administrador (Hipólito vs. Elvira).

2. **Algunas actividades del programa general de Hipólito pueden ser apropiadas para escuelas**. Hipólito puede marcar una actividad con una casilla de "para infantil también", y esa actividad aparece en el catálogo que consultan las escuelas al planificar su visita.

3. **El cine es un caso de solapamiento**: las salas de cine están a cargo de Elvira (mañanas para escuelas), pero el contenido llega a través de otros canales. El sistema necesita manejar la disponibilidad diferenciada por horario.

4. **Conflicto de agenda entre módulos**: un mismo tallerista podría estar programado en el módulo de Hipólito y en el de Elvira al mismo tiempo. El sistema debería detectarlo cruzando correo/teléfono como identificador.

---

## La diferencia entre los dos módulos (y por qué sí importa)

Aunque comparten arquitectura, hay diferencias reales:

| Aspecto | Juan Manuel (Programa General) | Isaac (Infantiles/Juveniles) |
|---|---|---|
| Administrador | Hipólito | Elvira |
| Público objetivo | Adultos, público general | Escuelas, niños y jóvenes |
| ¿Hay visita escolar? | No | Sí (es su proceso más complejo) |
| Convocatoria cierra | 2 de octubre | ~10-15 días antes de la feria |
| Espacios | Salones del programa general | Ek Balam + cine (mañanas) |
| Aforo típico | Varía (hasta 600 en gran foro) | Máx 105 por sala (Ek Balam) |
| Bloques de tiempo | 50 min estándar, flexibles | 50 min + 15 de descanso |

---

## Cómo se relaciona todo con los "eventos"

El término **"evento"** en FILEY funciona como paraguas que cubre:

| Tipo | Módulo | Quién lo propone | Quién lo aprueba |
|---|---|---|---|
| Conferencia, charla, mesa redonda | Juan Manuel | Proponente externo | Hipólito |
| Presentación de libro | Juan Manuel | Autor / editorial | Hipólito |
| Conversatorio, lectura de obra, encuentro | Juan Manuel | Proponente externo | Hipólito |
| Cartelera (eventos externos) | Juan Manuel | Se reciben por correo | Hipólito los captura |
| Taller infantil/juvenil | Isaac | Tallerista | Elvira |
| Visita escolar | Isaac | Institución educativa | Elvira (agenda, no aprueba) |
| Funciones de cine (mañanas) | Isaac | Canal externo | Elvira |

Todos comparten el mismo patrón de fondo. La diferencia es operativa, no arquitectónica.

---

## El core compartido de eventos

Edgar propuso que Juan Manuel e Isaac deben coordinar su trabajo alrededor de un **core de registro de eventos** común. Este core tendría:

- Un formulario base con campos comunes (nombre del evento, tipo, datos del proponente, adjuntos).
- **Bifurcación por tipo** de evento: según el tipo elegido, se muestran campos adicionales específicos.
- Un motor de estados compartido: recibido → en revisión → aceptado/rechazado → con horario → confirmado.
- Notificaciones automáticas por cada cambio de estado.
- La categoría de evento determina a quién le llega para revisión (Hipólito vs. Elvira).

Esto evita que Juan Manuel e Isaac construyan dos flujos paralelos que hacen lo mismo con código duplicado.

---

## Lo que Juan Manuel debe hacer diferente a lo que tiene

1. **Reorganizar sus requisitos** alrededor de los 3 cores (Registros / Programas / Salas), no como una lista lineal.
2. **Definir los campos exactos** de cada tipo de formulario de propuesta (actualmente solo tiene descripciones generales).
3. **Confirmar con Hipólito** qué datos necesita la cartelera y si es el mismo formulario que el programa formal o uno diferente.
4. **Resolver las constancias de participación** para actividades grupales.
5. **Homologar el formato** con el estilo de Hugo: índice de casos de uso numerados.

## Lo que Isaac debe hacer diferente a lo que tiene

1. **Desarrollar mejor el flujo de visita escolar** — es su proceso más complejo y está insuficientemente descrito.
2. **Coordinar con Juan Manuel** qué parte del core de eventos es compartida y cuál es específica de talleres.
3. **Decidir si la actualización de propuesta** (después de enviada) es necesaria en esta fase o se deja para después.
4. **Reorganizar sus requisitos** alrededor de los 3 cores.
5. **Homologar el formato** con Hugo.
