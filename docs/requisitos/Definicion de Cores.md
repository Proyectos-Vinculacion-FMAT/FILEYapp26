---
estado: propuesta
version: 0.1
tags:
  - arquitectura
  - cores
  - transversal
fecha: 2026-06-20
autor: Juan Manuel Hernandez Miranda
---
# Definición de los 3 Cores — Sistema FILEY

Los **cores** son los tres servicios transversales que no pertenecen a ningún dominio individual (STD / EVE / TAL) sino que todos los dominios los consumen. Definirlos como unidades separadas evita que cada módulo duplique lógica e impide inconsistencias entre los datos de Hipólito, Elvira y los expositores cuando una misma persona o espacio aparece en más de un dominio.

> [!important]
> Los cores **no son módulos con pantallas propias** (excepto el catálogo de salas, que sí tiene administración). Son **servicios y entidades compartidas** que cada dominio usa a través de interfaces definidas.

---

## Mapa de dependencias

```
              ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
  Dominio →   │     STD     │   │     EVE     │   │     TAL     │
              │   Stands    │   │  Eventos    │   │  Talleres   │
              └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
                     │                 │                  │
       ┌─────────────┼─────────────────┼──────────────────┤
       │             │                 │                  │
       ▼             ▼                 ▼                  ▼
  ┌──────────┐  ┌──────────────────────────┐  ┌──────────────────┐
  │  CORE    │  │         CORE             │  │      CORE        │
  │REGISTROS │  │       PROGRAMAS          │  │  SALAS/SALONES   │
  └──────────┘  └──────────────────────────┘  └──────────────────┘
```

| Core | Lo usa STD | Lo usa EVE | Lo usa TAL |
|------|-----------|-----------|-----------|
| **Registros** | Sí — Cuenta + perfil Editorial | Sí — identidad del proponente | Sí — identidad del tallerista/escuela |
| **Programas** | No (tiene su propio mapa de stands) | Sí — calendario maestro | Sí — programa infantil/juvenil |
| **Salas/Salones** | Referencia indirecta (stand como lugar de actividad) | Sí — asignación de sala por actividad | Sí — asignación de espacio Ek Balam / cine |

---

## Core 1 — Registros

### Propósito

Proporcionar una **identidad única de persona** que funcione como punto de entrada a cualquier módulo del sistema FILEY. Una misma persona (p. ej. un autor que da un taller y tiene stand) no debe capturar sus datos básicos más de una vez.

### Entidades

#### Persona
La entidad base de identidad. Compartida entre todos los dominios.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único interno. |
| correo | Correo electrónico (único en el sistema). |
| telefono | Teléfono de contacto (único en el sistema). |
| nombre_completo | Nombre de la persona o razón social. |
| tipo | `persona_fisica` / `institucion`. |
| fecha_registro | Alta en el sistema. |
| estado | `activa` / `inactiva`. |

> [!note]
> El identificador único de persona es la combinación **correo + teléfono** (acordado en Junta 2). El nombre no es confiable por variaciones de captura. **Pendiente confirmar** si ambos son obligatorios o si basta con uno.

#### SesionOTP
Mecanismo de autenticación sin contraseña (acordado en Junta 2).

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| persona_id | FK → Persona. |
| codigo_hash | Código OTP hasheado (un solo uso). |
| canal | `correo` / `sms`. |
| expira_en | Marca de tiempo de expiración. |
| usado | Booleano. |

#### RolPermiso
Los permisos administrativos son en dos niveles (acordado en Junta 2): **solo lectura** y **edición**, con un rol superior que ve todo.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| persona_id | FK → Persona. |
| modulo | `STD` / `EVE` / `TAL` / `*` (superadmin). |
| nivel | `lectura` / `edicion`. |

### Cómo lo usa cada dominio

| Dominio | Extensión de Persona |
|---------|---------------------|
| STD | `Editorial` — perfil de la entidad expositora (FK → Persona). |
| EVE | `Proponente` — perfil del proponente de actividad (FK → Persona). |
| TAL | `Tallerista` y `RepresentanteEscolar` — perfiles de TAL (FK → Persona). |

> [!important]
> Ningún dominio duplica los datos de Persona. Cada uno agrega solo los datos propios de su contexto.

### Regla de identidad cruzada

Si una misma persona tiene registros en EVE y TAL (caso: tallerista que también propone una conferencia), el sistema debe poder detectar que ambos perfiles corresponden a la misma Persona, para prevenir conflictos de horario entre módulos.

### Pendientes por validar (para el lunes)

- [ ] ¿Correo y teléfono son **ambos obligatorios**, o basta con uno?
- [ ] ¿Una Persona recién registrada puede iniciar el flujo de cualquier módulo, o debe esperar habilitación por parte de un admin?
- [ ] ¿Qué pasa si dos registros de distinto módulo tienen el mismo correo pero distinto teléfono?

---

## Core 2 — Programas

### Propósito

Proporcionar el **motor de calendarización** del sistema: la estructura de tiempo (bloques, horarios, recesos) y el **calendario maestro** que integra las actividades de EVE y los talleres/visitas de TAL en una sola vista de programación.

> [!note]
> STD **no** usa este core directamente. Los stands tienen su propio mapa y flujo de reserva. Sin embargo, una actividad de EVE puede ocurrir **en** un stand (caso RFH-33), lo que genera una referencia de solo lectura al mapa de STD.

### Entidades

#### EdicionFeria
La edición del año de la feria. Es la entidad raíz que todos los dominios referencian.

> [!note]
> Hugo llama a esta entidad `Evento` en el modelo de STD. Para evitar colisión con el dominio EVE (donde "evento" es una actividad), en el core se nombra `EdicionFeria`. **Se debe alinear con Hugo** que su `Evento` es esta misma entidad.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| nombre | P. ej. "FILEY 2026". |
| edicion | Número de edición (ej. XIV). |
| anio | Año de la edición. |
| fecha_inicio | Fecha de inicio de la feria. |
| fecha_fin | Fecha de fin de la feria. |
| sede | Recinto (ej. "Centro de Convenciones Yucatán Siglo XXI"). |
| estado | `configuracion` / `convocatoria` / `programacion` / `en_curso` / `cerrada`. |

#### BloqueHorario
Unidad mínima de tiempo en el calendario.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| edicion_id | FK → EdicionFeria. |
| fecha | Día del bloque. |
| hora_inicio | Hora de inicio del bloque. |
| hora_fin | Hora de fin del bloque (incluye colchón de transición). |
| duracion_actividad_min | Duración real de la actividad dentro del bloque (sin colchón). |
| tipo | `estandar` / `doble` / `cine`. |
| es_receso | Booleano — marca el receso de 14:00–16:00 (Hipólito) o 13:00–15:00 (Elvira). |

> [!note]
> Hipólito usa bloques de 1 h (o 1h15) donde la actividad dura 45-50 min. Los eventos masivos usan bloques de 2 h. Las salas de cine usan bloques de 2 h. El colchón entre actividades (~15 min) no aparece en el programa impreso pero sí bloquea tiempo en el sistema.

#### ProgramaMaestro
El agregado que integra EVE + TAL en una única vista de programación.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| edicion_id | FK → EdicionFeria. |
| version | Número de versión (el coordinador puede hacer varias iteraciones antes de publicar). |
| estado | `borrador` / `en_revision` / `publicado` / `definitivo`. |
| fecha_publicacion | Fecha en que se publicó esta versión. |
| publicado_por | FK → Persona (admin). |

> [!note]
> El coordinador puede iterar el programa varias veces (primera, segunda, tercera revisión) sin publicar ni notificar en cada ajuste intermedio. Solo cuando él decide que la versión está lista, cambia a `publicado`.

### Reglas de integración EVE ↔ TAL

- Los talleres de Elvira (TAL) que Hipólito decide **anexar al calendario maestro** de EVE aparecen en el ProgramaMaestro como entradas de tipo `taller_anexado`.
- Hipólito **no gestiona** la aprobación ni los horarios de los talleres — solo los anexa como referencia.
- **Pendiente por definir**: quién inicia el anexo (¿Elvira le pasa una lista? ¿Hipólito los jalala desde TAL?) y en qué formato.

### Pendientes por validar (para el lunes)

- [ ] ¿Cómo se transfiere un taller de TAL al calendario maestro de EVE? ¿Quién inicia esa acción?
- [ ] ¿El sistema debe detectar automáticamente conflictos de horario cuando un mismo tallerista tiene actividad en EVE y TAL?
- [ ] ¿La versión del programa se numera manualmente o el sistema la incrementa automáticamente?
- [ ] ¿El receso de Elvira (13:00–15:00) y el de Hipólito (14:00–16:00) deben modelarse como dos recesos independientes en el mismo día?

---

## Core 3 — Salas/Salones

### Propósito

Proporcionar un **catálogo compartido de espacios físicos** que tanto EVE (Hipólito) como TAL (Elvira) pueden reservar. Evita que cada módulo tenga su propia lista de salas con información desincronizada.

> [!note]
> Los **stands** del showfloor (STD) **no** forman parte de este catálogo — tienen su propio mapa de Godot. Sin embargo, cuando una actividad de EVE ocurre en el stand de una editorial (caso confirmado en programa 2026, RFH-33), la referencia al stand se toma del dominio STD como un campo especial, no de este catálogo.

### Entidades

#### Sala
Espacio físico reservable por EVE o TAL.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| edicion_id | FK → EdicionFeria (los nombres cambian cada edición). |
| nombre | Nombre del espacio (ej. "Salón Uxmal 3", "Ek Balam Norte"). |
| capacidad | Aforo máximo. |
| tipo | `salon` / `sala` / `mampara` / `cine` / `biblioteca` / `gran_foro`. |
| administrador | `hipolito` / `elvira` (quién gestiona este espacio). |
| accesible_desde | `EVE` / `TAL` / `EVE_TAL` (quién puede reservarla). |
| activa | Booleano. |
| notas | Observaciones (p. ej. "subdivisión con mamparas, capacidad 35-40"). |

### Espacios conocidos (a confirmar y completar con el cliente)

**Sistema de Hipólito (EVE):**
| Nombre | Tipo | Capacidad aprox. |
|--------|------|-----------------|
| Salón Uxmal 1 ("Gran Foro") | gran_foro | ~600 personas |
| Salón Uxmal 3 | salon | Por confirmar |
| Salón Uxmal 4 | salon | Por confirmar |
| Salón Dzibilchaltún | salon | Por confirmar |
| Sala Fernando del Paso (dentro de Chichén Itzá) | sala | Por confirmar |
| Sala Fernando Espejo (dentro de Chichén Itzá) | sala | Por confirmar |
| Sala Antonia Jiménez Trava (dentro de Chichén Itzá) | sala | Por confirmar |
| Sala de cine 1 | cine | ~130 personas |
| Sala de cine 2 | cine | ~130 personas |

**Sistema de Elvira (TAL, zona Ek Balam):**
| Nombre | Tipo | Capacidad aprox. |
|--------|------|-----------------|
| Ek Balam (subdivisiones con mamparas) | mampara | 35-40 por subdivisión |
| Sala de cine 1 | cine | ~130 personas |
| Sala de cine 2 | cine | ~130 personas |
| Biblioteca | biblioteca | Por confirmar |

> [!warning]
> Las salas de cine aparecen en ambos sistemas. Falta confirmar si son las **mismas** salas físicas administradas de forma distinta, o si son salas distintas.

> [!warning]
> Los nombres exactos de las subdivisiones de Ek Balam con mamparas son **desconocidos**. Es una pregunta abierta para la siguiente junta.

#### ReservaSala
El registro de que un espacio fue asignado a una actividad (de EVE o TAL) en un bloque de horario específico.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| sala_id | FK → Sala. |
| bloque_id | FK → BloqueHorario. |
| dominio_origen | `EVE` / `TAL` — qué dominio generó esta reserva. |
| entidad_id | ID de la actividad o taller que reservó la sala. |
| estado | `tentativa` / `confirmada` / `cancelada`. |

### Reglas de negocio

- Una sala no puede tener dos `ReservaSala` activas en el mismo bloque de horario (restricción de concurrencia compartida entre EVE y TAL).
- Hipólito puede reservar salas del sistema de Elvira (Uxmal 1) cuando necesita aforo grande para eventos masivos, y viceversa (confirmado en documentos de Software para agendar escuelas).
- En casos excepcionales se permite sobrecupo, pero se maneja con discreción y queda registrado como excepción.

### Pendientes por validar (para el lunes)

- [ ] ¿Cuántos espacios exactos tiene Elvira en Ek Balam? ¿Cómo se llaman las subdivisiones con mamparas?
- [ ] ¿Las salas de cine son las mismas físicamente para EVE y TAL, o son salas distintas?
- [ ] ¿Elvira puede reservar salas de Hipólito directamente en el sistema, o solo Hipólito puede hacer esa asignación?
- [ ] ¿Cómo se maneja el sobrecupo: el sistema lo bloquea completamente o solo emite una advertencia y permite al admin confirmarlo igual?

---

## Relación entre cores

```
EdicionFeria (Core Programas)
    │
    ├── STD usa edicion_id en: Aplicacion, Stand, Reserva
    ├── EVE usa edicion_id en: Propuesta, Actividad, ParametrosConvocatoria
    └── TAL usa edicion_id en: RegistroTallerista, RegistroVisitaEscolar

Persona (Core Registros)
    │
    ├── STD extiende con: Editorial
    ├── EVE extiende con: Proponente
    └── TAL extiende con: Tallerista, RepresentanteEscolar

Sala (Core Salas)
    │
    ├── EVE reserva via: ReservaSala (dominio_origen = EVE)
    └── TAL reserva via: ReservaSala (dominio_origen = TAL)
```

---

## Decisiones de diseño a tomar

Estos puntos requieren acuerdo del equipo antes de que cada dominio pueda implementar sus modelos de datos completos:

1. **Nombre canónico de `EdicionFeria`**: Alinear con Hugo que su entidad `Evento` = `EdicionFeria` del core, para que todos referencien lo mismo. (Hoy Hugo la llama `Evento`; cambiar el nombre en sus archivos o documentar el mapeo.)

2. **Obligatoriedad del teléfono**: ¿Correo o teléfono como identificador único, o los dos?

3. **Inicio del flujo de anexo EVE←TAL**: Definir explícitamente quién y cómo transfiere un taller al calendario maestro.

4. **Salas de cine compartidas**: Confirmar si son las mismas salas o distintas, para saber si hay un solo catálogo o dos.
