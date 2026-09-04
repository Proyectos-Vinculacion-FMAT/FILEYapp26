---
estado: propuesta
version: "0.1"
tags:
  - tipo/adr
  - tema/arquitectura
fecha: AAAA-MM-DD
id: ADR-NNNN
responsable: Nombre
supersede: ADR-XXXX
reemplazado_por: ADR-YYYY
---
# ADR-NNNN. Título corto, en presente ("Usar Postgres para todo el sistema", no "Usaremos...")

> [!note] Cómo usar esta plantilla
> Copia este archivo a `000N-titulo-en-kebab-case.md` (siguiente número disponible, ver el
> índice en [`README.md`](<README.md>)). Borra las secciones opcionales que no apliquen y este
> mismo callout antes de terminar. Guía completa de qué llevar cada sección en
> [`README.md`](<README.md>#cómo-se-escribe-uno).

## Estado

`Propuesto` mientras se discute. `Aceptado` cuando el equipo lo cierra — a partir de ahí no se
edita para cambiar la decisión (ver la regla de inmutabilidad en el README). Si reemplaza un
ADR anterior, indícalo en `supersede:` (frontmatter) y edita el ADR viejo para apuntar aquí con
`reemplazado_por:`.

## Contexto

¿Cuál es el problema que obliga a decidir algo? ¿Qué fuerzas están en juego —técnicas, de
tiempo del equipo, del cliente, de lo que ya existe construido? Descríbelo en tono neutral,
como si lo leyera alguien sin nada del contexto de la junta donde se discutió: si solo tiene
sentido para quien "estuvo ahí", falta contexto.

No adelantes la decisión aquí — esta sección explica el problema, no la solución.

## Opciones consideradas

Cada opción real que se evaluó, con su comparación honesta. No hace falta que estén balanceadas
(una puede tener 4 contras y la elegida ninguno) — lo que importa es que quien lea esto entienda
por qué las demás se descartaron, sin tener que preguntarle a nadie.

### Opción A: nombre de la opción

- **A favor:** ...
- **En contra:** ...

### Opción B: nombre de la opción

- **A favor:** ...
- **En contra:** ...

### Opción C: nombre de la opción

> [!note] Opcional
> Agrega tantas opciones como se hayan comparado en serio. Elimina las que sobren de esta
> plantilla; no dejes secciones vacías "por si acaso".

## Decisión

Una frase, en voz activa y afirmativa: **"Vamos a hacer X."** Esta es la parte que la gente va
a citar sin leer el resto — que quede clara sola.

## Consecuencias

Lo que se vuelve más fácil, lo que se vuelve más difícil, qué se descarta con esto y qué deuda
o riesgo se acepta a cambio. Incluye las negativas también — un ADR que solo lista ventajas no
es honesto y pierde el valor de advertir a quien lo lea después.

- **Positivas:** ...
- **Negativas / riesgos aceptados:** ...
- **Qué queda descartado por esta decisión:** ...

## Qué queda desactualizado por esta decisión

**Obligatorio si el ADR cambia o retira una regla escrita en otro sitio.** Lista los archivos
que dejan de ser ciertos y actualízalos **en el mismo cambio**, no después.

Un ADR aceptado no vuelve a leerse; lo que la gente lee a diario es `CLAUDE.md` y los skills.
Si la regla vieja se queda ahí, sigue gobernando durante meses aunque esté derogada — y quien
la siga no estará haciendo nada mal: estará leyendo lo que hay escrito.

Dónde mirar, con la frase de la regla vieja como término de búsqueda:

- `CLAUDE.md` — las reglas de arquitectura y el estado actual.
- `.claude/skills/*/SKILL.md` — los cuatro.
- `docs/requisitos/**` — los casos de uso que **justifican una decisión** citando la regla. Un
  CU que solo describe una pantalla concreta no hace falta tocarlo.
- Los ADR anteriores que la citen: no se editan, pero conviene saber cuáles quedan colgando.

> [!warning] Reformular, no anotar
> La regla vieja **se borra**; no se deja con una nota al lado diciendo que ya no vale. Un
> enunciado que arrastra su propia derogación obliga a leer las dos versiones para saber qué
> hacer, y la mitad de las veces se lee solo el titular.

| Archivo | Qué decía | Qué dice ahora |
| --- | --- | --- |
| ... | ... | ... |

Si esta decisión no toca ninguna regla escrita, borra esta sección.

## Referencias

> [!note] Opcional
> Enlaces a la junta, documento o conversación que originó esta decisión, y a cualquier ADR
> relacionado. Ayuda a rastrear el "por qué" hasta la fuente original si hace falta más detalle
> del que cabe en Contexto.

- ...
