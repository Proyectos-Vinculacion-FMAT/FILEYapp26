---
estado: propuesta
version: "2.1"
tags:
  - tipo/modelo-de-datos
  - dom/std
fecha: 2026-06-18
fecha_actualizacion: 2026-08-25
---
# Modelo de datos — Stands (reserva, pago y confirmación)

> Modelo **conceptual**: identifica las entidades y los datos que el sistema debe
> almacenar, sin comprometer aún tipos de base de datos, índices ni claves físicas.
> Las relaciones se describen en la sección 4.

<!-- -->

> [!important] Cambio 2026-08-21 — `STD` deja de modelar cuentas y ediciones de la feria
> La v1.0 definía dos entidades que no le pertenecen: `Cuenta` (acceso y rol del aplicante) y
> `Evento` (la edición de la feria). Ambas se **extraen** a las capas globales del sistema:
>
> | Entidad v1.0 | Dónde vive ahora | Por qué |
> | --- | --- | --- |
> | `Cuenta` | `Persona`, en [`REG`](<../REG/Modelo de datos - Registros.md>) | La identidad es única y global: quien expone en 2027 y propone una actividad en 2028 es la misma cuenta, con el mismo correo. `STD` no puede tener su propia noción de usuario. |
> | `Evento` | `Feria`, en [`FER`](<../FER/Modelo de datos - Ferias.md>) | La edición de la feria es el contenedor de **todos** los dominios, no un dato de `STD`. |
>
> No es un movimiento de cajas: cambia cómo se escribe este dominio. Ver la sección 2, que
> explica qué desaparece y con qué se sustituye cada cosa.

<!-- -->

> [!important] Cambio 2026-08-25 — `STD` se cuelga de su convocatoria (v2.1)
> Cuatro cambios, ninguno reversible sin volver a discutirlos:
>
> | Cambio | Dónde |
> | --- | --- |
> | `ConfiguracionSistema` se renombra a **`ConfiguracionSistema`** y pasa a colgar de la convocatoria. | §3.11 |
> | `Solicitud` gana **`registro_id`** → `RegistroConvocatoria` (`FER`). Es el enganche del dominio con su convocatoria. | §3.3 |
> | `ReservaStand` **pierde** `metros_cuadrados_snapshot` y `precio_snapshot`. | §3.7 |
> | `DescuentoAplicado` gana una **restricción única por (`reserva_id`, `tipo`)**: como mucho un pronto pago y un especial por reserva. | §3.9 |

---

## 1. Qué vive fuera de este modelo

Antes de las entidades propias, lo que `STD` **usa pero no define**. Viven en el schema
`public`, una sola vez para todo el sistema
([ADR-0003](<../../adr/0003-una-feria-por-schema.md>)):

| Entidad | Dominio | Qué aporta a `STD` |
| --- | --- | --- |
| `Persona` | `REG` | La cuenta de quien aplica, revisa, registra un abono o lo valida. Toda FK que la v1.0 dirigía a `Cuenta` apunta ahora aquí. |
| `Feria` | `FER` | La edición. **No se referencia con una FK**: ver la nota de abajo. |
| `AdminFeria` | `FER` | Quién puede operar el panel de stands de esta feria. `STD` no define permisos propios. |
| `Convocatoria` | `FER` | La convocatoria de venta de stands de esta feria (`tipo = STD`). Es quien dice si se admiten solicitudes. Vive en el schema de la feria, no en `public`. |
| `RegistroConvocatoria` | `FER` | Que una persona se inscribió a esa convocatoria. Es de donde cuelga toda la aplicación a expositor — ver §3.3. |

> [!important] `STD` no lleva `evento_id` en ninguna tabla — y no es un olvido
> Cada feria vive en su propio schema de base de datos. Los stands, las reservas y los abonos
> de FILEY 2027 están físicamente separados de los de FILEY 2028, así que **la edición es
> implícita**: una consulta de `STD` no puede alcanzar los datos de otra edición porque no
> están en el schema en el que está mirando.
>
> Por eso desaparecen `Solicitud.evento_id`, `Stand.evento_id` y `Reserva.evento_id`. Añadir
> uno de vuelta no solo sería redundante: reintroduciría la posibilidad de escribir la consulta
> que mezcla ediciones, que es justo lo que la separación por schema elimina. Es la misma
> decisión que `EVT` ya aplica en su modelo.

---

## 2. Qué se extrajo, y con qué se sustituye

### 2.a `Cuenta` → `Persona` (`REG`)

La v1.0 la marcaba como *"ilustrativo, fuera del scope de este componente"*. Ahora tiene un
dueño real, y sus atributos no sobreviven todos:

| Atributo de `Cuenta` (v1.0) | Qué pasa con él |
| --- | --- |
| `id`, `correo`, `estado`, `fecha_registro` | Existen igual en `Persona`. El correo es único **en todo el sistema**, no por feria. |
| `contrasena_hash` | **Desaparece.** No hay contraseñas: todo acceso es por OTP por correo (CU-REG-002 / CU-REG-003). |
| `rol` (`aplicante` / `administrador`) | **Desaparece.** Ser administrador no es un atributo de la cuenta: es tener acceso a una feria (`AdminFeria`, [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>)). La misma persona puede administrar una feria y ser aplicante en otra sin ambigüedad. |
| `es_recurrente` | **Desaparece de aquí**, y sigue sin implementarse. Saber si un expositor ya participó en ediciones anteriores exige comparar entre ferias, así que solo puede vivir en la capa global — es deuda registrada en `REG` §5 y `EVT` §5, no algo que `STD` pueda resolver por su cuenta. |

### 2.b `Evento` → `Feria` (`FER`)

| Atributo de `Evento` (v1.0) | Qué pasa con él |
| --- | --- |
| `id`, `nombre`, `fecha_inicio`, `fecha_fin` | Existen igual en `Feria`. |
| `edicion` (número, p. ej. XIV) | Se **añade a `Feria`**: es un dato de la edición, útil para cualquier dominio que imprima su nombre completo. |
| `sede` (p. ej. Centro de Convenciones Yucatán Siglo XXI) | Se **añade a `Feria`**: la sede es de la feria entera, no del showfloor. `PRG` y `SAL` la necesitan igual. |
| `salon` (p. ej. Salón Chichén Itzá) | **Se queda en `STD`**, en `ConfiguracionSistema` (§3.11). Es dónde se monta el showfloor, no dónde ocurre la feria: son cosas distintas y en 2026 coincidieron por casualidad. |

---

## 3. Detalle de entidades y atributos

Todas las entidades de esta sección viven **dentro del schema de una feria**.

### 3.1 Editorial
> Datos provenientes de la Ficha de Registro para Expositores.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| persona_id | FK → `Persona` (`REG`). Quién presenta y administra esta editorial. |
| nombre | Nombre de la editorial. |
| domicilio_calle, domicilio_numero, domicilio_colonia | Domicilio. |
| cp, municipio, estado, pais | Domicilio (cont.). |
| director_general_nombre, director_general_email | Contacto. |
| director_comercial_nombre, director_comercial_email | Contacto. |
| director_editorial_nombre, director_editorial_email | Contacto. |
| director_promocion_nombre, director_promocion_email | Contacto. |
| responsable_stand | Responsable del stand. |
| giro | `Editor` / `Librero` / `Distribuidor`. |
| telefono_oficina, telefono_celular | Teléfonos. |
| correo_electronico | Correo de contacto. **No es el correo de acceso**: ese vive en `Persona` y puede ser otro (p. ej. la cuenta personal de quien tramita, frente al buzón comercial de la editorial). |
| nombre_antepecho | Nombre que aparecerá en el antepecho del stand. |
| num_personas_atienden | Personas que atenderán el módulo. |
| total_sellos | Total de sellos editoriales participantes. |
| cantidad_libros_aprox | Cantidad aproximada de libros. |
| cantidad_titulos_aprox | Cantidad aproximada de títulos. |
| materiales | Multivalor: Libro, Audiolibro, Revista, Material didáctico, Libros electrónicos, Otro. |
| tematicas | Multivalor: lista de temáticas (Administración, Arte, Infantil, …). |
| constancia_fiscal_id | FK → Documento — Constancia de Situación Fiscal. Permite emitir facturas por fuera del sistema. |

> [!note] `Editorial` es de la feria, `Persona` es global
> Una editorial que expone en 2027 y en 2028 tiene **dos** registros `Editorial`, uno en cada
> schema, y **una sola** `Persona` detrás. Es lo correcto: la Ficha de Registro se llena cada
> edición y sus datos cambian (domicilio, directores, número de sellos). Lo que no cambia —
> quién es la persona— no se duplica.
>
> La contrapartida es que `STD` no puede saber por sí solo si una editorial ya participó antes:
> eso es la deuda de `es_recurrente` (§2.a).

### 3.2 SelloEditorial
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| editorial_id | FK → Editorial. |
| nombre | Nombre del sello/fondo editorial representado. |

### 3.3 Solicitud
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| registro_id | FK → `RegistroConvocatoria` (`FER`). **Uno a uno**: una solicitud es la participación de esa persona en la convocatoria de stands de esta feria. Ver la nota de abajo. |
| editorial_id | FK → Editorial. |
| estado | `pendiente` / `aceptada` / `rechazada` / `cambios_solicitados`. |
| fecha_envio | Fecha de envío. |
| fecha_revision | Fecha de revisión. |
| revisado_por | FK → `Persona` (`REG`) — el administrador que dictaminó. |
| motivo_peticion | Texto (si se solicitaron cambios o hay nota de rechazo). |

> [!important] Por qué el enganche va aquí y no en `Editorial`
> Quien se registra a una convocatoria es una **persona**, no una empresa: `RegistroConvocatoria`
> liga `Persona` con `Convocatoria` y nada más (ver [`FER`](<../FER/Modelo de datos - Ferias.md>)
> §3.4). En `STD`, lo que esa persona hace al registrarse es **aplicar a ser expositor**, y eso
> es exactamente una `Solicitud`. Por eso el enganche va aquí:
>
> - **`Solicitud` es la unidad que la convocatoria gobierna.** Que la convocatoria esté abierta o
>   cerrada decide si se puede enviar o reenviar una solicitud (CU-STD-001, CU-STD-002); no
>   decide nada sobre una `Editorial`, cuyos datos se pueden corregir después del cierre.
> - **`Editorial` es un expediente, no una inscripción.** Sigue colgando de `Persona` y se llena
>   una vez por feria. Poner ahí el `registro_id` obligaría a crear la editorial completa antes
>   de existir la solicitud, e impediría que una persona representara a dos editoriales.
> - **La cadena queda entera sin duplicar nada:**
>   `Persona → RegistroConvocatoria → Solicitud → Editorial → Reserva → Movimiento`. Ni `Reserva`
>   ni `Movimiento` necesitan su propio `registro_id`: llegan a la convocatoria por la solicitud.
>
> **Ojo desde el 2026-08-25:** ya no hay una sola convocatoria de stands por feria, así que "la
> solicitud de esta persona en esta feria" **ya no es una sola cosa**. La misma editorial puede
> aplicar a dos convocatorias de stands de la misma edición y tener dos solicitudes, dos reservas
> y dos saldos. Lo que sigue siendo único es la solicitud **por registro**: uno a uno.

> *Nota de diseño:* la información del formulario se solapa con **Editorial**. Decidir con
> el equipo si la solicitud guarda una copia (snapshot) de los datos enviados o si
> referencia directamente a la editorial. Los **documentos** de la solicitud se modelan en `Documento`.

### 3.4 Documento
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| tipo | `comprobante_pago`, `carta_representacion`, `lista_titulos`, `constancia_fiscal`, `doc_abono`, `otro`. |
| archivo_url | Ubicación/almacenamiento del archivo. |
| fecha_carga | Fecha de carga. |
| entidad_tipo | Entidad relacionada (`editorial`, `aplicacion`, `movimiento`). |
| entidad_id | Id de la entidad relacionada. |

### 3.5 Stand
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| clave | Identificador visible en el mapa. |
| pos_x, pos_y | Ubicación/coordenadas en el mapa. |
| ancho, largo | Dimensiones. |
| metros_cuadrados | Superficie (base del cálculo de precio). |
| estado | `Disponible` / `Reservado` / `Ocupado`. |
| incluye | Descripción de lo que incluye (estructura, contactos, exhibidores, etc.). |

> [!note] El mapa se rehace cada edición, y eso ahora sale gratis
> Los stands pertenecen al schema de su feria, así que rediseñar el showfloor de 2028 no toca
> nada de 2027 — ni sus reservas, ni su historial de pagos. Antes, con `evento_id`, convivían
> en la misma tabla y cualquier consulta que lo olvidara mezclaba dos mapas.

### 3.6 Reserva
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| editorial_id | FK → Editorial. |
| estado | `Por confirmar` / `Confirmada` / `Pagada` / `Cancelada`. |
| fecha_creacion | Inicio del plazo de 30 días. |
| fecha_vencimiento_anticipo | `fecha_creacion` + 30 días. |
| fecha_corte_pago_total | Fecha de bloqueo/límite de pago del 100% (modificable por admin). |
| monto_total | Suma de líneas, con descuento aplicado. |
| monto_abonado | Derivado de movimientos validados. |
| monto_pendiente | Derivado (`monto_total − monto_abonado`). |

### 3.7 ReservaStand
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| reserva_id | FK → Reserva. |
| stand_id | FK → Stand. |

`ReservaStand` es ahora una tabla puramente de unión: qué stands entran en qué reserva.

> [!warning] Se eliminó el snapshot de m² y precio — qué se gana y qué se pierde
> **Se gana** que deje de haber dos fuentes de verdad para la misma cifra. Los m² del stand
> están en `Stand.metros_cuadrados` y el precio se deriva de `ConfiguracionSistema.costo_m2`
> (§3.11); copiarlos a la línea abría la puerta a que la copia y el original discreparan sin que
> nadie se enterara.
>
> **Se pierde el desglose histórico por línea.** Si un administrador corrige el mapa
> (CU-STD-033, p. ej. amplía un stand) o cambia `costo_m2` (CU-STD-034), el desglose que ve una
> reserva ya confirmada se recalcula con los valores nuevos y deja de cuadrar con lo que la
> editorial aceptó en su momento.
>
> **Lo que sí queda congelado es el total:** `Reserva.monto_total` se almacena, no se deriva
> (§3.6). Así que el importe cobrado no cambia retroactivamente — lo que cambia es cómo se
> explica. Con eso el riesgo pasa de "cobramos otra cifra" a "el desglose no cuadra con el
> total", que es molesto pero no es un error de dinero.
>
> **Condición para que esto se sostenga:** el servicio que recalcula un desglose **nunca** debe
> reescribir `monto_total` de una reserva que no esté `Por confirmar`. Si en algún momento hace
> falta reconstruir el desglose exacto de una reserva vieja, la salida es la `Bitacora` (§3.12),
> no reponer los snapshots.

### 3.8 Movimiento
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| reserva_id | FK → Reserva. |
| monto | Monto del abono. |
| metodo | `transferencia` / `deposito` / `cheque`. |
| origen | `aplicante` / `admin_manual`. |
| estado | `pendiente_validacion` / `validado` / `rechazado`. |
| comprobante_id | FK → Documento (obligatorio en abono manual del admin). |
| registrado_por | FK → `Persona` (`REG`). |
| fecha_registro | Fecha de registro. |
| validado_por | FK → `Persona` (`REG`) — el administrador que validó. |
| fecha_validacion | Fecha de validación. |

### 3.9 DescuentoAplicado
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| reserva_id | FK → Reserva. |
| tipo | `pronto_pago` (10%) / `especial`. |
| porcentaje | Porcentaje aplicado. |
| motivo | Obligatorio para `especial`. |
| aplicado_por | FK → `Persona` (`REG`); nulo cuando lo aplica el sistema (pronto pago automático, CU-STD-023). |
| fecha | Fecha de solicitud. |

**Restricciones:**

- Único por (`reserva_id`, `tipo`): una reserva tiene **como máximo un** descuento de
  `pronto_pago` y **como máximo un** descuento `especial`. Nunca más de dos filas en total.

> [!important] La regla vive en la base de datos, no en la vista
> Antes esto era una frase en la sección de relaciones ("máximo dos"), y una frase no impide
> nada: dos administradores aplicando un descuento especial a la vez, o CU-STD-023 corriendo dos
> veces sobre la misma reserva, insertaban dos filas del mismo tipo y el total salía mal. Con la
> restricción única, el segundo intento **falla en la escritura** y cada caso de uso decide qué
> hacer:
>
> - **`pronto_pago` (CU-STD-023, automático):** el segundo intento es idempotente — si ya existe,
>   no es un error, es que el descuento ya estaba aplicado. No debe alarmar a nadie.
> - **`especial` (CU-STD-020, manual):** el segundo intento **sí** es un error que se muestra. El
>   administrador que quiera cambiar el porcentaje tiene que modificar el existente —dejando
>   rastro en `Bitacora`— o retirarlo y volver a aplicarlo, no acumular uno encima.
>
> Falta decidir si retirar un descuento borra la fila o la marca; hoy el modelo no tiene estado
> en esta entidad. Ver §6.

### 3.10 Notificacion
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| destinatario_id | FK → `Persona` (`REG`). |
| tipo | `aplicacion_aceptada`, `aplicacion_rechazada`, `aplicacion_cambios`, `reserva_confirmada`, `reserva_pagada`, `posible_cancelacion`, `reserva_cancelada`. |
| fecha_envio | Fecha de envío. |
| estado | `enviada` / `fallida`. |
| referencia_tipo, referencia_id | Entidad relacionada (solicitud / reserva). |

### 3.11 ConfiguracionSistema
> Configuración de **una** convocatoria de stands. Una fila por convocatoria, no una por feria.

| Atributo | Descripción |
|----------|-------------|
| convocatoria_id | FK → `Convocatoria` (`FER`), con `tipo = STD`. **Único**: cada convocatoria de stands tiene exactamente una configuración, y ninguna configuración flota sin convocatoria. |
| costo_m2 | Costo por metro cuadrado (p. ej. $2,500). |
| porcentaje_anticipo | Porcentaje para confirmar (50%). |
| plazo_reserva_dias | Días de vigencia de la reserva (30). |
| descuento_pronto_pago | Porcentaje (10%). |
| fecha_limite_pronto_pago | Fecha límite del pronto pago. |
| instrucciones_pago | Texto/datos bancarios (banco, cuenta, CLABE, sucursal, referencia). |
| salon_showfloor | Salón donde se monta el showfloor (p. ej. Salón Chichén Itzá). Viene del `Evento.salon` de la v1.0. |

> [!note] Las fechas de apertura y cierre **no** están aquí
> Quién puede enviar una solicitud y hasta cuándo lo decide `Convocatoria` (`FER` §3.3), no esta
> tabla. Lo que queda aquí es lo específico de stands: precios, porcentajes, plazos de pago y
> datos bancarios. `fecha_limite_pronto_pago` sí es de stands —es una regla de cobro, no la
> vigencia de la convocatoria— y se queda.

> [!warning] Cambio 2026-08-25 — puede haber **varias** convocatorias de stands en una feria
> Este documento asumía una convocatoria de stands por feria, y de ahí que esta fuera "una tabla
> de una sola fila". Ese supuesto **se retiró**
> ([`FER`](<../FER/Modelo de datos - Ferias.md>) §3.3): una feria puede abrir una convocatoria
> general y otra para un pabellón concreto, con precios y plazos distintos.
>
> El modelo aguanta el cambio sin tocar columnas —la configuración ya colgaba de
> `convocatoria_id`— pero **cambia lo que puede asumir el código**:
>
> | Ya no vale | En su lugar |
> | --- | --- |
> | "Lee la configuración" (hay una). | Lee la configuración **de esta convocatoria**. |
> | "El costo por m² de la feria". | El costo por m² **de esta convocatoria**. Dos stands de la misma feria pueden valer distinto. |
> | "La reserva de esta editorial". | La editorial puede tener una reserva **por convocatoria**, con saldos independientes. |
>
> Los casos de uso de `STD` se escribieron dando por hecho que había una sola, así que **hablan
> de "la convocatoria" en singular**. Revisarlos es trabajo pendiente (§6).

<!-- -->

> [!warning] Estos parámetros **no son globales**, aunque el nombre lo sugiera
> La v1.0 los describía como "configuración global del sistema". Con una feria por schema eso
> es falso y además peligroso: `costo_m2` y `fecha_limite_pronto_pago` cambian en cada edición,
> y son precisamente los datos que no deben compartirse entre ferias. Cada feria tiene su
> propia fila.
>
> El renombrado del 2026-08-25 a `ConfiguracionSistema` **no arregla esto**: "Sistema" sigue
> diciendo global, que es justo lo que no es, y sigue sin homologar con el
> `ParametrosConvocatoria` de `EVT`. Es el nombre acordado y se aplica tal cual; la
> inconsistencia queda registrada en §6.
>
> Lo que sí cambia de fondo es el `convocatoria_id`: la configuración pasa a colgar de la
> convocatoria que configura, en lugar de flotar sola en el schema.

### 3.12 Bitacora
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| persona_id | FK → `Persona` (`REG`) — quién ejecutó la acción. |
| accion | Acción (validar abono, prorrogar, descuento especial, editar mapa, etc.). |
| entidad_tipo, entidad_id | Objeto afectado. |
| detalle | Datos del cambio. |
| fecha | Marca de tiempo. |

---

## 4. Relaciones principales

- **Persona** (`REG`) 1—N **Editorial**: una persona puede representar a una editorial en esta
  feria, y a otra en otra feria. Dentro de una misma feria, una editorial por persona.
- **Editorial** 1—N **SelloEditorial**.
- **RegistroConvocatoria** (`FER`) 1—1 **Solicitud**: es el enganche del dominio con su
  convocatoria (§3.3). Cada registro tiene una solicitud y solo una — pero una misma persona
  puede tener varios registros en la misma feria si hay varias convocatorias de stands.
- **Convocatoria** (`FER`) 1—1 **ConfiguracionSistema**: una configuración por convocatoria de
  stands, no una por feria (§3.11).
- **Editorial** 1—N **Solicitud** (una activa por feria; permite reenvío tras solicitud de
  cambios, o creación de nueva tras rechazo).
- **Editorial** 1—1 **Documento** (Constancia de Situación Fiscal).
- **Solicitud** 1—N **Documento**; **Movimiento** 1—1 **Documento** (comprobante).
- **Editorial** 1—N **Reserva**; **Reserva** 1—N **ReservaStand** N—1 **Stand**
  (un stand pertenece a lo sumo a una reserva activa). `ReservaStand` ya no guarda importes: el
  precio se deriva de `Stand` y `ConfiguracionSistema` (§3.7).
- **Reserva** 1—N **Movimiento**.
- **Reserva** 1—N **DescuentoAplicado**, con un tope real: único por (`reserva_id`, `tipo`), o sea máximo dos filas — un pronto pago y un especial (§3.9).
- **Persona** (`REG`) 1—N **Notificacion**.

> [!note] Las relaciones con `Persona` cruzan la frontera del schema
> `Persona` vive en `public` y todo lo demás en el schema de la feria. Es la única frontera que
> el modelo atraviesa, y a propósito: la identidad tiene que ser una sola. Las demás relaciones
> son internas a la feria.

---

## 5. Mapa entidad → caso de uso (trazabilidad)

| Entidad | Casos de uso relacionados |
|---------|---------------------------|
| Editorial / SelloEditorial | CU-STD-001, CU-STD-002, CU-STD-030, CU-STD-031 |
| Solicitud / Documento | CU-STD-001–CU-STD-008, CU-STD-031 |
| Stand | CU-STD-009, CU-STD-010, CU-STD-032, CU-STD-033 |
| Reserva / ReservaStand | CU-STD-011–CU-STD-014, CU-STD-021, CU-STD-022, CU-STD-035, CU-STD-036, CU-STD-028, CU-STD-029 |
| Movimiento | CU-STD-015–CU-STD-019, CU-STD-029 |
| DescuentoAplicado | CU-STD-006, CU-STD-020, CU-STD-023 |
| Notificacion | CU-STD-008, CU-STD-014, CU-STD-024, CU-STD-025, CU-STD-026, CU-STD-027 |
| ConfiguracionSistema | CU-STD-010, CU-STD-023 (cálculos y descuentos), CU-STD-034 (configuración) |
| *`Convocatoria` / `RegistroConvocatoria` (`FER`)* | CU-STD-001 (crea el registro al aplicar); la apertura y el cierre de la convocatoria son casos de uso de `FER` que **todavía no existen** |
| *`Persona` (`REG`)* | CU-REG-001–CU-REG-004; en `STD` aparece como el actor de CU-STD-001 y como `revisado_por`/`registrado_por`/`validado_por` |
| *`Feria` (`FER`)* | CU-FER-001, CU-FER-002; en `STD` es el schema en el que ocurre todo |

---

## 6. Temas abiertos del modelo

- Confirmar si **Solicitud** guarda snapshot de datos o referencia a **Editorial**.
- El único estado de cierre es `Cancelada` (decisión del administrador). El sistema no
  libera reservas automáticamente.
- Necesidad real de **Bitacora** (auditoría) — sugerida por las acciones sensibles del
  administrador (validar abono, descuento especial, prórroga).
- **Los casos de uso de `STD` dicen "la convocatoria" en singular.** Se escribieron cuando había
  una sola convocatoria de stands por feria; desde el 2026-08-25 puede haber varias (§3.11). Hay
  que revisarlos uno por uno para que cada mención diga **cuál**: CU-STD-001 (a qué convocatoria
  aplica), CU-STD-010 y CU-STD-023 (con qué `costo_m2` calcula), CU-STD-034 (qué configuración
  edita) y las pantallas de administración, que hoy listarían solicitudes de todas mezcladas.
  Es la deuda más concreta que dejó ese cambio.
- **Homologar el nombre de `ConfiguracionSistema`** con el `ParametrosConvocatoria` de `EVT`.
  Siguen siendo la misma figura —la configuración de una convocatoria dentro de una feria— con
  dos nombres, y el de `STD` sigue diciendo "Sistema", que es justo lo que no es. El renombrado
  del 2026-08-25 (`ParametrosSistema` → `ConfiguracionSistema`) fue el acordado y ya está
  aplicado en los ocho documentos que lo mencionaban, pero **no cierra este punto**: si algún
  día se homologa de verdad, el nombre que lo diría bien es `ConfiguracionConvocatoria`.
- **Qué pasa al retirar un descuento.** La restricción única de §3.9 impide dos descuentos del
  mismo tipo, pero `DescuentoAplicado` no tiene estado: cambiar un descuento especial exige
  borrar la fila o editarla, y hoy el modelo no dice cuál. Si se decide borrarla, la `Bitacora`
  es el único rastro de que existió.
- **Reconstruir el desglose de una reserva vieja.** Sin los snapshots de `ReservaStand` (§3.7),
  el desglose por línea de una reserva confirmada se recalcula con los valores actuales del mapa
  y de `costo_m2`. Falta decidir si eso basta o si CU-STD-029 (detalle de la reserva) necesita
  mostrar el desglose tal como se aceptó — en cuyo caso la fuente es la `Bitacora`, no reponer
  las columnas.
- **`es_recurrente`**: `STD` necesita saber si un expositor ya participó en ediciones
  anteriores (era un atributo de `Cuenta` en la v1.0). No se resuelve dentro de este dominio:
  exige una tabla de participación histórica en la capa global. Es la misma deuda que ya
  registran `REG` §5, `EVT` §5 y `FER` §6 — cuando se implemente, se implementa una vez para
  los cuatro.
- **Correo de contacto duplicado**: `Editorial.correo_electronico` convive con
  `Persona.correo`. Se conservan ambos a propósito (§3.1), pero conviene confirmar con el
  cliente que el segundo no debe prellenarse desde el primero al llenar la Ficha.

---

## Reglas de negocio relacionadas

Las reglas RN-01 a RN-17 que rigen estos datos (cálculo por m², anticipo del 50% con
descuento, plazo de 30 días, descuentos no acumulables, estados de stand y reserva, etc.)
están documentadas en los requisitos del dominio y en el inventario de casos de uso
(`CU-STD Índice.md`).
