# Análisis a fondo — La parte de Hipólito (Programa General / Eventos)

## 1. ¿Qué es exactamente "la parte de Hipólito"?

Hipólito es quien administra lo que él mismo llama el **"Programa Maestro"**: el programa general de actividades de FILEY que **no** son ni stands ni talleres infantiles/visitas escolares. Concretamente:

- **Conferencias** (charla individual)
- **Mesas** (panel, normalmente ~4 ponentes + 1 moderador, con título de sesión y título de cada ponencia)
- **Congresos, coloquios y simposios** (eventos de varias sesiones, a veces de varios días, organizados internamente por el grupo que los propone)
- **Presentaciones de libro** y **firmas de autor** (necesitan más tiempo del bloque normal — 1.5 a 2 horas — porque conviene mantener al público dentro del salón en vez de dejarlo salir a pasillo)
- **Autores invitados** (un sub-caso especial: su espacio y logística se negocian aparte y no se "confirman" públicamente hasta que cierra la negociación, normalmente en diciembre/enero)
- **Eventos masivos** (los que esperan mucho público — su asistencia real a veces sorprende, para bien o para mal)

Y, sobre esa base de actividades, dos responsabilidades adicionales que se mencionan explícitamente:

- **Administrar el catálogo físico de salones y salas** que usa su programa (y, de forma más general, tiene visión de cómo se reparte el venue completo entre su programa, el de talleres/escolar y cine).
- **Publicar la cara pública del programa** hacia los visitantes (el "programa impreso" hoy, y a futuro algo como la app de la FIL de Guadalajara que él mismo describió como referencia).

Él mismo, casi al cierre de la reunión, resume la división del proyecto exactamente como la planteas tú: *"dividimos los [módulos]... lo que es etapa de expositores, [lo que] es mapa de actividades, lo que es aparte de talleres"* — es decir, **Hipólito mismo confirma que el proyecto tiene tres frentes**: Espacios/Stands, su Programa General ("mapa de actividades"), y Talleres/Escolar. Tu intuición de que son tres partes principales no es una simplificación tuya — es literalmente cómo el responsable de la feria divide el trabajo.

## 2. Por qué esta es, probablemente, la parte más compleja de las tres

No por volumen de pantallas, sino porque mezcla **cuatro problemas distintos a la vez**, mientras que stands y talleres resuelven básicamente uno o dos cada uno:

1. **Un proceso de convocatoria y selección** (como talleres: recibir propuestas, aceptar/rechazar, notificar).
2. **Una capa de programación con restricciones físicas reales** (salones con capacidad fija, ztándar) — esto es más parecido a *gestión de calendario* que a un simple catálogo con estado (blanco/verde/azul como en stands).
3. **Un sub-caso de "clientes especiales" sin convocatoria formal** (autores/editoriales), con su propio ritmo de confirmación, sin presión de fecha porque no hay cobro de por medio.
4. **Una cara pública orientada a *consumo*, no a registro** (el visitante que solo quiere ver qué hay y armar su agenda) — algo que ni stands ni talleres necesitan resolver con esa profundidad, porque sus usuarios siempre son gente que se registra para algo concreto (comprar un stand, agendar una visita escolar), mientras que el "asistente general" de Hipólito solo quiere explorar y planear, sin registrarse a nada.

Por eso vale la pena que la abordes con la cabeza de "estoy construyendo un mini sistema de calendario con flujo de aprobación + un portal de descubrimiento", no como "una convocatoria más".

## 3. El ciclo de vida completo, explicado paso a paso

Esto es lo que se puede reconstruir, con bastante consistencia, de los 205 turnos de Hipólito:

```
1. CONVOCATORIA ABIERTA
   └─ Se abre con fecha configurable (este año ~mediados de agosto, según él).
   └─ Formulario: datos del proponente, tipo de actividad, adjuntos (PDF/imagen),
      puede meter varias propuestas mientras la convocatoria esté abierta.

2. RECEPCIÓN Y CONCENTRADO
   └─ Las propuestas caen en un concentrado (hoy: Excel autogenerado por el
      formulario + columnas que él agrega a mano: aceptada/rechazada, fecha).
   └─ Hipólito revisa de forma INCREMENTAL conforme van llegando, no todas
      al final ("la primera semana llegan 30, ya empiezo a hacer una primera
      selección").
   └─ Mientras revisa, necesita ver EN VIVO cuántos espacios le quedan
      disponibles (tiene un total fijo de espacios/horarios y un número de
      propuestas que normalmente supera ese total — ej. "tengo 150 espacios,
      me llegan 300").

3. PRIMERA DECISIÓN: ACEPTAR / RECHAZAR (sin horario todavía)
   └─ Fecha límite para tener TODAS las respuestas listas: ~6 de octubre.
   └─ Al aceptar: notificación automática (sistema + correo) de que la
      propuesta fue aceptada, PERO sin asignar todavía fecha/salón/hora.
      Esto es deliberado: le da margen para mover piezas después.
   └─ Al rechazar: notificación automática también.
   └─ Caso especial: AUTORES/EDITORIALES no siguen este mismo ritmo — su
      confirmación es gradual y se cierra hasta diciembre/enero porque no
      hay cobro de por medio y la negociación de logística toma más tiempo.

4. CONSTRUCCIÓN DEL PROGRAMA MAESTRO (asignación de horario y salón, este programa se podria hacer con un calendario interactivo)
   └─ Trabaja por iteraciones: primera versión completa del acomodo,
      la revisa ("no me convence"), segunda versión, tercera versión ya
      son solo detalles menores.
   └─ Usa bloques de referencia (~1 hora + ~15 min de colchón interno no
      publicado) pero NECESITA poder salirse de esos bloques para casos
      reales: firmas de libro (1.5–2h), congresos que piden el día completo
      (9am–2pm como un solo bloque), eventos de cine (1–2h según función).
   └─ Pidió explícitamente que el sistema no se "rompa" si una actividad
      ocupa más de una casilla de horario — quiere la flexibilidad de los
      bloques por defecto SIN perder la posibilidad de salirse de ellos.

5. SEGUNDA NOTIFICACIÓN: ASIGNACIÓN DE HORARIO + CONFIRMACIÓN
   └─ Una vez que decide fecha/salón/hora, el proponente recibe la
      asignación y debe CONFIRMAR explícitamente ("que confirmen de
      recibido") — esto lo protege a él: si después hay un reclamo,
      tiene evidencia de que se le notificó y confirmó.
   └─ Ventana acotada para solicitar cambios: del 3 al 30 de noviembre.
      Pasada esa fecha, ya no se aceptan modificaciones — salvo casos
      excepcionales (alguien con peso político, una rectoría, etc.), que
      él maneja manualmente fuera del flujo formal pero quiere que quede
      registrado igual.
   └─ Cierre total/definitivo: ~10 de diciembre. A partir de ahí el
      programa maestro queda fijo.

6. EXPORTACIÓN PARA TRABAJO MANUAL FINAL
   └─ Pidió explícitamente poder exportar el resultado (Excel/Word/PDF)
      como "un territorio de trabajo para darle la pulida final" antes de
      pasarlo a la maestra para aprobación. No quiere quedar encerrado
      dentro del sistema sin poder retocar a mano la versión final.

7. PUBLICACIÓN PROGRESIVA AL PÚBLICO
   └─ Hoy el programa impreso sale tarde (a veces 3 días antes de la
      feria) porque esperan tener el 100% confirmado. Él quiere que la
      versión digital se pueda publicar 3-4 semanas antes mostrando lo
      que ya hay, aunque algunas piezas digan solo "Felicidades, [autor]
      fue aceptado — título por confirmar" y se vayan completando solas
      conforme avanza el proceso.
   └─ Referencia explícita que él mismo dio: la app de la FIL de
      Guadalajara — navegar por secciones/categorías, ver sinopsis (en el
      caso de autores/libros), agregar a "mi agenda" o descartar (basurita).
```

## 4. Entidades de datos que tendrías que modelar

A partir de lo anterior, las piezas mínimas son:

- **Propuesta** (proponente, tipo de actividad, adjuntos, estado: recibida / en revisión / aceptada / rechazada / en negociación).
- **Actividad/Sesión** (lo que ya fue aceptado y tiene — o está por tener — horario; puede tener varias sesiones si se repite).
- **Salón/Sala** (catálogo administrable: nombre —cambia cada año—, capacidad, tipo de uso). Es un catálogo **paralelo** al de espacios/stands y al de salones de talleres, pero con la misma forma de datos.
- **Bloque de horario** (plantilla configurable: duración estándar + colchón, con posibilidad de excepción manual por actividad).
- **Autor/Editorial** (sub-entidad con su propio estado de negociación, distinto al de una propuesta normal, sin fecha límite rígida porque no hay cobro).
- **Agenda pública** (vista de solo lectura, filtrable, que un visitante puede usar sin registrarse a nada salvo, opcionalmente, para guardar su "mi agenda").

## 5. Relación con las otras dos partes

### 5.1 — Con Talleres / Visitas Escolares (la parte de la coordinadora infantil-juvenil)

Es la relación más fuerte de las dos, porque **son las únicas dos convocatorias públicas que existen en toda la feria** (Hipólito lo dice de forma explícita: arte visual no tiene convocatoria pública, solo la suya y la de talleres). Eso significa que comparten, casi en automático, el mismo motor:

|                              | Programa General (Hipólito)                                  | Talleres / Visitas Escolares                                             |
| ---------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------ |
| ¿Hay convocatoria pública? | Sí                                                           | Sí                                                                      |
| ¿Quién propone?            | Ponentes, autores, editoriales                                | Talleristas                                                              |
| ¿Quién "consume"?          | El mismo que propone (no hay capa intermedia)                 | Hay una capa adicional: las escuelas, que eligen entre lo ya aprobado    |
| Flujo de revisión           | Aceptar/rechazar con cupo visible → asignar horario después | Igual: aceptar/rechazar → asignar horario/repeticiones después         |
| Confirmación                | El proponente confirma de recibido                            | El tallerista confirma; la escuela también confirma su propia reserva   |
| Catálogo de espacios        | Salones/salas del programa general                            | Salones del área infantil-juvenil + salas de cine (mañanas)            |
| Riesgo compartido            | Doble-booking de un mismo ponente en su propio programa       | Doble-booking de un mismo tallerista entre su programa y el de Hipólito |

El punto más importante a vigilar: **un mismo tallerista puede tener actividad en el programa de Hipólito y en el de talleres al mismo tiempo**, y hoy nadie lo detecta automáticamente. Si construyes tu parte sin pensar en esto, vas a dejar un hueco que después hay que parchar — conviene que, desde el diseño, tu módulo y el de talleres comparen agenda por correo/teléfono de la persona (no solo por nombre, que falla por errores de tipeo).

### 5.2 — Con Espacios / Stands (la plática del 12-06-2026)

La relación aquí es más de **patrón compartido que de datos compartidos**:

- El mismo flujo general "selecciona/propone → confirma → ficha → notificación" se repite, pero **stands cobra dinero (pago, comprobante, factura) y tu parte no cobra nada** — tu ciclo de vida es más corto: no hay paso de "pago" ni de "comprobante" ni de "factura" por defecto.
- Conceptualmente, la cuadrícula visual de stands (mapa 2D con celdas blanco/verde/azul) y tu calendario de salones/horarios son la misma idea de fondo —"mostrar qué está disponible y qué no"— pero representada de forma distinta (mapa espacial vs. calendario de tiempo). Vale la pena pensarlos como **dos vistas del mismo concepto de "disponibilidad"**, aunque la implementación visual sea diferente.
- **Dato curioso que conecta ambas partes:** Hipólito es, en la otra plática, quien entrega el plano físico de stands. Es decir, la misma persona toca ambos módulos del lado de la feria — operativamente es tu mismo interlocutor para temas de espacio físico en general, aunque a nivel de sistema sean catálogos separados.
- Identidad de usuario: igual que en stands, conviene que la misma persona pueda ser, por ejemplo, expositor (compra un stand) y además ponente en tu programa, sin registrarse dos veces. La propia idea de Hipólito de "una convocatoria FILEY para registrar, que bifurque según el tipo de actividad" coincide exactamente con esto.

### 5.3 — Resumen de las tres partes en una sola tabla

|                                                | Stands                                  | Programa General (Hipólito)                                                          | Talleres / Escolar                             |
| ---------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------- |
| ¿Cobra?                                       | Sí (transferencia/cheque)              | No                                                                                    | No                                             |
| ¿Convocatoria pública?                       | No es convocatoria, es venta directa    | Sí                                                                                   | Sí                                            |
| ¿Capa de "consumidor" además del proponente? | No (el expositor es quien compra y usa) | Parcial (autores/editoriales son un caso especial; el público general solo consulta) | Sí (escuelas eligen entre lo aprobado)        |
| Representación de disponibilidad              | Mapa 2D (Godot)                         | Calendario de horarios/salones                                                        | Calendario de horarios/salones + cupo por sala |
| ¿Necesita factura/CFDI?                       | Sí                                     | No                                                                                    | No                                             |
| Notificaciones                                 | Reserva, pago validado, factura         | Aceptación/rechazo, asignación de horario, confirmación                            | Igual que Hipólito + recordatorios a escuelas |

## 6. Lo más importante a cuidar en esta parte (en sus propias palabras)

1. **No forzar todo a bloques rígidos.** Pidió, casi preocupado, que el sistema no "rompa" o pierda el horario/salón si una actividad no encaja en un bloque estándar. Es el riesgo técnico más concreto que él mismo señaló.
2. **No perder la posibilidad de retoque manual final.** Quiere exportar a Excel/Word/PDF antes de la entrega final — si el sistema se vuelve una caja cerrada sin exportación, le quitas una parte de su flujo de trabajo actual que él valora.
3. **Separar "aceptado" de "con horario asignado".** Son dos notificaciones distintas a propósito — le da margen de maniobra. Si el sistema obliga a asignar horario en el mismo paso que aceptar, le quitas esa flexibilidad que pidió explícitamente.
4. **Autores/editoriales no deben forzarse al mismo calendario rígido que el resto.** Es un sub-flujo con su propio ritmo (sin fecha límite dura, sin presión porque no hay cobro) — tratarlo como una propuesta normal generaría fricción donde hoy no la hay.
5. **Permisos diferenciados, no solo "admin sí/no".** Él mismo distingue: él (coordinador, edita), posibles colaboradores que "metan mano" en su información (edición acotada), y "la maestra" (solo necesita visualizar, no editar). Es el mismo patrón "Google Drive" que ya se documentó en el análisis general, pero aquí con un matiz: el rol de supervisor debe ser explícitamente de solo lectura.
6. **Publicación progresiva, no todo-o-nada.** El valor real para él es poder sacar algo público semanas antes en vez de esperar a tener el 100%, porque hoy esa espera es la causa de que el programa impreso salga tarde.

## 7. Cómo abarcarlo — orden recomendado de trabajo

Te sugiero construirlo en este orden, de menor a mayor riesgo/complejidad:

1. **Catálogo de salones/salas** (RFH-10) — es la base de todo lo demás y es sencillo: nombre, capacidad, tipo. Puede incluso compartir componente con el catálogo de salones de talleres.
2. **Modelo de Propuesta + formulario de convocatoria** (RFH-01 a RFH-04) — reutilizable casi calcado del de talleres, así que conviene diseñarlo pensando en ambos desde el inicio aunque tú solo entregues el de Hipólito.
3. **Revisión aceptar/rechazar con contador de cupo en vivo** (RFH-05 a RFH-08) — sin asignación de horario todavía. Esto ya es un entregable útil por sí solo.
4. **Vista de calendario de disponibilidad + asignación de horario/salón** (RFH-11 a RFH-16) — la pieza más delicada técnicamente; aquí es donde vale la pena invertir en el manejo de bloques no estándar desde el diseño, no como parche después.
5. **Confirmación del proponente + ventana de cambios** (RFH-17 a RFH-20).
6. **Exportación editable + generación de ficha PDF** (RFH-26, RFH-27) — relativamente independiente, se puede hacer en paralelo.
7. **Agenda pública / cartelera** (RFH-21 a RFH-25) — déjalo para el final: depende de que todo lo anterior ya tenga datos reales cargados, y es la pieza con más valor "demo" para mostrarle a Hipólito y a "la maestra".

## 8. Pendientes a confirmar directamente con Hipólito antes de modelar

> **Actualización:** varios de estos puntos ya se resolvieron al revisar los documentos reales de la carpeta `archivos_de_contexto_exterior/` — ver `docs/resumen_archivos_contexto_exterior.md` para el análisis completo.

- ~~El conteo real de salones/salas (dijo "13 en total, 3 salones y 3 salas", que no cierra aritméticamente — 3+3=6, no 13)~~ — **Resuelto.** `Programación General FILEY 2027.xlsx` confirma 6 espacios: Salón Uxmal 3, Salón Uxmal 4, Salón Dzibilchaltún (los 3 "salones") + Sala Fernando del Paso, Sala Fernando Espejo, Sala Antonia Jiménez Trava dentro del Salón Chichén Itzá (las 3 "salas"). El "13" fue error de transcripción. El catálogo real es aún más grande: el programa impreso 2026 también usa Uxmal 1 ("Gran Foro", 600 personas) y al menos una sala de cine.
- ~~Las fechas exactas de esta edición~~ — **Resuelto.** `Convocatoria para Actividades FILEY 2027.pdf` y `Detalles para el Registro en Línea 2027.pdf` dan las fechas oficiales: 10 de agosto (lanzamiento), 2 de octubre 16:00 (cierre), 13 de noviembre (aviso de aceptación + fecha de participación), 7 de diciembre 16:00 (cierre de ajustes), 22 de enero (asignación de hora y salón), 26 de abril (constancias). Sustituyen las fechas aproximadas del audio.
- Qué tan formal debe ser el registro de los casos especiales de cambio de horario (políticos, rectoría) — dijo que quiere que quede registrado, pero no especificó si necesita aprobación de alguien más o basta con que él lo capture. **Sigue pendiente**, no aparece en los documentos oficiales revisados. (con casos especiales me refiero al hehco de entidades que se comunican diractamente con hipolito)
- Si los colaboradores que "le ayudan con la información" necesitan cuenta propia en el sistema o trabajan siempre bajo la cuenta de Hipólito. **Sigue pendiente.**
- Nuevo (detectado en los documentos reales, no en el audio): confirmar si el catálogo de "tipo de actividad" debe quedar abierto/extensible — el programa impreso real usa tipos (Cuentacuentos, Plática, Curso, Multidisciplinario, Concierto) que no están en el formulario oficial de 8 tipos (Conversatorio, Conferencia, Charla, Mesa redonda, Presentación de libro, Presentación de revista, Lectura de obra, Encuentro), casi siempre organizados directamente por FILEY-UADY sin pasar por la convocatoria pública. También se confirmó el tope real de duración: **50 minutos** para las actividades estándar (no 1 hora).
- ¿es Hipólito quien decide si una propuesta es "literaria" o "académica", o el proponente lo elige al registrarse?
- Nuevo: confirmar si las 4 categorías reales de propuestas (Literarias UADY / Actividades Literarias / Académicas UADY / Actividades Académicas, vistas en `Base Registro de Propuestas FILEY 2027.xlsx`) deben modelarse como un campo más o como colecciones separadas con su propio flujo de revisión.
- Nuevo: una actividad puede ubicarse físicamente en el stand de una editorial (visto en `Programa General FILEY 2026.pdf`: "Chichén Itzá, stand de Casa Editorial-UADY") — confirmar si el campo "lugar" de una actividad debe poder apuntar a un stand del módulo de Espacios además de a un salón del catálogo propio.
