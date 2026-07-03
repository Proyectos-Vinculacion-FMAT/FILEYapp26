---
estado: propuesta
version: 0.1
tags:
  - tipo/modelo-de-datos
  - dom/vis
fecha: 2026-06-29
---
# Modelo de datos — Visitas escolares

> Modelo **conceptual**: identifica las entidades y los datos que el sistema debe
> almacenar para una visita escolar, **antes** de su aceptación (Propuesta, datos del
> formulario real de Elvira) y **después** (Participante con itinerario de talleres
> reservados). No compromete tipos de base de datos, índices ni claves físicas.

---

## 1. Resumen de entidades

| Entidad                   | Propósito                                                                             |
| ------------------------- | ------------------------------------------------------------------------------------- |
| PropuestaVisita           | El registro que llena el Aplicante (institución) — existe **antes** de la aceptación. |
| Institución               | Datos de la escuela/institución dentro de la propuesta.                               |
| Responsable               | Quien llena el registro (no siempre el director/a).                                   |
| Grupo                     | Uno de hasta 3 grupos en los que se divide la visita (responsable, grado, cantidad).  |
| Visita *(= Participante)* | La propuesta ya **Aceptada**: existe **después** de la aceptación.                    |
| ReservaTaller             | Cupo reservado por una Visita en una Programación (ocasión) de un taller de `TAL`.    |
| EnvioConfirmación         | Paquete (carta + reglamento) enviado a la Visita tras armar/confirmar su itinerario.  |

---

## 2. Detalle de entidades y atributos

### 2.1 PropuestaVisita

> Existe desde que el Aplicante envía el formulario hasta que se Acepta (momento en el que
> se vuelve, además, una Visita — ver 2.5). Sigue el ciclo genérico de Convocatorias
> (`REG`): *Pendiente a revisión* → *Aceptada* / *Solicitud de cambios* / *Rechazada*.

| Atributo                    | Descripción                                                                                                      |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| id                          | Identificador único.                                                                                             |
| folio                       | Asignado por FILEY al recibir el registro (no lo llena el Aplicante).                                            |
| fecha_recepcion             | Asignada por FILEY.                                                                                              |
| aplicante_id                | FK → Cuenta (quien llena el registro).                                                                           |
| nivel_educativo             | `preescolar` / `primaria_alta` / `primaria_baja` / `secundaria` / `preparatoria` / `universidad` / `multigrado`. |
| cantidad_alumnos_visitantes | Total declarado de la propuesta. Regla dura [RN-VIS-001]: **máximo 105**.                                        |
| campo_libre                 | Texto libre (alumnos de más, niños con capacidades especiales, etc.).                                            |
| estado                      | `pendiente_revision` / `aceptada` / `solicitud_cambios` / `rechazada`.                                           |
| fecha_envio, fecha_revision | Control del ciclo de revisión.                                                                                   |
| revisado_por                | FK → Cuenta (Administrador).                                                                                     |
| motivo                      | Texto (si hay solicitud de cambios o rechazo).                                                                   |

> *Nota:* **un registro (propuesta) por nivel educativo** — una escuela con varios niveles
> envía una propuesta independiente por cada uno (no se modela como una sola propuesta con
> niveles múltiples).

### 2.2 Institución

| Atributo                                 | Descripción                                                                                                  |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| id                                       | Identificador único.                                                                                         |
| propuesta_id                             | FK → PropuestaVisita.                                                                                        |
| nombre                                   | Nombre de la institución.                                                                                    |
| cct                                      | Clave de centro de trabajo.                                                                                  |
| sector                                   | `publico` / `privado`.                                                                                       |
| turno                                    | `matutino` / `vespertino`.                                                                                   |
| direccion                                | Domicilio.                                                                                                   |
| estado                                   | `Yucatán` / `Campeche` / `Quintana Roo`.                                                                     |
| municipio                                | `Mérida` / `Tizimín` / `Cenotillo` / `Espita` / `Buctzotz` / `Cansahcab` / `Otro` (+ texto libre si `Otro`). |
| telefono_institucion, correo_institucion | Contacto de la institución (distinto del Responsable).                                                       |
| nombre_director                          | Director(a) de la institución (puede no ser el Responsable).                                                 |

### 2.3 Responsable

> Quien llena el registro; puede ser un maestro directo o un padre/madre de familia — no
> necesariamente el director/a de la institución.

| Atributo         | Descripción                          |
| ---------------- | ------------------------------------ |
| id               | Identificador único.                 |
| propuesta_id     | FK → PropuestaVisita.                |
| nombre           | Nombre completo.                     |
| cargo            | `director` / `docente` / `prefecto`. |
| telefono, correo | Contacto directo del Responsable.    |

### 2.4 Grupo

| Atributo           | Descripción                                                                                                                                          |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| id                 | Identificador único.                                                                                                                                 |
| propuesta_id       | FK → PropuestaVisita.                                                                                                                                |
| nombre_responsable | Representante de ese grupo (obligatorio por grupo; puede repetirse entre grupos — ver ejemplo real donde una misma maestra es responsable de los 3). |
| grado              | Grado del grupo.                                                                                                                                     |
| cantidad_alumnos   | Máximo 35 por grupo.                                                                                                                                 |

> *Nota:* hasta **3 grupos** por propuesta, cada uno **opcional** (no obligatorio declarar los
> 3). La validación de que el representante exista/asista es control interno de FILEY, no del
> sistema.

### 2.5 Visita *(= Participante)*

> Es la **misma fila** que PropuestaVisita en el momento en que su estado pasa a `aceptada`
> (no es una tabla nueva con datos duplicados): a partir de ahí el Aplicante es Participante y
> la propuesta gana las capacidades de 2.6–2.7. Se documenta aparte solo para distinguir qué
> datos/relaciones existen **antes** (2.1–2.4) y **después** de la aceptación.

| Atributo (adicional a PropuestaVisita) | Descripción                                          |
| -------------------------------------- | ---------------------------------------------------- |
| fecha_aceptacion                       | Cuándo se Aceptó.                                    |
| itinerario_confirmado                  | `true` una vez que tiene al menos una ReservaTaller. |

### 2.6 ReservaTaller

> El **Cupo** (CU-VIS-011) es una propiedad **derivada**, no una entidad propia: cupo restante
> de una Programación = aforo de su Sala (`SAL`) − suma de `cantidad_alumnos` de sus
> ReservaTaller activas. **Excepción (precisión 2026-06-29):** si la Actividad detrás de la
> Programación es de `EVT` (caso excepcional que Hipólito marcó como apto para infantil/
> juvenil, ver CU-VIS-010), **no tiene límite de cupo** — el cálculo de cupo restante no aplica
> y la reserva no se rechaza por cantidad. Esto solo rige para Actividades de `TAL`.

| Atributo         | Descripción                                                                                                                                                                                                                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id               | Identificador único.                                                                                                                                                                                                                                                                                          |
| visita_id        | FK → Visita.                                                                                                                                                                                                                                                                                                  |
| programacion_id  | FK → Programación (`PRG`) — la reserva es contra una **ocasión concreta** del taller (fecha/sala/bloque), no contra la Actividad en abstracto. Solo puede referenciar una Programación cuyo horario ya es **final** (ver nota abajo); mientras sea preliminar, esa Programación no es elegible para reservar. |
| cantidad_alumnos | Alumnos de **esta** Visita asignados a **esta** Programación (selección libre por asiento: el grupo puede repartirse entre varias).                                                                                                                                                                           |
| fecha_reserva    | Cuándo se reservó.                                                                                                                                                                                                                                                                                            |

> *Nota:* la suma de `cantidad_alumnos` de todas las ReservaTaller de una Visita no debe
> exceder su `cantidad_alumnos_visitantes` (PropuestaVisita); cada reserva individual valida
> contra el cupo restante de **esa** Programación, no contra el total de la Visita (CU-VIS-011).

### 2.7 EnvioConfirmación

| Atributo           | Descripción                                                                                                                                                     |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id                 | Identificador único.                                                                                                                                            |
| visita_id          | FK → Visita.                                                                                                                                                    |
| fecha_envio        | Fecha de envío.                                                                                                                                                 |
| estado             | `enviada` / `fallida`.                                                                                                                                          |
| reservas_incluidas | Snapshot de las ReservaTaller vigentes al momento del envío (tipo, título, fecha/hora, salón/sala — formato visto en el ejemplo real de carta de confirmación). |
| incluye_reglamento | `true` (siempre se anexa el reglamento de 16 reglas).                                                                                                           |

---

## 3. Relaciones principales

- **PropuestaVisita** 1—1 **Institución**.
- **PropuestaVisita** 1—1 **Responsable**.
- **PropuestaVisita** 1—N **Grupo** (máx. 3).
- **PropuestaVisita** 1—1 **Visita** (misma entidad lógica; Visita "activa" las capacidades de
  itinerario solo si `estado = aceptada`).
- **Visita** 1—N **ReservaTaller** N—1 **Programación** (de `PRG`, que a su vez referencia una
  Sala de `SAL`).
- **Visita** 1—N **EnvioConfirmación**.

---

## 4. Mapa entidad → caso de uso (trazabilidad)

| Entidad                                             | Casos de uso relacionados           |
| --------------------------------------------------- | ----------------------------------- |
| PropuestaVisita / Institución / Responsable / Grupo | CU-VIS-001 a CU-VIS-009             |
| Visita                                              | CU-VIS-015, CU-VIS-016              |
| ReservaTaller                                       | CU-VIS-010 a CU-VIS-014, CU-VIS-017 |
| EnvioConfirmación                                   | CU-VIS-009, CU-VIS-013              |

---

## 5. Temas abiertos del modelo

- Confirmar si `cantidad_alumnos_visitantes` (PropuestaVisita) es un campo declarado de forma
  independiente o si se deriva de la suma de `Grupo.cantidad_alumnos` — el formulario real
  permite declarar grupos por separado, pero la regla dura de 105 se evalúa sobre el total.
- Validación previa a reservar (¿hay alguna aprobación además de la Aceptación de la propuesta
  antes de poder reservar talleres?) — sigue abierta, ver `CU-VIS Índice.md`.
- Plantilla/membrete oficial de `EnvioConfirmación` — el contenido ya está confirmado con un
  ejemplo real (ver
  [Carta de confirmación](<../../soporte/extraido/Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Carta%20de%20confirmaci%C3%B3n.%20SECUNDARIA%20EDMUNDO%20VILLALVA%20RODR%C3%8DGUEZ.md>)),
  pero el diseño/membrete final de FILEY sigue pendiente.
- **Mecanismo de "horario final"** (precisión 2026-06-29): confirmado que `ReservaTaller` solo
  puede apuntar a una Programación con horario **final**, nunca preliminar — pero no está
  definido **cómo** una Programación pasa de preliminar a final (¿acción explícita del
  Administrador en `PRG`, o derivada de que ya no haya rechazos/cambios pendientes en
  CU-PRG-009?). Afecta también a `PRG/Modelo de datos - Programación.md`, que hoy no modela
  esta distinción.

---

## Reglas de negocio relacionadas

El máximo de 105 alumnos por propuesta [RN-VIS-001], el máximo de 35 por grupo, la validación
de cupo por Programación (no por visita completa) y la selección libre por asiento están
documentados en `CU-VIS Índice.md` y en cada CU referenciado arriba.

[RN-VIS-001]: </docs/requisitos/VIS/Modelo de datos - Visitas escolares.md>
