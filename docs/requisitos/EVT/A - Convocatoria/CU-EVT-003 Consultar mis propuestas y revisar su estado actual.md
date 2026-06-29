---
estado: acpetado
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVT-005
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-005 Consultar mis propuestas y revisar su estado actual

> chechar si habria que separarlo , en talleres y eventos, porque si puredes condualtar propuestas de

## Objetivo

El aplicante revisa el estado actualizado de todas sus propuestas enviadas en la edición activa, incluyendo los mensajes del administrador cuando los haya, para saber si debe actuar o simplemente esperar.

## Alcance

Módulo EVE — vista de seguimiento del proponente. Muestra únicamente las propuestas asociadas a la cuenta con sesión activa. No cubre la edición de propuestas, que corresponde a CU-EVT-004.

## Actores

### Actor principal

- Aplicante

## Disparador

El aplicante desea conocer el estado actual de sus propuestas enviadas.

## Precondiciones

- El aplicante tiene sesión iniciada.

## Postcondiciones

### En éxito

- El aplicante visualiza el listado completo de sus propuestas con sus estados actuales y, cuando aplica, los mensajes del administrador asociados.

### En fallo

- No aplica; es un flujo de solo lectura.

## Flujo principal

1. El aplicante accede a la sección "Mis propuestas".
2. El sistema lista todas las propuestas del proponente para la edición activa, mostrando por cada una: folio, tipo de actividad, título y estado actual.
3. El aplicante selecciona una propuesta para ver su detalle.
4. El sistema muestra el detalle completo: todos los datos enviados, estado actual y —según el estado— la información adicional correspondiente:
   - Si `cambios_solicitados`: el `mensaje_cambios_solicitados` del administrador y acceso directo a CU-EVT-004.
   - Si `rechazada`: el `motivo_rechazo` registrado por el administrador.
   - Si `aceptada`: confirmación de aceptación; la sala y horario se comunicarán en una notificación posterior.
   - Si `pendiente`: indicación de que la propuesta está en revisión.

## Flujos de excepción

### E1. Sin propuestas registradas en la edición activa

1. En el paso 2, el sistema no encuentra propuestas del proponente en la edición activa.
2. El sistema muestra un mensaje informativo y ofrece acceso directo al formulario de envío de propuesta (CU-EVT-002).

## Datos relevantes

### Entradas

- Ninguna; el sistema deriva el listado de la sesión activa del proponente.

### Salidas

- Vista de listado: folio, tipo de actividad, título y estado de cada propuesta.
- Vista de detalle: todos los datos enviados más el mensaje o motivo del administrador cuando aplique.
