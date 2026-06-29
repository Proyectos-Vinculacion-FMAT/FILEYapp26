---
tags:
  - tipo/junta-notas
  - tema/descubrimiento
  - tema/cliente
  - dom/std
  - dom/evt
  - dom/tal
  - dom/vis
  - tema/permisos
estado: borrador
fecha: 2026-06-17
fecha_actualizacion: 2026-06-29
---

# Preguntas para la siguiente sesion

Preguntas para validar la propuesta conceptual de tratamiento de usuarios y aclarar supuestos detectados en la primera junta.

> [!important]
> El objetivo de estas preguntas es confirmar procesos del cliente antes de definir automatizaciones, flujos finales o decisiones técnicas.

---

> [!success] Avance tras Junta 1, Junta 2 y Junta 3
> Varias preguntas quedaron resueltas (marcadas con `[x]`, con una nota de respuesta debajo). Otras tuvieron avances parciales (nota "Avance") y se mantienen abiertas. También se agregaron preguntas nuevas surgidas de los temas de stands, eventos, talleres, visitas escolares, identidad/acceso y permisos administrativos, a partir de un repaso de la transcripción completa de la Junta 2 con los oradores ya identificados, de la homologación de dominios y casos de uso en la Junta 3, y de una revisión del material de Contenidos que entregó FILEY (ver `docs/soporte/extraido/`).

---

> [!info] Dudas nuevas tras la Junta 2 con el Equipo de desarrollo
> En la junta interna de revisión de borradores ([resumen](<../resumenes/RSM - Junta 2 con Equipo de desarrollo.md>)) surgieron dudas adicionales para el cliente al detallar los casos de uso. Quedan marcadas abajo con la etiqueta *(Junta dev)* en sus secciones correspondientes.

<!-- -->

> [!info] Dudas y decisiones nuevas tras la Junta 3 con el Equipo de desarrollo
> En la homologación de dominios y casos de uso ([resumen](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md>)) se resolvieron o avanzaron varias dudas que ya estaban abiertas aquí (notas de avance/respuesta actualizadas), y quedaron **decisiones internas** sin resolver que el equipo dejó explícitas para retomar (ver la sección [Decisiones pendientes (Junta 3)](#decisiones-pendientes-junta-3) al final de este documento).

<!-- -->

> [!info] Vocabulario homologado (Junta 3) — cómo leer las preguntas de abajo
> La mayoría de estas preguntas se redactaron **antes** de la homologación y conservan el lenguaje original del cliente (Junta 1/2). Para no perder ese registro histórico no se reescribieron, pero conviene leerlas con el vocabulario actual del
> [glosario de la Junta 3](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md#2-glosario-de-dominio>):
>
> - **Aplicante** = quien llena una propuesta (sinónimo: "registrante"); pasa a **Participante** solo cuando su propuesta queda **Aceptada**. Es un rol *por propuesta/convocatoria*, no una identidad global del usuario.
> - **"Arrendatario"**, **"expositor"** y **"participante de evento"** (como roles, en minúscula) son, en el modelo homologado, el mismo par **Aplicante → Participante** aplicado a los tipos de propuesta `STD` y `EVT`/`TAL` respectivamente.
> - **"Contenidos"** es el nombre informal (de Hipólito/el equipo) del dominio que la Junta 3 homologó como **`EVT`** (Eventos); **"Talleres"** ya coincide con el nombre formal de **`TAL`**.
> - **Visita escolar** no es un "tipo de visitante": es un **tipo de propuesta** más (junto a stand, evento y taller) dentro de Convocatorias **`[REG]`**, con su propio ciclo Pendiente a revisión → Aceptada/Solicitud de cambios/Rechazada.
> - **"Visitante"** (asistente individual a la feria, sección siguiente) sigue **sin modelarse** en ninguna junta con el equipo; no debe confundirse con **Visita escolar**.

## Registro base

- [ ] ¿Qué datos mínimos necesitan para identificar a una persona dentro del sistema?
  - *Avance (Junta 2): se propuso usar la combinación de teléfono + correo electrónico como identificador único de una persona entre los distintos módulos (Hipólito y Elvira), ya que el nombre no es confiable por variaciones de captura. Falta confirmar si ambos serán obligatorios o si basta con uno.*
- [ ] ¿El registro base debe pedir nombre, teléfono, correo o algún otro dato indispensable?
- [ ] ¿Teléfono y correo deben ser obligatorios, o basta con uno de los dos?
- [x] ¿Una misma persona podría registrarse una sola vez y después solicitar distintos servicios?
  - *Respuesta (Junta 3): sí — el registro de Usuario se hace una sola vez; el inicio de sesión posterior es por código de un solo uso (OTP). Aplicante y Participante son roles **por propuesta/convocatoria**, no una identidad global: un mismo usuario puede ser Aplicante en una convocatoria y Participante en otra al mismo tiempo.*
- [ ] ¿Qué debe poder hacer una persona recién registrada, sin ningún rol especial?
- [x] ¿El sistema usará contraseñas o algún otro mecanismo de acceso?
  - *Respuesta (Junta 2): se propuso autenticación sin contraseña — el usuario da su correo (o teléfono) y recibe un código de acceso de un solo uso en cada inicio de sesión. Esto evita que la gente olvide su contraseña y termine duplicando registros con otro correo.*

## Visitantes

> [!note] Distinto de "Visita escolar"
> Este "visitante" es el asistente individual a la feria (no escolar). Ningún resumen de junta lo modela todavía como dominio; queda como alcance futuro (ver `CNT`/`ACC` en
> [requisitos/README.md](<../../../requisitos/README.md#dominios-futuros--no-prioritarios>)), distinto de **Visita escolar** (`VIS`, sección siguiente), que sí es prioritaria desde la Junta 3.

- [ ] ¿Quieren que los visitantes se registren antes de asistir a la feria?
- [ ] ¿Qué información necesitan conocer de los visitantes?
  - *Avance (Junta 2): para visitas escolares se necesita conocer el aforo del grupo y el nivel educativo de la escuela. Para visitantes individuales, ya existe un sistema de registro previo a este proyecto que capturaba nombre, correo, procedencia y edad (por año de nacimiento); puede servir de referencia. Falta confirmar si se mantienen los mismos campos.*
- [ ] ¿Cómo se validaría que un visitante llegó a la feria?
- [ ] ¿El registro de visitantes debe servir solo para acceso, o también para reportes?

## Visitas escolares

> [!note]
> Sección nueva, a partir de lo discutido en la Junta 2. Las visitas escolares son un volumen importante (~3,000-3,500 niños por día) y tienen necesidades distintas a las de un visitante individual.

<!-- -->

> [!info] Vocabulario (Junta 3)
> La Junta 3 confirmó y precisó esta sección: la **visita escolar** no es un "tipo de visitante", sino un **tipo de propuesta** más dentro de Convocatorias `[REG]` (junto a stand, evento y taller), con el mismo ciclo Pendiente a revisión → Aceptada/Solicitud de cambios/Rechazada. Ver
> [Junta 3 §2.8](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md#28-visitas-escolares-vis>)
> y [requisitos/VIS/CU-VIS Índice.md](<../../../requisitos/VIS/CU-VIS Índice.md>).

- [x] ¿Las visitas escolares deben registrarse como un tipo de visitante grupal, distinto al visitante individual?
  - *Respuesta (Junta 3): ni una cosa ni la otra — se modeló como un **tipo de propuesta** propio (`VIS`), no como una variante de "visitante". El representante de la escuela es el **Aplicante**; al aceptarse su propuesta pasa a **Participante** y arma su **Itinerario** reservando **Cupo** en actividades infantiles/juveniles.*
- [ ] ¿Qué datos debe capturar el registro de una escuela (aforo del grupo, nivel educativo, fecha y horario de visita)?
  - *Avance (Junta 3, precisado 2026-06-25): el registro captura los datos de la escuela, su contacto y la **cantidad total de alumnos/visitantes** que asistirán (CU-VIS-001, dato obligatorio según el documento de FILEY). La fecha/horario de visita no se captura como un dato suelto, sino que resulta de qué actividades elige el Aplicante al armar su Itinerario (CU-VIS-012/013). El "aforo del grupo" se valida repartiendo esa cantidad de visitantes contra el **Cupo** restante de **cada** actividad (CU-VIS-011) —el grupo puede dividirse entre varios talleres—, no contra un solo taller. Sigue pendiente confirmar con el cliente el detalle exacto del formulario — ver
    [requisitos/VIS/CU-VIS Índice.md](<../../../requisitos/VIS/CU-VIS Índice.md>).*
- [x] ¿Quién registra a la escuela: un representante de la escuela, o el personal de FILEY?
  - *Respuesta (Junta 3): un representante de la institución (el **Aplicante**), no el personal de FILEY — ver
    [Junta 3 §2.8](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md#28-visitas-escolares-vis>).*
- [ ] *(Análisis VIS, 2026-06-25)* ¿Qué **validación o aprobación previa** existe antes de que una visita escolar pueda **reservar** talleres?
  - *Contexto: se entiende que habrá *alguna* validación antes de habilitar la reserva, pero **no se sabe cuál exactamente**. El "al momento" del documento de FILEY se refiere a que la escuela elige en cuanto tiene la capacidad de hacerlo —eliminando el ida y vuelta de correos con la coordinación (catálogo → respuesta de confirmación)—, no a que no exista validación. Importante definirlo: determina si la reserva es inmediata tras el registro o si pasa por una aceptación. Ver [Análisis VIS vs Software para agendar escuelas — C2](<../../notas/Análisis VIS vs Software para agendar escuelas.md>).*
- [x] *(Análisis VIS, 2026-06-25)* ¿La vista del **itinerario** armado se **envía por correo automáticamente**, o basta con poder **verla/descargarla desde la app**?
  - *Respuesta (Junta 3 con organizadores FILEY): se envía por correo de forma automática, a **ambos contactos** (el de la institución y el del representante que registró). El paquete incluye reglamento, carta de confirmación/bienvenida e itinerario con membrete y formato oficial. **Sigue pendiente la plantilla** del documento oficial — bloqueante para implementarlo. Ver [RSM - Junta 3 con organizadores FILEY](<../resumenes/RSM - Junta 3 con organizadores FILEY.md>) y [Análisis VIS — C3](<../../notas/Análisis VIS vs Software para agendar escuelas.md>).*
- [x] *(Análisis VIS, 2026-06-25)* ¿Cuál es la **política definitiva de cuántos talleres** puede reservar una escuela?
  - *Respuesta (Junta 3 con organizadores FILEY): Elvira indicó que la selección ahora es **libre por asiento** — la escuela decide cómo dividir sus grupos y a qué actividades entrar, con cuántos alumnos. Ya no hay candados ni combinaciones de cupo prefijadas (se descarta el "una sala de cine o 3 talleres de 35"). La única regla vigente es que cada visita escolar tiene un **máximo de 105 alumnos**, y que cada **nivel educativo es un registro (propuesta) distinto**. Ver [RSM - Junta 3 con organizadores FILEY](<../resumenes/RSM - Junta 3 con organizadores FILEY.md>) y [CU-VIS-012](<../../../requisitos/VIS/C - Catálogo y reserva de talleres/CU-VIS-012 Reservar uno o varios talleres del catálogo para armar el itinerario de la visita.md>).*

## Arrendatarios de stand

> [!info] Vocabulario (Junta 3)
> "Arrendatario" es el término original del cliente. En el modelo homologado, quien solicita un stand es un **Aplicante**; al **Aceptarse** su propuesta pasa a **Participante** (tipo *compra de stand*, ver
> [Junta 3 §4.3](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md#43-participante>)). Las preguntas de esta sección se dejaron con "arrendatario" porque describen el proceso **actual** del cliente, previo al sistema.

- [ ] ¿En qué punto del proceso de solicitud de un stand debería asignarse el rol de arrendatario: al registrar la solicitud, al pagar el anticipo del 50%, o al liquidar el total?
  - *Avance (Junta 1): el anticipo del 50% es lo que "fija" la reserva, lo cual sugiere que ese pago podría ser el punto de transición a arrendatario.*
  - *Tensión a confirmar (Junta 3): el modelo homologado de Convocatorias define la transición Aplicante → Participante en el momento en que el Administrador **Acepta** la propuesta, de forma uniforme para los cuatro tipos de propuesta (`STD`/`EVT`/`TAL`/`VIS`) — ver
    [Junta 3 §2.1](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md#21-actores>). Esto no calza directamente con lo que sugiere Junta 1 (que es el **pago**, no una aceptación, lo que fija la reserva de un stand estándar). Falta aclarar con el cliente si para `STD` existe igualmente un paso de Aceptación (aunque sea automático) antes/al momento del pago, o si el stand es la excepción al ciclo general.*
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
  - *Respuesta (Junta 2): sí. Hipólito revisa cada propuesta y la marca como aceptada o rechazada. Una vez **Aceptada**, el Aplicante pasa a **Participante** y tiene una ventana de tiempo fija para modificar él mismo los datos de su actividad (no la fecha/horario, que la asigna FILEY); al cerrarse la ventana, el sistema bloquea cualquier cambio.*
- [ ] ¿Qué datos mínimos necesita el cliente para evaluar una solicitud de evento?
  - *Avance (Junta 2): para presentaciones de libros se contempla portada, foto del autor y sinopsis. Falta definir los datos mínimos generales para los demás tipos de evento.*
- [ ] *(Junta dev)* ¿Falta una categoría/opción en el **formulario de convocatoria** (tipo de actividad)? Confirmar el catálogo completo.
  - *Contexto (Junta dev): al revisar el PDF de registro de propuestas se notó que parecían faltar opciones (se mencionó la de "Encuentro"). Conviene que Hipólito confirme la lista definitiva de tipos de actividad y, por cada uno, qué campos son texto libre y cuáles deben ser de opciones predeterminadas.*
- [ ] *(Junta dev)* ¿La **cartelera** de eventos alrededor de FILEY debe formar parte del sistema y, de ser así, qué datos captura?
  - *Contexto (Junta dev): hoy a Hipólito solo le envían la información de la cartelera y él la incluye en el documento a imprimir; no hay un formato/formulario definido. Si entra al sistema, alguien tendría que capturarla y habría que distinguir "programa formal" vs "cartelera". Por ahora la publicación del programa se contempla solo interna.*
  - *Avance (Hipólito, 2026-06-29): confirma que el catálogo/programa con el detalle de actividades **no se hace llegar al público general**; es para trabajo interno. La información del programa ya específico se usa para el programa impreso/digital. No resuelve la pregunta de la cartelera en sí, pero reafirma que la publicación detallada es interna. Ver
    [Preguntas Para Hipolito Respondidas](<../../extraido/Material para Registro de Actividades FILEY 2027/Preguntas Para Hipolito Respondidas.md>).*
- [ ] *(Junta dev)* ¿Se entregan **constancias de participación**? ¿A quién (participantes, expositores, público) y cómo se manejan en actividades **grupales** (paneles, mesas con varios participantes)?
  - *Contexto (Junta dev): se requiere una plantilla para generarlas. El caso difícil es el grupal (una constancia con muchos nombres no es manejable); falta definir el formato. También se confundió con los gafetes, que son otra cosa.*
  - *Avance (Junta 3 con organizadores FILEY): se confirma que la generación **siempre será automática**, independientemente de si los nombres capturados por los registrantes son correctos. El diseño (texto, imagen de fondo y campos a rellenar) será **hardcodeado**, no configurable. Lo único que falta es la **plantilla** — sigue siendo el bloqueante. El caso grupal sigue sin resolver. Ver [RSM - Junta 3 con organizadores FILEY](<../resumenes/RSM - Junta 3 con organizadores FILEY.md>).*
- [x] ¿El "público al que va dirigido" de las actividades de Contenidos debe ser de **opciones predeterminadas** o texto libre?
  - *Respuesta (Hipólito, 2026-06-29): opción múltiple, confirmada. Opciones: Público en general, Académico, Estudiantil, Infantil, Familias. Ver
    [Preguntas Para Hipolito Respondidas](<../../extraido/Material para Registro de Actividades FILEY 2027/Preguntas Para Hipolito Respondidas.md>). Sigue pendiente documentarlo oficialmente como catálogo de `EVT` cuando se abra ese dominio (catálogo distinto al de Talleres).*
- [ ] *(Material FILEY)* ¿Conviene que el registro de propuestas de Contenidos ofrezca, para aplicantes de la UADY, una lista predeterminada de facultad/dependencia en vez de texto libre?
  - *Contexto: mismo dilema que la pregunta anterior (predeterminado vs. texto libre), aplicado a un campo distinto. El libro `Base Registro de Propuestas FILEY 2027.xlsx` ya desglosa, en su hoja de Conteo, un listado fijo de facultades/dependencias (Ciencias Antropológicas, Arquitectura, Medicina, Enfermería, Derecho, Educación, Secretaría General, entre otras) para fines de conteo — lo que sugiere que esa lista ya existe operativamente y podría reutilizarse en el formulario. Ver
    [extraído](<../../extraido/Material para Registro de Actividades FILEY 2027/Base Registro de Propuestas FILEY 2027/Base Registro de Propuestas FILEY 2027.Conteo.csv>).*
- [ ] *(Material FILEY)* ¿Cuál es la diferencia entre una actividad **académica** y una **literaria** dentro del registro de propuestas de Contenidos?
  - *Contexto: el mismo libro separa las propuestas en 4 categorías — Literarias, Literarias UADY, Académicas, Académicas UADY —, pero ninguna junta con el cliente explica qué distingue a una de otra; falta confirmarlo con Hipólito. Ver
    [índice de extraídos](<../../extraido/Indice.md>), sección "Base Registro de Propuestas FILEY 2027".*
- [ ] *(Material FILEY)* ¿El registro de actividades académicas/literarias de la **UADY** se gestiona de forma interna, o los aplicantes de la UADY llenan el mismo formulario que el resto de participantes?
  - *Contexto: es un caso distinto al de los eventos artísticos (Artes Visuales/Escénicas/Cinematográficas), que sí se sabe que se capturan solo para contabilidad interna sin pasar por aprobación (ver
    [Junta 2 con organizadores FILEY](<../resumenes/RSM - Junta 2 con organizadores FILEY.md#tipos-de-eventos>), sección "Tipos de eventos"). Para Literarias/Académicas UADY no hay esa confirmación.*
- [ ] *(Material FILEY)* ¿El libro `Base Registro de Propuestas FILEY 2027.xlsx` representa el universo completo de propuestas de Contenidos que revisa Hipólito, o es un grupo aislado de esas propuestas?
  - *Contexto: el [índice de extraídos](<../../extraido/Indice.md>) lo describe solo como "modelo de la base de datos de propuestas (salida del registro)", sin precisar si cubre el 100% de lo que Hipólito revisa.*
- [ ] ¿La revisión de propuestas con el sistema nuevo se hará **conforme van llegando** o **hasta que cierre la ventana de convocatorias**? (aplica a Contenidos y a Talleres)
  - *Avance (Junta 2): para eventos de Contenidos, Hipólito revisa de forma continua conforme llegan (ver "¿Cómo y cuándo se notifica...?" abajo). Falta confirmar si Talleres (Elvira) seguirá el mismo criterio o revisará al cierre. Esto determina qué puede hacer quien propone mientras tanto.*
- [ ] ¿Qué puede **editar** quien propone un taller o una actividad de Contenidos, y en qué momento?
  - *Detalle a definir campo por campo: ¿puede modificar quién participa, a quién va dirigido, corregir la semblanza, el título o la sinopsis? ¿Qué campos NO conviene que corrija (p. ej. tipo de actividad, o la fecha/horario que asigna FILEY)? Relacionado con la ventana de modificación post-aceptación de la pregunta "¿El registro de evento requiere aprobación manual?" arriba; falta el equivalente para Talleres.*
  - *Avance (Hipólito, 2026-06-29): confirmado que el proponente **no puede pedir cambios de horario, sala ni fecha** bajo ningún caso — esa opción no se ofrece. Solo el coordinador (Hipólito) hace esos cambios; si el cambio es de **fecha**, debe revisarlo primero con el involucrado. Consistente con `PRG` (la fecha/sala/horario las asigna el Administrador, no el Aplicante/Participante; ver
    [CU-PRG-002](<../../../requisitos/PRG/A - Armado del programa/CU-PRG-002 Asignar una programación a una actividad.md>)) y con la nota de que la reprogramación se negocia fuera del sistema (ver
    [CU-PRG-009](<../../../requisitos/PRG/B - Notificación y confirmación/CU-PRG-009 El Participante confirma su asistencia o incomparecencia al horario asignado.md>)). Ver
    [Preguntas Para Hipolito Respondidas](<../../extraido/Material para Registro de Actividades FILEY 2027/Preguntas Para Hipolito Respondidas.md>). Sigue pendiente el resto del detalle (semblanza, título, sinopsis, etc.).*
- [ ] ¿Los horarios propuestos por el usuario siempre son tentativos?
- [x] ¿Quién confirma el horario final?
  - *Respuesta (Junta 2): el equipo organizador revisa las propuestas de eventos y las acomoda dentro del horario general de actividades de la feria.*
- [x] ¿Cómo y cuándo se notifica al registrante si su evento fue aceptado o rechazado?
  - *Respuesta (Junta 2): Hipólito revisa las propuestas de forma continua conforme llegan (no solo al cierre de la convocatoria). Cuando termina su revisión, un solo envío notifica en lote a todos los aceptados y rechazados. El sistema debe registrar que la notificación fue enviada, para que Hipólito pueda deslindarse si alguien dice no haberla recibido.*
- [x] *(Material FILEY)* En presentación de libro/revista, el formulario pide "enviar un ejemplar" como obligatorio — ¿qué pasa si el solicitante no lo envía?
  - *Respuesta (Hipólito, 2026-06-29): no pasa nada en términos de la propuesta; es una presión para incentivar el envío, ya que el ejemplar ayuda a revisar mejor la propuesta. El solicitante no debe saber que en realidad no es bloqueante. No requiere validación del sistema más allá de marcar el campo como "obligatorio" en el formulario (lógica de UI, no de negocio). Ver
    [Preguntas Para Hipolito Respondidas](<../../extraido/Material para Registro de Actividades FILEY 2027/Preguntas Para Hipolito Respondidas.md>).*

## Espacios, horarios y talleres

> [!note]
> Sección nueva, a partir de lo discutido en la Junta 2.

- [ ] ¿Las ubicaciones de Hipólito (3 salones + sala de exposición con sub-espacios Uxmal, Dzibilchaltún y Chichén Itzá) y las de Elvira (Ek Balam subdividido con mamparas + 2 salas de cine + biblioteca) deben modelarse como dos conjuntos de recursos reservables independientes dentro del sistema?
  - *Avance (Junta dev): el equipo se inclina por un **único catálogo (CRUD) de salas/salones compartido** entre Hipólito y Elvira (visible para ambos, coordinándose internamente sobre qué espacio usa cada quien), en lugar de dos catálogos separados.*
  - *Avance (Junta 3): se homologó como catálogo único compartido (dominio `SAL`), sin distinguir Administradores por nombre propio — ver
    [requisitos/SAL/CU-SAL Índice.md](<../../../requisitos/SAL/CU-SAL Índice.md>). La confirmación final con el cliente sigue abierta.*
- [ ] *(Junta dev)* ¿Con qué frecuencia **realmente cruzan espacios** Hipólito y Elvira (un salón de uno usado por el otro en una ocasión)?
  - *Contexto (Junta dev): se entendió que es algo puntual/esporádico, pero define si basta con un catálogo compartido y disponibilidad visible, o si se necesita una gestión de conflictos más elaborada.*
- [ ] *(Junta dev)* ¿Por dónde se canalizan las **salas de cine** (solo mañanas, para actividades escolares) y quién las registra en el sistema?
  - *Contexto (Junta dev): por la grabación se entendió que funcionan parecido a los eventos artísticos (alguien le avisa a Hipólito que la sala está disponible y él la captura). Como están dirigidas a actividades escolares, en términos del sistema tendría más sentido canalizarlas por Elvira. Falta confirmarlo.*
- [x] ¿Cómo debe representar el sistema los bloques de 1 hora (o 1h15) del programa maestro de Hipólito, dentro de los cuales la actividad real ocupa 45-50 minutos, y sus excepciones (eventos masivos y salas de cine de 2 horas)?
  - *Respuesta (Junta 3 con organizadores FILEY): los bloques quedan **hardcodeados por panel**, sin CRUD en ningún dominio — **1:15** en el panel de Eventos, **1:00** (50 min de actividad + 10 min de descanso entre sesión) en el panel de Talleres. Una sala no tiene ningún horario relacionado al crearse; es el panel de programación el que define la división en bloques. Ver
    [requisitos/PRG/CU-PRG Índice.md](<../../../requisitos/PRG/CU-PRG Índice.md>) y [RSM - Junta 3 con organizadores FILEY](<../resumenes/RSM - Junta 3 con organizadores FILEY.md>). Las excepciones (eventos masivos, salas de cine de 2h) siguen sin tratamiento explícito en los CU.*
- [x] ¿Cómo debe apoyar el sistema la elección de talleres por parte de las escuelas (validando aforo y nivel educativo), sin depender de la revisión manual de la organizadora de talleres?
  - *Respuesta (Junta 3): se modeló como el dominio `VIS` (Visitas escolares) — la escuela consulta el catálogo de talleres filtrado, el sistema valida que el cupo restante cubra a sus visitantes, y la escuela reserva para armar su itinerario. Ver
    [requisitos/VIS/CU-VIS Índice.md](<../../../requisitos/VIS/CU-VIS Índice.md>) (CU-VIS-010 a CU-VIS-012). Sigue pendiente confirmar con el cliente el formulario exacto y la política de cuántos talleres por escuela (el documento de FILEY contempla varios; ver la pregunta dedicada más abajo y [Análisis VIS — R2](<../../notas/Análisis VIS vs Software para agendar escuelas.md>)).*
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
- [x] ¿Un mismo usuario puede ser visitante, arrendatario de stand y participante de evento?
  - *Respuesta (Junta 3): para stand/evento/taller/visita escolar, sí — Aplicante y Participante son roles **por propuesta/convocatoria**, no una identidad global del Usuario: el mismo Usuario puede ser Aplicante en una convocatoria y Participante en otra al mismo tiempo (ver
    [Junta 3 §2.1](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md#21-actores>)). Queda fuera de esta respuesta el rol de "visitante" individual, que todavía no se modela (ver nota de vocabulario al inicio del documento).*
- [x] ¿Los permisos deben depender del rol aprobado o del estado de una solicitud?
  - *Respuesta (Junta 3): del **estado de la propuesta** — Pendiente a revisión / Aceptada / Solicitud de cambios / Rechazada determina si el Usuario es Aplicante o Participante, y eso es lo que habilita sus acciones (editar actividad, confirmar asistencia, comprar stand, armar itinerario, según el tipo). No hay un "rol aprobado" aparte del estado de la propuesta. Ver
    [Junta 3 §2.1–§2.2](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md#21-actores>).*
- [ ] ¿Qué acciones debe poder hacer un usuario sin rol especializado?
- [ ] ¿Qué acciones solo deben estar disponibles después de aprobación y pago?
- [x] ¿Qué niveles de permisos administrativos necesitan los usuarios internos de FILEY?
  - *Respuesta (Junta 2): se definieron dos niveles, similar a Google Drive — solo lectura y edición. Por ejemplo, la maestra/directora necesitaría solo poder consultar la información, sin modificarla.*

## Etapas operativas

- [ ] ¿En qué momentos del proceso se abre el registro base?
  - *Avance (Junta 1): para stands, las solicitudes se abren a finales o mediados de agosto, y los pagos siguen llegando hasta enero-febrero. Falta confirmar si el registro base general sigue este mismo calendario o es independiente.*
- [x] ¿Hay una etapa temprana para expositores, arrendatarios o participantes de evento?
  - *Respuesta (Junta 1): sí, para arrendatarios de stand (hoy: Participantes tipo `STD`, ver nota de vocabulario al inicio): la etapa de solicitudes inicia a finales o mediados de agosto. Pendiente confirmar si aplica igual para participantes de evento.*
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

- *Avance (Junta 3): el modelo homologado responde la mitad de esta pregunta — la transición de **rol** (Usuario → Aplicante → Participante) sí es uniforme para los cuatro tipos de propuesta (`STD`, `EVT`/`TAL`, `VIS`), gobernada por el mismo ciclo de estado de la propuesta (Pendiente a revisión → Aceptada/Solicitud de cambios/Rechazada; ver
  [Junta 3 §2.1–§2.2](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md#21-actores>)). La pregunta original también subestimaba el alcance: no es solo "quienes soliciten un stand o evento" — el mismo ciclo aplica a talleres y visitas escolares. Lo que **no** se homologó en esta junta es el **pago** (explícitamente fuera de alcance de la Junta 3), así que la tensión Junta 1 vs. Junta 2 sobre cuándo se "fija" un stand sigue abierta (ver la sección "Arrendatarios de stand" arriba).*

- [ ] ¿El flujo de solicitud (aprobación, pago, asignación de rol) debe ser uniforme para todos los servicios, o puede variar según el tipo (p. ej. stands vs. eventos)?
  - *Avance (Junta 3): la **asignación de rol** ya es uniforme (ver nota arriba); lo que sigue sin resolver es si el **pago** debe encajar en ese mismo ciclo de la propuesta o ser un paso aparte — relacionado con la decisión pendiente [D1](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d1--alcance-del-armador-de-formularios-reg>) sobre el armador de convocatorias y con el pendiente de `PAG` en
    [requisitos/README.md](<../../../requisitos/README.md#dominios-futuros--no-prioritarios>).*

## Decisiones pendientes (Junta 3)

> [!note]
> Estas no son preguntas para el cliente, sino decisiones internas que el equipo de desarrollo dejó explícitamente abiertas en la
> [Junta 3 con Equipo de desarrollo](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md#6-decisiones-pendientes>)
> y conviene resolver (o, si dependen del cliente, convertir en pregunta) antes de la siguiente sesión.

- [x] *(Junta 3 — D1)* ¿El armador de convocatorias/formularios de `REG` entra en el alcance del proyecto? De entrar, ¿es una herramienta **dev-side** (el equipo de desarrollo arma/configura) o **embebida en el programa** (el administrador la usa directamente)?
  - *Respuesta (Junta 3 con organizadores FILEY): queda **fuera de alcance** por ahora; la herramienta es hardcodeada (ninguna de las dos variantes). Ver [RSM - Junta 3 con organizadores FILEY](<../resumenes/RSM - Junta 3 con organizadores FILEY.md>).*
- [x] *(Junta 3 — D2)* ¿En qué dominio vive el CRUD de **bloques de horario**: dentro de `SAL` (al crear/editar una sala) o dentro de `PRG` (como paso previo a la asignación)? Afecta si las acciones de bloques se mueven de "Programar actividades" a "Salas y salones" (ver
  [requisitos/PRG/CU-PRG Índice.md](<../../../requisitos/PRG/CU-PRG Índice.md>) y
  [requisitos/SAL/CU-SAL Índice.md](<../../../requisitos/SAL/CU-SAL Índice.md>)).
  - *Respuesta (Junta 3 con organizadores FILEY): en ninguno de los dos — no hay CRUD. Quedan hardcodeados por panel: 1:15 en Eventos, 1:00 (50 min de actividad + 10 min de descanso) en Talleres. Una sala se crea sin ningún horario relacionado. Ver [RSM - Junta 3 con organizadores FILEY](<../resumenes/RSM - Junta 3 con organizadores FILEY.md>).*
- [x] *(Junta 3 — D3)* ¿El modelo de **notificaciones** debe ser una bandeja transversal a todos los dominios, o una función granular por módulo (con un panel del Participante que las agregue después)? Afecta a CU-PRG-009.
  - *Respuesta (Junta 3 con organizadores FILEY): por módulo; se descarta la bandeja transversal. Cada panel (incluyendo los de revisión de propuestas, que viven por dominio — `EVT`, `TAL`, `STD`, `VIS` — y no en `REG`) tiene su propio apartado de notificaciones. Ver [RSM - Junta 3 con organizadores FILEY](<../resumenes/RSM - Junta 3 con organizadores FILEY.md>).*
- [ ] *(Junta 3 — D4)* ¿Es viable la **condicionalidad fuera del formulario** (reglas que dependan de información que no está en el propio formulario de la convocatoria)? Las reglas internas al formulario ya están contempladas.

## Documentos relacionados

- [Junta 1 con organizadores FILEY](<../resumenes/RSM - Junta 1 con organizadores FILEY.md>)
- [Junta 2 con organizadores FILEY](<../resumenes/RSM - Junta 2 con organizadores FILEY.md>)
- [Junta 2 con Equipo de desarrollo](<../resumenes/RSM - Junta 2 con Equipo de desarrollo.md>)
- [Junta 3 con Equipo de desarrollo](<../resumenes/RSM - Junta 3 con Equipo de desarrollo.md>)
- [Índice de documentos extraídos](<../../extraido/Indice.md>)
- [Análisis de archivos proporcionados](<../../extraido/Analisis de archivos proporcionados.md>)
