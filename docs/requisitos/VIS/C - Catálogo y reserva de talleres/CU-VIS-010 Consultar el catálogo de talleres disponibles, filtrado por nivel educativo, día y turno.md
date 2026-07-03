---
estado: propuesta
version: 0.01
tags:
  - tipo/caso-de-uso
  - dom/vis
fecha: 2026-06-24
id: CU-VIS-010
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
# CU-VIS-010 Consultar el catálogo de talleres disponibles, filtrado por nivel educativo, día y turno

## Objetivo

Permitir al Participante consultar el catálogo de talleres y actividades infantiles/juveniles disponibles, filtrando por nivel educativo, día y turno, para armar el itinerario de su visita escolar.

> [!note] Filtro vs. visualización
> El catálogo se **filtra** por nivel educativo, día y turno (matutino/vespertino), pero la **lista** muestra explícitamente, por cada taller/actividad, su **hora de inicio y fin**, su descripción y su lugar, para que la escuela detecte solapes y planee su itinerario. El turno es un criterio de filtrado, no la única información horaria mostrada. El catálogo solo incluye actividades **aptas para público infantil/juvenil** provenientes de propuestas **Aceptadas**, sin importar la sala donde se realicen (la sala determina su aforo, no su elegibilidad). Fuente: [Software para agendar escuelas](<../../../soporte/extraido/Software para agendar escuelas.md>) ("los días y horarios en los que se llevarán a cabo, así como la descripción del evento").

<!-- -->

> [!warning] Precisión directa del cliente (2026-06-29) — el catálogo solo muestra horario final, nunca preliminar
> `VIS` **solo consume un catálogo final**; no puede consumir de un horario preliminar. El
> flujo real en `TAL` es: Elvira revisa y dictamina (CU-TAL-009) → programa en `PRG` → notifica
> el preliminar a los talleristas → ajusta → cuando el horario queda **final**, esa actividad
> se publica aquí. Mientras el horario de una actividad sea preliminar (recién programado,
> pendiente de ajustes), esa actividad **no aparece** en este catálogo, aunque ya tenga sala y
> bloque asignados en `PRG`. El mecanismo exacto para marcar un horario como "final" (¿una
> acción explícita de Elvira/Hipólito, o derivado de que ya no haya rechazos/cambios
> pendientes en CU-PRG-009?) queda **pendiente de definir** — ver "Pendientes" en
> `CU-VIS Índice.md`.

<!-- -->

> [!note] Precisión interna (2026-06-29) — el catálogo no es exclusivo de `TAL`
> El grueso del catálogo son **talleres de `TAL`** (Elvira), con aforo limitado por sala. Pero
> `EVT` (Hipólito) puede, a su discreción, marcar **casos excepcionales** de su propio programa
> como aptos para nivel infantil/juvenil para que también aparezcan aquí. Esos casos de `EVT`
> **no tienen límite de cupo** (a diferencia de un taller normal), por lo que la validación de
> cupo (CU-VIS-011) no aplica con normalidad sobre ellos — ver la nota en ese CU.

## Alcance

Indicar el límite del sistema o subsistema al que aplica este caso de uso.

## Actores

### Actor principal

- Participante

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
