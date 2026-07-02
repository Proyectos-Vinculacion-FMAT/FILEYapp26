# Mapa de flujo — VIS (Visitas Escolares)

## Participante

Flujo de la escuela solicitante: acceso (via REG) → propuesta → reserva de talleres → itinerario.

| # | Pantalla | Archivo | CU |
| - | -------- | ------- | -- |
| 1–4 | Acceso + convocatorias | *(ver REG — Participante)* | — |
| 5 | Info convocatoria VIS | `aplicantes/convocatoria-vis.html` | — |
| 6 | Registrar mi escuela (propuesta) | `aplicantes/formulario-vis.html` | CU-VIS-001 |
| 7 | Confirmación con folio | `aplicantes/confirmacion-vis.html` | — |
| 8 | Mi registro (detalle de la visita) | `aplicantes/mi-visita.html` | CU-VIS-003 |
| 9 | Reservar talleres (catálogo) | `aplicantes/reservar.html` | CU-VIS-010 / 011 / 012 — ⚠ catálogo no filtra por nivel; brecha C1+C4 en análisis |
| 10 | Ver / confirmar itinerario | `aplicantes/itinerario.html` | CU-VIS-013 / 014 |

## Administrador

Entrada principal: `REG/administradores/admin-convocatorias.html` → VIS.
La pantalla `administradores/admin-login.html` es un acceso simplificado exclusivo de VIS
(útil para navegar el prototipo directamente sin pasar por REG).

```text
administradores/admin-propuestas.html        ← aterrizaje desde REG · panel principal
  ├── administradores/admin-escuela.html     registrar escuela manualmente
  ├── administradores/admin-escuela-edit.html  editar datos / grupos de una escuela
  ├── administradores/admin-reservar.html    reservar talleres en nombre de la escuela
  │     → administradores/itinerario-admin.html  ver / confirmar itinerario
  └── (dictamen: aceptar / solicitar cambios / rechazar — flujo en panel, no pantalla aparte)

administradores/admin-visitas.html           visitas aceptadas (vista de seguimiento)
```

| # | Pantalla | Archivo | CU |
| - | -------- | ------- | -- |
| — | Acceso admin (login VIS directo) | `administradores/admin-login.html` | CU-REG-003 |
| A2 | Propuestas — lista + dictamen | `administradores/admin-propuestas.html` | CU-VIS-004–009 / 015–017 |
| A2b | Reservar talleres (por la escuela) | `administradores/admin-reservar.html` | CU-VIS-010 / 011 / 012 |
| A3a | Itinerario de visita (admin) | `administradores/itinerario-admin.html` | CU-VIS-013 / 014 |
| A3b | Visitas aceptadas | `administradores/admin-visitas.html` | CU-VIS-015–017 |
| A3c | Registrar escuela manualmente | `administradores/admin-escuela.html` | CU-VIS-016 |
| A3d | Editar datos / grupos de escuela | `administradores/admin-escuela-edit.html` | CU-VIS-016 |
