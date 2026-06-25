# Propuesta

> [!info] Estado del documento (actualizado 2026-06-25)
> Esta es una **propuesta histórica previa a la Junta 3**. Su criterio sobre visitas escolares quedó **superado**: la **visita escolar entró en alcance** en la Junta 3 como dominio propio **`VIS`** (un tipo de propuesta más dentro de Convocatorias `REG`), con sus casos de uso en [requisitos/VIS/](<../../requisitos/VIS/CU-VIS Índice.md>). Además, el documento entregado por FILEY [Software para agendar escuelas](<../extraido/Software para agendar escuelas.md>) confirma que una escuela puede reservar **varios talleres** (una sala de cine **o** 3 talleres de 35 = 105), no uno solo. Ver el [Análisis VIS vs Software para agendar escuelas](<Análisis VIS vs Software para agendar escuelas.md>).

## Convención

Actores: Usuario · Administrador · Sistema
Una sola responsabilidad por CU (CRUD separados).
Numeración solo para conteo, independiente del nombre.
Stands ya existe: `CU-STD-001..035` en `docs/requisitos/STD/`, se mantiene como está.
~~Visita escolar queda fuera del scope actual (registro especulativo, sin formulario real aún); no se propone por ahora.~~ **(Superado — Junta 3:** la visita escolar es ahora el dominio `VIS`, en alcance; ver callout de estado arriba.**)**

## REG — Registro común

_Datos básicos del solicitante (núcleo común), compartidos por eventos y stands. Paso previo reutilizable. La selección del tipo de actividad enruta (lógica condicional) a la sección especializada que corresponda._

- CU-REG-001 Capturar los datos básicos del solicitante (núcleo común) — Usuario
- CU-REG-002 Editar los datos básicos antes de enviar — Usuario
- CU-REG-003 Seleccionar el tipo de actividad para mostrar la sección específica correspondiente (lógica condicional) — Usuario
- CU-REG-004 Validar que el formulario esté completo antes de permitir el envío — Sistema
- CU-REG-005 Guardar la respuesta del formulario al enviarlo (BD/Excel) — Sistema
- CU-REG-006 Enviar correo automático de respaldo al solicitante tras el envío — Sistema
- CU-REG-007 Generar la ficha concentrada (PDF) por solicitud para la coordinación — Sistema

## EVT — Eventos (Contenidos + Talleres)

_Core unificado: un taller es un tipo de evento. Mismo flujo para Hipólito y Elvira. El enrutamiento manda cada propuesta a un solo panel; la presentación de libro infantil/juvenil se reenruta al panel de Elvira._

**A. Propuesta**  

- CU-EVT-001 Registrar una propuesta de evento según su tipo (Contenidos o Taller) — Usuario
- CU-EVT-002 Editar la propuesta dentro de la ventana de modificación — Usuario
- CU-EVT-003 Consultar mis propuestas y su estado — Usuario

**B. Revisión**  

- CU-EVT-004 Enrutar la propuesta al panel correspondiente según su tipo (Hipólito / Elvira) — Sistema
- CU-EVT-005 Consultar la lista de propuestas de mi panel, filtrable por estado y tipo — Administrador (Hipólito o Elvira)
- CU-EVT-006 Revisar el detalle de una propuesta (datos y archivos) — Administrador (Hipólito o Elvira)
- CU-EVT-007 Aceptar una propuesta — Administrador (Hipólito o Elvira)
- CU-EVT-008 Rechazar una propuesta con motivo — Administrador (Hipólito o Elvira)
- CU-EVT-009 Marcar un evento del panel como apto para nivel infantil/juvenil (catálogo escolar) — Administrador (Hipólito)
- CU-EVT-010 Notificar en lote el resultado a aceptados y rechazados — Sistema
- CU-EVT-011 Registrar el envío de la notificación (para deslinde) — Sistema

**C. Cierre y administración**  

- CU-EVT-012 Configurar la fecha de cierre de la ventana de modificación — Administrador (Hipólito o Elvira)
- CU-EVT-013 Cerrar la ventana y bloquear cambios al vencer la fecha — Sistema
- CU-EVT-014 Consultar el contador de aceptados, rechazados y espacios disponibles en mi panel — Administrador (Hipólito o Elvira)

## PRG — Programación

_Andamiaje para empezar (pendiente de confirmar con el cliente). Dos programas independientes, uno por panel: el maestro de Hipólito (Contenidos) y el de talleres de Elvira. Cada uno consume las actividades aprobadas de su propio panel. La fecha/sala/horario la asigna FILEY, no el proponente. Solo el programa de Elvira admite repetición de una misma actividad._

**A. Armado del programa**  

- CU-PRG-001 Consultar las actividades aprobadas de mi panel pendientes de programar — Administrador (Hipólito o Elvira)
- CU-PRG-002 Asignar una actividad aprobada a una sala y un bloque horario — Administrador (Hipólito o Elvira)
- CU-PRG-003 Editar la asignación (sala u horario) de una actividad ya programada — Administrador (Hipólito o Elvira)
- CU-PRG-004 Quitar una actividad del programa (liberar su asignación) — Administrador (Hipólito o Elvira)
- CU-PRG-005 Programar una misma actividad en varias ocasiones para llenar huecos — Administrador (Elvira)
- CU-PRG-006 Validar que el aforo del grupo no supere el aforo de la sala al asignar — Sistema
- CU-PRG-007 Validar que la sala esté disponible en el día y turno de la asignación — Sistema

**B. Notificación y confirmación de asignación**  

- CU-PRG-008 Notificar al registrante su fecha, sala y horario asignados (segunda notificación) — Sistema
- CU-PRG-009 Confirmar mi disponibilidad para el horario asignado — Usuario (registrante)

**C. Visibilidad y exportación**  

- CU-PRG-010 Consultar en solo lectura el programa del otro panel — Administrador (Hipólito o Elvira)
- CU-PRG-011 Exportar el programa a Excel, Word o PDF para la pulida final — Administrador (Hipólito o Elvira)
- CU-PRG-012 Consultar el programa publicado en la web app — Usuario

## SAL — Salas y salones

_Andamiaje para empezar (pendiente de confirmar catálogo y aforos reales). CRUD único de espacios, compartido y visible para Hipólito y Elvira; ambos pueden crear salones. Un salón nace con una sala por defecto; agregar subdivisiones crea más salas. No aplica a stands._

**A. Salones**  

- CU-SAL-001 Crear un salón (se genera su primera sala automáticamente) — Administrador (Hipólito o Elvira)
- CU-SAL-002 Editar los datos de un salón — Administrador (Hipólito o Elvira)
- CU-SAL-003 Eliminar un salón — Administrador (Hipólito o Elvira)

**B. Salas**  

- CU-SAL-004 Agregar una sala (subdivisión) a un salón — Administrador (Hipólito o Elvira)
- CU-SAL-005 Editar una sala (aforo y disponibilidad) — Administrador (Hipólito o Elvira)
- CU-SAL-006 Eliminar una sala — Administrador (Hipólito o Elvira)

**C. Consulta**  

- CU-SAL-007 Consultar el catálogo compartido de salas y salones — Administrador (Hipólito o Elvira)
- CU-SAL-008 Consultar el detalle de una sala (aforo y disponibilidad) — Administrador (Hipólito o Elvira)