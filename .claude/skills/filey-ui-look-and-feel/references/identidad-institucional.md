# Identidad institucional real — FILEY / UADY

Curado una sola vez a partir del CSS/HTML servido en producción de los 3 sitios (no de descripciones genéricas). **Última revisión: 2026-06-29.** Si el usuario reporta que algún sitio cambió de diseño, vuelve a inspeccionar su CSS antes de confiar en este archivo.

## Cómo se extrajo

- `filey.org`: WordPress + tema Flatsome. Colores leídos de los hex repetidos en el HTML/CSS servido.
- `uady.mx` y `matematicas.uady.mx`: ambos sirven **el mismo bundle Angular** (`styles.<hash>.css` idéntico byte a byte), es decir, comparten una plataforma institucional única — lo que encuentres en uno aplica al otro.

## Colores oficiales confirmados

| Marca | Azul | Dorado | Fuente del dato |
|---|---|---|---|
| **FILEY** (filey.org) | `#01457C` | `#C99213` | hex dominante en el HTML/CSS servido (30+ apariciones cada uno) |
| **UADY** (uady.mx / matematicas.uady.mx) | `#002e5f` | `#c79316` | clases explícitas `.uady-azul` / `.uady-dorado` en el CSS del bundle Angular |

**Hallazgo clave:** el azul y dorado de FILEY (`#01457C` / `#C99213`) son **exactamente** los que ya usa `prototipo/REG - EVT/styles.css` como `--azul-institucional` y `--dorado-encabezado`. El azul oscuro de UADY (`#002e5f`) es casi idéntico al `--azul-900` (`#00254d`) que el prototipo usa para fondos profundos/degradados. Es decir: **el prototipo REG-EVT ya está bien alineado con la marca real** — no hay que corregir su paleta, solo respetarla como fuente de verdad (ver tabla de tokens del prototipo en `styles.css`).

No se reutilicen los demás colores que aparecen en filey.org (`#ff6900`, `#0693e3`, `#9b51e0`, etc.) — son la paleta default de bloques de WordPress/Gutenberg, no colores de marca.

## Tipografía

- **filey.org:** "Open Sans", sans-serif (tema Flatsome).
- **uady.mx / matematicas.uady.mx:** Roboto, "Helvetica Neue", sans-serif (Angular Material default).
- **prototipo/REG - EVT:** "Segoe UI", "Helvetica Neue", Arial, system-ui, sans-serif (fuente de sistema, sin carga de webfont — deliberado para un prototipo estático sin dependencias externas).

No hay un único webfont institucional confirmado entre los 3 sitios (cada plataforma usa la suya). Para el prototipo HTML, **no agregues una carga de Google Fonts** solo por "fidelidad" — el prototipo es intencionalmente sin dependencias de red; si el cliente pide igualar tipografía exacta, es una decisión a confirmar con el usuario, no algo que este skill deba decidir solo.

## Layout / componentes observados en los sitios reales

- **filey.org:** hero banner grande, navegación horizontal con logo a la izquierda + dropdowns de submenú + iconos de redes sociales en el header, contenido en **cards con foto/imagen y texto superpuesto** (overlay), estilo editorial — distinto a las `.conv-card` del prototipo, que usan banner de color sólido/degradado + ícono, sin fotografía. Footer minimalista con contacto + links a políticas + redes sociales repetidas.
- **uady.mx / matematicas.uady.mx:** plataforma Angular Material — no se pudo inspeccionar el layout renderizado (es una SPA, el HTML inicial es solo el shell vacío, el layout se arma con JS en el navegador y no hay tool de navegador headless disponible aquí). Solo se confirmaron tokens de tema (Angular Material + clases `.uady-azul`/`.uady-dorado`), no componentes reales.

## Qué NO está verificado (no asumir, no inventar valores)

- **Forma exacta de botones de filey.org** (radio de borde, uso de mayúsculas, padding): el theme Flatsome genera esos valores vía Customizer en CSS dinámico que no se pudo aislar del bundle servido. Solo se confirmó el color de fondo (`#01457c`), no la forma. No copiar un radio/tipografía de botón "a ojo" atribuyéndoselo a filey.org.
- **Cualquier componente de uady.mx/matematicas.uady.mx** (botones, cards, headers reales) — solo se tienen los tokens de color/tipografía del bundle, no el layout renderizado.
- Por lo anterior, **los patrones específicos de app del prototipo (login mitad-flyer, bloques bento numerados, badges de estado, formularios dinámicos) no tienen contraparte verificable en los sitios oficiales** — son sitios de difusión/informativos, no aplicaciones autenticadas. No existe nada que "armonizar" ahí: son categorías de interfaz distintas. Conserva esos patrones tal como están en `REG - EVT/styles.css`.

## Cómo usar este archivo

Para nueva UI dentro de `prototipo/REG - EVT`: no copies layout de filey.org/uady.mx literalmente (son sitios institucionales generales, no la app de registro). Úsalo solo para **validar que un color o ajuste nuevo es coherente con la marca real** antes de añadirlo a `:root` en `styles.css`. Si se necesita certeza sobre botones/layout no verificados arriba, hay que inspeccionar el sitio con un navegador (capturas o devtools), no asumir desde este documento.
