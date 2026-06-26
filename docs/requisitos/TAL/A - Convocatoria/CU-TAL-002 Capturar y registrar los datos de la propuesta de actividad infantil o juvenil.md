---
estado: propuesta
version: 0.1
tags:
  - requisitos
  - caso-de-uso
  - talleres
fecha: 2026-06-25
id: CU-TAL-002
dominio: TAL
reglas_de_negocio: []
---
# CU-TAL-002 Capturar y registrar los datos de la propuesta de actividad infantil o juvenil

> Borrador inicial (título y descripción). Cubre el **llenado** del formulario; el **envío**
> se describe en CU-TAL-003. Equivale a CU-EVT-002 pero con los campos propios de la
> convocatoria infantil/juvenil, que difieren de los del programa general (Hipólito).

## Objetivo

El tallerista captura en el formulario de registro todos los datos de su propuesta de actividad dirigida a infancias y juventudes —datos del responsable, datos del evento, datos de la presentación y público meta—, dejándolos completos y validados, listos para ser enviados y registrados (CU-TAL-003).

## Alcance

Módulo de Talleres (TAL) — formulario de registro (llenado) de propuesta infantil/juvenil. El tallerista debe estar autenticado (CU-REG-002). Cubre la captura y la validación local de los datos. No cubre el envío del registro (CU-TAL-003), la edición posterior (CU-TAL-005), ni el registro de visitas escolares (CU-TAL-007).

## Actores

### Actor principal

- Tallerista (persona o institución que propone una actividad infantil/juvenil)

## Disparador

El tallerista, tras iniciar sesión y elegir la convocatoria de actividades infantiles/juveniles, abre el formulario de registro de propuesta.

## Notas / diferencias respecto a EVT (campos del formulario)

A diferencia de CU-EVT-002, el formulario de esta convocatoria captura:

- **Datos del responsable del evento:** nombre completo, número de contacto, correo electrónico (enlace con la FILEY).
- **Datos del evento:** nombre oficial del evento, organizado por, nombre completo de los participantes (reciben constancia), procedencia (Local / Nacional / Internacional), tema, pequeña reseña, y **tipo de evento** (Taller, Cuentacuento, Plática para jóvenes, Presentación de libros para niños/jóvenes, Obra/Presentación teatral, Proyección en cines).
- **Datos de la presentación:** autor/autora/autores, nombre de quien presenta/participa, editorial.
- **Público meta (varias casillas):** Preescolar, Primaria baja, Primaria alta, Secundaria, Preparatoria.
- **Observaciones:** sugerencia de día y turno (matutino / vespertino), observaciones generales.

Diferencias clave: la actividad tiene **duración fija (45–50 min)**, admite **modalidad presencial o virtual**, el público se segmenta por **nivel escolar** (no por categoría literaria/académica) y **no se suben archivos adjuntos** (todos los campos son de texto/selección).
