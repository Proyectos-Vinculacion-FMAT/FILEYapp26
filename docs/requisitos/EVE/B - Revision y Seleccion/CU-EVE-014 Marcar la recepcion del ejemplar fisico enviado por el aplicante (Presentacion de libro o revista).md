---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVE-014
dominio: EVE
reglas_de_negocio: []
---
# CU-EVE-014 Marcar la recepción del ejemplar físico enviado por el aplicante (Presentación de libro/revista)

## Objetivo

El administrador registra que recibió el ejemplar físico que el proponente debía enviar a las oficinas de FILEY para una presentación de libro o revista, dejando constancia de cumplimiento de ese requisito.

## Alcance

Módulo EVE — seguimiento de requisitos de la propuesta. Solo aplica a tipos de actividad cuyo `TipoActividad.requiere_ejemplar_fisico = true` (Presentación de libro y Presentación de revista). Es un registro de control independiente del dictamen.

## Actores

### Actor principal

- Administrador (Hipólito) o su equipo de la Coordinación General de Contenidos.

## Disparador

El administrador recibe físicamente el ejemplar enviado por el proponente y lo registra en el sistema.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.
- La propuesta es de un tipo de actividad que requiere ejemplar físico (`requiere_ejemplar_fisico = true`).

## Postcondiciones

### En éxito

- La propuesta queda con `ejemplar_fisico_recibido = true`, indicando que el ejemplar fue recibido.

### En fallo

- El indicador permanece sin cambios.

## Flujo principal

1. El administrador abre el detalle de la propuesta (CU-EVE-008) cuyo tipo requiere ejemplar físico.
2. El sistema muestra el indicador de recepción del ejemplar (`ejemplar_fisico_recibido`) y su estado actual.
3. El administrador marca el ejemplar como recibido.
4. El sistema actualiza `ejemplar_fisico_recibido = true`.
5. El sistema confirma el registro de la recepción.

## Flujos alternos

### A1. Revertir una marca de recepción

1. En el paso 3, el administrador detecta que marcó la recepción por error.
2. El administrador desmarca el indicador.
3. El sistema actualiza `ejemplar_fisico_recibido = false` y confirma el cambio.

## Flujos de excepción

### E1. La propuesta no requiere ejemplar físico

1. En el paso 2, el sistema detecta que el tipo de actividad no requiere ejemplar físico.
2. El sistema no muestra el indicador de recepción y la acción no está disponible.

## Datos relevantes

### Entradas

- Identificador o folio de la propuesta.
- Marca de recepción (recibido / no recibido).

### Salidas

- Propuesta con `ejemplar_fisico_recibido` actualizado.
