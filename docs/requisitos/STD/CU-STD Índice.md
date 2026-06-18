---
estado: propuesta
version: 0.1
tags:
  - casos-de-uso
  - stands
fecha: 2026-06-18
---
# CU-STD — Índice de casos de uso (Stands)

Inventario preliminar de casos de uso del dominio **Stands** (`STD`): proceso de
**reserva, pago y confirmación** de stands. Solo títulos; la redacción detallada
(actores, flujo principal y alternos) se hará tras la revisión con el equipo.

**Actores:** Usuario (editorial/entidad expositora) · Administrador (coordinador del
showfloor) · Sistema (procesos automáticos y temporizados).

> [!note]
> Cada caso de uso tiene su propio archivo (plantilla a redactar) dentro de la carpeta de
> su módulo: `A - Aplicación/`, `B - Reserva/`, `C - Pago/`, `D - Confirmación y estados/`
> y `E - Administración/`. Este índice es la vista general.

> [!note]
> Los casos de uso de **pago** (CU-STD-014 a CU-STD-019, y los de cambio de estado por
> abono) se mantienen aquí por ahora; se traslapan con el dominio futuro `PAG` y podrían
> migrar cuando ese dominio se abra (ver `README.md`).

## A. Aplicación a expositor

- CU-STD-001 Aplicar a ser expositor (enviar datos y documentos) — *Usuario*
- CU-STD-002 Editar y reenviar la aplicación tras un rechazo — *Usuario*
- CU-STD-003 Consultar la lista de aplicaciones, filtrable por estado (pendientes / confirmadas / rechazadas) — *Administrador*
- CU-STD-004 Revisar el detalle de una aplicación (documentos e información enviada) — *Administrador*
- CU-STD-005 Aceptar una aplicación (incluye marcar elegibilidad al descuento local del 15%) — *Administrador*
- CU-STD-006 Rechazar una aplicación con motivo — *Administrador*
- CU-STD-007 Notificar al usuario el resultado de su aplicación (correo) — *Sistema*

## B. Reserva

- CU-STD-008 Visualizar el mapa del showfloor (solo disponibles y no disponibles) — *Usuario*
- CU-STD-009 Consultar el detalle de un stand (dimensiones y precio por m²) — *Usuario*
- CU-STD-010 Agregar / quitar / gestionar el carrito de stands — *Usuario*
- CU-STD-011 Realizar la reserva de los stands seleccionados — *Usuario*
- CU-STD-012 Consultar el estado de mi reserva (mapa, total, abonado, pendiente, descuento) — *Usuario*
- CU-STD-013 Atender la notificación de posible cancelación de mi reserva — *Usuario*

## C. Pago

- CU-STD-014 Consultar las instrucciones de pago (transferencia / depósito con cheque) — *Usuario*
- CU-STD-015 Registrar un pago/movimiento con comprobante adjunto — *Usuario*
- CU-STD-016 Consultar el historial de pagos/abonos — *Usuario*
- CU-STD-017 Validar un movimiento de pago y confirmar el abono — *Administrador*
- CU-STD-018 Registrar un abono manual con documento adjunto obligatorio — *Administrador*
- CU-STD-019 Aplicar un descuento especial (override manual) con motivo registrado — *Administrador*

## D. Confirmación y estados

- CU-STD-020 Marcar los stands como reservados al confirmarse la reserva — *Sistema*
- CU-STD-021 Mantener la reserva activa por 30 días en espera del 50% — *Sistema*
- CU-STD-022 Aplicar automáticamente el descuento del 10% por pronto pago — *Sistema*
- CU-STD-023 Liberar automáticamente la reserva sin ningún abono al vencer los 30 días — *Sistema*
- CU-STD-024 Notificar al administrador las reservas con abono parcial vencidas — *Sistema*
- CU-STD-025 Notificar al usuario que su reserva puede cancelarse — *Sistema*
- CU-STD-026 Resolver una reserva vencida con abono parcial: cancelar o prorrogar (nueva fecha) — *Administrador*
- CU-STD-027 Modificar la fecha de corte/bloqueo de una reserva — *Administrador*
- CU-STD-028 Confirmar y bloquear la reserva al cubrirse el 50% (+ notificar por correo) — *Sistema*
- CU-STD-029 Cambiar la reserva a "pagada" al cubrirse el 100% (+ notificar por correo) — *Sistema*

## E. Herramientas de administración (consulta y mapa)

- CU-STD-030 Consultar la lista de todas las reservas, filtrable — *Administrador*
- CU-STD-031 Ver el detalle de una reserva (abonos, contacto y acciones asociadas) — *Administrador*
- CU-STD-032 Consultar la lista de expositores con aplicación aceptada (habilitados para reservar) — *Administrador*
- CU-STD-033 Ver el detalle de un expositor (reservas, documentos, datos de empresa y contacto) — *Administrador*
- CU-STD-034 Visualizar el mapa completo (con quién reservó y saldo pendiente) — *Administrador*
- CU-STD-035 Corregir/editar un espacio del mapa (p. ej. por ampliación; sin registrar el evento) — *Administrador*

---

## Artefactos relacionados

- `Modelo de datos - Stands.md` — entidades y datos que el sistema almacena.
- `Proceso de alto nivel - Stands.md` — diagrama del flujo de punta a punta.
