---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/evt
fecha: 2026-06-24
id: CU-EVT-011
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-011 Visualizar el número de propuestas por estado

## Objetivo

El administrador visualiza en todo momento cuántas propuestas lleva aceptadas y rechazadas y cuántos espacios quedan disponibles por categoría, para tomar decisiones de selección informadas frente a los cupos configurados.

## Alcance

Módulo EVT — herramienta de administración (panel de seguimiento de la selección), separada del flujo de revisión propiamente dicho. Es una vista de solo lectura que se actualiza con cada dictamen (CU-EVT-009). No modifica propuestas ni cupos.

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

El administrador consulta el panel de seguimiento mientras revisa propuestas.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVT.
- La edición activa tiene `ParametrosConvocatoria` configurada con cupos por categoría.

## Postcondiciones

### En éxito

- Se muestran los contadores actualizados de propuestas por estado y los espacios disponibles por categoría.

### En fallo

- No se muestran los contadores; se informa el error de consulta.

## Flujo principal

1. El administrador abre el panel de seguimiento (o consulta el contador embebido en la lista de propuestas).
2. El sistema calcula, para la edición activa: total de propuestas recibidas, número de `pendiente`, `cambios_solicitados`, `aceptada` y `rechazada`.
3. El sistema calcula, por cada categoría (`literaria_uady`, `literaria_externa`, `academica_uady`, `academica_externa`), las aceptadas frente al cupo configurado y los espacios disponibles restantes.
4. El sistema presenta los contadores; los valores reflejan el estado vigente al momento de la consulta.

## Flujos alternos

### A1. Cupo de una categoría alcanzado o superado

1. En el paso 3, el sistema detecta que las aceptadas de una categoría igualan o superan el cupo.
2. El sistema resalta visualmente esa categoría como "cupo alcanzado", sin impedir aceptar más propuestas (la decisión sigue siendo del administrador).

## Flujos de excepción

### E1. Cupos no configurados

1. En el paso 3, el sistema detecta que la edición no tiene cupos configurados.
2. El sistema muestra los contadores por estado y omite el cálculo de espacios disponibles, indicando que faltan cupos por configurar (CU-EVT-001).

## Datos relevantes

### Entradas

- Ninguna; el sistema deriva los contadores de las propuestas y los cupos de la edición activa.

### Salidas

- Contadores por estado (pendiente, cambios solicitados, aceptada, rechazada).
- Espacios disponibles por categoría (aceptadas vs. cupo).
