---
estado: implementado
version: "1.0"
tags:
  - tipo/caso-de-uso
  - dom/fer
  - tema/alcance
  - tema/usuarios
fecha: 2026-08-25
fecha_actualizacion: 2026-08-26
id: CU-FER-006
dominio: FER
responsable: Hugo Janssen
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-FER-006 Consultar el catálogo de convocatorias de una feria

> [!important] Este catálogo es **la fuente de la pantalla del participante**
> No es una pantalla administrativa que además se enseña fuera: es la consulta que el frontend
> lee para pintarle a cualquiera las convocatorias abiertas de una feria. Sustituyó al catálogo
> hardcodeado que vivía en `filey/apps/registros/catalogo.py`, retirado el 2026-08-26 — ver
> "Estado de implementación" al final.

<!-- -->

> [!important] Es la misma pantalla para dos públicos muy distintos
> El **participante** entra a ver dónde puede participar; el **administrador**, a ver cómo va su
> convocatoria. Miran la misma tabla y ven cosas distintas: uno ve un escaparate, el otro un
> panel de control. Se documenta como un solo caso de uso porque la fuente es la misma y la
> diferencia es de **visibilidad**, no de lógica — pero esa diferencia es la parte que hay que
> implementar con cuidado (§ "Qué ve cada quién").

## Objetivo

Mostrar las convocatorias de una feria a quien las consulta, con el detalle y las acciones que le
correspondan: al participante, aquellas a las que puede registrarse; al administrador, el estado
real del catálogo que opera.

## Alcance

Core Ferias. Cubre **una feria**: la del contexto en el que se está (`/f/<slug>/…`). No resuelve
la pregunta que cruza ferias —"¿en qué feria hay algo abierto ahora mismo?"— que sigue sin caso
de uso (ver la nota final).

## Actores

### Actores principales

- **Participante** — cualquier persona interesada en registrarse a una convocatoria. **No
  necesita sesión** para consultar el catálogo (ver A1).
- **Administrador de la feria** — con fila en `AdminFeria` para esta feria.
- **Dueño de la feria** — el administrador que además administra el catálogo.

## Disparador

- El participante quiere saber si puede proponer una actividad, aplicar a expositor o solicitar
  una visita escolar en esta feria.
- El administrador entra al panel y necesita saber cómo va la convocatoria.

## Precondiciones

- La feria existe.
- Para el administrador y el dueño: sesión activa y acceso a esta feria.
- Para el participante: ninguna. Ver A1.

## Postcondiciones

### En éxito

- No modifica nada. Es una consulta.

## Qué ve cada quién

Es el corazón de este caso de uso. La misma consulta, filtrada y enriquecida según quién mira:

| | Participante | Administrador | Dueño |
| --- | --- | --- | --- |
| Convocatorias `abierta` | Sí | Sí | Sí |
| Convocatorias `cerrada` | Sí, marcadas como cerradas | Sí | Sí |
| Convocatorias `borrador` | **No, en absoluto** | Sí | Sí |
| Nombre, tipo y fechas anunciadas | Sí | Sí | Sí |
| Número de registros recibidos | **No** | Sí | Sí |
| Acción "Registrarme" | Sí, solo en las `abierta` | — | — |
| Nueva · Editar · Abrir/Cerrar · Eliminar | No | **No se ofrecen** | Sí |

> [!important] El `borrador` es invisible para el participante, y esa es toda su razón de ser
> Una convocatoria en `borrador` no tiene todavía su configuración revisada: puede no tener
> precio, ni cupos, ni fechas de dictamen. Si se filtrara al escaparate, alguien intentaría
> registrarse a algo que no está listo para recibirlo. **Filtrar en la consulta, no en la
> plantilla**: una convocatoria en borrador no debe llegar siquiera a la respuesta del
> participante.

<!-- -->

> [!important] El conteo de registros no es dato del participante
> Saber cuántas propuestas lleva recibidas una convocatoria influye en si alguien se anima a
> enviar la suya, y no es información que la feria tenga por qué publicar. Para el administrador,
> en cambio, es el dato que decide si una convocatoria se puede eliminar (CU-FER-009).

<!-- -->

> [!note] Ocultar no es proteger
> La tabla de arriba describe lo que se **muestra**. Lo que impide de verdad que un participante
> abra una convocatoria es que cada caso de uso rechace la petición en el servidor (CU-FER-005
> E5, CU-FER-007 E4, CU-FER-008 E5, CU-FER-009 E2), no que el botón no esté pintado.

## Flujo principal — participante

1. El participante llega al portal de una feria.
2. El sistema lista las convocatorias **`abierta` y `cerrada`** de esa feria, con tipo, nombre,
   descripción, estado y fechas anunciadas. **Puede haber varias del mismo tipo** (CU-FER-005 A2):
   se listan por separado y lo que las distingue es el nombre, no el tipo.
3. Cada convocatoria `abierta` ofrece **"Registrarme"**; las `cerrada` se muestran informativas,
   sin acción.
4. El participante elige una convocatoria abierta y continúa en el formulario **del módulo que le
   corresponde** — ahí termina `FER` (ver la nota de abajo).

> [!important] Dónde acaba `FER` y empieza el módulo
> Este caso de uso lleva al participante hasta la puerta; **no la cruza**. Crear el
> `RegistroConvocatoria` y capturar el expediente es del módulo: CU-EVT-002 para actividades,
> CU-STD-001 para expositores, CU-VIS-001 para visitas escolares. `FER` no sabe qué es una
> propuesta ni una ficha de expositor, y no debe aprenderlo.

## Flujo principal — administrador

1. El administrador entra a la sección "Convocatorias" del panel de su feria.
2. El sistema lista **todas** las convocatorias de esta feria, incluidas las de `borrador`, con:
   - **tipo** y **nombre**;
   - **estado** (`borrador` / `abierta` / `cerrada`), visualmente distinguible;
   - **fechas** de apertura y cierre anunciadas;
   - **número de registros** recibidos (`RegistroConvocatoria` con `estado = activo`);
   - las **acciones** que su rol permita.
3. El administrador consulta, o —si es el dueño— elige una acción.

### Qué acciones ofrece cada estado (solo al dueño)

| Estado | Acciones | Por qué |
| --- | --- | --- |
| `borrador` | Editar · Abrir · Eliminar | Nadie la ha visto todavía: todo es reversible. |
| `abierta` | Editar · Cerrar | Está recibiendo registros; eliminarla no se ofrece (CU-FER-009 E1). |
| `cerrada` | Editar · Reabrir · Eliminar *(solo si nunca tuvo registros)* | Reabrir es la prórroga (CU-FER-008 A1). |

## Flujos alternos

### A1. El participante consulta sin haber iniciado sesión

1. El participante llega al portal de la feria sin sesión.
2. El sistema muestra el catálogo **igual**: qué convocatorias hay y hasta cuándo es información
   pública.
3. Al elegir "Registrarme", el sistema lo lleva al acceso (CU-REG-001 / CU-REG-002) y, una vez
   dentro, al formulario del módulo.

> [!important] Pedir sesión para *mirar* rompería el embudo
> Nadie crea una cuenta para averiguar si hay algo a lo que apuntarse. La sesión hace falta para
> **registrarse**, porque el registro necesita una `Persona`; para consultar, no. Es la misma
> lógica por la que el acceso público admite que un correo revele si tiene cuenta: la usabilidad
> del embudo pesa más que un dato que no es secreto.

### A2. La feria no tiene ninguna convocatoria

1. El catálogo está vacío.
2. **Al participante** se le dice que esta feria todavía no tiene convocatorias abiertas — no una
   tabla vacía sin explicación.
3. **Al administrador**, lo mismo, y si es el dueño se le ofrece crear la primera (CU-FER-005 A1).

### A3. Hay varias convocatorias del mismo tipo

1. La feria tiene, por ejemplo, dos convocatorias de actividades.
2. El sistema las lista **como dos entradas independientes**, cada una con su nombre, su estado y
   sus fechas. No se agrupan por tipo ni se colapsan.
3. El participante elige a cuál registrarse; registrarse a una no lo inscribe en la otra.

> [!warning] Aquí se paga que dos convocatorias puedan llamarse igual
> El participante no ve el tipo como etiqueta técnica: ve el nombre. Si la feria crea dos
> convocatorias de stands y las nombra parecido, esta pantalla es donde el error se convierte en
> alguien registrándose a la que no era. La advertencia del alta (CU-FER-005 A2) existe por esto.

### A4. Ninguna convocatoria está abierta, pero hay cerradas

1. Para el participante, todas las convocatorias de la feria están `cerrada`.
2. El sistema las muestra con sus fechas, de modo que se vea **que existieron y cuándo cerraron**,
   en lugar de dar a entender que la feria no tiene convocatorias.

### A5. Ver el detalle de una convocatoria

1. Se abre una convocatoria del catálogo.
2. El sistema muestra sus datos completos. **Al administrador**, si el tipo es `STD`, con un
   enlace a la configuración del módulo (CU-STD-034), que vive en el panel de stands y no aquí.
3. Desde el detalle se llega a las mismas acciones que ofrece la lista.

> [!note] `FER` no configura los módulos, solo los enmarca
> La convocatoria dice **cuándo** y **si** se admiten registros. Cuánto cuesta el metro cuadrado,
> qué cupos tiene el dictamen o cuántas visitas caben por día lo dice cada módulo, en su propia
> pantalla de parámetros. Meter eso aquí obligaría a `FER` a conocer los tres dominios.

## Flujos de excepción

### E1. La feria está archivada

1. La feria tiene estado `archivada`.
2. **Al administrador**, el catálogo se muestra en solo lectura: sin acciones de edición,
   apertura ni borrado. Consultar una edición cerrada es legítimo; operarla no.
3. **Al participante**, la feria archivada no ofrece registro en ninguna convocatoria, con
   independencia del estado en que quedaran.

### E2. La feria no existe

1. El slug de la URL no corresponde a ninguna feria.
2. El sistema responde "no encontrado". No enumera las ferias existentes ni sugiere alternativas.

## Datos relevantes

### Salidas

- Lista de `Convocatoria` de esta feria, **filtrada según quién consulta** (ver la tabla)
- Para el administrador: conteo de `RegistroConvocatoria` por convocatoria
- Acciones disponibles por fila, derivadas del estado y del rol

---

## Estado de implementación

El **flujo del participante** se construyó el 2026-08-26. Con él desapareció el catálogo
hardcodeado de `filey/apps/registros/catalogo.py` y la ruta `/convocatorias` que alimentaba: el
catálogo es ahora la portada de `/f/<slug>/` y sale de la base.

| Pieza | Dónde |
| --- | --- |
| El filtro por público | `filey/apps/convocatorias/servicios/catalogo.py` |
| La pantalla | `filey/apps/convocatorias/views.py::catalogo_de_la_feria` |
| Quién administra ésta | `filey/apps/ferias/permisos.py::acceso_a` |
| Las pruebas | `filey/apps/convocatorias/pruebas/test_catalogo.py` |

**Lo que ve el participante está completo**: abiertas y cerradas, nunca los borradores, y el
aviso de A2/A4 cuando no hay nada. Lo que **falta** de este caso de uso:

- El **conteo de registros** por convocatoria, que necesita `RegistroConvocatoria` — todavía no
  existe como modelo.
- Las **acciones del dueño** (Nueva · Editar · Abrir/Cerrar · Eliminar), que son CU-FER-005,
  007, 008 y 009.
- El botón **"Registrarme"**, que lleva al formulario del módulo (CU-EVT-002, CU-STD-001,
  CU-VIS-001). Ninguno de los tres módulos está construido, así que hoy avisa y no navega.
- `TAL` sigue sin decidirse (`Convocatoria.tipo` admite tres tipos) — ver el índice de `FER`.

> [!warning] Falta la vista que cruza ferias, y no es esta
> Este caso de uso responde "¿qué hay en **esta** feria?". La pregunta "¿dónde puedo participar
> hoy?" cruza todas las ferias, y con `Convocatoria` viviendo en el schema de cada una no se
> responde con una consulta: hay que recorrer schemas o mantener un espejo en `public`. Sigue
> abierta en [`Modelo de datos - Ferias`](<Modelo de datos - Ferias.md>) §6.
