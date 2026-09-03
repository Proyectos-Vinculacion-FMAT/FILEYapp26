---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-020
modulo: C. Pago
actor_principal: Administrador
requisitos_relacionados: []
dependencias:
  - CU-STD-029
  - CU-STD-026
  - CU-STD-027
---
# CU-STD-020 Aplicar un descuento especial (override manual) con motivo registrado

## Descripción

El administrador otorga de manera manual y excepcional un descuento sobre el monto total de la reserva de un expositor. Esta acción requiere obligatoriamente registrar un motivo que justifique la decisión, fungiendo como un "override" de las reglas normales.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada.
- El administrador se encuentra en la vista de detalle de una reserva específica (A4).

## Disparador

El administrador detecta que procede aplicar un descuento fuera de los estándares (por ejemplo, debido a convenios especiales institucionales) y selecciona la acción "Aplicar descuento especial".

## Flujo principal

1. El administrador hace clic en "Aplicar descuento especial" desde el detalle de la reserva.
2. El sistema muestra un formulario solicitando:
   - Porcentaje de descuento a aplicar.
   - Motivo / justificación (campo de texto obligatorio).
3. El administrador ingresa el porcentaje y redacta la justificación.
4. El administrador confirma la acción.
5. El sistema valida que el motivo haya sido proporcionado.
6. El sistema crea un registro en `DescuentoAplicado` con tipo `especial`. Si la reserva **ya tenía** un especial, la escritura falla y se muestra el error (RN-05): para cambiar el porcentaje se modifica el que existe o se retira, no se acumula otro encima.
7. El sistema recalcula inmediatamente el `monto_total` y, en consecuencia, el `monto_pendiente`. Si la reserva tiene además un pronto pago, **los dos se aplican en secuencia** (RN-06): el especial se calcula sobre el subtotal ya descontado, así que 10% y 15% dan un 23.5% efectivo, no un 25%.
8. El sistema evalúa si con el nuevo monto total reducido, el saldo que el aplicante ya había abonado (`monto_abonado`) es suficiente para alcanzar el 50% o el 100%, disparando, si aplica, los procesos automáticos de confirmación (CU-STD-026) o liquidación (CU-STD-027).
9. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Motivo faltante
1. En el paso 5, el sistema detecta que el administrador dejó el campo de motivo en blanco.
2. El sistema impide aplicar el descuento y resalta el campo de motivo como obligatorio (RN-07).
3. El administrador escribe el motivo y reintenta la operación.

## Postcondiciones

- **Éxito:** La reserva reduce su costo total según el porcentaje indicado y guarda el rastro de auditoría del motivo.
- **Fallo:** El descuento no se aplica si no se ingresa la justificación requerida.

## Reglas de negocio relacionadas

- **RN-07:** el administrador fija el porcentaje caso por caso y el motivo es obligatorio.
- **RN-05:** como mucho un especial por reserva; el segundo intento es un error visible.
- **RN-06:** se acumula con el pronto pago, aplicándose en secuencia.
