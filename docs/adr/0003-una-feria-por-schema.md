---
estado: aceptada
version: "1.0"
tags:
  - tipo/adr
  - dom/fer
  - tema/arquitectura
fecha: 2026-08-21
fecha_actualizacion: 2026-08-21
id: ADR-0003
responsable: Hugo Janssen
supersede:
reemplazado_por:
---
# ADR-0003. Aislar cada feria en su propio schema de PostgreSQL, con Django resolviendo la feria en cada petición

## Estado

`Aceptado` — 2026-08-21.

## Contexto

FILEY no es un sistema de una sola feria. Cada edición (FILEY 2026, FILEY 2027, …) abre sus
propias convocatorias de eventos, stands, talleres y visitas escolares, con sus propios
parámetros, sus propias propuestas y su propio programa. Hasta hoy el sistema se ha construido
como si solo existiera una, y eso ya produjo **tres modelos de datos que se contradicen entre
sí**:

| Dominio | Cómo asume hoy la edición |
| --- | --- |
| `EVT` (v3.0, 2026-08-20) | **Instancia propia por edición.** `ParametrosConvocatoria` es "una tabla de una sola fila: cada edición de la feria vive en su propia instancia de base de datos, de modo que la edición es implícita y ninguna tabla del modelo guarda un identificador de edición". |
| `TAL` | **Tabla compartida con discriminador.** Cuatro tablas llevan `edicion_id` como FK a `EdicionFeria`, una de ellas dentro de su clave primaria compuesta. |
| `STD` | Una entidad `Evento` = "edición de la feria", referenciada por el resto del dominio. |

Los tres no pueden ser ciertos a la vez. Y la decisión no se puede seguir posponiendo, porque
`EVT` es el dominio que se construye a continuación y su modelo ya está escrito sobre una de
las tres respuestas.

Además hay una restricción que no es negociable y que ya está resuelta en el modelo de `REG`:
**la cuenta de una persona no pertenece a ninguna feria.** Alguien que expuso en FILEY 2026 y
propone una actividad en FILEY 2027 es la misma `Persona`, con el mismo correo, y el correo es
único en todo el sistema (ver
[`Modelo de datos - Registros`](<../requisitos/REG/Modelo de datos - Registros.md>), §5). La
identidad es global; lo que se separa por feria es el **contenido**.

Fuerzas a considerar:

- **Aislamiento real de los datos.** Una consulta mal escrita en el panel de FILEY 2027 no
  debe poder devolver, contar ni modificar propuestas de FILEY 2026. Es el daño más caro y más
  difícil de detectar: no falla, simplemente devuelve datos de más.
- **El modelo ya escrito de `EVT`.** Rehacerlo para meterle un `edicion_id` en cada tabla es
  trabajo real y toca todas sus consultas.
- **El volumen.** Una feria al año, con miles de propuestas por edición. No es un SaaS con
  diez mil inquilinos: son unidades pocas, grandes y de vida larga.
- **Archivar una edición terminada** debe ser barato y seguro: una edición cerrada no debería
  seguir compitiendo por índices ni apareciendo por accidente en las consultas de la vigente.
- **Django asistido por agentes de IA.** Cuanto menos dependa el aislamiento de que cada
  consulta futura *recuerde* filtrar, mejor: la regla que se cumple sola es la que sobrevive.

## Opciones consideradas

### Opción A: un schema de PostgreSQL por feria, resuelto por petición

Un schema `public` con lo global (identidad, registro de ferias, membresías administrativas) y
un schema por feria (`feria_2027`, `feria_2028`, …) con las tablas de los dominios de
contenido. En cada petición, Django resuelve a qué feria se está accediendo y fija el
`search_path` de la conexión a ese schema.

- **A favor:**
  - **El aislamiento no depende de acordarse de filtrar.** Una consulta sin `WHERE feria_id`
    —el error más fácil de cometer y el más difícil de ver— simplemente no puede alcanzar los
    datos de otra feria: no están en el schema en el que la conexión está mirando.
  - **El modelo de `EVT` ya escrito queda válido tal cual**, incluida su afirmación de que
    ninguna tabla guarda identificador de edición.
  - Los modelos de Django no llevan `feria_id` en ninguna tabla de dominio, ni las consultas
    un filtro extra: menos ruido en todo el código de los cuatro dominios que faltan.
  - Archivar una edición es aislar (o volcar y soltar) **un schema**, no depurar filas
    repartidas por veinte tablas.
  - Es una sola base de datos: una conexión, un `DATABASE_URL`, un respaldo. No multiplica la
    infraestructura como sí haría una base por feria.
- **En contra:**
  - Las migraciones hay que **aplicarlas a cada schema**, no una sola vez. Con una feria al
    año es poco, pero es un paso que no se puede olvidar y que hay que automatizar.
  - Django no trae multi-tenancy de fábrica: el "policía de tránsito" (resolver la feria y
    fijar el `search_path`) es código propio, y **un fallo suyo es grave** — dejar el
    `search_path` de una conexión reutilizada apuntando a la feria anterior serviría datos
    cruzados.
  - Una consulta que necesite **cruzar** ferias (¿en cuántas ediciones participó esta
    persona?) deja de ser un `JOIN` y pasa a ser una consulta por schema.
  - Atarse a PostgreSQL. Hoy el desarrollo usa SQLite, que no tiene schemas: los entornos
    dejan de ser equivalentes.

### Opción B: tablas compartidas con una columna `feria_id`

Todas las ferias en las mismas tablas, discriminadas por una columna, como hace hoy `TAL`.

- **A favor:**
  - Lo más simple de operar: un solo juego de tablas, una sola migración, y las consultas que
    cruzan ediciones son un `JOIN` normal.
  - Funciona igual en SQLite y en PostgreSQL: desarrollo y producción no divergen.
- **En contra:**
  - **El aislamiento pasa a depender de que cada consulta recuerde filtrar.** Basta un
    `Propuesta.objects.filter(estado="aceptada")` sin la feria para mezclar ediciones, y el
    resultado *parece* correcto. Es precisamente el error que este proyecto no puede permitirse
    detectar tarde.
  - Obliga a rehacer el modelo de `EVT` ya escrito, metiendo `feria_id` en cada tabla y en cada
    consulta de los cuatro dominios.
  - Archivar una edición terminada no libera nada: sus filas siguen en las mismas tablas e
    índices que la edición viva.
  - Se puede mitigar con un manager por defecto que filtre siempre, pero eso es reconstruir a
    mano —y de forma evadible— la garantía que un schema da por construcción.

### Opción C: una base de datos por feria

- **A favor:** el aislamiento más fuerte posible; una edición se respalda o se borra entera.
- **En contra:** multiplica la infraestructura (una `DATABASE_URL`, un respaldo y una cuota por
  feria) y complica el despliegue en Render/Supabase sin comprar nada a cambio que el schema no
  dé ya. Para una feria al año es desproporcionado.

## Decisión

**Cada feria vive en su propio schema de PostgreSQL, y Django resuelve en cada petición a qué
feria se está accediendo y fija el `search_path` de la conexión a ese schema.** Lo global
—identidad de las personas, registro de ferias y membresías administrativas— vive en `public`;
el contenido de cada edición —convocatorias, propuestas, actividades, stands, visitas,
programa— vive en el schema de su feria.

Concretamente:

| Vive en `public` (global, una sola copia) | Vive en `feria_<slug>` (una copia por feria) |
| --- | --- |
| `Persona` — la cuenta, con su correo único | Convocatorias y sus parámetros (`EVT`, `TAL`, `STD`, `VIS`) |
| `SesionOTP` — el acceso es al sistema, no a una feria | Propuestas, solicitudes y actividades |
| `Feria` — el registro de ediciones | Stands, reservas, abonos |
| `AdminFeria` — quién administra qué feria (ADR-0004) | Visitas escolares e itinerarios |
| | Programa, salas y bloques de horario (`PRG`, `SAL`) |

La feria se identifica en la **URL**, con un prefijo por feria (`/f/<slug>/…`). Es explícita,
se puede compartir como enlace, y no exige configurar DNS ni certificados por edición como sí
haría un subdominio. El subdominio queda como evolución posible, no como requisito.

El "policía de tránsito" es un **middleware**: resuelve la feria del prefijo de la URL,
comprueba que quien pide tiene acceso a esa feria (ADR-0004), fija el `search_path` de la
conexión y —esto es lo que no se puede olvidar— **lo restaura al terminar la petición**, porque
las conexiones se reutilizan entre peticiones y una conexión que se queda apuntando a la feria
anterior serviría datos cruzados.

## Consecuencias

**Positivas**

- El error más caro y silencioso posible en este sistema —servir o contar datos de otra
  edición— deja de depender de que cada consulta recuerde filtrar.
- El modelo de datos de `EVT` (v3.0) queda validado tal como está escrito, sin rehacerlo.
- Los tres modelos que hoy se contradicen quedan homologados en una sola respuesta.
- Ninguna tabla de dominio lleva `feria_id`, ni ninguna consulta un filtro extra: los cuatro
  dominios pendientes se escriben sin esa carga.
- Archivar una edición cerrada es una operación sobre un schema.

**Negativas / riesgos aceptados**

- **El middleware es un punto único de fallo.** Si no restaura el `search_path`, o si una
  tarea en segundo plano corre sin fijarlo, se sirven datos de la feria equivocada sin ningún
  error visible. Exige pruebas que verifiquen explícitamente el aislamiento, incluida la
  reutilización de conexiones y los hilos que no nacen de una petición HTTP (hoy existe uno: el
  envío de correo del OTP).
- **Las migraciones se aplican por schema.** Hay que automatizarlo en el arranque/despliegue;
  olvidar un schema deja una feria con un esquema viejo.
- **Se adopta PostgreSQL también en desarrollo.** SQLite no tiene schemas, así que dejaría de
  poder ejercitarse la parte del sistema que hace el aislamiento — justo la que más falta
  probar. Esto convierte en obligatorio algo que hasta hoy era opcional (ver `docker-compose.yml`).
- Las consultas que crucen ediciones (historial de participación de una persona, que el modelo
  de `REG` ya anticipa como deuda con `es_recurrente`) hay que resolverlas recorriendo schemas
  o con una tabla global explícita en `public`. No se resuelven con un `JOIN`.
- Cada feria nueva es una operación de infraestructura (crear schema + migrar), no una fila
  insertada.

**Qué queda descartado por esta decisión**

- La columna `edicion_id` de `TAL` y la entidad `Evento` de `STD` como mecanismo de separación
  por edición: ambos modelos hay que corregirlos para alinearlos con esta decisión.
- Añadir `feria_id` a cualquier tabla de dominio nueva.
- Que una consulta de dominio reciba la feria como parámetro: la feria es contexto de la
  conexión, no argumento de la consulta.

## Referencias

- [ADR-0001](<0001-arquitectura-monolito-vs-separado.md>) — el monolito Django dentro del cual
  vive este middleware.
- [ADR-0004](<0004-acceso-administrativo-por-feria.md>) — quién puede entrar a cada feria; es
  la comprobación que el middleware ejecuta antes de fijar el `search_path`.
- [`FER/Modelo de datos - Ferias`](<../requisitos/FER/Modelo de datos - Ferias.md>) — las
  entidades `Feria` y `AdminFeria` que esta decisión coloca en `public`.
- [`EVT/Modelo de datos - Eventos`](<../requisitos/EVT/Modelo de datos - Eventos.md>) §3.6 — la
  suposición de "una instancia por edición" que esta decisión confirma.
- [`Modelo de datos - Registros`](<../requisitos/REG/Modelo de datos - Registros.md>) §5 — la
  decisión previa de que las personas se comparten entre ferias.
