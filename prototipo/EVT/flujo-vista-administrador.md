# Flujo — Vista del Administrador (EVT) · v2

> Recorrido de pantallas y lógica de la **vista del administrador del módulo de Eventos**,
> para construir el prototipo estático. Basado en los CU de `REG`, `EVT` y `PRG` en
> `docs/requisitos/`, el prototipo del proponente (`prototipo/EVT/*.html`), el panel admin ya
> construido en `prototipo/STD/.../features/admin` (sidebar de referencia) y la grabación
> **"Standard recording 8 (mp3cut.net)"**.
>
> **Decisiones tomadas por el equipo (esta versión):**
> 1. El administrador entra por **OTP** (igual que el aplicante), no por contraseña. Ya se
>    actualizó **CU-REG-003** a OTP. En el prototipo se etiqueta como decisión de equipo.
> 2. Se modela a **Hipólito como administrador general** (`modulo = *`): al entrar ve los **3
>    módulos** (Eventos, Infantil/Juvenil, Stands), pero **solo Eventos es navegable**. Los
>    otros dos aparecen deshabilitados ("Próximamente"). Solo se maqueta la vista de Eventos.
> 3. Se define **CU-REG-006** para la pantalla de selección de módulo (ver `docs/requisitos/REG/`).
> 4. La gestión de usuarios administrativos (CU-REG-005) queda **fuera** de esta maqueta.
> 5. El re-dictamen (CU-EVT-009 A3) queda **pendiente para la siguiente versión**.
> 6. **Se incluye la etapa de programación (`PRG`)**: una vez aceptada una propuesta, se programa
>    (sala + bloque de horario) desde el mismo panel. Ver "Etapa de programación" abajo.

## Recorrido completo

```
index.html  (correo)
   → enlace "Acceso administrativo"           [se activa el link que hoy es href="#"]
otp.html  (código de 6 dígitos)               [MISMO OTP que el aplicante — etiqueta "demo"]
   ↓
Selección de módulo  (CU-REG-006)             [3 tarjetas; solo "Eventos" entra]
   ↓
PANEL ADMIN EVT (con sidebar)
   ├── Propuestas ............ revisar → dictaminar → (al aceptar) programar   [CU-EVT-007/008/009 + CU-EVT-012]
   ├── Programa / Horario .... ver y armar el calendario, notificar horario    [CU-PRG-001/002/003/004/008]
   ├── Notificaciones ........ avisar resultados (aceptada/rechazada) en lote   [CU-EVT-010]
   ├── Seguimiento ........... contadores por estado y cupos por categoría      [CU-EVT-011]
   └── Configuración ......... fechas y cupos de la convocatoria                [CU-EVT-001]
```

## Pantallas de acceso (reusadas del proponente, con etiqueta "demo")

| # | Pantalla | Qué cambia respecto al proponente | CU |
|---|----------|-----------------------------------|----|
| 1 | `index.html` | Se activa el enlace **"¿Eres parte del comité organizador? Acceso administrativo"** (hoy `href="#"`) para que lleve al OTP admin | — |
| 2 | `otp.html` (variante admin) | Mismo código de 6 dígitos, 15 min. Cintillo: *"Demo: acceso admin por OTP — decisión de equipo, sustituye la contraseña de CU-REG-003"* | CU-REG-003 (ya en OTP) |
| 3 | **Selección de módulo** | Nueva. Reusa el diseño de tarjetas de `convocatorias.html`, pero las 3 tarjetas entran al **panel admin**; solo Eventos es navegable | **CU-REG-006** |

> El administrador **no** captura nombre/teléfono: su cuenta la provisiona el administrador
> general (CU-REG-005), no se auto-registra. Por eso no hay `registro.html` en este flujo.

## Panel admin EVT — sidebar

El admin **sí lleva sidebar** (a diferencia del proponente, que "lo usa una vez"): en la
grabación se acordó *"mantenerlo en el Sidebar… el Sidebar para el administrador"*. El panel
de STD ya construyó ese patrón (`admin-layout.component.ts`). Secciones para EVT:

### 1. Propuestas — revisión, dictamen y disparo de la programación
- Lista filtrable: folio, actividad, proponente, tipo, categoría, estado, fecha; filtros por
  tipo/estado/categoría + buscador. → **CU-EVT-007**
- **Detalle** de una propuesta: datos del proponente, datos de la actividad, adjuntos,
  antecedentes de cambios. Si es "Presentación de libro/revista", checkbox de **ejemplar
  físico recibido**. → **CU-EVT-008 + CU-EVT-012**
- **Dictamen** desde el detalle: Aceptar (pide clasificar `literaria`/`academica`) / Solicitar
  cambios (mensaje obligatorio, notifica de inmediato) / Rechazar (motivo obligatorio).
  → **CU-EVT-009**
- **Clave del enganche con programación:** el botón del renglón cambia según el estado. Mientras
  la propuesta está pendiente → **"Revisar"**. En cuanto se **Acepta** → ese mismo botón pasa a
  **"Programar"**. No se puede programar sin aceptar antes. (Nota del índice de `EVT` y de `PRG`.)

### 2. Programa — etapa de programación (`PRG`) · **diseño híbrido compartido Hipólito/Elvira**

> **Decisión de diseño (v3):** la programación se arma en un **tablero híbrido** con la rejilla
> salas × bloques como lienzo principal (más un riel lateral de "Por programar"); la **lista**
> queda como vista alterna (móvil y "todas las ocasiones de una actividad", CU-PRG-002 A2). El
> modal de asignación imita el diálogo **"Nuevo evento" de Outlook**: formulario a la izquierda
> (actividad, fecha/bloque, sala) + **mini-calendario de día** a la derecha con el bloque ubicado.
>
> **Alcance de esta maqueta: solo la vista de Hipólito (Eventos).** Elvira **no** ve el programa
> de Hipólito ni al revés: cada quien entra a su propio panel (Hipólito → Eventos; Elvira →
> Talleres, su propio módulo, aún **no maquetado**). No hay "switch de panel" en la UI —eso rompería
> la separación—. Lo que **sí** se conserva es que ambos paneles se construyen sobre la **misma
> base de diseño**: cuando se maquete el de Elvira, reusa este esqueleto parametrizado, sin
> reinventarlo.
>
> ⚠️ **Maqueta vs. UI real:** en la **aplicación real se arrastra** la actividad desde el riel
> hasta el bloque (patrón resource-view tipo pretalx/FullCalendar), y el bloque verde del diálogo
> se estira como en Outlook. En **esta maqueta estática se hace clic** (primero la actividad,
> luego el bloque → modal de confirmación) y el bloque es **fijo de 1:15**. Solo se difiere la
> *física del arrastre*; el layout y el flujo son los definitivos. El tablero lleva un **banner**
> que lo aclara, y el modal de asignación lo repite.
>
> **Base compartida — qué es idéntico** (para cuando se construya el panel de Elvira): sidebar,
> riel de aceptadas por programar, rejilla salas × bloques, empalme no bloqueante (bloquea
> notificar, no guardar), guardado implícito (sin botón "guardar"), notificar en lote, y el
> diálogo de asignación estilo Outlook.
>
> **Base compartida — qué cambia según `panel`** (una sola variable de configuración; hoy solo se
> maqueta la columna de Eventos):
>
> | Parámetro | Eventos (Hipólito) — **maquetado** | Talleres (Elvira) — pendiente de maquetar |
> |---|---|---|
> | Duración de bloque | 1:15 | 1:00 (50 min + 10 de descanso) |
> | Repetir una actividad | No (0–1 programación) | **Sí** (N ocasiones para llenar huecos, CU-PRG-002 A1) — badge "ocasión N de M" |
> | Sala | Salón completo (1 sala) | **Sub-salas**: un salón se subdivide en salas A/B/C en paralelo (`SAL`), cada columna con su aforo |
> | Aforo | No se muestra | Se muestra por sala (👥); el cupo real lo valida `VIS`, `PRG` solo lo exhibe |
>
> **Pantallas (solo Eventos):** `admin-evt-horario.html` (tablero híbrido + diálogo Outlook),
> `admin-evt-programa.html` (lista alterna) y `admin-evt-programar.html` (formulario de una
> actividad y sus ocasiones). El tablero de Talleres se maquetará en el panel propio de Elvira.


Es la vista de armado del calendario del programa, y el botón de **visualización del horario**
que menciona el índice de `PRG`. Aquí:
- Se listan las actividades **aceptadas** con su estado de programación (*pendiente* /
  *programada*), filtrables por tipo, salón y sala. → **CU-PRG-001**
- **Programar** una actividad: elegir **sala** + **uno o varios bloques** de horario. En el
  panel de Eventos el bloque es fijo de **1:15** (hardcodeado; no se configura). Si necesita más
  tiempo, ocupa el siguiente bloque completo. → **CU-PRG-002**
- **Editar** (= mover a otra sala/bloque) y **Eliminar** una programación (libera la sala; si
  era la única, la actividad vuelve a *pendiente*). → **CU-PRG-003 / CU-PRG-004**
- **Alerta de empalme**: si dos actividades chocan en la misma sala/bloque, se marca pero **no
  bloquea**; debe resolverse antes de notificar. → CU-PRG-002 E1
- **Notificar horario** al participante (segunda notificación: fecha, sala, horario), por
  actividad o de forma masiva, a discreción del admin. → **CU-PRG-008**
- Guardado **implícito**: no hay botón de "guardar el programa"; cada cambio queda guardado.

### 3. Notificaciones — resultados de selección en lote
- Propuestas `aceptada`/`rechazada` pendientes de avisar; selección ("Incluir todas") y envío
  en lote; distingue lotes de **actualización**. → **CU-EVT-010**
- Ojo: esto es distinto de "Notificar horario" (CU-PRG-008). Son dos notificaciones en momentos
  diferentes: primero el resultado (aceptada/rechazada), después el horario asignado.

### 4. Seguimiento — contadores y cupos (solo lectura)
- Contadores por estado (pendiente / cambios solicitados / aceptada / rechazada) y espacios
  disponibles por categoría vs. cupo. → **CU-EVT-011**

### 5. Configuración — convocatoria
- 6 fechas clave + 4 cupos por categoría; valida orden cronológico; permite reabrir.
  → **CU-EVT-001**. Coincide con la grabación: *"para configurar fechas… le aparece un
  formulario… como la sección de configuración de Google"*.

## Pendiente para la siguiente versión (no en esta maqueta)
- Re-dictamen: cambiar un dictamen ya emitido (CU-EVT-009 A3).
- Gestión de usuarios administrativos / superadmin (CU-REG-005).
- Homologar CU-REG-005 al esquema OTP (ya no envía enlace de contraseña).

---

## Páginas HTML (CONSTRUIDAS)

El prototipo se dividió en dos carpetas dentro de `prototipo/EVT/`: `aplicantes/` (flujo del
proponente, ya existente) y `administradores/` (esta vista). `styles.css` queda compartido en
la raíz para ambas carpetas, incluyendo el shell del panel admin (sidebar, chips, calendario
estilo Outlook, rejilla de horario) — se descartó el `admin.css` propio de esta subcarpeta para
cumplir la política de un solo CSS por dominio.

**Acceso:**
1. `aplicantes/aplicantes-login.html` — se activó el enlace "Acceso administrativo" → OTP admin.
2. `administradores/admin-otp.html` — OTP de admin (visual de `otp.html`, cintillo "demo"). **CU-REG-003**
3. `administradores/admin-modulos.html` — selección de módulo, 3 tarjetas (solo Eventos entra). **CU-REG-006**

**Panel admin EVT (sidebar: Propuestas · Programa/Horario · Notificaciones · Seguimiento · Configuración):**
4. `administradores/admin-evt-propuestas.html` — dashboard: tarjetas resumen + tabla filtrable;
   botón "Revisar" / "Programar" según estado. Aterrizaje del panel. **CU-EVT-007 (+011 resumen)**
5. `administradores/admin-evt-detalle-propuesta.html` — detalle + adjuntos + ejemplar físico +
   dictamen en **modales** (Aceptar / Solicitar cambios / Rechazar). **CU-EVT-008 / 009 / 012**
5b. `administradores/admin-evt-detalle-rechazada.html` — detalle en **solo lectura** de una
   propuesta ya rechazada: formulario con las respuestas del aplicante + panel con el **motivo**
   registrado por el administrador. **CU-EVT-008** (consulta del detalle con dictamen anterior).
6. `administradores/admin-evt-programar.html` — formulario de una actividad y sus ocasiones:
   asignar sala + bloque(s) de 1:15, con alerta de empalme; **sin botón "guardar"** (implícito).
   **CU-PRG-002 / 003 / 004**
7. `administradores/admin-evt-horario.html` — **tablero híbrido**: riel "Por programar" + rejilla
   (salas × bloques, un día) + **diálogo de asignación estilo Outlook** (formulario + mini-día con
   el bloque en verde); empalmes y "Notificar horarios". **CU-PRG-001 / 002 / 008**
8. `administradores/admin-evt-notificaciones.html` — resultados de selección en lote. **CU-EVT-010**
9. `administradores/admin-evt-seguimiento.html` — contadores por estado + cupos (vista propia). **CU-EVT-011**
10. `administradores/admin-evt-configuracion.html` — fechas (calendario Outlook) y cupos. **CU-EVT-001**

Decisiones aplicadas: dictamen con **modales** dentro del detalle; **Seguimiento** como vista
propia; **Configuración** con calendario estilo Outlook. Todo reusa la paleta UADY de `styles.css`.
