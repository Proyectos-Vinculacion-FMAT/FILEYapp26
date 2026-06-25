---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-19
id: CU-STD-008
dominio: STD
reglas_de_negocio:
  - RN-16
---
# CU-STD-008 Notificar al usuario el resultado de su aplicación

## Objetivo

El sistema informa por correo a la editorial el resultado de su aplicación (aceptada, rechazada o con cambios solicitados), para que conozca el desenlace y los pasos siguientes.

## Alcance

Componente de Stands — módulo de Aplicación. Proceso automático disparado por la resolución de una aplicación (CU-STD-006 o CU-STD-007). La notificación es por correo; no contempla notificaciones dentro del sistema.

## Actores

### Actor principal

- Sistema

### Actores secundarios

- Servicio de correo

## Disparador

Una aplicación cambia de estado a `aceptada`, `rechazada` o `cambios_solicitados`.

## Precondiciones

- La aplicación tiene un resultado registrado (`aceptada`, `rechazada` o `cambios_solicitados`).
- La editorial cuenta con un correo de contacto válido.

## Postcondiciones

### En éxito

- Se envía el correo con el resultado al contacto de la editorial.
- Se registra la notificación (tipo, fecha de envío y estado `enviada`).

### En fallo

- La notificación queda registrada con estado `fallida` y se avisa al administrador para su atención.

## Flujo principal

1. El sistema detecta el cambio de estado de la aplicación a `aceptada`, `rechazada` o `cambios_solicitados`.
2. El sistema compone el mensaje según el resultado: si fue aceptada, indica que la editorial queda habilitada para reservar stands (RN-16); si fue rechazada, notifica la invalidación definitiva; si requiere cambios, incluye la petición e indica que puede editar y reenviar la aplicación (CU-STD-002).
3. El sistema envía el correo al contacto de la editorial.
4. El sistema registra la notificación con su tipo, fecha y estado `enviada`.

## Flujos alternos

### A1. Resultado: rechazada

1. En el paso 2, al ser rechazada de forma definitiva, el mensaje notifica que la aplicación ha sido invalidada para este ciclo.
2. El flujo continúa en el paso 3.

### A2. Resultado: cambios_solicitados

1. En el paso 2, al requerir cambios, el mensaje incluye los detalles de la petición de cambios y la indicación de reenvío.
2. El flujo continúa en el paso 3.

## Flujos de excepción

### E1. Fallo en el envío del correo

1. En el paso 3 el servicio de correo no logra enviar el mensaje.
2. El sistema registra la notificación con estado `fallida`.
3. El sistema avisa al administrador para que atienda el envío.

## Datos relevantes

### Entradas

- Aplicación resuelta (resultado y, en su caso, petición de cambios).
- Correo de contacto de la editorial.

### Salidas

- Correo enviado al usuario y registro de la notificación.
