---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/tal
fecha: 2026-06-29
id: CU-TAL-008
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-008 Revisar el detalle de una propuesta

## Objetivo

Elvira examina toda la información de una propuesta de taller —datos del responsable, datos del evento, datos de la presentación y público meta— para contar con los elementos necesarios y emitir un dictamen.

## Alcance

Módulo de Talleres (TAL) — vista de detalle de propuesta. Es la antesala del dictamen (CU-TAL-009). No cubre la edición de la propuesta por parte del tallerista (CU-TAL-003).

## Actores

### Actor principal

- Administrador (Elvira)

## Disparador

Elvira selecciona una propuesta desde la lista (CU-TAL-007).

## Precondiciones

- Elvira tiene sesión iniciada con permisos del módulo TAL.
- La propuesta existe en la edición activa.

## Postcondiciones

### En éxito

- Se muestra el detalle completo de la propuesta.

### En fallo

- No se muestra el detalle; se informa la condición (propuesta inexistente o error de consulta).

## Flujo principal

1. Elvira selecciona una propuesta desde la lista.
2. El sistema muestra los datos del responsable: nombre completo, número de contacto y correo electrónico.
3. El sistema muestra los datos del evento: nombre, organizado por, participantes que recibirán constancia, procedencia, tema, reseña, tipo de evento, modalidad y público meta.
4. El sistema muestra los datos de la presentación: autor(a)/autores, quien presenta/participa y editorial, cuando aplique.
5. Si la propuesta tiene historial (cambios solicitados previos o reenvíos), el sistema lo muestra como antecedente.
6. Desde el detalle, Elvira puede iniciar el dictamen (CU-TAL-009).

## Flujos de excepción

### E1. Sin antecedentes

1. En el paso 5, la propuesta no tiene historial previo (primer envío).
2. El sistema omite la sección de antecedentes sin bloquear la consulta.

## Datos relevantes

### Entradas

- Identificador o folio de la propuesta.

### Salidas

- Vista de detalle: datos del responsable, del evento, de la presentación y antecedentes.
