# FILEY — Prototipo Angular (Módulo Stands)

Prototipo funcional en Angular 19+ con datos mockeados para visualizar y validar el flujo completo del módulo de Stands (STD) de FILEY con clientes y usuarios finales.

> Diseñado y estilizado siguiendo la identidad visual de [filey.org](https://filey.org):
> - **Azul primario** `#01457c`
> - **Dorado/acento** `#c99213`
> - **Tipografía** Open Sans

---

## Características

- **6 vistas de Usuario/Expositor** (U1–U6)
- **10 vistas de Administrador** (A1–A10)
- **Mapa interactivo del showfloor** vía iframe de Godot con bridge `postMessage`
- **Datos mockeados** completos: 4 editoriales, 5 aplicaciones, 25 stands, 3 reservas, 6 movimientos
- **Lógica de negocio real**:
  - Cálculo de precios (m² × costo/m²)
  - Descuentos (pronto pago 10% + especial del admin)
  - Anticipo del 50%
  - Plazo de 30 días
  - Estados de reserva (Por confirmar → Confirmada → Pagada / Cancelada)
  - Umbrales automáticos al validar pagos
  - Snapshots de precio y m² al reservar
- **Role switcher** en el navbar para alternar entre Usuario y Administrador
- **Sin notificaciones de correo** (CU-STD-008 no implementado por no haber backend)

---

## Cobertura

| Módulo | CUs cubiertos |
|---|---|
| A · Aplicación | 001, 002, 003, 004, 005, 006, 007 (008 simulado como cambio de estado) |
| B · Reserva | 009, 010, 011, 012, 013, 014 |
| C · Pago | 015, 016, 017, 018, 019, 020 |
| D · Confirmación y estados | 021, 022, 023, 025, 026, 029, 030 (simulados en servicios) |
| E · Administración | 031, 032, 033, 034, 035, 036, 037 |

**Total: 35/36 CUs cubiertos** (28 con vista + 7 simulados en servicios).

---

## Estructura

```
prototipo/
├── src/app/
│   ├── core/
│   │   ├── layout/       # navbar, user-layout, admin-layout (sidenav)
│   │   └── guards/       # role.guard.ts
│   ├── shared/
│   │   ├── components/   # stand-map (wrapper Godot), status-badge, empty-state
│   │   └── pipes/        # currency-mx, date-mx
│   ├── data/
│   │   ├── models/       # Interfaces TS (Editorial, Aplicacion, Stand, etc.)
│   │   └── mock/         # Datos estáticos (mock-editoriales, mock-aplicaciones, etc.)
│   ├── services/         # auth, aplicacion, stand, carrito, reserva, movimiento, parametros, godot-bridge
│   └── features/
│       ├── usuario/      # u1-aplicacion, u2-mapa, u3-carrito, u4-confirmar-reserva, u5-mi-reserva, u6-pagos
│       └── admin/        # a1-aplicaciones, a2-detalle-aplicacion, a3-reservas, a4-detalle-reserva, a5-pagos-validar, a6-expositores, a7-detalle-expositor, a8-mapa-completo, a9-editar-espacio, a10-configuracion
├── src/assets/godot/     # Build web de Godot (mapa interactivo)
└── src/styles.scss       # Tema FILEY (azul #01457c + dorado #c99213)
```

---

## Cómo ejecutar

```bash
cd prototipo
npm install
npm start
```

Abrir [http://localhost:4200/](http://localhost:4200/) en el navegador.

### Build de producción

```bash
npm run build
```

Los archivos se generan en `dist/prototipo/`.

---

## Flujos de demostración

### Como Usuario (rol por defecto: Editorial Porrúa Yucatán)

1. **Aplicación (U1)** — Revisar la aplicación aceptada, datos de la editorial, contactos, sellos
2. **Mapa (U2)** — Click en stands disponibles para ver detalle y agregarlos al carrito
3. **Carrito (U3)** — Ver selección y subtotal
4. **Confirmar reserva (U4)** — Revisar resumen con descuento pronto pago
5. **Mi reserva (U5)** — Ver estado, alerta de vencimiento, progreso de pago
6. **Pagos (U6)** — Consultar instrucciones, registrar abonos, ver historial

### Como Administrador (usar el switcher en el navbar)

1. **Aplicaciones (A1)** — Filtrar por estado, ver solicitudes
2. **Detalle de aplicación (A2)** — Aceptar / Rechazar / Solicitar cambios
3. **Reservas (A3)** — Ver todas las reservas, filtro de vencidas
4. **Detalle de reserva (A4)** — Acciones: registrar abono manual, aplicar descuento, validar movimientos, resolver vencidas
5. **Pagos por validar (A5)** — Cola de movimientos pendientes
6. **Expositores (A6, A7)** — Perfiles de editoriales aceptadas
7. **Mapa completo (A8)** — Vista admin del mapa con todos los estados
8. **Editar espacio (A9)** — Corregir dimensiones de un stand
9. **Configuración (A10)** — Parámetros del sistema (costos, plazos, datos bancarios)

---

## Integración del mapa Godot

El mapa interactivo se carga vía iframe desde `src/assets/godot/` (build web de Godot). El bridge de comunicación usa `postMessage` con el canal `event-stand-map`.

Mensajes soportados:
- **Host → Godot**: `mapData` (datos del mapa), `setMode` (viewer/editor)
- **Godot → Host**: `ready`, `getMapData`, `openStand`, `addToCart`, `saveMap`, `error`

Ver `src/app/services/godot-bridge.service.ts` y `src/app/shared/components/stand-map.component.ts` para la implementación.

---

## Mock data incluido

| Recurso | Cantidad | Detalle |
|---|---|---|
| Editoriales | 4 | Porrúa, Gandhi, La Nave, Península |
| Aplicaciones | 5 | Cubren los 4 estados (pendiente, aceptada, rechazada, cambios_solicitados) |
| Stands | 25 | Distribuidos en 6 pabellones con estados variados |
| Reservas | 3 | 1 vencida con abono parcial, 1 confirmada, 1 pagada |
| Movimientos | 6 | Pendientes, validados, rechazados, manuales |

---

## Stack técnico

- **Angular 21.2** (standalone components, signals, zoneless)
- **Angular Material 21.2** (componentes UI)
- **TypeScript 5.9**
- **Godot 4.6** (mapa interactivo embebido)
- **RxJS 7.8** (BehaviorSubject para estado)

---

## Limitaciones conocidas (esperadas en un prototipo)

- No hay backend real: la "subida de archivos" es simulada
- No se envían correos de notificación (CU-STD-008 no implementado)
- El estado de la aplicación se pierde al recargar la página (todo en memoria)
- El role-switcher vive solo en el cliente
- Los procesos de sistema (CU-STD-021, 022, 023, 025, 026, 029, 030) se simulan al realizar acciones del usuario
