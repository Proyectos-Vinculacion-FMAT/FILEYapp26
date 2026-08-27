---
estado: propuesta
version: "3.0"
tags:
  - tipo/modelo-de-datos
  - dom/std
fecha: 2026-06-18
fecha_actualizacion: 2026-08-27
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

<!-- -->

> [!important] Cambio 2026-08-27 — el mapa es de la convocatoria y el modelo lo puede generar (v3.0)
> Ronda de decisiones tomada al planear la construcción del módulo. Cierra seis de los temas
> abiertos de §6 y abre el modelo a generar el JSON del mapa sin datos externos.
>
> | Decisión | Dónde | Regla |
> | --- | --- | --- |
> | **Un mapa por convocatoria.** `Stand` gana `convocatoria_id`; aparecen `MapaShowfloor` y `DecoracionMapa`. | §3.5, §3.13, §3.14 | RN-19 |
> | **El modelo lleva ya todo lo que el mapa dibuja**: retícula, forma en celdas, formas irregulares y zona. | §3.5, §3.13 | RN-19 |
> | **Los estados del mapa son los del dominio.** El componente se ajusta al dominio, no al revés. | §3.5 | RN-20 |
> | **El precio se queda como estaba**: `m² × costo_m2` de la convocatoria. La zona es descriptiva y **no** fija precio. | §3.11 | RN-01, RN-19 |
> | **`Solicitud` es un snapshot**, y tras un rechazo se puede volver a aplicar con la misma editorial. La relación con el registro pasa a **1—N**. | §3.3 | RN-22 |
> | **Una editorial por persona y por feria**, en los dos sentidos. | §3.1 | RN-21 |
> | **`Notificacion` es tabla de `STD`**, con el envío en `apps/notificaciones`. **La bitácora, una por módulo.** | §3.10, §3.12 | — |
>
> Las reglas viven ahora en un documento propio:
> [`Reglas de negocio - Stands`](<Reglas de negocio - Stands.md>).

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
| materiales | Multivalor: Libro, Audiolibro, Revista, Material didáctico, Libros electrónicos, Otro. Con `materiales_otro` para el texto de «Otro (especificar)». |
| tematicas | Multivalor: las **61 entradas** de la Ficha de Registro p. 2 (60 temáticas más «Otros»). Con `tematicas_otra` para el texto. |
| constancia_fiscal_id | FK → Documento — Constancia de Situación Fiscal. Permite emitir facturas por fuera del sistema. |

> [!note] Validado contra la ficha oficial (2026-08-27)
> Se comparó campo por campo con `Registro-para-Expositores-FILEY-2026.pdf`. Todo lo de arriba
> coincide, y aparecieron cuatro huecos que ya se cerraron: el catálogo de temáticas tenía nueve
> entradas y la ficha tiene 61; faltaba el texto de «Otro (especificar)» en materiales y en
> temáticas; faltaba la aceptación de las bases (§3.3); y el aviso de que cambiar el antepecho
> después se cobra.
>
> **Lo que no se construyó, y por qué:** la ficha ofrece «Tipo de stand: Básico / Personalizado».
> Se descartó por decisión del equipo — el básico 3×2 son $15,000, que es exactamente el
> `costo_m2` de $2,500 por sus 6 m², así que la distinción no cambia ni el precio ni el modelo.
>
> **Pendiente de resolver con el cliente:** las bases admiten *"instituciones de educación
> superior, librerías, asociaciones civiles y dependencias gubernamentales"*, pero la ficha solo
> ofrece `Editor / Librero / Distribuidor` en el campo `giro`. Los dos documentos se contradicen;
> el modelo sigue a la ficha.
>
> Y las bases confirman que la deuda de `es_recurrente` (§2.a) es una **regla operativa real**:
> *"se respetará a los participantes de la última edición"* al asignar espacios.

<!-- -->

> [!warning] El catálogo de temáticas está **sin verificar por una persona**
> La ficha oficial es un **escaneo sin capa de texto**: `pdftotext` no devuelve nada, así que las
> 61 entradas de `apps/stands/models.py::TEMATICAS` se transcribieron **leyendo la imagen** de la
> página 2, columna por columna. La aritmética cuadra —21 + 22 + 19 impresas, menos «Pintura»,
> que aparece repetida— pero una lista de 61 leída de un escaneo es justo donde se esconde una
> errata.
>
> **Hay que contrastarla contra el PDF antes de abrir la convocatoria.** Es un rato de trabajo y
> lo cubre `test_las_tematicas_son_las_de_la_ficha`, que fija la cuenta y las dos correcciones
> conocidas (`Braile` → Braille, `Sofware` → Software).
>
> Contexto de por qué importa: hasta el 2026-08-27 la lista tenía **nueve** entradas inventadas a
> partir del mock del prototipo Angular. El modelo decía *"lista de temáticas (Administración,
> Arte, Infantil, …)"*, con puntos suspensivos, y nadie había abierto el papel.

<!-- -->

> [!important] Una editorial por persona, y una persona por editorial (RN-21)
> Dentro de una feria la relación es **1—1 en los dos sentidos**: una `Persona` tiene una
> `Editorial` y una `Editorial` pertenece a una `Persona`. Representar a otras casas editoras
> **no** se modela con una segunda `Editorial`: eso es `SelloEditorial` más su carta de
> representación (RN-17).
>
> Corrige la relación "1—N" que decía §4 hasta el 2026-08-27, y la justificación de §3.3 que
> hablaba de "una persona representando a dos editoriales".

<!-- -->

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
| registro_id | FK → `RegistroConvocatoria` (`FER`). **Uno a muchos**: el registro es la inscripción de esa persona a esa convocatoria, y de él cuelgan todas sus solicitudes a lo largo del tiempo — con **como mucho una viva** (RN-22). Ver las notas de abajo. |
| datos_editorial | **Fotografía** de los datos de la editorial tal como se enviaron (RN-22). Corregir la ficha después no reescribe lo que el administrador dictaminó. |
| sellos | Fotografía de los sellos declarados en el envío. |
| editorial_id | FK → Editorial. |
| estado | `pendiente` / `aceptada` / `rechazada` / `cambios_solicitados`. |
| bases_aceptadas | Que se aceptaron las bases al enviar. En papel es la firma bajo *"RECONOZCO Y ACEPTO LAS BASES DE PARTICIPACIÓN"* (ficha p. 2). Va aquí y no en `Editorial` porque se aceptan las bases **de esta convocatoria**, en el momento de enviar: es parte de la fotografía. |
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
>   de existir la solicitud, y ataría el expediente a **una** convocatoria cuando la misma
>   editorial puede aplicar a varias de la misma feria.
> - **La cadena queda entera sin duplicar nada:**
>   `Persona → RegistroConvocatoria → Solicitud → Editorial → Reserva → Movimiento`. Ni `Reserva`
>   ni `Movimiento` necesitan su propio `registro_id`: llegan a la convocatoria por la solicitud.
>
> **Ojo desde el 2026-08-25:** ya no hay una sola convocatoria de stands por feria, así que "la
> solicitud de esta persona en esta feria" **ya no es una sola cosa**. La misma editorial puede
> aplicar a dos convocatorias de stands de la misma edición y tener dos solicitudes, dos reservas
> y dos saldos.
>
> **Y desde el 2026-08-27 tampoco es una por registro.** Tras un rechazo, la misma persona puede
> volver a aplicar con la misma editorial (RN-22): la solicitud rechazada se conserva y la nueva
> nace con su propia fotografía. Lo único único es **persona ↔ registro** dentro de una
> convocatoria; de ese registro cuelgan N solicitudes con **como mucho una viva** (`pendiente` o
> `cambios_solicitados`).

> [!important] La invariante que la base de datos NO puede sostener (ADR-0006)
> `registro_id` es una clave foránea real, pero **el `tipo` que decide que este expediente es de
> stands vive un salto más allá**, en `Convocatoria`. Nada en el esquema impide colgar una
> `Solicitud` de stands de un registro de una convocatoria de eventos.
>
> PostgreSQL podría expresarlo con una clave foránea compuesta, pero Django no la soporta de
> forma usable. Se acepta como **invariante de código**: el servicio que crea la solicitud
> comprueba `registro.convocatoria.tipo == STD` y hay una prueba que lo fija. Es la única
> invariante del dominio en esta situación, y por eso está escrita aquí y en
> [ADR-0006](<../../adr/0006-la-liga-entre-convocatoria-y-modulo.md>).

<!-- -->

> [!note] Snapshot, resuelto el 2026-08-27
> El tema abierto desde la v1.0 —*¿la solicitud copia los datos o referencia a la editorial?*—
> queda cerrado: **copia** (RN-22). `editorial_id` se conserva para saber de quién es el
> expediente y para las pantallas de administración (CU-STD-030, CU-STD-031); lo que se
> dictamina son los datos de la fotografía. Los **documentos** se modelan en `Documento`.

### 3.4 Documento
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| tipo | `comprobante_pago`, `carta_representacion`, `lista_titulos`, `constancia_fiscal`, `doc_abono`, `otro`. |
| archivo_url | Ubicación/almacenamiento del archivo. |
| fecha_carga | Fecha de carga. |
| ~~entidad_tipo~~ | **Desviación al construir (2026-08-27):** ver la nota. |
| ~~entidad_id~~ | **Desviación al construir (2026-08-27):** ver la nota. |

> [!important] Se construyó con claves foráneas reales, no con una referencia polimórfica
> `entidad_tipo` / `entidad_id` describe una referencia que **la base de datos no puede
> validar**: una fila puede apuntar a una tabla que no toca, o a un id que no existe, y nada lo
> impide. Es exactamente lo que
> [ADR-0006](<../../adr/0006-la-liga-entre-convocatoria-y-modulo.md>) descartó al elegir entre
> `RegistroConvocatoria` y el `RouterSolicitudes` de `EVT`.
>
> Con una feria por schema hay además un agravante concreto: un `ContentType` de Django dice
> `"app.modelo"`, y ese par significaría **una fila distinta en cada edición**.
>
> Lo construido son **columnas anulables con una restricción que exige exactamente una**:
> `editorial` y `solicitud` hoy, `movimiento` cuando exista la fase de pago. Cuesta una columna
> por destino y a cambio la integridad la sostiene PostgreSQL.

<!-- -->

> [!note] Dónde caen los archivos (2026-08-27)
> `archivo` es un `FileField` con `upload_to=CarpetaDeLaFeria("documentos")`, así que la ruta
> queda `feria_2027/documentos/<uuid>.pdf`: el aislamiento por feria llega también al disco, y
> el nombre original —que suele traer datos personales— no sobrevive en la ruta. Se conserva
> aparte, en `nombre_original`, para poder decirle a la persona cuál subió. Ver
> [ADR-0007](<../../adr/0007-los-archivos-empiezan-en-disco.md>).
>
> **Ningún documento se sirve por una URL.** La vista que los entrega comprobando quién pregunta
> está pendiente; hasta que exista, A2 los lista y no los deja descargar.

### 3.5 Stand
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| convocatoria_id | FK → `Convocatoria` (`FER`), con `tipo = STD`. **El mapa es de la convocatoria** (RN-19), no de la feria. |
| clave | Identificador del espacio (`IN-01`). Único dentro de su convocatoria. |
| etiqueta | Lo que se pinta dentro de la caja en el mapa (`Internacional 01`). |
| zona | Pabellón o sección (`Pabellón Internacional`). **Descriptiva: no fija precio** — ver la nota. |
| col, fila | Esquina superior izquierda, **en celdas** de la retícula (§3.13). |
| ancho_celdas, alto_celdas | Tamaño en celdas. Nulos en un stand de forma irregular. |
| rectangulos | Formas irregulares (L, T): lista de rectángulos en celdas cuya unión es el stand. Nulo en un stand rectangular, que usa los cuatro campos de arriba. |
| estado | `Disponible` / `Reservado` / `Ocupado` (RN-10). Son también los tres estados que viajan al componente de mapa (RN-20). |
| incluye | Descripción de lo que incluye (estructura, contactos, exhibidores, etc.). |

> [!important] `metros_cuadrados` es **derivado**, no una columna (2026-08-27)
> La superficie sale de la forma en la retícula y de `MapaShowfloor.metros_por_celda` (§3.13):
> para un stand rectangular, `ancho_celdas × alto_celdas × metros_por_celda²`; para uno
> irregular, la suma de sus rectángulos.
>
> Es el mismo criterio que retiró los snapshots de `ReservaStand` (§3.7): con la superficie
> almacenada **y** dibujada habría dos fuentes para la misma cifra, y el día que discreparan
> —alguien mueve un stand en el editor y no toca el número— el mapa y la factura dirían cosas
> distintas sin que nadie se entere. Lo que sí queda congelado es `Reserva.monto_total` (RN-01).
>
> **La contrapartida, que hay que tener presente al dibujar:** la retícula tiene que ser lo
> bastante fina para expresar las medidas reales. Un stand de 3 × 2.5 m no cabe en una retícula
> de un metro por celda; con `metros_por_celda = 0.5` sí.

<!-- -->

> [!note] `zona` no fija precio, y es deliberado
> Dentro de una convocatoria **todos los stands se cobran al mismo `costo_m2`** (RN-01), así que
> dos zonas del mismo mapa solo pueden diferir en precio por su tamaño. La `zona` sirve para
> agrupar, rotular y filtrar.
>
> Si el cliente quiere pabellones a precios por metro distintos, eso son **convocatorias
> distintas** —cada una con su mapa y su configuración—, que es exactamente el caso que la
> decisión del 2026-08-25 habilitó. El mapa de muestra `filey-map.json`, con cuatro precios por
> zona, describe cuatro convocatorias o un solo precio; no una convocatoria con cuatro tarifas.

<!-- -->

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
| monto_total | Suma de líneas, con los descuentos aplicados en secuencia (RN-06). Ver la nota: se congela frente al mapa y al precio, **no** frente a los descuentos. |
| monto_abonado | Derivado de movimientos validados. |
| monto_pendiente | Derivado (`monto_total − monto_abonado`). |

> [!important] `monto_total` se congela frente al precio, no frente a los descuentos
> Es una distinción que ningún documento hacía y que separa dos comportamientos opuestos:
>
> | Cambia… | ¿Se recalcula `monto_total`? |
> | --- | --- |
> | `costo_m2` de la convocatoria (CU-STD-034) | **No.** Lo cobrado no se mueve (RN-01). |
> | La forma o superficie de un stand (CU-STD-033) | **No.** Solo cambia el desglose (§3.7). |
> | Se consolida o vence el pronto pago (CU-STD-023) | **Sí**, inmediatamente. |
> | Se aplica o se retira un descuento especial (CU-STD-020) | **Sí**, inmediatamente. |
>
> Tiene sentido: un cambio de tarifa no debe alcanzar a quien ya aceptó un precio, pero un
> descuento **es** una modificación deliberada de lo que esa reserva cuesta. Por eso CU-STD-020
> recalcula en su paso 7 y vuelve a evaluar los umbrales del 50% y el 100% (RN-13, RN-14): bajar
> el total puede dejar una reserva pagada sin que entre un peso más.

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
| tipo | `pronto_pago` / `especial`. **El porcentaje no es del tipo**: el del pronto pago se configura por convocatoria y el del especial lo fija el administrador en cada caso (RN-04, RN-07). |
| porcentaje | Porcentaje aplicado, copiado al consolidarse. Se guarda **por fila**: es lo que permite reconstruir el desglose aunque después cambie la configuración. |
| motivo | Obligatorio para `especial`. |
| aplicado_por | FK → `Persona` (`REG`); nulo cuando lo aplica el sistema (pronto pago automático, CU-STD-023). |
| fecha | Fecha de solicitud. |

**Restricciones:**

- Único por (`reserva_id`, `tipo`) — **RN-05**: una reserva tiene como máximo un `pronto_pago` y
  como máximo un `especial`. Nunca más de dos filas.

> [!important] El tope vive en la base de datos, no en la vista
> Antes esto era una frase en la sección de relaciones ("máximo dos"), y una frase no impide
> nada: dos administradores aplicando un descuento especial a la vez, o CU-STD-023 corriendo dos
> veces sobre la misma reserva, insertaban dos filas del mismo tipo y el total salía mal. El
> segundo intento **falla en la escritura**; qué hacer con ese fallo lo decide cada caso de uso
> (RN-05).

<!-- -->

> [!important] Los dos tipos **se acumulan** (RN-06)
> Un `pronto_pago` y un `especial` conviven en la misma reserva y se aplican los dos. **No son
> excluyentes** — el resumen al pie de este documento decía "descuentos no acumulables" hasta el
> 2026-08-27 y era falso.
>
> Se aplican **en secuencia**, no sumando porcentajes: 10% y 15% dan un descuento efectivo del
> **23.5%**, no del 25%. Cualquier consulta que sume las dos filas para mostrar "el descuento
> total" da un número que no es el que se cobra.
>
> El orden no altera el total —la multiplicación es conmutativa— pero el desglose se presenta
> siempre con el pronto pago arriba, que es el que el expositor ya conocía al reservar.

<!-- -->

> [!question] Falta decidir si retirar un descuento borra la fila o la marca
> Hoy la entidad no tiene estado. Cambiar un especial exige borrar la fila o editarla, y el
> modelo no dice cuál; si se borra, la `Bitacora` es el único rastro. Ver §6.

### 3.10 Notificacion

> [!important] La tabla es de `STD`; el envío no (2026-08-27)
> Se separan dos cosas que se venían confundiendo:
>
> | | Quién | Dónde |
> | --- | --- | --- |
> | **El registro** de que se notificó algo | `STD` | Esta tabla, en el schema de la feria |
> | **El envío** del correo | `apps/notificaciones` | Capa compartida, ya construida |
>
> `STD` **no manda correos por su cuenta**: compone el contenido y se lo entrega a
> `apps/notificaciones`, igual que ya hace `REG` con el OTP. Todo el correo del proyecto sale por
> `django.core.mail`, y quién lo entrega lo decide un ajuste, no el dominio.
>
> Lo que sí es de `STD` es el registro: `referencia_tipo`/`referencia_id` apuntan a una
> `Solicitud` o a una `Reserva`, que viven en el schema de **esta** feria, y esa pareja de
> valores significaría otra cosa en otra edición. Por eso la tabla no puede estar en `public`.
>
> Es el mismo reparto que la bitácora (§3.12): el registro es del dominio, el mecanismo es
> compartido.

<!-- -->

> [!note] `estado` dice lo que contestó el envío, no lo que hizo el buzón
> `enviada` significa que el proveedor aceptó el mensaje; `fallida`, que no se pudo entregar.
> Que la persona lo lea, o que su servidor lo rebote horas después, queda fuera del alcance.


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
| descuento_pronto_pago | Porcentaje del pronto pago. **10% por omisión, configurable** (RN-04). |
| fecha_limite_pronto_pago | Fecha de corte del pronto pago. Es **una fecha de la convocatoria, igual para todos**, no un contador por reserva (RN-04): quien reserva tarde tiene menos días. |
| instrucciones_pago | Texto/datos bancarios (banco, cuenta, CLABE, sucursal, referencia). |
| ~~salon_showfloor~~ | **Movido a `MapaShowfloor.salon`** (§3.13) el 2026-08-27: es un dato del mapa, no de las condiciones económicas de la convocatoria. |

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

> [!important] Cada módulo tiene la suya — resuelto el 2026-08-27
> Hasta hoy esto era un tema abierto en tres documentos a la vez: `BitacoraFER`, esta `Bitacora`
> de `STD` y `BitacoraEVT` tienen la misma forma, y se venía diciendo que unificarlas "es lo
> razonable".
>
> **Se decide lo contrario: la bitácora se queda por módulo.** Lo que se registra son las
> acciones sensibles **de un dominio**, y esas no se parecen entre sí — validar un abono y
> mover la fecha de cierre de una convocatoria no comparten ni vocabulario ni quién las lee.
> Una tabla común obligaría a un `accion` que fuera la unión de todos los conjuntos cerrados, es
> decir, ninguno.
>
> Queda cerrado también el aviso que `FER` §6 dejaba escrito —*"lo urgente es que el cuarto
> dominio no añada la cuarta"*—: sí la añade, y a propósito.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| persona_id | FK → `Persona` (`REG`) — quién ejecutó la acción. |
| accion | Acción (validar abono, prorrogar, descuento especial, editar mapa, etc.). |
| entidad_tipo, entidad_id | Objeto afectado. |
| detalle | Datos del cambio. |
| fecha | Marca de tiempo. |

### 3.13 MapaShowfloor
> La retícula sobre la que se dibuja el showfloor de **una** convocatoria (RN-19). Una fila por
> convocatoria de stands: sin ella no hay mapa, y una convocatoria recién creada no lo tiene
> todavía (CU-STD-038 E2).

| Atributo | Descripción |
| --- | --- |
| convocatoria_id | FK → `Convocatoria` (`FER`), con `tipo = STD`. **Único**: un mapa por convocatoria. |
| columnas, filas | Tamaño de la retícula, en celdas. |
| metros_por_celda | Cuántos metros mide el lado de una celda. Es lo que convierte la forma dibujada en superficie real, y por tanto en precio (RN-01). |
| tamano_celda | Lado de la celda **en píxeles** al dibujar. Es presentación pura: no entra en ningún cálculo. |
| salon | Recinto donde se monta este showfloor. |

> [!note] `salon` se mueve aquí desde `ConfiguracionSistema`
> Estaba en §3.11 como `salon_showfloor`, heredado del `Evento.salon` de la v1.0. Es un dato del
> **mapa**, no de las condiciones económicas de la convocatoria, y ahora que el mapa es una
> entidad tiene dónde vivir. `ConfiguracionSistema` se queda con lo que es: precios, porcentajes,
> plazos y datos bancarios.

> [!important] Con esto el JSON del mapa se genera entero desde el modelo
> `MapaShowfloor` da la retícula, `Stand` da las formas y los estados, y `DecoracionMapa` el
> resto del recinto. No queda ningún dato del mapa fuera de la base: el archivo
> `filey-map.json` que usó el prototipo pasa a ser un **fixture de ejemplo**, no una fuente.

### 3.14 DecoracionMapa
> Lo que se dibuja en el mapa y **no** es un stand: escenarios, servicios, accesos, rótulos del
> recinto. No se reserva, no tiene precio y no participa en ninguna regla de negocio.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| mapa_id | FK → `MapaShowfloor`. |
| tipo | `rectangulo` (una superficie con color y rótulo) / `texto` (solo un rótulo). |
| col, fila | Posición en celdas. |
| ancho_celdas, alto_celdas | Tamaño en celdas. Nulos cuando `tipo = texto`. |
| color | Color de relleno. Nulo cuando `tipo = texto`. |
| etiqueta | Rótulo (`Escenario principal`, `Sanitarios`, `Acceso norte`). |

> [!note] Por qué es una entidad y no un campo JSON del mapa
> El administrador las edita desde el mismo editor que los stands (CU-STD-033), y un rótulo mal
> puesto se corrige tan a menudo como un stand. Guardarlas como un blob dentro de
> `MapaShowfloor` haría que cualquier corrección reescribiera el mapa entero.

---

## 4. Relaciones principales

- **Persona** (`REG`) 1—1 **Editorial** *dentro de una feria* (RN-21): una persona tiene una
  editorial en esta edición, y esa editorial es suya. Entre ediciones sí hay varias: la misma
  persona vuelve a llenar su ficha cada año, en el schema de cada feria.
- **Editorial** 1—N **SelloEditorial**.
- **RegistroConvocatoria** (`FER`) 1—N **Solicitud** (RN-22): es el enganche del dominio con su
  convocatoria (§3.3). De un registro cuelgan todas las solicitudes de esa persona a esa
  convocatoria a lo largo del tiempo, con **como mucho una viva** (`pendiente` o
  `cambios_solicitados`); tras un rechazo se puede volver a aplicar. Una misma persona puede
  tener además varios registros en la misma feria, si hay varias convocatorias de stands.
- **Convocatoria** (`FER`) 1—1 **ConfiguracionSistema**: una configuración por convocatoria de
  stands, no una por feria (§3.11).
- **Editorial** 1—N **Solicitud**: una viva **por convocatoria** (no por feria), con reenvío
  tras solicitud de cambios y solicitud nueva tras rechazo (RN-22).
- **Convocatoria** (`FER`) 1—1 **MapaShowfloor** 1—N **Stand** (RN-19): el mapa y sus espacios
  son de la convocatoria. `MapaShowfloor` 1—N **DecoracionMapa**.
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
| Stand | CU-STD-009, CU-STD-010, CU-STD-032, CU-STD-033, CU-STD-037, CU-STD-038 |
| MapaShowfloor / DecoracionMapa | CU-STD-009, CU-STD-032, CU-STD-033, CU-STD-037, CU-STD-038 |
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

### Resueltos el 2026-08-27

- ~~**`RN-05` y `RN-06` nunca se definieron.**~~ **Ocupados el 2026-08-27** con las dos reglas de
  descuentos que faltaban: el tope de uno por tipo (RN-05) y la acumulación en secuencia
  (RN-06). Nunca habían significado nada, así que ocuparlos no recicla ninguna cita.
- ~~**Los descuentos "no son acumulables".**~~ **Sí lo son** (RN-06): un pronto pago y un especial
  conviven, aplicándose en secuencia. La frase del resumen al pie era falsa y está corregida.

- ~~**¿En qué schema vive `Notificacion`?**~~ **Es tabla de `STD`**, en el schema de la feria;
  `apps/notificaciones` se ocupa solo del envío (§3.10). Desbloquea CU-STD-008.
- ~~**Falta el caso de uso de crear el mapa.**~~ **CU-STD-039**: se importa un JSON externo y el
  sistema lo traduce a filas, exclusivo del superusuario. El editor del componente y su
  `saveMap` quedan **fuera de alcance por ahora**.

- ~~**Confirmar si `Solicitud` guarda snapshot de datos o referencia a `Editorial`.**~~
  **Guarda snapshot** (RN-22, §3.3). Y de la misma decisión sale que tras un rechazo se puede
  volver a aplicar con la misma editorial, lo que convierte la relación con el registro en 1—N.
- ~~**Necesidad real de `Bitacora`.**~~ Se queda, **y una por módulo** (§3.12). Cierra también el
  aviso de `FER` §6 sobre no añadir una cuarta.
- ~~**Un mapa por feria o por convocatoria.**~~ **Por convocatoria** (RN-19). `Stand` gana
  `convocatoria_id` y aparecen `MapaShowfloor` (§3.13) y `DecoracionMapa` (§3.14).
- ~~**El modelo no podía generar el JSON del mapa.**~~ Ya puede: retícula, forma en celdas,
  formas irregulares y zona están en el modelo (§3.5, §3.13).
- ~~**Los estados del stand no coincidían con los del componente de mapa.**~~ Se igualan a los
  del dominio; el componente se ajusta (RN-20).
- ~~**Los cuatro precios por zona del mapa de muestra.**~~ El modelo de precio se queda como
  está: `m² × costo_m2` por convocatoria. La zona **no** fija precio; pabellones a tarifas
  distintas son convocatorias distintas (nota de §3.5).

### Abiertos — necesitan decisión

- **Homologar el nombre de `ConfiguracionSistema`** con el `ParametrosConvocatoria` de `EVT`.
  Siguen siendo la misma figura con dos nombres, y el de `STD` sigue diciendo "Sistema", que es
  justo lo que no es. El nombre que lo diría bien es `ConfiguracionConvocatoria`.
- **Qué pasa al retirar un descuento.** La restricción única de §3.9 impide dos del mismo tipo,
  pero `DescuentoAplicado` no tiene estado: cambiar un descuento especial exige borrar la fila o
  editarla, y hoy el modelo no dice cuál. Si se borra, la `Bitacora` es el único rastro.
- **Reconstruir el desglose de una reserva vieja.** Sin los snapshots de `ReservaStand` (§3.7),
  el desglose por línea se recalcula con los valores actuales. Falta decidir si eso basta o si
  CU-STD-029 necesita mostrarlo tal como se aceptó — en cuyo caso la fuente es la `Bitacora`.
- **`es_recurrente`**: exige una tabla de participación histórica en la capa global. Misma deuda
  que `REG` §5, `EVT` §5 y `FER` §6; cuando se implemente, se implementa una vez para los cuatro.
- **Correo de contacto duplicado**: `Editorial.correo_electronico` convive con `Persona.correo`.
  Se conservan ambos a propósito (§3.1); confirmar con el cliente que el segundo no debe
  prellenarse desde el primero.

### En curso

- **Los casos de uso de `STD` decían "la convocatoria" en singular.** Se escribieron cuando había
  una sola convocatoria de stands por feria. La revisión está en marcha: CU-STD-001, 002, 004,
  009, 010, 011, 012 y 034 son los afectados, y cada mención tiene que decir **cuál**.

---

## Reglas de negocio relacionadas

Las reglas RN-01 a RN-17 que rigen estos datos (cálculo por m², anticipo del 50% con
descuento, plazo de 30 días, descuentos acumulables en secuencia, estados de stand y reserva, etc.)
están documentadas en los requisitos del dominio y en el inventario de casos de uso
(`CU-STD Índice.md`).
