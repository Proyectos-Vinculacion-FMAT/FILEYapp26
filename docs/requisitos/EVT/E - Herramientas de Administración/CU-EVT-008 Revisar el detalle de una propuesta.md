---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/evt
fecha: 2026-06-24
id: CU-EVT-008
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-008 Revisar el detalle de una propuesta

## Objetivo

El administrador examina toda la información de una propuesta —datos del proponente, descripción de la actividad y archivos adjuntos— para contar con los elementos necesarios y emitir un dictamen.

## Alcance

Módulo EVT — vista de detalle de propuesta. Es la antesala del dictamen (CU-EVT-009). No cubre la edición de la propuesta por parte del proponente (CU-EVT-004).

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

El administrador selecciona una propuesta desde la lista (CU-EVT-007).

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.
- La propuesta existe en la edición activa.

## Postcondiciones

### En éxito

- Se muestra el detalle completo de la propuesta y sus adjuntos.

### En fallo

- No se muestra el detalle; se informa la condición (propuesta inexistente o error de consulta).

## Flujo principal

1. El administrador selecciona una propuesta desde la lista.
2. El sistema muestra los datos del proponente: nombre completo, correo, teléfono, dependencia o institución, cargo y ciudad/estado.
3. El sistema muestra los datos de la actividad: tipo, título, organiza, participantes, moderador, público al que va dirigido, si requiere constancia, categoría y estado actual.
4. El sistema lista los adjuntos (semblanzas, sinopsis y, según el tipo, portada y fotografía) con acceso para visualizarlos o descargarlos.
5. Si la propuesta tiene historial (cambios solicitados previos, reenvíos o un dictamen anterior), el sistema lo muestra como antecedente.
6. Desde el detalle, el administrador puede iniciar el dictamen (CU-EVT-009).

## Flujos alternos

### A1. Propuesta de tipo "Presentación de libro" o "Presentación de revista"

1. En el paso 3, el sistema muestra adicionalmente los campos de publicación: título de la publicación, rol del proponente, autores/editores, editorial, sinopsis extendida e indicador de recepción del ejemplar físico (`ejemplar_fisico_recibido`).
2. El flujo continúa en el paso 4.

## Flujos de excepción

### E1. Adjunto no disponible

1. En el paso 4, el sistema no puede recuperar uno de los archivos adjuntos.
2. El sistema muestra el resto del detalle e indica que el adjunto no está disponible, sin bloquear la consulta.

## Datos relevantes

### Entradas

- Identificador o folio de la propuesta.

### Salidas

- Vista de detalle: datos del proponente, datos de la actividad, adjuntos y antecedentes.
