---
estado: aceptada
version: "1.1"
tags:
  - tipo/adr
  - dom/fer
  - dom/reg
  - tema/arquitectura
  - tema/permisos
fecha: 2026-08-21
fecha_actualizacion: 2026-08-25
id: ADR-0004
responsable: Hugo Janssen
supersede:
reemplazado_por:
---
# ADR-0004. El acceso administrativo se otorga por feria, con un único dueño que es quien da de alta a los demás administradores

## Estado

`Aceptado` — 2026-08-21. Reemplaza el modelo de permisos por módulo y nivel (`RolPermiso`) que
implementan hoy CU-REG-003, CU-REG-005 y CU-REG-006. Ver "Consecuencias" para lo que eso
implica en esos tres casos de uso.

> [!warning] Enmendado el 2026-08-25 — administrar convocatorias también queda reservado al dueño
> La decisión original daba **todo** el contenido de la feria a cualquier administrador, y
> reservaba al dueño únicamente el alta y la baja de administradores. Al escribirse el CRUD de
> convocatorias (CU-FER-005 a CU-FER-009) se decidió que **crear, editar, abrir/cerrar y
> eliminar convocatorias es también exclusivo del dueño**.
>
> El motivo: una convocatoria no es contenido corriente. Define qué puertas están abiertas y
> hasta cuándo, y de ella cuelga el expediente entero de cada módulo — borrarla arrastraría
> solicitudes, editoriales, reservas y comprobantes de pago.
>
> **Lo que no cambia:** cualquier administrador sigue viendo el catálogo (CU-FER-006 — sin eso no
> podría operar su módulo) y sigue operando todo lo que cuelga de una convocatoria: dictaminar,
> revisar solicitudes, programar, validar abonos.
>
> Se registra como enmienda y no como ADR nuevo porque no cambia el modelo de datos ni el
> mecanismo: `AdminFeria(feria, persona, es_dueño)` sigue igual, solo crece la lista de lo
> reservado al dueño. **Si esa lista vuelve a crecer**, deja de ser una enmienda y toca escribir
> el ADR que sustituya a este: sería señal de que "el administrador puede todo el contenido" ya
> no describe el sistema.

> [!note] Enmendado en un punto por ADR-0005 (2026-08-27)
> La tabla de niveles de más abajo dice que el operador de la plataforma *"no es un rol dentro
> de ninguna feria"*. [ADR-0005](<0005-el-operador-alcanza-cualquier-feria.md>) abre esa puerta:
> el superusuario de Django alcanza cualquier feria, incluidas las pantallas reservadas a su
> dueño, sin tener fila en `AdminFeria`. Cierra el hueco que este mismo ADR dejó anotado en
> Consecuencias —qué pasa si el dueño se va—. **El resto de esta decisión sigue vigente**: el
> acceso se otorga por feria, con un dueño por feria, y `AdminFeria` no cambia.

## Contexto

[ADR-0003](<0003-una-feria-por-schema.md>) separa el contenido de cada feria en su propio
schema. Eso obliga a responder una pregunta que antes no existía: **¿quién puede entrar a qué
feria?** Mientras solo había una feria implícita, "ser administrador" era una propiedad de la
cuenta; con varias ferias, deja de serlo — alguien puede administrar FILEY 2027 sin tener nada
que ver con FILEY 2028.

Lo que existe hoy es `RolPermiso(persona, modulo, nivel)`: una cuenta es administrativa si
tiene al menos un permiso, y cada permiso da acceso a un módulo (`EVT`, `TAL`, `STD`, `VIS` o
`*`) con un nivel (`lectura` o `edicion`). Está construido y funcionando
(`filey/apps/registros/models.py`), y sobre él se apoyan el decorador `requiere_modulo`, la
pantalla de selección de módulo (CU-REG-006) y el alta de administradores (CU-REG-005).

El [`Modelo de datos - Registros`](<../requisitos/REG/Modelo de datos - Registros.md>) §2.2 ya
había registrado esta pregunta como abierta desde la sesión de diseño del 2026-08-19, donde se
esbozó una tabla `admin(usuario, feria)` y se dejó por decidir "si `RolPermiso` gana un
`feria_id` o si el acceso queda en dos niveles". Este ADR la cierra.

Hay además un requisito nuevo que ningún modelo anterior cubre: **cada feria tiene un dueño, y
solo él puede dar de alta a otros administradores de esa feria.** Hoy cualquiera con
`modulo = *` puede provisionar administradores (CU-REG-005), lo que significa que un
administrador puede crear administradores indefinidamente y nadie queda como responsable
identificable de quién tiene acceso.

Fuerzas a considerar:

- **Quién responde por los accesos.** El cliente necesita que en cada feria haya una persona
  concreta —no un rol difuso— responsable de quién entra. Es una necesidad organizativa, no
  técnica.
- **La granularidad por módulo no se está usando.** Los paneles de módulo aún no existen: hoy
  todas las cuentas administrativas caen en la misma pantalla de selección y ningún panel está
  conectado (CU-REG-006, nota de estado del 2026-08-05). La granularidad `modulo`/`nivel` es
  capacidad construida y no ejercida.
- **Coste de equivocarse en cada dirección.** Dar de más (un administrador ve un módulo que no
  le toca) es un problema entre compañeros de equipo que ya se conocen. Dar de menos (nadie
  puede administrar porque el permiso fino está mal puesto) bloquea la operación de la feria.
- **Un permiso que nadie sabe explicar no se administra.** Cruzar feria × módulo × nivel da una
  matriz que hay que mantener a mano, sin pantalla que hoy lo permita.

## Opciones consideradas

### Opción A: `AdminFeria(feria, persona, es_dueño)` — el permiso es por feria, con un dueño

Una cuenta es administradora **de una feria** si tiene una fila en `AdminFeria` para esa feria.
Esa fila la habilita para todo el contenido de esa feria. Exactamente una de las filas de cada
feria lleva `es_dueño = verdadero`, y solo esa persona puede crear o retirar administradores en
esa feria.

- **A favor:**
  - Responde la pregunta que ADR-0003 abre —quién entra a qué feria— con la tabla mínima que la
    responde, y es la que el equipo pidió explícitamente.
  - Deja una persona identificable como responsable de los accesos de cada feria, y hace
    imposible la cadena "un administrador crea administradores" que hoy existe.
  - El permiso se explica en una frase: *o administras esta feria, o no*. Se puede administrar
    sin pantalla y sin equivocarse.
  - Encaja con el middleware de ADR-0003: la comprobación de acceso es una consulta por
    (persona, feria), justo antes de fijar el `search_path`.
- **En contra:**
  - **Se pierde la granularidad por módulo y el nivel de solo lectura.** El supervisor de solo
    lectura que contempla CU-REG-005 A2 deja de ser expresable: hoy, o administras toda la
    feria, o no entras.
  - Un administrador de `TAL` puede tocar `STD`. Se acepta a sabiendas (ver "Consecuencias").
  - `RolPermiso` queda sin uso y hay que retirarlo, junto con el decorador `requiere_modulo` que
    se apoya en él.

### Opción B: `RolPermiso` gana una columna `feria_id`

Mantener módulo y nivel, y añadir la feria como tercera dimensión del permiso.

- **A favor:**
  - Conserva la granularidad ya construida, incluido el supervisor de solo lectura.
  - Cambio pequeño en el modelo: una columna y una constraint.
- **En contra:**
  - **No cubre lo que se pidió:** no expresa quién es el dueño de la feria ni impide que un
    administrador cree administradores. Habría que añadir *igualmente* la noción de dueño, con
    lo que se acaba manteniendo dos mecanismos de permiso a la vez.
  - Cruza feria × módulo × nivel sin pantalla que lo administre: la matriz se mantiene a mano,
    en un comando, y es fácil dejar a alguien fuera sin darse cuenta.
  - Sostiene granularidad para paneles que todavía no existen.

### Opción C: dos niveles — `AdminFeria` decide *si* entras, `RolPermiso` decide *a qué módulos*

La salida que el modelo de datos de `REG` dejaba esbozada.

- **A favor:** conserva ambas capacidades sin que ninguna estorbe a la otra, y es la evolución
  natural si más adelante hace falta el permiso fino.
- **En contra:** son **dos** tablas de permisos que mantener y dos preguntas que hacer antes de
  cada pantalla, para un equipo que hoy son cinco personas y unos paneles que aún no existen.
  Es la respuesta correcta a un problema que todavía no se tiene.

## Decisión

**El acceso administrativo se otorga por feria mediante `AdminFeria(feria, persona, es_dueño)`.
Una fila habilita a su persona para todo el contenido de esa feria. Cada feria tiene
exactamente un dueño, y solo el dueño puede dar de alta o retirar administradores de su feria.**

`RolPermiso(persona, modulo, nivel)` queda **derogado**: se retira del modelo y del código,
junto con el decorador `requiere_modulo`. Ser administrador deja de ser una propiedad de la
cuenta y pasa a ser una relación entre una cuenta y una feria.

El sistema queda con tres niveles de acceso, y no más:

| Nivel | Quién | Qué puede |
| --- | --- | --- |
| Operador de la plataforma | Equipo técnico, por comando en el servidor | Crear una feria y designar a su dueño (CU-FER-001). No es un rol dentro de ninguna feria. |
| Dueño de la feria | Una persona por feria | Todo lo de la feria **más** dar de alta y retirar a sus administradores (CU-FER-003, CU-FER-004) **y administrar sus convocatorias** (CU-FER-005 a CU-FER-009, enmienda 2026-08-25). |
| Administrador de la feria | Cero o más por feria | Todo el contenido de la feria: dictamen, programa, stands, visitas, y todo lo que cuelga de una convocatoria. **No** puede crear ni retirar administradores, **ni administrar las convocatorias** — aunque sí consultarlas (CU-FER-006). |

Quien no tiene fila en `AdminFeria` para una feria es, respecto de esa feria, un participante:
puede entrar al portal público a proponer, pero no al panel. La identidad sigue siendo global —
la `Persona` no pertenece a ninguna feria (ADR-0003).

## Consecuencias

**Positivas**

- Hay, por feria, **una persona identificable** responsable de quién tiene acceso.
- Desaparece la cadena de administradores creando administradores.
- El permiso se puede explicar y auditar sin pantalla: una fila por persona y feria.
- El middleware de ADR-0003 tiene una única comprobación que hacer antes de fijar el
  `search_path`, en vez de resolver una matriz de módulo y nivel.
- Se retira código y modelo que existían para paneles que aún no se han construido.

**Negativas / riesgos aceptados**

- **Se pierde el supervisor de solo lectura** (CU-REG-005 A2). Hoy no hay forma de dar acceso
  de observación sin dar acceso de edición. Si el cliente lo pide de vuelta, se recupera
  añadiendo columnas a `AdminFeria` —no resucitando `RolPermiso`— y con un ADR que reemplace a
  este.
- **Un administrador de un módulo puede tocar los demás.** Elvira puede entrar al panel de
  stands. Se acepta porque el equipo administrador de una feria es pequeño y se conoce, pero
  significa que la separación entre módulos pasa a ser una convención, no un control.
- **La `Persona` que hoy es "administradora" pierde ese atributo derivado.** `es_administrativa`
  (¿tiene algún `RolPermiso`?) deja de tener sentido sin una feria de referencia: la pregunta
  correcta pasa a ser "¿administra *esta* feria?".
- **Queda un hueco sin resolver: qué pasa si el dueño se va.** Con exactamente un dueño por
  feria y solo él pudiendo administrar accesos, una feria cuyo dueño deja el proyecto queda sin
  quien dé de alta a nadie. La salida provisional es que el operador de la plataforma reasigne
  la propiedad por comando; formalizarlo como caso de uso está pendiente (ver el índice de
  `FER`).
- Tres casos de uso ya escritos quedan desactualizados y hay que corregirlos: **CU-REG-003**
  (qué comprueba el acceso administrativo), **CU-REG-005** (el alta la hace el dueño, dentro de
  una feria) y **CU-REG-006** (lo que se elige tras entrar ya no son módulos sueltos).

**Qué queda descartado por esta decisión**

- `RolPermiso`, sus niveles `lectura`/`edicion` y el módulo `*` como forma de expresar
  "administrador general".
- El decorador `requiere_modulo(modulo, nivel)`.
- Que cualquier administrador pueda provisionar otros administradores.

## Estado de implementación — 2026-08-25

`AdminFeria` existe como código en `filey/apps/ferias/models.py`, y **`RolPermiso` se
retiró del código** ese mismo día (migración `registros/0004_retirar_rolpermiso`), junto
con `NivelPermiso`, `Persona.puede_administrar` y el decorador `requiere_modulo`. La
divergencia entre este ADR y lo desplegado, que llevaba abierta desde el 2026-08-21,
queda cerrada.

Lo que cambió de facto en las pantallas:

| Antes (`RolPermiso`) | Ahora (`AdminFeria`) |
| --- | --- |
| `Persona.es_administrativa` = "¿tiene algún rol?" | "¿administra alguna feria?" — se responde por la relación inversa `ferias_admin`, para que `registros` no dependa de `ferias` |
| `/admin/modulos/` listaba módulos | `/admin/ferias/` lista **ferias** (CU-FER-002). Lo primero que se elige es la edición; el módulo se elige dentro |
| `manage.py alta_admin --modulo EVT` | `manage.py alta_admin_feria --feria 2027` — el acceso necesita saber *a qué feria* |
| `requiere_modulo("EVT", nivel)` | `requiere_admin_feria` / `requiere_dueno_feria`, en `apps/ferias/permisos.py` |

El nivel de solo lectura no tiene sustituto, tal como este ADR decidió a sabiendas.

---

## Referencias

- [ADR-0003](<0003-una-feria-por-schema.md>) — el aislamiento por schema que obliga a decidir
  esto; el middleware que describe ejecuta la comprobación de este ADR.
- [`FER/Modelo de datos - Ferias`](<../requisitos/FER/Modelo de datos - Ferias.md>) — las
  entidades `Feria` y `AdminFeria`.
- [`FER/CU-FER Índice`](<../requisitos/FER/CU-FER Índice.md>) — los casos de uso que
  implementan esta decisión.
- [`Modelo de datos - Registros`](<../requisitos/REG/Modelo de datos - Registros.md>) §2.2 — la
  pregunta abierta desde el 2026-08-19 que este ADR cierra.
