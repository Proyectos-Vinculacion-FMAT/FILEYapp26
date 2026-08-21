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
> (`Persona`) y el acceso administrativo por módulo (`RolPermiso`), más el mecanismo de login
> (`SesionOTP`). Todos los demás dominios (`EVT`, `TAL`, `STD`, `VIS`) referencian estas
> entidades en vez de redefinirlas — ver la nota de cada uno de sus "Modelo de datos".

<!-- -->

> [!warning] Este core **ya está construido**, a diferencia de la mayoría de este repositorio
> `Persona`, `RolPermiso` y `SesionOTP` existen hoy como código real en
> `filey/apps/registros/models.py` (rama `feature/registro-otp`), implementando
> `CU-REG-001`/`002`/`003`/`005`. Este documento describe el modelo **objetivo** tras la
> sesión de diseño del 2026-08-19 (`nombres`/`apellidos` separados) — donde diverge de lo
> desplegado, se marca explícitamente. Migrar el código real a este modelo es trabajo aparte,
> no un efecto de editar este documento.

---

## 1. Resumen de entidades

| Entidad     | Propósito                                                                              |
| ----------- | ---------------------------------------------------------------------------------------- |
| Persona     | Identidad única del sistema — registro mínimo, compartido entre todos los módulos.      |
| RolPermiso  | Qué módulos puede administrar una `Persona`, y con qué nivel.                           |
| SesionOTP   | Código de un solo uso para autenticar una sesión (sin contraseña para usuarios externos). |

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

### 2.2 RolPermiso

> Lo que distingue a una cuenta administrativa: tener al menos un `RolPermiso` (`CU-REG-003`,
> `CU-REG-005`). Sin `RolPermiso`, la `Persona` es un usuario externo normal.

| Atributo    | Descripción                                                                                     |
| ------------ | --------------------------------------------------------------------------------------------- |
| id          | Identificador único.                                                                            |
| persona_id  | FK → Persona.                                                                                    |
| modulo      | `EVT` / `TAL` / `STD` / `VIS` / `*` (todos los módulos — administrador general).                |
| nivel       | `lectura` / `edicion` (acumulativo: quien puede editar también puede leer).                      |
| creado_en   | Fecha de asignación del permiso.                                                                 |

> Restricción: único por (`persona_id`, `modulo`) — no se puede duplicar el permiso de un
> mismo módulo para la misma persona (`CU-REG-005`, E1).

> [!note] Relación pendiente con `admin`(usuario, feria) — sesión de diseño 2026-08-19
> En esa sesión se propuso una tabla `admin(usuario, feria)` para controlar acceso por
> **feria**, con `feria` como FK a un dominio de Ferias "aún sin contemplar formalmente"
> (multi-tenant, fuera del alcance actual — solo existe una feria implícita hoy). Mientras
> `Feria` no exista, `RolPermiso` sigue siendo el único control de acceso administrativo y ya
> cumple lo que pide `CU-REG-005` (módulo + nivel, cosa que `admin(usuario, feria)` tal como
> se esbozó no cubre). Queda pendiente decidir, cuando `Feria` se formalice, si `RolPermiso`
> gana un `feria_id` o si el acceso queda en dos niveles: `admin` decide *si* eres
> administrador de esa feria, `RolPermiso` decide *de qué módulos* dentro de ella — ver
> sección 5.

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

- **Persona** 1—N **RolPermiso** (una persona puede administrar varios módulos).
- **Persona** 1—N **SesionOTP** (historial de códigos emitidos; en la práctica, 0 o 1 vigente a la vez).
- **Persona** 1—N *(entidad de solicitud de cada dominio)* — ver `EVT/Modelo de datos - Eventos.md` (`Propuesta.participante_id`) y equivalentes en `TAL`/`STD`/`VIS`.

---

## 4. Mapa entidad → caso de uso (trazabilidad)

| Entidad     | Casos de uso relacionados                  |
| ----------- | --------------------------------------------- |
| Persona     | CU-REG-001, CU-REG-002, CU-REG-003, CU-REG-004 |
| RolPermiso  | CU-REG-003, CU-REG-005                        |
| SesionOTP   | CU-REG-002, CU-REG-003                        |

---

## 5. Temas abiertos del modelo

- **Migración pendiente de código:** lo desplegado en `feature/registro-otp` tiene
  `Persona.nombre_completo` (un solo campo). Este documento fija `nombres`/`apellidos`
  separados como decisión definitiva (2026-08-19) — falta la migración de schema (y de datos,
  si ya hay registros de desarrollo cargados) para alinear el código real con este modelo.
- **Reconciliar `admin`(usuario, feria) con `RolPermiso`(modulo, nivel)** cuando el dominio
  `Feria` se formalice (ver nota en 2.2). No es urgente mientras solo exista una feria
  implícita, pero conviene decidirlo antes de que haya datos reales de `RolPermiso` que migrar.
- **Confirmar el alcance de unicidad de `Persona.correo`** una vez exista `Feria`: la sesión
  de diseño 2026-08-19 estableció que las ferias son "planas" (cada edición es una instancia
  propia) y que los usuarios se comparten entre todas — lo cual ya es compatible con el
  `unique=True` global desplegado hoy. Dejar constancia aquí para que nadie lo cambie a único
  *por feria* sin revisar esta decisión.
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
