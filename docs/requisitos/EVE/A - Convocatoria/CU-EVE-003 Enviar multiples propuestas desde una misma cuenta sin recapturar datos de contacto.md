---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVE-003
dominio: EVE
reglas_de_negocio: []
---
# CU-EVE-003 Enviar múltiples propuestas desde una misma cuenta sin recapturar datos de contacto

## Objetivo

El aplicante registra una segunda propuesta —o más— durante la misma sesión o en sesiones posteriores sin tener que volver a capturar sus datos de contacto y perfil, que el sistema reutiliza automáticamente.

## Alcance

Módulo EVE — extensión del flujo de envío de propuesta (CU-EVE-002). Aplica mientras la convocatoria esté en estado `abierta`. No cubre el primer registro de propuesta, que corresponde a CU-EVE-002.

## Actores

### Actor principal

- Aplicante

## Disparador

Tras enviar una propuesta exitosamente, el aplicante elige registrar otra actividad adicional en la misma edición.

## Precondiciones

- El aplicante tiene sesión iniciada.
- La convocatoria está en estado `abierta`.
- Existe al menos una propuesta enviada por el proponente en la edición activa.

## Postcondiciones

### En éxito

- Se crea una nueva `Propuesta` en estado `pendiente` con folio propio, vinculada al mismo proponente y a la misma edición.
- Los datos de contacto y perfil del proponente no se recapturan.

### En fallo

- No se crea ningún registro. La propuesta anterior enviada permanece sin cambios.

## Flujo principal

1. Tras completar el envío de una propuesta (CU-EVE-002, paso 11), el sistema presenta las opciones: "Crear una nueva solicitud" y "Cerrar".
2. El aplicante selecciona "Crear una nueva solicitud".
3. El sistema presenta el formulario de propuesta con los datos de contacto y perfil ya precargados. Estos campos no son editables en este flujo; si el aplicante necesita modificarlos debe hacerlo desde su perfil.
4. El flujo continúa desde el paso 4 de CU-EVE-002 (selección de tipo de actividad).

## Flujos de excepción

### E1. Convocatoria cerrada al intentar crear nueva solicitud

1. El aplicante intenta crear una nueva propuesta pero la convocatoria ya cerró.
2. El sistema informa que la convocatoria ya no está activa y no presenta el formulario.
3. El sistema ofrece únicamente la opción "Cerrar".

## Datos relevantes

### Entradas

- Los mismos campos del formulario original (CU-EVE-002), con los datos de contacto y perfil precargados.

### Salidas

- Nueva `Propuesta` en estado `pendiente` con folio propio.
- Registros `PropuestaAdjunto` por cada archivo adjuntado.
- Correo de confirmación al aplicante con el nuevo número de folio.
