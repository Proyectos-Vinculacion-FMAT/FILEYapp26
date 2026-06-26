---
estado: aceptado
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-25
id: CU-EVT-002.1
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-002.1 Enviar la propuesta de actividad

> Acción de **envío** de la propuesta. Es el paso de cierre del registro: toma los datos
> ya capturados y validados en CU-EVT-002 y los persiste creando el registro `Propuesta`.

## Objetivo

El aplicante envía la propuesta que capturó en CU-EVT-002; el sistema realiza la validación final, crea el registro `Propuesta` en estado `pendiente` con folio asignado, almacena los adjuntos y confirma la recepción por correo, dejando la propuesta en la cola de revisión del administrador.

## Alcance

Módulo EVE — acción de envío de la propuesta. Toma como entrada los datos capturados en CU-EVT-002. No cubre el llenado del formulario (CU-EVT-002) ni la edición posterior de una propuesta enviada (CU-EVT-004).

## Actores

### Actor principal

- Aplicante (proponente externo o UADY)

## Disparador

Con el formulario completo y validado (CU-EVT-002), el aplicante pulsa "Enviar".

## Precondiciones

- El aplicante tiene sesión iniciada.
- Los datos de la propuesta están capturados y validados (CU-EVT-002).
- La convocatoria está en estado `abierta`.

## Postcondiciones

### En éxito

- Se crea un registro `Propuesta` en estado `pendiente`, con folio asignado, vinculado al proponente y a la edición activa.
- El campo `categoria` queda con el sufijo `_uady` o `_externo` derivado automáticamente por el sistema; el prefijo (`literaria` / `academica`) permanece pendiente hasta el dictamen del administrador (CU-EVT-008).
- Los archivos adjuntos quedan almacenados como registros `PropuestaAdjunto`.
- El aplicante recibe por correo la confirmación de envío con su número de folio.

### En fallo

- No se crea ningún registro. El sistema devuelve al aplicante al formulario (CU-EVT-002) conservando los datos para corregir y reintentar.

## Flujo principal

1. El aplicante envía la propuesta.
2. El sistema realiza la validación final de que todos los campos obligatorios y adjuntos requeridos estén completos.
3. El sistema deriva el sufijo de `categoria`: `_uady` si `tipo_participante = uady`, `_externo` en cualquier otro caso.
4. El sistema registra la `Propuesta` en estado `pendiente` con su folio y fecha de envío.
5. El sistema almacena cada archivo adjunto como un registro `PropuestaAdjunto`.
6. El sistema envía al aplicante un correo con el número de folio y la confirmación de recepción.
7. El sistema presenta las opciones "Crear una nueva solicitud" (CU-EVT-003) y "Cerrar".

## Flujos de excepción

### E1. Convocatoria cerrada al momento del envío

1. En el paso 2, el sistema verifica que la fecha actual es posterior a `fecha_cierre_convocatoria`.
2. El sistema informa al aplicante que la convocatoria ya cerró y no acepta el envío.
3. No se crea ningún registro.

### E2. Campos obligatorios o adjuntos faltantes en la validación final

1. En el paso 2, el sistema detecta campos obligatorios sin completar o adjuntos ausentes.
2. El sistema devuelve al aplicante al formulario (CU-EVT-002) resaltando lo que falta.
3. El envío no procede hasta que el aplicante corrija y reintente.

## Datos relevantes

### Entradas

- Los datos del formulario capturados y validados en CU-EVT-002 (datos de perfil, datos de la actividad por tipo y adjuntos).

### Salidas

- `Propuesta` en estado `pendiente` con folio asignado y fecha de envío.
- Registros `PropuestaAdjunto` por cada archivo adjuntado.
- Correo de confirmación al aplicante con número de folio.
