---
estado: aceptado
version: 0.2
tags:
  - requisitos
  - caso-de-uso
  - eventos
fecha: 2026-06-25
id: CU-EVT-002
dominio: EVT
reglas_de_negocio: []
---
# CU-EVT-002 Registro de la propuesta de la actividad

> Este caso de uso cubre el **llenado** del formulario (captura y validación de los datos).
> El **envío** —la acción de mandar la propuesta a revisión— se describe en CU-EVT-002.1.

## Objetivo

El aplicante captura en el formulario de registro todos los datos de su propuesta de actividad para el programa de FILEY —datos de contacto y perfil, información de la actividad según su tipo y los archivos adjuntos requeridos—, dejándolos completos y validados, listos para ser enviados a la cola de revisión (CU-EVT-002.1).

## Alcance

Módulo EVE — formulario de registro (llenado) de propuesta. El aplicante debe estar autenticado (CU-REG-002). Cubre la captura y la validación local de los datos del formulario. No cubre el envío y el alta del registro `Propuesta` (CU-EVT-002.1), ni la edición de una propuesta ya enviada (CU-EVT-004).

## Actores

### Actor principal

- Aplicante (proponente externo o UADY)

## Disparador

El aplicante decide participar en el programa de FILEY y abre el formulario de registro de propuesta.

## Precondiciones

- El aplicante tiene sesión iniciada.
- La convocatoria está en estado `abierta` (fecha actual dentro del periodo configurado en `ParametrosConvocatoria`).

## Postcondiciones

### En éxito

- El formulario queda con todos los campos obligatorios completos y los adjuntos requeridos cargados, validados y listos para enviar.
- Aún **no** se crea el registro `Propuesta`; la creación ocurre al enviar (CU-EVT-002.1).
- al hacer envio se crea un registro `Propuesta` en estado `pendiente`, con folio asignado, vinculado al proponente y a la edición activa.
- El campo `categoria` queda con el sufijo `_uady` o `_externo` derivado automáticamente por el sistema; el prefijo (`literaria` / `academica`) permanece pendiente hasta el dictamen del administrador (CU-EVT-008).
- Los archivos adjuntos quedan almacenados como registros `PropuestaAdjunto`.
- El aplicante recibe por correo la confirmación de envío con su número de folio.

### En fallo

- El sistema conserva los datos capturados en el formulario para que el aplicante corrija y continúe.
- al hacer envio no se crea ningún registro. El sistema devuelve al aplicante al formulario (CU-EVT-002) conservando los datos para corregir y reintentar.

## Flujo principal

1. El aplicante abre el formulario de registro de propuesta.
2. El sistema precarga los datos de contacto del proponente (nombre completo, correo, teléfono) desde su perfil `Persona` / `Proponente`.
3. El aplicante completa los datos de perfil restantes: dependencia o institución (obligatorio), cargo (opcional) y ciudad/estado (obligatorio).
4. El aplicante selecciona el tipo de actividad del catálogo.
5. El sistema presenta los campos específicos del tipo seleccionado (ver sección Datos relevantes).
6. El aplicante completa los campos obligatorios, declara si requiere constancia de participación y adjunta los archivos requeridos.
7. El sistema valida en línea que los campos obligatorios y los adjuntos requeridos del tipo seleccionado estén completos, dejando el formulario listo para el envío.
8. El aplicante envía la propuesta. (precondiccion: Los datos de la propuesta están capturados y validados )
9. El sistema realiza la validación final de que todos los campos obligatorios y adjuntos requeridos estén completos.
10. El sistema deriva el sufijo de `categoria`: `_uady` si `tipo_participante = uady`, `_externo` en cualquier otro caso.
11. El sistema registra la `Propuesta` en estado `pendiente` con su folio y fecha de envío.
12. El sistema almacena cada archivo adjunto como un registro `PropuestaAdjunto`.
13. El sistema envía al aplicante un correo con el número de folio y la confirmación de recepción.
14. El sistema presenta las opciones "Crear una nueva solicitud" (CU-EVT-003) y "Cerrar".

## Flujos alternos

### A1. Tipo de actividad es "Presentación de libro" o "Presentación de revista"

1. En el paso 5, el sistema presenta adicionalmente los campos específicos de publicación: título de la publicación, rol del proponente, nombres de autores o editores, editorial, sinopsis extendida (800 palabras), fotografía del autor y portada.
2. El sistema muestra la instrucción de que el aplicante debe enviar también un ejemplar físico a las oficinas de FILEY.
3. El flujo continúa en el paso 6.

## Flujos de excepción

### E1. Campos obligatorios o adjuntos faltantes

1. En el paso 7, el sistema detecta campos obligatorios sin completar o adjuntos ausentes.
2. El sistema resalta cada campo en error con un mensaje descriptivo.
3. El formulario no queda listo para enviar hasta que el aplicante corrija.

### E1. Convocatoria cerrada al momento del envío

1. En el paso 9, el sistema verifica que la fecha actual es posterior a `fecha_cierre_convocatoria`.
2. El sistema informa al aplicante que la convocatoria ya cerró y no acepta el envío.
3. No se crea ningún registro.

### E2. Campos obligatorios o adjuntos faltantes en la validación final

1. En el paso 9, el sistema detecta campos obligatorios sin completar o adjuntos ausentes.
2. El sistema devuelve al aplicante al formulario resaltando lo que falta.
3. El envío no procede hasta que el aplicante corrija y reintente.

## Datos relevantes

### Entradas

Campos comunes a todos los tipos de actividad:

- Tipo de actividad (selección del catálogo) — obligatorio.
- Título de la actividad — obligatorio.
- Organiza — obligatorio.
- Público al que va dirigido (selección múltiple: Público en general · Académico · Estudiantil · Infantil · Familias; mínimo una opción) — obligatorio.
- ¿Requiere constancia de participación? (sí / no) — obligatorio.
- Semblanzas de los participantes en PDF (máx. 500 palabras c/u) — obligatorio.
- Sinopsis de la actividad en PDF (máx. 500 palabras) — obligatorio.
- Moderador/a — opcional.
- Comentarios u observaciones — opcional.

Campos adicionales por tipo de actividad:

- **Conversatorio / Mesa redonda:** nombre de los participantes (máx. 3) — obligatorio.
- **Conferencia / Charla / Lectura de obra / Encuentro:** nombre de quien imparte (máx. 2) — obligatorio.
- **Presentación de libro:** título de la publicación, rol del proponente (Autor/a, Editor/a, Antologador/a, Compilador/a, Coordinador/a), nombres igual a la portada (máx. 5), si el autor participará, nombres de autores presentes en caso de que no todos asistan (condicional), presentadores (máx. 2, opcional), editorial, sinopsis del libro en PDF (máx. 800 palabras), fotografía del autor en alta resolución (JPG/PNG) y portada del libro (JPG/PDF) — todos obligatorios salvo donde se indica.
- **Presentación de revista:** título de la publicación, nombre del editor/a (máx. 2), si el editor participará, nombres de editores presentes en caso de que no todos asistan (condicional), presentadores (máx. 2, opcional), sinopsis de la revista en PDF (máx. 800 palabras) y portada de la revista (JPG/PDF) — todos obligatorios salvo donde se indica.

### Salidas

- Formulario completo y validado (sin persistir aún), listo para el envío en CU-EVT-002.1.
