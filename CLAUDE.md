# FILEY 2027

Sistema de registro y gestión de la Feria Internacional de la Lectura Yucatán (UADY).
Todo lo siguiente vive en esta rama:

| Dónde | Qué es |
| --- | --- |
| `filey/` | El monolito Django real (ADR-0001). Hoy solo tiene construido el Core Registros. |
| `prototipo/` | Mockup HTML estático. Es la **especificación visual** y el entregable que ve el cliente; se publica a GitHub Pages en cada push a `main` que lo toque. |
| `docs/` | Requisitos por dominio (`CU-DOM-NNN`), ADRs y evidencia de juntas. |

La arquitectura la mandan `docs/adr/`; los detalles de cómo se construye una pantalla viven en
los skills, no aquí.

## Qué skill aplica

| Vas a… | Skill |
| --- | --- |
| Elegir color, tipografía, radio, sombra | `filey-identidad` |
| Decidir cuántos pasos/campos/opciones lleva una pantalla, qué se revela y cuándo, o escribir un texto que alguien va a leer | `filey-ux` |
| Escribir o editar CSS/markup, buscar si una clase ya existe | `filey-ui-componentes` |
| Tocar plantillas, vistas, URLs, estáticos, o portar del prototipo a Django | `filey-render` |

Cada hecho vive en **un solo** skill; los demás enlazan. No dupliques contenido entre ellos.

## Reglas de arquitectura

Vienen de los ADR y no se contradicen sin escribir uno nuevo (ver `docs/adr/README.md`).

1. **Monolito Django** (ADR-0001). Un solo proyecto, un solo despliegue. Sin API REST ni SPA
   separada; la interactividad es htmx + Alpine servidos desde `filey/estaticos/js/`.
2. **La sesión es la de Django** (ADR-0002), cookie `HttpOnly` con estado en el servidor. No
   hay JWT, ni tokens en el cliente, ni CORS. Ningún módulo implementa su propia autenticación
   ni su propio control de acceso: importa los decoradores. Quién decide qué:
   `apps/registros/permisos.py` para lo de fuera de una feria (`requiere_participante`,
   `requiere_admin`) y `apps/ferias/permisos.py` para lo de dentro (`requiere_admin_feria`,
   `requiere_dueno_feria`). Por encima de los dos pasa el **operador de la plataforma**
   —superusuario de Django—, que alcanza cualquier feria sin tener fila en `AdminFeria`
   (ADR-0005). No lo comprueba ninguna vista por su cuenta: vive en `es_operador()` y lo
   consultan `administra()` y `tiene_alcance_de_dueno()`, que son las dos funciones que
   responden "¿administra ésta?" para los decoradores **y** para las pantallas. El middleware de feria **no comprueba permisos** —corre antes de
   `AuthenticationMiddleware`, así que no hay `request.user`—: solo fija el schema.
   > **Autoridad y cara son dos preguntas.** `administra()` dice qué puede hacer y no la mueve
   > nada que decida quien mira: de ella cuelgan los decoradores, la entrega de archivos y el
   > recorte de `RN-18`. `ve_como_admin()` dice desde qué lado está mirando **ahora**, y es la
   > que usan la barra superior, el catálogo y el detalle de un espacio. La diferencia es la
   > puerta por la que entró (`sesion.contexto_de_la_sesion`): una misma cuenta coordina una
   > feria y tiene su editorial dentro de ella, y por el acceso de participante viene a lo
   > segundo. `ve_como_admin()` **solo quita**; entrar por la puerta de administración no
   > convierte a nadie en administrador. La barra ofrece el conmutador y abrir una pantalla de
   > administración devuelve esa cara sola.
3. **Capas por app:** `models.py` (datos e invariantes, modelos gordos) → `services/` (reglas de
   negocio) → `views.py` (traduce HTTP ↔ servicio, vistas delgadas) → plantillas.
   Si una regla no se puede llamar desde un comando de `manage.py` sin pasar por HTTP, está en
   el lugar equivocado: va a `services/`.
4. **Las dependencias van en una sola dirección.** Los dominios verticales (`eventos`,
   `talleres`, `stands`, `visitas`) importan de `registros` —que es la base de identidad—,
   nunca al revés, y nunca en círculo entre hermanos.
5. **Cada feria vive en su propio schema de PostgreSQL** (ADR-0003), y la feria es el
   contexto de la conexión, **no una columna**: ninguna tabla de contenido lleva `feria_id` ni
   ninguna consulta un filtro de feria. Se implementa con `django-tenants`; lo que decide dónde
   va la tabla de una app es en cuál de las dos listas de `settings.py` esté —`SHARED_APPS`
   (schema `public`) o `TENANT_APPS` (uno por feria)—. Una app en las dos duplica sus tablas en
   todos los schemas. **PostgreSQL es obligatorio, también en desarrollo**: SQLite no tiene
   schemas y el arranque aborta si `DATABASE_URL` no apunta a Postgres.
6. **Nada se carga de un CDN.** Todo lo que el navegador descarga vive en el repositorio —htmx,
   Alpine, y los 39 MB del build de Godot del showfloor—.
   > La otra mitad de esta regla —"toda pantalla funciona sin JavaScript"— **se retiró** en
   > ADR-0008: el mapa es un canvas de WASM y no puede cumplirla. Las pantallas que hoy
   > funcionan sin JavaScript siguen haciéndolo y conviene que sigan, pero ya no bloquea.
7. Nombres en español, consistentes, tanto en código como en rutas de archivo. Sin eñes en
   identificadores ni nombres de columna (`es_dueno`, `contrasena`): la eñe arrastra
   fricción de codificación en cada herramienta que toque la base.
8. **Un vertical se engancha a su convocatoria por el registro de módulos** (ADR-0006).
   `apps/convocatorias` **nunca nombra a un vertical**: cada app se inscribe a sí misma desde
   su `AppConfig.ready()` con `apps.convocatorias.modulos.registrar(Modulo(...))`, diciendo su
   tipo, a qué URL manda al aplicante y al administrador, y qué configuración crear en el alta.
   La liga persona↔convocatoria es `RegistroConvocatoria`, y la única puerta para crearla es
   `servicios/registros.py::obtener_o_crear_registro`, que exige `tipo_esperado` — es lo único
   que sostiene el invariante de tipo, porque la base no puede.
9. **Los archivos que sube la gente no tienen URL** (ADR-0007). `MEDIA_URL` no está montada en
   ningún urlconf, a propósito: son constancias fiscales y comprobantes de personas
   identificadas. Se alcanzan por una vista que primero decide y luego entrega
   (`apps/stands/servicios/archivos.py` es el patrón). Dónde viven lo decide `ALMACENAMIENTO`
   —`local` en disco, `s3` cuando haya bucket— y quien llama no cambia. Todo lo que se suba
   pasa por la lista blanca de `comun/almacenamiento.py`: se sirven desde nuestro propio
   origen, así que un `.html` admitido sería XSS con nuestras cookies detrás.

## Estado actual

- **Construido:** `REG` (Core Registros) — acceso por OTP de participante y de administrador,
  y alta de cuenta. `apps/registros/` es la app de referencia; `apps/notificaciones/` encapsula
  el envío de correo (Resend). `REG` acaba en cuanto hay sesión: lo que se ve después es de
  `FER`.

  > [!warning] `Persona.estado` **no** es una entidad federativa
  > Es el estado de la cuenta (`activa`/`inactiva`). La entidad se llama **`entidad`** —ese
  > nombre ya estaba tomado— y su etiqueta en pantalla sí es «Estado». Con `ciudad`, son los
  > dos campos que **solo se piden si el país es México** (`CU-REG-001` A2): fuera se quedan
  > vacíos, y `RegistroForm.clean` los descarta aunque lleguen, porque un POST fabricado a
  > mano no pasa por la pantalla que los esconde. Los dos catálogos guardan **código y no
  > nombre** —`MX`, `YUC`— por el mismo motivo: el nombre se escribe de varias formas y el
  > código no (`registros/paises.py`, `registros/estados_mx.py`). Para copiarlos a una ficha
  > que guarda texto —el domicilio fiscal de `STD`— está `Persona.estado_nombre`.
- **Construido:** `FER` (Core Ferias) — `apps/ferias/` (capa `public`: `Feria`, `AdminFeria`,
  el alta desde `/django-admin/`, las dos pantallas de elegir feria y los accesos de una feria
  en `/f/<slug>/accesos/`) y `apps/convocatorias/` (capa por feria: `Convocatoria` y su
  catálogo, que es la portada de `/f/<slug>/`, y el alta de convocatorias desde
  `/f/<slug>/django-admin/`), más `RegistroConvocatoria` y el registro de módulos que enganchan
  el catálogo con cada vertical (ADR-0006). Falta la pantalla de convocatorias del panel del
  dueño (CU-FER-005 a CU-FER-009 con su propia UI), la transferencia de propiedad y
  `BitacoraFER`.
- **Construido a medias:** `STD` (Stands) — `apps/stands/` tiene dos verticales completas:
  - **La solicitud de expositor** (CU-STD-001 a 008): la ficha oficial en U1, la cola de
    revisión y el detalle en A1 y A2, el dictamen con su aviso por correo, los adjuntos con
    permiso.
  - **El mapa del showfloor** (CU-STD-009, 010, 032, 039): `MapaShowfloor`, `Stand` y
    `DecoracionMapa`; la importación desde JSON —`servicios/mapas.py`, la pantalla del admin de
    la edición y `manage.py importar_mapa`—; y el mapa dibujado en **SVG servido**, que es la
    misma plantilla para el aplicante y para quien administra (lo que cambia es si `reservado`
    y `ocupado` llegan colapsados, RN-09). El mapa de 2026 vive en
    `apps/stands/mapas/filey-2026.json` (151 espacios, 2 628 m²), derivado del plano en papel
    por `scripts/derivar-mapa/`.

  - **La reserva** (CU-STD-011, 012, 013, 021, 028, 029): `Reserva`, `ReservaStand` y
    `DescuentoAplicado`; el carrito en la sesión, la reserva con los stands bloqueados
    (`select_for_update` — es lo que sostiene «primero en confirmar gana»), y el panel de
    reservas del administrador. **Todo el cálculo del dinero vive en
    `servicios/reservas.py::total_con_descuentos`**, que es la única función que calcula un
    total: los descuentos se aplican en secuencia, no sumando (RN-06).

  - **La cuenta y sus pagos** (CU-STD-013, 014, 015, 016, 017): `Movimiento`, y la pantalla
    del expositor —`/f/<slug>/stands/<id>/mi-reserva/`— con tres pestañas por `?ver=`:
    resumen, pagos y el plano en modo consulta. Los **datos bancarios son seis campos** de
    `ConfiguracionSistema` (titular, banco, cuenta, CLABE, sucursal, referencia) y no un
    bloque de texto: `CU-STD-015` pide enseñarlos estructurados, y así se copian de uno en uno
    frente a la app del banco. Los declara quien administra desde
    la pantalla de configuración del panel. Un abono que reporta el expositor nace
    `pendiente_validacion` y **no baja el saldo**: `Reserva.monto_abonado` solo cuenta lo
    validado, y lo que está en revisión ocupa sitio para que nadie reporte dos veces la misma
    transferencia. El pronto pago se aplica al reservar y **caduca**: si llega la fecha de
    corte sin liquidar se retira y el total sube (`RN-04`, `CU-STD-023` A1). Lo hace
    `servicios/pagos.py::caducar_pronto_pago`; mientras no exista la barrida diaria hay que
    llamarlo desde el cron con `manage.py caducar_pronto_pago --todas`.

  - **La configuración de la convocatoria** (CU-STD-034, vista A10): precios, plazos, el
    descuento de pronto pago y los datos bancarios, en
    `/f/<slug>/stands/<id>/configuracion/`. Es de quien **administra la feria**, no del
    equipo técnico — el `/f/<slug>/django-admin/` sigue sirviendo la misma fila, pero solo
    porque ahí vive también la importación del mapa, que es del operador (`ADR-0005`).

  **El flujo del expositor es una secuencia, no un menú** (`RN-23`): solicitud → revisión →
  espacios → confirmación → cuenta. La puerta del módulo es `stands:inicio` —a donde apunta
  el catálogo (`ADR-0006`)— y no una pantalla: `views.paso_actual()` mira en qué paso va cada
  quien y lo manda ahí, de modo que una solicitud aceptada entra al mapa y una reserva viva
  entra a su cuenta. La misma función alimenta la barra de pasos (`templatetags/flujo.py`),
  para que la barra no pueda marcar un paso distinto del que se está viendo. **Una editorial
  lleva una sola reserva viva por convocatoria**, y lo sostiene un índice único parcial sobre
  `registro`, no solo el servicio.

  > [!warning] `Solicitud` tiene **dos** conjuntos de estados y significan cosas distintas
  > `VIVOS` es «esperando dictamen» (`pendiente`, `cambios_solicitados`): lo que cuenta la cola
  > de A1 y lo que enseña la pantalla del aplicante. `OCUPAN_EL_REGISTRO` son esos dos **más
  > `aceptada`**: lo que impide enviar otra solicitud, y lo que sostienen a la vez
  > `enviar_solicitud` y el índice `una_solicitud_en_juego_por_registro`.
  >
  > Usar `VIVOS` para lo segundo fue un error real hasta el 2026-08-30: un expositor ya
  > aceptado podía mandar otra solicitud, y rechazársela **no le quitaba** la habilitación para
  > reservar, porque `RN-16` la lee de la aceptada. Volver a aplicar es lo que `RN-22` abre tras
  > un **rechazo**, no tras entrar.

  - **La validación de los pagos** (CU-STD-018, vista A5): la cola de
    `/f/<slug>/stands/<id>/pagos/`, transversal a todas las reservas de la convocatoria, y el
    detalle de un abono en un modal que trae htmx —la misma vista sirve la pantalla suelta sin
    JavaScript, como el detalle de un espacio—. Es lo que cierra el ciclo del dinero: hasta que
    existió, un abono nacía `pendiente_validacion` y **no había ningún camino** para darlo por
    bueno, así que `RN-13` y `RN-14` eran código muerto.

  - **El expediente de una reserva** (CU-STD-029, vista A4): `/f/<slug>/stands/reserva/<id>/`
    no es una ficha de consulta sino la **vista contenedor** que el caso de uso describe. De
    ahí cuelgan el historial de abonos —con el mismo modal de A5, que devuelve aquí porque
    `CU-STD-018` tiene dos puertas—, el **abono manual** (CU-STD-019) y el **descuento
    especial** (CU-STD-020), que se aplica o se retira pero nunca las dos cosas (`RN-05`).

    Dos cosas que no se deducen del código: un abono manual **nace `validado`** y mueve el
    saldo en el acto (`CU-STD-019` paso 6) — lo asienta quien coteja contra el banco, así que
    no tiene a quién esperar—; y el tope de «lo que ya reportaste ocupa sitio» **no le aplica**,
    porque quien administra es quien resuelve esa cola.

    > [!warning] Un descuento solo se mueve en una reserva viva
    > Las dos funciones que tocan el especial son las únicas del dominio que reescriben
    > `monto_total` (`RN-01`), y sobre una `cancelada` no hay nada que descontar: el importe
    > pasa a ser el registro de lo que esa reserva costó. Lo comprueba
    > `pagos.py::_exigir_reserva_viva`, que además bloquea la fila. La guarda vivía solo en la
    > plantilla de A4 hasta el 2026-08-30, y como la vista despacha la acción sin volver a
    > preguntar, un POST le reescribía el total a una reserva cerrada sin que nada protestara.

    > [!warning] Cualquier cambio de descuento recalcula sobre una instancia recién traída
    > `_recalcular_total` lee los descuentos con `reserva.descuentos.all()`. Quien llega desde
    > una pantalla trae `prefetch_related("descuentos")`, y esa caché se llenó **antes** de
    > insertar o borrar la fila: el total salía idéntico, el descuento quedaba guardado y no
    > descontaba nada. Las tres funciones que tocan descuentos lo hacen por eso.

  - **Los dos umbrales avisan** (CU-STD-026, 027): al cubrirse el anticipo y al liquidar sale
    un correo y queda su `Notificacion`, que A4 enseña. Dos cosas que no se ven en el código:

    > [!warning] El correo se programa con `transaction.on_commit`, no se manda
    > `reevaluar` corre **siempre** dentro de una transacción —validar un abono, asentar uno
    > manual, mover un descuento— y un correo no se puede deshacer. Mandarlo ahí significa que
    > un rollback posterior deja a la editorial con el aviso de una confirmación que no
    > ocurrió, y sin la `Notificacion` que lo explique, porque se va con el rollback. Es la
    > misma razón por la que el dictamen avisa fuera de su transacción; aquí no se puede sacar
    > al llamador porque `reevaluar` tiene cuatro puertas. **En pruebas hay que envolver con
    > `django_capture_on_commit_callbacks(execute=True)`, dentro del `schema_context`.**

    > [!warning] La edición no se saca de `connection.tenant`
    > En una petición ahí está la `Feria` de verdad. Dentro de un `schema_context` —un comando
    > de `manage.py`, la barrida diaria, las pruebas— hay un `FakeTenant` que solo sabe su
    > `schema_name` y revienta al pedirle el `slug`, y estos correos salen justo de ahí.
    > `avisos.py` la busca por `schema_name`. Y todo enlace de correo lleva `URL_BASE` delante:
    > un `/f/2027/...` suelto no es una dirección dentro de un cliente de correo.

    La **fecha de corte** ya se hereda: vive como base en `ConfiguracionSistema` y cada reserva
    se queda con la suya al confirmarse (`CU-STD-026` paso 4, `RN-13`). Confirmar no pisa una
    que se haya ajustado a mano.

  - **El reloj** (CU-STD-022, 023 A1, 024, 025): `manage.py barrida_diaria`, que corre una vez
    al día desde `.github/workflows/barrida-diaria.yml`. Hace **dos cosas y en este orden**:
    retira los pronto pago vencidos —lo que **sube** el total y con él el anticipo— y después
    avisa de las reservas cuyo plazo se agotó, a la editorial (`025`) y a cada persona que
    administra la feria (`024`). Al revés, el aviso saldría con cifras de antes.

    > [!warning] La barrida **no escribe en `Reserva`**
    > `RN-12`: vencer no libera nada. Lo único que escribe son `Notificacion`; cancelar o
    > prorrogar es una decisión de una persona (`CU-STD-035`). Una barrida que «limpia»
    > vencidas liberaría espacios que nadie decidió liberar, de madrugada y sin testigos.

    > [!note] Se avisa una vez por **vencimiento**, no por reserva
    > La pregunta que hace `servicios/vencimientos.py` es si ya salió un aviso *posterior a la
    > fecha de vencimiento vigente*. Así una prórroga (`CU-STD-035`) que también se agota
    > vuelve a avisar sin tener que borrar nada, y un aviso `fallida` se reintenta al día
    > siguiente (`CU-STD-024` E1).

  - **Resolver una reserva** (CU-STD-035, 036): prorrogar el plazo del anticipo, mover el
    corte del pago total y **cancelar**, en el bloque «Plazos y estado» de A4.
    `servicios/reservas.py::cancelar` es la **única función del dominio que devuelve stands a
    `disponible`** (`RN-11`): ni la barrida ni ningún umbral llegan ahí. Deja escrito quién,
    cuándo y por qué en la propia fila, avisa a la editorial y **no toca los abonos** — el
    dinero entró de verdad y qué se hace con él se acuerda fuera del sistema. Prorrogar solo
    admite fechas futuras: una pasada dejaría la reserva vencida el mismo día y la barrida
    volvería a avisar mañana.

  - **Los expositores** (CU-STD-030, 031, vistas A6 y A7): la lista de quién está habilitado
    para reservar y su expediente. **A7 enseña la ficha viva, no la fotografía** — A2 juzga lo
    que se envió (`RN-22`), A7 atiende a un cliente hoy—, y su alcance es **la feria y no la
    convocatoria** (`RN-19`, `RN-21`): la misma editorial puede haber aplicado a la general y
    a la de un pabellón. Por eso su URL no lleva convocatoria, como el detalle de una
    solicitud o de una reserva.

    > [!warning] El RFC no existe como columna
    > `CU-STD-031` paso 2 lo pide junto a la razón social. La ficha en papel **no lo pide como
    > dato, lo pide como archivo**: viene dentro de la constancia de situación fiscal. A6 y A7
    > enlazan la constancia y lo dicen; buscar por RFC o facturar sin abrir el PDF exige
    > añadirlo a la ficha de U1, y eso lo manda el documento oficial.

  - **La bitácora** (`BitacoraSTD`, modelo de datos §3.12): una línea de tiempo de las
    acciones de administración, **partida por convocatoria** — una feria puede tener la
    general y la de un pabellón (`RN-19`), y son dos ventas distintas—. **Su pantalla es
    `/f/<slug>/django-admin/`** y no una del panel —se consulta tres veces al año y cuando
    algo no cuadra—, en solo lectura y con la convocatoria como primer filtro.

    No sustituye al rastro de cada fila (`Movimiento.validado_por`, `Reserva.cancelada_por`):
    contesta «¿qué pasó con esta convocatoria el martes?». Doce acciones, de las que **cinco
    no dejan rastro en ninguna otra parte** porque borran una fila o sobreescriben una fecha:
    retirar un descuento, caducar un pronto pago, prorrogar, mover el corte e importar un
    mapa. **No entra lo del aplicante** —solicitar, reportar un abono, reservar—: ya se ve en
    su cola, y anotarlo llenaría la línea de ruido.

    > [!note] `convocatoria` se guarda al anotar, no se deduce al leer
    > Sale del objeto por una tabla explícita de cinco entradas en `servicios/bitacora.py`.
    > Adivinar recorriendo relaciones sería un `getattr` en cadena que falla en silencio, y
    > una entrada sin convocatoria queda fuera de todos los filtros sin que nada lo señale.

    > [!note] Se anota dentro de la transacción, y anotar nunca tumba la acción
    > Al revés que el correo, que va con `on_commit` porque no se puede deshacer: una anotación
    > sí, y una que sobreviviera a un rollback diría que pasó algo que no pasó. Si la escritura
    > falla, se registra en el log y se traga — perder una línea de historial es mejor que
    > revertir un cobro que el banco ya respaldó.

  **Falta solo la pantalla A9 de CU-STD-033** (corregir un espacio del mapa), que hoy se hace
  desde `/f/<slug>/django-admin/`. Con ella entraría también la décima acción de la bitácora:
  `importar` no recibe hoy quién lo hace, y firmar la entrada como «el sistema» sería mentira.
- **Construido a medias:** `EVT` (Eventos) — `apps/eventos/` tiene la **captura de una
  propuesta** (`CU-EVT-002`): los modelos de la etapa 1 completos, el formulario de los ocho
  tipos, la pantalla y el acuse por correo. Las ocho tablas de tipo cuelgan de una tabla padre
  con herencia multitabla, no de un `detalle_id` suelto (`ADR-0009`). **Falta todo lo demás**:
  consultar las propuestas propias (`CU-EVT-003`), editarlas tras una petición de cambios, y el
  panel del administrador entero —listado, dictamen, notificación en lote—, así que el módulo
  se inscribe en `ADR-0006` **sin `url_panel`**.
- **Solo documentado:** `TAL`, `VIS`, `PRG`, `SAL` — ver `docs/requisitos/`.
- **Solo en prototipo:** las pantallas de `REG`, `EVT` y `VIS` bajo `prototipo/`. **`STD` no
  tiene prototipo**: su especificación visual es la Ficha de Registro en papel
  (`docs/soporte/documentos proporcionados por FILEY/Material para Registro de Actividades
  FILEY 2027/Registro-para-Expositores-FILEY-2026.pdf`), que manda sobre las tablas abreviadas
  de `docs/requisitos/`.

## Comandos

```bash
cd filey && python manage.py check && python manage.py runserver
cd filey && pytest                  # las pruebas viven en apps/<dom>/pruebas/, no en tests.py
cd filey && python manage.py migrate_schemas        # migra `public` Y cada feria
cd filey && python manage.py alta_feria --help      # crear una feria por consola (CU-FER-001)
cd filey && python manage.py barrida_diaria --todas               # el reloj del dominio (fase 6)
cd filey && python manage.py caducar_pronto_pago --todas --seco   # RN-04: qué reservas lo pierden hoy
./prototipo/scripts/gen-inventario.sh   # reindexa el inventario CSS tras tocar un styles.css
./prototipo/scripts/check-ui.sh         # verifica el prototipo (E1/E2/E3 rompen; W1/W2/W4 con trinquete)
./prototipo/scripts/preview-vis.sh      # sirve prototipo/ por HTTP (los JSON de VIS usan fetch)
./prototipo/scripts/sync-proto.sh pull  # trae prototipo/ de main sin tocar STD (o `push`)
```

> [!warning] Una feria recién creada no la ve nadie de fuera
> Nace `en_preparacion`, y el participante solo ve las `activa` (CU-FER-010). Hay que activarla
> desde `/django-admin/`. Como la pantalla de elegir feria se salta cuando hay una sola activa,
> el síntoma de olvidarlo no es una tarjeta de menos: es que al entrar dice que no hay ninguna
> edición abierta.

> [!note] Todo el correo sale por `django.core.mail`
> Resend está detrás de un backend de correo (`apps/notificaciones/backends.py`), así que quién
> entrega lo decide `EMAIL_BACKEND`. En pruebas Django lo sustituye por `locmem`: ninguna prueba
> puede salir a la red aunque haya `RESEND_API_KEY` en el entorno. Si escribes un envío nuevo,
> hazlo con `EmailMultiAlternatives`, nunca llamando a Resend directamente.

> [!note] El chasis de las pantallas está en `plantillas/componentes/`
> La barra superior no se incluye a mano: la dibuja `{% topbar %}`
> (`apps/ferias/templatetags/chasis.py`), que decide sus tres variantes —anónimo, participante,
> administrador— y resuelve sus enlaces contra el urlconf público. Una pantalla nueva extiende
> `layouts/panel.html` y no vuelve a maquetarla. Para enlazar fuera de la feria desde cualquier
> otra plantilla está `{% load enlaces %}{% url_publica '...' %}`.

<!-- -->

> [!warning] Dos trampas del aislamiento por feria
> **`Feria.objects` incluye una fila que no es una feria.** `django-tenants` exige un tenant con
> `schema_name="public"` para servir todo lo que no cuelga de `/f/<slug>/`. Cualquier listado de
> ferias usa **`Feria.reales`**; con `objects` sale una feria fantasma en pantalla.
>
> **Dentro de `/f/<slug>/` el urlconf activo es `config/urls_feria.py`**, así que
> `reverse("registros:acceso")` falla ahí: ese nombre vive en el urlconf público. Para enlazar
> de una feria hacia fuera está `comun.urls.url_publica()` en Python y `{% url_publica %}` en
> plantillas. El acceso es global —la cuenta no pertenece a ninguna feria— y su URL no debe
> llevar prefijo de edición. Vale también para `plantillas/403.html`, que se pinta **dentro** de
> una feria cuando `requiere_dueno_feria` rechaza a alguien.
>
> `apps/ferias` tiene un urlconf a cada lado de esa frontera y **dos namespaces distintos**, a
> propósito: `ferias:` (`urls.py`) solo resuelve fuera de toda feria y `accesos:`
> (`urls_accesos.py`) solo dentro. Con un namespace compartido, el mismo prefijo significaría
> cosas distintas según el urlconf activo.

> [!warning] Hay **dos** sitios de admin de Django, y el modelo va en uno solo
> `/django-admin/` corre sobre `public` y sirve lo de `SHARED_APPS` (`Feria`, `AdminFeria`,
> `Persona`). `/f/<slug>/django-admin/` corre sobre el schema de la edición y sirve lo de
> `TENANT_APPS`; lo dibuja `comun/admin_feria.py::admin_feria`, que es otro `AdminSite`, no el
> de siempre.
>
> La regla es mecánica: **una app de `TENANT_APPS` registra en `admin_feria`; una de
> `SHARED_APPS`, en `admin.site`.** Equivocarse **no falla al arrancar** —el `check` pasa y la
> entrada se ve bien en el índice—: revienta con `relation "..." does not exist` la primera vez
> que alguien abre la pantalla, porque esa tabla no existe en `public`.
>
> El alta de convocatorias vive hoy ahí (CU-FER-005, provisional). Con eso el actor es el equipo
> técnico (`is_staff`) y no el dueño de la feria: la desviación está anotada en el caso de uso y
> se cierra cuando exista la pantalla del panel.

> [!warning] La caché por defecto no vale para producción
> El límite por IP de `comun/limites.py` cuenta en la caché. Con `LocMemCache` cada worker lleva
> su cuenta y el límite se multiplica por el número de procesos. `manage.py check --deploy` lo
> rechaza (`comun.E001`): en producción hay que configurar `REDIS_URL`.
