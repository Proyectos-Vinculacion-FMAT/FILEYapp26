---
estado: aceptada
version: "1.0"
tags:
  - tipo/adr
  - dom/evt
  - tema/arquitectura
fecha: 2026-09-01
id: ADR-0009
responsable: Isaac Ortiz
supersede:
reemplazado_por:
---
# ADR-0009. Las ocho actividades de `EVT` se representan con herencia multitabla, y se capturan con el tipo en la URL

## Estado

`Aceptado` — 2026-09-01, al construir `CU-EVT-002` (registro de la propuesta). Cierra cómo se
lleva a Django una entidad que tiene **ocho formas distintas**: en la base y en la pantalla.

## Contexto

Una propuesta del programa general es de uno de ocho tipos —conversatorio, conferencia, charla,
mesa redonda, presentación de libro, presentación de revista, lectura de obra, encuentro— y lo
que se le pide cambia con el tipo. Un conversatorio admite tres participantes; una presentación
de libro pide cinco autores, dos presentadores, el título de la publicación, la editorial, dos
archivos y el aviso de mandar un ejemplar físico.

[`Modelo de datos - Eventos`](<../requisitos/EVT/Modelo de datos - Eventos.md>) §2.6 y §2.7 lo
describe con **una tabla por tipo** y un enrutador polimórfico, `RouterActividades`, que guarda
el discriminador (`tipo_actividad_id`) y un `detalle_id` que apunta a la fila de la tabla que
corresponda. Las ocho tablas se mantienen separadas a propósito: hoy varias coinciden en
estructura, pero cada tipo es un formulario distinto y tener su propia tabla permite que
evolucione sin arrastrar a las demás.

Ese diseño está bien pensado, pero `detalle_id` **no es una clave foránea**: es un entero que la
base no puede validar contra nada, porque a qué tabla apunta depende del valor de otra columna.
Es el precio conocido del patrón polimórfico, y el documento lo dice.

Al mismo tiempo, y por el mismo motivo, hay que decidir cómo se **captura**: una pantalla cuyo
formulario cambia de forma según lo que se elija arriba.

`ADR-0008` retiró «toda pantalla funciona sin JavaScript» como requisito del sistema, así que
esa ya no es una restricción que obligue a nada. Pero dejó escrito que **las pantallas que hoy
funcionan sin él conviene que sigan haciéndolo**, y esta es una de las que puede: no es un mapa
interactivo, es un formulario.

Son dos caras del mismo problema —cómo se representa y cómo se pide algo que tiene ocho
formas—, y por eso se cierran juntas.

## Opciones consideradas

### En la base

#### Opción A: al pie de la letra del documento — discriminador y `detalle_id` entero

- **A favor:** el código calca el diagrama; nadie tiene que traducir al leerlo.
- **En contra:** nada impide guardar un `detalle_id` que no existe, ni borrar la fila hija
  dejando el enrutador apuntando al vacío. Cada lectura resuelve la tabla a mano. El modo de
  fallo es de los que no dan error: la fila se guarda, y el problema aparece al leerla.

#### Opción B: `GenericForeignKey` de `contenttypes`

- **A favor:** es el polimórfico estándar de Django, conocido por cualquiera que llegue.
- **En contra:** tampoco hay integridad —`object_id` sigue siendo un entero suelto—, y añade
  una dependencia incómoda con `ADR-0003`: `ContentType` vive en el schema `public` y las ocho
  tablas viven en el de cada feria.

#### Opción C: herencia multitabla

- **A favor:** Django crea la tabla padre y mantiene el enlace hacia la hija con **clave foránea
  de verdad**; la base rechaza una actividad colgada de una solicitud que no existe. Las ocho
  tablas siguen existiendo por separado, que es lo que el documento quería proteger.
- **En contra:** el diagrama deja de calcar el código: aparece una tabla padre que el documento
  no dibuja. Y una consulta que baje al detalle hace un `JOIN` que el entero suelto no haría.

### En la pantalla

#### Opción D: pintar los ocho juegos de campos y esconder siete con JavaScript

- **A favor:** una sola petición; cambiar de tipo es instantáneo.
- **En contra:** el POST arrastra los ocho juegos de campos y el servidor tiene que decidir
  cuáles mirar. Sin JavaScript quedan cuarenta campos contradictorios a la vista — y aunque eso
  ya no rompa ninguna regla, es una pantalla peor por una razón que no tiene que ver con
  JavaScript: la mayor parte de lo que se ve no aplica.

#### Opción E: el tipo viaja en la URL (`?tipo=…`)

- **A favor:** elegir el tipo es enviar el formulario por `GET`; el navegador arrastra lo ya
  escrito y la pantalla vuelve con los campos que tocan. En pantalla solo está lo que aplica, y
  el POST solo trae eso. Con htmx la misma petición cambia una sección y no hay recarga; sin
  JavaScript funciona igual, con recarga.
- **En contra:** una ida y vuelta al servidor por cada cambio de tipo.

## Decisión

**Las ocho tablas `Actividad_*` heredan de una tabla padre `Actividad`, y el tipo elegido viaja
en la URL.**

`Actividad` cumple el papel que el documento llama `RouterActividades`: lleva el discriminador
(`tipo`, FK a `CatalogoActividades`), la liga con la solicitud, y el enlace hacia la fila hija
que Django mantiene solo. **`RouterActividades` no llega a existir como tabla propia.** Por lo
mismo, `RouterDocumentos` es un `Documento` con una clave foránea normal hacia `Actividad`.

```python
class Actividad(models.Model):
    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE, related_name="actividad")
    tipo = models.ForeignKey(CatalogoActividades, on_delete=models.PROTECT, related_name="actividades")

class ActividadConversatorio(Actividad):
    nombre_participante_1 = nombre_de("participante", 1, obligatorio=True)
    semblanza_participante_1 = semblanza_de("participante", 1, obligatorio=True)
    ...
```

Y en la pantalla, el tipo se elige enviando el propio formulario por `GET`, con htmx encima
para no recargar:

```html
<button type="submit" formmethod="get" name="tipo" value="{{ opcion.nombre }}"
        hx-get="?tipo={{ opcion.nombre }}" hx-target="#campos-tipo"
        hx-swap="outerHTML" hx-include="closest form">
```

## Consecuencias

- **Positivas**
  - La base sostiene la invariante que el patrón polimórfico dejaba en manos del código. Hay
    prueba de ello: colgar una actividad de una solicitud inexistente es rechazado.
  - Bajar del padre a la hija se resuelve por el tipo, sin probar las ocho tablas
    (`Actividad.detalle`).
  - En pantalla solo está lo que aplica al tipo elegido, y cambiar de tipo no pierde lo ya
    capturado. La pantalla sigue funcionando sin JavaScript aunque ya no esté obligada
    (`ADR-0008`); lo que JavaScript añade —revelar personas de una en una, el contador, marcar
    obligatoriedades en vivo— es mejora, no requisito.
  - El orden de captura de cada tipo lo declara su formulario (`orden = (Campo(...),
    Personas(...))`) calcado del diagrama, así que se puede cotejar con él sin abrir una
    plantilla.

- **Negativas / riesgos aceptados**
  - **El diagrama y el código dejan de calcarse.** Está anotado en §2.7 del modelo de datos con
    un callout, pero alguien que lea solo el diagrama esperará una tabla que no existe.
  - **El `JOIN` del padre.** Irrelevante con los volúmenes de una feria; se anota por si algún
    listado del panel llegara a pesar.
  - **Dos reglas viven duplicadas en JavaScript y en Python** —que la semblanza sea obligatoria
    en cuanto hay nombre, y que haga falta un presentador si nadie de la publicación asiste—.
    La alternativa era pedir al servidor que repintara la sección con cada clic, y eso vacía los
    `<input type="file">`. Si una de esas reglas cambia, hay que tocar los dos sitios; está
    anotado en los tres archivos que participan.
  - **Los adjuntos se pierden si el servidor rechaza el envío.** Ningún navegador deja repoblar
    un `<input type="file">`, y no es cosa del entorno: pasa igual desplegado. Hoy se avisa en
    pantalla; el arreglo de verdad —guardar el archivo del lado del servidor mientras se corrige
    el formulario, y limpiar lo que nunca se envíe— queda como deuda conocida.

- **Qué queda descartado**
  - Un `detalle_id` entero sin clave foránea, en `EVT` y en cualquier módulo que copie este
    patrón.
  - Pintar los ocho juegos de campos y esconder siete.

## Referencias

- [`Modelo de datos - Eventos`](<../requisitos/EVT/Modelo de datos - Eventos.md>) §2.6, §2.7 y §2.8.
- [`CU-EVT-002`](<../requisitos/EVT/A - Convocatoria/CU-EVT-002 Registro de la propuesta de la actividad.md>).
- `ADR-0003` (una feria por schema) y `ADR-0006` (la liga entre convocatoria y módulo), de los
  que este depende: las ocho tablas viven en el schema de la feria, y la propuesta cuelga de un
  `RegistroConvocatoria`.
- `ADR-0008`, que retiró el «sin JavaScript» como requisito y dejó la recomendación que esta
  pantalla sigue.
