# Mapa de flujo — EVT (Eventos)

## Diagrama — Proponente (aplicantes/)

> El flujo real entra por REG. Los pasos 1–4 (acceso, registro, OTP, convocatorias) ocurren en REG.
> Los atajos de prototipo (`acceso-evt.html`, `registro.html`, `otp.html`) permiten navegar EVT directamente.

```mermaid
flowchart TD
    REG_IDX["REG/aplicantes/aplicantes-login.html"]
    REG_CONV["REG/aplicantes/\nconvocatorias.html"]

    subgraph EVT_ATAJOS["Atajos de prototipo EVT"]
        EP_ACC["aplicantes/acceso-evt.html\natajo de prototipo"]
        EP_REG["aplicantes/registro.html\natajo de prototipo"]
        EP_OTP["aplicantes/otp.html\natajo de prototipo"]
    end

    subgraph EVT_P["EVT · Proponente  (EVT/aplicantes/)"]
        EP_CONV["convocatoria-eventos.html"]
        EP_FORM["formulario.html"]
        EP_CONF["confirmacion.html"]
        EP_MIS["mis-propuestas.html"]
    end

    REG_IDX --> EP_ACC
    REG_CONV --> EP_CONV

    EP_ACC -->|correo nuevo| EP_REG
    EP_ACC -->|correo conocido| EP_OTP
    EP_REG --> EP_OTP
    EP_OTP --> REG_CONV

    EP_CONV --> EP_FORM
    EP_FORM -->|enviar| EP_CONF
    EP_FORM -.->|cancelar| EP_CONV
    EP_CONF -->|ver mis propuestas| EP_MIS
    EP_CONF -.->|otra propuesta| EP_FORM
    EP_MIS -.->|nueva propuesta| EP_CONV

    classDef shortcut fill:#fdf6e3,stroke:#b8860b,color:#6e4d03
    classDef ext fill:#f0f4ff,stroke:#6b7686,color:#3f4a5a
    class EP_ACC,EP_REG,EP_OTP shortcut
    class REG_IDX,REG_CONV ext
```

---

## Diagrama — Administrador (administradores/)

> El sidebar conecta: propuestas ↔ notificaciones ↔ programa ↔ seguimiento ↔ configuracion (malla completa — flechas grises).
> `admin-evt-horario.html` no está en el sidebar; se accede desde programa o programar.
> Atajos de prototipo (amarillo): EVT/administradores/{admin-registro, admin-otp, admin-modulos} permiten navegar el panel sin pasar por REG.

```mermaid
flowchart TD
    REG_ALOG["REG/administradores/admin-login.html"]
    REG_AMOD["REG/administradores/admin-convocatorias.html"]
    STD_A["STD/#/admin/aplicaciones"]

    subgraph EVT_A["EVT · Administrador  (EVT/administradores/)"]
        EA_REG["admin-registro.html\natajo de prototipo"]
        EA_OTP["admin-otp.html\natajo de prototipo"]
        EA_MOD["admin-modulos.html\natajo de prototipo"]

        subgraph PANEL["Panel EVT"]
            EA_PROP["admin-evt-propuestas.html"]
            EA_DET["admin-evt-detalle-propuesta.html"]
            EA_REC["admin-evt-detalle-rechazada.html"]
            EA_HOR["admin-evt-horario.html"]
            EA_PRG["admin-evt-programa.html"]
            EA_PGR["admin-evt-programar.html"]
            EA_NOT["admin-evt-notificaciones.html"]
            EA_SEG["admin-evt-seguimiento.html"]
            EA_CFG["admin-evt-configuracion.html"]
        end
    end

    REG_ALOG --> EA_REG
    REG_AMOD --> EA_PROP

    EA_REG --> EA_OTP
    EA_OTP --> EA_MOD
    EA_MOD --> EA_PROP
    EA_MOD --> STD_A

    EA_PROP --> EA_DET
    EA_PROP --> EA_PGR
    EA_PROP --> EA_REC

    EA_DET -.->|volver| EA_PROP
    EA_REC -.->|volver| EA_PROP

    EA_PRG <-->|chip tabs| EA_HOR
    EA_PRG --> EA_PGR
    EA_PGR -->|ir tablero| EA_HOR
    EA_PGR -.->|volver lista| EA_PRG

    %% Panel → REG (topbar Módulos ↖)
    EA_PROP -.->|Módulos ↖| REG_AMOD
    EA_NOT -.->|Módulos ↖| REG_AMOD
    EA_PRG -.->|Módulos ↖| REG_AMOD

    %% Sidebar: malla completa entre los 5 nodos del panel
    EA_PROP --- EA_NOT
    EA_PROP --- EA_PRG
    EA_PROP --- EA_SEG
    EA_PROP --- EA_CFG
    EA_NOT --- EA_PRG
    EA_NOT --- EA_SEG
    EA_NOT --- EA_CFG
    EA_PRG --- EA_SEG
    EA_PRG --- EA_CFG
    EA_SEG --- EA_CFG

    classDef shortcut fill:#fdf6e3,stroke:#b8860b,color:#6e4d03
    classDef ext fill:#f0f4ff,stroke:#6b7686,color:#3f4a5a
    class EA_REG,EA_OTP,EA_MOD shortcut
    class REG_ALOG,REG_AMOD,STD_A ext
```

**Líneas sin flecha (`---`):** sidebar de navegación lateral — todos los nodos enlazados en ambas direcciones.
**Flechas punteadas al techo (`-.->`):** acceso rápido desde topbar o proto-bar.

---

## Hallazgos

| Severidad | Archivo | Situación |
| --------- | ------- | --------- |
| ✅ Resuelto | `EVT/index.html` → `selector-rol.html` | Renombrado a nombre descriptivo. Actualizado admin-link → REG/admin-login. |
| ✅ Resuelto | `EVT/aplicantes/index.html` → `acceso-evt.html` | Renombrado. Auth-foot admin → REG/admin-login. Proto-bar marca atajo de prototipo. |
| ✅ Resuelto | `REG/aplicantes/index.html` → `aplicantes-login.html` | Renombrado. 37 HTML y 6 md actualizados. |
| ✅ Resuelto | Proto-bar en panel EVT | Todos los 9 archivos del panel tienen proto-bar A1→A2→A3…A7 (todas las secciones siempre visibles; sección activa en `<b>`). CU incluidos en la sección activa. |
| ✅ Resuelto | Topbar panel EVT | Topbar muestra solo "Configuración". El escape hacia REG está en la proto-bar como "Módulos ↗". |
| ℹ️ Atajo prototipo | `admin-registro.html`, `admin-otp.html`, `admin-modulos.html` | Permiten navegar el panel sin pasar por REG. Auth-foot corregido → REG/aplicantes/aplicantes-login.html. |
| ℹ️ Sin sidebar | `admin-evt-horario.html` | No aparece en el sidebar del panel. Se accede desde `admin-evt-programa.html` (chip tab) o `admin-evt-programar.html` (botón). |

---

## Tablas de pantallas

### Proponente

| # | Pantalla | Archivo | CU |
| - | -------- | ------- | -- |
| 1–4 | Acceso + convocatorias | *(ver REG — Participante)* | — |
| — | Acceso EVT (atajo prototipo) | `aplicantes/acceso-evt.html` | — |
| — | Registro (atajo prototipo) | `aplicantes/registro.html` | — |
| — | Código OTP (atajo prototipo) | `aplicantes/otp.html` | — |
| 5 | Info convocatoria Eventos | `aplicantes/convocatoria-eventos.html` | CU-EVE-001 |
| 6 | Formulario de propuesta | `aplicantes/formulario.html` | CU-EVE-002 / 003 |
| 7 | Confirmación con folio | `aplicantes/confirmacion.html` | CU-EVE-002 |
| + | Mis propuestas (seguimiento) | `aplicantes/mis-propuestas.html` | CU-EVE-036 |

### Administrador

| # | Pantalla | Archivo | CU |
| - | -------- | ------- | -- |
| A1–A2 | Acceso + módulos | *(ver REG — Administrador)* | — |
| — | Acceso admin (atajo prototipo) | `administradores/admin-registro.html` | — |
| — | OTP admin (atajo prototipo) | `administradores/admin-otp.html` | — |
| — | Módulos EVT (atajo prototipo) | `administradores/admin-modulos.html` | — |
| A3 | Propuestas — lista y dictamen | `administradores/admin-evt-propuestas.html` | CU-EVT-007 / 011 |
| A3a | Detalle de propuesta + dictamen | `administradores/admin-evt-detalle-propuesta.html` | CU-EVT-008 / 009 / 012 |
| A3b | Detalle propuesta rechazada (lectura) | `administradores/admin-evt-detalle-rechazada.html` | CU-EVT-008 |
| A4 | Notificaciones en lote | `administradores/admin-evt-notificaciones.html` | CU-EVT-010 |
| A5 | Lista del programa | `administradores/admin-evt-programa.html` | — |
| A5a | Tablero de programación | `administradores/admin-evt-horario.html` | CU-PRG-001 / 002 / 008 |
| A5b | Asignar sala / bloque | `administradores/admin-evt-programar.html` | CU-PRG-002 / 003 / 004 |
| A6 | Seguimiento (contadores) | `administradores/admin-evt-seguimiento.html` | CU-EVT-011 |
| A7 | Configuración (fechas + cupos) | `administradores/admin-evt-configuracion.html` | CU-EVT-001 |

---

## CSS

| Capa | Archivo |
| ---- | ------- |
| Base | `../common/styles-base.css` |
| Dominio | `EVT/styles.css` — base + panel admin completo (sidebar, modales, rejilla, tablero) |

Todas las pantallas de `EVT/` cargan únicamente `../styles.css`.
