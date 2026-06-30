---
estado: propuesta
version: 0.2
tags:
  - tipo/caso-de-uso
  - dom/tal
fecha: 2026-06-28
id: CU-TAL-002
dominio: TAL
reglas_de_negocio:
  - El folio y la fecha de envío los genera el sistema al crear el registro; el tallerista no los captura.
  - No existe categorización por tipo de participante (sin sufijo _uady / _externo); todas las propuestas se tratan igual.
  - No se suben archivos adjuntos; todos los campos son de texto o selección.
  - El tallerista debe registrar una propuesta por cada actividad que desee proponer.
---
# CU-TAL-002 Registro de los datos de la propuesta de actividad infantil o juvenil

> Integra el llenado del formulario y el envío de la propuesta (absorbe el antiguo "enviar
> la propuesta" como caso aparte). Equivale a CU-EVT-002 pero adaptado a la convocatoria
> infantil/juvenil de Elvira: sin adjuntos de archivo y con campos propios de este tipo de
> actividad.

<!-- -->

> [!warning] Corrección (2026-06-29) — Elvira sí dictamina en el sistema
> Una versión anterior de este CU asumía que la selección de Elvira era manual y fuera del
> sistema. **Corregido directamente por el cliente:** Elvira **sí** revisa cada propuesta en
> el sistema y dictamina aceptar, solicitar cambios o rechazar — el mismo ciclo que Hipólito
> en `EVT` (ver CU-TAL-009). Lo que sigue siendo distinto de `EVT` es solo lo que este CU no
> cubre: adjuntos de archivo y categorización cruzada.

## Objetivo

El tallerista captura en el formulario de registro todos los datos de su propuesta de actividad dirigida a infancias y juventudes —datos del responsable del evento, datos del evento, datos de la presentación y público meta— y la envía al sistema, que crea el registro con folio asignado y confirma la recepción por correo.

## Alcance

Módulo de Talleres (TAL) — formulario de registro y envío de propuesta infantil/juvenil. El tallerista debe estar autenticado (CU-REG-002). Cubre la captura, la validación local y el envío de la propuesta. No cubre la edición posterior (CU-TAL-003), el dictamen (CU-TAL-009) ni el registro de visitas escolares, que es responsabilidad del dominio `VIS` (ver `VIS/CU-VIS Índice.md`, CU-VIS-001). A diferencia de CU-EVT-002, no existe paso de categorización ni carga de archivos adjuntos.

## Actores

### Actor principal

- Tallerista (persona o institución que propone una actividad dirigida a infancias y juventudes)

## Disparador

El tallerista, tras iniciar sesión y elegir la convocatoria de actividades infantiles/juveniles, abre el formulario de registro de propuesta.

## Precondiciones

- El tallerista tiene sesión iniciada (CU-REG-002).
- La convocatoria de actividades infantiles/juveniles está en estado `abierta` (fecha actual dentro del periodo configurado en CU-TAL-001).

## Postcondiciones

### En éxito

- Se crea un registro `PropuestaTaller` en estado `pendiente`, con folio y fecha de envío asignados por el sistema.
- El tallerista recibe por correo la confirmación de recepción con su número de folio.
- La propuesta queda lista para que Elvira la revise y dictamine (CU-TAL-007 a CU-TAL-010).

### En fallo

- No se crea ningún registro. El sistema conserva los datos capturados en el formulario para que el tallerista corrija y reintente.

## Flujo principal

1. El tallerista abre el formulario de registro de propuesta infantil/juvenil.
2. El sistema precarga los datos del responsable (nombre completo, número de contacto, correo electrónico) desde su perfil `Persona`.
3. El tallerista revisa y completa los datos del responsable del evento si es necesario.
4. El tallerista captura los datos del evento: nombre oficial del evento, organizado por, nombre completo de los participantes que recibirán constancia, procedencia, tema, pequeña reseña, tipo de evento y modalidad.
5. El tallerista captura los datos de la presentación: autor(a)/autores, nombre de quien presenta/participa y editorial.
6. El tallerista selecciona el público meta por nivel escolar (mínimo uno).
7. El tallerista captura las observaciones: sugerencia de día y turno, y observaciones generales (ambos opcionales).
8. El sistema valida en línea que los campos obligatorios estén completos.
9. El tallerista pulsa "Enviar".
10. El sistema realiza la validación final de campos obligatorios.
11. El sistema verifica que la convocatoria siga en estado `abierta`.
12. El sistema crea el registro `PropuestaTaller` en estado `pendiente` con folio y fecha de envío.
13. El sistema envía al tallerista un correo con el número de folio y la confirmación de recepción.
14. El sistema muestra la confirmación con el folio asignado y las opciones "Registrar otra actividad" y "Cerrar".

## Flujos alternos

### A1. Modalidad virtual

1. En el paso 4, si el tallerista selecciona modalidad `Virtual`, el sistema presenta el campo de plataforma o enlace de videoconferencia (obligatorio).
2. El flujo continúa en el paso 5.

## Flujos de excepción

### E1. Campos obligatorios faltantes en la validación en línea

1. En el paso 8, el sistema detecta campos obligatorios sin completar.
2. El sistema resalta cada campo en error con un mensaje descriptivo.
3. El formulario no queda listo para enviar hasta que el tallerista corrija.

### E2. Convocatoria cerrada al momento del envío

1. En el paso 11, el sistema verifica que la fecha actual es posterior al cierre de la convocatoria.
2. El sistema informa al tallerista que la convocatoria ya cerró y no acepta el envío.
3. No se crea ningún registro.

### E3. Campos obligatorios faltantes en la validación final

1. En el paso 10, el sistema detecta campos obligatorios sin completar.
2. El sistema devuelve al tallerista al formulario resaltando lo que falta.
3. El envío no procede hasta que el tallerista corrija y reintente.

## Datos relevantes

### Entradas

**Datos del responsable del evento** (precargados desde el perfil `Persona`, editables):

- Nombre completo — obligatorio.
- Número de contacto — obligatorio.
- Correo electrónico (enlace con la FILEY) — obligatorio.

**Datos del evento:**

- Nombre oficial del evento — obligatorio.
- Organizado por — obligatorio.
- Nombre completo de los participantes que recibirán constancia — obligatorio.
- Procedencia (selección: Local · Nacional · Internacional) — obligatorio.
- Tema — obligatorio.
- Pequeña reseña — obligatorio.
- Tipo de evento (selección: Taller · Cuentacuento · Plática para jóvenes · Presentación de libros para niños/jóvenes · Obra/Presentación teatral · Proyección en cines) — obligatorio.
- Modalidad (selección: Presencial · Virtual) — obligatorio.
- Plataforma o enlace de videoconferencia — obligatorio solo si modalidad es `Virtual`.

**Datos de la presentación:**

- Autor/autora/autores — opcional.
- Nombre de quien presenta/participa — obligatorio.
- Editorial — opcional.

**Público meta** (mínimo una casilla seleccionada):

- Preescolar.
- Primaria baja.
- Primaria alta.
- Secundaria.
- Preparatoria.

**Observaciones:**

- Sugerencia de día y turno (selección: Matutino · Vespertino) — opcional.
- Observaciones generales — opcional.

### Salidas

- `PropuestaTaller` en estado `pendiente` con folio y fecha de envío.
- Correo de confirmación al tallerista.
