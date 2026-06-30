---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/evt
fecha: 2026-06-24
id: CU-EVT-005
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-005 Descargar constancia de participación

## Objetivo

El proponente descarga la constancia de participación de su actividad una vez concluida la feria, a partir de la fecha configurada, para acreditar su participación en FILEY.

## Alcance

Módulo EVT — entrega de constancias al proponente. Solo aplica a actividades que solicitaron constancia (`requiere_constancia = true`) y a partir de `fecha_constancias`. No cubre la configuración de esa fecha (CU-EVT-001).

## Actores

### Actor principal

- Aplicante (proponente)

## Disparador

El proponente entra a la app, después de la feria, para obtener su constancia.

## Precondiciones

- El proponente tiene sesión iniciada.
- La fecha actual es igual o posterior a `fecha_constancias`.
- El proponente tiene al menos una actividad confirmada que solicitó constancia (`requiere_constancia = true`).

## Postcondiciones

### En éxito

- El proponente obtiene el archivo de constancia de su actividad.

### En fallo

- No se genera ni entrega la constancia; el sistema informa el motivo.

## Flujo principal

1. El proponente accede a la sección "Mis constancias".
2. El sistema lista las actividades del proponente elegibles para constancia (confirmadas y con `requiere_constancia = true`).
3. El proponente selecciona la actividad de la que desea su constancia.
4. El sistema genera la constancia con los datos de la actividad y del participante.
5. El sistema entrega el archivo para su descarga.

## Flujos alternos

### A1. Varias actividades elegibles

1. En el paso 2, el proponente tiene más de una actividad elegible.
2. El sistema muestra todas y permite descargar la constancia de cada una por separado.

## Flujos de excepción

### E1. Constancias aún no disponibles

1. En el paso 1, la fecha actual es anterior a `fecha_constancias`.
2. El sistema informa la fecha a partir de la cual las constancias estarán disponibles y no permite la descarga.

### E2. Sin actividades elegibles

1. En el paso 2, el proponente no tiene actividades confirmadas que hayan solicitado constancia.
2. El sistema informa que no hay constancias disponibles para su cuenta.

## Datos relevantes

### Entradas

- Selección de la actividad de la que se desea la constancia.

### Salidas

- Archivo de constancia de participación de la actividad seleccionada.
