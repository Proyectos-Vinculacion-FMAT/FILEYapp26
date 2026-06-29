---
estado: aceptado
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVT-004
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-004 Editar una propuesta en respuesta a una solicitud de cambios del administrador

## Objetivo

El aplicante corrige su propuesta atendiendo las observaciones registradas por el administrador y la reenvía para una nueva revisión, sin tener que iniciar una solicitud desde cero.

## Alcance

Módulo EVE — edición de propuesta existente. Solo aplica cuando la propuesta está en estado `cambios_solicitados` y la fecha actual no ha superado `fecha_cierre_convocatoria`. No cubre el primer envío de propuesta (CU-EVT-002) ni el dictamen del administrador (CU-EVT-008).

## Actores

### Actor principal

- Aplicante

## Disparador

El aplicante recibe un correo notificando que el administrador solicitó cambios en una de sus propuestas.

## Precondiciones

- El aplicante tiene sesión iniciada.
- Existe al menos una propuesta propia en estado `cambios_solicitados`.
- La fecha actual es anterior o igual a `fecha_cierre_convocatoria`.

## Postcondiciones

### En éxito

- La propuesta queda en estado `pendiente`, con la fecha de reenvío registrada, lista para nueva revisión del administrador.
- Los adjuntos que el aplicante no reemplazó se conservan sin cambios.

### En fallo

- La propuesta permanece en estado `cambios_solicitados`. El aplicante puede reintentar.

## Flujo principal

1. El aplicante ingresa a "Mis propuestas" y selecciona la propuesta en estado `cambios_solicitados`.
2. El sistema muestra el detalle de la propuesta junto con el `mensaje_cambios_solicitados` registrado por el administrador.
3. El aplicante edita los campos señalados y, si aplica, reemplaza los adjuntos indicados.
4. El aplicante reenvía la propuesta.
5. El sistema valida que todos los campos obligatorios y adjuntos requeridos estén completos.
6. El sistema actualiza la `Propuesta` al estado `pendiente` y registra la fecha de reenvío.
7. El sistema confirma al aplicante que la propuesta fue reenviada y está en revisión nuevamente.

## Flujos de excepción

### E1. Plazo de respuesta vencido

1. El aplicante intenta reenviar pero la fecha actual es posterior a `fecha_cierre_convocatoria`.
2. El sistema informa que el plazo para responder ha vencido y bloquea el reenvío.
3. El sistema cambia el estado de la propuesta de `cambios_solicitados` de vuelta a `pendiente` para que el administrador la resuelva directamente.

### E2. Campos obligatorios o adjuntos faltantes

1. En el paso 5, el sistema detecta campos incompletos o adjuntos ausentes.
2. El sistema resalta cada campo en error con un mensaje descriptivo.
3. El reenvío no procede hasta que el aplicante corrija.

## Datos relevantes

### Entradas

- Los mismos campos del formulario original (CU-EVT-002), precargados con los valores enviados previamente.
- El `mensaje_cambios_solicitados` del administrador, visible como referencia durante la edición.

### Salidas

- `Propuesta` actualizada en estado `pendiente` con fecha de reenvío registrada.
