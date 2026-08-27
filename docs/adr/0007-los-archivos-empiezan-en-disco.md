---
estado: aceptada
version: "1.0"
tags:
  - tipo/adr
  - dom/std
  - tema/arquitectura
  - tema/seguridad
fecha: 2026-08-27
id: ADR-0007
responsable: Hugo Janssen
supersede:
reemplazado_por:
---
# ADR-0007. Los archivos que sube la gente empiezan en disco, con la puerta de salida puesta

## Estado

`Aceptado` — 2026-08-27. Es la primera de las dos decisiones de infraestructura que bloqueaban
la fase 2 de [`STD`](<../planes/STD.md>).

## Contexto

`CU-STD-001` sube archivos en su primer paso: acta constitutiva, RFC, comprobante de domicilio.
`CU-STD-018` sube comprobantes de pago. Y hoy **el proyecto no tiene dónde ponerlos**: no hay
`MEDIA_ROOT`, no hay `MEDIA_URL`, y no existe un solo `FileField` en ninguna app.

Lo que hay alrededor sí condiciona la decisión:

- **Render está en `plan: free`** (`filey/render.yaml`). Ahí el sistema de archivos del
  contenedor es efímero: cada despliegue lo reemplaza. Los discos persistentes son de los
  planes de pago.
- **La base de datos es Supabase** —lo dice el comentario de `DATABASE_URL` en el mismo
  archivo—, y Supabase incluye un almacén de objetos compatible con S3 en la misma cuenta. No
  está confirmado que esté habilitado.
- **Estos archivos no son públicos.** Son actas constitutivas, RFC y comprobantes de pago de
  personas identificadas. Es una diferencia de fondo con los estáticos, que son parte del
  despliegue y se sirven a cualquiera.
- **Los módulos se construyen a lo largo de meses.** Lo que se decida aquí lo repiten `EVT`,
  `VIS` y los demás, y cada uno que se construya sobre una convención de rutas la vuelve más
  cara de cambiar.

Fuerza principal: **no hay almacén de objetos contratado hoy, y esperar a tenerlo detendría la
fase 2**, que es la que valida la arquitectura entera de `STD`.

## Opciones consideradas

### Opción A: disco ahora, almacén de objetos conmutable por variable de entorno

Guardar con `FileSystemStorage` y dejar `STORAGES["default"]` elegido por una variable de
entorno, de forma que pasar a S3 sea configuración y no código.

- **A favor:**
  - No bloquea la fase 2, que es lo que urge.
  - La migración no toca código: cambiar `ALMACENAMIENTO=local` por `s3` y sus credenciales.
  - `django-storages` habla con Supabase Storage, R2 y AWS por la misma interfaz; lo único que
    los distingue es el endpoint, así que la decisión de *qué proveedor* se pospone sin costo.
- **En contra:**
  - Mientras el plan de Render siga en `free`, los archivos **se pierden en cada despliegue**.
    Es deuda real, no teórica.
  - Un `FileField` guarda una ruta; el archivo que hay detrás puede desaparecer sin que la fila
    cambie. El síntoma llega tarde y disfrazado.

### Opción B: esperar al almacén de objetos

- **A favor:** nada se guarda dos veces, no hay migración pendiente.
- **En contra:** detiene la fase 2 por una compra que no depende del equipo de desarrollo, y la
  fase 2 es la que valida si el enganche de [ADR-0006](<0006-la-liga-entre-convocatoria-y-modulo.md>)
  está bien planteado. Descubrirlo tarde es mucho más caro que migrar unos archivos.

### Opción C: guardar los archivos en PostgreSQL

- **A favor:** persistente desde el primer día, sin infraestructura nueva, y hereda gratis el
  aislamiento por schema de [ADR-0003](<0003-una-feria-por-schema.md>).
- **En contra:** infla la base con datos que no se consultan, complica los respaldos, y no es
  lo que Django espera de un `FileField` —habría que escribir un backend propio—. Se descarta
  por eso último: sería infraestructura a medida para ahorrarse una migración.

## Decisión

**Opción A.** Los archivos se guardan en el sistema de archivos, y el cambio a un almacén de
objetos es una variable de entorno. Con cuatro condiciones que hacen que la deuda no se olvide
y que la migración sea posible.

### 1. El almacén se elige por entorno, no por código

`ALMACENAMIENTO` vale `local` (por omisión) o `s3`. Con `s3` se leen `S3_BUCKET`,
`S3_ENDPOINT_URL`, `S3_ACCESS_KEY` y `S3_SECRET_KEY`, y **si falta alguna el arranque aborta**:
un sistema que arranca a medias perdería en silencio todo lo que alguien subiera.

`django-storages[s3]` **no está en `requirements.txt`** mientras nadie use esa rama — arrastra
`boto3`, que pesa, y el plan de Render es gratuito. Añadirlo es parte de la migración.

### 2. Cada feria guarda en su propia carpeta

`comun/almacenamiento.py::CarpetaDeLaFeria` es el `upload_to` de todos los `FileField` del
proyecto. Antepone el schema de la feria activa:

```
feria_2027/solicitudes/9f2c…a1.pdf
```

Sin eso, [ADR-0003](<0003-una-feria-por-schema.md>) aislaría la base y **no el disco**: las
actas de 2027 y las de 2028 caerían en la misma carpeta. Con el prefijo, el aislamiento llega
igual de lejos en los dos sitios — y en un almacén S3 ese prefijo es justo lo que permite dar
credenciales acotadas a una edición si algún día hace falta.

**El nombre original no se conserva.** `RFC_JUAN_PEREZ_2019.pdf` dice quién es la persona antes
de abrir el archivo, y además es adivinable. Se sustituye por un UUID y se conserva solo la
extensión.

> [!warning] Esto se congela en la primera migración que lo use
> `upload_to` viaja **dentro** de las migraciones. Cambiar el esquema de rutas más adelante no
> reescribe lo ya guardado: deja los archivos viejos donde estaban y los nuevos en otro sitio.
> Si hay que cambiarlo, se cambia con una migración de datos que mueva los archivos.

### 3. Ningún archivo se sirve por una URL

**No hay ruta para `MEDIA_URL` en ningún urlconf, y es deliberado.** Estos documentos son
privados; servirlos desde una URL estática los deja al alcance de cualquiera que la tenga o la
adivine, sin pasar por ninguna comprobación de permisos.

Cada módulo entrega los suyos por una vista que comprueba quién pregunta —es trabajo de la fase
2, junto con el primer `FileField`—. `MEDIA_URL` existe porque `FileField.url` la usa para
componer, no porque algo la resuelva.

Con `s3`, además, el bucket es privado y las URL van firmadas con caducidad; aun así **la puerta
sigue siendo la vista del módulo**, no el bucket.

### 4. La deuda avisa sola

`manage.py check --deploy` emite `comun.W001` cuando `DEBUG=False`, el almacén es el sistema de
archivos y `MEDIA_ROOT` no está declarada. Es un **aviso y no un error**: la decisión está
tomada y bloquear el despliegue por ella sería estorbar. Pero lo que se pierde no da ningún
síntoma —la fila sigue ahí, con su ruta, y el archivo ya no está detrás—, así que tiene que
haber algo que lo diga en voz alta.

Se calla de las dos formas correctas: apuntando `MEDIA_ROOT` a un disco montado, o poniendo
`ALMACENAMIENTO=s3`.

## Cómo se migra, cuando haya bucket

1. Añadir `django-storages[s3]` a `requirements.txt`.
2. Poner `ALMACENAMIENTO=s3` y las cuatro credenciales en el entorno.
3. Copiar el contenido de `MEDIA_ROOT` al bucket **conservando las rutas relativas**. Son las
   mismas claves: `feria_2027/solicitudes/9f2c….pdf` es la ruta en disco y la clave en S3.
4. Retirar el bloque `disk:` de `render.yaml`.

No hay migración de base de datos: lo que guarda un `FileField` es la ruta relativa, y no
cambia. Ese es el motivo de que el paso 2 de esta decisión —el prefijo por feria— importe tanto
como el 1.

## Consecuencias

**Positivas**

- La fase 2 puede empezar sin esperar a una compra.
- La migración es de configuración, no de código, y la convención de rutas ya la contempla.
- Los archivos nacen aislados por feria y con nombres que no dicen nada de quien los subió.
- Que no se sirvan por URL es lo seguro **por omisión**: si nadie escribe la vista, no se
  filtra nada; el fallo es no poder abrir un archivo, no exponerlo.

**Negativas / riesgos aceptados**

- **Con Render en `free`, los archivos se pierden en cada despliegue.** Es la deuda que esta
  decisión acepta a sabiendas. `render.yaml` ya trae el bloque `disk:` escrito, pero no tiene
  efecto hasta que el plan suba a `starter`.
- **`FileSystemStorage` no sirve para más de un proceso en máquinas distintas.** Hoy es un solo
  servicio; si algún día hay dos, el disco local deja de valer aunque persista.
- **Sin la vista de entrega, un `FileField` guardado no se puede abrir desde la aplicación.**
  Es intencional, y es trabajo de la fase 2.

**Qué queda descartado por esta decisión**

- Servir archivos subidos desde una URL estática, con o sin WhiteNoise.
- Guardar binarios en PostgreSQL.
- Un `upload_to` escrito a mano en cualquier `FileField` del proyecto.

## Referencias

- [ADR-0003](<0003-una-feria-por-schema.md>) — el aislamiento por feria que el prefijo de ruta
  extiende al disco.
- [`Plan de construcción — Stands`](<../planes/STD.md>) — fase 1, la decisión que este ADR cierra.
- `CU-STD-001` y `CU-STD-018` — los dos casos de uso que suben archivos.
- `filey/comun/almacenamiento.py` y `filey/comun/checks.py::almacenamiento_persistente_en_produccion`.
