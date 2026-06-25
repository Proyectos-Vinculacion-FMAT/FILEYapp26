---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/prg
fecha: 2026-06-24
id: CU-PRG-011
dominio: PRG
responsable: Nombre
issue_relacionado: PSD-XX
pr_relacionado: "#XX"
reglas_de_negocio:
  - RN-XXX-001
diagramas_relacionados:
  - BPMN-XXX-001
trazabilidad:
  ddr:
    - DDR-XX
---
# CU-PRG-011 Exportar el programa a Excel o Word para uso interno

> [!note] Ya no genera PDF (Junta 3)
> Se elimina la generación de PDF de esta exportación: el PDF público/compartible es
> responsabilidad de CU-PRG-010 (Visualización de programa). Excel y Word son privados, de
> uso interno, y la separación es intencional.

## Objetivo

Generar, desde la herramienta de programación, un archivo Excel o Word del programa para control interno del Administrador.

## Alcance

Aplica a los programas de eventos y de talleres, en cualquiera de sus estados. Es una exportación de uso interno, distinta de la Visualización de programa pública (CU-PRG-010).

## Actores

### Actor principal

- Administrador

## Disparador

El Administrador solicita exportar el programa desde la herramienta de programación.

## Precondiciones

- El programa tiene al menos una actividad asignada.

## Postcondiciones

### En éxito

- Se genera el archivo solicitado: Excel (una hoja por salón, con sus horarios) o Word (un documento por salón).

### En fallo

- No se genera el archivo; se informa el motivo al Administrador.

## Flujo principal

1. El Administrador elige exportar el programa a Excel o a Word.
2. El sistema genera el archivo correspondiente, organizado por salón.
3. El sistema entrega el archivo al Administrador.
