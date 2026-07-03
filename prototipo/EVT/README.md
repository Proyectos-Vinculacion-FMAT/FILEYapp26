# Prototipo UI — Eventos FILEY 2027 (flujo del proponente)

Prototipo **estático en HTML/CSS** para mostrar a los clientes (Hipólito y equipo).
Cubre el flujo del **proponente externo** desde que entra por primera vez a la página
hasta que envía su propuesta de actividad para el programa general (Eventos).

> Diseño **demostrativo**: no guarda datos ni envía nada. Los botones navegan entre
> pantallas para simular el recorrido completo.

## Estructura de carpetas

El prototipo se divide por tipo de usuario, compartiendo la hoja de estilos base:

```
prototipo/EVT/
├── styles.css                 ← paleta/estilos compartidos (raíz)
├── aplicantes/                ← flujo del proponente externo (index.html, otp.html, …)
│   └── app.js                 ← campos dinámicos del formulario
└── administradores/           ← vista del administrador (Hipólito)
    └── admin.css              ← shell del panel: sidebar, chips, calendario, horario
```

Los HTML de `aplicantes/` y `administradores/` enlazan `../styles.css`; los de
`administradores/` además enlazan su `admin.css` local.

## Cómo verlo

Flujo del proponente: abre **`aplicantes/index.html`**. Vista del administrador: abre
**`administradores/admin-otp.html`** (o entra desde el enlace "Acceso administrativo" del
`index.html` del proponente). Avanza con los botones o con la barra superior de prototipo.

## Pantallas (en orden del flujo)

| # | Archivo | Pantalla | CU relacionado |
|---|---------|----------|----------------|
| 1 | `index.html` | Acceso (ingresa correo) | CU-REG-002 |
| 2 | `registro.html` | Crear cuenta (nombre + teléfono) — solo primera vez | CU-REG-001 |
| 3 | `otp.html` | Código de acceso por correo (OTP) | CU-REG-002 |
| 4 | `convocatorias.html` | Convocatorias abiertas (Stands, Infantil/Juvenil, Eventos) | — |
| 5 | `convocatoria-eventos.html` | Información de la convocatoria (fechas, tipos, requisitos, cupos) → Aplicar | CU-EVE-001 |
| 6 | `formulario.html` | Formulario de propuesta (datos de participación → tipo → campos dinámicos) | CU-EVE-002 / 003 |
| 7 | `confirmacion.html` | Confirmación con folio | CU-EVE-002 |
| + | `mis-propuestas.html` | Seguimiento de propuestas (P2) | CU-EVE-036 |

## Decisiones de diseño acordadas

- **Datos de participación primero:** nombre, correo y teléfono se precargan de la cuenta;
  dependencia, cargo y ciudad/estado se piden en el formulario **antes** de elegir el tipo,
  porque son comunes a todos los tipos de actividad.
- **Tres convocatorias visibles** para todos; las **cerradas no desaparecen**, se muestran
  con el estado "Convocatoria cerrada".
- **Página de información** previa al formulario, con botón de "Aplicar".
- **Campos por tipo:** el formulario muestra dinámicamente los campos de cada uno de los
  8 tipos de actividad, tomados del documento *Registro de propuestas FILEY 2027*.

## Identidad visual

- **Colores:** azul institucional + dorado (UADY), según `diseño_UI.md`.
- **Referencias:** distribución y estilo de filey.org / uady.mx.
- Logo representado como marca tipográfica "FILEY" (placeholder del logo oficial UADY/FILEY).

## Archivos de apoyo

- `styles.css` — estilos compartidos (paleta, componentes).
- `app.js` — genera los campos del formulario según el tipo de actividad elegido.
