---
estado: propuesta
version: 0.2
tags:
  - casos-de-uso
  - eventos
fecha: 2026-06-20
---
# CU-EVE — Índice de casos de uso (Eventos generales)

Inventario de casos de uso del dominio **Eventos Generales** (`EVE`): desde la apertura de la convocatoria hasta la publicación y cierre definitivo del programa. Cubre los módulos de contenidos (Hipólito) y talleres/VIDA (Elvira).

**Actores:** Aplicante (persona/institución que propone una actividad) · Administrador (Hipólito, Elvira y sus equipos) · Sistema (procesos automáticos y temporizados).

> [!note]
> Cada caso de uso tiene su propio archivo dentro de su módulo. Este índice es la vista general.
> La redacción detallada (actores, flujo principal y alternos) se hará después de revisar con el equipo.

> [!note]
> Los casos de uso de **salas** (asignación, disponibilidad) dependen del Core Salas.
> Los de **identidad** (registro de Aplicante, acceso OTP) dependen del Core Registros:
> ver `CORES/REG/CU-REG Índice.md` — CU-REG-001, CU-REG-002 (usuarios externos) y CU-REG-003 (admin).

## Flujo de alto nivel

```
STD:  Aplicación → Reserva   → Pago          → Confirmación y estados → Administración
EVE:  Convocatoria → Revisión → Programación  → Confirmación y Cierre  → Publicación y Admin
```

> Los módulos son paralelos en intención: A inicia el proceso, B evalúa, C asigna el recurso, D lo cierra y E lo gestiona desde el lado administrativo.

---

## A. Convocatoria

Cubre la apertura del periodo de recepción de propuestas y todo lo que hace el aplicante mientras la convocatoria está abierta.

- CU-EVE-001 Configurar la convocatoria: abrir periodo, fechas clave y cupos por categoría — *Administrador*
- CU-EVE-002 Enviar propuesta de actividad con datos y adjuntos — *Aplicante*
- CU-EVE-003 Enviar múltiples propuestas desde una misma cuenta sin recapturar datos de contacto — *Aplicante*
- CU-EVE-004 Editar una propuesta en respuesta a una solicitud de cambios del administrador — *Aplicante*
- ~~CU-EVE-005 Cerrar automáticamente la convocatoria al vencer la fecha configurada~~ — absorbido en CU-EVE-001
- ~~CU-EVE-006 Registrar una actividad interna sin pasar por convocatoria pública~~ — pospuesto para v2
- CU-EVE-036 Consultar mis propuestas y revisar su estado actual — *Aplicante*

## B. Revisión y Selección

Hipólito revisa de forma continua (semana a semana, no solo al cierre). Las decisiones se notifican en un solo lote cuando termina su revisión.

- CU-EVE-007 Consultar la lista de propuestas recibidas, filtrable por tipo, estado y categoría — *Administrador*
- CU-EVE-008 Ver el detalle de una propuesta (datos del aplicante, descripción y adjuntos) — *Administrador*
- CU-EVE-009 Dictaminar una propuesta: aceptar, solicitar cambios o rechazar — *Administrador*
- ~~CU-EVE-010 Rechazar una propuesta con motivo registrado~~ — absorbido en CU-EVE-009 (flujo alterno A2)
- ~~CU-EVE-011 Marcar una propuesta como "en negociación"~~ — pospuesto para v2 (estado no definido para MVP)
- CU-EVE-012 Ver el contador en tiempo real: aceptadas, rechazadas y espacios disponibles por categoría — *Administrador*
- CU-EVE-013 Enviar en un solo lote las notificaciones de resultado (aceptadas y rechazadas) — *Administrador*
- CU-EVE-014 Marcar la recepción del ejemplar físico enviado por el aplicante (Presentación de libro/revista) — *Administrador*

## C. Programación

El coordinador arma el programa de forma iterativa — puede hacer múltiples versiones en borrador antes de notificar. La asignación de sala y horario es independiente de la aceptación.

- CU-EVE-015 Crear una nueva versión borrador del programa maestro e iterar el acomodo sin publicar — *Administrador*
- CU-EVE-016 Consultar la disponibilidad de salas en vista de calendario por día y bloque — *Administrador*
- CU-EVE-017 Asignar sala, fecha y bloque de horario a una actividad aceptada — *Administrador*
- CU-EVE-018 Asignar una actividad de duración no estándar que ocupa múltiples bloques — *Administrador*
- CU-EVE-019 Configurar la duración del bloque estándar y el colchón de transición entre actividades — *Administrador*
- CU-EVE-020 Asignar un stand del módulo STD como lugar de una actividad (en lugar de sala del catálogo) — *Administrador*
- CU-EVE-021 Programar una actividad en múltiples sesiones o fechas sin duplicar su registro — *Administrador*
- CU-EVE-022 Marcar una actividad aceptada como apta para nivel juvenil/escolar — *Administrador*
- CU-EVE-023 Notificar al aplicante la sala y horario asignados — *Sistema*

## D. Confirmación y Cierre

El aplicante recibe su horario y lo confirma. Existe una ventana de tiempo para solicitar cambios; fuera de ella, el sistema bloquea modificaciones.

- CU-EVE-024 Responder a la notificación de horario asignado (confirmar o indicar incomparecencia) — *Aplicante*
- ~~CU-EVE-025 Solicitar cambio de horario dentro de la ventana de modificaciones permitida~~ — absorbido en CU-EVE-024 (flujo alterno A1); el cambio de horario se gestiona fuera del sistema vía correo con el admin → CU-EVE-026
- CU-EVE-026 Hacer un cambio de horario excepcional fuera de la ventana (con registro en bitácora y motivo) — *Administrador*
- CU-EVE-027 Cerrar definitivamente el programa: bloquear cualquier modificación posterior — *Administrador*
- CU-EVE-028 Descargar constancia de participación (disponible a partir de la fecha configurada, post-feria) — *Aplicante*

## E. Publicación y Administración

Exportación, publicación para visitantes, catálogos y auditoría.

- CU-EVE-029 Publicar una versión del programa de forma incremental (sin tener el 100% confirmado) — *Administrador*
- CU-EVE-030 Exportar el programa completo o un subconjunto a Excel, Word o PDF — *Administrador*
- CU-EVE-031 Generar la ficha PDF de una actividad individual (título, tipo, organiza, fecha, sala, horario) — *Sistema*
- CU-EVE-032 Mostrar la cartelera pública filtrable por categoría/sección para visitantes — *Sistema*
- CU-EVE-033 Mostrar el detalle de una actividad pública (con sinopsis y datos de autor para presentaciones de libro) — *Sistema*
- CU-EVE-034 Administrar el catálogo de tipos de actividad (agregar, editar, activar/desactivar) — *Administrador*
- CU-EVE-035 Consultar la bitácora de cambios excepcionales de una actividad — *Administrador*

---

## Artefactos relacionados

- `Modelo de datos - Eventos.md` — entidades y datos que el sistema almacena.
- `Proceso de alto nivel - Eventos.md` — diagrama del flujo de punta a punta.
- `CORES/Definicion de Cores.md` — entidades compartidas con STD y TAL.

## Mapa CU → Requisito (equivalencia con RFH)

| Módulo | CUs | Requisitos origen |
|--------|-----|-------------------|
| A. Convocatoria | CU-EVE-001 a 004, CU-EVE-036 | RFH-01, RFH-02, RFH-03, RFH-31 |
| B. Revisión y Selección | CU-EVE-007 a 009, CU-EVE-012 a 014 | RFH-05, RFH-06, RFH-07, RFH-08, RFH-09, RFH-35, RFH-04.1 |
| C. Programación | CU-EVE-015 a 023 | RFH-09, RFH-10, RFH-11, RFH-12, RFH-13, RFH-14, RFH-15, RFH-33, RFH-37 |
| D. Confirmación y Cierre | CU-EVE-024 a 028 | RFH-17, RFH-18, RFH-19, RFH-20, RFH-22.1 |
| E. Publicación y Admin | CU-EVE-029 a 035 | RFH-21, RFH-22, RFH-23, RFH-24, RFH-25, RFH-32, RNFH-03 |
