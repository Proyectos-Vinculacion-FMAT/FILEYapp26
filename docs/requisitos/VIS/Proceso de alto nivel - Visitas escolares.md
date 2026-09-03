---
estado: propuesta
version: 0.1
tags:
  - tipo/proceso
  - dom/vis
fecha: 2026-06-30
---
# Proceso de alto nivel — Visitas escolares (VIS)

El dominio **VIS** cubre el ciclo completo de una visita escolar: desde que una institución
registra su propuesta hasta que recibe por correo su itinerario confirmado con talleres
reservados. El proceso se divide en dos etapas: **A. Propuesta y dictamen** (quien aplica ↔ admin)
y **C. Catálogo y reserva de talleres** (el Participante arma su itinerario autónomamente una
vez aceptado).

Los grupos de una escuela **no son editables una vez registrada la propuesta**; la institución
sólo puede modificarlos si el Admin emite una *Solicitud de cambios*. Cada propuesta registra
entre 1 y 3 grupos de hasta 35 alumnos cada uno (máximo 105 por visita).

---

## Proceso general (punta a punta)

```mermaid
%% Proceso de alto nivel: Visitas Escolares (VIS) — FILEY
flowchart TD
    CAT[/Catálogo de talleres final\npublicado por PRG/] --> PA

    PA([Aplicante envía propuesta\nescuela · CCT · nivel · grupos · contacto]) --> PEN[Propuesta PENDIENTE]
    PEN --> REV{Admin revisa\nla propuesta}
    REV -->|Solicita cambios| SC[/Sistema notifica observaciones\nal Aplicante/]
    SC --> ED([Aplicante edita y reenvía\ngrupos son los mismos, solo\ncorrige lo señalado])
    ED --> PEN
    REV -->|Rechaza con motivo| REJ[Propuesta RECHAZADA]
    REJ --> NOT_REJ[/Sistema notifica rechazo/]
    REV -->|Acepta| ACE[Propuesta ACEPTADA\nAplicante → Participante]
    ACE --> NOT_ACE[/Sistema notifica aceptación\ny activa acceso al catálogo/]

    NOT_ACE --> CATV([Participante consulta catálogo\nfiltrado por nivel educativo, día y turno])
    CATV --> SEL([Participante elige taller\ny asigna qué grupo o grupos asistirán])
    SEL --> VAL{¿Cupo restante\ncubre el grupo elegido?}
    VAL -->|No — cupo insuficiente| CATV
    VAL -->|Sí| RES[Taller reservado en itinerario]
    RES --> MAS{¿Agregar otro taller\no ajustar el itinerario?}
    MAS -->|Agregar| CATV
    MAS -->|Quitar un taller| QUIT([Participante quita taller del itinerario\nse libera el cupo])
    QUIT --> MAS
    MAS -->|Itinerario listo| EMAIL[/Sistema envía correo automático\nItinerario · Carta de confirmación · Reglamento/]
    EMAIL --> DONE([Visita escolar programada])

    classDef participante fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef admin fill:#fef3c7,stroke:#d97706,color:#7c2d12;
    classDef sistema fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef fin fill:#f3f4f6,stroke:#6b7280,color:#111827;

    class PA,ED,SEL,QUIT,CATV participante;
    class REV admin;
    class PEN,SC,NOT_REJ,ACE,NOT_ACE,VAL,RES,MAS,EMAIL sistema;
    class CAT,REJ,DONE,NOT_REJ fin;
```

---

## Vista del Participante (institución / escuela)

Solo las acciones e interacciones que realiza la institución, desde que envía la propuesta
hasta que recibe el correo con su itinerario.

```mermaid
%% Vista Participante — VIS
flowchart TD
    A([Completa el formulario de propuesta\nescuela · CCT · nivel educativo\ngrupos · representante · contacto]) --> B[Propuesta enviada\nqueda en estado PENDIENTE]
    B --> C{Consulta el estado\nde su propuesta}
    C -->|Solicitud de cambios| D([Edita la propuesta según la observación\nlos grupos no cambian si no hay instrucción\nexplícita de corregirlos])
    D --> B
    C -->|Rechazada| E([Trámite cerrado])
    C -->|Aceptada| F([Accede al catálogo de talleres\nfiltrado por su nivel educativo])
    F --> G([Selecciona taller y decide\nqué grupo o grupos de los suyos asistirán])
    G --> H{¿El cupo restante del taller\ncubre la cantidad de alumnos\ndel grupo elegido?}
    H -->|No — cupo insuficiente o cerrado| F
    H -->|Sí| I[Taller añadido al itinerario]
    I --> J{¿Ajustar el itinerario?}
    J -->|Agregar otro taller| F
    J -->|Quitar un taller reservado| K([Elimina el taller\nel cupo queda disponible para otras escuelas])
    K --> J
    J -->|Itinerario listo| L[/Recibe correo automático con\nsu itinerario · carta de confirmación · reglamento/]
    L --> M([Visita confirmada])

    classDef participante fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef sistema fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef fin fill:#f3f4f6,stroke:#6b7280,color:#111827;

    class A,D,F,G,K participante;
    class B,C,H,I,J,L sistema;
    class E,M fin;
```

---

## Vista del Administrador

Solo las acciones que realiza la coordinación: dictar propuestas, consultar visitas aceptadas
y gestionar las reservaciones de cada escuela.

```mermaid
%% Vista Administrador — VIS
flowchart TD
    A([Consulta lista de propuestas pendientes\ncon filtros por estado · nivel · fecha]) --> B([Abre el detalle de una propuesta])
    B --> C{Dictamen}
    C -->|Rechaza con motivo| D[/Sistema notifica el rechazo\nal Aplicante/]
    C -->|Solicita cambios| E[/Sistema notifica las observaciones\nal Aplicante/]
    E --> F[Espera el reenvío\nde la propuesta corregida]
    F --> B
    C -->|Acepta| G[/Sistema notifica la aceptación\ny activa el acceso al catálogo/]
    D --> MAS_PROP{¿Más propuestas\npendientes?}
    G --> MAS_PROP
    MAS_PROP -->|Sí| A
    MAS_PROP -->|No por ahora| VIS

    VIS([Consulta lista de visitas escolares aceptadas\nfiltrable por escuela · taller · fecha]) --> DET([Abre el detalle de una visita\nescuela · grupos registrados · talleres reservados])
    DET --> ACC{Acción\nrequerida}
    ACC -->|Sin cambios| VIS
    ACC -->|Baja por cancelación imprevista| QUIT([Quita manualmente la visita de un taller\nel cupo queda libre])
    ACC -->|Editar reservaciones de la escuela| EDIT([Modifica asignación:\nagregar taller · cambiar grupo asignado\n· quitar participación])
    QUIT --> VIS
    EDIT --> VIS

    classDef admin fill:#fef3c7,stroke:#d97706,color:#7c2d12;
    classDef sistema fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef fin fill:#f3f4f6,stroke:#6b7280,color:#111827;

    class A,B,F,VIS,DET,QUIT,EDIT admin;
    class C,D,E,G,MAS_PROP,ACC sistema;
```

---

## Notas del proceso

### Grupos fijos desde el registro

La institución registra sus grupos al momento de enviar la propuesta (mínimo 1, máximo 3,
de hasta 35 alumnos cada uno). Esos grupos **no pueden modificarse unilateralmente** una vez
enviada la propuesta; solo cambian si el Admin emite una *Solicitud de cambios* que
explícitamente lo indique.

### Selección de talleres por grupo

Al reservar un taller, el Participante elige **cuál o cuáles de sus grupos asistirán**. Un grupo
puede estar en un taller y otro en otro de forma simultánea. El sistema valida que el cupo
restante del taller cubra la cantidad de alumnos del grupo elegido antes de confirmar la reserva.

### Vista del catálogo (layout lateral)

El catálogo de talleres se presenta como una columna lateral de salas disponibles; cada sala
muestra una página por día y dentro de la página los talleres ordenados por columna horaria
(matutino / vespertino). Filtros activos: nivel educativo, día y turno.

### Edición administrativa de reservaciones (CU-VIS-017)

El Admin no solo puede dar de baja una visita de un taller (baja por cancelación); también
puede **editar las reservaciones activas** de una escuela ya aceptada: agregar un taller
nuevo, cambiar qué grupo asiste a uno existente, o quitar completamente su participación
en un taller para liberar el cupo.

### Pendiente: ludoteca sin taller programado

Queda por confirmar cuáles son las condiciones para que una escuela pueda reservar la
ludoteca cuando esta no tenga un taller programado en el período de la visita.

### Pendiente: validación previa al acceso al catálogo

Se asume que existe alguna forma de validación o aprobación (la aceptación de la propuesta)
antes de que la escuela pueda reservar talleres, pero el mecanismo exacto de cómo una
Programación de `PRG` pasa de preliminar a **final** (y por tanto visible en el catálogo VIS)
está pendiente de definir.

### Artefactos relacionados

- [`CU-VIS Índice.md`](CU-VIS%20Índice.md) — inventario de casos de uso por módulo.
- [`Modelo de datos - Visitas escolares.md`](Modelo%20de%20datos%20-%20Visitas%20escolares.md) — entidades y datos que el sistema almacena.
