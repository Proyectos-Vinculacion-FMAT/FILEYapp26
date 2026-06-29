---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-19
id: CU-STD-002
dominio: STD
reglas_de_negocio:
  - RN-17
---
# CU-STD-002 Editar y reenviar la solicitud tras solicitud de cambios

## Objetivo

La editorial corrige la solicitud, atendiendo los cambios solicitados por el administrador, y la reenvía para una nueva revisión, sin tener que iniciar una solicitud desde cero.

## Alcance

Componente de Stands — módulo de Solicitud. Reutiliza la misma solicitud que fue devuelta para cambios; no crea una solicitud nueva.

## Actores

### Actor principal

- Aplicante (editorial / entidad expositora)

## Disparador

El aplicante recibe el aviso de solicitud de cambios y decide corregir y reenviar su solicitud.

## Precondiciones

- El aplicante tiene sesión iniciada.
- Existe la solicitud de la editorial/cuenta en estado `cambios_solicitados`, con los detalles de la petición registrados.
- El periodo de convocatoria sigue abierto.

## Postcondiciones

### En éxito

- La misma solicitud vuelve al estado `pendiente`, con su fecha de envío actualizada y la información/documentos corregidos.
- La solicitud regresa a la cola de revisión del administrador.

### En fallo

- La solicitud permanece en estado `cambios_solicitados`; el sistema conserva las ediciones para que el aplicante las complete y reintente.

## Flujo principal

1. El aplicante consulta los cambios solicitados para su solicitud.
2. El aplicante abre la solicitud para editarla.
3. El aplicante modifica los datos y/o reemplaza los documentos según corresponda.
4. El aplicante reenvía la solicitud.
5. El sistema valida que los campos obligatorios y los documentos requeridos estén completos.
6. El sistema actualiza la misma solicitud al estado `pendiente`, registra la nueva fecha de envío y conserva la petición de cambios anterior como antecedente.
7. El sistema confirma al aplicante que su solicitud fue reenviada y se encuentra nuevamente en revisión.

## Flujos alternos

### A1. Reemplazo de un documento adjunto

1. En el paso 3, el aplicante sustituye un documento previamente cargado (p. ej. la constancia de situación fiscal o una carta de representación, RN-17).
2. El sistema reemplaza el documento conservando el historial de la solicitud.
3. El flujo continúa en el paso 4.

## Flujos de excepción

### E1. Información o documentos obligatorios faltantes

1. En el paso 5 el sistema detecta campos obligatorios o documentos requeridos sin completar.
2. El sistema señala lo que falta y no reenvía la solicitud.
3. El aplicante completa la información y reintenta el reenvío.

### E2. La solicitud ya no está en estado cambios_solicitados

1. En el paso 2 o 6 el sistema detecta que la solicitud ya no está en `cambios_solicitados` (p. ej. fue re-evaluada).
2. El sistema impide la edición y muestra el estado vigente de la solicitud.

## Datos relevantes

### Entradas

- Datos y documentos corregidos de la solicitud devuelta para cambios.

### Salidas

- Solicitud nuevamente en estado `pendiente` con acuse de reenvío.
