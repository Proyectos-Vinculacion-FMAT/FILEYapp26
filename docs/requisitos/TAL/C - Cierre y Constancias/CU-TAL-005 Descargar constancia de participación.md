---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/tal
fecha: 2026-06-29
id: CU-TAL-005
dominio: TAL
reglas_de_negocio:
  - La constancia se genera siempre de forma automática, independientemente de si los nombres capturados por el tallerista son correctos.
  - El diseño (texto, imagen de fondo y campos a rellenar) es hardcodeado, no configurable.
---
# CU-TAL-005 Descargar constancia de participación

> [!note] Evidencia (2026-06-29)
> CU-TAL-002 ya captura, desde el primer registro, el campo **"Nombre completo de los
> participantes que recibirán constancia"** — confirma que los talleristas sí tienen derecho
> a constancia, igual que los proponentes de `EVT` (CU-EVT-005). La generación automática e
> incondicional, con diseño hardcodeado y plantilla pendiente como único bloqueante, está
> confirmada para este dominio en
> [RSM - Junta 3 con organizadores FILEY](<../../../soporte/meetings/resumenes/RSM - Junta 3 con organizadores FILEY.md>)
> (sesión centrada en el área de Elvira, que trató explícitamente "las constancias de
> participación").

## Objetivo

El tallerista descarga la constancia de participación de su actividad una vez concluida la feria, para acreditar su participación en FILEY.

## Alcance

Módulo de Talleres (TAL) — entrega de constancias al tallerista. Aplica a actividades `aceptadas`/`programada` cuyos participantes fueron declarados en CU-TAL-002. No cubre la configuración de la fecha a partir de la cual se habilitan (pendiente de definir; ver "Pendientes" en `CU-TAL Índice.md`).

## Actores

### Actor principal

- Tallerista

## Disparador

El tallerista entra a la app, después de la feria, para obtener su constancia.

## Precondiciones

- El tallerista tiene sesión iniciada.
- El tallerista tiene al menos una actividad `aceptada` con participantes declarados para constancia (CU-TAL-002).

## Postcondiciones

### En éxito

- El tallerista obtiene el archivo de constancia de su actividad.

### En fallo

- No se genera ni entrega la constancia; el sistema informa el motivo.

## Flujo principal

1. El tallerista accede a la sección "Mis constancias".
2. El sistema lista las actividades del tallerista elegibles para constancia.
3. El tallerista selecciona la actividad de la que desea su constancia.
4. El sistema genera la constancia con los datos de la actividad y los nombres de participantes declarados.
5. El sistema entrega el archivo para su descarga.

## Flujos alternos

### A1. Varias actividades elegibles

1. En el paso 2, el tallerista tiene más de una actividad elegible (p. ej. repitió el taller varias veces).
2. El sistema muestra todas y permite descargar la constancia de cada una por separado.

## Flujos de excepción

### E1. Sin actividades elegibles

1. En el paso 2, el tallerista no tiene actividades aceptadas con participantes declarados.
2. El sistema informa que no hay constancias disponibles para su cuenta.

## Datos relevantes

### Entradas

- Selección de la actividad de la que se desea la constancia.

### Salidas

- Archivo de constancia de participación de la actividad seleccionada.
