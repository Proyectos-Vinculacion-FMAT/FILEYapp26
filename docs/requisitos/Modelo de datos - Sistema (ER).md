---
estado: vigente
version: "1.0"
tags:
  - tipo/modelo-de-datos
  - tema/arquitectura
  - tema/trazabilidad
fecha: 2026-08-21
fecha_actualizacion: 2026-08-21
---
# Modelo de datos del sistema — diagrama ER

Vista única de **todas** las entidades documentadas de FILEY y de cómo se referencian entre
dominios. Es un espejo, no una propuesta.

> [!danger] Este diagrama refleja el estado actual **con sus errores**, a propósito
> No corrige nada. Donde dos dominios se contradicen, se dibujan **las dos versiones**; donde
> un modelo referencia una entidad que nadie define, esa entidad aparece marcada como
> **fantasma** en vez de omitirse.
>
> Un diagrama "limpio" aquí sería una mentira útil para nadie: escondería justo lo que hay que
> decidir. El inventario de lo que está mal está en la [sección final](#inconsistencias-que-este-diagrama-hace-visibles),
> con su origen exacto.

**Fuentes.** Los siete `Modelo de datos - *.md` de `requisitos/`, leídos el 2026-08-21.
`SAL` no tiene modelo de datos (ver I-7).

---

## 0. Las dos capas

Antes de las entidades, la división que lo ordena todo
([ADR-0003](<../adr/0003-una-feria-por-schema.md>)): lo **global** vive una sola vez; lo de
**cada feria** vive una vez por edición, en su propio schema.

```mermaid
flowchart TD
    subgraph GLOBAL["🌐 Schema public — una sola copia"]
        REG["<b>REG</b> · Identidad<br/>Persona · SesionOTP<br/><i>RolPermiso (derogado)</i>"]
        FER["<b>FER</b> · Ferias<br/>Feria · AdminFeria"]
        REG --- FER
    end

    subgraph FERIA["🏛️ Schema feria_&lt;slug&gt; — una copia por edición"]
        direction LR
        STD["<b>STD</b><br/>Stands"]
        EVT["<b>EVT</b><br/>Eventos"]
        TAL["<b>TAL</b><br/>Talleres"]
        VIS["<b>VIS</b><br/>Visitas"]
        PRG["<b>PRG</b><br/>Programa"]
        SAL["<b>SAL</b><br/>Salas"]
    end

    GLOBAL -.->|"search_path por petición"| FERIA

    EVT -->|actividades aceptadas| PRG
    TAL -->|actividades aceptadas| PRG
    PRG -->|ocupa| SAL
    VIS -->|reserva cupo en| PRG
    EVT -.->|"ProgramacionActividad.stand_id"| STD

    classDef global fill:#01457C,stroke:#00437C,color:#fff
    classDef feria fill:#C99213,stroke:#8a6410,color:#fff
    class REG,FER global
    class STD,EVT,TAL,VIS,PRG,SAL feria
```

> [!note] `EVT` → `STD` es una flecha que sorprende
> `ProgramacionActividad.stand_id` permite programar una actividad **dentro de un stand**
> (presentaciones en el stand de una editorial). Es la única dependencia de un dominio de
> contenido hacia `STD`, y no está reflejada en el modelo de `STD`, que no sabe que sus stands
> se usan para eso.

---

## 1. Capa global — `REG` + `FER`

```mermaid
erDiagram
    PERSONA ||--o{ SESION_OTP : "emite"
    PERSONA ||--o{ ADMIN_FERIA : "administra"
    FERIA   ||--o{ ADMIN_FERIA : "es administrada por"
    PERSONA ||--o{ ROL_PERMISO : "DEROGADO_pero_vive_en_codigo"

    PERSONA {
        int id PK
        string correo UK "único global, no por feria"
        string nombre_completo "decidido separar en nombres/apellidos, sin migrar"
        string telefono
        string estado "activa | inactiva"
        datetime fecha_registro
        datetime ultimo_acceso
    }

    SESION_OTP {
        int id PK
        int persona_id FK
        string codigo_hash "nunca en claro"
        string canal "correo"
        datetime creado_en
        datetime expira_en "creado_en + 15 min"
        bool usado
        int intentos "máx 3"
        bool acertado
    }

    FERIA {
        int id PK
        string nombre "FILEY 2027"
        string edicion "ordinal, XIV — vino de STD.Evento"
        string slug UK "prefijo de URL y nombre del schema"
        string estado "en_preparacion | activa | archivada"
        string sede "vino de STD.Evento"
        date fecha_inicio
        date fecha_fin
        datetime creada_en
    }

    ADMIN_FERIA {
        int id PK
        int feria_id FK
        int persona_id FK
        bool es_dueno "exactamente uno por feria"
        datetime creado_en
        int creado_por FK "Persona; nulo para el dueño"
    }

    ROL_PERMISO {
        int id PK "DEROGADO en docs (ADR-0004)"
        int persona_id FK "sigue existiendo en filey/apps/registros/models.py"
        string modulo "EVT | TAL | STD | VIS | *"
        string nivel "lectura | edicion"
        datetime creado_en
    }
```

> [!warning] `ROL_PERMISO` está en el diagrama porque está en el código
> La documentación lo derogó el 2026-08-21; `filey/apps/registros/models.py` todavía lo
> implementa, y el acceso administrativo real sigue funcionando con él. Es la única entidad del
> diagrama que existe **solo** en el código.

---

## 2. `STD` — Stands *(modelo v2.0, el único ya alineado con FER)*

```mermaid
erDiagram
    PERSONA ||--o{ EDITORIAL : "representa"
    PERSONA ||--o{ NOTIFICACION_STD : "recibe"
    EDITORIAL ||--o{ SELLO_EDITORIAL : "representa"
    EDITORIAL ||--o{ SOLICITUD_STD : "envía"
    EDITORIAL ||--o{ RESERVA : "hace"
    EDITORIAL ||--|| DOCUMENTO : "constancia fiscal"
    SOLICITUD_STD ||--o{ DOCUMENTO : "adjunta"
    RESERVA ||--o{ RESERVA_STAND : "detalla"
    STAND ||--o{ RESERVA_STAND : "es reservado en"
    RESERVA ||--o{ MOVIMIENTO : "recibe abonos"
    MOVIMIENTO ||--|| DOCUMENTO : "comprobante"
    RESERVA ||--o{ DESCUENTO_APLICADO : "aplica"
    PERSONA ||--o{ BITACORA_STD : "ejecuta"

    PERSONA {
        int id PK "REG — global"
    }
    EDITORIAL {
        int id PK
        int persona_id FK "era cuenta_id en v1.0"
        string nombre
        string giro "Editor | Librero | Distribuidor"
        string correo_electronico "distinto de Persona.correo"
        string nombre_antepecho
        int constancia_fiscal_id FK
    }
    SELLO_EDITORIAL {
        int id PK
        int editorial_id FK
        string nombre
    }
    SOLICITUD_STD {
        int id PK
        int editorial_id FK
        string estado "pendiente | aceptada | rechazada | cambios_solicitados"
        datetime fecha_envio
        datetime fecha_revision
        int revisado_por FK "Persona"
        string motivo_peticion
    }
    DOCUMENTO {
        int id PK
        string tipo
        string archivo_url
        string entidad_tipo "polimórfico"
        int entidad_id
    }
    STAND {
        int id PK
        string clave "sin evento_id: la feria es el schema"
        float pos_x
        float pos_y
        float metros_cuadrados
        string estado "Disponible | Reservado | Ocupado"
    }
    RESERVA {
        int id PK
        int editorial_id FK
        string estado "Por confirmar | Confirmada | Pagada | Cancelada"
        date fecha_vencimiento_anticipo "creacion + 30 días"
        date fecha_corte_pago_total
        money monto_total
        money monto_abonado
    }
    RESERVA_STAND {
        int id PK
        int reserva_id FK
        int stand_id FK
        float metros_cuadrados_snapshot
        money precio_snapshot
    }
    MOVIMIENTO {
        int id PK
        int reserva_id FK
        money monto
        string metodo "transferencia | deposito | cheque"
        string estado "pendiente_validacion | validado | rechazado"
        int registrado_por FK "Persona"
        int validado_por FK "Persona"
    }
    DESCUENTO_APLICADO {
        int id PK
        int reserva_id FK
        string tipo "pronto_pago | especial"
        float porcentaje
        int aplicado_por FK "Persona; nulo si automático"
    }
    NOTIFICACION_STD {
        int id PK
        int destinatario_id FK "Persona"
        string tipo
        string estado "enviada | fallida"
    }
    PARAMETROS_SISTEMA {
        money costo_m2 "una fila por feria, pese al nombre"
        float porcentaje_anticipo "50"
        int plazo_reserva_dias "30"
        float descuento_pronto_pago "10"
        date fecha_limite_pronto_pago
        string instrucciones_pago
        string salon_showfloor "vino de STD.Evento"
    }
    BITACORA_STD {
        int id PK
        int persona_id FK
        string accion
    }
```

---

## 3. `EVT` — Eventos *(patrón de routers polimórficos)*

```mermaid
erDiagram
    PERSONA ||--o{ ROUTER_SOLICITUDES : "crea"
    ROUTER_SOLICITUDES ||--|| SOLICITUDES_EVT : "apunta si convocatoria=EVT"
    SOLICITUDES_EVT ||--|| ROUTER_ACTIVIDADES : "enruta"
    ROUTER_ACTIVIDADES ||--|| ACTIVIDAD_TIPO_N : "una de ocho"
    SOLICITUDES_EVT ||--o{ ROUTER_DOCUMENTOS : "adjunta"
    SOLICITUDES_EVT ||--|| DETALLES_ADMIN_SOLICITUD : "dictamen"
    SOLICITUDES_EVT ||--o| SOLICITUDES_APROBADAS : "solo si aceptada"
    SOLICITUDES_APROBADAS ||--o{ PROGRAMACION_ACTIVIDAD : "se programa"
    PROGRAMACION_ACTIVIDAD ||--|| CONFIRMACION_APLICANTE : "confirma"
    PERSONA ||--o{ CONFIRMACION_APLICANTE : "responde"
    PERSONA ||--o{ NOTIFICACION_LOTE : "envía"
    PERSONA ||--o{ BITACORA_EVT : "ejecuta"

    PROGRAMACION_ACTIVIDAD }o--|| SALA_SAL : "ocupa"
    PROGRAMACION_ACTIVIDAD }o--o| STAND_STD : "o un stand"
    PROGRAMACION_ACTIVIDAD }o--|| BLOQUE_HORARIO_FANTASMA : "inicia en"
    PROGRAMACION_ACTIVIDAD }o--|| PROGRAMA_MAESTRO_FANTASMA : "pertenece a"

    PERSONA {
        int id PK "REG. EVT le supone pais/estado_pais/ciudad que REG no define"
    }
    ROUTER_SOLICITUDES {
        int id PK
        int usuario_django FK "Persona"
        string convocatoria "EVT | TAL | STD | VIS — discriminador"
        int solicitud_id "apunta a la tabla que diga el discriminador"
    }
    SOLICITUDES_EVT {
        int id PK
        string folio
        string institucion "por solicitud, no por persona"
        string cargo
    }
    ROUTER_ACTIVIDADES {
        int id PK
        int solicitud_id FK
        string tipo_actividad "8 valores — discriminador"
    }
    ACTIVIDAD_TIPO_N {
        int id PK "8 tablas: conversatorio, conferencia, charla…"
    }
    ROUTER_DOCUMENTOS {
        int id PK
        int solicitud_id FK
        string storage_key
    }
    DETALLES_ADMIN_SOLICITUD {
        int id PK
        int solicitud_id FK
        int revisado_por FK "Persona"
        string categoria "literaria | academica"
        bool is_participante_uady
    }
    SOLICITUDES_APROBADAS {
        int id PK
        int solicitud_id FK
        int aprobada_por FK "Persona"
    }
    PROGRAMACION_ACTIVIDAD {
        int id PK
        int solicitud_aprobada_id FK
        int sala_id FK "SAL"
        int stand_id FK "STD — nulo si va en sala"
        int bloque_id FK "PRG"
        int programa_maestro_id FK "PRG"
    }
    CONFIRMACION_APLICANTE {
        int id PK
        int programacion_id FK
        int usuario_id FK "Persona"
    }
    NOTIFICACION_LOTE {
        int id PK
        string tipo "seleccion | horario"
        int enviado_por FK "Persona"
        int total_enviadas
    }
    PARAMETROS_CONVOCATORIA {
        string prefijo_folio "tabla de una sola fila por feria"
        int cupo_literario_uady
        int cupo_literario_externo
        int cupo_academico_uady
        int cupo_academico_externo
        bool programa_archivado
        int archivado_por FK "Persona"
    }
    BITACORA_EVT {
        int id PK
        int usuario_id FK "Persona"
    }
    SALA_SAL {
        int id PK "SAL — sin modelo de datos propio"
    }
    STAND_STD {
        int id PK "STD"
    }
    BLOQUE_HORARIO_FANTASMA {
        int id PK "NO EXISTE — EVT la sitúa en PRG, PRG no la define"
    }
    PROGRAMA_MAESTRO_FANTASMA {
        int id PK "NO EXISTE — EVT la sitúa en PRG, PRG no la define"
    }
```

---

## 4. `TAL` — Talleres

```mermaid
erDiagram
    PERSONA ||--|| TALLERISTA : "es"
    TALLERISTA ||--o{ PROPUESTA_TALLER : "envía"
    TIPO_ACTIVIDAD_TAL ||--o{ PROPUESTA_TALLER : "clasifica"
    PROPUESTA_TALLER ||--o| ACTIVIDAD_TAL : "solo si aceptada"
    TIPO_ACTIVIDAD_TAL ||--o{ ACTIVIDAD_TAL : "clasifica"
    PERSONA ||--o{ NOTIFICACION_LOTE_TAL : "envía"

    EDICION_FERIA_FANTASMA ||--o{ PROPUESTA_TALLER : "edicion_id"
    EDICION_FERIA_FANTASMA ||--o{ ACTIVIDAD_TAL : "edicion_id"
    EDICION_FERIA_FANTASMA ||--|| PARAMETROS_CONVOCATORIA_TAL : "edicion_id (PK compuesta)"
    EDICION_FERIA_FANTASMA ||--o{ NOTIFICACION_LOTE_TAL : "edicion_id"

    PERSONA {
        int id PK "REG"
    }
    TALLERISTA {
        int id PK
        int persona_id FK
    }
    TIPO_ACTIVIDAD_TAL {
        int id PK
        string nombre "Taller | Cuentacuentos | Plática…"
    }
    PROPUESTA_TALLER {
        int id PK
        int edicion_id FK "❌ contradice ADR-0003"
        int tallerista_id FK
        int tipo_actividad_id FK
        int revisado_por FK "Persona"
        string estado
    }
    ACTIVIDAD_TAL {
        int id PK
        int propuesta_id FK
        int edicion_id FK "❌ contradice ADR-0003"
        int tipo_actividad_id FK
    }
    PARAMETROS_CONVOCATORIA_TAL {
        int edicion_id PK "❌ dentro de la clave primaria compuesta"
    }
    NOTIFICACION_LOTE_TAL {
        int id PK
        int edicion_id FK "❌ contradice ADR-0003"
        int enviado_por FK "Persona"
    }
    EDICION_FERIA_FANTASMA {
        int id PK "NO EXISTE — es Feria (FER); ningún modelo define EdicionFeria"
    }
```

---

## 5. `VIS` — Visitas escolares

```mermaid
erDiagram
    CUENTA_FANTASMA ||--o{ PROPUESTA_VISITA : "aplicante_id / revisado_por"
    PROPUESTA_VISITA ||--|| INSTITUCION : "describe"
    PROPUESTA_VISITA ||--|| RESPONSABLE : "la llena"
    PROPUESTA_VISITA ||--o{ GRUPO : "divide en (máx 3)"
    PROPUESTA_VISITA ||--|| VISITA : "se activa al aceptarse"
    VISITA ||--o{ RESERVA_TALLER : "arma itinerario"
    VISITA ||--o{ ENVIO_CONFIRMACION : "recibe"
    RESERVA_TALLER }o--|| PROGRAMACION_PRG : "reserva cupo en"

    CUENTA_FANTASMA {
        int id PK "NO EXISTE — es Persona (REG)"
    }
    PROPUESTA_VISITA {
        int id PK
        int aplicante_id FK "❌ apunta a Cuenta"
        int revisado_por FK "❌ apunta a Cuenta"
        string estado
    }
    INSTITUCION {
        int id PK
        int propuesta_id FK
        string nombre
    }
    RESPONSABLE {
        int id PK
        int propuesta_id FK
        string nombre "no siempre el director"
    }
    GRUPO {
        int id PK
        int propuesta_id FK
        string grado
        int cantidad
    }
    VISITA {
        int id PK "= PropuestaVisita aceptada"
    }
    RESERVA_TALLER {
        int id PK
        int visita_id FK
        int programacion_id FK "una ocasión concreta, no la Actividad"
    }
    ENVIO_CONFIRMACION {
        int id PK
        int visita_id FK
        string paquete "carta + reglamento"
    }
    PROGRAMACION_PRG {
        int id PK "PRG"
    }
```

---

## 6. `PRG` + `SAL` — Programa y salas

```mermaid
erDiagram
    ACTIVIDAD_PRG ||--o{ PROGRAMACION : "ocurre en"
    PROGRAMACION }o--|| SALA : "ocupa"
    ACTIVIDAD_PRG ||--o{ NOTIFICACION_PRG : "se notifica"
    PROGRAMACION ||--o{ RESPUESTA_PROGRAMACION : "se responde"
    NOTIFICACION_PRG ||--o{ RESPUESTA_PROGRAMACION : "origina"
    CUENTA_FANTASMA ||--o{ NOTIFICACION_PRG : "disparada_por"
    SALON_FANTASMA ||--o{ SALA : "se subdivide en"

    ACTIVIDAD_PRG {
        int id PK "referencia a la aceptada de EVT/TAL — el dato vive allá"
    }
    PROGRAMACION {
        int id PK
        int actividad_id FK
        int sala_id FK "SAL"
        date fecha
        string estado "preliminar | final"
    }
    SALA {
        int id PK "definida aquí, pero descrita como 'referencia a SAL'"
        int aforo
        string disponibilidad
    }
    NOTIFICACION_PRG {
        int id PK
        int actividad_id FK "por actividad, no por Programación"
        int disparada_por FK "❌ apunta a Cuenta"
    }
    RESPUESTA_PROGRAMACION {
        int id PK
        int programacion_id FK
        int notificacion_id FK
        string respuesta "asiste | no asiste"
    }
    CUENTA_FANTASMA {
        int id PK "NO EXISTE — es Persona (REG)"
    }
    SALON_FANTASMA {
        int id PK "NO EXISTE — SAL no tiene modelo de datos"
    }
```

---

## Inconsistencias que este diagrama hace visibles

Ninguna está corregida. Ordenadas por lo que cuesta arreglarlas.

| # | Qué | Dónde | Estado |
| --- | --- | --- | --- |
| **I-1** | `edicion_id` → `EdicionFeria`, una entidad que **ningún modelo define**. Contradice ADR-0003: ninguna tabla de dominio guarda identificador de edición. En `ParametrosConvocatoriaTAL` está **dentro de la clave primaria compuesta**, que es lo que la vuelve cara de quitar. | `TAL` §2.3, §2.4, §2.5, §2.6 | Ya registrada |
| **I-2** | `aplicante_id` y `revisado_por` → `Cuenta`, entidad extraída a `Persona`. | `VIS` §2.1 | Ya registrada |
| **I-3** | `Notificacion.disparada_por` → `Cuenta`. | `PRG` §2.4 | Ya registrada |
| **I-4** | **Dos modelos de programación coexistiendo.** `EVT` define `ProgramacionActividad` (con `sala_id`, `stand_id`, `bloque_id`, `programa_maestro_id`) y `PRG` define `Programación` (con `actividad_id`, `sala_id`). No es que uno referencie al otro: son dos diseños distintos del mismo hecho. `VIS` reserva contra el de `PRG`. | `EVT` §3.3 vs `PRG` §2.2 | **Nueva** |
| **I-5** | `EVT` referencia `BloqueHorario` y `ProgramaMaestro` **situándolas en `PRG`**, y `PRG` no define ninguna de las dos. | `EVT` §3.3 | **Nueva** |
| **I-6** | `EVT` afirma que `Persona` guarda `pais`, `estado_pais` y `ciudad`. El modelo de `REG` **no define esos atributos**. Un dominio le está poniendo campos a una entidad de otro. | `EVT` §2.1 vs `REG` §2.1 | **Nueva** |
| **I-7** | **`SAL` no tiene modelo de datos.** `Salón` y `Sala` son el catálogo del que depende toda la programación, y la única definición de `Sala` está dentro de `PRG` §2.3 — que a su vez la describe como "referencia al espacio de `SAL`". `Salón` no está definido en ninguna parte. | `SAL` | **Nueva** |
| **I-8** | **Tres nombres para la unidad programable.** `EVT` la llama `SolicitudesAprobadas`, `TAL` la llama `Actividad`, y `PRG` la llama `Actividad` describiéndola como referencia a ambas. `PRG` no puede referenciar dos tablas distintas con una sola FK sin un discriminador, y no lo tiene. | `EVT` §3.2, `TAL` §2.4, `PRG` §2.1 | **Nueva** |
| **I-9** | `EVT.ProgramacionActividad.stand_id` → `Stand` (`STD`). Es legítimo (actividades dentro de un stand), pero el modelo de `STD` no lo menciona: desde `STD`, sus stands solo los usa `ReservaStand`. | `EVT` §3.3 | **Nueva** |
| **I-10** | `RolPermiso` derogado en la documentación, **vivo en el código**. Es la única entidad que existe solo en `filey/`. | `REG` §2.2 vs código | Ya registrada |
| **I-11** | `Persona.nombre_completo` desplegado vs. `nombres`/`apellidos` decididos el 2026-08-19. | `REG` §5 | Ya registrada |
| **I-12** | Tres nombres para la configuración de una convocatoria: `ParametrosSistema` (`STD`), `ParametrosConvocatoria` (`EVT`), `ParametrosConvocatoriaTAL` (`TAL`). Misma figura, tres nombres. | `STD` §3.11, `EVT` §3.6, `TAL` §2.5 | Ya registrada |

> [!important] Las cinco nuevas se concentran en la frontera `EVT` ↔ `PRG` ↔ `SAL`
> I-4, I-5, I-7 y I-8 son **el mismo problema visto desde cuatro ángulos**: nadie ha decidido
> quién es el dueño del modelo de programación. `EVT` se construyó el suyo completo (con
> bloques y programa maestro), `PRG` construyó otro más simple, `SAL` no construyó ninguno, y
> `VIS` ya reserva cupo contra el de `PRG`.
>
> Es la misma clase de contradicción que ADR-0003 resolvió para la edición de la feria, y
> conviene resolverla antes de construir `PRG`: hoy `EVT` es el dominio que se implementa a
> continuación, y su modelo asume entidades que no existen.
