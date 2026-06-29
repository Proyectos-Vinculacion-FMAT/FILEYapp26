---
estado: propuesta
version: 0.1
tags:
  - tipo/modelo-de-datos
  - dom/prg
fecha: 2026-06-29
---
# Modelo de datos — Programación

> Modelo **conceptual**: identifica las entidades y los datos que el sistema debe
> almacenar para programar una actividad (sala + horario) y notificar/confirmar esa
> asignación, sin comprometer aún tipos de base de datos, índices ni claves físicas.
> Las relaciones se describen en la sección 3.

---

## 1. Resumen de entidades

| Entidad | Propósito |
|---------|-----------|
| Actividad | Referencia a la propuesta Aceptada de `EVT`/`TAL` que se programa. Su dato propio (formulario) vive en esos dominios; aquí solo se referencia. |
| Programación | Una ocasión concreta en que una Actividad ocupa una Sala y uno o varios bloques de horario. |
| Sala | Referencia al espacio de `SAL` donde se programa (catálogo único global). |
| Notificación | Envío al Participante de la(s) fecha(s)/sala/horario vigentes de una Actividad. |
| RespuestaProgramación | Aceptación o rechazo del Participante a una Programación notificada. |

---

## 2. Detalle de entidades y atributos

### 2.1 Actividad
> No es una entidad propia de `PRG`: es la misma Actividad de `EVT`/`TAL` (una propuesta
> Aceptada). Se referencia aquí solo por los campos que `PRG` necesita leer/derivar.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único (de `EVT` o `TAL`). |
| dominio_origen | `EVT` / `TAL`. |
| panel | `eventos` / `talleres` — determina la duración hardcodeada del bloque (1:15 / 1:00). |
| estado_programacion | Derivado: `pendiente` (0 Programaciones) / `programada` (≥1 Programación vigente). |

### 2.2 Programación
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| actividad_id | FK → Actividad. |
| sala_id | FK → Sala (`SAL`). |
| fecha | Día de la ocasión. |
| bloque_inicio, bloque_fin | Bloque(s) hardcodeados que ocupa (consecutivos; igual a `bloque_inicio` si ocupa solo uno). |
| tiene_empalme | Derivado: `true` si choca con otra Programación de la misma Sala (CU-PRG-002 E1); no bloquea el guardado, sí bloquea notificar. |
| estado_notificacion | `sin_notificar` / `notificada` / `cambio_sin_notificar` (se vuelve a este último al mover/eliminar una Programación ya notificada de la misma Actividad). |
| creado_el, actualizado_el | Control de cambios; no hay un campo de "guardado" aparte — guardado implícito. |

> *Nota:* una Actividad puede tener **varias** Programaciones solo en el panel de
> **talleres** (repetir la misma actividad para llenar huecos, CU-PRG-002 A1).

### 2.3 Sala
> Entidad propia de `SAL`, referenciada aquí. Ver `SAL/CU-SAL Índice.md` para su detalle
> completo (aforo, disponibilidad). `PRG` no almacena copia de sus datos, solo la FK.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único (de `SAL`). |
| aforo | Usado solo si `VIS` necesita validar cupo contra la sala (fuera del alcance de `PRG`). |

### 2.4 Notificación
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| actividad_id | FK → Actividad — la notificación es **por actividad**, no por Programación individual. |
| disparada_por | FK → Cuenta (Administrador) / `masiva` si se originó en una notificación en lote (CU-PRG-008 A1). |
| programaciones_incluidas | Snapshot de las Programaciones vigentes de esa Actividad al momento del envío (fecha, sala, bloque(s) de cada una). |
| fecha_envio | Fecha de envío. |
| estado | `enviada` / `fallida` (reintento, ver CU-PRG-008). |

### 2.5 RespuestaProgramación
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| programacion_id | FK → Programación — la respuesta es **por Programación**, nunca en bloque (CU-PRG-009). |
| notificacion_id | FK → Notificación (la que la originó). |
| respuesta | `aceptada` / `rechazada`. |
| motivo_rechazo | Texto libre, opcional (solo si `respuesta = rechazada`). La negociación de una reprogramación a partir de este motivo ocurre **fuera del sistema**. |
| fecha_respuesta | Fecha de la respuesta. |

---

## 3. Relaciones principales

- **Actividad** 1—N **Programación** (N solo en el panel de talleres; 0 o 1 en eventos).
- **Programación** N—1 **Sala** (de `SAL`; una sala puede tener muchas Programaciones de distintas Actividades, sin empalme de bloques).
- **Actividad** 1—N **Notificación** (una por cada vez que el Administrador decide notificar).
- **Programación** 1—N **RespuestaProgramación** (en la práctica, 0 o 1 respuesta vigente por Programación; una nueva notificación tras editar invalida la respuesta anterior y exige una nueva).
- **Notificación** 1—N **RespuestaProgramación** (todas las respuestas que originó ese envío).

---

## 4. Mapa entidad → caso de uso (trazabilidad)

| Entidad | Casos de uso relacionados |
|---------|---------------------------|
| Actividad | CU-PRG-001 a CU-PRG-004 |
| Programación | CU-PRG-002, CU-PRG-003, CU-PRG-004 |
| Sala | CU-SAL-001 a CU-SAL-007 (referenciada, no editada desde `PRG`) |
| Notificación | CU-PRG-008 |
| RespuestaProgramación | CU-PRG-009 |

---

## 5. Temas abiertos del modelo

- **R5 (hueco conocido):** no hay entidad para Programaciones manuales sin Actividad/propuesta
  Aceptada detrás (artísticos de control interno, "pulida final" del programa). Evidencia real:
  bloques tipo "Salón 6. APARTADO — Hipólito" en el borrador de
  [Agenda escuelas](<../../soporte/extraido/Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Agenda%20escuelas.%20Programa%20para%20revisi%C3%B3n.md>).
  Pendiente decidir si se modela como una Actividad "fantasma" o un tipo de Programación aparte.
- Confirmar si `programaciones_incluidas` de Notificación se guarda como snapshot (copia) o se
  deriva siempre en vivo de las Programaciones vigentes al momento de renderizar el correo.
- `tiene_empalme` puede calcularse en consulta (no almacenarse) si el volumen de Programaciones
  por sala es bajo; decisión de implementación, no de negocio.

---

## Reglas de negocio relacionadas

Bloques hardcodeados por panel (1:15 Eventos, 1:00 Talleres), máximo de empalme no bloqueante,
y guardado implícito están documentados en `CU-PRG Índice.md` y en cada CU referenciado arriba.
