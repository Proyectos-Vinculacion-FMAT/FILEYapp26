---
estado: nota
version: 1.1
tags:
  - tipo/analisis
  - dom/vis
fecha: 2026-06-21
fecha_actualizacion: 2026-06-25
fuente_a: "docs/requisitos/VIS/ (CU-VIS-001 … CU-VIS-017)"
fuente_b: "docs/soporte/extraido/Software para agendar escuelas.md"
---
# Análisis comparativo: CUs de VIS ↔ "Software para agendar escuelas"

**Material comparado:** los CUs de [VIS](../../requisitos/VIS/) (a nivel de objetivo, que
es lo único redactado; el resto de cada CU es plantilla) contra
[Software para agendar escuelas](../extraido/Software%20para%20agendar%20escuelas.md).

**Nota de método:** la fuente describe el proceso *actual* (forms + autocrat + Excel) y una
*propuesta de resolución* autoservicio. Los CUs ya asumen la homologación al ciclo de
propuestas de `REG` (ver nota de alcance del
[índice CU-VIS](../../requisitos/VIS/CU-VIS%20Índice.md)).

> [!success] Revisión 2026-06-25
> Cada hallazgo fue revisado con el cliente interno. Se conserva el texto original del análisis
> y debajo de cada punto se añade su **Resolución**. Cambios principales: **C2 y C3 dejaron de
> ser contradicciones** (eran confusiones del análisis); **R7 se redirige** a `TAL`/`EVT`/`REG`,
> no es de `VIS`; el resto se tradujo a ediciones concretas en los CU, callouts y notas.

---

## 1. Contradicciones

### C1 — Validación de cupo vs. división del grupo (impacto: alto, lógica central)

[CU-VIS-011](../../requisitos/VIS/C%20-%20Catálogo%20y%20reserva%20de%20talleres/CU-VIS-011%20Validar%20que%20el%20cupo%20restante%20del%20taller%20cubra%20la%20cantidad%20de%20visitantes.md)
decía: *"impida reservar un taller cuyo cupo restante sea menor a la cantidad de visitantes que
la institución representa"*. Es decir, validaba **al grupo completo contra un solo taller**.

La fuente (líneas 42, 50) dice lo contrario: el salón Ek Balam es de **35 personas máximo**, y
una escuela de hasta **105 alumnos** se agenda *"3 talleres de 35 personas para ocupar los 105
espacios"* — el grupo **se divide entre varios talleres**. Con la regla anterior, una escuela
de 105 alumnos **nunca podría reservar un taller de Ek Balam** (cupo 35 < 105), bloqueando el
caso que la fuente describe como normal.

> [!check] Resolución (confirmada)
> La fuente tiene razón, el CU estaba mal. Se reescribió el objetivo de **CU-VIS-011**: la
> validación es por la **cantidad asignada a cada taller** contra su cupo restante, **no** por el
> total del grupo; el grupo puede repartirse entre varias actividades. Se añadió la regla de
> negocio (restricción) correspondiente.

### C2 — "Itinerario al momento" vs. compuerta de aceptación previa → **no es contradicción**

El análisis original lo leyó como que el modelo de los CUs (registrar → aceptar → reservar)
contradecía el *"al momento"* de la fuente (línea 36).

> [!check] Resolución
> Era una confusión del análisis. El *"al momento"* de la fuente significa que la escuela elige **en cuanto tiene la capacidad
> de hacerlo**, eliminando el ida y vuelta que antes hacía falta (la coordinación enviaba el
> catálogo y esperaba la respuesta para confirmar a qué taller iban); **no** significa ausencia
> de validación. Además, el **horario** de las actividades es consultable por cualquiera vía la
> URL estática del programa (CU-PRG-010); lo que cambia con `VIS` es la **capacidad de reservar**.
>
> Queda **una duda abierta** (no una contradicción): qué **validación o aprobación previa**
> existe antes de que una visita escolar pueda reservar. Se entiende que habrá *alguna*, pero no
> se sabe cuál. **Callout añadido** en el [índice VIS](../../requisitos/VIS/CU-VIS%20Índice.md) y
> pregunta en [Preguntas para la siguiente sesión](../../soporte/meetings/meeting%20notes/Preguntas%20para%20la%20siguiente%20sesion.md#visitas-escolares).

### C3 — Correo de confirmación: comprobante vs. aviso de resultado → **no es contradicción**

El análisis original sostuvo que ningún CU cubría el comprobante del itinerario que pide la
fuente (líneas 54-56).

> [!check] Resolución
> Se confundió la **confirmación de itinerario** con el **registro para ser visita escolar**. La
> fuente habla del **itinerario**, que se arma cuando la escuela **selecciona y reserva**
> (CU-VIS-012) y se consulta en CU-VIS-013. Eso **ya está cubierto**.
>
> Queda **una duda abierta**: ¿la vista del itinerario se **envía por correo automáticamente** o
> basta con **verla/descargarla desde la app**? **Callout/pregunta añadidos.**

---

## 2. Roces

### R1 — Reglas de "candado" combinatorio no modeladas → **regla de negocio (restricción)**

La fuente (líneas 50-52) define candados precisos que los objetivos de los CU no recogían:
sala de cine para 105 **o** 3 talleres de 35; un cupo para Gran Foro/académicas (con lista
previa); y *mismo día* preferente.

> [!check] Resolución
> Es una **restricción** (propiedad de la reserva), no un comportamiento ni un flujo. Se anotó
> como **regla de negocio** en CU-VIS-011 (equivalencia de cupo) y CU-VIS-012 (equivalencia de
> cupo + mismo día preferente).

### R2 — "Un taller por escuela" vs. "varios talleres"

El [índice](../../requisitos/VIS/CU-VIS%20Índice.md) y la
[Junta 2](../../soporte/meetings/resumenes/RSM%20-%20Junta%202%20con%20organizadores%20FILEY.md#pendientes-por-definir)
dejaban pendiente una política de *"un taller / un tipo de actividad por escuela"*, que choca
con la fuente (3 talleres por escuela).

> [!check] Resolución
> La **fuente tiene razón** (contempla varios talleres). Se actualizaron los callouts: nota de
> matiz en la Junta 2, warning en CU-VIS-012 y pregunta dedicada en Preguntas para la siguiente
> sesión. La política definitiva queda como pregunta al cliente.

### R3 — Captura de "cantidad de alumnos/visitantes" no explícita

Varios CU dependen de la cantidad de visitantes, pero CU-VIS-001 sólo declaraba capturar
*"datos de la escuela/institución y de su contacto"*.

> [!check] Resolución (confirmada)
> Se declaró **explícitamente** en CU-VIS-001 que la **cantidad de alumnos/visitantes** que
> asistirán debe registrarse en la propuesta (dato obligatorio).

### R4 — Granularidad "día y turno" vs. "días y horarios"

CU-VIS-010 filtra por *día y turno*; la fuente habla de *días y horarios*.

> [!check] Resolución
> Es una cuestión de **filtrado**. El filtro es por día y turno (matutino/vespertino), pero la
> **lista** de talleres ya muestra la **hora de inicio y fin** de cada uno. Se dejó **explícito**
> en el objetivo/nota de CU-VIS-010.

### R5 — "Saber automáticamente la cantidad total de alumnos" sin CU

La fuente (línea 58) pide un **agregado** de asistentes.

> [!check] Resolución
> Va en administración. Se añadió como **numeralia** (suma simple) en CU-VIS-015 (puede
> consultarse también en CU-VIS-016 o tratarse de forma transversal).

### R6 — CU-VIS-014 (quitar taller) sin respaldo + falta baja administrativa

> [!check] Resolución
> Se **acota CU-VIS-014** como **autocorrección del Participante** (quitar un taller elegido por
> error) **antes de generar el itinerario final**, y se **crea** **CU-VIS-017**: el
> **Administrador** puede dar de **baja manualmente** a una visita de un taller en casos de
> cancelación imprevista (mencionado en
> [Junta 2](../../soporte/meetings/resumenes/RSM%20-%20Junta%202%20con%20organizadores%20FILEY.md#pendientes-por-definir)).

### R7 — Curación previa de Foro/académicas → **no es de VIS**

> [!check] Resolución
> Este roce pertenece a `TAL`/`EVT`/`REG`, no a `VIS`. `VIS` sólo **muestra en el catálogo** las
> actividades **aptas para público infantil/juvenil** provenientes de propuestas **Aceptadas**,
> **sin importar la sala** donde se realicen (la sala determina su aforo, no su elegibilidad). Se
> aclaró en la nota de CU-VIS-010. La curación del subcatálogo elegible se trata en esos otros
> dominios.

---

## 3. Coincidencias (de mayor a menor impacto)

### Co1 — Autoservicio de catálogo de talleres (núcleo de la propuesta) — alto

CU-VIS-010 ↔ fuente línea 36. Es la solución medular que pidió FILEY, fielmente recogida.

### Co2 — Control de cupo / "Cupo lleno" — alto

CU-VIS-011 ↔ fuente línea 38. El *qué* coincide (el *cómo* se corrigió en C1).

### Co3 — Armar y consultar el itinerario — alto

CU-VIS-012 y CU-VIS-013 ↔ fuente línea 36. Concepto de itinerario fielmente trasladado (cubre
el comprobante; ver C3).

### Co4 — Administración: "qué escuela va a qué taller" — medio/alto

CU-VIS-015 y CU-VIS-016 ↔ fuente línea 56. Necesidad operativa de la coordinación bien cubierta.

### Co5 — Registro inicial de la escuela/contacto — medio

CU-VIS-001 ↔ fuente línea 24. Coincide en intención; ahora también captura la cantidad de
alumnos (R3).

### Co6 — Notificación automática por correo — medio

CU-VIS-009 ↔ fuente líneas 54-56. Coinciden en que hay correo automático del **resultado de la
revisión**; la entrega del **itinerario** (canal por confirmar) es la duda abierta de C3.

### Co7 — Capacidades por espacio como datos de referencia — bajo

Las capacidades de la fuente (Ek Balam 35, Cine 120, Gran Foro 600, académicas 50-250; líneas
42-48) sustentan el cupo de CU-011/016, como dato maestro.

---

## Resumen ejecutivo (tras revisión 2026-06-25)

| Estado | Hallazgo | Acción aplicada |
| --- | --- | --- |
| ✅ Corregido | **C1** validación de cupo bloqueaba grupos grandes | CU-VIS-011 reescrito: validar por cantidad asignada a cada taller; grupo divisible |
| 🟦 Aclarado + duda abierta | **C2** "al momento" no contradice; falta saber la validación previa a reservar | Callout/pregunta para la próxima junta |
| 🟦 Aclarado + duda abierta | **C3** itinerario ya cubierto (CU-VIS-013); falta canal de entrega | Callout/pregunta (correo vs. vista/descarga) |
| ✅ Anotado | **R1** candados como regla de negocio (restricción) | Notas RN en CU-VIS-011 y 012 |
| 🟧 Pregunta abierta | **R2** "un taller" vs. varios — fuente manda | Callouts en Junta 2, CU-VIS-012 y preguntas |
| ✅ Corregido | **R3** cantidad de alumnos en la propuesta | CU-VIS-001 actualizado |
| ✅ Explícito | **R4** filtro día/turno; lista muestra horas | Nota en CU-VIS-010 |
| ✅ Añadido | **R5** numeralia total de asistentes | CU-VIS-015 |
| ✅ Corregido + nuevo CU | **R6** CU-VIS-014 acotado; baja administrativa | CU-VIS-014 + nuevo CU-VIS-017 |
| ↪️ Redirigido | **R7** curación no es de VIS | Aclarado en CU-VIS-010; pertenece a TAL/EVT/REG |
