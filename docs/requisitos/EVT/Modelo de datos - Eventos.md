---
estado: propuesta
version: "4.0"
tags:
  - tipo/modelo-de-datos
  - dom/evt
fecha: 2026-06-23
fecha_actualizacion: 2026-08-25
---
# Modelo de datos — Eventos generales (EVT)

Modelo conceptual del dominio de Eventos Generales: qué información almacena el sistema
para registrar, dictaminar y programar las actividades del programa de FILEY.

El desarrollo se divide en **dos etapas**, y el modelo está organizado igual:

1. **Captura** (§2) — el aplicante llena y envía su solicitud. Se implementa primero, para
   contar con una base de datos poblada sobre la cual construir lo demás.
2. **Administración y programación** (§3) — el administrador dictamina las solicitudes
   (aceptar, rechazar o solicitar cambios) y programa las aceptadas.

La separación no es solo cronológica: **cada tabla pertenece a una sola etapa según quién la
escribe**. Las de §2 las escribe el aplicante; las de §3, únicamente el administrador. Ningún
dato queda en ambos lados.

---

## 1. Arquitectura y patrón de enrutamiento

### Entidades principales

| Entidad | Propósito |
| --- | --- |
| Persona (`REG`) | La persona registrada en el sistema. Existe con independencia de cualquier convocatoria y se reutiliza en todas. |
| Solicitud (EVT) | Una solicitud concreta enviada por una persona a esta convocatoria. Contiene los datos comunes a cualquier tipo de actividad. |
| Actividad específica (EVT) | Los datos propios del tipo de actividad elegido. Existen ocho variantes, una por tipo. |

### Elementos de asociación y enrutamiento

Tres tablas intermedias resuelven las relaciones. Ninguna guarda datos de negocio: solo
conectan entidades y, cuando hace falta, indican **a qué tabla** apunta la conexión. Todas son
polimórficas y las alimentan dos catálogos —uno por router, salvo el de documentos, que
**reutiliza el mismo catálogo que el de actividades** en vez de tener uno propio, porque enruta
contra el mismo conjunto de ocho tablas.

| Tabla | Propósito |
| --- | --- |
| Router de solicitudes | Relaciona a la persona con las solicitudes que ha creado. Su discriminador, `convocatoria_id`, es una FK a `CatalogoConvocatorias` (§2.2); la fila referida trae el `prefijo` (`EVT`, `TAL`, `STD` o `VIS`) con el que se resuelve a qué tabla pertenece la solicitud. Es único para todo el sistema: sirve a los cuatro dominios. |
| Router de actividades | Relaciona una solicitud con su actividad específica. Su discriminador, `tipo_actividad_id`, es una FK a `CatalogoActividades` (§2.5); la fila referida trae el `nombre` con el que se resuelve cuál de las ocho tablas la contiene. |
| Router de documentos | Relaciona los archivos adjuntos con la actividad específica que los requiere. Comparte discriminador con el router de actividades —`tipo_actividad_id`, FK al mismo `CatalogoActividades`— y resuelve contra la misma tabla `Actividad_*`. Hoy solo hay filas para presentación de libro y revista, pero el esquema no limita a esas dos: cualquier tipo de actividad que llegue a necesitar un archivo usa el mismo mecanismo sin cambiar la tabla. |

Visualmente:

```mermaid
flowchart TD
    U[Persona<br/>registro global del sistema]

    CC[(CatalogoConvocatorias<br/>prefijo: EVT/TAL/STD/VIS)]
    DD[(DetallesConvocatoria)]
    RS{{Router de solicitudes<br/>discriminador: convocatoria_id}}

    S_EVT[Solicitudes EVT]
    S_TAL[Solicitudes TAL]
    S_STD[Solicitudes STD]
    S_VIS[Solicitudes VIS]

    CA[(CatalogoActividades<br/>8 tipos)]
    RA{{Router de actividades<br/>discriminador: tipo_actividad_id}}
    RD{{Router de documentos<br/>discriminador: tipo_actividad_id}}

    A_1[Actividad tipo 1]
    A_2[Actividad tipo 2]
    A_n[Actividad tipo N]

    U --> RS
    CC --> RS
    CC -.-> DD
    RS --> S_EVT
    RS --> S_TAL
    RS --> S_STD
    RS --> S_VIS

    S_EVT --> RA
    CA --> RA
    CA --> RD

    RA -.->|solo una| A_1
    RA -.-> A_2
    RA -.-> A_n

    RD -.->|si requiere archivos| A_1

    style S_EVT fill:#2C4C8C , stroke:#01457C
```

### Referencias polimórficas

Los tres routers comparten un mecanismo: guardan un **discriminador** que nombra la tabla
destino y un **identificador** de la fila dentro de esa tabla. El discriminador vive **en la
fila del router**, no en el catálogo: ya no es un string suelto, sino una FK (`convocatoria_id`,
`tipo_actividad_id`) hacia una tabla de catálogo. El catálogo referido no es el discriminador
—es el que la aplicación consulta, ya siguió la FK, para resolver a qué tabla apunta—, a través
de un campo propio de esa fila: `prefijo` en `CatalogoConvocatorias`, `nombre` en
`CatalogoActividades`. Agregar una convocatoria o un tipo de actividad es entonces dar de alta
una fila de catálogo, no tocar un `enum` en código.

`RouterActividades` y `RouterDocumentos` (§2.6, §2.8) van un paso más allá: **comparten el
mismo catálogo**. No hay un `CatalogoDocumentos` aparte —sería un catálogo con el mismo
contenido que `CatalogoActividades`, solo que vacío en seis de sus ocho filas—; ambos routers
discriminan contra `CatalogoActividades` y resuelven a la misma familia de tablas `Actividad_*`.
Lo único que distingue su alcance es de negocio, no de esquema: hoy únicamente presentación de
libro y revista requieren archivos, pero cualquier tipo nuevo que los necesite usa el mecanismo
que ya existe.

| Router | Discriminador (en el router) | Se resuelve con | Identificador | Destinos posibles |
| --- | --- | --- | --- | --- |
| `RouterSolicitudes` | `convocatoria_id` (FK) | `CatalogoConvocatorias.prefijo` | `solicitud_id` | `Solicitudes_EVT`, `Solicitudes_TAL`, `Solicitudes_STD`, `Solicitudes_VIS` |
| `RouterActividades` | `tipo_actividad_id` (FK) | `CatalogoActividades.nombre` | `detalle_id` | Las ocho tablas `Actividad_*` |
| `RouterDocumentos` | `tipo_actividad_id` (FK) | `CatalogoActividades.nombre` | `detalle_id` | Las ocho tablas `Actividad_*` (en la práctica, solo hay filas para `Actividad_PresentacionLibro` y `Actividad_PresentacionRevista`) |

Como el identificador puede apuntar a tablas distintas según el discriminador, **no es una
clave foránea con restricción**: la base de datos no puede validarlo. La integridad depende de
la capa de aplicación, y conviene resguardarla con pruebas o con el mecanismo de relaciones
genéricas que ofrezca el ORM. A cambio, el patrón permite agregar convocatorias o tipos de
actividad sin modificar las tablas existentes.

> `CatalogoConvocatorias.prefijo` no aparece en la lista de atributos que definió el pedido
> original —solo `nombre_convocatoria`, las fechas y `esta_activa`—; se añade aquí porque el
> router necesita resolver a `EVT`/`TAL`/`STD`/`VIS` desde algún campo estable, y
> `nombre_convocatoria` es texto editable por el administrador (pensado para mostrarse, no para
> enrutar). Se nombra `prefijo` y no `dominio` porque `EVT`/`TAL`/`STD`/`VIS` ya funciona como
> prefijo literal en el resto del sistema —nombres de tabla (`Solicitudes_EVT`,
> `Actividad_*`), IDs de caso de uso (`CU-EVT-*`), tags (`dom/evt`)—, mientras que "dominio" es
> el término de arquitectura que ya usa este documento para el concepto, no el nombre de un
> campo. Revisar si esta inferencia es correcta.

---

## 2. Etapa 1 — Captura de solicitudes

```mermaid
erDiagram
    Persona {
        bigint id PK
        string nombres
        string apellidos
        string correo
        string celular
        string pais
        string estado_pais
        string ciudad
    }

    CatalogoConvocatorias {
        bigint id PK
        string nombre_convocatoria
        string prefijo
        date fecha_apertura
        date fecha_cierre
        boolean esta_activa
    }

    DetallesConvocatoria {
        bigint id PK
        bigint convocatoria_id FK
    }

    RouterSolicitudes {
        bigint id PK
        bigint usuario_django FK
        bigint convocatoria_id FK "DISCRIMINADOR"
        bigint solicitud_id FK "REFERENCIA POLIMORFICA"
    }

    Solicitudes_EVT {
        bigint id PK
        string institucion
        string cargo
        string titulo_actividad
        string nombre_moderador
        string nombre_organizador_organizacion
        string publico_objetivo
        string sinopsis
        boolean es_uady
        boolean requiere_constancia
        string comentarios
        timestamp fecha_de_solicitud
    }

    CatalogoActividades {
        bigint id PK
        string nombre
    }

    RouterActividades {
        bigint id PK
        bigint solicitud_id FK
        bigint tipo_actividad_id FK "DISCRIMINADOR"
        bigint detalle_id FK "REFERENCIA POLIMORFICA"
    }

    RouterDocumentos {
        bigint id PK
        bigint tipo_actividad_id FK "DISCRIMINADOR"
        bigint detalle_id FK "REFERENCIA POLIMORFICA"
        string tipo_documento
        string storage_key
    }

    Actividad_Conversatorio {
        bigint id PK
        string nombre_participante_1
        string semblanza_participante_1
        string nombre_participante_2
        string semblanza_participante_2
        string nombre_participante_3
        string semblanza_participante_3
    }

    Actividad_Conferencia {
        bigint id PK
        string nombre_participante_1
        string semblanza_participante_1
        string nombre_participante_2
        string semblanza_participante_2
    }

    Actividad_Charla {
        bigint id PK
        string nombre_participante_1
        string semblanza_participante_1
        string nombre_participante_2
        string semblanza_participante_2
    }

    Actividad_MesaRedonda {
        bigint id PK
        string nombre_participante_1
        string semblanza_participante_1
        string nombre_participante_2
        string semblanza_participante_2
        string nombre_participante_3
        string semblanza_participante_3
    }

    Actividad_PresentacionLibro {
        bigint id PK
        string titulo_publicacion
        string tipo_presentador
        string nombre_autor_1
        string semblanza_autor_1
        string nombre_autor_2
        string semblanza_autor_2
        string nombre_autor_3
        string semblanza_autor_3
        string nombre_autor_4
        string semblanza_autor_4
        string nombre_autor_5
        string semblanza_autor_5
        boolean autor_participa
        string nombres_de_autores_presentes
        string nombre_participante_1
        string semblanza_participante_1
        string nombre_participante_2
        string semblanza_participante_2
        string nombre_editorial
    }

    Actividad_PresentacionRevista {
        bigint id PK
        string titulo_publicacion
        string tipo_presentador
        string nombre_editor_1
        string semblanza_editor_1
        string nombre_editor_2
        string semblanza_editor_2
        boolean editor_participa
        string nombres_de_editores_presentes
        string nombre_participante_1
        string semblanza_participante_1
        string nombre_participante_2
        string semblanza_participante_2
        string nombre_editorial
    }

    Actividad_LecturaObra {
        bigint id PK
        string nombre_participante_1
        string semblanza_participante_1
        string nombre_participante_2
        string semblanza_participante_2
    }

    Actividad_Encuentro {
        bigint id PK
        string nombre_participante_1
        string semblanza_participante_1
        string nombre_participante_2
        string semblanza_participante_2
    }


    Persona ||--o{ RouterSolicitudes : "tiene"
    CatalogoConvocatorias ||--o{ RouterSolicitudes : "clasifica"
    CatalogoConvocatorias ||--|| DetallesConvocatoria : "detalla"

    RouterSolicitudes }o--|| Solicitudes_EVT : "enruta"

    Solicitudes_EVT ||--o{ RouterActividades : "contiene"

    CatalogoActividades ||--o{ RouterActividades : "clasifica"
    CatalogoActividades ||--o{ RouterDocumentos : "clasifica"

    RouterActividades }o..|| Actividad_Conversatorio : "enruta"
    RouterActividades }o..|| Actividad_Conferencia : "enruta"
    RouterActividades }o..|| Actividad_Charla : "enruta"
    RouterActividades }o..|| Actividad_MesaRedonda : "enruta"
    RouterActividades }o..|| Actividad_PresentacionLibro : "enruta"
    RouterActividades }o..|| Actividad_PresentacionRevista : "enruta"
    RouterActividades }o..|| Actividad_LecturaObra : "enruta"
    RouterActividades }o..|| Actividad_Encuentro : "enruta"

    RouterDocumentos }o..|| Actividad_PresentacionLibro : "adjunta"
    RouterDocumentos }o..|| Actividad_PresentacionRevista : "adjunta"
```

### 2.1 Persona

Entidad del core de Registros (`REG`); se referencia aquí, no se define. Su detalle completo
—incluido el acceso por código de un solo uso— está en
[`REG/Modelo de datos - Registros.md`](<../REG/Modelo%20de%20datos%20-%20Registros.md>).

Guarda la identidad y la **procedencia geográfica** (`pais`, `estado_pais`, `ciudad`), que son
datos de perfil: se capturan una vez y se reutilizan en cualquier convocatoria. La institución
y el cargo, en cambio, se capturan por solicitud (§2.4), porque una misma persona puede aplicar
representando a instituciones distintas.

Al no existir copia de la procedencia dentro de la solicitud, el modelo refleja siempre el
valor vigente del perfil, no el que tenía la persona al enviar.

> El formulario del prototipo captura "Ciudad / Estado" en un solo campo de texto; al portarlo
> habrá que dividirlo en los tres campos que define esta entidad.

### 2.2 CatalogoConvocatorias

Catálogo del que cuelgan todas las convocatorias del sistema —una por dominio (`EVT`, `TAL`,
`STD`, `VIS`), y potencialmente varias por dominio si en el futuro conviven ediciones—. Es la
tabla que referencia `RouterSolicitudes.convocatoria_id` (§2.3): el discriminador vive en esa
FK del router, no aquí; esta tabla es la que la aplicación consulta, una vez seguida la FK, para
saber a qué dominio pertenece la solicitud y si la convocatoria sigue aceptando envíos.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| nombre_convocatoria | Nombre visible de la convocatoria (p. ej. "Convocatoria FILEY 2027 — Eventos generales"). Editable por el administrador; no participa en el enrutamiento. |
| prefijo | `EVT`, `TAL`, `STD` o `VIS`. El campo que resuelve a qué tabla de solicitudes apunta `RouterSolicitudes.solicitud_id` una vez seguida la FK (§1). No forma parte del pedido original de campos; se agrega porque el enrutamiento necesita un valor estable, distinto del nombre editable. Se llama `prefijo` y no `dominio` porque así es como `EVT`/`TAL`/`STD`/`VIS` ya se usa en el resto del sistema (nombres de tabla, IDs de caso de uso, tags) — "dominio" queda para el concepto de arquitectura, no para el nombre del campo. |
| fecha_apertura | Fecha en que la convocatoria empieza a aceptar solicitudes. |
| fecha_cierre | Fecha en que deja de aceptarlas. |
| esta_activa | Permite pausar la convocatoria en una emergencia sin tocar `fecha_cierre`: con `esta_activa = false`, aunque la fecha actual esté dentro del rango, no se aceptan envíos. |

Los parámetros que no son comunes a cualquier convocatoria —cupos, prefijo de folio, fechas de
notificación, etc.— no viven aquí: cada dominio los define en su propia tabla de detalle
(`detalles` en el diagrama de §1), enlazada uno a uno por `convocatoria_id`. Para `EVT` esa
tabla es `DetallesConvocatoria` (§3.6); el diagrama de esta etapa la muestra como referencia
mínima —su definición completa vive en la etapa 2, porque es el administrador quien la escribe.

### 2.3 RouterSolicitudes

Único vínculo entre una persona y sus solicitudes: `Solicitudes_EVT` no tiene clave foránea
hacia `Persona`. Sin una fila aquí, la solicitud no tiene dueño conocido, por lo que su
creación es obligatoria al enviar.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| usuario_django | FK → Persona. Conserva el nombre `usuario_django` porque referencia la tabla de usuarios del framework. |
| convocatoria_id | Discriminador. FK → CatalogoConvocatorias (§2.2); su campo `prefijo` determina a qué tabla apunta `solicitud_id`. |
| solicitud_id | Referencia polimórfica a la solicitud, en la tabla que indique `CatalogoConvocatorias.prefijo` (§1). |

### 2.4 Solicitudes_EVT

Los datos que el aplicante captura y que son **comunes a los ocho tipos de actividad**. Lo que
varía entre tipos vive en las tablas `Actividad_*` (§2.7); lo que decide el administrador vive
en la etapa 2 (§3).

| Atributo | Descripción |
| --- | --- |
| id | Identificador único, `bigint`. Es la base del folio: el folio visible **no se almacena**, se compone como `{prefijo_folio}-{id}` con el prefijo de `DetallesConvocatoria` (§3.6). |
| institucion | Dependencia o institución que representa. Obligatorio. |
| cargo | Cargo dentro de esa institución. Opcional. |
| titulo_actividad | Título de la actividad tal como lo propone el aplicante. Si el administrador lo modifica tras la revisión, el valor definitivo queda en `DetallesAdminSolicitud.titulo_final` (§3.1). |
| nombre_moderador | Moderador de la actividad. Opcional, uno como máximo. |
| nombre_organizador_organizacion | Persona u organización que organiza. Obligatorio. |
| publico_objetivo | Público al que va dirigida. Lista de valores separados sobre el conjunto cerrado `publico_general`, `academico`, `estudiantil`, `infantil`, `familias`; al menos uno. Al no estar normalizado, filtrar por público exige recorrer el texto. |
| sinopsis | Sinopsis de la actividad, capturada como texto. Antes era un PDF adjunto marcado por `tiene_sinopsis`; ahora el aplicante escribe el contenido directamente y no hay archivo que administrar. |
| es_uady | Indica si el aplicante se declara parte de la UADY. Es la autodeclaración en la captura; el administrador la valida (o la corrige) en `DetallesAdminSolicitud.is_participante_uady` (§3.1), que es el valor que cuenta para el conteo por categoría de `DetallesConvocatoria` (§3.6). |
| requiere_constancia | Indica si el aplicante solicita constancia de participación. Precondición de CU-EVT-005 (descargar constancia); antes no existía en el modelo (§5). |
| comentarios | Observaciones libres del aplicante. Opcional. |
| fecha_de_solicitud | Marca de tiempo del momento en que la solicitud se envía y se guarda. |

Las semblanzas ya no viven aquí como un booleano único: son un campo de texto por cada
participante, y por eso se definen junto a cada `nombre_participante_*` en las tablas
`Actividad_*` (§2.7) —una persona, una semblanza—.

### 2.5 CatalogoActividades

Catálogo de los ocho tipos de actividad. Antes `RouterActividades.tipo_actividad` guardaba el
valor de texto directamente; ahora ese campo es una FK hacia aquí, y esta tabla es la que la
aplicación consulta, una vez seguida la FK, para saber a qué tabla `Actividad_*` corresponde.
`RouterDocumentos` (§2.8) reutiliza este mismo catálogo como su propio discriminador —no tiene
uno aparte—, porque enruta contra la misma familia de tablas.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| nombre | `conversatorio`, `conferencia`, `charla`, `mesa_redonda`, `presentacion_libro`, `presentacion_revista`, `lectura_obra` o `encuentro`. El campo que resuelve a qué tabla `Actividad_*` apunta `RouterActividades.detalle_id` una vez seguida la FK (§1). |

Ocho filas fijas, una por tipo. Mover el valor a una tabla no cambia el conjunto cerrado de
tipos —siguen siendo ocho—, pero permite listarlos, ordenarlos o describirlos para la interfaz
sin tocar código.

### 2.6 RouterActividades

Conecta la solicitud con su actividad específica y determina de qué tipo es. Una fila por
solicitud.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| solicitud_id | FK → Solicitudes_EVT. |
| tipo_actividad_id | Discriminador. FK → CatalogoActividades (§2.5); su campo `nombre` determina a qué tabla `Actividad_*` apunta `detalle_id`. |
| detalle_id | Referencia polimórfica a la fila de la tabla `Actividad_*` que corresponda (§1). |

### 2.7 Tablas `Actividad_*`

Ocho tablas, una por tipo de actividad. Contienen únicamente lo que distingue a ese tipo: los
campos que comparten los ocho ya viven en `Solicitudes_EVT` (§2.4).

Hoy varios tipos coinciden en su estructura —Conversatorio y Mesa redonda por un lado;
Conferencia, Charla, Lectura de obra y Encuentro por otro—, pero se mantienen separados a
propósito. Cada tipo corresponde a un formulario distinto, y tener su propia tabla permite que
evolucione sin arrastrar a los demás; agruparlos por coincidencia actual cerraría esa puerta.

Cada nombre de participante va acompañado de su propia `semblanza_*`: un campo de texto libre,
capturado por el aplicante junto con el nombre. Ya no hay un booleano `tiene_semblanza` a nivel
de solicitud ni un archivo PDF adjunto —la semblanza es contenido, no un anexo—.

#### Actividad_Conversatorio · Actividad_MesaRedonda

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| nombre_participante_1 … 3 | Nombres de los participantes. Obligatorio el primero; hasta tres. |
| semblanza_participante_1 … 3 | Semblanza de cada participante, en el mismo orden. |

#### Actividad_Conferencia · Actividad_Charla · Actividad_LecturaObra · Actividad_Encuentro

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| nombre_participante_1 … 2 | Nombre de quien imparte. Obligatorio el primero; hasta dos. |
| semblanza_participante_1 … 2 | Semblanza de cada participante, en el mismo orden. |

#### Actividad_PresentacionLibro

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| titulo_publicacion | Título del libro. Obligatorio. |
| tipo_presentador | Rol del proponente respecto a la publicación: `autor`, `editor`, `antologador`, `compilador` o `coordinador`. |
| nombre_autor_1 … 5 | Nombres tal como aparecen en la portada. Obligatorio el primero; hasta cinco. |
| semblanza_autor_1 … 5 | Semblanza de cada autor, en el mismo orden. |
| autor_participa | Indica si el autor estará presente en la actividad. |
| nombres_de_autores_presentes | Nombres de quienes sí asistirán, cuando no todos los autores participan. |
| nombre_participante_1 … 2 | Presentadores. Opcional, hasta dos. |
| semblanza_participante_1 … 2 | Semblanza de cada presentador, en el mismo orden. |
| nombre_editorial | Editorial. Obligatorio; si la publicación es independiente, se anota así. |

`ejemplar_fisico_entregado` ya no vive en esta tabla: al ser un dato que **solo el
administrador escribe**, se movió a `DetallesAdminSolicitud` (§3.1), con nota de que aplica
únicamente a solicitudes de este tipo o de `Actividad_PresentacionRevista`.

Las fotografías del autor y de la portada dejaron de tener un booleano `tiene_foto_*` en esta
tabla: hoy se consultan directamente en `RouterDocumentos` (§2.8), anclado a esta misma tabla.

#### Actividad_PresentacionRevista

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| titulo_publicacion | Título de la revista. Obligatorio. |
| tipo_presentador | Rol del proponente respecto a la publicación. Mismo conjunto de valores que en `Actividad_PresentacionLibro`. |
| nombre_editor_1 … 2 | Nombres de los editores. Obligatorio el primero; hasta dos. |
| semblanza_editor_1 … 2 | Semblanza de cada editor, en el mismo orden. |
| editor_participa | Indica si el editor estará presente en la actividad. |
| nombres_de_editores_presentes | Nombres de quienes sí asistirán, cuando no todos los editores participan. |
| nombre_participante_1 … 2 | Presentadores. Opcional, hasta dos. |
| semblanza_participante_1 … 2 | Semblanza de cada presentador, en el mismo orden. |
| nombre_editorial | Editorial responsable de la revista. |

`ejemplar_fisico_entregado` sigue la misma lógica que en `Actividad_PresentacionLibro`: vive en
`DetallesAdminSolicitud` (§3.1), no aquí.

La portada de la revista sigue la misma lógica que en `Actividad_PresentacionLibro`: sin
booleano de caché, se consulta en `RouterDocumentos` (§2.8).

### 2.8 RouterDocumentos

Registro de los archivos que acompañan a una **actividad específica**, no a la solicitud en
general. Es polimórfico, y reutiliza exactamente el mismo mecanismo que `RouterActividades`
(§2.6) en vez de definir uno propio: mismo discriminador (`tipo_actividad_id`, FK a
`CatalogoActividades`, §2.5), mismo identificador (`detalle_id`, apuntando a la fila de
`Actividad_*` que corresponda). No hay un catálogo de "tipos de documento por actividad"
separado porque sería el mismo catálogo con la mayoría de sus filas sin usar.

Anclarlo a `Solicitudes_EVT` con una FK simple —como se intentó en una revisión anterior de
este documento— resolvía el caso de hoy (solo libro y revista llevan archivos) pero cerraba la
puerta a que otro tipo de actividad los necesite mañana sin agregar una columna nueva. Al
compartir el discriminador con `RouterActividades`, agregar un adjunto a un tipo de actividad
que hoy no lleva ninguno no requiere ninguna migración: solo empezar a escribir filas aquí con
ese `tipo_actividad_id`.

En la práctica, hoy solo existen filas para `Actividad_PresentacionLibro` y
`Actividad_PresentacionRevista`; para el resto de tipos, la tabla queda vacía. Esa restricción
no la impone la base de datos —el patrón polimórfico nunca lo hace (§1)—, la impone que
ningún otro formulario pida adjuntos todavía.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| tipo_actividad_id | Discriminador. FK → CatalogoActividades (§2.5); comparte el mismo campo y el mismo significado que `RouterActividades.tipo_actividad_id`. |
| detalle_id | Referencia polimórfica a la fila de la tabla `Actividad_*` que corresponda (§1) — hoy, siempre una de las dos tablas de presentación. |
| tipo_documento | Qué documento es. Hoy usa `portada_libro`, `portada_revista` o `retrato_autor` (este último solo aplica a libro); un tipo de actividad nuevo que requiera archivos agrega sus propios valores aquí, sin tocar la tabla. |
| storage_key | Ubicación del archivo almacenado. El formato —clave de almacenamiento, ruta o URL— está por definir. |

---

## 3. Etapa 2 — Administración y programación

Esta etapa agrupa los datos que **solo el administrador escribe**. Al aceptarse una solicitud
se crea una fila en `SolicitudesAprobadas`; únicamente lo registrado ahí puede programarse, y a
partir de ese punto entran las funciones del dominio `PRG`.

```mermaid
erDiagram
    Solicitudes_EVT {
        bigint id PK
        string titulo_actividad
        timestamp fecha_de_solicitud
    }
    DetallesAdminSolicitud {
        bigint id PK
        bigint solicitud_id FK
        string estado
        string categoria
        boolean is_participante_uady
        string titulo_final
        boolean es_apta_juvenil
        bigint revisado_por FK
    }
    SolicitudesAprobadas {
        bigint id PK
        bigint solicitud_id FK
        timestamp fecha_aprobacion
        bigint aprobada_por FK
    }
    ProgramacionActividad {
        bigint id PK
        bigint solicitud_aprobada_id FK
        date fecha
        bigint sala_id FK
        bigint bloque_id FK
        int num_ocasion
        string estado
    }
    ConfirmacionAplicante {
        bigint id PK
        bigint programacion_id FK
        bigint usuario_id FK
        timestamp fecha_confirmacion
    }

    Solicitudes_EVT ||--|| DetallesAdminSolicitud : "dictamina"
    Solicitudes_EVT ||--o| SolicitudesAprobadas : "si aceptada"
    SolicitudesAprobadas ||--o{ ProgramacionActividad : "programa"
    ProgramacionActividad ||--o| ConfirmacionAplicante : "notifica"
```

### 3.1 DetallesAdminSolicitud

El estado de la solicitud, su dictamen y los valores definitivos que fija el administrador.
La fila se crea al enviarse la solicitud, con `estado = pendiente` y el resto de los campos en
nulo; por eso la relación con `Solicitudes_EVT` es uno a uno obligatoria. Crearla desde el
inicio permite consultar las solicitudes pendientes sin interpretar la ausencia de una fila.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| solicitud_id | FK → Solicitudes_EVT. |
| estado | `pendiente`, `cambios_solicitados`, `aceptada`, `rechazada` o `cancelada`. `cancelada` solo aplica después de `aceptada`. |
| categoria | `literaria` o `academica`. La asigna el administrador durante el dictamen. |
| is_participante_uady | Indica si el participante pertenece a la UADY. **Lo determina el administrador, no el aplicante**, por lo que vive en esta etapa y no en la solicitud. Parte de `Solicitudes_EVT.es_uady` (§2.4) como autodeclaración, pero es este campo —no aquel— el que se usa junto con `categoria` para el conteo por categoría de `DetallesConvocatoria` (§3.6); el administrador puede confirmarlo o corregirlo. |
| titulo_final | Título definitivo de la actividad si el administrador lo modifica; nulo significa que vale `Solicitudes_EVT.titulo_actividad`. |
| organizador_final | Organizador definitivo; nulo significa que vale `Solicitudes_EVT.nombre_organizador_organizacion`. |
| es_apta_juvenil | Marca la actividad como apta para el catálogo escolar y juvenil de `VIS`. |
| en_cartelera_informal | Indica que la actividad aparece solo en cartelera informativa, sin horario fijo comprometido. |
| ejemplar_fisico_entregado | Indica si FILEY recibió el ejemplar físico de la publicación. **Específico de las solicitudes cuyo tipo de actividad (§2.6) es presentación de libro o revista**; nulo o sin sentido en las otras seis. Lo marca el administrador, por lo que vive aquí y no en `Actividad_PresentacionLibro` / `Actividad_PresentacionRevista` (§2.7), aunque el dato sea inherente a esas dos publicaciones. |
| fecha_revision | Fecha en que el administrador emitió el dictamen. |
| revisado_por | FK → Persona (administrador). |
| motivo_rechazo | Motivo registrado cuando `estado = rechazada`. |
| mensaje_cambios_solicitados | Indicación de qué debe corregir el aplicante. Obligatorio cuando `estado = cambios_solicitados`. |
| resultado_notificado | Indica si el resultado vigente ya se comunicó al aplicante en un lote (§3.5). |
| fecha_resultado_notificado | Fecha del último envío de resultado; nulo si nunca se ha notificado. |

Esta tabla ocupa el lugar de lo que sería una entidad "Actividad" independiente. No existe tal
entidad porque duplicaría el estado de la solicitud y obligaría a mantener ambos sincronizados.
Los estados de avance que esa entidad habría guardado son **derivados** y no se almacenan:

- Sin horario: no hay filas en `ProgramacionActividad` (§3.3).
- Programada: hay al menos una.
- Confirmada: sus programaciones tienen confirmación del aplicante (§3.4).

`PRG` y `TAL` sí modelan una entidad `Actividad` propia; queda pendiente homologar cómo
referencian desde ahí lo que en `EVT` es una solicitud aprobada.

### 3.2 SolicitudesAprobadas

Registro de las solicitudes que pasaron el dictamen. **Existir aquí equivale a estar
aprobada**, y `ProgramacionActividad` referencia esta tabla y no `Solicitudes_EVT`: así la
regla "solo se programa lo aprobado" queda garantizada por una clave foránea real, en lugar de
depender de que la aplicación consulte el estado.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| solicitud_id | FK → Solicitudes_EVT. |
| fecha_aprobacion | Marca de tiempo de la aprobación. |
| aprobada_por | FK → Persona (administrador que aceptó). |

Si una solicitud aprobada se cancela, **se eliminan sus filas de `ProgramacionActividad`** para
liberar la sala y el bloque, pero **la fila de esta tabla se conserva** como constancia de que
llegó a estar aprobada.

### 3.3 ProgramacionActividad

Una fila por cada **ocasión concreta** en que una actividad ocupa una fecha, una sala y uno o
más bloques de horario. Una misma actividad puede tener varias: repetirse el mismo día en
bloques distintos, o en días diferentes. La combinación de `fecha` y `bloque_id` es lo que
distingue una ocasión de otra.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| solicitud_aprobada_id | FK → SolicitudesAprobadas (§3.2). |
| fecha | Día de esta ocasión. |
| sala_id | FK → Sala (`SAL`). |
| stand_id | FK → Stand (`STD`); nulo si la actividad ocurre en una sala del catálogo. |
| bloque_id | FK → BloqueHorario (`PRG`). Bloque en que inicia. |
| bloques_extra | Bloques consecutivos adicionales, cuando la actividad dura más de uno. |
| num_ocasion | Número de esta ocasión dentro de la misma actividad: 1, 2, 3… |
| motivo_repeticion | Razón de la repetición: disponibilidad amplia del ponente, llenar un hueco del programa, etc. Nulo en la primera ocasión. |
| programa_maestro_id | FK → ProgramaMaestro (`PRG`). Versión del programa a la que pertenece. |
| estado | `tentativa`, `notificada`, `confirmada_por_aplicante` o `cerrada`. Corresponde a **esta ocasión**, no a la actividad completa. |

No pueden existir dos filas con la misma combinación de `sala_id`, `fecha` y `bloque_id`: un
bloque no admite dos actividades simultáneas.

### 3.4 ConfirmacionAplicante

Acuse de que el aplicante recibió y confirmó un horario. Como una actividad puede programarse
varias veces, existe una confirmación por cada ocasión notificada.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| programacion_id | FK → ProgramacionActividad. |
| usuario_id | FK → Persona. |
| fecha_notificacion | Fecha en que se envió la notificación del horario. |
| fecha_confirmacion | Fecha en que el aplicante confirmó; nulo mientras no responda. |
| solicito_cambio | Indica si el aplicante solicitó un cambio dentro de la ventana permitida. |
| detalle_cambio | Qué cambio solicitó, cuando aplica. |

### 3.5 NotificacionLote

Los resultados no se comunican solicitud por solicitud, sino en un envío masivo al terminar la
revisión.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| tipo | `seleccion` para el resultado del dictamen, `horario` para la asignación de sala y hora. |
| fecha_envio | Fecha del envío masivo. |
| enviado_por | FK → Persona (administrador). |
| total_enviadas | Número de notificaciones que incluyó el lote. |
| estado | `enviada` o `fallida_parcial`. |

### 3.6 DetallesConvocatoria

Es la tabla `detalles` que cuelga de `CatalogoConvocatorias` (§2.2) para el dominio `EVT`: los
parámetros comunes a cualquier convocatoria (nombre, fechas de apertura/cierre, `esta_activa`)
ya viven en el catálogo; lo que es específico de `EVT` —cupos, duración, prefijo de folio, y el
resto del calendario posterior al cierre— vive aquí. Relación uno a uno con la fila de
`CatalogoConvocatorias` cuyo `prefijo = EVT`.

Antes se llamaba `ParametrosConvocatoria` y era una tabla de una sola fila para toda la base de
datos, bajo la premisa de que cada edición de la feria vive en su propia instancia. Esa premisa
no cambia dentro de `EVT` —sigue habiendo una sola fila vigente aquí—, pero ahora es una fila
**por convocatoria** en vez de una fila fija de sistema, enlazada explícitamente por FK en lugar
de asumida.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| convocatoria_id | FK → CatalogoConvocatorias (§2.2), fila con `prefijo = EVT`. |
| prefijo_folio | Prefijo con el que se compone el folio visible de una solicitud (§2.4). Constante por convocatoria, modificable en el módulo; no se edita desde una pantalla de administración. |
| duracion_maxima_actividad | Duración máxima por actividad. Cincuenta minutos en la edición 2027. |
| fecha_notificacion_seleccion | Fecha en que se enviará el lote con los resultados del dictamen. |
| fecha_cierre_ajustes_aplicante | Fecha límite para que el aplicante solicite cambios de horario. |
| fecha_asignacion_horario | Fecha a partir de la cual los aplicantes ven su sala y hora asignadas. |
| fecha_constancias | Fecha a partir de la cual pueden descargarse las constancias. |
| cupo_literario_uady | Meta de actividades literarias de la UADY para esta convocatoria. Es una referencia de planeación, no un tope que la aplicación haga cumplir. |
| cupo_literario_externo | Meta de actividades literarias externas. Misma naturaleza que `cupo_literario_uady`. |
| cupo_academico_uady | Meta de actividades académicas de la UADY. Misma naturaleza que `cupo_literario_uady`. |
| cupo_academico_externo | Meta de actividades académicas externas. Misma naturaleza que `cupo_literario_uady`. |
| programa_archivado | Indica si el programa se cerró definitivamente. |
| fecha_archivado | Fecha y hora del cierre definitivo. |
| archivado_por | FK → Persona (administrador que ejecutó el cierre). |
| motivo_archivado | Motivo registrado al archivar. Obligatorio. |

Los cuatro `cupo_*` **no se consumen ni se hacen cumplir**: cuántas solicitudes de cada
categoría se aceptan es una decisión 100% del administrador, sin límite impuesto por el sistema.
Son la meta que se fijó al planear la convocatoria, y sirven de referencia frente a un **conteo
derivado** —no una columna, se calcula agrupando `DetallesAdminSolicitud` (§3.1) con
`estado = aceptada` por `categoria` × `is_participante_uady`— que la pantalla de revisión le
muestra al administrador para que sepa, en cualquier momento del dictamen, cuántas lleva
aceptadas de cada tipo frente a la meta. La decisión de seguir aceptando por encima o por debajo
de esa meta es suya.

### 3.7 BitacoraEVT

Auditoría de las acciones excepcionales del administrador: cambios de horario fuera de la
ventana normal, ediciones manuales del programa y similares.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| usuario_id | FK → Persona (quién ejecutó la acción). |
| accion | Acción realizada. |
| entidad_tipo | Entidad afectada: `DetallesAdminSolicitud`, `ProgramacionActividad`, etc. |
| entidad_id | Identificador de la fila afectada. |
| detalle | Descripción del cambio, del valor anterior al nuevo. |
| motivo | Razón registrada por el administrador. |
| fecha | Marca de tiempo. |

---

## 4. Relaciones principales

### Etapa 1 — captura

- **CatalogoConvocatorias** 1—N **RouterSolicitudes**. Cada solicitud enruta a través de una convocatoria vigente.
- **Persona** (`REG`) 1—N **RouterSolicitudes** 1—1 **Solicitudes_EVT**. Único camino entre una persona y sus solicitudes.
- **CatalogoActividades** 1—N **RouterActividades**. Cada fila de enrutamiento clasifica contra un tipo del catálogo.
- **Solicitudes_EVT** 1—1 **RouterActividades** →(polimórfica) **Actividad_\***. Una de las ocho, según `tipo_actividad_id`.
- **CatalogoActividades** 1—N **RouterDocumentos** →(polimórfica) **Actividad_\***. Comparte catálogo y mecanismo con `RouterActividades`; en la práctica solo hay filas para presentación de libro y revista.

### Etapa 2 — administración y programación

- **CatalogoConvocatorias** 1—1 **DetallesConvocatoria**. Los parámetros específicos de la convocatoria `EVT`.
- **Solicitudes_EVT** 1—1 **DetallesAdminSolicitud**. Se crea al enviarse la solicitud.
- **Solicitudes_EVT** 0/1—1 **SolicitudesAprobadas**. Solo si el dictamen fue `aceptada`.
- **SolicitudesAprobadas** 1—N **ProgramacionActividad**. Más de una cuando la actividad se repite.
- **ProgramacionActividad** 1—1 **ConfirmacionAplicante**. Una por cada ocasión notificada.
- **ProgramacionActividad** N—1 **Sala** (`SAL`) o N—1 **Stand** (`STD`).
- **ProgramacionActividad** N—1 **BloqueHorario** (`PRG`) y N—1 **ProgramaMaestro** (`PRG`).

---

## 5. Trazabilidad: entidad → caso de uso

Los casos de uso con número mayor a 012 corresponden a alcance previsto que aún no se redactó
como archivo; se listan como referencia, no como requisitos vigentes.

| Entidad | Casos de uso |
| --- | --- |
| CatalogoConvocatorias | CU-EVT-001, CU-EVT-002, CU-EVT-005, CU-EVT-011, CU-EVT-026 |
| RouterSolicitudes | CU-REG-001, CU-EVT-002 |
| Solicitudes_EVT · CatalogoActividades · RouterActividades · Actividad_* | CU-EVT-002, CU-EVT-003, CU-EVT-004, CU-EVT-006, CU-EVT-007, CU-EVT-008, CU-EVT-012 |
| RouterDocumentos | CU-EVT-002, CU-EVT-004 |
| DetallesAdminSolicitud | CU-EVT-003, CU-EVT-007 a CU-EVT-011, CU-EVT-012 |
| SolicitudesAprobadas | CU-EVT-009; CU-PRG-001 a CU-PRG-004 |
| ProgramacionActividad | CU-EVT-006, CU-EVT-014 a CU-EVT-017, CU-EVT-019, CU-EVT-020, CU-EVT-022 |
| ConfirmacionAplicante | CU-EVT-005, CU-EVT-022, CU-EVT-023 |
| NotificacionLote | CU-EVT-010, CU-EVT-022 |
| DetallesConvocatoria | CU-EVT-001, CU-EVT-005, CU-EVT-011, CU-EVT-026 |
| BitacoraEVT | CU-EVT-025, CU-EVT-026, CU-EVT-034 |

Cobertura de los doce casos de uso vigentes: todos quedan cubiertos por al menos una entidad.
**CU-EVT-005 (descargar constancia)** exigía como precondición que la actividad tuviera
`requiere_constancia = true`, campo que antes no existía en el modelo —solo estaba
`DetallesConvocatoria.fecha_constancias`, que define desde cuándo se descargan las constancias,
pero nada registraba quién las había solicitado—. Esa brecha queda cerrada con
`Solicitudes_EVT.requiere_constancia` (§2.4).
