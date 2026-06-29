---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-016
modulo: C. Pago
actor_principal: Aplicante
requisitos_relacionados: []
dependencias:
  - CU-STD-012
  - CU-STD-015
---
# CU-STD-016 Registrar un pago o movimiento con comprobante adjunto

## Descripción

El aplicante registra un abono realizado para su reserva, ingresando el monto, el método utilizado y subiendo el comprobante oficial. El movimiento queda en estado pendiente hasta ser validado por el administrador.

## Actores

- **Actor principal:** Aplicante (editorial / entidad expositora)

## Precondiciones

- El aplicante tiene sesión iniciada.
- El aplicante tiene una reserva registrada en estado `Por confirmar` o `Confirmada`.
- La reserva tiene un saldo pendiente mayor a cero.

## Disparador

El aplicante realiza un pago bancario y decide registrar el comprobante en la plataforma para que se acredite a su reserva.

## Flujo principal

1. El aplicante accede a la sección de pagos de su reserva y selecciona la opción de "Registrar abono".
2. El sistema despliega un formulario solicitando los siguientes datos:
   - Monto abonado.
   - Método de pago (lista desplegable: transferencia, depósito, cheque).
   - Documento comprobante (archivo adjunto).
3. El aplicante completa los datos y adjunta el comprobante bancario.
4. El aplicante envía el formulario.
5. El sistema valida que todos los campos requeridos estén presentes y que el monto sea válido (mayor a cero).
6. El sistema crea un registro en la entidad `Movimiento` asociado a la reserva, con origen `aplicante` y estado `pendiente_validacion`.
7. El sistema guarda el comprobante en la entidad `Documento` vinculándolo al movimiento.
8. El sistema muestra un mensaje de confirmación al aplicante, indicando que su pago está en revisión por el administrador.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Formulario incompleto o archivo faltante
1. En el paso 5, el sistema detecta que falta ingresar el monto, seleccionar el método o adjuntar el comprobante.
2. El sistema muestra un mensaje de error señalando los campos faltantes.
3. El aplicante corrige la información y reintenta el envío (regresa al paso 4).

### E2. Monto excede el saldo pendiente
1. En el paso 5, el sistema detecta que el monto ingresado es mayor al saldo pendiente de la reserva.
2. El sistema muestra una advertencia indicando el saldo máximo que puede abonar.
3. El aplicante ajusta el monto y reintenta el envío (regresa al paso 4).

## Postcondiciones

- **Éxito:** Se registra un nuevo movimiento en estado `pendiente_validacion` que queda en la cola de revisión del administrador (CU-STD-018). El saldo de la reserva aún no se actualiza hasta su validación.
- **Fallo:** No se registra el movimiento si el aplicante abandona el formulario o no adjunta el comprobante.

## Reglas de negocio relacionadas

- **RN-08:** Métodos de pago permitidos: transferencia bancaria, depósito y cheque. No se permite efectivo.
