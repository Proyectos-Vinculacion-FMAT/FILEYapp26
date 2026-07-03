---
estado: propuesta
version: 0.1
tags:
  - tipo/funcionalidades
  - dom/evt
fecha: 2026-07-03
---

# FILEY — Módulo de Eventos: Funcionalidades y tiempos estimados

Documento de presentación para el cliente. Describe **qué se va a construir** en el
módulo de **Eventos generales** (el programa general de la feria) y **cuánto tiempo**
aproximado toma cada parte.

> El sistema FILEY tiene tres módulos: **Stands**, **Eventos** e **Infantiles/Juveniles**.
> Este documento cubre **únicamente el módulo de Eventos**.

## ¿Qué resuelve el módulo de Eventos?

Todo el ciclo de una convocatoria de actividades del programa general, de principio a fin:

1. La coordinación **abre la convocatoria** y define fechas y cupos.
2. Los **proponentes envían sus propuestas** de actividad (charlas, conversatorios,
   presentaciones de libro, etc.) con sus documentos.
3. La coordinación **revisa y dictamina** cada propuesta (aceptar, pedir cambios o rechazar).
4. El sistema **notifica los resultados** a todos los proponentes.
5. Al cerrar la feria, los proponentes **descargan su constancia** y se pueden generar
   **fichas de difusión** de cada actividad.

---

## A. Funcionalidades para el Proponente (quien propone una actividad)

| # | Funcionalidad | Qué hace | Estimado |
|---|---------------|----------|:--------:|
| 1 | **Ver información de la convocatoria** † | Pantalla previa al formulario que muestra fechas clave, tipos de actividad, requisitos y cupos, con el botón "Aplicar". | 1 día |
| 2 | **Envío de propuesta** | Formulario completo para registrar una actividad: datos de contacto, tipo de actividad y sus campos específicos (conversatorio, conferencia, presentación de libro/revista, etc.), carga de documentos (sinopsis, semblanzas, portada) y envío con folio y correo de confirmación. Es la pieza más grande del lado del proponente. | 6 días |
| 3 | **Consultar mis propuestas** | Pantalla donde el proponente ve todas sus propuestas, su estado actual (pendiente, cambios solicitados, aceptada, rechazada) y los mensajes de la coordinación. | 3 días |
| 4 | **Editar propuesta tras solicitud de cambios** | El proponente corrige y reenvía su propuesta cuando la coordinación le pide ajustes, sin empezar de cero. | 2 días |
| 5 | **Descargar constancia de participación** | Después de la feria, el proponente descarga su constancia en PDF de las actividades en que participó. | 3 días |
| | **Subtotal Proponente** | | **15 días** |

---

## B. Funcionalidades para la Coordinación (administrador)

| # | Funcionalidad | Qué hace | Estimado |
|---|---------------|----------|:--------:|
| 5 | **Configurar la convocatoria** | La coordinación define las fechas clave (apertura, cierre, notificación, constancias) y los cupos por categoría, y deja la convocatoria abierta o la reabre. | 3 días |
| 6 | **Lista de propuestas filtrable** | Panel con todas las propuestas recibidas, con búsqueda y filtros por tipo de actividad, estado y categoría, para dar seguimiento a la revisión. | 3 días |
| 7 | **Revisar el detalle de una propuesta** | Vista completa de una propuesta: datos del proponente, descripción de la actividad y todos sus documentos adjuntos, lista para dictaminar. | 2 días |
| 8 | **Dictaminar una propuesta** | Aceptar, solicitar cambios o rechazar, con clasificación por categoría, registro del motivo y posibilidad de cambiar un dictamen ya emitido. Es la funcionalidad central de la coordinación. | 5 días |
| 9 | **Notificación de resultados en lote** | Envío de todos los resultados (aceptadas y rechazadas) en un solo lote de correos, con constancia de qué se envió y cuándo. | 4 días |
| 10 | **Contadores por estado y cupos** | Tablero de solo lectura que muestra en todo momento cuántas propuestas hay por estado y cuántos espacios quedan por categoría. | 2 días |
| 11 | **Marcar recepción del ejemplar físico** | Registro de control interno para presentaciones de libro/revista: marcar cuándo llegó el ejemplar físico enviado por el proponente. | 1 día |
| 12 | **Catálogo de tipos de actividad** † | Alta y edición de los tipos de actividad, incluidos los tipos internos que no salen en el formulario público (cuentacuentos, concierto, plática, etc.). | 3 días |
| 13 | **Registrar actividad interna** † | La coordinación crea directamente actividades que no pasan por convocatoria pública (p. ej. artísticas) y las marca como aptas para el catálogo juvenil. | 3 días |
| 14 | **Cierre definitivo del programa** † | Archivar el programa como versión definitiva, bloquear cambios posteriores y dejar registro de quién lo cerró, cuándo y por qué (con bitácora de cambios excepcionales). | 2 días |
| | **Subtotal Coordinación** | | **28 días** |

---

## C. Documentos automáticos

| # | Funcionalidad | Qué hace | Estimado |
|---|---------------|----------|:--------:|
| 15 | **Ficha PDF de una actividad** | Genera una ficha en PDF de una actividad individual (título, tipo, organiza, fecha, sala y horario) para difundirla o compartirla. | 2 días |
| | **Subtotal Documentos** | | **2 días** |

> La generación de la constancia (funcionalidad 5) ya está contada en el bloque del Proponente.

> **†** Funcionalidad detectada en el modelo de datos, el prototipo ya construido y la sección
> "Pendientes" del índice de casos de uso, pero **aún no redactada como caso de uso formal**.
> Su estimación es más aproximada que la del resto y su alcance fino está por confirmar con el equipo.

---

## D. Base técnica compartida (no visible, pero necesaria)

Trabajo de fondo que sostiene todas las pantallas anteriores.

| # | Componente | Qué incluye | Estimado |
|---|------------|-------------|:--------:|
| 16 | **Modelo de datos y backend base** | Estructura de datos y servicios para propuestas, actividades, parámetros de convocatoria, adjuntos y notificaciones. | 5 días |
| 17 | **Registro y acceso (OTP)** | Alta del proponente y acceso seguro por código de un solo uso. *Compartido con los otros módulos.* | 3 días |
| 18 | **Envío de correos** | Infraestructura para los correos de confirmación, cambios y resultados. | 2 días |
| | **Subtotal Base técnica** | | **10 días** |

---

## Resumen de tiempos

| Bloque | Tiempo |
|--------|:------:|
| A. Proponente | 15 días |
| B. Coordinación | 28 días |
| C. Documentos | 2 días |
| D. Base técnica compartida | 10 días |
| Integración, pruebas y ajustes (~15%) | 8 días |
| **Total estimado** | **≈ 63 días de desarrollo** |

### Traducción a calendario

- Con **1 desarrollador**: ≈ **12 a 14 semanas**.
- Con **2 desarrolladores** trabajando en paralelo: ≈ **7 a 8 semanas**.

> **Rango realista total: entre 55 y 70 días de desarrollo.** Las estimaciones son
> aproximadas y pueden variar según el detalle final de cada pantalla, revisiones con el
> cliente y pruebas. No incluyen tiempo de despliegue en producción ni capacitación.

---

## Fuera del alcance de este módulo (aclaración)

Para evitar confusiones con el cliente, estas tareas **existen en el sistema pero no
pertenecen al módulo de Eventos**:

- **Asignación de sala y horario** a las actividades aceptadas: la realiza el módulo de
  **Programación (PRG)**, aunque se dispara desde el mismo panel de Eventos.
- **Exportación del programa completo** a Excel/Word y la **cartelera pública** para
  visitantes: pertenecen a Programación (PRG).
- La convocatoria de **actividades infantiles y juveniles**: es el **tercer módulo**, aparte.

---

*Referencia interna: este documento resume los casos de uso CU-EVT-001 a CU-EVT-012.
Ver `CU-EVT Índice.md` para el detalle técnico de cada uno.*
