---
estado: aceptada
version: "1.0"
tags:
  - tipo/adr
  - dom/fer
  - dom/std
  - dom/evt
  - tema/arquitectura
fecha: 2026-08-27
id: ADR-0006
responsable: Hugo Janssen
supersede:
reemplazado_por:
---
# ADR-0006. Una convocatoria se liga a su módulo por `RegistroConvocatoria` y un registro de módulos, no por conocimiento mutuo

## Estado

`Aceptado` — 2026-08-27. Cierra dos temas abiertos que llevaban meses: la colisión entre
`RegistroConvocatoria` y el `RouterSolicitudes` de `EVT`
([`FER/Modelo de datos - Ferias`](<../requisitos/FER/Modelo de datos - Ferias.md>) §3.4 y §6), y
cómo el catálogo de convocatorias lleva a la pantalla del módulo que la gobierna.

## Contexto

El catálogo de convocatorias de una feria está construido y es la portada de `/f/<slug>/`
(CU-FER-006). Cada tarjeta lleva un botón "Registrarme" que **hoy no hace nada**: dispara un
aviso que dice que el formulario "se conecta con su módulo en una siguiente entrega". Entre
`Convocatoria` y cualquier módulo de contenido no hay tabla, ni ruta, ni contrato.

Construir `STD` obliga a cerrarlo, y con él tres preguntas que hasta ahora se podían posponer:

**1. Quién guarda que una persona se inscribió.** El modelo de `FER` define
`RegistroConvocatoria(convocatoria, persona, estado, fecha_registro)`, deliberadamente flaco:
afirma *quién entró por qué puerta* y nada más. `EVT`, en cambio, definió
`RouterSolicitudes(usuario_django, convocatoria, solicitud_id)` donde `convocatoria` es un
discriminador de **dominio** (`EVT`/`TAL`/`STD`/`VIS`), no una convocatoria con identidad
propia. Son la misma figura con dos soluciones incompatibles, y el propio modelo de `FER` dice
que **no pueden coexistir**.

**2. Quién sabe que `tipo = STD` lleva a la pantalla de stands.** Si `apps/convocatorias`
resolviera `reverse("stands:aplicar")`, la dependencia se invertiría: `apps/convocatorias` es la
mitad por feria de `FER`, y los dominios verticales dependen de `FER`, nunca al revés (regla 4
de `CLAUDE.md`). Además el catálogo reventaría en cualquier despliegue donde ese módulo no esté
instalado — que es el estado normal hoy, con cinco de seis módulos sin construir.

**3. Quién crea la configuración del módulo al dar de alta una convocatoria.** CU-FER-005 paso 6
exige que una convocatoria de tipo `STD` nazca con su `ConfiguracionSistema` en la misma
transacción, y E1 exige que si eso falla no quede ni la convocatoria. El servicio de alta
(`apps/convocatorias/servicios/altas.py`) ya deja el `transaction.atomic` preparado y el hueco
vacío, precisamente porque llenarlo exigía que `convocatorias` importara `stands`.

Fuerzas a considerar:

- **`tipo` es una cadena, y el acoplamiento que expresa no es verificable por la base.** El
  expediente de un módulo cuelga del registro, pero el `tipo` vive **un salto más allá**, en
  `Convocatoria`. Nada impide colgar una `Solicitud` de stands de un registro cuya convocatoria
  es de eventos.
- **Los módulos se construyen de uno en uno, a lo largo de meses.** Lo que se decida aquí lo van
  a repetir cinco módulos más, y el que menos se parece a `STD` —`VIS`, visitas escolares— ni
  siquiera tiene modelo de datos escrito.
- **El catálogo es público** (CU-FER-006, A1). Lo mira gente sin cuenta, y no puede fallar
  porque un módulo no esté instalado o porque una convocatoria sea de un tipo que nadie sirve
  todavía.

## Opciones consideradas

### Opción A: `RegistroConvocatoria` + un registro de módulos por tipo

`FER` es dueña de la tabla flaca y del contrato. Cada módulo se inscribe a sí mismo, desde su
`AppConfig.ready()`, declarando qué tipo sirve y por dónde se entra.

- **A favor:**
  - La dependencia apunta en la única dirección permitida: `stands → convocatorias`, nunca al
    revés. `apps/convocatorias` no nombra a ningún módulo.
  - Un tipo sin módulo instalado degrada a "próximamente" en la tarjeta, en vez de romper una
    pantalla pública.
  - Resuelve el paso 6 de CU-FER-005 sin importar nada: el módulo deja registrado un callback
    que crea su configuración, y el servicio de alta lo llama.
  - Es el patrón que el proyecto ya usa dos veces: `admin.site.register` de Django y el
    `admin_feria` de ADR-0005.
  - Las claves foráneas son reales y la base las valida.
- **En contra:**
  - Hay un momento de arranque en el que el registro se puebla, y un módulo que olvide
    registrarse falla en silencio (su tarjeta dice "próximamente" para siempre).
  - No resuelve, por sí solo, la invariante del `tipo` — ver "Decisión".

### Opción B: el `RouterSolicitudes` de `EVT`

Una tabla única `(usuario, convocatoria_como_dominio, solicitud_id)` con referencia polimórfica.

- **A favor:** una sola tabla para todo el sistema; agregar un módulo no toca nada.
- **En contra:**
  - `solicitud_id` es polimórfico: **la base no puede validarlo**. Una fila puede apuntar a una
    solicitud que no existe, o a la tabla equivocada, y nada lo impide.
  - Su discriminador se llama `convocatoria` pero nombra un **dominio**, no una convocatoria.
    Con varias convocatorias del mismo tipo en una feria (decisión del 2026-08-25) no puede
    decir a **cuál** se inscribió alguien, que es justo lo que hay que saber.
  - No aporta nada que A no dé: A también permite agregar un módulo sin tocar tablas.

### Opción C: convención de rutas (`/{tipo}/convocatoria/<id>/aplicar/`)

Sin registro: el catálogo compone la URL a partir del `tipo`.

- **A favor:** cero infraestructura.
- **En contra:** el acoplamiento existe igual pero deja de ser visible; no hay dónde colgar el
  callback de configuración ni la etiqueta del módulo; y un tipo sin módulo produce un 404 en
  vez de una tarjeta honesta.

## Decisión

**La liga entre una convocatoria y su módulo se hace con dos piezas, las dos propiedad de
`FER`:**

**1. `RegistroConvocatoria` —** la tabla flaca que ya define el modelo de `FER` §3.4, en
`apps/convocatorias`. Única por (`convocatoria`, `persona`). Cada módulo cuelga su expediente de
ella con una FK real. **`RouterSolicitudes` queda derogado**: `EVT` corrige su modelo para
apuntar aquí.

**2. Un registro de módulos por tipo —** `apps/convocatorias/modulos.py`. Cada app vertical se
inscribe desde su `AppConfig.ready()`:

```python
# apps/stands/apps.py
registrar(Modulo(
    tipo=TipoConvocatoria.STD,
    etiqueta="Venta de stands",
    url_aplicar="stands:aplicar",          # recibe convocatoria_id
    url_panel="stands:panel",
    crear_configuracion=servicios.configuracion.crear_por_defecto,
))
```

`apps/convocatorias` define `Modulo`, `registrar()` y `modulo_de(tipo)`, y **no nombra a ningún
módulo**. La tarjeta del catálogo pregunta al registro:

| Estado | Qué muestra la tarjeta |
| --- | --- |
| No hay módulo para ese tipo | "Próximamente" — desactivado. No es un error. |
| Hay módulo y la convocatoria está `abierta` | "Registrarme" → `url_aplicar` |
| Hay módulo y la persona ya tiene registro | "Ver mi solicitud" → `url_aplicar` |
| La convocatoria está `cerrada` o en `borrador` | Sin acción (el borrador solo lo ve quien administra) |

### Cuándo nace el registro

**Al guardarse el expediente del módulo, no al pulsar el botón.** El enlace de la tarjeta solo
navega. Si el registro se creara al hacer clic, cualquier visita curiosa dejaría una inscripción
vacía y las listas de la convocatoria contarían gente que nunca aplicó.

El módulo lo pide con `obtener_o_crear_registro(convocatoria, persona)`, dentro de la misma
transacción que crea su expediente. La tabla es de `FER`, así que el módulo nunca la escribe
directamente.

### La invariante que la base NO puede garantizar

`Solicitud.registro_id → RegistroConvocatoria` es una FK real, pero el `tipo` que decide qué
módulo puede colgar de ahí vive en `Convocatoria`, un salto más allá. **Nada en el esquema
impide colgar una `Solicitud` de stands de un registro de una convocatoria de eventos.**

PostgreSQL sí podría expresarlo —un `UNIQUE (id, tipo)` en `Convocatoria`, una FK compuesta en
`RegistroConvocatoria` y un `CHECK (tipo = 'STD')` en `Solicitud`—, pero Django no soporta claves
foráneas compuestas de forma usable, y montarlo a mano con SQL crudo dejaría un esquema que el
ORM no entiende y que ninguna migración futura mantendría.

**Se acepta que sea una invariante de código**, con tres condiciones que la hacen sostenible:

1. El servicio del módulo que crea el expediente **comprueba el tipo** y falla si no coincide.
2. Hay una prueba por módulo que lo fija, y falla si alguien quita la comprobación.
3. Queda escrito en el modelo, junto al campo, que esta invariante **no** la sostiene la base.

Es la única invariante de todo `FER` que está en esta situación, y por eso se nombra aquí en vez
de dejarla implícita.

## Consecuencias

**Positivas**

- El catálogo deja de ser un escaparate muerto: es la puerta real de los seis módulos.
- Agregar un módulo no toca ninguna tabla ni ninguna plantilla existente. Se inscribe y aparece.
- Se cierra el paso 6 de CU-FER-005, que estaba construido a medias a propósito.
- `EVT` deja de tener un modelo que contradice al de `FER`, sin que nadie tenga que recordar
  cuál de los dos era el bueno.
- Una feria puede tener dos convocatorias del mismo tipo y cada persona puede inscribirse a las
  dos: son dos registros y dos expedientes, con la unicidad puesta donde corresponde.

**Negativas / riesgos aceptados**

- **La invariante del tipo es de código.** Ver arriba: se acepta a sabiendas, con prueba.
- **Un módulo que olvide registrarse falla en silencio**, con la tarjeta diciendo "próximamente"
  para siempre. Mitigación: una prueba por módulo que compruebe que `modulo_de(su_tipo)` no es
  `None` tras el arranque.
- **El registro es estado global del proceso**, poblado en `ready()`. Es el mismo compromiso que
  ya aceptamos con el `admin.site` de Django y con `admin_feria`.
- **`EVT` queda temporalmente contradiciendo a este ADR.** Su modelo sigue describiendo
  `RouterSolicitudes`, que aquí queda derogado. **No se toca ahora, por decisión de alcance**: lo
  que se construye es `STD`, y `EVT` no tiene código todavía, así que la contradicción es de
  papel y no de base de datos. Corregirlo es trabajo pendiente y con dueño: retirar
  `RouterSolicitudes` de su modelo y reapuntar `Solicitudes_EVT` al registro, antes de que `EVT`
  se empiece a construir.

**Qué queda descartado por esta decisión**

- `RouterSolicitudes` y cualquier referencia polimórfica entre una convocatoria y el expediente
  de su módulo.
- Que `apps/convocatorias` conozca, importe o nombre a un módulo de contenido.
- Que el `tipo` de una convocatoria se resuelva por convención de URL.

## Referencias

- [`FER/Modelo de datos - Ferias`](<../requisitos/FER/Modelo de datos - Ferias.md>) §3.4 —
  `RegistroConvocatoria` y la colisión que este ADR cierra.
- [`STD/Modelo de datos - Stands`](<../requisitos/STD/Modelo de datos - Stands.md>) §3.3 — el
  primer expediente que cuelga del registro.
- [ADR-0003](<0003-una-feria-por-schema.md>) — por qué el registro vive en el schema de la feria.
- [ADR-0005](<0005-el-operador-alcanza-cualquier-feria.md>) — el `admin_feria`, el otro sitio
  donde el proyecto usa un registro poblado en el arranque.
- [`CU-FER-005`](<../requisitos/FER/CU-FER-005 Dar de alta una convocatoria en mi feria.md>) —
  paso 6 y E1, que este ADR desbloquea.
