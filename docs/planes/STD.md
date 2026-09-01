---
estado: propuesta
version: "1.0"
tags:
  - tipo/plan
  - dom/std
  - dom/fer
  - tema/alcance
  - tema/arquitectura
fecha: 2026-08-27
responsable: Hugo Janssen
---
# Plan de construcción — Stands (`STD`)

Siete fases ordenadas por dependencia para llevar `STD` de 39 casos de uso documentados a un
módulo servido. **El orden no es de comodidad**: cada fase está donde está porque desbloquea la
siguiente.

| | |
| --- | --- |
| Casos de uso | 39 (`CU-STD-001` … `CU-STD-039`) |
| Entidades | 16 |
| Reglas de negocio | 22 (`RN-01` … `RN-22`) |
| ADR que lo gobiernan | 0001, 0003, 0004, 0005, 0006 |

---

## 1. Dónde estamos hoy

### Construido y probado

- `REG` — identidad y acceso por OTP.
- `FER` — ferias, accesos por feria, catálogo de convocatorias.
- Alta de convocatorias desde el admin de la edición (`/f/<slug>/django-admin/`).
- **La fase 0 completa** (2026-08-27): `RegistroConvocatoria`, el registro de módulos, la
  tarjeta del catálogo enlazando de verdad y el callback de configuración del alta.
- **La fase 1, en su mitad de almacenamiento** ([ADR-0007](<../adr/0007-los-archivos-empiezan-en-disco.md>)).
- **La fase 2 completa** (2026-08-27): `apps/stands` con la vertical de solicitud entera,
  `CU-STD-001` a `008`, y las vistas U1, A1 y A2.
- 301 pruebas en verde.
- Los estados del mapa en Godot: renombrados al vocabulario del dominio, probados y reexportados.

### Decidido, sin construir

- [ADR-0006](<../adr/0006-la-liga-entre-convocatoria-y-modulo.md>) — la liga convocatoria ↔ módulo.
- [`Modelo de datos - Stands`](<../requisitos/STD/Modelo de datos - Stands.md>) v3.0.
- [`Reglas de negocio - Stands`](<../requisitos/STD/Reglas de negocio - Stands.md>) — `RN-01` a `RN-22`.
- `CU-STD-037`, `CU-STD-038` y `CU-STD-039` — servir e importar el mapa.

- [ADR-0007](<../adr/0007-los-archivos-empiezan-en-disco.md>) — dónde viven los archivos
  subidos, **construido** el 2026-08-27: ajustes conmutables, `CarpetaDeLaFeria` y el aviso
  `comun.W001`.

### Sin decidir

Ver §4. Queda una que bloquea una fase: quién invoca la barrida diaria de la fase 6.

> [!note] Qué cambió respecto del plan anterior
> **El mapa dejó de ser la fase cara.** Era el riesgo mayor —editor dentro del sistema,
> `saveMap`, persistencia en las dos direcciones— y al decidirse que por ahora solo se importa un
> JSON externo y el sistema lo vuelve a generar (`CU-STD-039`), pasó a ser una fase acotada. Por
> eso el mapa y la reserva, que antes iban juntos, ahora son dos fases: cada una es demoable por
> su cuenta.

---

## 2. Las siete fases

### Fase 0 · El enganche — ✅ construida el 2026-08-27

> **Es `FER`, no `STD`.** Vive en `apps/convocatorias` y desbloquea todo lo demás.

- `RegistroConvocatoria`, única por (`convocatoria`, `persona`). Primera clave foránea del
  proyecto que cruza del schema de una feria a `public`.
- `modulos.py`: el registro donde cada vertical se inscribe desde su `AppConfig.ready()`.
- `servicios/registros.py`: la única puerta por la que un módulo crea una inscripción, y donde
  se comprueba la invariante del tipo que la base no puede sostener.
- La tarjeta del catálogo enlazando de verdad, con degradado a «próximamente» cuando el tipo no
  tiene módulo instalado, y el conteo de registros para quien administra.
- El callback que crea la configuración del módulo — cierra el paso 6 y E1 de `CU-FER-005`.

> [!important] El registro nace al guardarse el expediente, no al pulsar el botón
> El enlace de la tarjeta solo navega. Si el registro naciera con el clic, cualquier visita
> curiosa dejaría una inscripción vacía y las listas de la convocatoria contarían gente que
> nunca aplicó.

### Fase 1 · Dos decisiones de infraestructura

| Decisión | Qué bloquea | Estado |
| --- | --- | --- |
| **Almacenamiento de archivos** | Fase 2 (`CU-STD-001`) | ✅ [ADR-0007](<../adr/0007-los-archivos-empiezan-en-disco.md>) — 2026-08-27 |
| **Quién invoca la barrida diaria** | Fase 6 | ✅ Workflow programado de GitHub Actions — 2026-08-29 |

**Almacenamiento — decidido y construido.** Empieza en disco y el paso a un almacén de objetos
es una variable de entorno, no código. Con eso la fase 2 deja de estar bloqueada. Lo que queda
es una deuda con nombre: mientras Render siga en `plan: free` no hay disco persistente y los
archivos se pierden en cada commit a la rama desplegada — `manage.py check --deploy` lo dice en
voz alta (`comun.W001`) para que no se olvide.

**La barrida — decidida el 2026-08-29: workflow programado de GitHub Actions.** Lo que hace
falta es **un** comando de `manage.py`, idempotente, que corra una vez al día; no un
planificador para seis procesos (ver la fase 6).

Se eligió Actions porque **el patrón ya existe y funciona**: `deploy.yml` corre
`migrate_schemas` y `ensure_superuser` contra Supabase con `SUPABASE_DB_URL` en los secretos.
Un workflow con `schedule:` es ese mismo bloque con otro disparador.

> [!note] Supabase no era una opción, aunque lo pareciera
> Su único reloj es `pg_cron`, que ejecuta **SQL dentro de Postgres**. La barrida manda dos
> correos (`CU-STD-024` y `CU-STD-025`) por el backend de Resend y escribe una `Notificacion`
> por envío. Partirla entre SQL y Python dejaría la misma regla de negocio en dos lenguajes y
> rompería la regla 3.

> [!warning] Lo que Actions cuesta, y hay que asumir a sabiendas
> `RESEND_API_KEY` **no está hoy en los secretos de GitHub** y tendrá que estar. Con eso las
> credenciales de producción viven en **dos** sitios —Render y GitHub—: un secreto más que rotar
> y un sitio más desde el que se puede mandar correo con la identidad de FILEY.
>
> La alternativa que lo evita es que la barrida sea una **URL protegida por token** que el
> workflow golpea: corre dentro del contenedor, con su entorno, y el disparador no necesita más
> credencial que el token. Es más código y menos superficie de secreto; queda anotada por si al
> montar la fase 6 se prefiere.

No bloquea la fase 2.

### Fase 2 · Solicitud — ✅ construida el 2026-08-27

> `CU-STD-001` a `008` · vistas U1, A1, A2 · **necesita** las fases 0 y 1.

- Esqueleto de `apps/stands` —app de Django propia, en `TENANT_APPS`— e inscripción en el
  registro de módulos.
- `Editorial` (1—1 con `Persona` por feria, `RN-21`), `SelloEditorial`, `Solicitud` (fotografía y
  1—N por registro, `RN-22`), `Documento`.
- `ConfiguracionSistema` y su `crear_por_defecto`, que es lo que la fase 0 invoca por callback.
- `Notificacion` en el schema de la feria, con el envío por `apps/notificaciones`.
- La entrega de adjuntos: una vista que comprueba quién pregunta y, con almacén de objetos,
  redirige a una URL firmada sin que el archivo pase por Django (`ADR-0007`).

> [!important] `stands` es una app, y no comparte modelos con ningún otro módulo
> Ni con `EVT`, ni con una app «de convocatorias» que sirva a varios. Cada vertical tiene su
> propia app, sus propias tablas y su propio namespace de URLs; lo único común es lo que `FER`
> es dueña de tener común —`Convocatoria`, `RegistroConvocatoria` y el registro de módulos—, y
> la dependencia va en una sola dirección (ADR-0006).
>
> Vale también para la configuración: `ConfiguracionSistema` es de `stands` y vive en
> `apps/stands`. Homologar su nombre con el `ParametrosConvocatoria` de `EVT` (§4) es alinear
> **cómo se llaman**, no fundirlas en una tabla.

> [!important] Es la fase que valida la arquitectura, y por eso va antes que el mapa
> Recorre la vertical entera —catálogo, registro, expediente, dictamen, correo— **sin mapa ni
> dinero**. Si el enganche de ADR-0006 está mal, se ve aquí y es barato arreglarlo. Descubrirlo
> en la fase 4 significa tener reservas encima.

### Fase 3 · El mapa

> `CU-STD-037`, `038`, `039` · vistas U2, A8 · **necesita** la fase 2.

> [!important] Construida el 2026-08-29, y con una corrección de rumbo
> Se construyó primero **en SVG servido por el servidor**, por no releer este plan: aquí decía
> Godot y el `CU-STD.csv` marca `Embedded Godot View`. Corregido con
> [ADR-0008](<../adr/0008-el-mapa-corre-en-el-navegador.md>), que además retira la mitad de la
> regla 6 que el canvas no puede cumplir.
>
> Lo que quedó: el build vendorizado en `filey/estaticos/mapa/` **fuera del manifiesto**
> (`comun/estaticos.py` — el riesgo Alto de §3, cerrado y con prueba), el puente `postMessage`
> en `filey.js`, los dos endpoints de datos con el recorte de `RN-09` **antes de serializar**, y
> la tarjeta de detalle del lado de la página, que es donde el contrato del componente la pone.

- `MapaShowfloor`, `Stand` con su forma en celdas, `DecoracionMapa`.
- Importar un JSON externo (`CU-STD-039`) desde el admin de la edición, que ya está construido.
- Servir el mapa a los dos públicos: el aplicante no distingue reservado de ocupado (`RN-09`), el
  administrador sí (`RN-18`).
- Vendorizar el build de Godot y escribir el popover de detalle del stand en `filey.css`.

> [!warning] El recorte de `RN-09` va en la consulta, no en la plantilla
> Si el estado real y la identidad de quien reservó viajaran al navegador —aunque la pantalla no
> los pinte—, cualquiera con las herramientas de desarrollo abiertas vería qué editorial tiene
> apartado qué espacio.

### Fase 4 · Reserva

> `CU-STD-009` a `014` y `021` · vistas U3, U4, U5 · **necesita** la fase 3.

- Carrito en la sesión de Django: todavía no hay `Reserva`.
- `Reserva` y `ReservaStand`, que solo dice qué stands entran y no guarda importes.
- El plazo de 30 días (`RN-03`) y el paso de los stands a `Reservado` (`RN-10`).

### Fase 5 · Pago

> `CU-STD-015` a `020` · vistas U6, A4, A5 · **necesita** las fases 1 y 4.

> [!important] Construida (2026-08-29)
> El lado del expositor entero (`015`, `016`, `017`), **la cola de validación** (`018`, vista
> A5) —que es la que cierra el ciclo: sin ella un abono se quedaba `pendiente_validacion` para
> siempre y los umbrales de `RN-13`/`RN-14` no podían dispararse nunca— y **A4** (`029`) como
> vista-contenedor, con el abono manual (`019`) y el descuento especial (`020`) colgando de
> ella.
>
> Dos decisiones que la construcción tuvo que tomar y conviene saber:
>
> - **El abono manual nace `validado`**, como pide el paso 6 de `CU-STD-019`, y no
>   `pendiente_validacion` como el del expositor. Lo asienta quien coteja contra el banco; una
>   cola en la que la administración se valida a sí misma no significa nada.
> - **Retirar un descuento borra la fila** (ver §4). Es lo que ya hacía `caducar_pronto_pago`
>   desde que se construyó, así que la alternativa habría dejado dos comportamientos distintos
>   para la misma operación.
>
> Y un defecto que solo aparece con pantalla delante: cualquier cambio de descuento **recalcula
> sobre una instancia recién traída**. `_recalcular_total` lee `reserva.descuentos.all()`, y una
> vista llega con `prefetch_related` puesto —la caché se llenó antes de tocar la fila—, así que
> el total salía idéntico y el descuento no descontaba nada.

- `Movimiento` con comprobante, y su validación.
- `DescuentoAplicado`, con el tope de uno por tipo garantizado en la base (`RN-05`).
- Los dos descuentos aplicados **en secuencia** (`RN-06`): 10% y 15% dan un 23.5% efectivo, no un
  25%.

> [!warning] `monto_total` se congela frente al precio, pero no frente a los descuentos
> Es una distinción que ningún documento hacía hasta la v3.0 del modelo. Cambiar el `costo_m2` o
> corregir el mapa **no** mueve lo cobrado; aplicar o retirar un descuento **sí**, y obliga a
> reevaluar los umbrales del 50% y el 100%.

### Fase 6 · Estados automáticos

> `CU-STD-022` a `027` · sin vistas · **necesita** las fases 1 y 5.

> [!important] Fase construida (2026-08-30)
> `manage.py barrida_diaria` cierra `CU-STD-022`, `024` y `025`, y con ellos la mitad de
> `CU-STD-023` que necesitaba reloj. La invoca `.github/workflows/barrida-diaria.yml` a las
> 09:00 de Mérida — por la mañana y no de madrugada a propósito: de ahí salen correos a
> editoriales, y llegar a las 3 a. m. hace que se lean como spam.
>
> El orden dentro de la barrida importa: **primero se retira el pronto pago vencido y después
> se avisa**. Retirarlo sube el total y con él el anticipo, así que una reserva al filo puede
> quedarse corta el mismo día, y el aviso tiene que salir con las cifras de después.
>
> Se avisa **una vez por vencimiento**, no una por reserva: la pregunta es si ya salió un aviso
> posterior a la fecha de vencimiento vigente. Así una prórroga que también se agota vuelve a
> avisar sin borrar nada, y un aviso `fallida` se reintenta al día siguiente.

> [!important] Los dos umbrales ya avisan (2026-08-30)
> `CU-STD-026` y `CU-STD-027` están construidos: al cubrirse el anticipo y al liquidar sale un
> correo y queda su `Notificacion`, que A4 enseña. Con ellos entró lo que el paso 4 de
> `CU-STD-026` daba por existente y no estaba en ninguna tabla: la **base** de la fecha de
> corte, en `ConfiguracionSistema`, de la que cada reserva hereda la suya al confirmarse. Sin
> ella `Reserva.fecha_corte_pago_total` no lo escribía nadie.
>
> El correo se programa con `transaction.on_commit` y no se manda dentro de `reevaluar`: esa
> función corre siempre en una transacción, y un correo no se puede deshacer.
>
> **Queda la barrida**: `022`, `024` y `025`, que son las tres que sí necesitan reloj.

> [!important] No son seis procesos temporizados — es uno
> El plan decía "los seis procesos temporizados" y los casos de uso no lo sostienen. Corregido
> el 2026-08-27, porque cambia el tamaño de la decisión de la fase 1.

**Lo que necesita reloj es una sola barrida diaria**, la de `CU-STD-022` paso 3: recorre las
reservas `Por confirmar`, y de las que ya pasaron su `fecha_vencimiento_anticipo` sin llegar al
50% dispara el aviso al administrador (`CU-STD-024`) y la advertencia al aplicante
(`CU-STD-025`). Esos dos no son procesos aparte: son lo que la barrida hace al encontrar algo.

**Lo que no necesita reloj** son los umbrales. `CU-STD-026` (50%) y `CU-STD-027` (100%) se
disparan *durante la reevaluación del saldo*, o sea dentro de validar un abono, en la misma
petición y de forma síncrona. No hay nada que esperar.

`CU-STD-023` —el 10% por pronto pago— está a caballo: se aplica al reservar, se consolida al
liquidar, y **caduca con el reloj**. Esa última mitad la escribió `caducar_pronto_pago` el
2026-08-29 —sin ella el descuento no se retiraba nunca y el carrito prometía lo contrario— y
desde el 2026-08-30 la llama `barrida_diaria`. El comando suelto se queda como herramienta de
diagnóstico: tiene `--seco` con el detalle reserva por reserva.

> [!warning] La barrida tiene que recorrer los schemas, no las filas
> `Reserva` vive en el schema de cada feria y ninguna consulta lleva filtro de edición
> (`ADR-0003`). Un `Reserva.objects.filter(...)` desde `public` no ve **nada**: no falla, no
> devuelve nada, y el comando parecería no tener trabajo. Hay que iterar las ferias y correr la
> barrida dentro de cada una — el mismo patrón que `migrate_schemas`.
>
> Y solo sobre las ediciones vivas: una feria archivada no manda avisos de vencimiento a nadie.

> [!important] Vencer el plazo no libera nada
> El sistema notifica y espera la decisión de una persona (`RN-12`, y el paso 7 de
> `CU-STD-022`): la reserva se queda donde está hasta que alguien la cancele o la prorrogue. Es
> la regla que más se presta a implementarse de más — un comando que "limpia" reservas vencidas
> liberaría stands que nadie decidió liberar.

### Fase 7 · Administración restante

> `CU-STD-028` a `036` · vistas A3, A6, A7, A9, A10 · **necesita** la fase 6.

> [!important] Construida salvo Expositores y A9 (2026-08-30)
> Hechas: `028` y `029` (A3 y A4), `032` (A8), `034` (A10), y `035` y `036` en el bloque
> «Plazos y estado» de A4. Con `035` deja de haber un agujero que llevaba abierto desde el
> principio: **`cancelada` era un estado inalcanzable**, así que ninguna reserva podía cerrarse
> por ningún camino y `RN-11` describía algo que no existía.
>
> Y desde el 2026-08-30 también `030` y `031` (A6 y A7), con lo que **no queda ninguna sección
> del panel apagada**. Ahí salió a la luz que `CU-STD-031` paso 2 pide un RFC que el modelo no
> tiene: la ficha en papel lo entrega como constancia adjunta, no como campo. Ver A7 en
> [`Estructura de vistas`](<../requisitos/STD/Estructura de vistas - Stands.md>).
>
> Y con `BitacoraSTD` (2026-08-30) queda cerrado §3.12: **su pantalla es el admin de Django**,
> en solo lectura. Decisión del cliente, y la correcta — se consulta tres veces al año, y una
> sección propia en la barra lateral costaría más de lo que resuelve.
>
> Queda la pantalla A9 de `033`, que hoy solo se hace desde el admin de Django, y que se
> aplaza a propósito (2026-08-30).

- Listados de reservas y de expositores, con el detalle de cada uno.
- ~~Configuración de la convocatoria (`CU-STD-034`)~~ — **construida el 2026-08-29**, adelantada
  a esta fase porque sin ella los datos bancarios de `CU-STD-015` no se podían declarar más que
  desde el admin de Django. Es la vista A10.
- Resolución de reservas vencidas.
- `Bitacora` de `STD` — una por módulo, decidido el 2026-08-27.

---

## 3. Riesgos con nombre

| Riesgo | Nivel | Por qué importa |
| --- | --- | --- |
| ~~El build de Godot pesa 39.5 MB~~ | **Cerrado** | 2026-08-29. Vive en `filey/estaticos/mapa/` y `comun/estaticos.py` lo deja sin hashear **pero dentro del manifiesto** — sacarlo del todo rompía `{% static %}` con `Missing staticfiles manifest entry`, que era el mismo fallo por otra puerta. Cubierto por `comun/pruebas/test_estaticos.py`. |
| El prototipo de `STD` no está en `prototipo/` | **Alto** | Vive en `/Users/janssen/Projects/Filey/STD` (Angular + Material) y el componente de mapa en `/Users/janssen/Projects/Filey/event-stand-map`. **Que no estén en este repositorio ya costó una fase**: se dieron por inexistentes y se construyó el mapa en SVG. Portar U1–U6 y A1–A10 sigue sin ser mecánico. |
| La invariante del tipo es de código | Medio | Nada en el esquema impide colgar una `Solicitud` de stands de un registro cuya convocatoria es de eventos. Se comprueba en el servicio y hay prueba, pero la base no lo sostiene (ADR-0006). |
| Una vista de participante dentro de una feria enlaza fuera | Bajo | `requiere_participante` redirigía con `reverse("registros:acceso")`, que no resuelve dentro de `/f/<slug>/`. No se había notado porque ninguna vista de participante vivía dentro de una feria; U1 fue la primera. Corregido con `url_publica` y con prueba, pero es el patrón que va a volver en `EVT` y en `VIS`. |
| `stand-map-host` sigue en inglés | Medio | No está bajo git y tiene dos parches LAN aplicados a mano. Hoy funciona porque su build y sus datos son igual de viejos; al refrescarlo hay que reaplicar los parches y traducir los JSON en el mismo paso. |
| El modelo de `EVT` contradice a ADR-0006 | Medio | Sigue describiendo el `RouterSolicitudes` derogado. Es contradicción de papel, no de base de datos: corregirla es requisito para empezar `EVT`, no para terminar `STD`. |

---

## 4. Lo que sigue sin decidirse

| Pregunta | Bloquea | Quién decide |
| --- | --- | --- |
| Quién invoca la barrida diaria: Actions o un cron de Render | Fase 6 | Equipo — es un ADR, y depende del plan de Render |
| Subir Render a `starter` para tener disco persistente, o contratar almacén de objetos | Nada, pero hay archivos en juego | Equipo — ver ADR-0007 |
| ~~Retirar un descuento: ¿borra la fila o la marca?~~ **Borra la fila** (2026-08-29). Es lo que `caducar_pronto_pago` ya hacía; marcarla habría dejado dos comportamientos para lo mismo. El rastro de quién lo retiró vive hoy solo en el log — lo recoge `BitacoraSTD` cuando exista | — | Decidido |
| ¿Hace falta el desglose de una reserva vieja tal como se aceptó? | Fase 7 | Cliente |
| ¿El correo de la editorial se prellena desde el de la persona? | Fase 2 | Cliente |
| `es_recurrente` — exige una tabla histórica en la capa global | Fase 7 | Equipo, una vez para los cuatro dominios |
| Homologar el nombre de `ConfiguracionSistema` con el de `EVT` (I-12) — mismo nombre, una tabla por módulo | Nada | Equipo |

---

## 5. Por dónde empezar

**La fase 3, el mapa.** Es lo siguiente que la fase 2 desbloquea: ya hay expositores
aceptados y `RN-16` los habilita para reservar, pero no hay dónde elegir espacios.

**Lo que la fase 2 dejó comprobado**, y que valía la pena saber antes de seguir:

- El enganche de [ADR-0006](<../adr/0006-la-liga-entre-convocatoria-y-modulo.md>) **funciona
  end-to-end**. El alta de una convocatoria de stands crea su `ConfiguracionSistema` sin que
  `apps/convocatorias` importe nada de `apps/stands`, y hay prueba que recorre los dos dominios.
- La tarjeta del catálogo **navega de verdad** por primera vez: `STD` dejó de decir
  «próximamente».
- `requiere_participante` estaba roto dentro de una feria y nadie lo había notado — ver la tabla
  de riesgos.

---

Ver también: [Índice de casos de uso](<../requisitos/STD/CU-STD Índice.md>) ·
[Modelo de datos](<../requisitos/STD/Modelo de datos - Stands.md>) ·
[Reglas de negocio](<../requisitos/STD/Reglas de negocio - Stands.md>) ·
[ADR-0006](<../adr/0006-la-liga-entre-convocatoria-y-modulo.md>)
