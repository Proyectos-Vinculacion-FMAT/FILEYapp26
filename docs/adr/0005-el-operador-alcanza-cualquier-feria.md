---
estado: aceptada
version: "1.0"
tags:
  - tipo/adr
  - dom/fer
  - tema/arquitectura
  - tema/permisos
fecha: 2026-08-27
id: ADR-0005
responsable: Hugo Janssen
supersede:
reemplazado_por:
---
# ADR-0005. El operador de la plataforma alcanza cualquier feria, sin fila en `AdminFeria`

## Estado

`Aceptado` — 2026-08-27. **Enmienda a [ADR-0004](<0004-acceso-administrativo-por-feria.md>) en
un punto y solo en uno**; el resto de aquella decisión sigue vigente y no se toca.

> [!note] Por qué es un ADR nuevo y no otra enmienda dentro de ADR-0004
> ADR-0004 ya lleva una enmienda escrita en su propio archivo (2026-08-25, las convocatorias
> pasan a ser del dueño), y ella misma fija el criterio para la siguiente: se admitió como
> enmienda **"porque no cambia el modelo de datos ni el mecanismo"**.
>
> Esto sí cambia el mecanismo. ADR-0004 decide que el acceso administrativo se responde con una
> consulta a `AdminFeria` y escribe, en su tabla de niveles, que el operador de la plataforma
> *"no es un rol dentro de ninguna feria"*. Lo de aquí añade una **segunda fuente de autoridad**
> que no es por feria y contradice esa línea. Editar el archivo viejo para que dijera otra cosa
> es justo lo que la regla de inmutabilidad del [README](<README.md>) prohíbe.

## Contexto

ADR-0004 dejó una consecuencia negativa anotada y sin resolver, con estas palabras:

> **Queda un hueco sin resolver: qué pasa si el dueño se va.** Con exactamente un dueño por
> feria y solo él pudiendo administrar accesos, una feria cuyo dueño deja el proyecto queda sin
> quien dé de alta a nadie. La salida provisional es que el operador de la plataforma reasigne
> la propiedad por comando.

Ese hueco dejó de ser teórico al construirse las pantallas. Hoy el sistema tiene tres
situaciones en las que el equipo técnico se queda fuera de una feria que sí opera:

1. **El dueño se va.** Nadie puede dar de alta a un administrador en esa edición. La única
   salida es entrar al servidor y escribir SQL o un comando — no hay pantalla.
2. **Soporte sobre una edición ajena.** Diagnosticar por qué a alguien no le aparece una
   convocatoria exige ver la feria como la ve quien la administra, y el equipo no puede.
3. **Preparar una edición nueva.** Entre que se crea la feria y que su dueño empieza a
   trabajar, alguien tiene que dejarla montada.

A esto se suma que el alta de convocatorias vive hoy en el admin de Django de la edición
(`/f/<slug>/django-admin/`, CU-FER-005 provisional), que se gobierna por `is_staff`. Es decir:
el equipo técnico **ya** opera el contenido de cualquier feria, y sin embargo no alcanza las
pantallas del dueño. La frontera quedó en un sitio que no responde a ninguna regla.

Fuerzas a considerar:

- **Un `AdminFeria` de mentira es peor que una excepción declarada.** La salida barata —darle
  al equipo una fila de dueño en cada feria— haría que la tabla dejara de significar lo que
  dice: quién responde por los accesos de esa edición.
- **El riesgo real de la excepción.** Un superusuario ya puede leer y escribir cualquier tabla
  del sistema desde `/django-admin/` y desde la consola. Que además pueda hacerlo por la
  pantalla no le da poder nuevo; le da un camino trazable.
- **Dos techos existentes que conviene no fundir.** Django ya distingue `is_staff` de
  `is_superuser`, y el proyecto ya usa el primero para las dos pantallas de admin.
- **Que la respuesta salga de un solo sitio.** El catálogo de una feria y el decorador que
  protege sus pantallas tienen que contestar igual a "¿administra ésta?", o el operador vería
  el escaparate del participante sobre una feria que sí puede administrar.

## Opciones consideradas

### Opción A: el superusuario pasa las dos comprobaciones, sin fila en `AdminFeria`

`administra()` y `tiene_alcance_de_dueno()` responden que sí a un superusuario en cualquier
feria. `AdminFeria` no cambia.

- **A favor:**
  - Cierra el hueco de ADR-0004 con pantalla, sin entrar al servidor.
  - `AdminFeria` conserva su significado: sigue diciendo **quién responde** por los accesos de
    una edición, y el operador no aparece ahí porque no responde por ninguna.
  - La excepción se declara en un sitio (`apps/ferias/permisos.py`) y se lee en dos funciones.
  - No inventa un nivel nuevo: reutiliza el `is_superuser` que Django ya tiene y que ya
    significa "puede todo".
- **En contra:**
  - Hay **dos** fuentes de autoridad sobre una feria, y auditar "quién puede entrar aquí" pasa
    a ser dos consultas: la tabla, y la lista de superusuarios.
  - Un superusuario deja de ser solo un poder de infraestructura y pasa a ser un actor dentro
    de la feria.

### Opción B: darle al equipo una fila `AdminFeria` en cada feria

- **A favor:** una sola fuente de autoridad; auditar sigue siendo una consulta a una tabla.
- **En contra:** hay que crear la fila en cada alta de feria y no olvidarla nunca, y la tabla
  deja de responder lo que se le pregunta — "¿quién responde por esta edición?" pasaría a
  incluir a gente que no responde por ninguna. Además, `es_dueño` es único por feria: el
  operador entraría como administrador y **seguiría sin alcanzar** las pantallas del dueño, que
  es justo el hueco que había que cerrar.

### Opción C: un caso de uso de transferencia de propiedad, y nada más

Que el dueño saliente traspase la feria antes de irse.

- **A favor:** no toca el modelo de permisos; el responsable sigue siendo uno y siempre está
  identificado.
- **En contra:** resuelve la salida ordenada y **no** la desordenada, que es la que duele: si
  el dueño ya se fue, no hay quien transfiera. Tampoco cubre soporte ni preparación de una
  edición. Sigue haciendo falta, pero como caso de uso aparte, no como respuesta a esto.

## Decisión

**El operador de la plataforma —el superusuario de Django— alcanza cualquier feria sin tener
fila en `AdminFeria`: pasa tanto `requiere_admin_feria` como `requiere_dueno_feria`.**

`AdminFeria` no cambia ni gana filas: sigue siendo la respuesta a *quién responde por los
accesos de esta edición*, y el operador no está ahí porque no responde por ninguna.

El techo son **dos**, y son los de Django:

| Marca | Qué abre |
| --- | --- |
| `is_staff` | Los dos admin de Django: `/django-admin/` (capa global) y `/f/<slug>/django-admin/` (contenido de una edición, donde hoy se dan de alta las convocatorias). |
| `is_superuser` | Además, todo lo que el sistema reserva al dueño de una feria: sus accesos (CU-FER-003, CU-FER-004) y sus convocatorias (CU-FER-005 a CU-FER-009). |

La excepción vive en `apps/ferias/permisos.py::es_operador`, y la consultan las dos funciones
que responden las dos preguntas del sistema: `administra()` y `tiene_alcance_de_dueno()`.
Ninguna vista, plantilla ni servicio comprueba `is_superuser` por su cuenta.

Queda actualizada así la tabla de niveles de ADR-0004:

| Nivel | Quién | Qué puede |
| --- | --- | --- |
| Operador de la plataforma | Equipo técnico (`is_superuser`) | Crear ferias y designar dueños (CU-FER-001) **y, desde este ADR, todo lo de cualquier feria, incluido lo reservado a su dueño.** |
| Dueño de la feria | Una persona por feria | Todo lo de la feria más sus accesos y sus convocatorias. |
| Administrador de la feria | Cero o más por feria | Todo el contenido de la feria; ni accesos ni convocatorias. |

## Consecuencias

**Positivas**

- El hueco que ADR-0004 dejó abierto se cierra: una feria cuyo dueño se fue se desatasca desde
  la pantalla, sin entrar al servidor.
- El equipo puede dar soporte sobre una edición ajena viéndola como quien la administra.
- Deja de haber una frontera arbitraria: hasta hoy el equipo operaba el contenido de cualquier
  feria (por `is_staff`) y no sus accesos, sin que ninguna regla lo explicara.
- La transferencia de propiedad deja de ser urgente. Sigue haciendo falta como caso de uso —el
  dueño debería poder traspasar su feria sin pedírselo a nadie—, pero ya no es lo único que
  evita una feria muerta.

**Negativas / riesgos aceptados**

- **Auditar quién puede entrar a una feria pasa a ser dos preguntas**: su `AdminFeria` y la
  lista de superusuarios. La segunda no se ve desde ninguna pantalla de FER.
- **Una cuenta de superusuario comprometida alcanza todas las ediciones por la interfaz**, no
  solo por la base. Se acepta porque ese acceso ya existía por otras vías; lo que cambia es que
  ahora es cómodo. Los superusuarios deben ser los menos posibles.
- **`is_staff` deja de ser inofensivo.** Una cuenta del equipo sin `is_superuser` ya puede dar
  de alta convocatorias en cualquier feria a través del admin de la edición. Es consecuencia de
  que el alta de CU-FER-005 viva ahí de forma provisional, no de este ADR, pero conviene tenerlo
  presente al repartir `is_staff`.
- **Nada registra que el operador actuó.** `BitacoraFER` no está construida, así que un alta de
  administrador hecha por el equipo no se distingue de una hecha por el dueño salvo por
  `AdminFeria.creado_por`. Cuando la bitácora exista, esto es lo primero que debe anotar.

**Qué queda descartado por esta decisión**

- Darle al equipo técnico filas `AdminFeria` en cada feria.
- Que "administrar una feria" se responda mirando **solo** `AdminFeria`. A partir de aquí la
  pregunta se hace con `administra()` / `tiene_alcance_de_dueno()`, nunca con `acceso_a()` a
  secas — `acceso_a()` sigue existiendo y sigue devolviendo la fila real, que es otra pregunta.

## Referencias

- [ADR-0004](<0004-acceso-administrativo-por-feria.md>) — el acceso por feria y el hueco del
  dueño ausente que esto cierra.
- [ADR-0003](<0003-una-feria-por-schema.md>) — el aislamiento por schema que obliga a que el
  permiso se responda por feria.
- [`FER/CU-FER-003`](<../requisitos/FER/CU-FER-003 Dar de alta un administrador en mi feria.md>)
  y [`CU-FER-004`](<../requisitos/FER/CU-FER-004 Retirar el acceso de un administrador de mi feria.md>)
  — las pantallas que el operador pasa a alcanzar.
- [`FER/Modelo de datos - Ferias`](<../requisitos/FER/Modelo de datos - Ferias.md>) §6 — el tema
  abierto "qué pasa si el dueño se va".
