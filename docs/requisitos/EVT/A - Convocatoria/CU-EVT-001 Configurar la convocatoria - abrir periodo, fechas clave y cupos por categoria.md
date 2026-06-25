---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVT-001
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-001 Configurar la convocatoria: abrir periodo, fechas clave y cupos por categoría

## Objetivo

El administrador configura las fechas clave y los cupos por categoría de la convocatoria para una edición de FILEY, dejándola activa para que los proponentes puedan enviar propuestas.

## Alcance

Módulo EVE — sección de configuración de convocatoria. Solo aplica a usuarios con permisos administrativos del módulo EVE. No cubre la creación de la edición de la feria (`EdicionFeria`).

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

El administrador decide abrir la convocatoria de una nueva edición de FILEY, o necesita reabrir una convocatoria cerrada.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.
- Existe una `EdicionFeria` activa con `ParametrosConvocatoria` sin configurar, o con una convocatoria cerrada que se desea reabrir.

## Postcondiciones

### En éxito

- `ParametrosConvocatoria` queda guardada con todas las fechas clave y los cupos por categoría.
- La convocatoria queda en estado `abierta`, habilitando el envío de propuestas.

### En fallo

- Los parámetros previos (si existían) permanecen sin cambios. No se guarda ningún valor nuevo.

## Flujo principal

1. El administrador abre la sección de configuración de convocatoria de la edición activa.
2. El sistema presenta el formulario con los siguientes parámetros:
   - Fecha de apertura de convocatoria.
   - Fecha de cierre de convocatoria.
   - Fecha de notificación de selección.
   - Fecha límite para ajustes del proponente (`fecha_cierre_ajustes_proponente`).
   - Fecha de asignación de horario.
   - Fecha de disponibilidad de constancias.
   - Cupos por categoría: `literaria_uady`, `literaria_externa`, `academica_uady`, `academica_externa`.
3. El administrador captura los valores y confirma.
4. El sistema valida que las fechas sean cronológicamente coherentes: apertura ≤ cierre < notificación ≤ asignación ≤ constancias.
5. El sistema guarda los parámetros y establece la convocatoria en estado `abierta`.
6. El sistema confirma al administrador que la convocatoria quedó configurada y publicada.

## Flujos alternos

### A1. Reabrir una convocatoria cerrada

1. El administrador selecciona una convocatoria cuyo estado es `cerrada`.
2. El sistema solicita doble verificación: "¿Confirmas que deseas reabrir esta convocatoria?"
3. El administrador confirma.
4. El sistema presenta el formulario del paso 2 con los valores anteriores precargados para que el administrador los ajuste si es necesario.
5. El flujo continúa en el paso 3 del flujo principal.

### A2. Editar parámetros con propuestas ya recibidas

1. El administrador modifica fechas o cupos cuando ya existen propuestas registradas en la edición.
2. El sistema muestra una advertencia: "Ya existen propuestas recibidas para esta edición. ¿Confirmas el cambio de parámetros?"
3. El administrador confirma.
4. El sistema aplica los cambios. Las propuestas existentes no se alteran.
5. El flujo continúa en el paso 6 del flujo principal.

### A3. Cupo de una categoría alcanzado

1. El sistema detecta que el número de propuestas aceptadas en una categoría iguala el cupo configurado.
2. El sistema notifica al administrador mediante un indicador visual en el panel de seguimiento.
3. La convocatoria continúa abierta; el administrador decide manualmente si ajusta el cupo o deja de aceptar propuestas de esa categoría.

## Flujos de excepción

### E1. Fechas cronológicamente inconsistentes

1. En el paso 4, el sistema detecta que alguna fecha viola el orden esperado.
2. El sistema resalta los campos en conflicto con un mensaje descriptivo.
3. El flujo no avanza hasta que las fechas sean válidas.

## Datos relevantes

### Entradas

- 6 fechas clave del proceso (apertura, cierre, notificación, ajustes, asignación, constancias).
- 4 cupos por categoría (literaria y académica × UADY y externa).

### Salidas

- `ParametrosConvocatoria` guardada.
- Convocatoria en estado `abierta`.
