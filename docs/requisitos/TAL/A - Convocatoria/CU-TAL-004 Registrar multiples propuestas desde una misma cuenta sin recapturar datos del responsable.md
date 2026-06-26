---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - talleres
fecha: 2026-06-25
id: CU-TAL-004
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-004 Registrar múltiples propuestas desde una misma cuenta sin recapturar datos del responsable

> Borrador inicial (título y descripción). Equivale a CU-EVT-003.

## Objetivo

El tallerista registra una segunda propuesta —o más— durante la misma sesión o en sesiones posteriores sin tener que volver a capturar los datos del responsable, que el sistema reutiliza automáticamente; se mantiene la regla de **una propuesta por actividad**.

## Alcance

Módulo de Talleres (TAL) — extensión del flujo de registro de propuesta (CU-TAL-002 / CU-TAL-003). Aplica mientras la convocatoria esté `abierta`. No cubre el primer registro de propuesta.

## Actores

### Actor principal

- Tallerista

## Disparador

Tras enviar una propuesta exitosamente, el tallerista elige registrar otra actividad adicional en la misma edición.

## Notas / diferencias respecto a EVT

- La convocatoria infantil/juvenil indica explícitamente llenar **un formulario por cada actividad**; este CU evita recapturar los datos del responsable en cada uno.
