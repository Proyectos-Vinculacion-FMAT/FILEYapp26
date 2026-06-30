---
estado: propuesta
version: 0.01
tags:
  - tipo/caso-de-uso
  - dom/vis
fecha: 2026-06-24
id: CU-VIS-015
dominio: VIS
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
# CU-VIS-015 Consultar la lista de visitas escolares aceptadas, filtrable

## Objetivo

Permitir al Administrador consultar la lista de visitas escolares ya Aceptadas (Participantes), filtrándola según lo necesite, incluyendo el **total agregado de alumnos/visitantes** que asistirán.

> [!note] Numeralia de asistentes
> La vista incluye una **numeralia** simple: la **suma total** de alumnos/visitantes de las visitas aceptadas (y, según el filtro aplicado, por día o por actividad), para saber de manera automática cuántas personas visitarán la FILEY. Es una agregación sencilla sobre la cantidad de visitantes declarada en cada propuesta ([CU-VIS-001](<../A - Aplicación/CU-VIS-001 Registrar la propuesta de visita escolar (datos de la escuela y del contacto).md>)). Fuente: [Software para agendar escuelas](<../../../soporte/extraido/Software para agendar escuelas.md>) ("saber también de manera automática la cantidad de alumnos que visitarán la FILEY").

## Alcance

Indicar el límite del sistema o subsistema al que aplica este caso de uso.

## Actores

### Actor principal

- Administrador

### Actores secundarios

> [!note] Opcional
> Usar solo si participan actores de apoyo además del principal. Eliminar esta sección si no aplica.

## Disparador

Evento que inicia el caso de uso.

## Precondiciones

- Condición 1

## Postcondiciones

### En éxito

- Resultado esperado si el flujo termina correctamente

### En fallo

- Estado resultante si el flujo no puede completarse

## Flujo principal

1. El actor realiza la acción inicial.
2. El sistema valida la condición correspondiente.
3. El sistema ejecuta la acción principal.
4. El sistema confirma el resultado al actor.

## Flujos de excepción

### E1. Nombre de la excepción

1. Ocurre una condición inválida o error.
2. El sistema detiene, rechaza o compensa la operación.
3. Se informa el motivo al actor.
