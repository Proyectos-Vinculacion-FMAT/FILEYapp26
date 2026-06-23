# Resumen de la Plática — Programa Académico y Cultural FILEY

> Basado en la transcripción: `Archivo de audio2 (1).docx` (transcripción automática, ~2h56min, 8 oradores)
> Transcripción limpia (fusionada por turno de habla): `contexto/audio2_transcripcion_merged.txt`
> Reunión: equipo de desarrollo del sistema + dos coordinadores de programación de FILEY

**Nota sobre la fuente:** es una transcripción automática de audio y tiene errores de reconocimiento notorios (números cortados, palabras inventadas, nombres mal oídos). El más importante: cuando el texto dice "Philadelphia", "fidel", "filade" o "fiel" casi siempre el hablante dijo **"FILEY"** (o "FIL"). También "Colito" es **"Hipólito"**. Hice la corrección por contexto en todo este resumen; donde un dato (fecha, cifra, conteo de salones) queda ambiguo por la calidad del audio lo marco explícitamente como **[verificar]** en vez de inventar precisión que la grabación no tiene.

---

## 0. ¿Quiénes hablan?

A diferencia de la plática del 12-06-2026 (que era sobre venta de espacios/stands), aquí los interlocutores de la feria son **otros dos**:

| Orador | Rol identificado | Qué gestiona |
| --- | --- | --- |
| Orador 1 | **Hipólito** | El "Programa Maestro": salones/salas, presentaciones de libro, firmas, congresos/coloquios/simposios, autores invitados. También es quien en la plática anterior entrega el plano de espacios — es decir, es el responsable de **logística física** de toda la feria, no solo de stands. |
| Orador 3 | Coordinadora de **Programación Infantil y Juvenil** | Talleres infantiles/juveniles y **visitas escolares** agendadas. |
| Orador 2 | Equipo de desarrollo (el mismo rol que en la plática del 12-06) | Levanta requisitos, propone soluciones de sistema. |
| Oradores 4–8 | Resto del equipo de desarrollo / interjecciones de fondo | Apoyo, sin aportes de requisitos relevantes propios. |

Se menciona también una **"maestra"** (jefa de ambos, no presente en la llamada) a quien le presentarán el resultado más adelante, y de quien llega información sobre eventos artísticos.

---

## 1. ¿De qué se habló? — Por sectores

### Sector A — El "Programa Maestro" (Hipólito): congresos, presentaciones, autores

- Hipólito administra **3 salones grandes + 3 salas** (las salas cambian de nombre cada año según una figura literaria/académica homenajeada).
- El programa se organiza en **bloques de horario** (1 hora, con ~15 min de colchón entre eventos que no se publica pero sí se reserva internamente). Las firmas de libro a veces necesitan 1.5–2 horas y se prefiere mantener todo "adentro del salón" para controlar al público en vez de sacarlo a pasillos.
- Existe una **convocatoria abierta** para proponer actividades (congresos, mesas, ponencias, presentaciones): la gente llena un formulario (con archivos PDF/imagen), puede meter varias propuestas, y Hipólito las revisa.
- Flujo de revisión: **recibido → en revisión → aceptado/rechazado → notificación automática → asignación de fecha/salón/hora → confirmación del proponente → posible ventana corta para solicitar cambios → cierre definitivo**.
- Mencionó fechas de referencia de esta edición (no asumir que son fijas de año en año — el sistema debe permitir configurarlas cada vez, ver RF-17 ya existente): convocatoria cierra a mediados de agosto, primeras respuestas de aceptación/rechazo alrededor del 6 de octubre, ventana para pedir modificaciones del 3 al 30 de noviembre, y el "cierre total" de confirmaciones de horario alrededor del 10 de diciembre **[verificar fechas exactas con Hipólito; el audio las menciona de forma poco clara]**.
- Hoy todo esto lo hace con **Excel + una plantilla de Word con macro** que le genera una "ficha" en PDF por actividad — es exactamente el mismo patrón manual que ya se documentó para expositores (ficha + comprobante) en la otra plática, aplicado a actividades en vez de a stands.
- Quiere saber en todo momento **cuántos espacios le quedan disponibles** mientras va aceptando/rechazando (igual que un cupo que se va consumiendo).
- Un mismo ponente puede tener **más de un evento** (no se vuelve a registrar, simplemente se le programan varias actividades).

### Sector B — Talleres Infantiles y Juveniles

- La coordinadora recibe entre **250 y 300 propuestas de talleres** por edición; tras filtrar (sin viáticos, sin patrocinio, no aplica), quedan operando del orden de 230 sesiones reales derivadas de unos 40 talleres distintos (algunos talleristas dan 2 o 3 sesiones, según lo que negocien con ella).
- Espacios: el salón grande (antes uno solo, hoy subdividido con mamparas) se parte en 6 salones + 2 salones adicionales solo en la mañana + 1 salita de biblioteca ⇒ unos **9 espacios concurrentes** en la mañana para estas actividades; en la tarde pierde la sala de cine (uso comercial) y se queda con menos.
- Los talleres duran entre 40–50 minutos por convención, salvo que el tallerista pida un bloque doble (~2h).
- Algunos talleres se dan a cambio de descuentos/cortesías a editoriales (mencionó ~5 casos) — esto es una variante del descuento manual que ya existe como RF-19, no algo nuevo, pero conviene anotarlo como caso explícito de "intercambio por actividad" para que el admin lo pueda registrar.

### Sector C — Visitas Escolares (el tema que más le preocupa a la coordinadora)

Es, en sus palabras, la parte que hoy es **completamente manual y la más complicada**:

- Reciben hasta **3,000–3,500 niños por día**, de lunes a viernes, en visitas escolares.
- Las escuelas se registran y piden un horario; ella tiene que **acomodar manualmente** cada escuela en una actividad acorde a su nivel educativo (preescolar/primaria/secundaria) y a la capacidad disponible en ese momento.
- Quiere que el sistema funcione **"como un boleto de cine"**: la escuela ve qué actividades hay, cuántos lugares quedan, y elige — en vez de que ella tenga que negociar uno por uno.
- Problema identificado de integridad de datos: **una misma escuela a veces se registra 3 veces con personas distintas** para poder meter a más niños de los que un solo registro permitiría (ej. autobuses de 35–45 niños cada uno, escuela de 300 alumnos = 3 fichas separadas). El sistema necesita poder identificar esto.
- Propuesta del equipo de desarrollo: limitar el aforo que una sola institución puede tomar de una actividad/sala (ej. **máximo 50% del aforo por institución**) para que una sola escuela no agote la sala de cine (130 lugares) y deje a otra escuela sin nada.
- Vencimiento/cancelaciones: si la escuela no confirma a tiempo (recordatorios automáticos antes de la visita) el lugar se libera; aun así "se les ponchó una llanta" o cosas similares son inevitables y quedan fuera del sistema.
- La convocatoria de visitas escolares se cierra antes de la feria (alrededor de enero), pero **igual llegan escuelas sin registro previo** — para esos casos quieren un **registro abierto sin actividades asignadas**, solo para fines estadísticos y para que el equipo en la puerta sepa cuántos llegaron, no para reservar cupo.
- Quiere mantener un margen de flexibilidad humana (intercambiar grupos entre niveles, negociar in situ) — no todo debe quedar rígido en el sistema.

### Sector D — Eventos Artísticos / Arte Visual

- Es una coordinación pequeña y **no tiene convocatoria pública** (no cobra ni abre al público en general).
- Acordaron que **no necesita salir en el sistema como registro público**, pero sí les convendría un **registro interno** (cuántas actividades, de qué tipo) para llevar control/contabilidad, sin URL pública.
- También participan en espacios externos a la feria (facultades de arquitectura, matemáticas, etc.) que **no se coordinan desde FILEY** y por tanto quedan fuera del sistema.

### Sector E — Identidad única de usuario ("una sola cuenta FILEY")

Este es el punto donde el equipo de desarrollo conecta explícitamente con la visión de "app de FILEY" que ya habían anotado como pendiente a futuro en la plática anterior (punto J):

- Propusieron un **registro base único**: nombre, correo, teléfono (+ un par de preguntas demográficas), que sirve como identidad para *cualquier* cosa dentro de FILEY: comprar un stand, proponer una actividad del programa general, registrar un taller, registrar una visita escolar, o simplemente asistir como público general.
- El reto que reconocen: **el nombre no es una llave confiable** (errores de tipeo, acentos) — proponen usar **teléfono + correo** como combinación para identificar de forma única a la misma persona/institución entre subsistemas distintos.
- Esto resuelve un caso concreto que mencionaron: si un mismo tallerista tiene actividad programada por Hipólito (programa general) **y** por la coordinadora infantil-juvenil al mismo tiempo, el sistema podría detectar el conflicto de agenda cruzando ese identificador único, algo que hoy descubren solo si alguna de las dos partes se acuerda de avisar a la otra.

### Sector F — Autenticación sin contraseña

- Propuesta explícita del equipo de desarrollo: en vez de pedir contraseña (que la gente solo usa una vez al año y olvida), enviar un **código de acceso de un solo uso al correo**, que cambia cada vez que se solicita.
- Justificación dada: evita tener que construir/soportar flujo de "recuperar contraseña", y da garantía razonable de que quien entra tiene acceso real a ese correo.

### Sector G — Notificaciones automáticas y dominio propio

- Confirmaron que existe un dominio **filey.org** administrado por ellos mismos, con cuentas de correo institucionales (ej. `hipólito@filey.org`).
- Recomendación del equipo: usar esas cuentas institucionales para los **correos automatizados** del sistema (en vez de Gmail personal), y que el personal pueda seguir respondiendo manualmente desde Gmail si quiere — solo concentrar el envío automatizado en un solo dominio.
- Mencionaron que el sistema podría dar **trazabilidad de apertura de correos** ("¿lo abrieron o no?"), útil para responder reclamos de "no me llegó nada".
- Sobre WhatsApp: tienen un número de feria atendido manualmente por una persona; ya se les **bloqueó antes por enviar mensajes masivos** ("broadcast"). Quedó claro que automatizar WhatsApp con un bot está fuera de alcance por ahora.

### Sector H — Cartelera en vivo / pantallas y QR

- Idea (del equipo de desarrollo, validada por ambos coordinadores): ya que toda la información de horarios estará digitalizada, generar automáticamente una **pantalla/cartelera en vivo** tipo "qué está pasando ahorita" — comparada por ellos mismos con un letrero de cine o un menú de McDonald's — que se actualiza sola conforme avanza el día.
- Aplicaciones mencionadas: pantallas físicas en el recinto, y un **QR** que el público o el personal de servicio social pueda escanear para ver la agenda del momento sin tener que cargar carpetas impresas (que es lo que hacen hoy).
- Hoy intentan hacer esto con un diseñador que no tiene tiempo — el sistema lo resolvería generando la plantilla automáticamente.

### Sector I — Agenda pública filtrable (estilo app de la FIL Guadalajara)

- Hipólito describió con bastante detalle cómo funciona la app de la FIL de Guadalajara como referencia (la misma que ya se había mencionado como inspiración en la plática anterior, punto J): se navega el programa por secciones, se puede filtrar, ver sinopsis/detalle, y agregar actividades a "mi agenda" o descartarlas (ícono de basura).
- Importante: el programa **se va revelando progresivamente** mientras se confirma — primero solo aparece "felicidades, [autor] fue aceptado" sin detalles, y poco a poco se completa título, fecha y hora a medida que se confirma.
- Es gratuito participar, aunque Hipólito mencionó (sin decidir nada) la idea a futuro de una **cuota de recuperación** para quien usa espacio/mobiliario de congresos — quedó solo como idea, no como requisito.

### Sector J — Cierre de la reunión / próximos pasos

- Acordaron que el equipo de desarrollo va a producir **piezas visuales** (mockups) de ambos módulos (programa general y programa infantil/escolar) para mostrarlas en 1–2 sesiones más antes de presentarle el resultado a "la maestra".
- Plazo que el equipo de desarrollo pidió: que ellos (Hipólito y la coordinadora) compartan/organicen su información interna **esta semana o inicios de la próxima**; meta de tener elementos visuales tangibles **antes de fin de mes**.
- Comparten un grupo de contacto ya existente ("gente de FILEY") para seguimiento.

---

## 2. Relación con la plática anterior (12-06-2026)

**Es el mismo proyecto y, de hecho, la misma visión a futuro que ya estaba anotada como pendiente — esta plática es esa visión, ya con mucho más detalle.**

Evidencia concreta de continuidad:

1. **Hipólito aparece en ambas pláticas.** En la del 12-06 es quien entrega "la cuadrícula definitiva del plano 2027" (el plano físico de stands). En esta plática es quien administra salones/salas y el programa de actividades. Es la misma persona — el responsable de **espacio físico** de toda la feria, ya sea para stands o para programación. Esto confirma que ambas conversaciones describen al mismo equipo operativo de FILEY, no a dos clientes distintos.
2. **El punto J de `resumen_platica.md`** ("Visión a Futuro — App FIL") decía textualmente: *"el sistema debe diseñarse como la app de FILEY que sirva para múltiples propósitos: expositores, asistentes a eventos/talleres/conferencias (agenda personalizada), asistentes generales... un mismo usuario puede ser expositor y asistente a la vez sin volver a registrarse"*. Esta segunda plática es exactamente esa ampliación: ya no es una idea a futuro, es una reunión completa dedicada a diseñar el módulo de "Programa Académico y Cultural" con la misma lógica de identidad única.
3. **El patrón de flujo es el mismo que el de espacios/stands**, aplicado a otro dominio:

   | Espacios/Stands (plática 1) | Programa Académico (plática 2) |
   | --- | --- |
   | Expositor entra, ve mapa, selecciona espacio | Escuela entra, ve agenda, selecciona actividad |
   | Carrito → ficha de reserva | Propuesta → ficha de actividad |
   | Reservado (azul) → admin valida pago → vendido (verde) | Propuesta recibida → admin acepta/rechaza → confirmada |
   | Vencimiento automático si no paga a tiempo | Vencimiento/liberación si la escuela no confirma a tiempo |
   | Notificación por correo en cada paso | Notificación por correo en cada paso |
   | Roles: expositor / administrador | Roles: proponente / Hipólito / coordinadora infantil-juvenil (cada uno con su propio "espacio" que administrar) |

   Es, literalmente, el **mismo motor de "convocatoria → revisión → asignación → confirmación → notificación"** reutilizado para un dominio distinto. Esto es una señal fuerte de que conviene diseñarlo como un módulo genérico reutilizable, no como código separado para cada coordinación (ver recomendaciones).

4. **RF-17 (Configuración de fechas clave)**, ya documentado en `requisitos_ideas.md`, se confirma y se generaliza: esta plática agrega un segundo conjunto completo de fechas configurables (apertura/cierre de convocatoria de propuestas, fecha de primeras respuestas, ventana de modificación, cierre de registro escolar) que son independientes de las fechas de espacios/stands. El sistema necesita fechas configurables **por módulo**, no una sola fecha global.
5. **RNF-06/RF-09 (roles)** quedan claramente insuficientes: la plática original solo distinguía expositor/administrador. Aquí aparecen *al menos* dos roles administrativos adicionales con permisos sobre áreas distintas (Hipólito ve y gestiona su programa; la coordinadora ve y gestiona el suyo; ninguno necesita ver todo lo del otro salvo para detectar conflictos de agenda). Ver sección de incongruencias.
6. La idea de **identidad única + login sin contraseña** es la respuesta concreta, a nivel técnico, a cómo lograr que "un mismo usuario pueda ser expositor y asistente a la vez sin volver a registrarse" (frase textual de la plática 1). Antes era una aspiración; ahora hay una propuesta de mecanismo (correo+teléfono como llave, código de un solo uso).

**Conclusión de la relación:** no son dos sistemas — es **un solo sistema FILEY con (al menos) dos módulos de negocio**: (1) Gestión de Espacios/Stands (ya detallado en la plática 1) y (2) Programa Académico y Cultural (esta plática), ambos construidos sobre una capa compartida de identidad de usuario, notificaciones y panel administrativo. El stack tecnológico ya elegido (React+Vite, Godot para mapas/grids, FastAPI, PostgreSQL, JWT, Resend, R2) sigue siendo válido para este módulo — de hecho se vuelve más rentable, porque ahora se reutiliza entre dos módulos en vez de uno.

---

## 3. ¿Qué quieren ellos en el sistema? — Síntesis

Pedido explícito de **Hipólito**:
- Automatizar la convocatoria de propuestas (recepción, revisión, aceptar/rechazar con notificación automática).
- Ver en todo momento cuántos espacios/horarios le quedan disponibles mientras revisa.
- Asignar horario/salón con una vista tipo calendario que le muestre qué bloques están libres (como Outlook/Google Calendar), evitando duplicar horarios sin darse cuenta.
- Que el proponente reciba y confirme su horario asignado, con una ventana acotada para pedir cambios.
- Generar la misma "ficha" que hoy hace a mano (PDF) sin tener que mantener la macro de Word.
- Administrar salones/salas como catálogo (poder agregar, quitar, renombrar).

Pedido explícito de la **coordinadora infantil-juvenil**:
- Que las escuelas elijan su actividad y horario directamente (estilo boleto de cine), en vez de que ella negocie uno por uno.
- Controlar cupo por institución para que una sola escuela no agote una actividad popular.
- Recordatorios y confirmaciones automáticas para reducir su seguimiento manual (llamadas, WhatsApp).
- Mantener un registro abierto solo informativo para escuelas que llegan sin haberse registrado a tiempo.
- Conservar flexibilidad manual para casos especiales (intercambios de grupo, negociaciones con talleristas).
- Un reemplazo digital de su actual "concentrado" en Excel/Word de ~300 fichas.

Pedido implícito/compartido por ambos:
- Que el sistema detecte si la misma persona quedó programada dos veces en horarios encimados entre los dos programas.
- Que el correo de notificaciones salga de una cuenta institucional confiable y se pueda saber si se abrió.
- Una cartelera en vivo / QR que reemplace las carpetas impresas y el trabajo manual de diseño gráfico para señalética.
- No tener que volver a capturar los mismos datos básicos (nombre, correo, teléfono) cada vez que alguien participa en otra cosa de FILEY.

---

## 4. Incongruencias, ambigüedades y puntos a verificar

1. **Modelo de roles desactualizado.** `requisitos_ideas.md` (RF-09, RNF-06) solo contempla dos roles: expositor y administrador. Esta plática deja claro que habrá *varios* roles administrativos con permisos acotados a su propia área (Hipólito, coordinadora infantil-juvenil, y posiblemente arte visual o futuras coordinaciones), comparado explícitamente por ellos mismos con permisos "tipo Google Drive". **Esto no es un error de la plática anterior, es información nueva que la vuelve incompleta** — hay que generalizar el modelo de roles a "permisos por módulo/área" antes de construir el panel de admin, o se va a tener que rehacer.
2. **Autenticación: dos propuestas distintas convivientes, sin reconciliar explícitamente.** La plática 1 asumía JWT + OAuth2 (típicamente con contraseña). Esta plática propone acceso **sin contraseña** vía código de un solo uso al correo, pensado para usuarios que entran una vez al año (expositores, escuelas, talleristas, público). Técnicamente no son incompatibles (un código de un solo uso puede emitir igualmente un JWT de sesión), pero **nadie en ninguna de las dos pláticas decidió esto explícitamente para los roles administrativos** (Hipólito, coordinadora, admin de espacios) — ¿ellos también entran con código de un solo uso, o mantienen credencial fija porque entran todos los días durante meses? Recomiendo decidirlo explícitamente: típicamente conviene contraseña/sesión persistente para roles operativos frecuentes, y código de un solo uso para los roles "de una vez al año" (expositor, escuela, tallerista, público).
3. **Conteo de salones de Hipólito no cierra.** En el audio dice *"yo tengo 13 en total, 3 salones y 3 salas"* — 3+3 no da 13. Puede ser un error de la transcripción automática (probablemente dijo otro número, o se refería a algo distinto con "13"). **No se debe tomar ese "13" como dato real** — hay que confirmárselo directamente a Hipólito antes de modelar el catálogo de salones.
4. **Fechas clave mencionadas son de la edición en curso, no reglas fijas.** Tanto el cierre de convocatoria de propuestas (~mediados de agosto), como el 6 de octubre (primeras respuestas), 3–30 de noviembre (ventana de cambios) y ~10 de diciembre (cierre total) se mencionaron de forma poco precisa y se pisan parcialmente con las fechas ya anotadas para espacios/stands (15 de noviembre como límite de pronto pago/primer pago). No son necesariamente incongruentes —son módulos distintos— pero **refuerzan que el sistema necesita un calendario de fechas configurable por módulo (ya cubierto conceptualmente por RF-17), y ninguna fecha debe quedar fija en código.**
5. **Duplicidad de registros de escuela como problema reconocido pero sin solución decidida.** Identificaron el problema (una escuela registrándose 3 veces con personas distintas para sumar más niños) pero no llegaron a una solución concreta más allá de "ya veremos". Vale la pena proponérselo como pregunta abierta en la siguiente sesión: ¿se valida por nombre de escuela (CCT/clave de centro de trabajo) en vez de por persona que registra?
6. **Caso de "cuota de recuperación" mencionado pero no decidido.** Hipólito especuló sobre cobrar por el uso de espacio/mobiliario en congresos a futuro — esto contradiría la idea actual de que el programa académico es gratuito para quien propone. No se decidió nada; no debe modelarse como requisito todavía, solo dejarlo anotado como posible evolución futura (igual que el punto de pasarela de pago en la plática 1, que también quedó "pendiente de decisión").
7. **Arte visual: registrado internamente, pero ¿quién lo captura?** Acordaron que no será público, pero no quedó claro si **el equipo de arte visual capturará directamente en el sistema** o si seguirán mandando un Excel/correo a alguien más para que lo capture por ellos — vale la pena confirmarlo, porque cambia si necesitan o no una cuenta de usuario.
8. **Nombres de hablantes no confirmados con certeza.** La transcripción automática nunca dice el nombre real de la coordinadora infantil-juvenil (Orador 3) ni de "la maestra" que se menciona como superior jerárquica — se documentó por rol, no por nombre, para no inventar un nombre que el audio no dio con claridad.

---

## 5. Recomendaciones del sistema (para este módulo)

Se reutiliza el stack ya decidido en `resumen_platica.md` (React+Vite, Tailwind/shadcn, FastAPI, PostgreSQL, SQLModel, JWT, R2, Resend, Vercel+Railway). Lo que agrega esta plática:

1. **Diseñar un módulo genérico de "Convocatoria → Revisión → Asignación → Confirmación"**, parametrizable por tipo (espacio/stand, propuesta de programa general, taller, visita escolar), en vez de construir cuatro flujos separados. Las cuatro coordinaciones describieron, sin saberlo, el mismo patrón de estados. Un solo motor de estados + notificaciones reduce muchísimo el trabajo de mantenimiento futuro y hace consistente la experiencia.
2. **Tabla de identidad única de persona/institución**, con `nombre + correo + teléfono` como llave de identificación entre módulos (no solo nombre). Permite: reconocer al mismo usuario en distintos módulos, detectar conflictos de agenda entre coordinaciones, y evitar re-captura de datos básicos.
3. **Login sin contraseña (passwordless / código de un solo uso por correo)** para los roles "de uso esporádico" (expositor, escuela, tallerista, proponente, público general). Para roles operativos internos (Hipólito, coordinadores, admin) se recomienda mantener sesión persistente normal (usuario/contraseña u OAuth2 corporativo), ya que entran con frecuencia y necesitan trazabilidad estable — esto resuelve la incongruencia #2 de arriba.
4. **Modelo de permisos por módulo/área** (no solo "admin sí/no"): cada coordinador ve y administra únicamente su propio catálogo de espacios/actividades, con un rol superior ("la maestra"/admin general) que ve todo. Es exactamente el patrón de permisos de Google Drive que ellos mismos mencionaron como referencia — vale la pena tomarlos literalmente esa metáfora para el diseño de roles en FastAPI (scopes por módulo en el JWT).
5. **Catálogo administrable de salones/salas/espacios de programación**, separado del catálogo de stands pero con la misma forma (id, nombre, capacidad, tipo de uso), reutilizable tanto por Hipólito como por la coordinadora infantil-juvenil — y con vista tipo calendario (slots libres/ocupados) para asignar horario sin choques, igual que pidieron explícitamente comparándolo con Outlook.
6. **Generación de "ficha" en PDF desde el sistema** (reemplazando la plantilla Word+macro de Hipólito y el Excel-a-PDF de la coordinadora), reutilizando el mismo generador de PDFs que ya se planea para las fichas de reserva de stands.
7. **Notificaciones transaccionales desde el dominio filey.org**, con seguimiento de apertura (Resend ya soporta esto de forma nativa) — confirma y refuerza la elección de Resend hecha en la plática 1, ahora con un caso de uso explícito (evitar que los correos de Hipólito/coordinadora se vayan a spam o se confundan con su Gmail personal).
8. **Vista de "cartelera en vivo"**: una pantalla de solo lectura, generada automáticamente a partir de la agenda ya cargada en base de datos, filtrando "qué ocurre ahora / qué sigue", accesible por URL pública (para proyectar en pantallas físicas) y por QR. Es una pieza de bajo costo de desarrollo (una consulta a la agenda + un refresco periódico) con alto impacto percibido, vale la pena priorizarla como "quick win" para la próxima demo.
9. **Agenda pública filtrable para visitantes** (inspirada en la app de FIL Guadalajara que Hipólito describió): filtros por categoría/sección, ficha de detalle, "agregar a mi agenda"/descartar. Esto es la materialización concreta del punto J de la plática 1 ("asistentes a eventos: agenda personalizada") — puede construirse sobre la misma tabla de actividades/agenda que ya alimenta la cartelera en vivo (punto 8), simplemente con una interfaz orientada al público en lugar de a pantallas de señalización.
10. **No automatizar WhatsApp todavía.** Quedó explícitamente fuera de alcance (ya tuvieron un bloqueo por mensajes masivos); no meterlo en el plan de esta fase.

---

## 6. Mapa general del sistema FILEY (con ambos módulos)

```
                         ┌────────────────────────────┐
                         │   IDENTIDAD ÚNICA FILEY     │
                         │ nombre + correo + teléfono  │
                         │  login sin contraseña (OTP) │
                         └──────────────┬───────────────┘
                                        │
            ┌───────────────────────────┼────────────────────────────┐
            │                           │                            │
 ┌──────────▼─────────┐      ┌──────────▼──────────┐      ┌──────────▼──────────┐
 │ MÓDULO ESPACIOS     │      │ MÓDULO PROGRAMA      │      │ MÓDULO ESCOLAR /     │
 │ (plática 1)         │      │ GENERAL (Hipólito)   │      │ TALLERES (coord.     │
 │                     │      │                       │      │ infantil-juvenil)    │
 │ Mapa Godot de stands│      │ Convocatoria de       │      │ Convocatoria de       │
 │ Carrito → reserva   │      │ propuestas → revisión │      │ talleres + agenda de  │
 │ Pago manual + CFDI  │      │ → salón/horario →     │      │ visitas escolares     │
 │                     │      │ confirmación           │      │ (estilo "boleto de    │
 │                     │      │                       │      │ cine")               │
 └─────────────────────┘      └───────────────────────┘      └───────────────────────┘
            │                           │                            │
            └───────────────┬───────────┴────────────┬───────────────┘
                             │                        │
                  ┌──────────▼──────────┐   ┌──────────▼──────────┐
                  │ Notificaciones       │   │ Cartelera en vivo /  │
                  │ (Resend, filey.org)  │   │ Agenda pública (QR)  │
                  └───────────────────────┘   └───────────────────────┘
```

Ambos módulos comparten identidad, notificaciones y el patrón "convocatoria → revisión → asignación → confirmación" — son ramas del mismo sistema, no proyectos separados.

---

## 7. Pendientes y próximos pasos (de esta plática)

- [ ] Confirmar con Hipólito el conteo real de salones/salas (el "13 en total, 3+3" no cierra) **(ellos)**
- [ ] Definir fechas clave reales del programa general y de visitas escolares para esta edición, y confirmar que no chocan con las de espacios/stands **(ellos)**
- [ ] Decidir mecanismo para detectar escuelas que se registran varias veces con personas distintas **(nosotros + ellos)**
- [ ] Confirmar si arte visual capturará directamente en el sistema o seguirá mandando su información a un tercero **(ellos)**
- [ ] Decidir explícitamente el método de autenticación para roles administrativos (Hipólito, coordinadores) vs. el código de un solo uso para usuarios esporádicos **(nosotros)**
- [ ] Producir wireframes/mockups del módulo de Programa General y del módulo Escolar/Talleres **(nosotros)**
- [ ] Confirmar uso de cuentas `@filey.org` para notificaciones automatizadas **(ellos)**
- [ ] Documentar y compartir por escrito todo lo acordado antes de fin de mes **(nosotros)**
- [ ] Próximas 1–2 sesiones de revisión visual antes de presentar a "la maestra" **(ambos)**
