---
estado: propuesta
version: 0.1
tags:
  - tipo/proceso
  - dom/tal
fecha: 2026-06-29
---
# Proceso de alto nivel — Talleres (actividades infantiles y juveniles)

Diagrama del flujo de punta a punta: desde que **abre la convocatoria** de Elvira hasta que
el catálogo de talleres queda **publicado para `VIS`**, incluyendo la rama de dictamen, la
programación delegada a `PRG` y las constancias.

> [!warning] Corrección directa del cliente (2026-06-29)
> Una versión anterior de este proceso asumía selección manual fuera del sistema, sin
> dictamen. El cliente confirmó que Elvira **sí dictamina cada propuesta en el sistema**, igual
> que Hipólito en `EVT`. Este diagrama refleja esa corrección.

El color de cada nodo indica quién interviene: Tallerista, Administradora (Elvira), Sistema y estados finales.

```mermaid
%% Proceso de alto nivel: Talleres (TAL) — FILEY
flowchart TD
    A([Elvira abre convocatoria\ny configura fechas y modalidades]) --> B[/Convocatoria abierta/]
    B --> C([Tallerista envía propuesta\ncon datos del evento y de la presentación])
    C --> D[Propuesta en estado PENDIENTE]
    D --> E{¿Convocatoria\naún abierta?}
    E -->|Sí| C2([Tallerista puede enviar\nmás propuestas])
    C2 --> D
    E -->|No, venció la fecha| F[Sistema cierra convocatoria]

    F --> G[Elvira revisa propuestas]
    G --> H{Dictamen por propuesta}
    H -->|Rechazada con motivo| I[Propuesta RECHAZADA]
    H -->|Cambios solicitados| J[Propuesta CAMBIOS_SOLICITADOS\nnotificación inmediata]
    J --> K([Tallerista edita y reenvía])
    K --> D
    H -->|Aceptada| L[Propuesta ACEPTADA\nActividad creada SIN horario]

    I --> M[Elvira decide notificar\nresultados en lote]
    L --> N[Elvira asigna sala y horario\nen su panel de PRG]
    M --> N

    N --> O[Programación en estado PRELIMINAR]
    O --> P[Sistema notifica al tallerista\nsu sala y horario preliminares]
    P --> Q{¿Tallerista responde\ndentro de la ventana?}
    Q -->|Acepta| R[RespuestaProgramación: aceptada]
    Q -->|Rechaza con motivo| S[RespuestaProgramación: rechazada]
    S --> T[Elvira ajusta la programación\nfuera del sistema, con el tallerista]
    T --> N

    R --> U{¿Elvira sigue\najustando el programa?}
    U -->|Sí, hay huecos o cambios| N
    U -->|No, queda listo| V[Programación pasa a FINAL]

    V --> W[/Catálogo de esa actividad\nse publica para VIS/]
    V --> X[/Tallerista puede descargar\nsu constancia, post-feria/]

    classDef tallerista fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef admin fill:#fef3c7,stroke:#d97706,color:#7c2d12;
    classDef sistema fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef fin fill:#f3f4f6,stroke:#6b7280,color:#111827;

    class C,C2,K,Q tallerista;
    class A,G,H,M,N,T,U admin;
    class B,D,E,F,J,L,O,P,R,S,V,W,X sistema;
    class I fin;
```

---

## Notas del proceso

### Dictamen idéntico a EVT, programación delegada a PRG

A diferencia de `EVT`, `TAL` no asigna categoría (literaria/académica × UADY/externa) al
aceptar — el resto del ciclo de dictamen es igual. La asignación de sala y horario **no es un
proceso propio de `TAL`**: ocurre en el panel de Elvira dentro de `PRG` (ver
`PRG/Proceso de alto nivel...` — pendiente de escribir un documento equivalente en `PRG` — y
`PRG/CU-PRG Índice.md`).

### Preliminar → final → publicación a VIS

El programa de talleres pasa por un estado preliminar (recién asignado, notificado, sujeto a
ajustes) antes de quedar final. **`VIS` solo consume el catálogo una vez que el horario es
final** (precisión directa del cliente, 2026-06-29): mientras sea preliminar, esa actividad no
aparece en el catálogo de talleres disponibles para visitas escolares (CU-VIS-010), aunque ya
tenga sala y bloque asignados. El mecanismo exacto para marcar un horario como "final" queda
pendiente de definir (ver "Temas abiertos" en `PRG/Modelo de datos - Programación.md`).

### Constancias obligatorias

A diferencia de `EVT` (constancia opcional, declarada por el proponente), en `TAL` el
tallerista declara desde el registro (CU-TAL-002) los nombres de quienes recibirán constancia,
sin opción de omitirlo — la generación es siempre automática (ver CU-TAL-005).

### Artefactos relacionados

- [`Modelo de datos - Talleres.md`](<Modelo de datos - Talleres.md>) — entidades y datos que el sistema almacena.
- [`CU-TAL Índice.md`](<CU-TAL Índice.md>) — inventario de casos de uso por sección.
- [`PRG/Modelo de datos - Programación.md`](<../PRG/Modelo de datos - Programación.md>) — entidades de la programación delegada.
