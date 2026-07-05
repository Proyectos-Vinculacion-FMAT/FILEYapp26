# Mapa de flujo — VIS (Visitas Escolares)

## Diagrama — Escuela / Participante (aplicantes/)

```mermaid
flowchart TD
    REG_CONV["REG/aplicantes/\nconvocatorias.html"]

    subgraph VIS_P["VIS · Escuela  (VIS/aplicantes/)"]
        VP_CONV["convocatoria-vis.html"]
        VP_FORM["formulario-vis.html"]
        VP_CONF["confirmacion-vis.html"]
        VP_MV["mi-visita.html"]
        VP_RES["reservar.html"]
        VP_ITN["itinerario.html"]
    end

    REG_CONV --> VP_CONV

    VP_CONV --> VP_FORM
    VP_FORM -->|enviar propuesta| VP_CONF
    VP_FORM -.->|cancelar| VP_CONV
    VP_CONF --> VP_RES
    VP_CONF -.->|topnav| VP_MV
    VP_MV --> VP_RES
    VP_RES --> VP_ITN
    VP_ITN -.->|seguir editando| VP_RES
    VP_ITN -->|confirmar| REG_CONV

    classDef ext fill:#f0f4ff,stroke:#6b7686,color:#3f4a5a
    class REG_CONV ext
```

**Nota:** al confirmar el itinerario, el participante regresa a `REG/aplicantes/convocatorias.html` (hub compartido).

---

## Diagrama — Administrador (administradores/)

```mermaid
flowchart TD
    REG_A["REG/administradores/\nadmin-convocatorias.html"]
    EVIDENCIA["VIS/talleres-preescolar.html\n⚠ ISLA — evidencia interna,\nnadie apunta aquí"]

    subgraph VIS_A["VIS · Administrador  (VIS/administradores/)"]
        VA_LOG["admin-login.html\natajo de prototipo"]
        VA_PROP["admin-propuestas.html\nhub principal"]
        VA_ESC["admin-escuela.html\nA3a — alta manual"]
        VA_EDIT["admin-escuela-edit.html\nA3d — editar datos"]
        VA_RES["admin-reservar.html\nA3b — reservar"]
        VA_ITN["itinerario-admin.html\nA3c — itinerario"]
    end

    REG_A --> VA_PROP
    VA_LOG --> VA_PROP

    VA_PROP --> VA_ESC
    VA_PROP --> VA_EDIT
    VA_PROP --> VA_RES

    VA_ESC -->|registrar y reservar| VA_RES
    VA_ESC -.->|cancelar| VA_PROP

    VA_EDIT -.->|cancelar| VA_PROP

    VA_RES --> VA_ITN
    VA_ITN -.->|volver| VA_PROP

    classDef island fill:#fbeae8,stroke:#CC311D,color:#73190B
    classDef ext fill:#f0f4ff,stroke:#6b7686,color:#3f4a5a
    classDef hub fill:#e6f0fa,stroke:#01457C
    class EVIDENCIA island
    class REG_A ext
    class VA_PROP hub
```

**`admin-login.html`:** es un atajo de prototipo para navegar VIS directamente; el flujo real siempre llega vía `REG/administradores/admin-convocatorias.html`.

---

## Hallazgos

| Severidad | Archivo | Problema |
| --------- | ------- | -------- |
| 🔴 Isla | `VIS/talleres-preescolar.html` | Ningún archivo del prototipo apunta a él. Sin salidas de navegación. Es un archivo de evidencia interna (Acción A2 del análisis de desalineación). |
| ℹ️ Nota | `VIS/administradores/admin-login.html` | Atajo de prototipo: proto-bar muestra A1 (activo) + A2. Módulos + A3/A3a/A3b como links. El flujo real siempre entra vía `REG/administradores/admin-convocatorias.html → admin-propuestas.html`. |
| ℹ️ Nota | `VIS/aplicantes/itinerario.html` | Al confirmar, redirige a `REG/aplicantes/convocatorias.html` (sale de VIS al hub compartido). Esperado. |
| ℹ️ Nota | `VIS/aplicantes/mi-visita.html` | Accesible desde `REG/aplicantes/convocatorias.html` (tarjeta de la convocatoria VIS) y desde topnav en formulario/confirmacion — no solo desde el flujo secuencial. |

---

## Tablas de pantallas

### Escuela (Participante)

| # | Pantalla | Archivo | CU |
| - | -------- | ------- | -- |
| 1–4 | Acceso + convocatorias | *(ver REG — Participante)* | — |
| 5 | Info convocatoria VIS | `aplicantes/convocatoria-vis.html` | — |
| 6 | Registrar mi escuela (propuesta) | `aplicantes/formulario-vis.html` | CU-VIS-001 |
| 7 | Confirmación con folio | `aplicantes/confirmacion-vis.html` | — |
| 8 | Mi registro (detalle de la visita) | `aplicantes/mi-visita.html` | CU-VIS-003 |
| 9 | Reservar talleres (catálogo) ⚠ | `aplicantes/reservar.html` | CU-VIS-010 / 011 / 012 |
| 10 | Ver / confirmar itinerario | `aplicantes/itinerario.html` | CU-VIS-013 / 014 |

> **⚠ Brecha C1+C4:** catálogo no filtra por nivel educativo. Ver análisis de desalineación de CUs.

### Administrador

| # | Pantalla | Archivo | CU |
| - | -------- | ------- | -- |
| A1–A2 | Acceso + módulos | *(ver REG — Administrador)* | — |
| — | Acceso directo VIS (atajo prototipo) | `administradores/admin-login.html` | CU-REG-003 |
| A3 | Propuestas — lista + dictamen inline | `administradores/admin-propuestas.html` | CU-VIS-004–009 / 015–017 |
| A3a | Alta manual de escuela | `administradores/admin-escuela.html` | CU-VIS-016 |
| A3b | Reservar talleres (por la escuela) | `administradores/admin-reservar.html` | CU-VIS-010 / 011 / 012 |
| A3c | Itinerario de visita (admin) | `administradores/itinerario-admin.html` | CU-VIS-013 / 014 |
| A3d | Editar datos de escuela | `administradores/admin-escuela-edit.html` | CU-VIS-016 / 017 |

---

## CSS

| Capa | Archivo |
| ---- | ------- |
| Base | `../common/styles-base.css` |
| Dominio | `VIS/styles.css` — base + tokens `--vis-*`, componentes VIS |

Todas las pantallas de `VIS/` cargan únicamente `../styles.css`.
