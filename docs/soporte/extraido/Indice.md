---
tags:
  - tipo/indice
tipo: indice
descripcion: Mapa de navegación entre los documentos extraídos a texto plano y sus archivos fuente originales.
generado_el: 2026-06-24
fuente_originales: "docs/soporte/documentos proporcionados por FILEY/"
---
# Índice de documentos extraídos

Esta carpeta contiene **versiones en texto plano** (Markdown y CSV) de los documentos
que FILEY entregó en `../documentos proporcionados por FILEY/` (formatos de oficina y PDF).
Sirven para lectura humana, búsqueda, *diff* en git y consumo por IA — que lee Markdown/CSV
de forma nativa pero no abre `.xlsx`/`.docx`.

> La **fuente autoritativa** siempre es el archivo original en
> `../documentos proporcionados por FILEY/`. Estos extractos pueden perder formato
> (tablas complejas, imágenes, celdas combinadas). Cada `.md` lleva en su *frontmatter*
> la ruta de su documento fuente.

## Convenciones

- La estructura de `extraido/` **espeja** la de la carpeta fuente.
- **PDF / DOCX de texto → `.md`** (un archivo por documento, con metadata de fuente).
- **XLSX → carpeta con el nombre del libro**, y dentro **un `.csv` por hoja**
  (`<libro>.<Hoja>.csv`), para no saturar las carpetas raíz.
- **PDF imagen/escaneado → no extraíble** (requiere OCR, fuera del alcance). Se consulta el original.

## Documentos en texto plano (`.md`)

> `FILEY/` = `../documentos proporcionados por FILEY/` · `Material…` = `Material para Registro de Actividades FILEY 2027/`.

| Extraído                                                                                                                                                                    | Fuente original                                                | Tipo                                                   |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------ |
| [MUESTRA TALLERES Supermicrobios.md](MUESTRA%20TALLERES%20Supermicrobios.md)                                                                                                | `FILEY/MUESTRA TALLERES  Supermicrobios.pdf`                   | PDF texto                                              |
| [Software para agendar escuelas.md](Software%20para%20agendar%20escuelas.md)                                                                                                | `FILEY/Software para agendar escuelas.docx`                    | DOCX                                                   |
| [Material…/Convocatoria Expositores 2026.md](Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Convocatoria%20Expositores%202026.md)                             | `FILEY/Material…/Convocatoria Expositores 2026.pdf`            | PDF texto                                              |
| [Material…/Convocatoria para Actividades FILEY 2027.md](Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Convocatoria%20para%20Actividades%20FILEY%202027.md)   | `FILEY/Material…/Convocatoria para Actividades FILEY 2027.pdf` | PDF texto                                              |
| [Material…/Detalles para el Registro en Linea 2027.md](Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Detalles%20para%20el%20Registro%20en%20Linea%202027.md) | `FILEY/Material…/Detalles para el Registro en Linea 2027.pdf`  | PDF texto                                              |
| [Material…/Programa General FILEY 2026.md](Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Programa%20General%20FILEY%202026.md)                               | `FILEY/Material…/Programa General FILEY 2026.pdf`              | PDF texto (programa impreso, extenso)                  |
| [Material…/Registro de propuestas FILEY 2027.md](Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Registro%20de%20propuestas%20FILEY%202027.md)                 | `FILEY/Material…/Registro de propuestas FILEY 2027.pdf`        | PDF texto (formulario modelo, **versión actualizada**) |

## Hojas de cálculo (`.xlsx` → CSV por hoja)

### ACTIVIDADES ARTES VISUALES 2026

Fuente: `FILEY/ACTIVIDADES ARTES VISUALES 2026.xlsx` — Carpeta: [ACTIVIDADES ARTES VISUALES 2026/](ACTIVIDADES%20ARTES%20VISUALES%202026/)

| CSV (hoja)   | Contenido                                                                                                                                                                                |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `…Hoja1.csv` | Catálogo de actividades de Artes Visuales (sede, fecha, institución, título, disciplina, obras, especialidad, participantes). Incluye bloques *Virtuales* y *Presenciales*. ~1.2k filas. |
| `…Hoja2.csv` | Hoja secundaria del mismo libro.                                                                                                                                                         |

### Base Registro de Propuestas FILEY 2027

Fuente: `FILEY/Material…/Base Registro de Propuestas FILEY 2027.xlsx` — Carpeta: [Base Registro de Propuestas FILEY 2027/](Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Base%20Registro%20de%20Propuestas%20FILEY%202027/)

Este libro es el **modelo de base de datos del registro de propuestas** (Contenidos). Una hoja por categoría:

| CSV (hoja)                    | Contenido                                                                                                                                                                                                |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `…Actividades Literarias.csv` | Registro de propuestas literarias (no-UADY). Columnas: ID, fecha, contacto, cargo, institución, correo, celular, tipo de actividad, nombre, organiza, local/nacional, estatus, fecha/hora/sala asignada. |
| `…Literarias UADY.csv`        | Igual, para propuestas literarias de la UADY.                                                                                                                                                            |
| `…Actividades Académicas.csv` | Propuestas académicas (no-UADY).                                                                                                                                                                         |
| `…Académicas UADY.csv`        | Propuestas académicas de la UADY.                                                                                                                                                                        |
| `…Conteo.csv`                 | Tablero de conteo: propuestas por tipo de actividad y por facultad/dependencia.                                                                                                                          |

### Programación General FILEY 2027

Fuente: `FILEY/Material…/Programación General FILEY 2027.xlsx` — Carpeta: [Programación General FILEY 2027/](Material%20para%20Registro%20de%20Actividades%20FILEY%202027/Programaci%C3%B3n%20General%20FILEY%202027/)

**Programa maestro (calendario)**: una hoja por sala/salón, con la grilla `Horario × Día` (sábado 13 a domingo 21). Modelo 2027 con contenidos 2026 de muestra.

| CSV (hoja)                        | Espacio                    |
| --------------------------------- | -------------------------- |
| `…Salón Uxmal 3.csv`              | Salón Uxmal 3              |
| `…Salón Uxmal 4.csv`              | Salón Uxmal 4              |
| `…Salón Dzibilchaltún.csv`        | Salón Dzibilchaltún        |
| `…Sala Fernando del Paso.csv`     | Sala Fernando del Paso     |
| `…Sala Fernando Espejo.csv`       | Sala Fernando Espejo       |
| `…Sala Antonia Jiménez Trava.csv` | Sala Antonia Jiménez Trava |

### Registro de actividades infantiles y juveniles - FILEY 2027

Fuente: `FILEY/Registro de actividades infantiles y juveniles - FILEY 2027.xlsx` — Carpeta: [Registro de actividades infantiles y juveniles - FILEY 2027/](Registro%20de%20actividades%20infantiles%20y%20juveniles%20-%20FILEY%202027/)

Respuestas de un Google Form para el registro de propuestas de actividades infantiles/juveniles (folio, contacto, datos del evento, presentación de libros, programación sugerida, logística). Llegó el 2026-06-23; al momento de la extracción no tiene filas de datos, solo encabezados.

| CSV (hoja)                              | Contenido                                                                      |
| --------------------------------------- | ------------------------------------------------------------------------------ |
| `…Respuestas de formulario 1.csv`       | Encabezados del formulario de registro (sin respuestas capturadas aún).        |
| `…DO NOT DELETE - AutoCrat Job Se….csv` | Configuración interna del add-on AutoCrat (mail merge); no es dato de negocio. |

### Horario-programación actividades infantiles y juveniles - FILEY 2027

Fuente: `FILEY/Horario-programación actividades infantiles y juveniles - FILEY 2027.xlsx` — Carpeta: [Horario-programación actividades infantiles y juveniles - FILEY 2027/](Horario-programaci%C3%B3n%20actividades%20infantiles%20y%20juveniles%20-%20FILEY%202027/)

Grilla `Horario × Sala` por día (sábado 13 a domingo 21), exclusiva de la sección infantil/juvenil: Sala 1–6, Sala cine 1–2, Espacio lúdico y Virtual. Llegó el 2026-06-23; plantilla vacía (sin contenidos asignados aún), análoga a la de `Programación General FILEY 2027` pero para este público.

| CSV (hoja) | Contenido                                           |
| ---------- | --------------------------------------------------- |
| `…csv`     | Única hoja del libro (mismo nombre que el archivo). |

## No extraíbles (PDF imagen — requieren OCR)

Estos se quedan **solo como PDF original**; consúltalos directamente:

| Documento (fuente)                                         | Por qué                                           |
| ---------------------------------------------------------- | ------------------------------------------------- |
| `FILEY/Información general talleres FILEY.pdf`             | PDF de imagen (sin capa de texto).                |
| `FILEY/Material…/Plano FILEY 2026 Salón Chichén Itzá.pdf`  | Plano/mapa del showfloor; es un dibujo, no texto. |
| `FILEY/Material…/Registro-para-Expositores-FILEY-2026.pdf` | Ficha de registro escaneada (imagen).             |

## Otros

- `FILEY/motivo de entrega.md` — correo de entrega de FILEY. **Ya es texto plano**; no se duplica aquí, se consulta en la carpeta fuente.
- [Analisis de archivos proporcionados.md](Analisis%20de%20archivos%20proporcionados.md) — análisis de qué pide cada documento y su contraste con lo documentado (juntas y casos de uso).
