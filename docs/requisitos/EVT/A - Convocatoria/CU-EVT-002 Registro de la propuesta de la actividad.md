---
estado: implementado
version: 0.3
tags:
  - tipo/caso-de-uso
  - dom/evt
fecha: 2026-06-25
id: CU-EVT-002
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-002 Registro de la propuesta de la actividad

> [!note] Construido el 2026-09-01 — `filey/apps/eventos/`
> Esta versión pone el caso de uso al día con lo que quedó implementado. Lo que cambió respecto
> de la v0.2 no fue el flujo, sino tres supuestos que el modelo de datos ya había corregido y
> este documento arrastraba:
>
> - **Semblanzas y sinopsis son texto, no PDF.** Son contenido, no anexos
>   (`Modelo de datos - Eventos` §2.7). Los únicos archivos que quedan son la fotografía del
>   autor y las portadas.
> - **No se deriva ninguna `categoria` al enviar.** Lo que se guarda es `es_uady`, la
>   autodeclaración de quien propone; la categoría —literaria o académica— la asigna el comité
>   al dictaminar (`CU-EVT-009`), y hasta entonces no existe.
> - **Quién estará presente se marca persona por persona.** Sustituye al «sí/no» sobre «el
>   autor» más la lista de nombres escrita a mano.
>
> Las entidades se nombran aquí como en el código: `Solicitud` (era `Propuesta`), `Actividad` y
> sus ocho tablas de tipo, `Documento` (era `PropuestaAdjunto`) y `ConfiguracionConvocatoria`
> (era `ParametrosConvocatoria`). Ver `ADR-0009`.

<!-- -->

> [!note] El acuse cambió el 2026-09-03, al construirse `CU-EVT-003`
> Enseñaba también una tabla con las otras propuestas de esa persona. Dejó de hacerlo en cuanto
> existió el listado de seguimiento: era la misma lista dos veces —aquí sin poder abrir nada— y
> encima **sin la propuesta que se acababa de enviar**, que era la única que importaba en ese
> momento.
>
> Ahora hace una sola cosa, que es lo que dibuja `prototipo/EVT/aplicantes/confirmacion.html`:
> folio en grande y qué sigue. Su botón primario lleva al listado señalando la recién enviada,
> y el que decía "Cerrar" —que iba al catálogo— es ahora ese mismo.
>
> El acuse también dejó de listar lo ya enviado: era la misma lista dos veces y sin la
> propuesta recién mandada, que era la única que importaba en ese momento.

> Este caso de uso cubre tanto el **llenado** del formulario (captura y validación de los
> datos) como el **envío** —la acción de mandar la propuesta a revisión—, en un solo flujo
> (homologado, 2026-06-29; el envío ya no es un sub-caso aparte).

## Objetivo

El aplicante captura en el formulario de registro todos los datos de su propuesta de actividad para el programa de FILEY —datos de contacto y perfil, información de la actividad según su tipo y los archivos adjuntos requeridos— y la envía a la cola de revisión, dejando creado el registro correspondiente.

## Alcance

Módulo EVT — formulario de registro y envío de propuesta. El aplicante debe estar autenticado (CU-REG-002). Cubre la captura, la validación de los datos del formulario, y el envío y alta de la `Solicitud`. No cubre la edición de una propuesta ya enviada (CU-EVT-004).

## Actores

### Actor principal

- Aplicante (proponente externo o UADY)

## Disparador

El aplicante decide participar en el programa de FILEY y abre el formulario de registro de propuesta.

## Precondiciones

- El aplicante tiene sesión iniciada.
- La convocatoria está en estado `abierta`. **Lo que abre la puerta es el `estado`, no las fechas** (`CU-FER-008`): adelantar la fecha de cierre no cierra una convocatoria.

## Postcondiciones

### En éxito

- El formulario queda con todos los campos obligatorios completos y los adjuntos requeridos cargados, validados.
- Al enviar, se crea una `Solicitud` con folio y en estado `pendiente`, vinculada a quien propone por su `RegistroConvocatoria` (`ADR-0006`), y su `Actividad` en la tabla del tipo elegido. Los campos del dictamen son columnas de la propia solicitud y nacen vacíos; el modelo de datos §3.1 los describe como entidad aparte y explica ahí por qué en Django son columnas.
- Queda guardada la autodeclaración `es_uady`. **No se deriva ninguna categoría**: la asigna el comité al dictaminar (`CU-EVT-009`), y el administrador puede corregir la autodeclaración.
- Los archivos que el tipo pida quedan almacenados como registros `Documento`, colgando de la actividad.
- El aplicante recibe por correo la confirmación de envío con su número de folio.
- El folio **no se almacena**: se compone como `{prefijo_folio}-{id}` con el prefijo de `ConfiguracionConvocatoria`.

### En fallo

- El sistema conserva los datos capturados en el formulario para que el aplicante corrija y continúe.
- al hacer envio no se crea ningún registro. El sistema devuelve al aplicante al formulario (CU-EVT-002) conservando los datos para corregir y reintentar.

## Flujo principal

1. El aplicante abre el formulario de registro de propuesta.
2. El sistema precarga de `Persona` los datos de contacto —nombre completo, correo, teléfono, país y, si el país es México, estado y ciudad—. **Se muestran y no se capturan**: quien decide de quién es la propuesta es la sesión, no el formulario.
3. El aplicante completa lo único que se pide por solicitud: dependencia o institución (obligatorio), si es de la UADY, y cargo (opcional). Se piden aquí y no en el perfil porque una misma persona puede proponer representando a instituciones distintas.
4. El aplicante selecciona el tipo de actividad del catálogo.
5. El sistema presenta los campos de ese tipo, en el orden del diagrama del modelo, conservando lo ya escrito.
6. El aplicante completa los campos, marca si necesita constancia y adjunta los archivos que el tipo pida.
7. La pantalla acompaña la captura: la semblanza de una persona se abre cuando su nombre tiene algo escrito y pasa a obligatoria, no se puede añadir a la siguiente hasta completar la anterior, y el adjunto cargado se marca con su nombre.
8. El aplicante envía la propuesta.
9. El sistema valida en el servidor: campos obligatorios, adjuntos, que ninguna persona quede a medias ni con hueco, y que la actividad no se quede sin nadie delante (ver `RN-EVT-01`).
10. El sistema registra la `Solicitud` en estado `pendiente` con su fecha de envío, su `Actividad` en la tabla del tipo y, si es la primera vez, su `RegistroConvocatoria`. Todo en una transacción: o queda entero, o no queda nada.
11. El sistema almacena cada archivo como un `Documento` colgado de la actividad.
12. El sistema envía al aplicante un correo con el folio y la confirmación de recepción. **Que ese correo falle no deshace la propuesta**, que ya tiene folio.
13. El sistema lleva al acuse, que enseña el folio en grande, el estado y qué sigue. **No lleva la lista de lo ya enviado**: ver la nota de abajo.
14. El acuse ofrece "Enviar otra propuesta" (vuelve al paso 1) y "Ver mis propuestas" (`CU-EVT-003`), que es la acción primaria.

## Flujos alternos

### A1. Tipo de actividad es "Presentación de libro" o "Presentación de revista"

1. En el paso 5, el sistema presenta además: título de la publicación, rol del proponente, autores o editores **con una casilla por cada uno para decir si estará presente**, presentadores, editorial, la sinopsis con el tope largo, y los archivos del tipo.
2. El sistema muestra la instrucción de enviar también un ejemplar físico a las oficinas de FILEY, después de los adjuntos.
3. El flujo continúa en el paso 6.

## Flujos de excepción

> [!note] En la v0.2 había **dos** excepciones numeradas `E1`
> Una era la falta de campos en la captura y otra la convocatoria cerrada. Se renumeran; el
> contenido no cambia salvo donde se indica.

### E1. Convocatoria cerrada al momento del envío

1. En el paso 9, el sistema comprueba que la convocatoria siga en estado `abierta` — pudo cerrarse entre que se pintó el formulario y se pulsó enviar.
2. El sistema informa al aplicante de que no se admiten envíos.
3. **No se crea ningún registro**: ni la solicitud, ni la actividad, ni la inscripción a la convocatoria.

### E2. Campos obligatorios o adjuntos faltantes

1. El sistema detecta campos obligatorios sin completar, adjuntos ausentes, una persona a medias o un hueco entre la 1 y la 3.
2. El sistema devuelve al aplicante al formulario **conservando lo capturado y el tipo elegido**, y resalta cada campo con su mensaje.
3. El envío no procede hasta que corrija y reintente.

> [!note] Los adjuntos también se conservan, desde el 2026-09-03
> **Antes eran la excepción.** Ningún navegador permite repoblar un `<input type="file">` —si
> lo permitiera, cualquier página podría subir archivos del disco de quien la visita—, así que
> tras un envío rechazado había que volver a adjuntarlos y la pantalla lo decía. Era honesto y
> era la forma más rápida de que alguien abandonara un formulario de treinta campos.
>
> Lo que el navegador no puede hacer lo hace el servidor: lo que llegó se guarda en una cola
> (`servicios/en_espera.py`) y el campo deja de ser obligatorio mientras haya algo guardado. En
> pantalla se ve como cualquier archivo recién adjuntado, con la opción de descartarlo — **no**
> se explica que hay un caché detrás, porque eso es funcionamiento interno.
>
> La política, decidida el 2026-09-03:
>
> | | |
> | --- | --- |
> | Cuánto se guarda | `settings.EVT_MAX_ARCHIVOS_EN_ESPERA`, hoy 6 por persona y convocatoria. Es margen para un formulario de hasta cuatro adjuntos, no un número de intentos |
> | Qué se desaloja | El más viejo, **nunca el último de cada tipo**. Sin esa salvedad el tope no cumple lo que promete: la séptima subida tiraría el adjunto que nadie ha vuelto a subir |
> | Cuándo se vacía | Cinco momentos: al enviarse la propuesta —ya son `Documento`—, al salir del formulario hacia el listado o el catálogo, al cerrar sesión, al aparecer esa persona con otra sesión, y **al cambiar a un tipo de actividad que no pida ese adjunto** |
> | Quién recoge lo demás | `manage.py barrida_espera`, que borra las filas **cuya sesión ya no existe**. Cerrar la pestaña no pasa por ninguna de las cuatro salidas |
>
> **`EVT` no tiene política de días, y no debe tenerla.** Aquí no se guardan borradores de
> solicitud: o se envía, o no hay nada. Un adjunto suelto no significa nada fuera del rato en
> que alguien está llenando el formulario, así que lo que le pone caducidad es la sesión que lo
> subió —12 h deslizantes, `SESSION_COOKIE_AGE`— y no un plazo propio. Contar días es de `STD`,
> donde los plazos son del negocio y los decide quien coordina la feria.
>
> La salida por el catálogo va por una señal y no por una llamada: `apps/convocatorias` no
> nombra a ningún vertical (`ADR-0006`).
>
> Y el barrido por cambio de tipo **no compara con el tipo anterior**: cada petición trae solo
> el tipo actual, y la pregunta correcta no es «¿cambió?» sino «¿cabe este archivo en lo que hay
> elegido?». Guardar el tipo previo en la sesión para compararlo sería un estado más que
> mantener y otra forma de que se desincronice. Sin tipo elegido no se barre nada: no hay con
> qué comparar, y borrar por no saber es peor que conservar de más.

> [!note] La pantalla del tipo sigue siendo la de `ADR-0009`
> Los ocho juegos de campos no se pintan a la vez; el tipo viaja en la URL.

### E3. Nadie de la publicación estará presente y no hay presentador

1. En una presentación de libro o revista, ningún autor o editor está marcado como que asiste y no se capturó ningún presentador.
2. El sistema lo señala en el primer presentador, que pasa a ser obligatorio.
3. El envío no procede hasta que se marque a alguien o se capture un presentador (`RN-EVT-01`).

## Datos relevantes

### Entradas

Campos comunes a todos los tipos de actividad:

- Tipo de actividad (selección del catálogo) — obligatorio.
- Título de la actividad — obligatorio.
- Organiza — obligatorio.
- Público al que va dirigido (selección múltiple: Público en general · Académico · Estudiantil · Infantil · Familias; mínimo una opción) — obligatorio.
- ¿Necesita constancia de participación? — **casilla**, no una pregunta obligatoria: sin marcar ya es una respuesta, y es la inofensiva.
- Semblanza de cada persona — **texto**, máx. 2000 caracteres. Obligatoria en cuanto su nombre tiene algo escrito.
- Sinopsis de la actividad — **texto**, máx. 2000 caracteres (4000 en libro y revista) — obligatorio.
- Moderador/a — opcional, uno como máximo, sin semblanza.
- Comentarios u observaciones — opcional.
- Dependencia o institución — obligatorio. Si es de la UADY — casilla; es autodeclaración.
- Cargo — opcional.

El orden en que se piden es: título · moderador · organiza · público · **lo propio del tipo, en
el orden del diagrama del modelo** · constancia · sinopsis · adjuntos · aviso del ejemplar
físico · comentarios. Los adjuntos salen del orden del diagrama a propósito: adjuntar es lo
último que se hace, y así su sitio no cambia entre un tipo y otro.

Campos adicionales por tipo de actividad:

- **Conversatorio / Mesa redonda:** nombre de los participantes (máx. 3) — obligatorio.
- **Conferencia / Charla / Lectura de obra / Encuentro:** nombre de quien imparte (máx. 2) — obligatorio.
- **Presentación de libro:** título de la publicación, rol del proponente (Autor/a, Editor/a, Antologador/a, Compilador/a, Coordinador/a), autores con su nombre igual a la portada (máx. 5) **y una casilla por autor para decir si estará presente**, presentadores (máx. 2), editorial, fotografía del autor (JPG/PNG) y portada del libro (JPG/PNG/PDF).
- **Presentación de revista:** lo mismo con editores (máx. 2) y una sola portada (JPG/PNG/PDF).

## Reglas de negocio

### RN-EVT-01 · La actividad no se queda sin nadie delante

En una presentación de libro o revista, quien la sostiene es **un autor —o editor— que asista, o
un presentador**. Basta con uno de los dos:

| Al menos un autor marcado como que asiste | Los presentadores son opcionales |
| --- | --- |
| Ninguno asiste | Hace falta al menos un presentador |

Solo cuenta la marca, no el nombre: escribir a alguien no lo trae a la feria. Y solo cuentan los
que se capturaron — la casilla sin marcar de un autor que no existe no dice nada.

### Salidas

- `Solicitud` en estado `pendiente` con su `Actividad`, sus `Documento` si el tipo los pide, y correo de confirmación enviado con el folio.
