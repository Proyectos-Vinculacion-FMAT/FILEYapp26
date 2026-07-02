# Prototipo — EVT (Eventos)

HTML/CSS/JS estático demostrativo para el módulo de propuestas de actividades FILEY.
No guarda ni envía datos; los botones navegan entre pantallas para simular el recorrido.

## Estructura

```text
prototipo/EVT/
  index.html          ← hub selector de rol (aplicante / administrador)
  styles.css          ← estilos del dominio (extiende ../common/styles-base.css)
  app.js              ← campos dinámicos del formulario de propuesta
  aplicantes/         ← flujo del proponente externo
  administradores/    ← panel del administrador
    admin.css         ← shell del panel: sidebar, chips, calendario, rejilla de horario
```

## Cómo verlo

- **Proponente:** abre `aplicantes/index.html`
- **Administrador:** abre `administradores/admin-otp.html` (o desde el enlace
  "¿Eres parte del comité organizador?" en `aplicantes/index.html`)
- Navega con los botones o con la barra de prototipo superior.

## Mapa de pantallas y flujo

Ver [mapas/EVT.md](../mapas/EVT.md)

## Decisiones de diseño

- **Datos comunes primero:** nombre/correo/teléfono se precargan de la cuenta; dependencia,
  cargo y ciudad/estado se capturan en el formulario antes de elegir el tipo de actividad,
  porque son comunes a todos los tipos.
- **Convocatorias cerradas visibles:** se atenúan con el estado "Convocatoria cerrada" pero
  no desaparecen.
- **Acceso admin por OTP** (misma mecánica que el aplicante — decisión de equipo;
  CU-REG-003 actualizado para usar OTP en lugar de contraseña).
- **Hipólito como admin general** (`modulo = *`): ve los 3 módulos (Eventos, Infantil/Juvenil,
  Stands) pero solo Eventos es navegable en esta maqueta. Los otros aparecen como
  "Próximamente".
- **Tablero de programación híbrido:** rejilla salas × bloques como lienzo principal + riel
  lateral "Por programar". Clic en lugar de arrastre (se difiere la física del arrastre;
  layout y flujo son los definitivos). El modal de asignación imita el diálogo "Nuevo evento"
  de Outlook.
- **Guardado implícito** en programación: cada cambio queda guardado sin botón explícito.
- **Dictamen con modales** dentro del detalle de propuesta (no página aparte).
- **Seguimiento** como sección propia en el sidebar (no inline en la lista).
- **Panel de Talleres (Elvira) pendiente:** reutilizará este mismo esqueleto parametrizado;
  los parámetros que cambian están documentados en [mapas/EVT.md](../mapas/EVT.md).

## Pendientes (fuera del alcance de esta maqueta)

- Re-dictamen: cambiar un dictamen ya emitido (CU-EVT-009 A3)
- Gestión de usuarios administrativos / superadmin (CU-REG-005)
- Panel de Talleres (Elvira) — ver nota en decisiones de diseño
