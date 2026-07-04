# Prototipo — VIS (Visitas Escolares)

HTML/CSS/JS estático demostrativo para el módulo de visitas escolares de FILEY.
Cubre el flujo completo: propuesta de la escuela → revisión administrativa → reserva
de talleres en el catálogo → itinerario confirmado.

## Estructura

```text
prototipo/VIS/
  styles.css           ← estilos del dominio (extiende ../common/styles-base.css)
  app.js               ← interacciones de demostración (feature-detect; sirve a todas las pantallas)
  aplicantes/          ← flujo de la escuela solicitante
  administradores/     ← panel del administrador VIS
```

## Cómo verlo

- **Escuela (participante):** abre `../../REG/aplicantes/index.html` y navega hasta
  la convocatoria de Visitas Escolares; o entra directo en `aplicantes/convocatoria-vis.html`.
- **Administrador:** abre `administradores/admin-login.html` (acceso directo al panel VIS)
  o llega desde `REG/administradores/admin-convocatorias.html`.
- Navega con los botones o con la barra de prototipo superior.

## Mapa de pantallas y flujo

Ver [mapas/VIS.md](../mapas/VIS.md)

## Decisiones de diseño

- **Propuesta por escuela, no por persona:** el formulario captura datos de la institución
  (CCT, nivel educativo, sector, municipio) y hasta 3 grupos de 35 alumnos cada uno
  (máximo 105 alumnos por propuesta — RN-VIS-001).
- **Folio asignado por FILEY:** el sistema genera el folio al enviar; la escuela no lo elige.
- **Catálogo sin filtro de nivel:** `reservar.html` muestra **todos** los talleres
  disponibles sin filtrar por nivel educativo. Las píldoras de nivel en cada tarjeta
  de taller son meramente descriptivas; el aplicante elige según su criterio.
- **Un grupo no puede reservar dos talleres en el mismo bloque horario** (salvo actividades
  de acceso libre). Validación en tiempo real al confirmar el itinerario.
- **Dictamen admin sin pantalla aparte:** las acciones (Aceptar / Solicitar cambios /
  Rechazar) se operan desde el panel de propuestas mediante el detalle expandible de cada
  fila — no hay una ruta de navegación separada para el dictamen en esta maqueta.
- **Admin puede reservar en nombre de la escuela:** `admin-reservar.html` replica el catálogo
  del participante pero con topbar de administración.

- **Discrepancia de nomenclatura de nivel (gap no resuelto):** el formulario de propuesta
  captura `Primaria` como una única opción, pero el catálogo distingue `Primaria alta` y
  `Primaria baja` como categorías separadas. No existe un mapeo definido entre ambas.
  Una escuela que elige "Primaria" en el registro no puede saber qué píldora de catálogo
  corresponde a sus grupos.

## Pendientes (fuera del alcance de esta maqueta)

- Pantalla de edición de propuesta por el aplicante (CU-VIS-002)
- Flujo completo de dictamen: modales de Aceptar / Solicitar cambios / Rechazar con
  campos de texto (CU-VIS-006 / 007 / 008 / 009)
- Badge de estado de revisión en "Mi registro" (Pendiente / Aceptada / Solicitud de cambios
  / Rechazada)
- Notificación al aplicante tras el dictamen (CU-VIS-009)
