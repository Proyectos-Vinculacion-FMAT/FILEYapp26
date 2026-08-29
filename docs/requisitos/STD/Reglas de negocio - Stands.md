---
estado: propuesta
version: "1.0"
tags:
  - tipo/referencia
  - dom/std
  - tema/reglas-de-negocio
fecha: 2026-08-27
responsable: Hugo Janssen
---
# Reglas de negocio — Stands (`RN-01` … `RN-22`)

Catálogo único de las reglas que rigen el dominio `STD`. Hasta hoy **no existía**: cada regla
estaba definida dentro del caso de uso que la citaba, varias tenían dos redacciones distintas en
archivos distintos, y dos números se usaban sin haberse definido nunca. Este documento las
consolida y pasa a ser la fuente; los casos de uso las **citan**, no las redefinen.

> [!important] Cómo se usa
> - Un caso de uso cita `RN-NN` y no repite su texto. Si necesita matizarla, el matiz va en el
>   caso de uso y la regla se queda como está.
> - Cambiar una regla se hace **aquí**, y se revisa la columna "Dónde se aplica" para ver qué
>   casos de uso hay que releer.
> - Una regla nueva se numera al final. **No se reutiliza un número que ya significó algo**: una
>   cita vieja diría entonces algo distinto de lo que decía.
>
> `RN-05` y `RN-06` estuvieron saltados desde la primera redacción del dominio —sin definición y
> sin una sola cita— y se ocuparon el 2026-08-27 con las dos reglas de descuentos que faltaban.
> Ocuparlos no recicla nada: nunca significaron nada.

---

## 1. Cálculo y dinero

### RN-01 · El precio de un stand se deriva de su superficie

El precio de un stand es `metros_cuadrados × ConfiguracionSistema.costo_m2` **de la convocatoria
a la que pertenece el stand**. No se almacena por stand ni por línea de reserva: se deriva
siempre.

**Corolario (congelado del total):** al crear una reserva se calcula y **se almacena**
`Reserva.monto_total` con los valores vigentes en ese momento. Cambiar después el `costo_m2`
(CU-STD-034) o corregir el mapa (CU-STD-033) **no altera lo cobrado**. Lo que sí cambia es el
**desglose por stand**, que se recalcula y puede dejar de cuadrar con el total almacenado; ver
[`Modelo de datos - Stands`](<Modelo de datos - Stands.md>) §3.7.

> [!warning] Ningún servicio puede reescribir `monto_total` de una reserva que no esté `Por confirmar`
> Es la condición que sostiene el corolario. Si se rompe, el importe cobrado cambia
> retroactivamente y la editorial recibe una cifra distinta de la que aceptó.

*Dónde se aplica:* CU-STD-010, CU-STD-011, CU-STD-012, CU-STD-033, CU-STD-034.

### RN-02 · El anticipo es el 50% del total con descuento

Para confirmar una reserva hay que cubrir el **50%** del total **después** de aplicar los
descuentos, no del total bruto. El porcentaje es configurable por convocatoria
(`ConfiguracionSistema.porcentaje_anticipo`); 50% es su valor por omisión.

*Dónde se aplica:* CU-STD-012, CU-STD-013, CU-STD-026.

### RN-03 · La reserva vive 30 días esperando el anticipo

Desde su creación, una reserva permanece activa **30 días naturales** en espera de que se cubra
el anticipo de RN-02. El plazo es configurable por convocatoria
(`ConfiguracionSistema.plazo_reserva_dias`).

*Dónde se aplica:* CU-STD-012, CU-STD-022, CU-STD-014.

### RN-04 · Descuento por pronto pago, automático

Si la reserva queda liquidada **antes de `ConfiguracionSistema.fecha_limite_pronto_pago`**, se
consolida un descuento por pronto pago. Lo aplica el sistema, sin intervención del
administrador.

- **El porcentaje es configurable** por convocatoria (`descuento_pronto_pago`). **10% es el
  valor por omisión**, no una constante del sistema.
- **El plazo es una fecha de la convocatoria, no un contador por reserva.** Es una campaña con
  una fecha de corte igual para todos: quien reserva tarde tiene menos días para aprovecharla.
  Es deliberado, y es lo que lo distingue del plazo de 30 días de RN-03, que sí arranca con
  cada reserva.
- **"Liquidada" significa cubrir el total *ya descontado*.** El sistema compara el monto abonado
  contra el total con el pronto pago aplicado, no contra el bruto (CU-STD-023, paso 3).
- Si la fecha vence sin liquidar, **el beneficio se retira** y la reserva vuelve a su total sin
  este descuento (CU-STD-023, A1).

*Dónde se aplica:* CU-STD-012, CU-STD-013, CU-STD-023.

### RN-05 · Como mucho un descuento de cada tipo por reserva

Una reserva admite **un `pronto_pago` y un `especial`**, y nunca dos del mismo tipo. Son como
mucho dos filas en `DescuentoAplicado`.

Lo garantiza una **restricción única en la base** por (`reserva_id`, `tipo`)
([`Modelo de datos - Stands`](<Modelo de datos - Stands.md>) §3.9), no una comprobación de
pantalla: dos administradores aplicando un especial a la vez, o CU-STD-023 corriendo dos veces,
insertarían dos filas y el total saldría mal. El segundo intento **falla en la escritura**, y
cada caso de uso decide qué hacer con ese fallo:

- **`pronto_pago`** (automático): es **idempotente**. Que ya exista no es un error, es que ya
  estaba aplicado. No debe alarmar a nadie.
- **`especial`** (manual): **sí es un error y se muestra**. Para cambiar el porcentaje hay que
  modificar el que existe —dejando rastro en la `Bitacora`— o retirarlo y volver a aplicarlo,
  no acumular uno encima.

*Dónde se aplica:* CU-STD-020, CU-STD-023.

### RN-06 · Los dos descuentos se acumulan, aplicándose en secuencia

Un `pronto_pago` y un `especial` **coexisten en la misma reserva y se aplican los dos**. No son
excluyentes.

Se aplican **en secuencia**, no sumando porcentajes: primero el pronto pago sobre el total
bruto, y el especial sobre el subtotal ya descontado.

```
Total bruto              $100,000
  Pronto pago    10%  →   -10,000
                         --------
  Subtotal                 90,000
  Especial       15%  →   -13,500
                         --------
  Total a pagar          $ 76,500     (descuento efectivo 23.5%, no 25%)
```

> [!note] El orden no cambia el resultado, pero sí lo que se lee
> `0.90 × 0.85` y `0.85 × 0.90` dan lo mismo: el total es el mismo se aplique el que se aplique
> primero. Lo que fija el orden es **cómo se presenta el desglose**, y ahí siempre va el pronto
> pago arriba — es el que el expositor ya conocía cuando reservó.

> [!warning] El porcentaje que se anuncia no es el que se cobra
> Con 10% y 15% el descuento efectivo es **23.5%**, no 25%. Cualquier pantalla que muestre "un
> total de X% de descuento" tiene que calcularlo, no sumar las dos filas de `DescuentoAplicado`.

*Dónde se aplica:* CU-STD-012, CU-STD-013, CU-STD-020, CU-STD-023, CU-STD-029.

### RN-07 · El descuento especial lo configura el administrador, con motivo obligatorio

El administrador aplica un descuento **especial** que refleja acuerdos tomados fuera del
sistema (convenios institucionales, por ejemplo). **Él decide el porcentaje**, caso por caso —
no hay un valor configurado ni por omisión — y **el motivo es obligatorio**: es lo único que
explica, meses después, por qué esa reserva costó menos.

Se acumula con el pronto pago (RN-06) y está sujeto al tope de uno por tipo (RN-05).

*Dónde se aplica:* CU-STD-020.

### RN-08 · Métodos de pago: transferencia, depósito y cheque. Nunca efectivo

Los únicos métodos admitidos son **transferencia bancaria**, **depósito** y **cheque**. El
sistema **no acepta efectivo** y lo advierte explícitamente en las instrucciones de pago.

> [!warning] Este número estaba duplicado
> Hasta el 2026-08-27, `RN-08` nombraba **dos reglas distintas**: ésta y "transparencia
> administrativa" en CU-STD-032. La segunda pasa a ser **RN-18**; la cita de CU-STD-032 se
> corrigió.

*Dónde se aplica:* CU-STD-015, CU-STD-016, CU-STD-019.

---

## 2. El mapa y los stands

### RN-09 · El aplicante no distingue reservado de ocupado

En el mapa del aplicante, los estados `Reservado` y `Ocupado` se presentan **ambos** como
`Ocupado`. El aplicante no puede saber si un espacio está apartado o ya montado, ni quién lo
tiene.

**Se aplica en el servidor, no en la pantalla:** el JSON que se envía al mapa del aplicante ya
sale con el estado colapsado, así que la información no viaja al navegador. Ocultarla con CSS o
en la plantilla la dejaría en el HTML.

*Dónde se aplica:* CU-STD-009, CU-STD-010, CU-STD-011, CU-STD-037.

### RN-10 · Un stand tiene tres estados: Disponible, Reservado, Ocupado

| Estado | Significa | Quién lo pone |
| --- | --- | --- |
| `Disponible` | Se puede agregar al carrito y reservar. | Estado inicial; y al cancelarse una reserva. |
| `Reservado` | Entra en una reserva `Por confirmar` o `Confirmada`. | CU-STD-021, al crearse la reserva. |
| `Ocupado` | La reserva que lo contiene está `Pagada`. | CU-STD-027, al cubrirse el 100%. |

Los tres nombres son también los del protocolo del mapa: ver RN-20.

*Dónde se aplica:* CU-STD-009, CU-STD-012, CU-STD-021, CU-STD-027, CU-STD-033.

### RN-18 · Transparencia administrativa en el mapa

El administrador ve el mapa **sin censura**: el estado real de cada stand (`Reservado` frente a
`Ocupado`), quién lo reservó y el saldo pendiente de esa reserva. Es la contrapartida exacta de
RN-09 y la razón de que existan dos casos de uso distintos para servir el mismo mapa
(CU-STD-037 y CU-STD-038).

> Antes se citaba como `RN-08`, por duplicación de número. Renumerada el 2026-08-27.

*Dónde se aplica:* CU-STD-032, CU-STD-038.

### RN-19 · Un mapa por convocatoria *(nueva — 2026-08-27)*

El showfloor pertenece a **una convocatoria**, no a la feria. Cada convocatoria de tipo `STD`
tiene su propio mapa: su retícula, sus stands y sus decoraciones.

**Por qué:** desde el 2026-08-25 una feria puede abrir varias convocatorias de stands —una
general y otra para un pabellón concreto, con precios y plazos distintos—. Con un solo mapa por
feria, dos convocatorias competirían por los mismos espacios y `costo_m2` no podría diferir.

**Consecuencia inmediata:** `Stand` lleva `convocatoria_id`. Es la única FK de `STD` hacia `FER`
además de la de `Solicitud`, y no contradice ADR-0003: la convocatoria vive en el mismo schema.

**Consecuencia de precio:** dentro de una convocatoria **todos los stands se cobran al mismo
`costo_m2`** (RN-01). Si el cliente quiere pabellones a precios distintos, eso son
**convocatorias distintas**, cada una con su mapa y su configuración — que es justo el caso que
la decisión del 2026-08-25 habilitó.

*Dónde se aplica:* CU-STD-009, CU-STD-010, CU-STD-032, CU-STD-033, CU-STD-034, CU-STD-037, CU-STD-038.

### RN-20 · El mapa habla el idioma del dominio *(nueva — 2026-08-27)*

Los estados que viajan al mapa son los de RN-10 —`disponible`, `reservado`, `ocupado`— y no una
traducción. El componente de mapa se ajusta para usarlos; el dominio no se ajusta al componente.

**Por qué:** una tabla de traducción entre `Disponible/Reservado/Ocupado` y
`available/reserved/unavailable` es un sitio más donde equivocarse, en el camino exacto donde un
error significa enseñarle a un aplicante quién reservó un stand. Además `unavailable` no
distinguía `Reservado` de `Ocupado`, que es precisamente lo que el administrador necesita ver
(RN-18).

*Dónde se aplica:* CU-STD-037, CU-STD-038, y el proyecto del mapa (`event-stand-map`).

---

## 3. Solicitud y habilitación

### RN-16 · Solo una solicitud aceptada habilita para reservar

Únicamente los expositores cuya solicitud está en estado `aceptada` pueden ver el mapa, usar el
carrito y reservar. Es la precondición de todas las vistas U2–U6.

*Dónde se aplica:* CU-STD-006, CU-STD-008, CU-STD-009, CU-STD-010, CU-STD-011, CU-STD-012.

### RN-17 · Representar a otra editorial exige carta con membrete y firma

Si el aplicante representa a dos o más editoriales, adjunta **por cada una** una carta con
**membrete del representado** y **firma de un ejecutivo facultado**, autorizando exhibir y
comercializar su fondo editorial en la FILEY de forma exclusiva.

**Origen:** Convocatoria de Expositores FILEY 2026. Existe para evitar la duplicidad de fondos
en stands distintos.

*Dónde se aplica:* CU-STD-001, CU-STD-002.

### RN-21 · Una editorial por persona y por feria *(nueva — 2026-08-27)*

Dentro de una feria, una `Persona` tiene **exactamente una** `Editorial`, y una `Editorial`
pertenece a **exactamente una** `Persona`. La misma persona vuelve a llenar su ficha cada
edición: son dos `Editorial` en dos schemas, con una sola `Persona` detrás.

**No lo contradice RN-17:** representar a otras editoriales se modela con `SelloEditorial` y su
carta, no con una segunda `Editorial`.

*Dónde se aplica:* CU-STD-001, CU-STD-030, CU-STD-031.

### RN-22 · La solicitud es una fotografía, y se puede volver a aplicar *(nueva — 2026-08-27)*

Una `Solicitud` **guarda una copia** de los datos de la editorial tal como se enviaron. Corregir
la ficha después no reescribe lo que el administrador dictaminó.

Y de ahí lo segundo: **tras un rechazo, la misma persona puede volver a aplicar con la misma
editorial**, corrigiendo lo que haya que corregir. Esa nueva aplicación es una **`Solicitud`
nueva**, con su propia fotografía; la rechazada se conserva.

> [!important] Esto corrige una relación del modelo de `FER`
> `FER` §3.4 describía `RegistroConvocatoria` 1—1 `Solicitud`. Con reaplicación tras rechazo la
> relación es **1—N**, con **como mucho una solicitud viva** (`pendiente` o
> `cambios_solicitados`) por registro. Lo único que sigue siendo 1—1 es *persona ↔ registro*
> dentro de una convocatoria.

*Dónde se aplica:* CU-STD-001, CU-STD-002, CU-STD-005, CU-STD-006.

---

## 4. Reserva, pago y cierre

### RN-11 · Una reserva tiene cuatro estados, y solo uno es de cierre

`Por confirmar` → `Confirmada` → `Pagada`, más `Cancelada`. **`Cancelada` es el único estado
final de cierre**, y solo lo pone una decisión del administrador (RN-12): el sistema nunca
cancela por su cuenta.

*Dónde se aplica:* CU-STD-012, CU-STD-013, CU-STD-026, CU-STD-027, CU-STD-035.

### RN-12 · Vencer el plazo no libera la reserva: la escala a una persona

Al agotarse los 30 días de RN-03 sin haberse cubierto el anticipo —con abono parcial o sin
ninguno— el sistema **no libera los stands ni cancela nada**. Notifica al administrador **y al
aplicante**, y espera la decisión: cancelar o prorrogar con una fecha nueva.

*Dónde se aplica:* CU-STD-014, CU-STD-022, CU-STD-024, CU-STD-025, CU-STD-035.

### RN-13 · Al 50%, la reserva queda Confirmada y bloqueada

Cuando los abonos **validados** alcanzan el anticipo de RN-02, la reserva pasa a `Confirmada` y
queda bloqueada hasta su `fecha_corte_pago_total`. Esa fecha parte de una base general y el
administrador la ajusta caso por caso (CU-STD-036).

*Dónde se aplica:* CU-STD-018, CU-STD-019, CU-STD-026, CU-STD-036.

### RN-14 · Al 100%, la reserva queda Pagada

Cuando los abonos validados cubren el total, la reserva pasa a `Pagada` y sus stands pasan a
`Ocupado` (RN-10).

*Dónde se aplica:* CU-STD-018, CU-STD-019, CU-STD-027.

### RN-15 · Todo abono manual del administrador lleva documento adjunto

Un `Movimiento` con `origen = admin_manual` **exige** un documento de respaldo. No es una
validación de formulario que se pueda saltar: sin comprobante no se registra el abono.

*Dónde se aplica:* CU-STD-019.

---

## 5. Índice rápido

| Regla | En una línea | Estado |
| --- | --- | --- |
| RN-01 | Precio = m² × costo_m2; el total se congela al reservar | Vigente |
| RN-02 | Anticipo = 50% del total con descuento | Vigente |
| RN-03 | La reserva vive 30 días esperando el anticipo | Vigente |
| RN-04 | Pronto pago: automático, % y fecha configurables | Vigente |
| RN-05 | Como mucho un descuento de cada tipo por reserva | **Nueva** |
| RN-06 | Los dos se acumulan, aplicados en secuencia | **Nueva** |
| RN-07 | Especial: lo fija el administrador, con motivo | Vigente |
| RN-08 | Transferencia, depósito o cheque. Nunca efectivo | Vigente |
| RN-09 | El aplicante ve `Ocupado` donde hay `Reservado` | Vigente |
| RN-10 | Stand: Disponible / Reservado / Ocupado | Vigente |
| RN-11 | Reserva: cuatro estados; solo `Cancelada` cierra | Vigente |
| RN-12 | Vencer no libera: escala al administrador | Vigente |
| RN-13 | 50% → Confirmada y bloqueada | Vigente |
| RN-14 | 100% → Pagada | Vigente |
| RN-15 | Abono manual sin comprobante no existe | Vigente |
| RN-16 | Solo la solicitud aceptada habilita a reservar | Vigente |
| RN-17 | Representar exige carta con membrete y firma | Vigente |
| RN-18 | El administrador ve el mapa sin censura | Nueva (era RN-08) |
| RN-19 | Un mapa por convocatoria; un `costo_m2` por mapa | Nueva |
| RN-20 | El mapa usa los estados del dominio | Nueva |
| RN-21 | Una editorial por persona y por feria | Nueva |
| RN-22 | La solicitud es una fotografía; se puede reaplicar | Nueva |

---

Ver también: [`CU-STD Índice`](<CU-STD Índice.md>) ·
[`Modelo de datos - Stands`](<Modelo de datos - Stands.md>) ·
[`Estructura de vistas - Stands`](<Estructura de vistas - Stands.md>)
