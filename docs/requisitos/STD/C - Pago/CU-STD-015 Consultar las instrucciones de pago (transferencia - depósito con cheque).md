---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-015
modulo: C. Pago
actor_principal: Usuario
requisitos_relacionados: []
dependencias:
  - CU-STD-012
---
# CU-STD-015 Consultar las instrucciones de pago (transferencia / depósito con cheque)

## Descripción

El usuario consulta los datos bancarios y las instrucciones necesarias para realizar el pago o abono de su reserva. El sistema le muestra la información de la cuenta destino y le advierte sobre los métodos de pago permitidos.

## Actores

- **Actor principal:** Usuario (editorial / entidad expositora)

## Precondiciones

- El usuario tiene sesión iniciada.
- El usuario tiene una reserva registrada en el sistema (en estado `Por confirmar` o `Confirmada`) con saldo pendiente por cubrir.

## Disparador

El usuario ingresa a la sección de pagos de su reserva con la intención de realizar un abono y consulta los datos bancarios.

## Flujo principal

1. El usuario navega a la sección de pagos de su reserva (vista U6).
2. El sistema recupera los datos bancarios desde la configuración global (`ParametrosSistema`).
3. El sistema muestra las instrucciones de pago estructuradas según los datos vigentes. A modo de ejemplo, mostrará el titular (ej. *Patronato de la UADY*), el banco, la cuenta, la cuenta CLABE, la sucursal y la instrucción de concepto/referencia (ej. *Nombre de la Editorial*).
4. El sistema subraya la advertencia de que solo se aceptan pagos por transferencia bancaria, depósito o cheque, y que **no se acepta efectivo** (RN-08).
5. El usuario toma nota de los datos para realizar su operación bancaria fuera del sistema.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

> [!note] Opcional
> Sin excepciones relevantes.

## Postcondiciones

- **Éxito:** El usuario visualiza la información bancaria de forma correcta y comprende el método de pago permitido.
- **Fallo:** No aplica.

## Reglas de negocio relacionadas

- **RN-08:** Métodos de pago permitidos: transferencia bancaria, depósito y cheque. No se permite efectivo.
