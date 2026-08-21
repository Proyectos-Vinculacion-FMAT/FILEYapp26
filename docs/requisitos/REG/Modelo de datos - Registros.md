---
estado: propuesta
version: 0.1
tags:
  - tipo/modelo-de-datos
  - dom/reg
fecha: 2026-08-19
---
# Modelo de datos — Registros (REG)

> Modelo **conceptual** del core transversal `REG`: la identidad única del sistema
> (`Persona`) y el mecanismo de login (`SesionOTP`). Todos los demás dominios (`EVT`, `TAL`,
> `STD`, `VIS`) referencian estas entidades en vez de redefinirlas — ver la nota de cada uno de
> sus "Modelo de datos".

<!-- -->

> [!warning] `RolPermiso` quedó derogado el 2026-08-21 — el acceso administrativo ya no vive aquí
> Este documento describía también el acceso administrativo por módulo y nivel
> (`RolPermiso`). Ese modelo lo reemplaza `AdminFeria`, en
> [`FER/Modelo de datos - Ferias`](<../FER/Modelo de datos - Ferias.md>): el permiso se otorga
> **por feria**, no por módulo, y cada feria tiene un dueño que es el único que administra sus
> accesos (ver [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>)).
>
> `RolPermiso` se conserva en §2.2 marcado como derogado, y no por nostalgia: **sigue existiendo
> en el código** (`filey/apps/registros/models.py`) y hay que retirarlo. Hasta que esa migración
> se ejecute, código y documentación no coinciden — manda la documentación.
>
> Lo que **no** cambia: `Persona` sigue siendo global y no pertenece a ninguna feria.

<!-- -->

> [!warning] Este core **ya está construido**, a diferencia de la mayoría de este repositorio
> `Persona`, `RolPermiso` y `SesionOTP` existen hoy como código real en
> `filey/apps/registros/models.py` (en `main`), implementando `CU-REG-001`/`002`/`003`/`005`.
> Este documento describe el modelo **objetivo**; donde diverge de lo desplegado, se marca
> explícitamente. Migrar el código real a este modelo es trabajo aparte, no un efecto de editar
> este documento. Hay **dos divergencias abiertas**, ambas en §5:
>
> 1. `nombre_completo` desplegado vs. `nombres`/`apellidos` decididos el 2026-08-19.
> 2. `RolPermiso` desplegado vs. derogado el 2026-08-21 en favor de `AdminFeria` (`FER`).

---

## 1. Resumen de entidades

| Entidad     | Propósito                                                                              |
| ----------- | ---------------------------------------------------------------------------------------- |
| Persona     | Identidad única del sistema — registro mínimo, compartido entre todos los módulos y todas las ferias. |
| SesionOTP   | Código de un solo uso para autenticar una sesión (sin contraseña para usuarios externos). |
| ~~RolPermiso~~ | **Derogado 2026-08-21.** Lo reemplaza `AdminFeria` (`FER`). Ver §2.2.                 |

Ambas entidades vivas son **globales**: viven en el schema `public` y hay una sola copia para
todo el sistema, con independencia de cuántas ferias existan
([ADR-0003](<../../adr/0003-una-feria-por-schema.md>)).

---

## 2. Detalle de entidades y atributos

### 2.1 Persona

> La cuenta única del sistema (`CU-REG-001`). Un registro por correo, reutilizado en
> cualquier convocatoria/módulo al que la persona participe.

| Atributo         | Descripción                                                                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| id                | Identificador único.                                                                                                                                          |
| nombres           | Nombre(s) de pila. **Decisión 2026-08-19:** separado de `apellidos` de forma definitiva. Lo desplegado hoy tiene un solo campo `nombre_completo` — pendiente de migración (ver sección 5). |
| apellidos         | Apellido(s). Ver nota de `nombres`.                                                                                                                           |
| correo            | Único en todo el sistema (`unique=True`). Es el `USERNAME_FIELD` de autenticación.                                                                            |
| telefono          | Teléfono de contacto.                                                                                                                                         |
| estado            | `activa` / `inactiva`.                                                                                                                                        |
| fecha_registro    | Alta de la cuenta.                                                                                                                                             |
| ultimo_acceso     | Última vez que inició sesión (nulo si nunca).                                                                                                                 |

> *Nota:* no hay contraseña para el flujo de usuario externo — el acceso es 100% por OTP
> (`SesionOTP`, 2.3). Lo desplegado usa la infraestructura de `AbstractBaseUser` de Django
> (con `set_unusable_password()`) para poder reusar su sistema de sesiones; eso es detalle de
> implementación, no forma parte de este modelo conceptual.

### 2.2 ~~RolPermiso~~ — derogado el 2026-08-21

> [!danger] No implementar ni extender esta entidad
> La reemplaza `AdminFeria(feria, persona, es_dueño)` en
> [`FER/Modelo de datos - Ferias`](<../FER/Modelo de datos - Ferias.md>) §3.2. Se conserva aquí
> **solo** para que quien lea el código actual —donde todavía existe— entienda qué era y por
> qué se fue. Ver la tabla de equivalencia al final de esta sección.

> Lo que distinguía a una cuenta administrativa: tener al menos un `RolPermiso` (`CU-REG-003`,
> `CU-REG-005`). Sin `RolPermiso`, la `Persona` era un usuario externo normal.

| Atributo    | Descripción                                                                                     |
| ------------ | --------------------------------------------------------------------------------------------- |
| id          | Identificador único.                                                                            |
| persona_id  | FK → Persona.                                                                                    |
| modulo      | `EVT` / `TAL` / `STD` / `VIS` / `*` (todos los módulos — administrador general).                |
| nivel       | `lectura` / `edicion` (acumulativo: quien puede editar también puede leer).                      |
| creado_en   | Fecha de asignación del permiso.                                                                 |

> Restricción: único por (`persona_id`, `modulo`) — no se puede duplicar el permiso de un
> mismo módulo para la misma persona (`CU-REG-005`, E1).

> [!success] Pregunta cerrada el 2026-08-21 — ganó `admin(usuario, feria)`
> Esta sección preguntaba, desde la sesión de diseño del 2026-08-19, si al formalizarse `Feria`
> el permiso ganaría un `feria_id` o quedaría en dos niveles. La respuesta es **ninguna de las
> dos**: `RolPermiso` desaparece y lo sustituye `AdminFeria`, que es la tabla
> `admin(usuario, feria)` que aquella sesión esbozó, más el flag de dueño.
>
> Se descartó mantener los dos niveles (`AdminFeria` decide *si* entras, `RolPermiso` de *qué
> módulos*) por ser la respuesta correcta a un problema que todavía no se tiene: los paneles de
> módulo no existen y la granularidad nunca se ha ejercido. El razonamiento completo, con lo que
> se pierde a cambio, está en
> [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>).

**Equivalencia entre el modelo viejo y el nuevo:**

| `RolPermiso` (derogado) | `AdminFeria` (vigente) |
| --- | --- |
| `modulo = *`, `nivel = edicion` | Una fila por cada feria que administra. Si además la creó el operador de la plataforma al dar de alta la feria, con `es_dueño = verdadero`. |
| `modulo = EVT`, `nivel = edicion` | Una fila en la feria correspondiente. **Se pierde la restricción al módulo**: administra toda la feria. |
| `nivel = lectura` (supervisor) | **No tiene equivalente.** Ver ADR-0004, "Negativas / riesgos aceptados". |
| `Persona.es_administrativa` (¿tiene algún rol?) | Sin equivalente global: la pregunta pasa a ser "¿administra *esta* feria?". |

### 2.3 SesionOTP

> Código de un solo uso enviado por correo (`CU-REG-002`/`003`). Ya desplegado sin cambios
> pendientes — se documenta aquí por completitud del core.

| Atributo         | Descripción                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| id                | Identificador único.                                                                              |
| persona_id        | FK → Persona.                                                                                      |
| codigo_hash       | El código nunca se guarda en claro — se hashea igual que una contraseña.                          |
| canal             | `correo` (único canal hoy).                                                                       |
| creado_en         | Marca de tiempo de creación.                                                                       |
| expira_en         | `creado_en` + 15 minutos.                                                                          |
| usado             | Booleano — se "quema" al validarse, al agotar intentos, o al ser reemplazado por un reenvío.      |
| intentos          | Cuenta de intentos fallidos — máximo 3 (`CU-REG-002`, E1).                                        |
| acertado          | Booleano — distingue "usado porque acertó" de "usado por agotar intentos o por reenvío".          |

---

## 3. Relaciones principales

- **Persona** 1—N **SesionOTP** (historial de códigos emitidos; en la práctica, 0 o 1 vigente a la vez).
- **Persona** 1—N **AdminFeria** (`FER`) — una persona puede administrar varias ferias, y ser dueña de unas y administradora de otras.
- **Persona** 1—N *(entidad de solicitud de cada dominio)* — ver `EVT/Modelo de datos - Eventos.md` (`Propuesta.participante_id`) y equivalentes en `TAL`/`STD`/`VIS`. Esas entidades viven en el schema de una feria; `Persona` no.

---

## 4. Mapa entidad → caso de uso (trazabilidad)

| Entidad     | Casos de uso relacionados                  |
| ----------- | --------------------------------------------- |
| Persona     | CU-REG-001, CU-REG-002, CU-REG-003, CU-REG-004, CU-FER-001, CU-FER-003 |
| SesionOTP   | CU-REG-002, CU-REG-003                        |
| ~~RolPermiso~~ | Derogado. Su trazabilidad pasa a `AdminFeria`: CU-FER-001, CU-FER-002, CU-FER-003, CU-FER-004 |

---

## 5. Temas abiertos del modelo

- **Migración pendiente de código:** lo desplegado en `feature/registro-otp` tiene
  `Persona.nombre_completo` (un solo campo). Este documento fija `nombres`/`apellidos`
  separados como decisión definitiva (2026-08-19) — falta la migración de schema (y de datos,
  si ya hay registros de desarrollo cargados) para alinear el código real con este modelo.
- ~~**Reconciliar `admin`(usuario, feria) con `RolPermiso`(modulo, nivel)**~~ — **resuelto el
  2026-08-21**: `RolPermiso` se deroga y lo sustituye `AdminFeria`. Ver §2.2 y
  [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>). Queda como trabajo de código
  retirar `RolPermiso` y el decorador `requiere_modulo` de `filey/apps/registros/`.
- ~~**Confirmar el alcance de unicidad de `Persona.correo`**~~ — **confirmado el 2026-08-21**:
  el correo es único **globalmente**, no por feria, y así queda fijado por
  [ADR-0003](<../../adr/0003-una-feria-por-schema.md>), que coloca `Persona` en el schema
  `public` y el contenido de cada feria en el suyo. La cuenta no pertenece a ninguna feria.
  Nadie debe cambiarlo a único por feria sin reemplazar ese ADR.
- **`es_recurrente` (¿ya participó en ediciones anteriores?) — deuda pendiente, no una
  decisión por tomar hoy.** Cada dominio de captura (`EVT`, y a futuro `TAL`/`STD`/`VIS`)
  necesita saber si un participante es recurrente, pero el dato solo tiene sentido si vive
  donde algo trasciende instancias de feria — es decir, aquí, en `Persona`. Implementarlo de
  verdad exige una tabla nueva de participación histórica (qué `Persona` participó en qué
  convocatoria de qué edición), que no existe todavía y que añade complejidad no justificada
  mientras solo haya una edición corriendo. Además, **no es verificable hasta que el sistema
  se use al menos dos veces para dos ediciones de la misma feria** — no hay forma de probar
  que funciona antes de eso. Ver la nota original en
  `EVT/Modelo de datos - Eventos.md` (sección 5), que es donde primero se detectó el hueco al
  eliminar `Proponente.es_recurrente`.
