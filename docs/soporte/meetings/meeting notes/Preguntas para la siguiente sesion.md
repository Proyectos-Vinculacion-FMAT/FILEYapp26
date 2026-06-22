---
tags:
  - juntas
  - preguntas
  - descubrimiento
  - cliente
  - stands
  - eventos
  - talleres
  - permisos
estado: borrador
fecha: 2026-06-17
---

# Preguntas para la siguiente sesion

Preguntas para validar la propuesta conceptual de tratamiento de usuarios y aclarar supuestos detectados en la primera junta.

> [!important]
> El objetivo de estas preguntas es confirmar procesos del cliente antes de definir automatizaciones, flujos finales o decisiones técnicas.

---

> [!success] Avance tras Junta 1 y Junta 2
> Varias preguntas quedaron resueltas (marcadas con `[x]`, con una nota de respuesta debajo). Otras tuvieron avances parciales (nota "Avance") y se mantienen abiertas. También se agregaron preguntas nuevas surgidas de los temas de stands, eventos, talleres, visitas escolares, identidad/acceso y permisos administrativos, a partir de un repaso de la transcripción completa de la Junta 2 con los oradores ya identificados.

---

> [!info] Dudas nuevas tras la Junta 2 con el Equipo de desarrollo
> En la junta interna de revisión de borradores ([resumen](<../resumenes/RSM - Junta 2 con Equipo de desarrollo.md>) surgieron dudas adicionales para el cliente al detallar los casos de uso. Quedan marcadas abajo con la etiqueta *(Junta dev)* en sus secciones correspondientes.

## Registro base

- [ ] ¿Qué datos mínimos necesitan para identificar a una persona dentro del sistema?
  - *Avance (Junta 2): se propuso usar la combinación de teléfono + correo electrónico como identificador único de una persona entre los distintos módulos (Hipólito y Elvira), ya que el nombre no es confiable por variaciones de captura. Falta confirmar si ambos serán obligatorios o si basta con uno.*
- [ ] ¿El registro base debe pedir nombre, teléfono, correo o algún otro dato indispensable?
- [ ] ¿Teléfono y correo deben ser obligatorios, o basta con uno de los dos?
- [ ] ¿Una misma persona podría registrarse una sola vez y después solicitar distintos servicios?
- [ ] ¿Qué debe poder hacer una persona recién registrada, sin ningún rol especial?
- [x] ¿El sistema usará contraseñas o algún otro mecanismo de acceso?
  - *Respuesta (Junta 2): se propuso autenticación sin contraseña — el usuario da su correo (o teléfono) y recibe un código de acceso de un solo uso en cada inicio de sesión. Esto evita que la gente olvide su contraseña y termine duplicando registros con otro correo.*

## Visitantes

- [ ] ¿Quieren que los visitantes se registren antes de asistir a la feria?
- [ ] ¿Qué información necesitan conocer de los visitantes?
  - *Avance (Junta 2): para visitas escolares se necesita conocer el aforo del grupo y el nivel educativo de la escuela. Para visitantes individuales, ya existe un sistema de registro previo a este proyecto que capturaba nombre, correo, procedencia y edad (por año de nacimiento); puede servir de referencia. Falta confirmar si se mantienen los mismos campos.*
- [ ] ¿Cómo se validaría que un visitante llegó a la feria?
- [ ] ¿El registro de visitantes debe servir solo para acceso, o también para reportes?

## Visitas escolares

> [!note]
> Sección nueva, a partir de lo discutido en la Junta 2. Las visitas escolares son un volumen importante (~3,000-3,500 niños por día) y tienen necesidades distintas a las de un visitante individual.

- [ ] ¿Las visitas escolares deben registrarse como un tipo de visitante grupal, distinto al visitante individual?
- [ ] ¿Qué datos debe capturar el registro de una escuela (aforo del grupo, nivel educativo, fecha y horario de visita)?
- [ ] ¿Quién registra a la escuela: un representante de la escuela, o el personal de FILEY?

## Arrendatarios de stand

- [ ] ¿En qué punto del proceso de solicitud de un stand debería asignarse el rol de arrendatario: al registrar la solicitud, al pagar el anticipo del 50%, o al liquidar el total?
  - *Avance (Junta 1): el anticipo del 50% es lo que "fija" la reserva, lo cual sugiere que ese pago podría ser el punto de transición a arrendatario.*
- [ ] ¿Existe alguna revisión o aprobación antes de confirmar una solicitud de stand, más allá de validar el pago del anticipo?
  - *Avance (Junta 1): solo se mencionó revisión a discreción para casos de descuento especial; no se mencionó aprobación previa para solicitudes de stand estándar.*
- [ ] ¿Qué información adicional (más allá de los datos fiscales para factura) se le pide a alguien que solicita un stand?
  - *Avance (Junta 1): si el cliente requiere factura, debe proporcionar sus datos fiscales. Falta definir el resto (selección de stand en el mapa, datos del expositor, etc.). Pendiente también recibir de FILEY la cuadrícula oficial para la selección del mapa.*
- [x] ¿El pago ocurre antes o después de la aprobación?
  - *Respuesta (Junta 1): para stands estándar no hay una aprobación previa separada — pagar el anticipo del 50% es lo que fija la reserva. La revisión a discreción solo aplica a solicitudes de descuento especial.*
- [ ] Si se niega un descuento solicitado, ¿cómo se notifica al expositor y cómo se refleja ese cambio en su adeudo?
  - *Pregunta ajustada: la pregunta original ("¿qué pasa si una solicitud de stand es rechazada?") no aplica tal cual, ya que en Junta 1 no se mencionó rechazo de la solicitud de stand en sí, solo evaluación a discreción de descuentos. Se relaciona con la bitácora contable mencionada en Junta 1.*

## Eventos

- [ ] ¿Quién puede solicitar registrar un evento?
- [x] ¿El registro de evento requiere aprobación manual?
  - *Respuesta (Junta 2): sí. Hipólito revisa cada propuesta y la marca como aceptada o rechazada. Los registrantes aceptados después tienen una ventana de tiempo fija para modificar ellos mismos los datos de su actividad (no la fecha/horario, que la asigna FILEY); al cerrarse la ventana, el sistema bloquea cualquier cambio.*
- [ ] ¿Qué datos mínimos necesita el cliente para evaluar una solicitud de evento?
  - *Avance (Junta 2): para presentaciones de libros se contempla portada, foto del autor y sinopsis. Falta definir los datos mínimos generales para los demás tipos de evento.*
- [ ] *(Junta dev)* ¿Falta una categoría/opción en el **formulario de convocatoria** (tipo de actividad)? Confirmar el catálogo completo.
  - *Contexto (Junta dev): al revisar el PDF de registro de propuestas se notó que parecían faltar opciones (se mencionó la de "Encuentro"). Conviene que Hipólito confirme la lista definitiva de tipos de actividad y, por cada uno, qué campos son texto libre y cuáles deben ser de opciones predeterminadas.*
- [ ] *(Junta dev)* ¿La **cartelera** de eventos alrededor de FILEY debe formar parte del sistema y, de ser así, qué datos captura?
  - *Contexto (Junta dev): hoy a Hipólito solo le envían la información de la cartelera y él la incluye en el documento a imprimir; no hay un formato/formulario definido. Si entra al sistema, alguien tendría que capturarla y habría que distinguir "programa formal" vs "cartelera". Por ahora la publicación del programa se contempla solo interna.*
- [ ] *(Junta dev)* ¿Se entregan **constancias de participación**? ¿A quién (participantes, expositores, público) y cómo se manejan en actividades **grupales** (paneles, mesas con varios participantes)?
  - *Contexto (Junta dev): se requiere una plantilla para generarlas. El caso difícil es el grupal (una constancia con muchos nombres no es manejable); falta definir el formato. También se confundió con los gafetes, que son otra cosa.*
- [ ] ¿El "público al que va dirigido" de las actividades de Contenidos debe ser de **opciones predeterminadas** o texto libre?
  - *Nota: planeamos opciones predeterminadas para evitar normalizar los datos después, pero falta confirmar con el cliente qué prefiere. En el formulario actual (PDF) es texto libre. Es un catálogo distinto al de Talleres (`publicoObjetivoContenidos` vs `publicoObjetivoTalleres` en `docs/requisitos/organizacion.json`).*
- [ ] ¿La revisión de propuestas con el sistema nuevo se hará **conforme van llegando** o **hasta que cierre la ventana de convocatorias**? (aplica a Contenidos y a Talleres)
  - *Avance (Junta 2): para eventos de Contenidos, Hipólito revisa de forma continua conforme llegan (ver "¿Cómo y cuándo se notifica...?" abajo). Falta confirmar si Talleres (Elvira) seguirá el mismo criterio o revisará al cierre. Esto determina qué puede hacer quien propone mientras tanto.*
- [ ] ¿Qué puede **editar** quien propone un taller o una actividad de Contenidos, y en qué momento?
  - *Detalle a definir campo por campo: ¿puede modificar quién participa, a quién va dirigido, corregir la semblanza, el título o la sinopsis? ¿Qué campos NO conviene que corrija (p. ej. tipo de actividad, o la fecha/horario que asigna FILEY)? Relacionado con la ventana de modificación post-aceptación de la pregunta "¿El registro de evento requiere aprobación manual?" arriba; falta el equivalente para Talleres.*
- [ ] ¿Los horarios propuestos por el usuario siempre son tentativos?
- [x] ¿Quién confirma el horario final?
  - *Respuesta (Junta 2): el equipo organizador revisa las propuestas de eventos y las acomoda dentro del horario general de actividades de la feria.*
- [x] ¿Cómo y cuándo se notifica al registrante si su evento fue aceptado o rechazado?
  - *Respuesta (Junta 2): Hipólito revisa las propuestas de forma continua conforme llegan (no solo al cierre de la convocatoria). Cuando termina su revisión, un solo envío notifica en lote a todos los aceptados y rechazados. El sistema debe registrar que la notificación fue enviada, para que Hipólito pueda deslindarse si alguien dice no haberla recibido.*

## Espacios, horarios y talleres

> [!note]
> Sección nueva, a partir de lo discutido en la Junta 2.

- [ ] ¿Las ubicaciones de Hipólito (3 salones + sala de exposición con sub-espacios Uxmal, Dzibilchaltún y Chichén Itzá) y las de Elvira (Ek Balam subdividido con mamparas + 2 salas de cine + biblioteca) deben modelarse como dos conjuntos de recursos reservables independientes dentro del sistema?
  - *Avance (Junta dev): el equipo se inclina por un **único catálogo (CRUD) de salas/salones compartido** entre Hipólito y Elvira (visible para ambos, coordinándose internamente sobre qué espacio usa cada quien), en lugar de dos catálogos separados. Falta confirmar con el cliente si prefieren catálogo compartido o separado.*
- [ ] *(Junta dev)* ¿Con qué frecuencia **realmente cruzan espacios** Hipólito y Elvira (un salón de uno usado por el otro en una ocasión)?
  - *Contexto (Junta dev): se entendió que es algo puntual/esporádico, pero define si basta con un catálogo compartido y disponibilidad visible, o si se necesita una gestión de conflictos más elaborada.*
- [ ] *(Junta dev)* ¿Por dónde se canalizan las **salas de cine** (solo mañanas, para actividades escolares) y quién las registra en el sistema?
  - *Contexto (Junta dev): por la grabación se entendió que funcionan parecido a los eventos artísticos (alguien le avisa a Hipólito que la sala está disponible y él la captura). Como están dirigidas a actividades escolares, en términos del sistema tendría más sentido canalizarlas por Elvira. Falta confirmarlo.*
- [ ] ¿Cómo debe representar el sistema los bloques de 1 hora (o 1h15) del programa maestro de Hipólito, dentro de los cuales la actividad real ocupa 45-50 minutos, y sus excepciones (eventos masivos y salas de cine de 2 horas)?
- [ ] ¿Cómo debe apoyar el sistema la elección de talleres por parte de las escuelas (validando aforo y nivel educativo), sin depender de la revisión manual de la organizadora de talleres?
- [x] ¿Los eventos artísticos deben excluirse por completo del sistema, o solo de la programación de horarios?
  - *Respuesta (Junta 2): no se excluyen del sistema. El área artística organiza su propia cartelera de forma independiente y le entrega a Hipólito una lista preliminar ya organizada; Hipólito solo la captura en el sistema para fines de contabilidad interna, sin gestionar su aprobación ni programación de horario.*
- [ ] ¿Los participantes de Talleres deben llevar **semblanza** (como en Contenidos), o no aplica?
  - *Nota: por ahora el formulario de Talleres NO pide semblanza por participante; en Contenidos la semblanza va ligada a cada participante. Conviene aclararlo para confirmar si es intencional o un faltante.*
- [ ] ¿Cuántos espacios exactos administra Elvira en Ek Balam, incluyendo los nombres de las subdivisiones con mamparas?
- [ ] ¿Qué información mínima debe capturarse de la lista preliminar de eventos artísticos para registrarla en el sistema?
- [ ] ¿La ventana de modificación post-aceptación de eventos debe ser una fecha configurable cada año por Hipólito, o sigue una regla fija?

## Roles y permisos

- [ ] ¿Qué roles reales existen hoy en su operación?
  - *Avance (Junta 1 y 2): se identificaron roles administrativos del lado del cliente: organizador general (Hipólito), asistente (Laura), contador de la asociación y organizadora de talleres (Elvira). Falta confirmar si estos deben modelarse como roles dentro del sistema, o si la pregunta se refiere solo a roles de usuarios externos (visitante, arrendatario, etc.).*
- [ ] ¿Un mismo usuario puede ser visitante, arrendatario de stand y participante de evento?
- [ ] ¿Los permisos deben depender del rol aprobado o del estado de una solicitud?
- [ ] ¿Qué acciones debe poder hacer un usuario sin rol especializado?
- [ ] ¿Qué acciones solo deben estar disponibles después de aprobación y pago?
- [x] ¿Qué niveles de permisos administrativos necesitan los usuarios internos de FILEY?
  - *Respuesta (Junta 2): se definieron dos niveles, similar a Google Drive — solo lectura y edición. Por ejemplo, la maestra/directora necesitaría solo poder consultar la información, sin modificarla.*

## Etapas operativas

- [ ] ¿En qué momentos del proceso se abre el registro base?
  - *Avance (Junta 1): para stands, las solicitudes se abren a finales o mediados de agosto, y los pagos siguen llegando hasta enero-febrero. Falta confirmar si el registro base general sigue este mismo calendario o es independiente.*
- [x] ¿Hay una etapa temprana para expositores, arrendatarios o participantes de evento?
  - *Respuesta (Junta 1): sí, para arrendatarios de stand: la etapa de solicitudes inicia a finales o mediados de agosto. Pendiente confirmar si aplica igual para participantes de evento.*
- [ ] ¿Hay una etapa posterior enfocada en visitantes?
- [ ] ¿Qué solicitudes deben estar disponibles en cada etapa?
- [ ] ¿Quién decide cuándo se abre o cierra cada etapa?

## Pagos

- [ ] ¿Qué servicios requieren pago?
  - *Avance (Junta 1): confirmado que los stands requieren pago (anticipo del 50% + liquidación). Falta confirmar si eventos o talleres también implican algún costo.*
- [x] ¿El pago confirma automáticamente una solicitud o todavía requiere revisión?
  - *Respuesta (Junta 1): para stands, el pago del anticipo (50%) fija la reserva directamente; no hay revisión o aprobación previa separada, salvo para casos de descuento especial que se evalúan a discreción.*
- [x] ¿Qué método de pago usan actualmente?
  - *Respuesta (Junta 1): transferencia bancaria. No se aceptan depósitos en efectivo, por políticas antilavado.*
- [ ] ¿OpenPay es un requisito, una opción o solo una idea?
  - *Avance (Junta 1): sigue sin decidirse. El cliente debe elegir entre una pasarela de pago automatizada (con comisión) o un proceso manual (sin comisión). OpenPay sigue siendo solo una opción mencionada, no una decisión.*
- [ ] ¿Qué comprobantes o estados de pago necesita ver administración?
  - *Avance (Junta 1): se requiere un módulo contable que reciba comprobantes digitales o en imagen y muestre los montos acumulados por participante. Los estados concretos de pago/reserva (p. ej. "pendiente", "parcial", "liquidado") aún deben definirse.*
- [ ] *(Junta dev)* ¿Los descuentos de **pronto pago** y **local** se **acumulan** o son excluyentes (uno u otro)?
  - *Contexto (Junta dev): en la junta del equipo quedó como pendiente porque Hipólito y el contador no coincidían. La decisión afecta el modelo: se busca manejar un **único descuento global** por reserva (pronto pago automático por fecha + un descuento a discreción del administrador) en vez de un catálogo de descuentos. Falta la confirmación del cliente sobre si se suman.*

## Procesos manuales

- [ ] ¿Cómo registran actualmente visitantes, expositores, arrendatarios y eventos?
  - *Avance (Junta 1 y 2): se conoce el proceso de solicitudes y pagos de stands (Junta 1) y el proceso de propuesta/aprobación de eventos y asignación de talleres a escuelas (Junta 2). Falta el detalle paso a paso de cómo se registra cada tipo hoy (formularios, canales, etc.).*
- [ ] ¿Qué partes del proceso quieren conservar manuales?
  - *Avance (Junta 1): el cliente aún debe decidir entre una pasarela de pago automatizada o un proceso manual de comprobación. La revisión de descuentos especiales también se maneja a discreción.*
  - *Avance (Junta 2): Hipólito quiere mantener manual la "pulida final" del programa maestro antes de pasarlo a su editor (quien hace el diseño/maquetación), pero pide que el sistema pueda exportar el programa a Excel, Word o PDF para apoyar ese paso.*
- [ ] ¿Qué partes les gustaría automatizar primero?
- [ ] ¿Quién revisa solicitudes actualmente?
  - *Avance (Junta 2): para eventos, Hipólito revisa las propuestas de forma continua (semana a semana, conforme llegan), no solo al cierre de la convocatoria. El sistema debe mostrarle un contador de aceptados, rechazados y espacios disponibles restantes. Falta confirmar quién revisa las solicitudes de stand.*
- [ ] ¿Qué información revisan antes de aprobar o rechazar?

## Conteo demografico

- [ ] ¿El conteo de visitantes es parte del alcance inicial o solo una posibilidad futura?
- [ ] ¿Qué personas deberían contar como visitantes para ese conteo?
- [ ] ¿Los expositores o participantes de eventos deben excluirse del conteo de visitantes?
- [ ] ¿Qué nivel de detalle necesitan: total general, por día, por evento, por acceso?
  - *Avance (Junta 2): las visitas escolares representan ~3,000-3,500 niños al día, lo cual da una idea de la magnitud del conteo diario.*
- [ ] ¿El conteo debe ser manual, con QR, lista o algún otro mecanismo?

## Pregunta central de validacion

> [!question]
> ¿Les hace sentido que todas las personas inicien como usuario base, y que solo quienes soliciten un stand o evento pasen por aprobación, pago y asignación de rol especializado?

- *Avance: Junta 1 sugiere que, para stands, el pago del anticipo (no una aprobación previa) es lo que confirma la reserva. Junta 2 confirma que, para eventos, sí existe una aprobación manual del organizador. Esto sugiere que el flujo "solicitud → aprobación → pago → rol" podría variar según el tipo de servicio.*

- [ ] ¿El flujo de solicitud (aprobación, pago, asignación de rol) debe ser uniforme para todos los servicios, o puede variar según el tipo (p. ej. stands vs. eventos)?

## Documentos relacionados

- [Preguntas para la siguiente sesion](<Preguntas para la siguiente sesion.md>)
- [Junta 1 con organizadores FILEY](<../resumenes/RSM - Junta 1 con organizadores FILEY.md>)
- [Junta 2 con organizadores FILEY](<../resumenes/RSM - Junta 2 con organizadores FILEY.md>)
- [Junta 2 con Equipo de desarrollo](<../resumenes/RSM - Junta 2 con Equipo de desarrollo.md>)
