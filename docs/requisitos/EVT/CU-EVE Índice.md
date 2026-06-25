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

- CU-EVT-001 Configurar la convocatoria: abrir periodo, fechas clave y cupos por categoría — *Administrador*
- CU-EVT-002 Enviar propuesta de actividad con datos y adjuntos — *Aplicante*
- CU-EVT-003 Enviar múltiples propuestas desde una misma cuenta sin recapturar datos de contacto — *Aplicante*
- CU-EVT-004 Editar una propuesta en respuesta a una solicitud de cambios del administrador — *Aplicante*
- CU-EVT-005 Consultar mis propuestas y revisar su estado actual — *Aplicante*

## B. Revisión y Selección

Hipólito revisa de forma continua (semana a semana, no solo al cierre). Las decisiones se notifican en un solo lote cuando termina su revisión.

- CU-EVT-006 Consultar la lista de propuestas recibidas, filtrable por tipo, estado y categoría — *Administrador*
- CU-EVT-007 Ver el detalle de una propuesta (datos del aplicante, descripción y adjuntos) — *Administrador*
- CU-EVT-008 Dictaminar una propuesta: aceptar, solicitar cambios o rechazar — *Administrador*
- ~~CU-EVT-009 Rechazar una propuesta con motivo registrado~~ — absorbido en CU-EVT-008 (flujo alterno A2)
- ~~CU-EVT-010 Marcar una propuesta como "en negociación"~~ — pospuesto para v2 (estado no definido para MVP)
- CU-EVT-011 Ver el contador en tiempo real: aceptadas, rechazadas y espacios disponibles por categoría — *Administrador*
- CU-EVT-012 Enviar en un solo lote las notificaciones de resultado (aceptadas y rechazadas) — *Administrador*
- CU-EVT-013 Marcar la recepción del ejemplar físico enviado por el aplicante (Presentación de libro/revista) — *Administrador*

## C. Programación

El coordinador arma el programa de forma iterativa — puede hacer múltiples versiones en borrador antes de notificar. La asignación de sala y horario es independiente de la aceptación.

- CU-EVT-014 Crear una nueva versión borrador del programa maestro e iterar el acomodo sin publicar — *Administrador*
- CU-EVT-015 Consultar la disponibilidad de salas en vista de calendario por día y bloque — *Administrador*
- CU-EVT-016 Asignar sala, fecha y bloque de horario a una actividad aceptada — *Administrador*
- CU-EVT-017 Asignar una actividad de duración no estándar que ocupa múltiples bloques — *Administrador*
- CU-EVT-018 Configurar la duración del bloque estándar y el colchón de transición entre actividades — *Administrador*
- CU-EVT-019 Asignar un stand del módulo STD como lugar de una actividad (en lugar de sala del catálogo) — *Administrador*
- CU-EVT-020 Programar una actividad en múltiples sesiones o fechas sin duplicar su registro — *Administrador*
- CU-EVT-021 Marcar una actividad aceptada como apta para nivel juvenil/escolar — *Administrador*
- CU-EVT-022 Notificar al aplicante la sala y horario asignados — *Sistema*

## D. Confirmación y Cierre

El aplicante recibe su horario y lo confirma. Existe una ventana de tiempo para solicitar cambios; fuera de ella, el sistema bloquea modificaciones.

- CU-EVT-023 Responder a la notificación de horario asignado (confirmar o indicar incomparecencia) — *Aplicante*
- ~~CU-EVT-024 Solicitar cambio de horario dentro de la ventana de modificaciones permitida~~ — absorbido en CU-EVT-023 (flujo alterno A1); el cambio de horario se gestiona fuera del sistema vía correo con el admin → CU-EVT-025
- CU-EVT-025 Hacer un cambio de horario excepcional fuera de la ventana (con registro en bitácora y motivo) — *Administrador*
- CU-EVT-026 Cerrar definitivamente el programa: bloquear cualquier modificación posterior — *Administrador*
- CU-EVT-027 Descargar constancia de participación (disponible a partir de la fecha configurada, post-feria) — *Aplicante*

## E. Publicación y Administración

Exportación, publicación para visitantes, catálogos y auditoría.

- CU-EVT-028 Publicar una versión del programa de forma incremental (sin tener el 100% confirmado) — *Administrador*
- CU-EVT-029 Exportar el programa completo o un subconjunto a Excel, Word o PDF — *Administrador*
- CU-EVT-030 Generar la ficha PDF de una actividad individual (título, tipo, organiza, fecha, sala, horario) — *Sistema*
- CU-EVT-031 Mostrar la cartelera pública filtrable por categoría/sección para visitantes — *Sistema*
- CU-EVT-032 Mostrar el detalle de una actividad pública (con sinopsis y datos de autor para presentaciones de libro) — *Sistema*
- CU-EVT-033 Administrar el catálogo de tipos de actividad (agregar, editar, activar/desactivar) — *Administrador*
- CU-EVT-034 Consultar la bitácora de cambios excepcionales de una actividad — *Administrador*

---

## Artefactos relacionados

- `Modelo de datos - Eventos.md` — entidades y datos que el sistema almacena.
- `Proceso de alto nivel - Eventos.md` — diagrama del flujo de punta a punta.
- `CORES/Definicion de Cores.md` — entidades compartidas con STD y TAL.

## Mapa CU → Requisito (equivalencia con RFH)

| Módulo | CUs | Requisitos origen |
|--------|-----|-------------------|
| A. Convocatoria | CU-EVT-001 a 005 | RFH-01, RFH-02, RFH-03, RFH-31 |
| B. Revisión y Selección | CU-EVT-006 a 008, CU-EVT-011 a 013 | RFH-05, RFH-06, RFH-07, RFH-08, RFH-09, RFH-35, RFH-04.1 |
| C. Programación | CU-EVT-014 a 022 | RFH-09, RFH-10, RFH-11, RFH-12, RFH-13, RFH-14, RFH-15, RFH-33, RFH-37 |
| D. Confirmación y Cierre | CU-EVT-023 a 027 | RFH-17, RFH-18, RFH-19, RFH-20, RFH-22.1 |
| E. Publicación y Admin | CU-EVT-028 a 034 | RFH-21, RFH-22, RFH-23, RFH-24, RFH-25, RFH-32, RNFH-03 |
