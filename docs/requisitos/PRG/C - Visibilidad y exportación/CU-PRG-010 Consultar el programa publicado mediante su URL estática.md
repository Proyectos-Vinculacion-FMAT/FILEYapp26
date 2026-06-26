---
estado: propuesta
version: 0.02
tags:
  - tipo/caso-de-uso
  - dom/prg
fecha: 2026-06-24
id: CU-PRG-010
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
# CU-PRG-010 Consultar el programa publicado mediante su URL estática

> [!note] Unifica CU-PRG-010 y CU-PRG-012 (Junta 3)
> La consulta del programa publicado en la web app y la "visualización del programa del
> otro panel" son el mismo caso de uso: una **Visualización de programa** de solo lectura,
> alcanzable por una URL estática, que refleja siempre lo último guardado sin importar si
> el programa es preliminar o final.

## Objetivo

Permitir a cualquier actor —incluido el panel de administración que no es propietario del programa— consultar, en modo solo lectura y por una URL estática, el estado actual del programa de eventos o de talleres.

## Alcance

Aplica a los programas de eventos y de talleres, en cualquiera de sus estados (preliminar o final). El modo lectura no depende de roles ni permisos del sistema: cualquiera con la URL puede consultarlo.

## Actores

### Actor principal

- Todos

## Disparador

Un actor abre la URL estática del programa.

## Precondiciones

- El programa fue guardado al menos una vez (preliminar o final).

## Postcondiciones

### En éxito

- Se muestra el estado más reciente del programa guardado, en lista con vistas por salón y sala (como el Excel de exportación, CU-PRG-011), sin que el actor pueda modificarlo.

### En fallo

- No existe aún un programa guardado; se informa que no hay nada publicado todavía.

## Flujo principal

1. El actor abre la URL estática del programa (eventos o talleres).
2. El sistema muestra la última versión guardada del programa, organizada por salón y sala.
3. El actor puede generar un PDF de esa vista para compartirla públicamente.

## Flujos de excepción

### E1. Programa aún sin guardar

1. El programa no se ha guardado ninguna vez.
2. El sistema muestra un mensaje indicando que el programa todavía no está disponible.
