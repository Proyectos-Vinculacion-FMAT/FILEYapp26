---
estado: propuesta
version: 0.6
tags:
  - tipo/indice
  - dom/tal
fecha: 2026-06-25
fecha_actualizacion: 2026-06-29
---
# CU-TAL — Índice de casos de uso (Actividades infantiles y juveniles)

Inventario de casos de uso del dominio **Talleres** (`TAL`): la convocatoria de **actividades dirigidas a infancias y juventudes** que administra **Elvira**, paralela —y simétrica en su ciclo de revisión— a la convocatoria del programa general (Hipólito, dominio `EVT`). Las notas y los ajustes de homologación se concentran al final de este índice.

**Actores:** Tallerista (persona/institución que propone una actividad infantil/juvenil) · Administrador (Elvira y su equipo) · Sistema.

## A. Convocatoria

- [CU-TAL-001 Configurar la convocatoria de actividades infantiles y juveniles](<A - Convocatoria/CU-TAL-001 Configurar la convocatoria de actividades infantiles y juveniles.md>)
- [CU-TAL-002 Registro de los datos de la propuesta de actividad infantil o juvenil](<A - Convocatoria/CU-TAL-002 Registo de los datos de la propuesta de actividad infantil o juvenil.md>)
- [CU-TAL-003 Consultar mis propuestas de actividad y revisar su estado actual](<A - Convocatoria/CU-TAL-003 Consultar mis propuestas de actividad y revisar su estado actual.md>)

## B. Revisión y Selección

- [CU-TAL-004 Editar una propuesta en respuesta a una solicitud de cambios del administrador](<B - Revisión y Selección/CU-TAL-004 Editar una propuesta en respuesta a una solicitud de cambios del administrador.md>)

## C. Cierre y Constancias

- [CU-TAL-005 Descargar constancia de participación](<C - Cierre y Constancias/CU-TAL-005 Descargar constancia de participación.md>)

## D. Publicación

- [CU-TAL-006 Generar la ficha PDF de una actividad](<D - Publicación/CU-TAL-006 Generar la ficha PDF de una actividad.md>)

## E. Herramientas de Administración

- [CU-TAL-007 Consultar la lista de propuestas, filtrable](<E - Herramientas de Administración/CU-TAL-007 Consultar la lista de propuestas, filtrable.md>)
- [CU-TAL-008 Revisar el detalle de una propuesta](<E - Herramientas de Administración/CU-TAL-008 Revisar el detalle de una propuesta.md>)
- [CU-TAL-009 Dictaminar una propuesta](<E - Herramientas de Administración/CU-TAL-009 Dictaminar una propuesta.md>)
- [CU-TAL-010 Enviar notificaciones de resultado en lote](<E - Herramientas de Administración/CU-TAL-010 Enviar notificaciones de resultado en lote.md>)

---

## Notas y aclaraciones

> [!warning] Corrección directa del cliente (2026-06-29) — Elvira sí dictamina en el sistema
> La primera homologación de `TAL` (a partir de la rama `main-juan`) asumía que la selección
> de Elvira era manual y fuera del sistema, sin un proceso de aceptar/solicitar cambios/
> rechazar. **El cliente corrigió esto directamente:** el flujo real es *Tallerista registra
> (forms) → Elvira revisa y dictamina → la aceptada se vuelve Actividad → se programa en `PRG`
> → se notifica el preliminar → se ajusta → cuando el horario queda final, el catálogo se
> publica para `VIS`*. Por eso los CUs de revisión y dictamen se incorporan ahora en la sección **D (Herramientas de Administración)**,
> simétrica a la de `EVT`, que no existía en la versión anterior.

<!-- -->

> [!note] La sala y el horario los asigna `PRG`, desde el mismo panel de `TAL`
> La programación no tiene pantalla aparte: una vez que el Administrador acepta una propuesta
> en el panel de `TAL`, el botón **"Revisar"** se reemplaza por **"Programar"** en ese mismo
> renglón (dispara CU-PRG-002). Los CUs de asignación, edición y eliminación de programaciones
> pertenecen a `PRG` (ver [`PRG/CU-PRG Índice.md`](<../PRG/CU-PRG Índice.md>)); el catálogo
> de salas/espacios es el catálogo único global de `SAL` (ver `SAL/CU-SAL Índice.md`).
> CU-TAL-001 ya no configura espacios propios (corrección 2026-06-29).

<!-- -->

> [!warning] Precisión directa del cliente (2026-06-29) — VIS solo consume horario final
> El catálogo de talleres que consume `VIS` (CU-VIS-010) **no se publica con el horario
> preliminar**: solo cuando Elvira termina de ajustar y el horario queda **final**. El
> mecanismo exacto para marcar ese estado queda pendiente de definir (ver "Pendientes" abajo y
> en `PRG/Modelo de datos - Programación.md`).

<!-- -->

> [!note] Identidad y registro de cuenta
> El alta de cuenta y el acceso (OTP) del tallerista dependen del Core Registros: ver
> `REG/CU-REG Índice.md` — CU-REG-001 y CU-REG-002.

<!-- -->

> [!note] Flujo de alto nivel
> Flujo operativo: `Convocatoria → Revisión y dictamen → Cierre y Constancias`; la
> programación en `PRG` ocurre desde el mismo panel tras aceptar. Las secciones del
> índice agrupan por tipo de funcionalidad; **Herramientas de Administración** se lista
> al final como referencia.
> Ver el diagrama completo en [`Proceso de alto nivel - Talleres.md`](<Proceso de alto nivel - Talleres.md>).

<!-- -->

> [!note] Diferencias clave respecto a EVT (Hipólito)
> El registro de propuestas de Elvira **no es idéntico** al de Hipólito, aunque el ciclo de
> dictamen ya es el mismo:
>
> | Aspecto | EVT (Hipólito) | TAL (Elvira) |
> | --- | --- | --- |
> | Público objetivo | General (literario / académico) | Infancias y juventudes, por nivel escolar |
> | Tipos de actividad | Conversatorio, Conferencia, Presentación de libro/revista, etc. | Taller, Cuentacuentos, Plática para jóvenes, Presentación de libros para niños/jóvenes, Obra/Presentación teatral, Proyección en cines |
> | Categorización | `literaria` / `academica` × `uady` / `externo` | Ninguna |
> | Duración | Variable (bloques estándar) | Fija, 45–50 min |
> | Modalidad | Presencial | Presencial o virtual |
> | Adjuntos | PDF/imágenes obligatorios | Sin adjuntos (texto/selección) |
> | Revisión de propuestas | Dictamen por propuesta: aceptar / solicitar cambios / rechazar | **Igual** (corrección 2026-06-29) |
> | Constancia | Opcional, declarada por el proponente | **Obligatoria**: el tallerista siempre declara participantes que la recibirán |
> | Volumen de selección | — | ~250 de ~300 propuestas aceptadas ([Junta 2 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#administración-de-salas-y-talleres>)) |

## Ajustes de homologación (2026-06-29)

- **Se agrega la sección de Herramientas de Administración (hoy sección D)**, antes inexistente: CU-TAL-007 a 010, espejo de CU-EVT-007 a 010. Motivo: corrección directa del cliente sobre el proceso real de Elvira.
- **CU-TAL-001** ya no crea "espacios disponibles con nombre y cupo": duplicaba el catálogo único global de `SAL`. Ahora solo configura fechas y modalidades.
- **CU-TAL-002** ya no afirma "sin dictamen"; su estado inicial pasa de `registrada` a `pendiente`, para alinear vocabulario con `EVT`.
- **CU-TAL-003** se renombra de "Editar... mientras la convocatoria esté abierta" (edición libre) a **"Editar una propuesta en respuesta a una solicitud de cambios del administrador"**, espejo exacto de CU-EVT-003.
- **CU-TAL-004**: se corrige la cifra "~50 de ~300" (sin respaldo) a **"~250 de ~300"** ([Junta 2 con organizadores FILEY](<../../soporte/meetings/resumenes/RSM - Junta 2 con organizadores FILEY.md#administración-de-salas-y-talleres>)); se agregan los estados de dictamen que antes se negaban.
- **Se agrega CU-TAL-005 (Cierre y Constancias, hoy sección B)**: fundamentado en que CU-TAL-002 ya capturaba un campo obligatorio de participantes que reciben constancia.
- **"Visualizar el número de propuestas por estado"** (antiguo CU-TAL-010) se **absorbe en CU-TAL-007** (Consultar la lista de propuestas): la lista muestra directamente el total encontrado desglosado por estado; no se justifica un CU aparte. Era tentativo desde el inicio, sin evidencia directa de necesidad de Elvira.
- **"Registrar la solicitud de visita de una escuela o grupo de excursionistas" (antiguo CU-TAL-007)** sigue **fuera de `TAL`**: la Junta 3 homologó las visitas escolares como dominio propio `VIS` (ver `VIS/CU-VIS Índice.md`, CU-VIS-001). El archivo y su modelo de datos asociado se eliminaron del repositorio (2026-06-29); la numeración activa de `TAL` no reutiliza ese número.
- **"Consultar y actualizar el registro de una visita escolar" (antiguo CU-TAL-008)** se descarta por el mismo motivo.
- **RF-TAL-01 a RF-TAL-04**: eran plantillas sin contenido; se eliminaron del repositorio (2026-06-29).
- La numeración de CUs es solo de conteo y no se reutiliza ni se recorre tras estas fusiones/bajas.

## Pendientes

- **Volumen y cadencia de revisión:** ¿Elvira revisa conforme llegan las propuestas (como Hipólito) o hasta el cierre de la convocatoria? Sigue abierto, ver `docs/soporte/meetings/meeting notes/Preguntas para la siguiente sesion.md`.
- **Notificación en lote vs. caso por caso:** CU-TAL-010 extrapola por simetría con `EVT`; no hay evidencia directa de que Elvira notifique en lote.
- **Ventana de edición post-aceptación:** ¿existe, además de CU-TAL-004 (respuesta a cambios solicitados), una ventana en la que el tallerista edite su actividad ya aceptada (como sugiere la Junta 2 con organizadores FILEY para "registrantes aceptados")? Ninguno de los dos dominios (`EVT` ni `TAL`) tiene hoy un CU dedicado a esto.
- **Mecanismo de "horario final":** confirmado que `VIS` solo consume catálogo final, nunca preliminar (ver nota arriba), pero no está definido cómo una Programación de `PRG` pasa de preliminar a final.
- **Fecha de habilitación de constancias (CU-TAL-005):** no se ha confirmado una fecha análoga al 26 de abril de `EVT`.

## Artefactos relacionados

- [`Modelo de datos - Talleres.md`](<Modelo de datos - Talleres.md>) — entidades y datos que el sistema almacena (vigente).
- [`Proceso de alto nivel - Talleres.md`](<Proceso de alto nivel - Talleres.md>) — diagrama del flujo de punta a punta.
- [`EVT/CU-EVT Índice.md`](<../EVT/CU-EVT Índice.md>) — convocatoria del programa general (Hipólito), de referencia estructural.
- [`REG/CU-REG Índice.md`](<../REG/CU-REG Índice.md>) — alta de cuenta y autenticación de talleristas.
- [`PRG/CU-PRG Índice.md`](<../PRG/CU-PRG Índice.md>) — programación (sala, fecha, horario) de las propuestas aceptadas.
- [`VIS/CU-VIS Índice.md`](<../VIS/CU-VIS Índice.md>) — visitas escolares (dominio propio, no de `TAL`), que consumen el catálogo final de talleres.
