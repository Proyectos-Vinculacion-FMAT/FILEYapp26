---
estado: propuesta
version: 0.3
tags:
  - tipo/caso-de-uso
  - dom/tal
fecha: 2026-06-28
id: CU-TAL-004
dominio: TAL
reglas_de_negocio:
  - La edición solo está disponible mientras la convocatoria esté en estado `abierta`; al cerrarse, el sistema bloquea cualquier cambio.
  - El tallerista solo puede editar sus propias propuestas; no puede ver ni editar las de otros.
  - El folio y la fecha de envío originales no se modifican al editar.
---
# CU-TAL-004 Editar una propuesta en respuesta a una solicitud de cambios del administrador

> [!warning] Corrección (2026-06-29) — sí hay dictamen y `cambios_solicitados`
> Una versión anterior de este CU asumía edición libre en cualquier momento porque se creía
> que `TAL` no tenía dictamen. **Corregido por el cliente:** Elvira sí dictamina cada
> propuesta (CU-TAL-009), igual que Hipólito en `EVT`. Este CU se alinea con CU-EVT-003: el
> tallerista edita y reenvía **en respuesta a una solicitud de cambios**, no libremente.
>
> **Pendiente de confirmar:** la evidencia original citada aquí (Junta 2 con organizadores
> FILEY, "los registrantes tienen una ventana de tiempo... para modificar por sí mismos los
> datos de su actividad") describe en realidad una ventana de edición **posterior a la
> aceptación** (similar a la de EVT, que tampoco tiene CU propio todavía — ver "Pendientes" en
> `CU-TAL Índice.md`), no una edición libre durante la revisión. Se deja esa ventana
> post-aceptación como pendiente separado.

## Objetivo

El tallerista corrige su propuesta atendiendo las observaciones registradas por Elvira y la reenvía para una nueva revisión, sin tener que iniciar una propuesta desde cero.

## Alcance

Módulo de Talleres (TAL) — edición de una propuesta existente. Solo aplica cuando la propuesta está en estado `cambios_solicitados` y la convocatoria sigue `abierta`. No cubre el primer registro (CU-TAL-002), el dictamen (CU-TAL-009) ni el registro de visitas escolares, que es responsabilidad del dominio `VIS` (ver `VIS/CU-VIS Índice.md`).

## Actores

### Actor principal

- Tallerista

## Disparador

El tallerista recibe la notificación de que Elvira solicitó cambios en su propuesta (CU-TAL-009).

## Precondiciones

- El tallerista tiene sesión iniciada (CU-REG-002).
- Existe al menos una propuesta propia en estado `cambios_solicitados`.
- La convocatoria de actividades infantiles/juveniles está en estado `abierta`.

## Postcondiciones

### En éxito

- La propuesta queda en estado `pendiente`, con la fecha de reenvío registrada, lista para que Elvira la revise de nuevo (CU-TAL-007 a CU-TAL-009).
- El folio y la fecha de envío originales se conservan sin cambio.

### En fallo

- La propuesta permanece en estado `cambios_solicitados`. El tallerista puede reintentar.

## Flujo principal

1. El tallerista accede a "Mis propuestas" (CU-TAL-003) y selecciona la propuesta en estado `cambios_solicitados`.
2. El sistema muestra el detalle de la propuesta junto con el mensaje de cambios solicitados por Elvira.
3. El tallerista modifica los campos señalados.
4. El tallerista reenvía la propuesta.
5. El sistema valida en línea que los campos obligatorios permanezcan completos.
6. El sistema actualiza el registro `PropuestaTaller` al estado `pendiente` y registra la fecha de reenvío.
7. El sistema confirma al tallerista que la propuesta fue reenviada y está en revisión nuevamente.

## Flujos de excepción

### E1. Convocatoria cerrada al intentar reenviar

1. En el paso 4, el sistema detecta que la convocatoria ya no está en estado `abierta`.
2. El sistema informa al tallerista que el periodo de edición ha cerrado y que no se pueden realizar cambios.
3. El sistema muestra la propuesta en modo solo lectura.

### E2. Campos obligatorios faltantes

1. En el paso 5, el sistema detecta campos obligatorios sin completar.
2. El sistema resalta cada campo en error con un mensaje descriptivo.
3. El reenvío no procede hasta que el tallerista corrija y reintente.

## Datos relevantes

- Los campos editables son los mismos que los del formulario de registro original (CU-TAL-002): datos del responsable, datos del evento, datos de la presentación, público meta y observaciones.
- El folio de registro y la fecha de envío original son generados por el sistema al crear la propuesta (CU-TAL-002) y no pueden modificarse.
- El mensaje de cambios solicitados por Elvira queda visible como referencia durante la edición.
