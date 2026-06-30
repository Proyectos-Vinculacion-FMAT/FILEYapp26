---
estado: aceptado
version: 0.2
tags:
  - requisitos
  - caso-de-uso
  - talleres
fecha: 2026-06-28
id: CU-TAL-003
dominio: TAL
reglas_de_negocio:
  - La edición solo está disponible mientras la convocatoria esté en estado `abierta`; al cerrarse, el sistema bloquea cualquier cambio.
  - El tallerista solo puede editar sus propias propuestas; no puede ver ni editar las de otros.
  - No existe solicitud de cambios por parte del administrador; la edición es autogestionada por el tallerista.
  - El folio y la fecha de envío originales no se modifican al editar.
---
# CU-TAL-003 Editar o actualizar mi propuesta de actividad mientras la convocatoria esté abierta

> **Diferencia clave con EVT:** en la convocatoria infantil/juvenil no hay dictamen ni solicitud
> de cambios del administrador (no existe el flujo de revisión de Hipólito). La edición es
> autogestionada: la inicia el propio tallerista, no una observación del administrador.
> Da cobertura a RF-TAL-02. Origen del requisito: Junta 2 con organizadores FILEY (flujo de
> aprobación y notificaciones), donde se establece que los registrantes tienen una ventana de
> tiempo con fecha de cierre fija para modificar por sí mismos los datos de su actividad.

## Objetivo

El tallerista consulta y modifica los datos de una propuesta que ya registró —para corregir un error o actualizar información— mientras la convocatoria siga abierta, manteniendo el registro vigente sin tener que crear una propuesta nueva.

## Alcance

Módulo de Talleres (TAL) — edición autogestionada de una propuesta propia. Solo aplica a propuestas asociadas a la cuenta con sesión activa y mientras la convocatoria esté en estado `abierta`. No cubre el primer registro (CU-TAL-002) ni el registro de visitas escolares (CU-TAL-007). A diferencia de CU-EVT-004, no existe estado `cambios_solicitados` ni mensaje del administrador que inicie la edición.

## Actores

### Actor principal

- Tallerista

## Disparador

El tallerista detecta un error o necesita actualizar los datos de una propuesta que ya envió.

## Precondiciones

- El tallerista tiene sesión iniciada (CU-REG-002).
- El tallerista tiene al menos una propuesta en estado `registrada`.
- La convocatoria de actividades infantiles/juveniles está en estado `abierta`.

## Postcondiciones

### En éxito

- Los datos de la propuesta quedan actualizados en el registro `PropuestaTaller`.
- El folio y la fecha de envío originales se conservan sin cambio.
- El estado de la propuesta permanece `registrada`.
- No se envía notificación al administrador; la edición es silenciosa.

### En fallo

- No se realizan cambios en el registro. El sistema conserva los datos previos y devuelve al tallerista al formulario con los errores indicados.

## Flujo principal

1. El tallerista accede a la sección "Mis propuestas" (CU-TAL-006) y selecciona la propuesta que desea editar.
2. El sistema verifica que la convocatoria esté en estado `abierta` y que la propuesta pertenezca al tallerista con sesión activa.
3. El sistema presenta el formulario precargado con los datos actuales de la propuesta.
4. El tallerista modifica los campos que desea actualizar.
5. El sistema valida en línea que los campos obligatorios permanezcan completos.
6. El tallerista confirma los cambios pulsando "Guardar".
7. El sistema realiza la validación final de campos obligatorios.
8. El sistema actualiza el registro `PropuestaTaller` con los nuevos datos.
9. El sistema confirma al tallerista que los cambios fueron guardados y regresa a la vista de detalle de la propuesta.

## Flujos alternos

### A1. El tallerista cancela la edición

1. En cualquier momento antes del paso 6, el tallerista pulsa "Cancelar".
2. El sistema descarta los cambios no guardados y regresa a la vista "Mis propuestas" (CU-TAL-006) sin modificar el registro.

## Flujos de excepción

### E1. Convocatoria cerrada al intentar editar

1. En el paso 2, el sistema detecta que la convocatoria ya no está en estado `abierta`.
2. El sistema informa al tallerista que el periodo de edición ha cerrado y que no se pueden realizar cambios.
3. El sistema muestra la propuesta en modo solo lectura.

### E2. Campos obligatorios faltantes en la validación final

1. En el paso 7, el sistema detecta campos obligatorios sin completar.
2. El sistema resalta cada campo en error con un mensaje descriptivo.
3. Los cambios no se guardan hasta que el tallerista corrija y reintente.

## Datos relevantes

- Los campos editables son los mismos que los del formulario de registro original (CU-TAL-002): datos del responsable, datos del evento, datos de la presentación, público meta y observaciones.
- El folio de registro y la fecha de envío son generados por el sistema al crear la propuesta (CU-TAL-002) y no pueden modificarse.
- Esta edición no afecta el proceso de selección de Elvira ni genera notificación al administrador.
