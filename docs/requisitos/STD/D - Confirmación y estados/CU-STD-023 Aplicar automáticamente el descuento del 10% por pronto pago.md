---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-023
modulo: D. Confirmación y estados
actor_principal: Sistema
requisitos_relacionados: []
dependencias:
  - CU-STD-018
  - CU-STD-019
---
# CU-STD-023 Aplicar automáticamente el descuento del 10% por pronto pago

## Descripción

El sistema consolida el descuento por pronto pago si la editorial liquida el monto total con descuento antes de la fecha límite establecida. Si la fecha expira sin que se haya liquidado, el sistema retira la oferta y ajusta el monto pendiente al precio regular.

> [!important] Construido el 2026-08-27 · el descuento se aplica **al reservar**, no al liquidar
> El flujo principal de abajo describe el descuento como algo que se *registra cuando se
> cumple la condición* (pasos 3 y 4), reevaluado con cada abono o por la rutina diaria. **No es
> lo que se construyó, y la diferencia es deliberada.**
>
> `servicios/reservas.py::crear` inserta el `DescuentoAplicado` de tipo `pronto_pago` en el
> momento de reservar, si `pronto_pago_vigente()` devuelve un porcentaje. Así la cifra que la
> editorial **acepta** ya lo lleva puesto, que es lo que el paso 3 de
> [CU-STD-012](<../B - Reserva/CU-STD-012 Realizar la reserva de los stands seleccionados.md>)
> pide enseñar: el total con descuento, el tiempo que queda para conservarlo y a cuánto sube si
> se deja pasar. Con el modelo de abajo, el carrito tendría que prometer un descuento que
> todavía no existe en ninguna fila y que el aplicante solo vería al pagar del todo.
>
> El `A1` es entonces lo que **de verdad** hace el reloj: `servicios/pagos.py::caducar_pronto_pago`
> lo retira si llega la fecha de corte sin liquidar, y el total sube. `RN-04` está redactada
> sobre el modelo construido —«se aplica al reservar y caduca»—; este caso de uso conserva su
> redacción original porque describe bien la **regla comercial**, que no cambió: se paga menos
> si se paga antes del corte.
>
> **Lo que la diferencia sí cambia, y hay que saber:** poner o ampliar
> `fecha_limite_pronto_pago` (`CU-STD-034`) **no le da el descuento a las reservas que ya
> existen**. Solo lo llevan las que nacieron con la fecha vigente. Es coherente con `RN-01`
> —el total se congela al reservar— y con que `RN-04` sea una campaña con corte y no un
> beneficio por reserva, pero no se deduce de la pantalla de configuración: si se abre la
> campaña tarde, hay que decidir a mano qué se hace con lo ya reservado (`CU-STD-020` es la
> herramienta).

## Actores

- **Actor principal:** Sistema

## Precondiciones

- La reserva tiene un saldo pendiente y se encuentra dentro de la fecha límite de pronto pago.

## Disparador

Validación de un abono (CU-STD-018 o CU-STD-019) o ejecución de la revisión diaria de vencimientos del sistema.

## Flujo principal

1. El sistema realiza una evaluación de la reserva (activada por un nuevo abono o por rutina diaria).
2. El sistema compara la fecha actual con la `fecha_limite_pronto_pago` de la `ConfiguracionSistema` **de esta convocatoria** (RN-19). Es una fecha de corte igual para todos, no un plazo que arranque con cada reserva (RN-04).
3. Si la fecha sigue vigente, el sistema verifica si el `monto_abonado` cubre el **total ya descontado** — es decir, el bruto menos el pronto pago y, si existe, menos el descuento especial aplicado en secuencia (RN-06).
4. Al cumplirse la condición, el sistema registra el descuento en `DescuentoAplicado` con tipo `pronto_pago` y el porcentaje **configurado en esta convocatoria** (10% por omisión). Si la fila ya existía, no es un error: el descuento ya estaba aplicado (RN-05).
5. El sistema recalcula el total, establece que la reserva está cubierta al 100% y dispara el cambio de estado a Pagada (CU-STD-027).
6. El caso de uso termina.

## Flujos alternativos

### A1. Vencimiento del plazo de pronto pago sin liquidar

1. En el paso 3, el sistema (mediante rutina diaria) detecta que la `fecha_limite_pronto_pago` ha expirado y la reserva no alcanzó el 100% del pago reducido.
2. El sistema retira de la vista del aplicante el aviso del beneficio de pronto pago.
3. El sistema recalcula el `monto_pendiente` retirando **solo** el pronto pago. **Un descuento especial que ya estuviera aplicado se conserva** (RN-05, RN-06): son independientes, y vencer el plazo de una campaña no revoca un convenio.
4. El caso de uso termina.

## Excepciones

> [!note] Opcional
> Sin excepciones relevantes.

## Postcondiciones

- **Éxito:** El descuento queda consolidado de manera permanente y la reserva se marca como pagada, o bien, el beneficio expira y la reserva vuelve a su costo normal.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-04:** pronto pago automático; porcentaje y fecha de corte configurables por convocatoria.
- **RN-05:** como mucho un descuento de cada tipo; aquí el segundo intento es idempotente.
- **RN-06:** se acumula con el especial, aplicándose en secuencia.

> [!note] El título de este caso de uso dice "10%" y es el valor por omisión
> El porcentaje se configura por convocatoria (CU-STD-034). El nombre del archivo se conserva
> para no romper los enlaces ya escritos.
