---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - stands
fecha: 2026-06-19
id: CU-STD-002
dominio: STD
reglas_de_negocio:
  - RN-17
---
# CU-STD-002 Editar y reenviar la aplicación tras solicitud de cambios

## Objetivo

La editorial corrige la aplicación, atendiendo los cambios solicitados por el administrador, y la reenvía para una nueva revisión, sin tener que iniciar una solicitud desde cero.

## Alcance

Componente de Stands — módulo de Aplicación. Reutiliza la misma aplicación que fue devuelta para cambios; no crea una solicitud nueva.

## Actores

### Actor principal

- Usuario (editorial / entidad expositora)

## Disparador

El usuario recibe el aviso de solicitud de cambios y decide corregir y reenviar su aplicación.

## Precondiciones

- El usuario tiene sesión iniciada.
- Existe la aplicación de la editorial/cuenta en estado `cambios_solicitados`, con los detalles de la petición registrados.
- El periodo de convocatoria sigue abierto.

## Postcondiciones

### En éxito

- La misma aplicación vuelve al estado `pendiente`, con su fecha de envío actualizada y la información/documentos corregidos.
- La aplicación regresa a la cola de revisión del administrador.

### En fallo

- La aplicación permanece en estado `cambios_solicitados`; el sistema conserva las ediciones para que el usuario las complete y reintente.

## Flujo principal

1. El usuario consulta los cambios solicitados para su aplicación.
2. El usuario abre la aplicación para editarla.
3. El usuario modifica los datos y/o reemplaza los documentos según corresponda.
4. El usuario reenvía la aplicación.
5. El sistema valida que los campos obligatorios y los documentos requeridos estén completos.
6. El sistema actualiza la misma aplicación al estado `pendiente`, registra la nueva fecha de envío y conserva la petición de cambios anterior como antecedente.
7. El sistema confirma al usuario que su aplicación fue reenviada y se encuentra nuevamente en revisión.

## Flujos alternos

### A1. Reemplazo de un documento adjunto

1. En el paso 3, el usuario sustituye un documento previamente cargado (p. ej. la constancia de situación fiscal o una carta de representación, RN-17).
2. El sistema reemplaza el documento conservando el historial de la aplicación.
3. El flujo continúa en el paso 4.

## Flujos de excepción

### E1. Información o documentos obligatorios faltantes

1. En el paso 5 el sistema detecta campos obligatorios o documentos requeridos sin completar.
2. El sistema señala lo que falta y no reenvía la aplicación.
3. El usuario completa la información y reintenta el reenvío.

### E2. La aplicación ya no está en estado cambios_solicitados

1. En el paso 2 o 6 el sistema detecta que la aplicación ya no está en `cambios_solicitados` (p. ej. fue re-evaluada).
2. El sistema impide la edición y muestra el estado vigente de la aplicación.

## Datos relevantes

### Entradas

- Datos y documentos corregidos de la aplicación devuelta para cambios.

### Salidas

- Aplicación nuevamente en estado `pendiente` con acuse de reenvío.
