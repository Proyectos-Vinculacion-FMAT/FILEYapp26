---
estado: propuesta
version: 0.2
fecha_actualizacion: 2026-09-03
tags:
  - tipo/caso-de-uso
  - dom/evt
fecha: 2026-06-24
id: CU-EVT-009
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-009 Dictaminar una propuesta

> [!note] Construido el 2026-09-03 — `filey/apps/eventos/servicios/dictamen.py`
> El flujo de este documento se implementó tal cual, con dos precisiones que se descubrieron al
> construirlo y que su redacción daba por otra cosa:
>
> - **El dictamen son columnas de `Solicitud`, no una tabla aparte.** El modelo de datos §3.1
>   describe `DetallesAdminSolicitud` como una relación uno a uno **obligatoria y creada al
>   enviarse la solicitud**, que es la definición de una columna con un `JOIN` de más. La
>   desviación está argumentada en el propio documento. Si `TAL` acaba siendo una convocatoria
>   `EVT` con otros criterios de revisión, esto tendrá que desacoplarse: la pregunta está
>   abierta en `ADR-0011`.
> - **Aceptar no crea ninguna `Actividad`.** Ya existe desde el envío: es la tabla padre de las
>   ocho de tipo, con herencia multitabla (`ADR-0009`). Lo que el paso 6 llama «crear una
>   `Actividad` en estado `sin_horario`» corresponde a `SolicitudesAprobadas` (§3.2), que sí
>   nace al aceptar, y a la ausencia de filas en `ProgramacionActividad` (§3.3) — «sin horario»
>   es un estado **derivado**, no una columna.
>
> Los dos textos del dictamen se leen desde el otro lado: `CU-EVT-003` paso 4 los enseña a
> quien propuso.

## Objetivo

El administrador resuelve una propuesta emitiendo uno de tres dictámenes —aceptar, solicitar cambios o rechazar— dejando registro de la decisión para que el proceso avance hacia la programación o la notificación de resultados.

## Alcance

Módulo EVT — dictamen de propuesta. Absorbe el rechazo con motivo (flujo alterno A2) y el cambio de dictamen ya emitido (flujo alterno A3). La notificación de aceptaciones y rechazos al proponente se realiza en lote (CU-EVT-010); la solicitud de cambios sí se notifica de inmediato. No cubre la asignación de sala y horario, delegada por completo a `PRG` (ver `PRG/CU-PRG Índice.md`).

## Actores

### Actor principal

- Administrador (Hipólito)

## Disparador

Desde el detalle de una propuesta (CU-EVT-008), el administrador decide emitir su dictamen.

## Precondiciones

- El administrador tiene sesión iniciada con permisos del módulo EVT.
- La propuesta está en estado `pendiente` (o `cambios_solicitados`, si el proponente aún no responde y el administrador decide resolverla directamente).

## Postcondiciones

### En éxito

- La propuesta queda en estado `aceptada`, `cambios_solicitados` o `rechazada`, con su fecha de revisión y el administrador que la revisó (`revisado_por`).
- Si fue **aceptada**: el sistema registra su `categoria` (`literaria` / `academica`) y la procedencia confirmada, y la deja pendiente de notificación en lote (`resultado_notificado = false`). Queda **sin horario**, que no es un estado almacenado sino la ausencia de filas en `ProgramacionActividad` — ver la corrección del flujo principal.
- Si fue **cambios solicitados**: se registra el `mensaje_cambios_solicitados` y el sistema notifica de inmediato al proponente por correo.
- Si fue **rechazada**: se registra el `motivo_rechazo` y la propuesta queda pendiente de notificación en lote (`resultado_notificado = false`).

### En fallo

- La propuesta permanece sin cambios en su estado actual.

## Flujo principal (Aceptar)

1. En el detalle de la propuesta, el administrador elige "Aceptar".
2. El sistema presenta una segunda pantalla de confirmación que solicita clasificar la propuesta como `literaria` o `academica`, sugiriendo una opción a partir de la dependencia o institución del proponente.
3. El administrador confirma la clasificación y la aceptación.
4. El sistema registra la clasificación elegida (`literaria` / `academica`) **y** la procedencia que el administrador confirma o corrige (`is_participante_uady`). Son dos datos, no un valor compuesto: el conteo por categoría de `DetallesConvocatoria` agrupa por los dos por separado (`Modelo de datos - Eventos` §3.6), y una cadena `literaria_uady` no se puede agrupar por una de sus mitades sin partirla. La etiqueta que se lee en pantalla —«Literaria · UADY»— se compone al mostrar y no se almacena, igual que el folio.
5. El sistema cambia la propuesta a `aceptada`, registra la fecha de revisión y el revisor.
6. El sistema marca la propuesta como pendiente de notificación (`resultado_notificado = false`) para incluirla en el siguiente lote (CU-EVT-010).
7. El sistema confirma al administrador que la propuesta fue aceptada.

> [!warning] Corrección del 2026-09-03 — aceptar **no crea ninguna `Actividad`**
> Este flujo decía en su paso 6 que aceptar «crea una `Actividad` en estado `sin_horario`».
> Está escrito contra un modelo que `Modelo de datos - Eventos` §3.1 ya descartó: **no existe
> tal entidad**, porque duplicaría el estado de la solicitud y obligaría a mantener los dos
> sincronizados. «Sin horario» es un estado **derivado** — no hay filas en
> `ProgramacionActividad` (§3.3)—, no una columna.
>
> El nombre además ya está tomado y significa otra cosa: en `apps/eventos/models.py`,
> `Actividad` es el enrutador polimórfico que se crea al **enviar** la propuesta, uno por cada
> uno de los ocho tipos (`ADR-0009`).
>
> Lo que §3.2 sí pide crear al aceptar es `SolicitudesAprobadas`, cuya razón de ser es darle a
> `ProgramacionActividad` una clave foránea real hacia lo aprobado. Como `PRG` no está
> construido, hoy sería una tabla sin ningún consumidor cuyas dos columnas repiten
> `fecha_revision` y `revisado_por`: se crea cuando llegue quien la necesita.

## Flujos alternos

### A1. Solicitar cambios

1. En el detalle de la propuesta, el administrador elige "Solicitar cambios".
2. El sistema solicita el `mensaje_cambios_solicitados` (campo de texto obligatorio) indicando qué debe corregir el proponente.
3. El administrador redacta el mensaje y confirma.
4. El sistema cambia la propuesta a `cambios_solicitados` y registra la fecha de revisión y el revisor.
5. El sistema notifica de inmediato al proponente por correo, para que pueda corregir y reenviar (CU-EVT-004) antes del cierre de la convocatoria.
6. El administrador puede solicitar cambios cuantas veces sea necesario sobre la misma propuesta; él determina cuándo la información es suficiente.

### A2. Rechazar

1. En el detalle de la propuesta, el administrador elige "Rechazar".
2. El sistema solicita el `motivo_rechazo` (campo de texto obligatorio).
3. El administrador redacta el motivo y confirma.
4. El sistema cambia la propuesta a `rechazada`, registra la fecha de revisión y el revisor.
5. El sistema marca la propuesta como pendiente de notificación (`resultado_notificado = false`) para incluirla en el siguiente lote.

> [!note] Cómo «el sistema solicita el texto», resuelto el 2026-09-03
> El paso 2 de A1 y de A2 es una **ventana** que se abre al elegir la acción, como en el prototipo (`prototipo/EVT/administradores/admin-evt-detalle-propuesta.html`), y no un recuadro permanentemente abierto en el panel del dictamen.
>
> La razón es la frecuencia: el desenlace normal es aceptar, y un campo «qué debe corregir, o por qué se rechaza» siempre a la vista pone el caso excepcional delante del habitual y obliga a un solo texto a servir para dos cosas que no se escriben igual. Cada acción pregunta lo suyo, y solo cuando se eligió.
>
> **Se abre por dos caminos.** Con JavaScript la abre Alpine al pulsar el botón. Sin él, el botón envía el dictamen sin texto, el servicio lo rechaza por `E3` y la vista devuelve la pantalla con la ventana ya abierta y el aviso dentro. Se implementa en `apps/eventos/templates/eventos/parciales/modal_dictamen.html`, que lo explica.
>
> La clasificación de **aceptar** (paso 2 del flujo principal) no va en ventana: son dos opciones excluyentes que caben a la vista en el propio panel, y esconderlas detrás de un clic no confirma nada que no confirme ya el botón.

### A3. Cambiar un dictamen ya emitido (re-dictamen)

1. El administrador abre una propuesta cuyo dictamen ya fue emitido (`aceptada` o `rechazada`) y elige cambiarlo.
2. El sistema verifica que quien lo intenta es el **operador de la plataforma** —el superusuario, `ADR-0005`—; si no lo es, deniega la acción (ver E2).
3. El sistema solicita doble verificación de la acción.
4. Si el cambio pasa de `aceptada` a `rechazada`, el sistema exige obligatoriamente el `motivo_rechazo`.
5. El administrador confirma.
6. El sistema aplica el nuevo dictamen y, si la propuesta ya había sido notificada antes (`fecha_resultado_notificado` no nula), restablece `resultado_notificado = false` para que el cambio se comunique como **actualización** en el siguiente lote.
7. Si el cambio implica pasar de `aceptada` a otro estado, la propuesta deja de estar aprobada y por tanto deja de ser programable. No hay ninguna `Actividad` que marcar: ver la corrección del flujo principal. Cuando exista `PRG`, es aquí donde se liberan sus `ProgramacionActividad` (`Modelo de datos - Eventos` §3.2).

## Flujos de excepción

### E1. Cupo de la categoría alcanzado al aceptar

1. En el paso 4 (Aceptar), el sistema detecta que la categoría ya alcanzó su cupo configurado.
2. El sistema advierte al administrador del cupo alcanzado, pero **no bloquea** la aceptación (permite mantener propuestas en reserva ante posibles bajas).
3. El administrador decide confirmar o cancelar la aceptación.

> [!note] Todavía no construido (2026-09-03)
> El aviso necesita los cuatro `cupo_*` de `DetallesConvocatoria` (`Modelo de datos - Eventos`
> §3.6), y esos son de **CU-EVT-001** —configurar la convocatoria—, que no está construido: hoy
> `ConfiguracionConvocatoria` solo lleva el prefijo del folio. Se dejó fuera a sabiendas y no se
> pierde nada mientras tanto: el propio §3.6 dice que los cupos **no se consumen ni se hacen
> cumplir**, son una meta de planeación, y esta excepción explícitamente no bloquea la
> aceptación. Entra con `CU-EVT-001`.

### E2. Sin permiso para re-dictaminar

1. En el paso 2 de A3, el sistema detecta que quien lo intenta administra la feria pero **no es el operador de la plataforma**.
2. El sistema deniega la acción y muestra el dictamen vigente sin alterarlo, diciendo a quién corresponde pedírselo.

> [!note] Quién puede re-dictaminar, resuelto el 2026-09-03
> Este CU pedía «un permiso para re-dictaminar» sin decir cuál, y `ADR-0004` no define ningún
> nivel entre administrar una feria y ser su dueño. Se resolvió con el escalón que sí existe por
> encima de los dos: el **operador de la plataforma** (`ADR-0005`), que es el superusuario de
> Django. La razón es que un dictamen emitido pudo salir ya por correo, y corregirlo obliga a
> comunicar una rectificación a alguien que quizá ya organizó su viaje — no es la misma acción
> que emitirlo, y no debe estar al alcance del mismo reflejo.
>
> La comprobación vive en `servicios/dictamen.py` y no en la vista, para que un comando de
> `manage.py` se tope con ella igual que un POST.

### E3. Motivo o mensaje obligatorio faltante

1. Al solicitar cambios (A1) o rechazar (A2/A3), el administrador deja en blanco el campo de texto obligatorio.
2. El sistema impide registrar el dictamen y resalta el campo como obligatorio.
3. El administrador completa el texto y reintenta.

## Datos relevantes

### Entradas

- Identificador o folio de la propuesta.
- Decisión de dictamen (aceptar / solicitar cambios / rechazar).
- Clasificación `literaria` / `academica` (al aceptar).
- `mensaje_cambios_solicitados` (al solicitar cambios) o `motivo_rechazo` (al rechazar).

### Salidas

- Propuesta en estado `aceptada` (con `Actividad` creada en `sin_horario`), `cambios_solicitados` (con notificación inmediata) o `rechazada`.
- Fecha de revisión y revisor registrados.
