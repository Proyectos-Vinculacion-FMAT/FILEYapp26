---
estado: propuesta
version: 0.2
tags:
  - casos-de-uso
  - eventos
fecha: 2026-06-20
---
# CU-EVT — Índice de casos de uso (Eventos generales / Programa general)

Inventario de casos de uso del dominio **Eventos Generales** (`EVT`): la convocatoria del **programa general** que administra **Hipólito**, desde la apertura de la convocatoria hasta la publicación y cierre definitivo del programa.

**Actores:** Aplicante (persona/institución que propone una actividad) · Administrador (Hipólito y su equipo) · Sistema (procesos automáticos y temporizados).

> [!note] Dominio paralelo
> La convocatoria de **actividades infantiles y juveniles** que administra **Elvira** es un
> dominio aparte: ver `TAL/CU-TAL Índice.md`. A diferencia de EVT, TAL **no tiene revisión/dictamen
> por propuesta dentro del sistema** (la selección es manual y la confirmación llega por correo).

> [!note] note
> Cada caso de uso tiene su propio archivo dentro de su módulo. Este índice es la vista general.
> La redacción detallada (actores, flujo principal y alternos) se hará después de revisar con el equipo.

> [!note] note
> Los casos de uso de **salas** (asignación, disponibilidad) dependen del Core Salas.
> Los de **identidad** (registro de Aplicante, acceso OTP) dependen del Core Registros:
> ver `REG/CU-REG Índice.md` — CU-REG-001, CU-REG-002 (usuarios externos) y CU-REG-003 (admin).

## Flujo de alto nivel

```
STD:  Aplicación → Reserva   → Pago          → Confirmación y estados → Administración
EVT:  Convocatoria → Revisión → Programación  → Confirmación y Cierre  → Publicación y Admin
```

> Los módulos son paralelos en intención: A inicia el proceso, B evalúa, C asigna el recurso, D lo cierra y E lo gestiona desde el lado administrativo.

---

## primera version (historial)

### A. Convocatoria

Cubre la apertura del periodo de recepción de propuestas y todo lo que hace el aplicante mientras la convocatoria está abierta.

- CU-EVT-001 Configurar la convocatoria: abrir periodo, fechas clave y cupos por categoría — *Administrador*
- CU-EVT-002 registrar la propuesta de la actividad (llenado del formulario) — *Aplicante*
- CU-EVT-002.1 Enviar la propuesta de actividad (acción de envío) — *Aplicante * [es absor por 002]
- CU-EVT-003 Enviar múltiples propuestas desde una misma cuenta sin recapturar datos de contacto — *Aplicante * [rechazado]
- CU-EVT-004 Editar una propuesta en respuesta a una solicitud de cambios del administrador — *Aplicante * [este pasaria al B]
- CU-EVT-005 Consultar mis propuestas y revisar su estado actual — *Aplicante*

### B. Revisión y Selección

Hipólito revisa de forma continua (semana a semana, no solo al cierre). Las decisiones se notifican en un solo lote cuando termina su revisión.

- CU-EVT-006 Consultar la lista de propuestas recibidas, filtrable por tipo, estado y categoría — *Administrador *
- CU-EVT-007 Ver el detalle de una propuesta (datos del aplicante, descripción y adjuntos) — *Administrador*
- CU-EVT-008 Dictaminar una propuesta: aceptar, solicitar cambios o rechazar — *Administrador*
- ~~CU-EVT-009 Rechazar una propuesta con motivo registrado~~ — absorbido en CU-EVT-008 (flujo alterno A2)
- ~~CU-EVT-010 Marcar una propuesta como "en negociación"~~ — pospuesto para v2 (estado no definido para MVP)
- CU-EVT-011 visualizar el numero de actividades: aceptadas, rechazadas y espacios disponibles por categoría — *Administrador*
- CU-EVT-012 Enviar notificaciones de resultado (aceptadas y rechazadas) — *Administrador*
- CU-EVT-013 Marcar la recepción del ejemplar físico enviado por el aplicante (Presentación de libro/revista) — *Administrador [pendiente (preguntar a hipolito)]*

### D. Confirmación y Cierre

El aplicante recibe su horario y lo confirma. Existe una ventana de tiempo para solicitar cambios; fuera de ella, el sistema bloquea modificaciones.

- CU-EVT-027 Descargar constancia de participación (disponible a partir de la fecha configurada, post-feria) — *Aplicante*

### E. Publicación y Administración

Exportación, publicación para visitantes, catálogos y auditoría.

- CU-EVT-030 Generar la ficha PDF de una actividad individual (título, tipo, organiza, fecha, sala, horario) — *Sistema*

## Segunda version

### A. Convocatoria

Cubre la apertura del periodo de recepción de propuestas y todo lo que hace el aplicante mientras la convocatoria está abierta.

- CU-EVT-001 Configurar la convocatoria: abrir periodo, fechas clave y cupos por categoría — *Administrador*
- CU-EVT-002 Registro de la propuesta de la actividad — *Aplicante*
- CU-EVT-003 Consultar mis propuestas y revisar su estado actual — *Aplicante* 

### B. Revisión y Selección

Hipólito revisa de forma continua (semana a semana, no solo al cierre). Las decisiones se notifican en un solo lote cuando termina su revisión.

- CU-EVT-004 Editar una propuesta en respuesta a una solicitud de cambios del administrador — *Aplicante * [este pasaria al B]
- CU-EVT-005 Consultar la lista de propuestas recibidas, filtrable por tipo, estado y categoría — *Administrador*
- CU-EVT-006 Ver el detalle de una propuesta (datos del aplicante, descripción y adjuntos) — *Administrador*
- CU-EVT-007 Dictaminar una propuesta: aceptar, solicitar cambios o rechazar — *Administrador*
- ~~CU-EVT-009 Rechazar una propuesta con motivo registrado~~ — absorbido en CU-EVT-008 (flujo alterno A2)
- ~~CU-EVT-010 Marcar una propuesta como "en negociación"~~ — pospuesto para v2 (estado no definido para MVP)
- CU-EVT-08 visualizar el numero de actividades: aceptadas, rechazadas y espacios disponibles por categoría — *Administrador*
- CU-EVT-09 Enviar notificaciones de resultado (aceptadas y rechazadas) — *Administrador*
- CU-EVT-010 Marcar la recepción del ejemplar físico enviado por el aplicante (Presentación de libro/revista) — *Administrador [pendiente (preguntar a hipolito)]*

### D. Confirmación y Cierre

El aplicante recibe su horario y lo confirma. Existe una ventana de tiempo para solicitar cambios; fuera de ella, el sistema bloquea modificaciones.

- CU-EVT-011 Descargar constancia de participación (disponible a partir de la fecha configurada, post-feria) — *Aplicante*

### E. Publicación y Administración

Exportación, publicación para visitantes, catálogos y auditoría.

- CU-EVT-012 Generar la ficha PDF de una actividad individual (título, tipo, organiza, fecha, sala, horario) — *Sistema*

---

## Artefactos relacionados

- `Modelo de datos - Eventos.md` — entidades y datos que el sistema almacena.
- `Proceso de alto nivel - Eventos.md` — diagrama del flujo de punta a punta.
- `CORES/Definicion de Cores.md` — entidades compartidas con STD y TAL.

## Mapa CU → Requisito (equivalencia con RFH)

| Módulo                   | CUs                                | Requisitos origen                                                      |
| ------------------------- | ---------------------------------- | ---------------------------------------------------------------------- |
| A. Convocatoria           | CU-EVT-001 a 005                   | RFH-01, RFH-02, RFH-03, RFH-31                                         |
| B. Revisión y Selección | CU-EVT-006 a 008, CU-EVT-011 a 013 | RFH-05, RFH-06, RFH-07, RFH-08, RFH-09, RFH-35, RFH-04.1               |
| C. Programación          | CU-EVT-014 a 022                   | RFH-09, RFH-10, RFH-11, RFH-12, RFH-13, RFH-14, RFH-15, RFH-33, RFH-37 |
| D. Confirmación y Cierre | CU-EVT-023 a 027                   | RFH-17, RFH-18, RFH-19, RFH-20, RFH-22.1                               |
| E. Publicación y Admin   | CU-EVT-028 a 034                   | RFH-21, RFH-22, RFH-23, RFH-24, RFH-25, RFH-32, RNFH-03                |
