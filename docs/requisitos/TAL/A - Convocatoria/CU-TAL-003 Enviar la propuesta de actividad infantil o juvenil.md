---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - talleres
fecha: 2026-06-25
id: CU-TAL-003
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-003 Enviar la propuesta de actividad infantil o juvenil

> Borrador inicial (título y descripción). Acción de **envío**; toma los datos capturados
> en CU-TAL-002. Equivale a CU-EVT-002.1.

## Objetivo

El tallerista envía la propuesta que capturó en CU-TAL-002; el sistema realiza la validación final, crea el registro de la propuesta con folio asignado y confirma la recepción por correo. A diferencia de la convocatoria de Hipólito, **no hay un dictamen por propuesta dentro del sistema**: la confirmación de participación la comunica la coordinación por correo más adelante (en diciembre).

## Alcance

Módulo de Talleres (TAL) — acción de envío de la propuesta. Toma como entrada los datos capturados en CU-TAL-002. No cubre el llenado del formulario (CU-TAL-002) ni la edición posterior (CU-TAL-005).

## Actores

### Actor principal

- Tallerista

## Disparador

Con el formulario completo y validado (CU-TAL-002), el tallerista pulsa "Enviar".

## Notas / diferencias respecto a EVT

- Tras el envío, el sistema confirma por correo que la propuesta fue recibida; los resultados se dan a conocer en diciembre.
- Si el tallerista tiene más de una actividad, debe registrar **una propuesta por cada actividad** (ver CU-TAL-004).
