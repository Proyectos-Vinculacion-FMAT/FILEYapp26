# Derivar el mapa del showfloor desde el plano en PDF

`CU-STD-039` importa el showfloor de un JSON externo. Este directorio es lo que **produce** ese
JSON cuando lo único que hay es el plano en papel.

El plano de 2026 (`docs/soporte/documentos proporcionados por FILEY/Material para Registro de
Actividades FILEY 2027/Plano FILEY 2026 Salón Chichén Itzá.pdf`) es un PDF **hecho en
Photoshop**: una imagen, sin vectores ni capa de texto. `pdftotext` devuelve dos bytes. Así que
la geometría se mide sobre los píxeles y los números se leen mirando.

Resultado: [`filey/apps/stands/mapas/filey-2026.json`](../../filey/apps/stands/mapas/filey-2026.json)
— **151 espacios, 2 628 m² vendibles, retícula de 167 × 59 m**.

## Cómo se ejecuta

```bash
PLANO="docs/soporte/documentos proporcionados por FILEY/Material para Registro de Actividades FILEY 2027/Plano FILEY 2026 Salón Chichén Itzá.pdf"
pdftoppm -r 300 -singlefile "$PLANO" /tmp/plano300      # PPM crudo, fácil de leer sin dependencias
python scripts/derivar-mapa/1-formas.py   /tmp/plano300.ppm > /tmp/formas.json
python scripts/derivar-mapa/2-reticula.py /tmp/formas.json  > /tmp/celdas.json
python scripts/derivar-mapa/3-asignar.py  /tmp/celdas.json  filey/apps/stands/mapas/filey-2026.json
```

Los tres pasos no necesitan nada instalado: PPM se parsea a mano, precisamente para no meter
Pillow ni OpenCV como dependencia por un script que se corre una vez por edición.

| Paso | Qué hace | Qué puede salir mal |
| --- | --- | --- |
| `1-formas.py` | Máscara del azul institucional → componentes conexos → la **forma** de cada caja como lista de rectángulos. | Si el plano cambia de color, ajustar `AZUL`. |
| `2-reticula.py` | Píxeles → metros, agrupando por islote. | Avisa de cualquier solape; hoy son **cero**. |
| `3-asignar.py` | Le pone su número a cada forma y escribe el JSON. | Falla si la extracción y la tabla dejan de casar. |

## Las dos decisiones que sostienen todo

### 1. El stand tipo mide 3 × 2 m, y eso fija la escala

Es el único anclaje métrico que existe: **el plano no trae escala gráfica**. Viene del precio que
dio el cliente — «el básico 3×2 vale 15 000, que equivale a los 2 500 por metro cuadrado» — y
cuadra con lo medido: la caja pequeña del plano son 50 × 32 px, y su paso 54 × 36 px, o sea una
relación de 1.5 entre ancho y fondo. De ahí sale **18.05 px por metro a 300 dpi**, y con esa
escala *todas* las cajas del plano caen en múltiplos enteros de metro. Que 161 formas
independientes encajen a la vez es la comprobación de que la escala es la correcta.

> [!warning] Lo que **no** está verificado es el tamaño del salón
> Los 167 × 59 m salen de aplicar esa escala al dibujo entero, y los planos de feria suelen
> dibujar los stands más grandes de lo que tocaría para que se lean los números. Si el salón
> resulta ser más chico, lo que encoge son **los pasillos**, no los stands: la superficie de cada
> espacio —y por tanto su precio, que es `m² × costo_m2` (RN-01)— no depende del tamaño del
> recinto. Contrastar contra las medidas reales del Centro de Convenciones antes de publicar el
> mapa al público.

### 2. Los islotes se ajustan por separado

Dentro de un islote el dibujo es exacto. **Entre islotes no**: se dibujó en Photoshop y los
pasillos miden lo que se vio bien. Forzar una retícula global metía medio metro de error en cada
caja; ajustar cada islote por su cuenta y redondear solo su origen deja el error en el pasillo,
que es donde no importa — el ancho de un pasillo es una decisión, no una medida.

Con eso: **cero solapes** entre 151 stands y 10 decoraciones.

## Lo que hay que mirar a mano

`3-asignar.py` lleva la tabla `ASIGNACION` escrita a mano, islote por islote en orden de lectura.
Es el único paso que no se puede automatizar: los números son texto blanco dentro de una caja
azul. Se indexa por la **posición y forma** de cada caja, no por un número de orden, así que si
la extracción cambia el script falla en vez de asignarle a un stand el número de otro.

Comprueba sola tres cosas que un mapa mal derivado hace en silencio: claves repetidas, huecos en
la numeración del 1 al 141, y lados de cero.

### Los tres stands en L

`62`, `97` y `109` no son rectángulos: son una banda ancha al fondo con un retorno lateral. Van
con `ancho_celdas`/`alto_celdas` en `null` y su forma en `rectangulos`, que es lo que §3.5 del
modelo de datos prevé. Los tres se verificaron mirando el plano ampliado.

### Los ocupantes de 2026

El plano rotula quién estuvo en dieciséis espacios (Grupo Planeta en el 68, Gandhi en el 93,
Sanborns en el 129…). Van en el JSON bajo `ocupante_2026` y **no se importan**: una convocatoria
nueva nace con todo `Disponible`, y pintar «SANBORNS» sobre un espacio libre sería mentir. Están
porque el plano es el único registro de quién estuvo dónde, y tirarlo al convertirlo a datos
sería perder información que nadie tiene en otro sitio.

## Al cargarlo

El precio **no viene en el mapa**: vive en `ConfiguracionSistema` de la convocatoria (§3.11,
RN-19). Para reproducir 2026 hay que dejarlo en **`costo_m2 = 2500`**, que es lo que hace que el
espacio de 6 m² cueste los 15 000 de la convocatoria.
