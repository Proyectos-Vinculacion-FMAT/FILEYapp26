---
estado: vigente
version: "1.0"
tags:
  - tipo/referencia
  - tema/trazabilidad
fecha: 2026-06-24
---
# Mapa de etiquetas (taxonomía del repositorio)

Vocabulario **controlado y facetado** que usan todos los `.md` de este repositorio en su
frontmatter (`tags:`). Su objetivo es que humanos e IAs puedan **navegar por temas** de forma
predecible, sin depender solo de las carpetas.

> [!important] Una etiqueta solo vale si **agrupa**
> Antes de inventar una etiqueta nueva, búscala aquí. Si no existe, **agrégala primero a este
> mapa** y luego úsala. No se crean etiquetas de un solo uso ad hoc: una etiqueta que aparece
> una sola vez no sirve para navegar.

## Cómo funciona: tres facetas con prefijo

Cada etiqueta pertenece a **una faceta**, identificada por su prefijo `faceta/valor`:

| Faceta | Responde a… | Cardinalidad | Ejemplo |
| ------ | ----------- | ------------ | ------- |
| `tipo/` | ¿Qué **es** el documento? | **exactamente 1** por archivo | `tipo/caso-de-uso` |
| `dom/`  | ¿A qué **dominio** pertenece? | 0 o más | `dom/std` |
| `tema/` | ¿De qué **trata** (transversal)? | 0 o más | `tema/pagos` |

Los prefijos hacen el espacio de etiquetas **autodescriptivo**: con ver `dom/` ya sabes que lo
que sigue es un código de dominio. En Obsidian las etiquetas anidadas se agrupan solas en el
panel de tags y en el grafo.

## Faceta `tipo/` — clase de documento (1 por archivo)

| Etiqueta | Significado | Dónde vive |
| -------- | ----------- | ---------- |
| `tipo/caso-de-uso` | Un caso de uso individual (`CU-DOM-NNN`) | `requisitos/DOM/**` |
| `tipo/indice` | Índice/portada que enlaza otros documentos | `CU-DOM Índice.md`, `Filey.md`, `extraido/Indice.md` |
| `tipo/plantilla` | Plantilla base para crear documentos | `CU-XX-NN Template.md` |
| `tipo/modelo-de-datos` | Modelo de datos de un dominio | `STD/Modelo de datos - Stands.md` |
| `tipo/proceso` | Proceso de alto nivel / flujo | `STD/Proceso de alto nivel - Stands.md` |
| `tipo/referencia` | Documento de referencia/alcance transversal | `requisitos/README.md`, este mapa |
| `tipo/junta-resumen` | Resumen (minuta) de una junta | `meetings/resumenes/RSM - *` |
| `tipo/junta-transcripcion` | Transcripción literal de una junta | `meetings/transcripciones/**/TRS - *` |
| `tipo/junta-notas` | Notas/preguntas preparatorias de junta | `meetings/meeting notes/*` |
| `tipo/documento-extraido` | Texto extraído automáticamente de un original (PDF/DOCX) | `soporte/extraido/**` |
| `tipo/analisis` | Análisis/contraste de fuentes | `extraido/Analisis de archivos proporcionados.md` |
| `tipo/nota` | Nota de trabajo o documento fuente suelto | `soporte/notas/*`, `documentos proporcionados.../*` |

## Faceta `dom/` — dominio del sistema (0 o más)

**Alineada 1:1 con los códigos del** [README de requisitos](<requisitos/README.md>). Esa es la
fuente de verdad de qué es cada dominio; aquí solo se listan los códigos como etiqueta.

| Etiqueta | Dominio | Estado |
| -------- | ------- | ------ |
| `dom/std` | Stands / Expositores | Documentado |
| `dom/prg` | Programa General | Documentado |
| `dom/sal` | Salas y salones | Documentado |
| `dom/vis` | Visitas escolares | Documentado |
| `dom/reg` | Registros / Convocatorias (core transversal) | Sin carpeta aún |
| `dom/evt` | Eventos | Sin carpeta aún |
| `dom/tal` | Talleres | Sin carpeta aún |
| `dom/pag` | Pagos | Futuro (reservado) |
| `dom/acc` | Acceso y verificación | Futuro (reservado) |
| `dom/cnt` | Contabilidad de visitantes (antes `VIS`) | Futuro (reservado) |
| `dom/rep` | Reportes | Futuro (reservado) |

> [!note] Regla de oro
> Si abres un dominio nuevo, su etiqueta `dom/xxx` debe ser **el mismo código** (en minúsculas)
> que el README. Nunca uses el nombre largo (`stands`, `programacion`) como etiqueta.

## Faceta `tema/` — temas transversales (lista cerrada)

Temas que cruzan varios dominios. **Lista cerrada**: para añadir uno nuevo, edítalo primero aquí.

| Etiqueta | Cubre |
| -------- | ----- |
| `tema/alcance` | Qué entra/no entra en la entrega; priorización |
| `tema/arquitectura` | Decisiones técnicas, cores, estructura del sistema |
| `tema/cliente` | Junta/material del lado del cliente (FILEY) |
| `tema/equipo-desarrollo` | Junta/material del lado del equipo de desarrollo |
| `tema/descubrimiento` | Fase de levantamiento/descubrimiento de necesidades |
| `tema/feedback` | Retroalimentación sobre lo documentado |
| `tema/pagos` | Cobros, abonos, métodos de pago |
| `tema/descuentos` | Descuentos (pronto pago, local, override) |
| `tema/facturacion` | Facturación |
| `tema/contabilidad` | Contabilidad |
| `tema/reservas` | Reserva de espacios/cupos |
| `tema/permisos` | Roles, identidad, control de acceso |
| `tema/formularios` | Formularios/convocatorias de captura |
| `tema/trazabilidad` | Bitácora, deslinde, registro de envíos |
| `tema/usuarios` | Tipos de usuario/participante |

## Cómo navegar

- **Obsidian:** clic en cualquier etiqueta, o búsqueda `tag:#dom/std`. Las anidadas se agrupan
  solas en el panel de Etiquetas y en el grafo por faceta.
- **Dataview** (si se usa): `LIST FROM #tipo/caso-de-uso AND #dom/vis`.
- **ripgrep / línea de comandos:**
  ```bash
  # Todos los casos de uso del dominio de visitas escolares
  rg -l "dom/vis" --glob "*.md" | rg -l "tipo/caso-de-uso"
  # Toda la evidencia (juntas + material) que tocó pagos
  rg -l "tema/pagos" --glob "*.md"
  ```
- **Para una IA:** los prefijos son estables. Para acotar contexto, filtra por `dom/<codigo>`
  (dominio) + `tipo/<clase>` (qué tipo de documento) antes de leer cuerpos.

## Convenciones

1. **Una** `tipo/` por archivo; tantas `dom/` y `tema/` como apliquen de verdad.
2. Etiquetas en **kebab-case** y sin acentos (`tema/facturacion`, no `facturación`).
3. `dom/` = código del [README](<requisitos/README.md>); `tema/` = esta lista cerrada.
4. La etiqueta describe el **contenido del documento**, no lo que el documento menciona de pasada.

Ver también: [Portada del repositorio](<../Filey.md>) · [README de requisitos](<requisitos/README.md>).
