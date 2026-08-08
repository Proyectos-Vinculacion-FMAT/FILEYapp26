---
estado: vigente
version: "1.0"
tags:
  - tipo/referencia
  - tema/arquitectura
fecha: 2026-08-06
---
# ADR — Registro de decisiones de arquitectura

Un **ADR** (*Architecture Decision Record*) es un documento corto que explica **una** decisión
técnica importante: qué problema había, qué opciones se compararon, qué se decidió y qué
consecuencias trae. Esta carpeta es el historial de esas decisiones para el sistema **FILEY**.


## Por qué esto nos sirve a nosotros en concreto

No es un ritual: **ha habido cambios —o, más que cambios, falta de certeza— en la
arquitectura, en el stack y en decisiones clave en general que no se cerraban formalmente.**
Para eso sirve el ADR: para dejar esas decisiones realmente tomadas, no solo discutidas. por ejemplo:

nosotros tomamos la decicion de usar primero el stack de Django + angular, pero no tomamos en cuenta 
en ese momento la qruitectura monolotica por lo que ahora tenemos que hacer ese cambio, pero nosotros lo tenemos
presente ahora pero en un futuro o alguien mas que entre se hara muy dificil 
comprender que es lo que se hizo.

por eso que la decisión viva solo en la cabeza del equipo o en una
transcripción de junta, y meses después alguien vuelva a proponer lo mismo que ya se descartó
porque nadie se acuerda del porqué— es exactamente lo que un ADR evita. Un ADR no es para
nosotros mismos hoy; es para el compañero que se une en octubre, o para nosotros mismos dentro
de tres meses, cuando ya no recordemos si "usamos Django porque sí" o "usamos Django porque
evaluamos NestJS, Rails, Laravel y Phoenix y esta fue la razón".

Tres beneficios concretos para este proyecto:

- **Evita re-litigar lo mismo en cada junta.** Si la decisión de monolito-vs-separado queda
  escrita con su motivo, la siguiente vez que alguien pregunte "¿y por qué no usamos Angular
  aquí?" hay una respuesta en 30 segundos, no otra hora de discusión.
- **Hoy es el momento más barato para decidir esto.** Solo existe un módulo construido
  (`registro/`). Si la arquitectura se decide y se escribe ahora, los siguientes (`EVT`,
  `STD`, `TAL`, `VIS`) nacen ya alineados, en vez de heredar la inconsistencia de haber
  mezclado dos enfoques.
- **Es la forma más barata de que un agente de IA respete la arquitectura.** Un `CLAUDE.md`
  puede decir "sigue la arquitectura decidida"; el ADR es el documento que explica *cuál es* y
  *por qué*, para que la regla no sea arbitraria ni para el agente ni para quien la lee.

## Cuándo se escribe un ADR (y cuándo no)

> [!important] Regla para decidir si algo merece un ADR
> Pregúntate: ¿esto cambia la **estructura** del sistema, sus **dependencias**, algún
> **atributo de calidad** (seguridad, rendimiento, mantenibilidad) o la **forma de
> construirlo**, y es **caro de revertir**? Si la respuesta es sí a lo primero y a lo último,
> es ADR. Si es una preferencia de estilo o algo trivial de deshacer, no lo es.

**Sí llevan ADR** (ejemplos reales de este proyecto):

- Elegir Django sobre NestJS/Rails/Laravel/Phoenix.
- Monolito (Django + templates/HTMX) vs. backend separado (Django API + Angular).
- Cómo se modelan en base de datos los distintos tipos de evento (tabla genérica +
  discriminador vs. tablas específicas por dominio) — pendiente interno 
- Elegir SQLite en desarrollo y Postgres en producción, o una sola base para ambos.
- Adoptar una pasarela de pago y el modelo de conciliación (webhook automático vs. validación
  manual).

**No llevan ADR:** nombres de variables, formato de commits, qué librería de fechas usar,
cualquier cosa que se revierte en un PR sin dolor. Eso va al `CLAUDE.md` del proyecto o a una
convención de equipo normal, no aquí.

## Cómo se escribe uno

1. Copia [`0000-template.md`](<0000-template.md>) a un archivo nuevo con el siguiente número:
   `000N-titulo-corto-en-kebab-case.md`.
2. Llena **Contexto** (el problema, sin todavía decir la solución), **Opciones consideradas**
   (con pros/contras reales, no de relleno) y, cuando ya esté decidido, **Decisión** y
   **Consecuencias**.
3. Mientras se discute, el estado es `Propuesto`. Cuando el equipo lo cierra, pasa a
   `Aceptado` — y a partir de ahí **el archivo ya no se edita para cambiar la decisión**.
4. Agrégalo a la tabla de abajo.

> [!warning] Un ADR aceptado es inmutable
> Si la decisión cambia después, **no edites el ADR viejo**. Escribe uno nuevo, márcalo como
> `Reemplaza ADR-000X`, y en el viejo cambia el estado a `Obsoleto — reemplazado por ADR-000Y`.
> El objetivo es conservar el historial completo: por qué se decidió algo *entonces*, con la
> información que se tenía *entonces*. Editar el pasado rompe justo lo que esto sirve para dar.

### Estados posibles

| Estado | Significa |
| --- | --- |
| `Propuesto` | En discusión; contexto y opciones ya están, decisión todavía no está cerrada. |
| `Aceptado` | El equipo lo decidió; aplica desde su fecha en adelante. |
| `Rechazado` | Se consideró formalmente y se descartó (se documenta igual, para no reabrirlo sin motivo nuevo). |
| `Obsoleto` | Ya no aplica; debe apuntar al ADR que lo reemplaza. |

## Índice

| # | Título | Estado | Fecha |
| - | ------ | ------ | ----- |
| [0001](<0001-arquitectura-monolito-vs-separado.md>) | Arquitectura: monolito Django vs. Django API + Angular separado | Aceptado | 2026-08-06 |


## Estructura de la carpeta

```text
adr/
├── README.md              ← este archivo (índice + guía)
├── 0000-template.md        ← plantilla vacía; copiar para cada ADR nuevo
├── 0001-arquitectura-monolito-vs-separado.md
├── 0002-migracion-de-registro-al-monolito.md
└── 000N-....md
```

> [!note] Relación con `docs/requisitos/`
> `requisitos/` documenta **qué** hace el sistema por dominio (`CU-DOM-NNN`); `adr/` documenta
> **cómo** se construye, a nivel transversal — una decisión de arquitectura como "monolito
> sí/no" no pertenece a ningún dominio (`REG`, `EVT`, `STD`...) porque afecta a todos por
> igual. Por eso vive en su propia carpeta al mismo nivel, no dentro de `requisitos/`.

Ver también: [Portada del repositorio](<../../Filey.md>) · [Mapa de etiquetas](<../MAPA-DE-ETIQUETAS.md>).
