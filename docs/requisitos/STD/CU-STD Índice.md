---
estado: propuesta
version: "0.2"
tags:
  - tipo/indice
  - dom/std
fecha: 2026-06-18
fecha_actualizacion: 2026-08-27
---
# CU-STD — Índice de casos de uso (Stands)

Inventario de casos de uso del dominio **Stands** (`STD`): proceso de **reserva, pago y
confirmación** de stands.

> [!important] Actualización 2026-08-27 — dos casos de uso nuevos y un documento de reglas
> - **CU-STD-037 y CU-STD-038** cubren *servir los datos del mapa*, uno por público. Son dos y no
>   uno porque devuelven cosas distintas —el aplicante no ve quién reservó qué (RN-09), el
>   administrador sí (RN-18)— y equivocarse ahí filtra información sin dar ningún síntoma.
> - Las reglas de negocio ya no viven sueltas dentro de cada caso de uso: están en
>   [`Reglas de negocio - Stands`](<Reglas de negocio - Stands.md>). Un caso de uso las **cita**;
>   no las redefine.
> - **`RN-08` estaba duplicado** —métodos de pago y transparencia administrativa— y la segunda
>   pasó a ser **`RN-18`**.
> - **CU-STD-039** cubre cómo entra un mapa al sistema: se importa un JSON externo, y solo lo
>   hace el superusuario. Dibujar el mapa dentro del sistema queda fuera de alcance por ahora.

**Actores:** Aplicante (editorial/entidad expositora) · Administrador (coordinador del
showfloor, con acceso a esta feria) · Sistema (procesos automáticos y temporizados).

> [!important] Actualización 2026-08-21 — `STD` ocurre **dentro de una feria**
> El modelo de datos se corrigió a la v2.0 para extraer lo que no le pertenecía:
>
> - **`Cuenta` ya no existe en `STD`.** La identidad es `Persona`, global y única para todo el
>   sistema ([`REG`](<../REG/Modelo de datos - Registros.md>)). Donde estos casos de uso dicen
>   "la cuenta" o "la editorial/cuenta" en prosa, la entidad concreta es `Persona` para la
>   persona y `Editorial` para la empresa: son dos cosas distintas desde la v2.0.
> - **`Evento` ya no existe en `STD`.** La edición de la feria es `Feria`
>   ([`FER`](<../FER/Modelo de datos - Ferias.md>)) y **no se referencia con una FK**: cada feria
>   vive en su propio schema, así que la edición es implícita
>   ([ADR-0003](<../../adr/0003-una-feria-por-schema.md>)).
> - **Ser administrador ya no es un rol de la cuenta**, sino tener acceso a esta feria
>   (`AdminFeria`, [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>)). Quien
>   administra una feria puede operar todo su contenido, stands incluidos.
>
> Lo que estos casos de uso describen no cambia; cambia dónde viven los datos que tocan. Ver
> [`Modelo de datos - Stands`](<Modelo de datos - Stands.md>) §2.

> [!note]
> Cada caso de uso tiene su propio archivo dentro de la carpeta de
> su módulo. Los módulos A y C están subdivididos por actor:
> `A - Solicitud/` (A.Aplicante, A.Admin, A.Sistema) ·
> `B - Reserva/` · `C - Pago/` (C.Aplicante, C.Admin) ·
> `D - Confirmación y estados/` · `E - Administración/`.
> Este índice es la vista general.

> [!note]
> Los casos de uso de **pago** (CU-STD-015 a CU-STD-020, y los de cambio de estado por
> abono) se mantienen aquí por ahora; se traslapan con el dominio futuro `PAG` y podrían
> migrar cuando ese dominio se abra (ver `README.md`).

## A. Solicitud a expositor

### A.Aplicante — Enviar y dar seguimiento a la solicitud

- CU-STD-001 Aplicar a ser expositor (enviar datos y documentos) — *Aplicante*
- CU-STD-002 Editar y reenviar la solicitud tras solicitud de cambios — *Aplicante*
- CU-STD-003 Revisar el estado de la solicitud — *Aplicante*

### A.Admin — Revisar la solicitud

- CU-STD-004 Consultar la lista de solicitudes, filtrable por estado — *Administrador*
- CU-STD-005 Revisar el detalle de una solicitud (documentos e información enviada) — *Administrador*
- CU-STD-006 Aceptar o rechazar una solicitud — *Administrador*
- CU-STD-007 Solicitar cambios a una solicitud — *Administrador*

### A.Sistema — Notificar el resultado

- CU-STD-008 Notificar al aplicante el resultado de su solicitud (correo) — *Sistema*

## B. Reserva

- CU-STD-009 Visualizar el mapa del showfloor (solo disponibles y no disponibles) — *Aplicante*
- CU-STD-010 Consultar el detalle de un stand (dimensiones y precio por m²) — *Aplicante*
- CU-STD-011 Agregar / quitar / gestionar el carrito de stands — *Aplicante*
- CU-STD-012 Realizar la reserva de los stands seleccionados — *Aplicante*
- CU-STD-013 Consultar el estado de mi reserva (mapa, total, abonado, pendiente, descuento) — *Aplicante*
- CU-STD-014 Atender la notificación de posible cancelación de mi reserva — *Aplicante*
- CU-STD-037 Servir los datos del mapa al aplicante — *Aplicante · Sistema*

## C. Pago

### C.Aplicante — Registrar y consultar abonos

- CU-STD-015 Consultar las instrucciones de pago (transferencia / depósito con cheque) — *Aplicante*
- CU-STD-016 Registrar un pago/movimiento con comprobante adjunto — *Aplicante*
- CU-STD-017 Consultar el historial de pagos/abonos — *Aplicante*

### C.Admin — Validar y gestionar abonos

- CU-STD-018 Validar un movimiento de pago y confirmar el abono — *Administrador*
- CU-STD-019 Registrar un abono manual con documento adjunto obligatorio — *Administrador*
- CU-STD-020 Aplicar un descuento especial (override manual) con motivo registrado — *Administrador*

## D. Confirmación y estados (Sistema)

- CU-STD-021 Marcar los stands como reservados al confirmarse la reserva — *Sistema*
- CU-STD-022 Mantener la reserva activa por 30 días en espera del 50% — *Sistema*
- CU-STD-023 Aplicar automáticamente el descuento del 10% por pronto pago — *Sistema*
- CU-STD-024 Notificar al administrador las reservas vencidas (con o sin abono) — *Sistema*
- CU-STD-025 Notificar al aplicante que su reserva puede cancelarse — *Sistema*
- CU-STD-026 Confirmar y bloquear la reserva al cubrirse el 50% (+ notificar por correo) — *Sistema*
- CU-STD-027 Cambiar la reserva a "pagada" al cubrirse el 100% (+ notificar por correo) — *Sistema*

## E. Administración

- CU-STD-028 Consultar la lista de todas las reservas, filtrable — *Administrador*
- CU-STD-029 Ver el detalle de una reserva (abonos, contacto y acciones asociadas) — *Administrador*
- CU-STD-030 Consultar la lista de expositores con solicitud aceptada (habilitados para reservar) — *Administrador*
- CU-STD-031 Ver el detalle de un expositor (reservas, documentos, datos de empresa y contacto) — *Administrador*
- CU-STD-032 Visualizar el mapa completo (con quién reservó y saldo pendiente) — *Administrador*
- CU-STD-033 Corregir/editar un espacio del mapa (p. ej. por ampliación; sin registrar el evento) — *Administrador*
- CU-STD-034 Configurar los parámetros del sistema (costo m², %s, fechas límite, datos bancarios) — *Administrador*
- CU-STD-035 Resolver una reserva vencida: cancelar o prorrogar (nueva fecha) — *Administrador*
- CU-STD-036 Modificar la fecha de corte/bloqueo de una reserva — *Administrador*
- CU-STD-038 Servir los datos del mapa al administrador — *Administrador · Sistema*
- CU-STD-039 Importar el mapa de una convocatoria desde un JSON externo — *Operador de la plataforma*

---

## Artefactos relacionados

- `Reglas de negocio - Stands.md` — **las reglas `RN-01` a `RN-22`. Fuente única.**
- `Modelo de datos - Stands.md` — entidades y datos que el sistema almacena.
- `Proceso de alto nivel - Stands.md` — diagrama del flujo de punta a punta.
- `Estructura de vistas - Stands.md` — arquitectura de ventanas (aplicante y administrador).
