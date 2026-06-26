---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - talleres
fecha: 2026-06-25
id: CU-TAL-001
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-001 Configurar la convocatoria de actividades infantiles y juveniles

> Borrador inicial (título y descripción). El flujo detallado se redactará después.
> Equivale a CU-EVT-001 pero para la convocatoria que administra Elvira (talleres / actividades
> dirigidas a infancias y juventudes), que tiene parámetros distintos a la de Hipólito.

## Objetivo

El administrador configura la convocatoria de actividades dirigidas a infancias y juventudes para una edición de FILEY —periodo de recepción, fecha límite, modalidades admitidas (presencial / virtual), espacios disponibles y cupos—, dejándola activa para que los talleristas puedan registrar sus propuestas.

## Alcance

Módulo de Talleres (TAL) — sección de configuración de convocatoria. Solo aplica a usuarios con permisos administrativos del módulo TAL (equipo de Elvira). No cubre la creación de la edición de la feria (`EdicionFeria`), ni la convocatoria de actividades del programa general (CU-EVT-001, Hipólito).

## Actores

### Actor principal

- Administrador (Elvira / equipo de actividades infantiles y juveniles)

## Disparador

El administrador decide abrir la convocatoria de actividades infantiles/juveniles de una nueva edición de FILEY.

## Notas / diferencias respecto a EVT

- La duración de las actividades es fija (45–50 min), no se configuran bloques por categoría literaria/académica.
- Se contemplan dos modalidades: presencial (talleristas locales o con patrocinio) y virtual (talleristas fuera de Mérida).
- Los espacios son específicos del público infantil/juvenil (p. ej. Salón Ek Balam subdividido, Salas de cine).
