---
name: filey-ux
description: Cómo se comporta una pantalla de FILEY — cuántos pasos, campos u opciones lleva, cuándo se revela cada cosa, cómo se bloquea un control sin que parezca una avería, cómo se redacta un error o un estado vacío, y cómo se verifica todo eso con números. Úsalo antes de estructurar un flujo, al decidir qué se enseña y qué se esconde, al escribir cualquier texto que lea un usuario, y al revisar una pantalla terminada. No dice qué color ni qué radio usar.
---

# FILEY — comportamiento de una pantalla

Este skill responde **¿cómo se comporta y qué dice?**. Los otros tres:

| Necesitas | Skill |
| --- | --- |
| Elegir un color, tipografía, radio, sombra | `filey-identidad` |
| Saber si una clase existe y en qué capa vive el CSS | `filey-ui-componentes` |
| Convertir eso en plantilla servida o HTML del prototipo | `filey-render` |

> [!note] Antes vivía dentro de `filey-identidad`
> Se separó el 2026-09-02. El motivo es práctico y no de orden: `filey-identidad` se carga
> cuando alguien pregunta *«¿qué color va aquí?»*, y las leyes de UX hacen falta antes, cuando
> se decide *qué se enseña y en qué orden*. Mezcladas, se consultaban tarde.

---

## 1. Las cinco leyes que más cortan decisiones

Detalle y las cinco secundarias —Jakob, Proximidad, Zeigarnik, Peak-end, Estética-usabilidad—
en [references/leyes-ux.md](references/leyes-ux.md). Aquí lo que se aplica a diario:

| Ley | Regla FILEY | Cómo se comprueba |
| --- | --- | --- |
| **Hick** | Máx. ~7 opciones visibles. Si el dominio impone más, se **agrupan** (una rejilla de 4×2 se lee como dos filas, no como ocho opciones) | Contar controles del mismo tipo a la vista |
| **Miller** | Ninguna sección con más de 9 campos **visibles a la vez**. Lo que no aplica todavía, no se pinta | Contar `input`/`textarea`/`select` visibles por sección |
| **Fitts** | Acción primaria ≥ 40 px de alto y al final del flujo de lectura. Las destructivas, separadas de las confirmatorias | Medir el alto real del control, no el del texto |
| **Doherty** | Bajo 400 ms se siente instantáneo; sobre 2000 ms, roto. Toda acción responde o muestra indicador | Cualquier ida al servidor que pinte de nuevo lleva `hx-indicator` |
| **Postel** | Aceptar entrada sucia y normalizar al guardar. **Validar al salir del campo, no en cada tecla** | Ver §3, que tiene la excepción |

## 2. Revelar de a poco, no esconder

Hick y Miller no se cumplen encogiendo la letra: se cumplen **no pintando lo que todavía no
aplica**. Tres formas, en orden de preferencia:

1. **No renderizarlo.** Si no se ha elegido el tipo de actividad, la sección de sus campos no
   existe. Es lo que hace `CU-EVT-002`.
2. **Renderizarlo y revelarlo de una en una.** Las cinco filas de autor están en el HTML —el
   servidor las necesita— y JavaScript enseña la siguiente cuando la anterior está completa.
3. **Renderizarlo apagado.** Solo cuando lo importante es que se vea que *existe* y que hay
   algo pendiente por hacer.

> [!warning] Esconder los ocho juegos de campos y enseñar uno **no** es revelar de a poco
> El navegador los tiene todos, el envío los arrastra todos y el servidor tiene que decidir
> cuáles mirar. Se ve igual y es peor por dentro. Ver `ADR-0009`.

## 3. Un control bloqueado

Pasa mucho en formularios largos: un campo que aún no toca, un botón que todavía no puede
pulsarse. Tres reglas, y las tres salen de haberlas incumplido:

- **Se apaga, no se esconde.** Que se vea que existe es lo que dice que hay algo por hacer.
- **Siempre con texto que diga qué falta.** Un control gris sin motivo se lee como una avería,
  no como un paso pendiente. Es la misma razón por la que un estado nunca se comunica solo con
  color (`filey-identidad` §4).
- **Nunca solo con el cursor.** `cursor: not-allowed` no se ve hasta que alguien ya intentó
  usarlo, y en táctil no existe.

> [!note] La excepción a Postel, y por qué es una excepción
> Postel dice validar al salir del campo, no en cada tecla. Un **candado que se abre** es otra
> cosa que una validación que reprocha: si la semblanza se habilita al escribir el nombre, el
> aviso «escribe primero el nombre» tiene que irse en cuanto deja de ser cierto, y esperar al
> `blur` lo dejaría mintiendo. La regla queda: **al teclear se abre; al salir se reprocha.**

## 4. Lo que el navegador no deja arreglar

Conviene saberlo antes de prometerlo en una pantalla:

- **Un `<input type="file">` no se puede repoblar, así que lo guarda el servidor.** Si se
  pudiera repoblar, cualquier página subiría archivos del disco de quien la visita; no es cosa
  del entorno, pasa igual desplegado. Lo que el navegador no puede hacer lo hace el servidor:
  un envío rechazado guarda los adjuntos que sí llegaron, y el campo deja de pedirlos
  (`apps/eventos/servicios/en_espera.py`).

  **Y la pantalla no cuenta que existe ese guardado.** El archivo se ve dentro del mismo
  componente que cualquier otro recién adjuntado, con la opción de descartarlo. Que venga de un
  intento anterior es funcionamiento interno, no información para quien lo subió.

  > [!important] Antes de escribir un texto que explica una limitación, pregúntate si la
  > limitación se puede quitar
  > Un cartel que avisa de algo molesto es honesto y no arregla nada. Suele ser más barato de
  > lo que parece quitar lo molesto, y entonces el cartel sobra — y si aun así hay que
  > explicarlo, el texto ya es otro.
- **Volver a pintar una sección vacía sus campos de archivo.** Por eso una regla que dependa de
  algo dentro de esa sección se resuelve en el navegador aunque quede duplicada, en vez de
  pedirle al servidor que repinte (`ADR-0009`).
- **El texto del botón de un control de archivo lo pone el navegador, en su idioma.** No hay
  CSS que lo cambie. Si tiene que estar en español, el control se esconde dentro de su rótulo
  —sigue recibiendo el foco— y se dibuja el bloque encima.

## 5. La barra superior es fija

`scrollIntoView` deja el elemento pegado al borde de la ventana, que está **debajo** de la
barra: el encabezado de la sección a la que se acaba de llegar no se ve. Se reserva el hueco en
CSS, no con cuentas en JavaScript:

```css
#campos-tipo { scroll-margin-top: calc(var(--alto-topbar) + 16px); }
```

Lo respetan `scrollIntoView` y también una navegación por ancla.

## 6. Tono de los textos

Español de México, formal pero directo. Trato de **tú** al aplicante; **usted** nunca.

| Situación | Sí | No |
| --- | --- | --- |
| Error de validación | «Falta el correo de contacto.» | «Error: campo inválido» |
| Estado vacío | «Aún no has enviado propuestas.» + acción para crear una | «Sin resultados» |
| Confirmación | «Tu propuesta quedó registrada con folio EVT-024.» | «Operación exitosa» |
| Control bloqueado | «Escribe primero el nombre.» | dejarlo gris y callado |
| Acción destructiva | «Quitar el taller del itinerario» + qué consecuencia tiene | «¿Estás seguro?» |

Nunca terminología interna en pantalla («dictaminar» sí, es del dominio; «CU-EVT-009» no).

Una casilla se rotula **en la voz de quien la marca** —«Necesito constancia de participación»—,
no como una pregunta que hay que contestar. Y si su valor por omisión es el inofensivo, **no
lleva asterisco**: sin marcar ya es una respuesta.

## 7. Auditar una pantalla terminada

No de memoria: con números. Sobre el HTML que manda el servidor.

```bash
# Opciones a la vista de un mismo tipo (Hick)
grep -o 'class="tipo-opt' pantalla.html | wc -l

# Controles por sección (Miller) — descontando los que JavaScript esconde
grep -o '<\(input\|textarea\|select\)\b' seccion.html | wc -l
```

- [ ] Ninguna sección pasa de 9 controles visibles; si pasa, está partida o revelada de a poco
- [ ] Ningún grupo pasa de ~7 opciones sin agrupar
- [ ] La acción primaria mide ≥ 40 px de alto
- [ ] Cada control bloqueado tiene texto que dice qué falta
- [ ] Cada ida al servidor que repinta tiene indicador
- [ ] El flujo termina en confirmación con folio y siguiente paso (Peak-end)
- [ ] Cada estado se comunica con color **y** texto

> [!warning] Deuda conocida — `CU-EVT-002` no cumple Miller
> Su sección 3 tiene 12 controles visibles en el tipo más simple y ~23 en presentación de libro,
> contra el tope de 9. Está medido, no estimado. Se acepta a sabiendas porque el formulario en
> papel es así y partirlo en más pasos cambia el flujo que el cliente aprobó; queda anotado para
> revisarlo con la Coordinación, no para ignorarlo.
