---
estado: propuesta
version: 0.1
tags:
  - tipo/indice
  - dom/std
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
> Los casos de uso de **pago** (CU-STD-015 a CU-STD-020, y los de cambio de estado por
> abono) se mantienen aquí por ahora; se traslapan con el dominio futuro `PAG` y podrían
> migrar cuando ese dominio se abra (ver `README.md`).

## A. Aplicación a expositor

- CU-STD-001 Aplicar a ser expositor (enviar datos y documentos) — *Usuario*
- CU-STD-002 Editar y reenviar la aplicación tras solicitud de cambios — *Usuario*
- CU-STD-003 Revisar el estado de la aplicación — *Usuario*
- CU-STD-004 Consultar la lista de aplicaciones, filtrable por estado — *Administrador*
- CU-STD-005 Revisar el detalle de una aplicación (documentos e información enviada) — *Administrador*
- CU-STD-006 Aceptar o rechazar una aplicación — *Administrador*
- CU-STD-007 Solicitar cambios a una aplicación — *Administrador*
- CU-STD-008 Notificar al usuario el resultado de su aplicación (correo) — *Sistema*

## B. Reserva

- CU-STD-009 Visualizar el mapa del showfloor (solo disponibles y no disponibles) — *Usuario*
- CU-STD-010 Consultar el detalle de un stand (dimensiones y precio por m²) — *Usuario*
- CU-STD-011 Agregar / quitar / gestionar el carrito de stands — *Usuario*
- CU-STD-012 Realizar la reserva de los stands seleccionados — *Usuario*
- CU-STD-013 Consultar el estado de mi reserva (mapa, total, abonado, pendiente, descuento) — *Usuario*
- CU-STD-014 Atender la notificación de posible cancelación de mi reserva — *Usuario*

## C. Pago

- CU-STD-015 Consultar las instrucciones de pago (transferencia / depósito con cheque) — *Usuario*
- CU-STD-016 Registrar un pago/movimiento con comprobante adjunto — *Usuario*
- CU-STD-017 Consultar el historial de pagos/abonos — *Usuario*
- CU-STD-018 Validar un movimiento de pago y confirmar el abono — *Administrador*
- CU-STD-019 Registrar un abono manual con documento adjunto obligatorio — *Administrador*
- CU-STD-020 Aplicar un descuento especial (override manual) con motivo registrado — *Administrador*

## D. Confirmación y estados

- CU-STD-021 Marcar los stands como reservados al confirmarse la reserva — *Sistema*
- CU-STD-022 Mantener la reserva activa por 30 días en espera del 50% — *Sistema*
- CU-STD-023 Aplicar automáticamente el descuento del 10% por pronto pago — *Sistema*
- CU-STD-025 Notificar al administrador las reservas vencidas (con o sin abono) — *Sistema*
- CU-STD-026 Notificar al usuario que su reserva puede cancelarse — *Sistema*
- CU-STD-027 Resolver una reserva vencida: cancelar o prorrogar (nueva fecha) — *Administrador*
- CU-STD-028 Modificar la fecha de corte/bloqueo de una reserva — *Administrador*
- CU-STD-029 Confirmar y bloquear la reserva al cubrirse el 50% (+ notificar por correo) — *Sistema*
- CU-STD-030 Cambiar la reserva a "pagada" al cubrirse el 100% (+ notificar por correo) — *Sistema*

## E. Herramientas de administración (consulta y mapa)

- CU-STD-031 Consultar la lista de todas las reservas, filtrable — *Administrador*
- CU-STD-032 Ver el detalle de una reserva (abonos, contacto y acciones asociadas) — *Administrador*
- CU-STD-033 Consultar la lista de expositores con aplicación aceptada (habilitados para reservar) — *Administrador*
- CU-STD-034 Ver el detalle de un expositor (reservas, documentos, datos de empresa y contacto) — *Administrador*
- CU-STD-035 Visualizar el mapa completo (con quién reservó y saldo pendiente) — *Administrador*
- CU-STD-036 Corregir/editar un espacio del mapa (p. ej. por ampliación; sin registrar el evento) — *Administrador*
- CU-STD-037 Configurar los parámetros del sistema (costo m², %s, fechas límite, datos bancarios) — *Administrador*

---

## Artefactos relacionados

- `Modelo de datos - Stands.md` — entidades y datos que el sistema almacena.
- `Proceso de alto nivel - Stands.md` — diagrama del flujo de punta a punta.
- `Estructura de vistas - Stands.md` — arquitectura de ventanas (usuario y administrador).
