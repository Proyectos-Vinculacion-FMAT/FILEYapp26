# Mapa de flujo — REG (Acceso y módulos)

REG es el punto de entrada compartido: gestiona el acceso de participantes y administradores
y los dirige a su dominio de contenido (EVT, VIS, TAL).

## Participante

| # | Pantalla | Archivo | CU |
| - | -------- | ------- | -- |
| 1 | Acceso (ingresa correo) | `aplicantes/index.html` | CU-REG-002 |
| 2 | Crear cuenta — solo primera vez | `aplicantes/registro.html` | CU-REG-001 |
| 3 | Código OTP | `aplicantes/otp.html` | CU-REG-002 |
| 4 | Convocatorias abiertas → sale a EVT / VIS / TAL | `aplicantes/convocatorias.html` | — |

## Administrador

| # | Pantalla | Archivo | CU |
| - | -------- | ------- | -- |
| 1 | Acceso admin (ingresa correo) | `administradores/admin-login.html` | CU-REG-003 |
| 2 | Código OTP admin | `administradores/admin-otp.html` | CU-REG-003 |
| 3 | Selección de módulo → sale a EVT admin / VIS admin / TAL admin | `administradores/admin-convocatorias.html` | CU-REG-006 |
