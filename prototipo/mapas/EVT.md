# Mapa de flujo — EVT (Eventos)

## Participante

Flujo del proponente externo: acceso → formulario de propuesta → seguimiento.

| # | Pantalla | Archivo | CU |
| - | -------- | ------- | -- |
| 1 | Acceso (correo) | `aplicantes/index.html` | CU-REG-002 |
| 2 | Crear cuenta — solo primera vez | `aplicantes/registro.html` | CU-REG-001 |
| 3 | Código OTP | `aplicantes/otp.html` | CU-REG-002 |
| 4 | Convocatorias abiertas | `aplicantes/convocatorias.html` | — |
| 5 | Info convocatoria Eventos | `aplicantes/convocatoria-eventos.html` | CU-EVE-001 |
| 6 | Formulario de propuesta (campos dinámicos por tipo) | `aplicantes/formulario.html` | CU-EVE-002 / 003 |
| 7 | Confirmación con folio | `aplicantes/confirmacion.html` | CU-EVE-002 |
| + | Mis propuestas (seguimiento) | `aplicantes/mis-propuestas.html` | CU-EVE-036 |

---

## Administrador

Flujo del administrador general (Hipólito): OTP → selección de módulo → panel EVT.

```text
administradores/admin-otp.html          ← entrada vía "Acceso administrativo" en aplicantes/index.html
  → admin-modulos.html                  3 módulos; solo Eventos es navegable en esta maqueta
    → admin-evt-propuestas.html         dashboard: tabla filtrable + tarjetas de resumen
        ├── admin-evt-detalle-propuesta.html   detalle + dictamen modal (Aceptar / Solicitar cambios / Rechazar)
        │   └── admin-evt-detalle-rechazada.html   solo lectura — propuesta ya rechazada
        └── admin-evt-horario.html      tablero híbrido: riel "Por programar" + rejilla salas×bloques + modal Outlook
            └── admin-evt-programar.html       formulario de asignación sala + bloque(s)
    → admin-evt-notificaciones.html     resultados de selección en lote
    → admin-evt-seguimiento.html        contadores por estado + cupos disponibles
    → admin-evt-configuracion.html      fechas clave + cupos por categoría
```

| # | Pantalla | Archivo | CU |
| - | -------- | ------- | -- |
| 1 | OTP admin | `administradores/admin-otp.html` | CU-REG-003 |
| 2 | Selección de módulo | `administradores/admin-modulos.html` | CU-REG-006 |
| 3 | Propuestas — lista y dictamen | `administradores/admin-evt-propuestas.html` | CU-EVT-007 / 011 |
| 4 | Detalle de propuesta + dictamen | `administradores/admin-evt-detalle-propuesta.html` | CU-EVT-008 / 009 / 012 |
| 4b | Detalle propuesta rechazada (solo lectura) | `administradores/admin-evt-detalle-rechazada.html` | CU-EVT-008 |
| 5 | Tablero de programación | `administradores/admin-evt-horario.html` | CU-PRG-001 / 002 / 008 |
| 5b | Formulario de programación | `administradores/admin-evt-programar.html` | CU-PRG-002 / 003 / 004 |
| 6 | Notificaciones en lote | `administradores/admin-evt-notificaciones.html` | CU-EVT-010 |
| 7 | Seguimiento (contadores) | `administradores/admin-evt-seguimiento.html` | CU-EVT-011 |
| 8 | Configuración (fechas + cupos) | `administradores/admin-evt-configuracion.html` | CU-EVT-001 |
