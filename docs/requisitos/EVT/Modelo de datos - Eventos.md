---
estado: propuesta
version: "3.0"
tags:
  - tipo/modelo-de-datos
  - dom/evt
fecha: 2026-06-23
fecha_actualizacion: 2026-08-20
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
conectan entidades y, cuando hace falta, indican **a qué tabla** apunta la conexión.

| Tabla | Propósito |
| --- | --- |
| Router de solicitudes | Relaciona a la persona con las solicitudes que ha creado, y determina mediante `convocatoria` a qué dominio pertenece cada una. Es único para todo el sistema: sirve a `EVT`, `TAL`, `STD` y `VIS`. |
| Router de actividades | Relaciona una solicitud con su actividad específica, y determina mediante `tipo_actividad` cuál de las ocho tablas la contiene. |
| Router de documentos | Relaciona los documentos adjuntos con su solicitud. Permite uno o varios por solicitud y guarda la ubicación del archivo. |

Visualmente:

```mermaid
flowchart TD
    U[Persona<br/>registro global del sistema]

    RS{{Router de solicitudes<br/>discriminador: convocatoria}}

    S_EVT[Solicitudes EVT]
    S_TAL[Solicitudes TAL]
    S_STD[Solicitudes STD]
    S_VIS[Solicitudes VIS]

    RD{{Router de documentos<br/>tipo_documento + storage_key}}
    RA{{Router de actividades<br/>discriminador: tipo_actividad}}

    A_1[Actividad tipo 1]
    A_2[Actividad tipo 2]
    A_n[Actividad tipo N]

    U --> RS
    RS --> S_EVT
    RS --> S_TAL
    RS --> S_STD
    RS --> S_VIS

    S_EVT --> RD
    S_EVT --> RA

    RA -.->|solo una| A_1
    RA -.-> A_2
    RA -.-> A_n

    style S_EVT fill:#2C4C8C , stroke:#01457C
```

### Referencias polimórficas

Los routers de solicitudes y de actividades comparten un mecanismo: guardan un
**discriminador** que nombra la tabla destino y un **identificador** de la fila dentro de esa
tabla.

| Router | Discriminador | Identificador | Destinos posibles |
| --- | --- | --- | --- |
| `RouterSolicitudes` | `convocatoria` | `solicitud_id` | `Solicitudes_EVT`, `Solicitudes_TAL`, `Solicitudes_STD`, `Solicitudes_VIS` |
| `RouterActividades` | `tipo_actividad` | `detalle_id` | Las ocho tablas `Actividad_*` |

Como el identificador puede apuntar a tablas distintas según el discriminador, **no es una
clave foránea con restricción**: la base de datos no puede validarlo. La integridad depende de
la capa de aplicación, y conviene resguardarla con pruebas o con el mecanismo de relaciones
genéricas que ofrezca el ORM. A cambio, el patrón permite agregar convocatorias o tipos de
actividad sin modificar las tablas existentes.

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

    RouterSolicitudes {
        bigint id PK
        bigint usuario_django FK
        string convocatoria "DISCRIMINADOR"
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
        boolean tiene_semblanza
        boolean tiene_sinopsis
        string comentarios
        timestamp fecha_de_solicitud
    }

    RouterActividades {
        bigint id PK
        bigint solicitud_id FK
        string tipo_actividad "DISCRIMINADOR"
        bigint detalle_id FK "REFERENCIA POLIMORFICA"
    }

    RouterDocumentos {
        bigint id PK
        bigint solicitud_id FK
        string tipo_documento
        string storage_key
    }

    Actividad_Conversatorio {
        bigint id PK
        string nombre_participante_1
        string nombre_participante_2
        string nombre_participante_3
    }

    Actividad_Conferencia {
        bigint id PK
        string nombre_participante_1
        string nombre_participante_2
    }

    Actividad_Charla {
        bigint id PK
        string nombre_participante_1
        string nombre_participante_2
    }

    Actividad_MesaRedonda {
        bigint id PK
        string nombre_participante_1
        string nombre_participante_2
        string nombre_participante_3
    }

    Actividad_PresentacionLibro {
        bigint id PK
        string titulo_publicacion
        string tipo_presentador
        string nombre_autor_1
        string nombre_autor_2
        string nombre_autor_3
        string nombre_autor_4
        string nombre_autor_5
        boolean autor_participa
        string nombres_de_autores_presentes
        string nombre_participante_1
        string nombre_participante_2
        string nombre_editorial
        boolean tiene_foto_autor
        boolean tiene_foto_portada
        boolean ejemplar_fisico_entregado
    }

    Actividad_PresentacionRevista {
        bigint id PK
        string titulo_publicacion
        string tipo_presentador
        string nombre_editor_1
        string nombre_editor_2
        boolean editor_participa
        string nombres_de_editores_presentes
        string nombre_participante_1
        string nombre_participante_2
        string nombre_editorial
        boolean tiene_foto_portada
        boolean ejemplar_fisico_entregado
    }

    Actividad_LecturaObra {
        bigint id PK
        string nombre_participante_1
        string nombre_participante_2
    }

    Actividad_Encuentro {
        bigint id PK
        string nombre_participante_1
        string nombre_participante_2
    }


    Persona ||--o{ RouterSolicitudes : "tiene"

    RouterSolicitudes }o--|| Solicitudes_EVT : "enruta"

    Solicitudes_EVT ||--o{ RouterActividades : "contiene"
    Solicitudes_EVT ||--o{ RouterDocumentos : "adjunta"

    RouterActividades }o..|| Actividad_Conversatorio : "enruta"
    RouterActividades }o..|| Actividad_Conferencia : "enruta"
    RouterActividades }o..|| Actividad_Charla : "enruta"
    RouterActividades }o..|| Actividad_MesaRedonda : "enruta"
    RouterActividades }o..|| Actividad_PresentacionLibro : "enruta"
    RouterActividades }o..|| Actividad_PresentacionRevista : "enruta"
    RouterActividades }o..|| Actividad_LecturaObra : "enruta"
    RouterActividades }o..|| Actividad_Encuentro : "enruta"
```

### 2.1 Persona

Entidad del core de Registros (`REG`); se referencia aquí, no se define. Su detalle completo
—incluido el acceso por código de un solo uso— está en
[`REG/Modelo de datos - Registros.md`](<../REG/Modelo%20de%20datos%20-%20Registros.md>).

Guarda la identidad y la **procedencia geográfica** (`pais`, `estado_pais`, `ciudad`), que son
datos de perfil: se capturan una vez y se reutilizan en cualquier convocatoria. La institución
y el cargo, en cambio, se capturan por solicitud (§2.3), porque una misma persona puede aplicar
representando a instituciones distintas.

Al no existir copia de la procedencia dentro de la solicitud, el modelo refleja siempre el
valor vigente del perfil, no el que tenía la persona al enviar.

> El formulario del prototipo captura "Ciudad / Estado" en un solo campo de texto; al portarlo
> habrá que dividirlo en los tres campos que define esta entidad.

### 2.2 RouterSolicitudes

Único vínculo entre una persona y sus solicitudes: `Solicitudes_EVT` no tiene clave foránea
hacia `Persona`. Sin una fila aquí, la solicitud no tiene dueño conocido, por lo que su
creación es obligatoria al enviar.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| usuario_django | FK → Persona. Conserva el nombre `usuario_django` porque referencia la tabla de usuarios del framework. |
| convocatoria | Discriminador: `EVT`, `TAL`, `STD` o `VIS`. Determina a qué tabla apunta `solicitud_id`. |
| solicitud_id | Referencia polimórfica a la solicitud, en la tabla que indique `convocatoria` (§1). |

### 2.3 Solicitudes_EVT

Los datos que el aplicante captura y que son **comunes a los ocho tipos de actividad**. Lo que
varía entre tipos vive en las tablas `Actividad_*` (§2.5); lo que decide el administrador vive
en la etapa 2 (§3).

| Atributo | Descripción |
| --- | --- |
| id | Identificador único, `bigint`. Es la base del folio: el folio visible **no se almacena**, se compone como `{prefijo_folio}-{id}` con el prefijo de `ParametrosConvocatoria` (§3.6). |
| institucion | Dependencia o institución que representa. Obligatorio. |
| cargo | Cargo dentro de esa institución. Opcional. |
| titulo_actividad | Título de la actividad tal como lo propone el aplicante. Si el administrador lo modifica tras la revisión, el valor definitivo queda en `DetallesAdminSolicitud.titulo_final` (§3.1). |
| nombre_moderador | Moderador de la actividad. Opcional, uno como máximo. |
| nombre_organizador_organizacion | Persona u organización que organiza. Obligatorio. |
| publico_objetivo | Público al que va dirigida. Lista de valores separados sobre el conjunto cerrado `publico_general`, `academico`, `estudiantil`, `infantil`, `familias`; al menos uno. Al no estar normalizado, filtrar por público exige recorrer el texto. |
| tiene_semblanza | Indica si se adjuntó la semblanza de los participantes (PDF). |
| tiene_sinopsis | Indica si se adjuntó la sinopsis de la actividad (PDF). |
| comentarios | Observaciones libres del aplicante. Opcional. |
| fecha_de_solicitud | Marca de tiempo del momento en que la solicitud se envía y se guarda. |

Los campos `tiene_*` duplican información que ya está en `RouterDocumentos` (§2.6): si existe
una fila con el `tipo_documento` correspondiente, el documento fue adjuntado. Se conservan como
caché para validar el formulario sin consultar el router, con la condición de que un solo
servicio sea responsable de escribir ambos; de lo contrario pueden desincronizarse.

### 2.4 RouterActividades

Conecta la solicitud con su actividad específica y determina de qué tipo es. Una fila por
solicitud.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| solicitud_id | FK → Solicitudes_EVT. |
| tipo_actividad | Discriminador: `conversatorio`, `conferencia`, `charla`, `mesa_redonda`, `presentacion_libro`, `presentacion_revista`, `lectura_obra` o `encuentro`. |
| detalle_id | Referencia polimórfica a la fila de la tabla `Actividad_*` que corresponda (§1). |

### 2.5 Tablas `Actividad_*`

Ocho tablas, una por tipo de actividad. Contienen únicamente lo que distingue a ese tipo: los
campos que comparten los ocho ya viven en `Solicitudes_EVT` (§2.3).

Hoy varios tipos coinciden en su estructura —Conversatorio y Mesa redonda por un lado;
Conferencia, Charla, Lectura de obra y Encuentro por otro—, pero se mantienen separados a
propósito. Cada tipo corresponde a un formulario distinto, y tener su propia tabla permite que
evolucione sin arrastrar a los demás; agruparlos por coincidencia actual cerraría esa puerta.

Los campos `tiene_*` siguen la misma lógica descrita en §2.3: son un indicador de que el
documento fue adjuntado, mientras el archivo se registra en `RouterDocumentos`.

#### Actividad_Conversatorio · Actividad_MesaRedonda

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| nombre_participante_1 … 3 | Nombres de los participantes. Obligatorio el primero; hasta tres. |

#### Actividad_Conferencia · Actividad_Charla · Actividad_LecturaObra · Actividad_Encuentro

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| nombre_participante_1 … 2 | Nombre de quien imparte. Obligatorio el primero; hasta dos. |

#### Actividad_PresentacionLibro

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| titulo_publicacion | Título del libro. Obligatorio. |
| tipo_presentador | Rol del proponente respecto a la publicación: `autor`, `editor`, `antologador`, `compilador` o `coordinador`. |
| nombre_autor_1 … 5 | Nombres tal como aparecen en la portada. Obligatorio el primero; hasta cinco. |
| autor_participa | Indica si el autor estará presente en la actividad. |
| nombres_de_autores_presentes | Nombres de quienes sí asistirán, cuando no todos los autores participan. |
| nombre_participante_1 … 2 | Presentadores. Opcional, hasta dos. |
| nombre_editorial | Editorial. Obligatorio; si la publicación es independiente, se anota así. |
| tiene_foto_autor | Indica si se adjuntó la fotografía del autor en alta resolución. |
| tiene_foto_portada | Indica si se adjuntó la portada del libro. |
| ejemplar_fisico_entregado | Indica si FILEY recibió el ejemplar físico que exige este tipo de actividad. Lo marca el administrador, pero reside aquí por ser un dato inherente a la publicación. |

#### Actividad_PresentacionRevista

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| titulo_publicacion | Título de la revista. Obligatorio. |
| tipo_presentador | Rol del proponente respecto a la publicación. Mismo conjunto de valores que en `Actividad_PresentacionLibro`. |
| nombre_editor_1 … 2 | Nombres de los editores. Obligatorio el primero; hasta dos. |
| editor_participa | Indica si el editor estará presente en la actividad. |
| nombres_de_editores_presentes | Nombres de quienes sí asistirán, cuando no todos los editores participan. |
| nombre_participante_1 … 2 | Presentadores. Opcional, hasta dos. |
| nombre_editorial | Editorial responsable de la revista. |
| tiene_foto_portada | Indica si se adjuntó la portada de la revista. |
| ejemplar_fisico_entregado | Indica si FILEY recibió el ejemplar físico. Ver la nota equivalente en `Actividad_PresentacionLibro`. |

### 2.6 RouterDocumentos

Registro de los archivos que acompañan a una solicitud. Una fila por documento, de modo que
una solicitud puede tener tantos como requiera su tipo de actividad sin columnas fijas.

| Atributo | Descripción |
| --- | --- |
| id | Identificador único. |
| solicitud_id | FK → Solicitudes_EVT. |
| tipo_documento | Qué documento es: semblanza, sinopsis de la actividad, sinopsis de la publicación, fotografía del autor o portada. |
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
| is_participante_uady | Indica si el participante pertenece a la UADY. **Lo determina el administrador, no el aplicante**, por lo que vive en esta etapa y no en la solicitud. Junto con `categoria` decide qué cupo consume (§3.6). |
| titulo_final | Título definitivo de la actividad si el administrador lo modifica; nulo significa que vale `Solicitudes_EVT.titulo_actividad`. |
| organizador_final | Organizador definitivo; nulo significa que vale `Solicitudes_EVT.nombre_organizador_organizacion`. |
| es_apta_juvenil | Marca la actividad como apta para el catálogo escolar y juvenil de `VIS`. |
| en_cartelera_informal | Indica que la actividad aparece solo en cartelera informativa, sin horario fijo comprometido. |
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

### 3.6 ParametrosConvocatoria

Configuración de la convocatoria. Cambia en cada edición, por lo que no puede quedar fija en
código. Es una tabla de **una sola fila**: cada edición de la feria vive en su propia instancia
de base de datos, de modo que la edición es implícita y ninguna tabla del modelo guarda un
identificador de edición.

| Atributo | Descripción |
| --- | --- |
| prefijo_folio | Prefijo con el que se compone el folio visible de una solicitud (§2.3). Constante por convocatoria, modificable en el módulo; no se edita desde una pantalla de administración. |
| duracion_maxima_actividad | Duración máxima por actividad. Cincuenta minutos en la edición 2027. |
| fecha_apertura_convocatoria | Fecha de lanzamiento de la convocatoria pública. |
| fecha_cierre_convocatoria | Fecha y hora en que deja de recibirse solicitudes. |
| fecha_notificacion_seleccion | Fecha en que se enviará el lote con los resultados del dictamen. |
| fecha_cierre_ajustes_aplicante | Fecha límite para que el aplicante solicite cambios de horario. |
| fecha_asignacion_horario | Fecha a partir de la cual los aplicantes ven su sala y hora asignadas. |
| fecha_constancias | Fecha a partir de la cual pueden descargarse las constancias. |
| cupo_literario_uady | Número máximo de actividades literarias de la UADY. |
| cupo_literario_externo | Número máximo de actividades literarias externas. |
| cupo_academico_uady | Número máximo de actividades académicas de la UADY. |
| cupo_academico_externo | Número máximo de actividades académicas externas. |
| programa_archivado | Indica si el programa se cerró definitivamente. |
| fecha_archivado | Fecha y hora del cierre definitivo. |
| archivado_por | FK → Persona (administrador que ejecutó el cierre). |
| motivo_archivado | Motivo registrado al archivar. Obligatorio. |

Los cuatro cupos se consumen **al aceptar una solicitud**, en la etapa de administración. El
administrador asigna `categoria` e `is_participante_uady` (§3.1) y la combinación de ambos
determina cuál de los cuatro contadores se decrementa: una solicitud literaria marcada como
UADY resta uno a `cupo_literario_uady`, una académica no marcada resta uno a
`cupo_academico_externo`, y así con el resto.

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

**Etapa 1 — captura**

- **Persona** (`REG`) 1—N **RouterSolicitudes** 1—1 **Solicitudes_EVT**. Único camino entre una persona y sus solicitudes.
- **Solicitudes_EVT** 1—1 **RouterActividades** →(polimórfica) **Actividad_\***. Una de las ocho, según `tipo_actividad`.
- **Solicitudes_EVT** 1—N **RouterDocumentos**.

**Etapa 2 — administración y programación**

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
| RouterSolicitudes | CU-REG-001, CU-EVT-002 |
| Solicitudes_EVT · RouterActividades · Actividad_* | CU-EVT-002, CU-EVT-003, CU-EVT-004, CU-EVT-006, CU-EVT-007, CU-EVT-008, CU-EVT-012 |
| RouterDocumentos | CU-EVT-002, CU-EVT-004 |
| DetallesAdminSolicitud | CU-EVT-003, CU-EVT-007 a CU-EVT-011, CU-EVT-012 |
| SolicitudesAprobadas | CU-EVT-009; CU-PRG-001 a CU-PRG-004 |
| ProgramacionActividad | CU-EVT-006, CU-EVT-014 a CU-EVT-017, CU-EVT-019, CU-EVT-020, CU-EVT-022 |
| ConfirmacionAplicante | CU-EVT-005, CU-EVT-022, CU-EVT-023 |
| NotificacionLote | CU-EVT-010, CU-EVT-022 |
| ParametrosConvocatoria | CU-EVT-001, CU-EVT-005, CU-EVT-011, CU-EVT-026 |
| BitacoraEVT | CU-EVT-025, CU-EVT-026, CU-EVT-034 |

Cobertura de los doce casos de uso vigentes: todos quedan cubiertos por al menos una entidad,
salvo una dependencia sin resolver. **CU-EVT-005 (descargar constancia)** exige como
precondición que la actividad tenga `requiere_constancia = true`, y ese campo no existe en el
modelo: `ParametrosConvocatoria.fecha_constancias` define desde cuándo se descargan las
constancias, pero nada registra quién las solicitó.
