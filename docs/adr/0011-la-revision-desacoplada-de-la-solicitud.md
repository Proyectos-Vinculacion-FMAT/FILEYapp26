---
estado: propuesta
version: "0.1"
tags:
  - tipo/adr
  - dom/evt
  - dom/tal
  - tema/arquitectura
fecha: 2026-09-04
id: ADR-0011
responsable: Isaac Ortiz
supersede:
reemplazado_por:
---
# ADR-0011. Dónde vive la revisión de una propuesta: columnas de `Solicitud` o entidad propia

## Estado

`Propuesto` — 2026-09-04.

**Mientras se discute gobierna lo que ya está mergeado en `develop`: los campos del dictamen son
columnas de `Solicitud`.** No es una decisión provisional por comodidad — es que la alternativa
solo se puede diseñar bien cuando se sepa qué necesita `TAL`, y ese modelo de datos está en
revisión.

Este ADR existe para que la pregunta no se pierda: se descubrió resolviendo un conflicto de
merge, que es el peor sitio donde tomar una decisión de arquitectura y el mejor donde
detectarla.

## Contexto

El 2026-09-03 y el 2026-09-04, dos ramas resolvieron **el mismo problema de formas
incompatibles**, sin saberlo, y las dos numeraron su migración `0004`:

| | `feature/evt-panel-propuestas` (mergeada en `develop`) | `isaac-develop` |
| --- | --- | --- |
| Necesidad | Dictaminar una propuesta (`CU-EVT-007` a `011`) | Enseñar el desenlace a quien propuso (`CU-EVT-003` paso 4) |
| Dónde puso el dictamen | Columnas de `Solicitud` | Tabla `DetallesAdminSolicitud` |
| `Solicitud.estado` | Se queda | Se muda a la tabla nueva |

Las dos son defendibles y las dos están argumentadas por escrito.

**A favor de las columnas** —lo que dice el modelo de datos de `develop`—: la relación que
describe `Modelo de datos - Eventos` §3.1 es *uno a uno obligatoria, con la fila creada al
enviarse la solicitud*, y eso es la definición de una columna con un `JOIN` de más. `estado`
además ya vivía en `Solicitud`. Es el trato que `STD` le da a la suya.

**A favor de la entidad propia**: el §3.1 describe un diagrama entidad-relación, no un esquema
de Django, y lo que separa no es la cardinalidad sino **quién escribe**. La solicitud la escribe
quien propone; la revisión, quien administra. Con las columnas juntas, toda convocatoria de tipo
`EVT` comparte una única forma de revisar, para siempre.

### Lo que hace que esto no sea académico

`apps/convocatorias/models.py` dice, en el código y no en un plan:

> `TAL` no está, y está pendiente a propósito: falta decidir si es un cuarto tipo o una
> convocatoria `EVT` con otro público.

Si `TAL` acaba siendo **una convocatoria `EVT` con otro público** —los talleres infantiles y
juveniles que coordina Elvira—, entonces dos convocatorias del mismo tipo tendrán:

- campos distintos que capturar,
- y sobre todo **criterios distintos que revisar**: lo que Elvira comprueba de un taller
  infantil no es lo que Hipólito comprueba de una mesa redonda.

Con la revisión desacoplada, una convocatoria se engancha a la forma de revisión que le sirve,
como un vertical se engancha a su módulo (`ADR-0006`) o como una actividad se engancha a su
tabla de tipo (`ADR-0009`). Con la revisión en columnas, o se comparte una forma que no le sirve
a nadie del todo, o se añaden columnas que sobran en la mitad de las filas.

### Lo que ya cuesta cambiarlo

Medido el 2026-09-04 sobre `develop`: **~155 referencias en 16 archivos**. Las que importan no
son las más numerosas:

| Dónde | Qué es lo delicado |
| --- | --- |
| `servicios/dictamen.py` | El `select_for_update()` que bloquea la fila, el `update_fields` de ocho campos, y el `__dict__.update` con el que la vista refresca su objeto |
| `servicios/revision.py` | `filter(estado=…)`, `filter(categoria=…)` y el `values("estado").annotate(Count)` de los conteos: pasan a agrupar por una tabla unida |
| `models.py` | `esta_dictaminada` y `categoria_completa`, que leen esos campos |
| `pruebas/test_panel_propuestas.py` | 49 referencias, mecánicas pero todas |

Y la migración `0004` de `develop`, ya aplicada en las bases de quien haya trabajado con esa
rama.

**Este número solo sube.** Aplazar la decisión no la abarata; la encarece. Es la fuerza que
empuja a decidirlo pronto, y la razón de que este ADR se escriba ahora y no cuando estorbe.

## Opciones consideradas

### Opción A: los campos del dictamen son columnas de `Solicitud`

Lo que hay hoy en `develop`.

- **A favor:**
  - Una consulta sin `JOIN` para la cola, los filtros y los conteos, que es la pantalla más
    usada del panel.
  - `estado` no se mueve de donde ya estaba, así que nada de lo construido antes se toca.
  - Es lo que `STD` hace con su `Solicitud`, y dos dominios que se parecen se leen más fácil.
- **En contra:**
  - Toda convocatoria `EVT` comparte una sola forma de revisión. Si `TAL` entra como
    convocatoria `EVT`, o hereda criterios que no son los suyos o se le añaden columnas que
    sobran en el resto de las filas.
  - Mezcla en una tabla lo que escribe quien propone y lo que escribe quien administra, que son
    dos actores, dos momentos y dos permisos.

### Opción B: una entidad de revisión, ligada a la solicitud

Lo que `isaac-develop` construyó como `DetallesAdminSolicitud`, uno a uno.

- **A favor:**
  - La revisión se puede variar sin tocar `Solicitud`: es el mismo patrón de `ADR-0009`.
  - Separa por quién escribe, no por cardinalidad.
- **En contra:**
  - Un `OneToOneField` con columnas fijas **no varía por convocatoria todavía**: es el sitio
    donde poner la variación, no la variación. Sin el paso siguiente —herencia multitabla, o un
    discriminador— da lo mismo que las columnas, con un `JOIN` de más.
  - Cuesta las ~155 referencias de arriba, sobre código recién mergeado de otra persona.

### Opción C: una entidad de revisión **por tipo de convocatoria**, con herencia multitabla

La forma completa de lo que la opción B insinúa: una `Revision` con lo común, y una tabla hija
por cada forma de revisar, igual que las ocho `Actividad_*` de `ADR-0009`.

- **A favor:**
  - Es lo único que cumple de verdad «cada convocatoria revisa lo suyo».
  - El patrón ya existe en el proyecto, con su ADR y su código funcionando.
- **En contra:**
  - **Hoy no se puede diseñar.** Solo hay una forma de revisión conocida: la de Hipólito. La
    segunda —la de Elvira— está en revisión, y una jerarquía derivada de un solo caso suele ser
    la jerarquía equivocada.
  - Es la opción más cara de las tres, y la que más código ajeno reescribe.

## Decisión

**Pendiente.** Se decide cuando el modelo de datos de `TAL` conteste la pregunta de la que
depende: si los talleres infantiles y juveniles son una convocatoria de tipo `EVT` o un tipo
propio.

- Si son una convocatoria `EVT` con otros criterios de revisión → **opción C**, y la B es el
  primer paso de esa migración.
- Si son un tipo propio con sus propias tablas → **opción A** se queda, y este ADR se cierra
  como `Rechazado` con el motivo escrito.

> [!warning] Lo que **no** es un motivo para decidir esto
> Que una rama u otra llegara primero. La opción A gobierna hoy porque está mergeada y porque
> `CU-EVT-003` no necesita más —lee un estado y dos textos—, no porque sea la elegida.

## Qué queda desactualizado por esta decisión

Nada todavía: `Propuesto` no cambia ninguna regla escrita. Cuando se cierre, lo que habrá que
revisar es esto —anotado ahora, que es cuando se sabe—:

| Archivo | Qué habría que mirar |
| --- | --- |
| `docs/requisitos/EVT/Modelo de datos - Eventos.md` §3.1 | La nota que justifica las columnas se sustituye o se confirma |
| `docs/requisitos/TAL/Modelo de datos - Talleres.md` | Es quien contesta la pregunta; hoy está en revisión |
| `CLAUDE.md`, estado de `EVT` | Dónde vive el dictamen |
| `apps/convocatorias/models.py::TipoConvocatoria` | El comentario que declara `TAL` pendiente |

## Referencias

- [`ADR-0006`](<0006-la-liga-entre-convocatoria-y-modulo.md>) — cómo se engancha hoy una
  convocatoria con lo que hay detrás; el patrón que la opción C extendería a la revisión.
- [`ADR-0009`](<0009-las-ocho-actividades-de-evt.md>) — la herencia multitabla que la opción C
  reutilizaría, con su precedente ya construido.
- `Modelo de datos - Eventos` §3.1 — la nota de `develop` que argumenta las columnas.
- `apps/convocatorias/models.py` — el comentario que deja `TAL` sin decidir.
