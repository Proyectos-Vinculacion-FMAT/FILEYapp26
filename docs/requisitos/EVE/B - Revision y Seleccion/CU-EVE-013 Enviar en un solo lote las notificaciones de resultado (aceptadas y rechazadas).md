---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-24
id: CU-EVE-013
dominio: EVE
reglas_de_negocio: []
---
# CU-EVE-013 Enviar en un solo lote las notificaciones de resultado (aceptadas y rechazadas)

## Objetivo

El administrador comunica los resultados de la selección enviando en un solo lote las notificaciones de las propuestas aceptadas y rechazadas, dejando constancia del envío para deslindar responsabilidad ante quien alegue no haber recibido el aviso.

## Alcance

Módulo EVE — notificación de resultados de selección. Cubre las propuestas en estado `aceptada` o `rechazada` pendientes de comunicar. La solicitud de cambios se notifica de inmediato en CU-EVE-009 y no entra en este lote. No cubre la notificación de sala y horario (CU-EVE-023).

## Actores

### Actor principal

- Administrador (Hipólito)

### Actores secundarios

- Sistema (compone y envía el lote de correos).

## Disparador

El administrador termina (total o parcialmente) su revisión y decide comunicar los resultados acumulados.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVE.
- Existe al menos una propuesta en estado `aceptada` o `rechazada` con `resultado_notificado = false`.

## Postcondiciones

### En éxito

- Se crea un registro `NotificacionLote` de tipo `seleccion` con la fecha de envío, el administrador que lo envió y el total de notificaciones.
- Cada propuesta incluida queda marcada con `resultado_notificado = true` y `fecha_resultado_notificado = ahora`.
- Cada proponente recibe un correo con el resultado de su(s) propuesta(s).

### En fallo

- No se crea el lote; las propuestas conservan su estado de notificación previo para reintentar.

## Flujo principal

1. El administrador abre la sección de notificación de resultados.
2. El sistema muestra las propuestas pendientes de notificar (estado `aceptada` o `rechazada` con `resultado_notificado = false`).
3. El administrador selecciona cuáles incluir, con la opción de "Incluir todas".
4. El administrador confirma el envío del lote.
5. El sistema compone, por cada propuesta incluida, un correo con: estado (aceptada / rechazada), nombre de la actividad y motivo (el `motivo_rechazo` cuando aplique).
6. El sistema envía los correos, crea el registro `NotificacionLote` (tipo `seleccion`) y marca cada propuesta incluida como notificada (`resultado_notificado = true`, `fecha_resultado_notificado = ahora`).
7. El sistema confirma al administrador el total de notificaciones enviadas.

## Flujos alternos

### A1. Lote de actualización (resultado ya notificado que cambió)

1. En el paso 5, el sistema detecta propuestas que ya tenían una notificación previa (`fecha_resultado_notificado` no nula) y cuyo dictamen cambió (CU-EVE-009, A3).
2. El sistema marca esos correos explícitamente como **actualización** del resultado comunicado anteriormente, para evitar confusión con la notificación previa.
3. El flujo continúa en el paso 6.

### A2. Envío de múltiples lotes

1. El administrador puede repetir este caso de uso tantas veces como necesite a lo largo de su revisión.
2. Cada nuevo lote incluye únicamente las propuestas pendientes de notificar en ese momento, evitando reenviar resultados ya comunicados que no han cambiado.

## Flujos de excepción

### E1. Sin propuestas pendientes de notificar

1. En el paso 2, no existen propuestas con `resultado_notificado = false`.
2. El sistema informa que no hay resultados pendientes de comunicar y no permite crear un lote vacío.

### E2. Fallo parcial en el envío

1. En el paso 6, el envío de uno o más correos falla.
2. El sistema registra el `NotificacionLote` con estado `fallida_parcial`, marca como notificadas solo las propuestas cuyo correo se envió correctamente y reporta al administrador las que fallaron para reintentar.

## Datos relevantes

### Entradas

- Selección de propuestas a incluir en el lote (o "Incluir todas").

### Salidas

- `NotificacionLote` (tipo `seleccion`) con fecha, remitente y total enviado.
- Propuestas incluidas marcadas como notificadas.
- Correos de resultado a los proponentes (estado, actividad y motivo cuando aplica).
