---
estado: propuesta
version: "0.3"
tags:
  - tipo/caso-de-uso
  - dom/fer
  - tema/formularios
  - tema/alcance
fecha: 2026-08-25
fecha_actualizacion: 2026-08-27
id: CU-FER-005
dominio: FER
responsable: Hugo Janssen
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-FER-005 Dar de alta una convocatoria en mi feria

> [!important] Sin este caso de uso, `EVT`, `STD` y `VIS` no tienen de dónde colgar
> `RegistroConvocatoria` es el punto del que cuelga el expediente de cada módulo
> ([`Modelo de datos - Ferias`](<Modelo de datos - Ferias.md>) §3.4), y no puede existir sin una
> `Convocatoria`. Mientras este alta no exista, cada módulo termina inventándose su propia forma
> de saber si está abierto — que es exactamente lo que la entidad viene a evitar.

## Objetivo

Permitir que el dueño de la feria cree una de sus convocatorias —actividades, venta de
stands o visitas escolares— y la deje configurada en `borrador`, lista para abrirse cuando toque.

## Alcance

Core Ferias — panel de la feria, sección "Convocatorias". Crea la convocatoria **dentro de la
feria en la que se está operando**; no existe forma de crear una convocatoria en otra feria.
Abrirla al público es un acto distinto y deliberado (CU-FER-008).

## Actores

### Actor principal

- **Dueño de la feria** (fila en `AdminFeria` con `es_dueño = verdadero` para esta feria).

> [!important] Solo el dueño, no cualquier administrador
> Las convocatorias no son contenido corriente de la feria: definen **qué puertas están abiertas
> y hasta cuándo**, y de ellas cuelga el expediente entero de cada módulo. Por eso su
> administración queda reservada al dueño, junto con la de los accesos.
>
> Esto **enmienda** a [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>), que decía
> que lo único reservado al dueño era dar de alta y retirar administradores. Cualquier
> administrador **sí** puede consultar el catálogo (CU-FER-006) — sin eso no podría operar su
> propio módulo — y sigue pudiendo operar todo lo que cuelga de una convocatoria: dictaminar,
> revisar solicitudes, validar abonos.

> [!note] Implementación provisional (2026-08-27) — el alta vive en el admin de Django
> Mientras la pantalla de este caso de uso no exista, las convocatorias se dan de alta desde
> **`/f/<slug>/django-admin/`**, el admin de Django de la edición (`comun/admin_feria.py`). Es
> otro `AdminSite` que el de `/django-admin/`, y tiene que serlo: `Convocatoria` vive en el
> schema de la feria, y el admin de siempre corre sobre `public`, donde esa tabla no existe.
>
> **Lo que cambia mientras dure:** el actor real es el **operador de la plataforma** (`is_staff`),
> no el dueño de la feria. El admin de Django se gobierna por `is_staff` y un dueño no lo es, así
> que E3 —rechazar a quien no es dueño— todavía no se ejerce como lo describe este documento.
>
> **Lo que no cambia:** la convocatoria nace en `borrador` (paso 6), una edición archivada la
> rechaza (E2), el aviso de A2 se muestra, y las validaciones de nombre y fechas se cumplen. La
> lógica no está en la pantalla: vive en `apps/convocatorias/servicios/altas.py`, que es a quien
> llamará también la pantalla del panel cuando se construya.

<!-- -->

> [!note] El paso 6 y E1 ya están construidos — falta quien los conteste (2026-08-27)
> El alta le pregunta al **registro de módulos** ([ADR-0006](<../../adr/0006-la-liga-entre-convocatoria-y-modulo.md>))
> quién sirve el tipo de la convocatoria y llama al callback que ese módulo dejó inscrito,
> **dentro de la misma transacción**. Si el callback revienta, la transacción se deshace entera
> y no queda ni la convocatoria: eso es E1, y está probado.
>
> Lo que falta no es el mecanismo sino el módulo: `apps/stands` no existe, así que hoy nadie
> se inscribe para `STD` y la convocatoria se crea sin configuración. **Que no haya módulo no es
> un error** y no bloquea el alta — es el estado normal de los tres tipos.
>
> Sigue sin construirse la entrada de `BitacoraFER`, cuyo modelo no existe. Va en esa misma
> transacción cuando exista.

## Disparador

La feria arranca su planeación y hay que preparar las convocatorias de la edición.

## Precondiciones

- El actor tiene sesión activa **y es dueño de la feria** en la que opera.
- La feria no está `archivada`.

## Postcondiciones

### En éxito

- Existe una fila `Convocatoria` en el schema de esta feria, con `estado = borrador`.
- Si el tipo es `STD`, existe además su fila de `ConfiguracionSistema` ligada a ella, con los
  valores por omisión (ver el paso 6).
- **Nadie ajeno a la feria la ve todavía.** Una convocatoria en `borrador` no admite registros y
  no aparece en ninguna pantalla pública (CU-FER-006).
- Queda una entrada `convocatoria_creada` en `BitacoraFER`.

### En fallo

- No se crea nada. Si el tipo es `STD` y la configuración no pudo crearse, **la convocatoria
  tampoco queda creada**: una convocatoria de stands sin `costo_m2` no se puede operar y dejarla
  a medias es peor que no tenerla (ver E3).

## Flujo principal

1. El dueño entra a la sección "Convocatorias" del panel de su feria.
2. El sistema muestra el catálogo de convocatorias de esta feria (CU-FER-006).
3. El dueño elige "Nueva convocatoria".
4. El sistema presenta el formulario con: **tipo**, **nombre**, **fecha de apertura** y **fecha
   de cierre**. Los tres tipos están siempre disponibles: una feria puede tener varias
   convocatorias del mismo tipo (ver A2).
5. El dueño completa el formulario y confirma.
6. El sistema crea la convocatoria con `estado = borrador` y, **si el tipo es `STD`**, crea
   también su `ConfiguracionSistema` con los valores por omisión, en la misma transacción.
7. El sistema confirma y la convocatoria aparece en el catálogo marcada como borrador, con la
   acción "Abrir convocatoria" disponible (CU-FER-008).

> [!note] Por qué nace en `borrador` y no abierta
> Una convocatoria recién creada no tiene todavía su configuración revisada: `STD` no tiene
> precios, `EVT` no tiene cupos ni fechas de dictamen. Abrirla en el mismo acto que crearla
> significaría publicar un formulario que cobra mal o que no sabe cuántas propuestas admite. El
> estado inicial obliga a un segundo acto explícito, que es donde se comprueba que la
> configuración está completa (CU-FER-008 E1).

## Flujos alternos

### A1. Es la primera convocatoria de la feria

1. En el paso 2 el catálogo está vacío.
2. El sistema lo dice y ofrece el alta directamente, sin obligar a buscar el botón.
3. El flujo continúa igual desde el paso 4.

### A2. Ya existe otra convocatoria del mismo tipo

1. La feria ya tiene, por ejemplo, una convocatoria de actividades, y el dueño crea otra.
2. **El sistema lo permite** (decisión 2026-08-25): dos convocatorias de actividades con públicos
   distintos, o una de stands general y otra para un pabellón concreto, son casos legítimos.
3. El sistema **advierte** de que ya existe otra del mismo tipo y muestra su nombre, para que un
   alta duplicada por descuido se note antes de confirmar y no después.
4. Si el tipo es `STD`, la convocatoria nueva recibe **su propia** `ConfiguracionSistema`: precios
   y plazos son independientes de los de la otra.

> [!warning] Dos convocatorias del mismo tipo obligan a nombrarlas bien
> Es lo único que las distingue en el catálogo del participante (CU-FER-006), donde no se ve el
> tipo como etiqueta técnica sino el nombre. Dos filas llamadas "Convocatoria de Stands" son
> indistinguibles para quien tiene que elegir a cuál registrarse.

## Flujos de excepción

### E1. Falla la creación de la configuración del módulo

1. En el paso 6, con tipo `STD`, no se puede crear `ConfiguracionSistema`.
2. **La transacción se deshace entera**: no queda ni la convocatoria.
3. El sistema informa del fallo. Es deliberadamente distinto de CU-FER-003 E3, donde lo que
   falla es un correo de cortesía: aquí lo que falta es un dato sin el cual el módulo no opera.

### E2. La feria está archivada

1. La feria tiene estado `archivada`.
2. El sistema rechaza el alta: una edición cerrada se consulta, no se opera.

### E3. Quien lo intenta no es el dueño de la feria

1. Un administrador de la feria —con acceso legítimo al contenido— intenta crear una convocatoria.
2. El sistema **rechaza la operación en el servidor**, no solo ocultando el botón.
3. El sistema explica que las convocatorias las administra el dueño de la feria, e indica quién
   es.

## Datos relevantes

### Entradas

- Tipo (`EVT` / `STD` / `VIS`)
- Nombre visible
- Fecha de apertura y fecha de cierre

### Salidas

- Fila `Convocatoria` con `estado = borrador`
- Fila `ConfiguracionSistema` con valores por omisión, solo si el tipo es `STD`

### Validaciones

| Campo | Regla |
| --- | --- |
| Tipo | Obligatorio. Solo valores del conjunto cerrado (`EVT` / `STD` / `VIS`). **No** hay restricción de unicidad: caben varias del mismo tipo. |
| Nombre | Obligatorio, mínimo 3 caracteres. Es lo que distingue dos convocatorias del mismo tipo ante el participante (A2). |
| Fecha de apertura | Obligatoria. |
| Fecha de cierre | Obligatoria y **posterior** a la de apertura. |

> [!note] Las fechas son lo que se anuncia, no lo que abre la puerta
> Quien decide si se admiten registros es `estado`, no el calendario (CU-FER-008). Por eso aquí
> se admite crear una convocatoria cuyas fechas ya pasaron —al cargar una edición histórica, por
> ejemplo— sin que eso signifique nada operativo.
