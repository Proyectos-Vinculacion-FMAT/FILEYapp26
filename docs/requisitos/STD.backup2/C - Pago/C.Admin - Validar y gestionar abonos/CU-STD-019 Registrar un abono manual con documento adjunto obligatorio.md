---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-019
modulo: C. Pago
actor_principal: Administrador
requisitos_relacionados: []
dependencias:
  - CU-STD-032
  - CU-STD-029
  - CU-STD-030
---
# CU-STD-019 Registrar un abono manual con documento adjunto obligatorio

## Descripción

El administrador registra directamente un pago a favor de la reserva de un expositor (p. ej., si hubo un problema técnico o es un acuerdo excepcional). El movimiento requiere invariablemente un documento que lo sustente y queda validado de forma automática.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene sesión iniciada.
- El administrador se encuentra en la vista de detalle de una reserva específica (A4).
- La reserva tiene un saldo pendiente mayor a cero.

## Disparador

El administrador decide asentar un pago manual seleccionando la opción correspondiente en el detalle de la reserva.

## Flujo principal

1. El administrador hace clic en "Registrar abono manual".
2. El sistema despliega un formulario solicitando:
   - Monto a abonar.
   - Método de pago (transferencia, depósito, cheque).
   - Documento de respaldo (archivo adjunto, obligatorio por RN-15).
3. El administrador captura los datos y sube el documento.
4. El administrador confirma el registro del abono.
5. El sistema valida que todos los campos, especialmente el documento adjunto, estén presentes.
6. El sistema crea el `Movimiento` con origen `admin_manual` y estado `validado`.
7. El sistema vincula el archivo a la entidad `Documento`.
8. El sistema suma inmediatamente el monto al saldo abonado de la `Reserva` y recalcula el saldo pendiente.
9. El sistema evalúa si el nuevo saldo activa los procesos automáticos de confirmación (CU-STD-029) o de liquidación total (CU-STD-030).
10. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Documento de respaldo faltante
1. En el paso 5, el sistema detecta que el administrador no adjuntó ningún archivo.
2. El sistema impide el registro y muestra un error indicando que "Todo abono manual requiere un documento de respaldo obligatorio".
3. El administrador adjunta el archivo y reintenta la operación.

## Postcondiciones

- **Éxito:** El abono se registra directamente como validado y afecta el saldo de la reserva al instante.
- **Fallo:** Si falta información o el documento, no se registra ningún movimiento.

## Reglas de negocio relacionadas

- **RN-08:** Métodos de pago permitidos (no se acepta efectivo).
- **RN-13 / RN-14:** Evaluación de umbrales del 50% y 100% para la confirmación de la reserva.
- **RN-15:** Todo abono manual del administrador requiere documento adjunto obligatorio.
