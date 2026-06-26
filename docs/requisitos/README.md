---
estado: propuesta
version: 0.4
tags:
  - tipo/referencia
  - tema/alcance
fecha: 2026-06-18
fecha_actualizacion: 2026-06-24
---
# README — Dominios y necesidades del cliente

Resumen de cómo se divide el sistema **FILEY** en dominios y qué información guarda cada uno. Sirve como índice y referencia de alcance para los **casos de uso** (`CU-DOM-NNN`) de cada dominio.

> [!tip] Navegación por etiquetas
> Además de por carpetas, todo el repositorio se navega por una taxonomía facetada en el
> frontmatter (`tipo/` · `dom/` · `tema/`). Los códigos `dom/` son los mismos que los de la
> tabla de dominios de abajo. Ver el [Mapa de etiquetas](<../MAPA-DE-ETIQUETAS.md>).

<!-- -->

> [!note] Actualización 2026-06-24
> Esta versión documentaba originalmente la primera propuesta de dominios (post Junta 1/2,
> con requisitos funcionales `RF-DOM-NN`). En la
> [Junta 3 con Equipo de desarrollo](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#1-contexto-y-alcance>)
> el equipo homologó los dominios, formalizó un core transversal de **Registros** (`REG`) y
> sustituyó los `RF-DOM-NN` por **casos de uso** (`CU-DOM-NNN`; ver la plantilla
> [`CU-XX-NN Template.md`](<CU-XX-NN Template.md>)). Esta revisión actualiza el mapa de dominios y enlaza cada uno a su
> **índice de CUs** y a la **evidencia** (juntas y material proporcionado por FILEY) que lo
> sustenta.

## Enfoque

El sistema se organiza por **dominios verticales**. Cada dominio tiene **uno o varios tipos de registro**, y cada tipo de registro es un **modelo de datos**: define qué información se guarda de quien solicita ese servicio.

Cada dominio documenta su alcance mediante **casos de uso** (`CU-DOM-NNN`); donde aplica, también un modelo de datos y un proceso de alto nivel propios (ver `STD/`, el más maduro de los cuatro dominios ya documentados).

> [!important]
> El **alcance de la primera entrega (agosto)** es el **registro de solicitantes**: capturar los datos de quienes exponen, dan talleres, rentan stands o agendan excursiones escolares. Es lo primero que ocurre, previo a la feria. Confirmado como objetivo de referencia en
> [Junta 2 con Equipo de desarrollo](<../soporte/meetings/resumenes/RSM - Junta 2 con Equipo de desarrollo.md>)
> ("Objetivo de entrega de referencia: agosto... no entra todo; se debe priorizar") y reiterado en
> [Junta 3](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md>). Los demás
> alcances (pagos con pasarela, acceso/verificación, reportes) están planeados a futuro y se
> documentan aquí como referencia, no como compromiso de esta entrega.

## Propiedades compartidas (no son dominios)

Estas características aparecen en todos los registros, pero **se infieren** como propiedades comunes; **no** se modelan como un dominio transversal:

- **Solicitud / registro:** el acto de llenar un formulario para solicitar un servicio (rentar, exponer, impartir, agendar).
- **Datos de contacto:** la identidad mínima de quien solicita (nombre y medio de contacto).
- **Tipo de participante:** quién puede participar — asociaciones civiles, comunidad-UADY, editoriales, instituciones culturales, universidades públicas y privadas, y otras instituciones.

> [!note]
> Se manejan como propiedad compartida —y no como dominio— porque ya hay clientes reales con necesidades aisladas por dominio, y cada una se expresa fácilmente como una historia de usuario propia. Organizar por dominio mantiene esas necesidades concretas y separadas.

<!-- -->

> [!info] Actualización (Junta 3) — ahora formalizadas en el core `REG`
> Lo que aquí se infería como propiedad compartida hoy tiene un modelo de datos propio: el
> core transversal de **Registros / Convocatorias** (`REG`), descrito en
> [Junta 3 §2.2](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#22-registros-reg>).
> *Solicitud/registro* es la **Propuesta** que resulta de llenar un **Formulario para
> aplicantes**; *Datos de contacto* y *Tipo de participante* son **Preguntas** dentro de sus
> **Bloques de preguntas**. `REG` es responsabilidad de Juan Manuel Miranda y unifica la
> captura de `STD`, `EVT`, `TAL` y `VIS`; aún no tiene carpeta propia en `requisitos/` (ver
> [Organización de los requisitos](#organización-de-los-requisitos)).

## Mapa de dominios

### Dominios prioritarios — primera entrega (agosto)

Homologado en
[Junta 3 §1 — Contexto y alcance](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#1-contexto-y-alcance>)
(tabla de dominios) y
[§4 — Acciones por actor](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#4-acciones-por-actor>).

| Código | Dominio | Ámbito | Responsable (equipo) | Necesidad de (cliente) | Artefactos |
| ------ | ------- | ------ | --------------------- | ----------------------- | ---------- |
| `REG` | Registros / Convocatorias | Transversal: captura y revisión de propuestas para `STD`/`EVT`/`TAL`/`VIS` | Juan Manuel Miranda | — | Pendiente: aún sin carpeta en `requisitos/` |
| `STD` | Stands / Expositores | Renta, reserva, pago y confirmación de espacios en el showfloor | Hugo Janssen | Hipólito / Gilberto | [`STD/CU-STD Índice.md`](<STD/CU-STD Índice.md>) · `Modelo de datos - Stands.md` · `Proceso de alto nivel - Stands.md` |
| `EVT` | Eventos | Actividades de público general (conversatorio, conferencia, charla, mesa redonda, presentación de libro/revista, lectura de obra, encuentro) | Juan Manuel Miranda | Hipólito | Pendiente: aún sin carpeta en `requisitos/` |
| `TAL` | Talleres | Actividades de aforo reducido, normalmente infantil/juvenil | Juan Manuel Miranda | Elvira | Pendiente: aún sin carpeta en `requisitos/` |
| `VIS` | Visitas escolares | Itinerarios de instituciones que reservan cupo en el catálogo de talleres/actividades | Isaac Ortiz | Elvira | [`VIS/CU-VIS Índice.md`](<VIS/CU-VIS Índice.md>) |
| `PRG` | Programa General | Organización espacio-temporal de las actividades aceptadas de `EVT`/`TAL` | Isaac Ortiz | Hipólito / Elvira | [`PRG/CU-PRG Índice.md`](<PRG/CU-PRG Índice.md>) |
| `SAL` | Salas y salones | Catálogo único de espacios (salones y sus salas) | Isaac Ortiz | Hipólito / Elvira | [`SAL/CU-SAL Índice.md`](<SAL/CU-SAL Índice.md>) |

> [!warning] Dos renombres respecto a versiones anteriores de este README
>
> - **`EVE` → `EVT`:** el dominio de eventos generales se llamaba `EVE` en la propuesta inicial; la Junta 3 lo homologó como `EVT`.
> - **`VIS` cambió de significado:** antes era el código reservado para *"Contabilidad de visitantes"* (dominio futuro, ver abajo). La Junta 3 lo reasignó a **Visitas escolares**, que pasó de considerarse "fuera de scope" a ser un dominio prioritario — ver el roce R1 del
>   [Análisis de archivos proporcionados](<../soporte/extraido/Analisis de archivos proporcionados.md>)
>   y la necesidad original del cliente en
>   [Software para agendar escuelas](<../soporte/extraido/Software para agendar escuelas.md>).
>   La antigua *"Contabilidad de visitantes"* sigue pendiente, pero necesita un código nuevo (ver nota en la tabla de dominios futuros).

<!-- -->

> [!note]
> `EVT` es el dominio con más variantes y funciona como **calendario maestro**: además de sus formatos propios, integra los talleres que Elvira organiza en `TAL` (un taller es un tipo de evento, ver
> [Junta 2 con Equipo de desarrollo](<../soporte/meetings/resumenes/RSM - Junta 2 con Equipo de desarrollo.md>),
> sección "Nuevas directrices y para cuándo").

<!-- -->

> [!note]
> El dominio `STD` abarca, además del registro del arrendatario, el **proceso de reserva, pago y confirmación** de stands. Sus artefactos viven en `STD/`: índice de casos de uso ([`CU-STD Índice.md`](<STD/CU-STD Índice.md>)), modelo de datos (`Modelo de datos - Stands.md`) y proceso de alto nivel (`Proceso de alto nivel - Stands.md`). Esto **resuelve** el pendiente que tenía este README sobre si ese flujo entraba en la primera entrega: hoy ya está documentado con CUs propios.

### Dominios futuros — no prioritarios

Ordenados por la prioridad esperada después de la primera entrega. Sin ajustes de la Junta 3 (no se trataron en esa sesión, ver su nota de alcance); se mantienen tal como se identificaron en juntas anteriores con FILEY.

| Orden | Código | Dominio | Necesidad que cubre | Condición | Evidencia |
| ----- | ------ | ------- | -------------------- | --------- | --------- |
| 1 | `PAG` | Pagos | Confirmar el cobro asociado a un registro aprobado (pasarela electrónica). | Sujeto a decisión del cliente; esta edición usa validación manual de comprobantes. | [Junta 3 §1](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#1-contexto-y-alcance>) ("el flujo de pago... se aborda por separado"); detalle de pasarela en [Junta 1 con organizadores FILEY](<../soporte/meetings/resumenes/RSM - Junta 1 con organizadores FILEY.md>), sección "Método de cobro: pasarela vs. manual". |
| 2 | `ACC` | Acceso y verificación | Verificar la entrada de visitantes a la feria (QR u otro). | Mecanismo por definir. | Sin evidencia nueva en juntas con FILEY; se mantiene como en la propuesta inicial. |
| 3 | `CNT` *(antes `VIS`)* | Contabilidad de visitantes | Contar a los visitantes registrados. | Va al final; **código por reasignar** porque `VIS` ahora es Visitas escolares (ver advertencia arriba). | [Junta 2 con organizadores FILEY](<../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md>), sección "Identidad, acceso y permisos" (sistema de registro de visitantes anterior, con nombre/correo/procedencia/edad). |
| 4 | `REP` | Reportes | Generar reportes a partir de los datos. | Secundario. | Sin evidencia nueva en juntas con FILEY; se mantiene como en la propuesta inicial. |

## Organización de los requisitos

Los requisitos **se dividen por dominio** y se documentan como **casos de uso** (`CU-DOM-NNN`), no como `RF-DOM-NN` (convención reemplazada en la homologación de la
[Junta 3](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#1-contexto-y-alcance>)). Cada dominio con CUs ya escritos tiene su propia carpeta, con un índice (`CU-DOM Índice.md`) que enlaza cada caso de uso a su archivo y a la evidencia que lo sustenta.

```text
requisitos/
├── README.md
├── CU-XX-NN Template.md
├── PRG/   → CU-PRG-NNN  (programa general; ver PRG/CU-PRG Índice.md)
├── SAL/   → CU-SAL-NNN  (salas y salones; ver SAL/CU-SAL Índice.md)
├── STD/   → CU-STD-NNN  (stands; incluye índice de CU, modelo de datos y proceso de alto nivel)
└── VIS/   → CU-VIS-NNN  (visitas escolares; ver VIS/CU-VIS Índice.md)
```

> [!note]
> `REG`, `EVT` y `TAL` (responsabilidad de Juan Manuel Miranda) todavía no tienen carpeta en
> este repositorio. Al abrirse, seguir la misma convención: carpeta `DOM/`, índice
> `CU-DOM Índice.md` y un archivo por caso de uso a partir de [`CU-XX-NN Template.md`](<CU-XX-NN Template.md>).

<!-- -->

> [!note]
> Cada carpeta de dominio agrupa solo sus casos de uso. Crear una carpeta nueva al abrir un dominio adicional (p. ej. `PAG/`, `ACC/`) siguiendo la misma convención.

## Relación entre dominios

- `REG` (Convocatorias) es el **paso previo transversal**: cualquier propuesta de `STD`, `EVT`, `TAL` o `VIS` se captura y revisa ahí; al **Aceptarse**, el Aplicante pasa a Participante y, si es de tipo `EVT`/`TAL`, la propuesta se convierte en **Actividad** (ver
  [Junta 3 §2.2](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#22-registros-reg>)
  y
  [§2.1](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#21-actores>)).
- Elvira organiza los talleres en `TAL`; al cerrarlos, Hipólito los **anexa al calendario maestro** de `EVT`. Por eso `EVT` "hereda" los talleres como entradas de calendario, aunque su modelo de datos viva en `TAL` (sin cambios respecto a la propuesta inicial).
- `PRG` consume las **Actividades Aceptadas** de `EVT`/`TAL` y las asigna a una sala/bloque de `SAL`; `SAL` es el catálogo único de espacios del que `PRG` depende (ver
  [PRG/CU-PRG Índice.md](<PRG/CU-PRG Índice.md>)
  y
  [SAL/CU-SAL Índice.md](<SAL/CU-SAL Índice.md>)).
- `VIS` depende de `EVT`/`TAL`: una visita escolar reserva **cupo** en actividades que Hipólito o Elvira marcaron como aptas para nivel infantil/juvenil (ver
  [Junta 2 con organizadores FILEY](<../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#tipos-de-eventos>)
  y
  [Junta 3 §4.3](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#43-participante>)).
  `VIS` no genera Actividad ni entra al programa de `PRG` por sí misma; solo consume cupo de actividades que ya están ahí.

## Pendientes por validar

- Si los **pagos** (`PAG`) entran en alcance y bajo qué condiciones (decisión del cliente); no se trató en
  [Junta 3](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#1-contexto-y-alcance>).
- El **modelo de notificaciones** (`REG`/`PRG`): ¿concentrado transversal o por módulo? — decisión pendiente
  [D3](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d3--modelo-de-notificaciones-reg--prg>).
- El **dominio del CRUD de bloques de horario** (`PRG` o `SAL`) — decisión pendiente
  [D2](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d2--dominio-del-crud-de-bloques-de-horario-prg--sal>).
- El **alcance del armador de convocatorias/formularios** de `REG` (herramienta dev-side vs. embebida) — decisión pendiente
  [D1](<../soporte/meetings/resumenes/RSM - Junta 3 con Equipo de desarrollo.md#d1--alcance-del-armador-de-formularios-reg>).
- **Edición manual del programa** sin pasar por una propuesta aceptada (artísticos de control interno, ajustes de "pulida final") — hueco R5 del
  [Análisis de archivos proporcionados](<../soporte/extraido/Analisis de archivos proporcionados.md>),
  aún sin CU dedicado en `PRG`.
- **Registro interno de artísticos** (Artes Visuales, Escénicas, Cinematográficas) con sus propios rubros — huecos R6/R7 del mismo análisis; sin CU dedicado todavía.
- Si la **contabilidad de visitantes** (futuro `CNT`, antes `VIS`) y los **reportes** (`REP`) entran en alcance posterior, y bajo qué código se documenta la primera ahora que `VIS` está tomado.
- Detalle real del **formulario de aplicación de visita escolar** y la política de **un taller por escuela** — ver pendientes listados en
  [VIS/CU-VIS Índice.md](<VIS/CU-VIS Índice.md>).

> [!note]
> El detalle de qué información guarda cada tipo de registro **no vive aquí**: es responsabilidad de cada dominio (`CU-DOM Índice.md`) y sus artefactos relacionados.
