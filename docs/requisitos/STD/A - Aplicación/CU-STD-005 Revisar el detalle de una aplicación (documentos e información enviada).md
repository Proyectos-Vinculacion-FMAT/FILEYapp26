---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-19
id: CU-STD-005
dominio: STD
reglas_de_negocio: []
---
# CU-STD-005 Revisar el detalle de una aplicación (documentos e información enviada)

## Objetivo

El administrador revisa toda la información y los documentos enviados en una aplicación para sustentar su decisión de aceptarla, rechazarla o solicitar cambios.

## Alcance

Componente de Stands — módulo de Aplicación. Vista de detalle del administrador; es el punto desde el que se disparan la aceptación o rechazo definitivo (CU-STD-006) y la solicitud de cambios (CU-STD-007).

## Actores

### Actor principal

- Administrador (coordinador del showfloor)

## Disparador

El administrador selecciona una aplicación desde la lista (CU-STD-004).

## Precondiciones

- El administrador tiene sesión iniciada con rol de administrador.
- La aplicación existe.

## Postcondiciones

### En éxito

- Se muestran los datos y documentos de la aplicación; el administrador queda en posición de aceptarla, rechazarla o solicitar cambios.

### En fallo

- No se muestra el detalle; se informa la causa (aplicación inexistente o documento no disponible).

## Flujo principal

1. El administrador abre una aplicación desde la lista.
2. El sistema muestra los datos de la editorial, sus contactos, sellos, materiales y temáticas.
3. El sistema muestra los documentos adjuntos: constancia de situación fiscal, lista de títulos y, en su caso, las cartas de representación.
4. El administrador consulta y/o descarga los documentos.
5. El administrador procede a aceptar o rechazar (CU-STD-006) o solicitar cambios (CU-STD-007) a la aplicación.

## Flujos alternos

### A1. Aplicación ya resuelta (solo lectura)

1. En el paso 1 la aplicación ya está `aceptada`, `rechazada` o en `cambios_solicitados`.
2. El sistema muestra el detalle en modo consulta, incluyendo el resultado, la fecha de revisión y, si aplica (rechazada o cambios solicitados), el motivo o petición.
3. El caso de uso termina sin habilitar nuevas acciones de resolución.

## Flujos de excepción

### E1. Documento no disponible

1. En el paso 3 o 4 un documento adjunto no puede recuperarse o está dañado.
2. El sistema informa la incidencia y permite continuar revisando el resto de la información.

## Datos relevantes

### Entradas

- Identificador de la aplicación a revisar.

### Salidas

- Detalle de la aplicación: datos de la editorial y documentos adjuntos.
