---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/tal
fecha: 2026-06-29
id: CU-TAL-010
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-010 Enviar notificaciones de resultado en lote

> [!note] Equivalente a CU-EVT-010
> Sin evidencia directa de que Elvira notifique en lote en vez de caso por caso (a diferencia
> de CU-EVT-010, que sí cita esa evidencia para Hipólito); se extrapola por simetría. La
> notificación de **cambios solicitados** sí es inmediata (CU-TAL-009, A1), igual que en `EVT`.

## Objetivo

Elvira comunica los resultados de la revisión enviando las notificaciones de las propuestas aceptadas y rechazadas, dejando constancia del envío.

## Alcance

Módulo de Talleres (TAL) — notificación de resultados de revisión. Cubre las propuestas en estado `aceptada` o `rechazada` pendientes de comunicar. La solicitud de cambios se notifica de inmediato en CU-TAL-009 y no entra en este lote. No cubre la notificación de sala y horario, responsabilidad de `PRG` (ver CU-PRG-008 en `PRG/CU-PRG Índice.md`).

## Actores

### Actor principal

- Administrador (Elvira)

### Actores secundarios

- Sistema (compone y envía el lote de correos).

## Disparador

Elvira termina (total o parcialmente) su revisión y decide comunicar los resultados acumulados.

## Precondiciones

- Elvira tiene sesión iniciada con permisos del módulo TAL.
- Existe al menos una propuesta en estado `aceptada` o `rechazada` pendiente de notificar.

## Postcondiciones

### En éxito

- Cada propuesta incluida queda marcada como notificada.
- Cada tallerista recibe un correo con el resultado de su(s) propuesta(s).

### En fallo

- Las propuestas conservan su estado de notificación previo para reintentar.

## Flujo principal

1. Elvira abre la sección de notificación de resultados.
2. El sistema muestra las propuestas pendientes de notificar (estado `aceptada` o `rechazada`).
3. Elvira selecciona cuáles incluir, con la opción de "Incluir todas".
4. Elvira confirma el envío.
5. El sistema compone, por cada propuesta incluida, un correo con el resultado (aceptada / rechazada) y el motivo cuando aplique.
6. El sistema envía los correos y marca cada propuesta incluida como notificada.
7. El sistema confirma a Elvira el total de notificaciones enviadas.

## Flujos de excepción

### E1. Sin propuestas pendientes de notificar

1. En el paso 2, no existen propuestas pendientes de notificar.
2. El sistema informa que no hay resultados pendientes de comunicar.

### E2. Fallo parcial en el envío

1. En el paso 6, el envío de uno o más correos falla.
2. El sistema marca como notificadas solo las propuestas cuyo correo se envió correctamente y reporta a Elvira las que fallaron para reintentar.

## Datos relevantes

### Entradas

- Selección de propuestas a incluir (o "Incluir todas").

### Salidas

- Propuestas incluidas marcadas como notificadas.
- Correos de resultado a los talleristas.
