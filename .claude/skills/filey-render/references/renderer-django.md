# Renderizador Django — `filey/`

Verificado contra el código real de esta rama al 2026-08-28. `REG` (Core Registros) y `FER`
(Core Ferias) están construidos y con pruebas. `EVT`, `TAL`, `STD`, `VIS`, `PRG`, `SAL` todavía
no existen como código, solo como especificación en `docs/requisitos/`.

> [!warning] "El código vive en la rama X" ya no es una frase segura en este repo
> `main` y `feature/registro-otp` tienen **dos** copias de `filey/` que divergieron: esta
> siguió (Core Ferias, multi-tenant, `pais`/nombre en tres campos), la otra se quedó en la
> versión previa a todo eso. Lo que sigue describe **el `filey/` de esta rama**, no asume que
> aplique en otra. Antes de citar esta referencia fuera de aquí, confirma en cuál estás.

## Arrancar

```bash
cd filey
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env          # editar antes de usar — DATABASE_URL es obligatorio, ver abajo
python manage.py migrate_schemas    # migra `public` Y cada feria; migrate normal no alcanza
python manage.py runserver
```

Dependencias de ejecución: `Django>=5.2,<6`, `django-tenants`, `python-dotenv`, `whitenoise`.
**Sin DRF, sin SimpleJWT, sin corsheaders** — se retiraron con la API REST (ADR-0002) y no
vuelven sin un ADR que lo autorice. Hay un `uv.lock` en `filey/`, pero `pyproject.toml` es
explícito: las dependencias no se declaran ahí, viven en `requirements*.txt`.

Comandos propios: `python manage.py alta_admin`, `python manage.py alta_feria` (crea una
feria por consola, CU-FER-001), `python manage.py probar_correo <destino>`.

## Decisiones ya tomadas en `config/settings.py`

| Ajuste | Valor | Por qué |
| --- | --- | --- |
| `DEBUG` | `false` por defecto | Un despliegue que olvide la variable no queda filtrando trazas |
| `SECRET_KEY` | aborta el arranque si es la de ejemplo y `DEBUG=False` | Firma las cookies de sesión |
| `AUTH_USER_MODEL` | `registros.Persona` | Usuario propio del dominio |
| `TEMPLATES` | `DIRS=[plantillas]` **y** `APP_DIRS=True` | Esqueleto compartido + pantallas por app |
| `STATIC_URL` / `STATICFILES_DIRS` | `estaticos/` | Nombres en español, consistentes |
| `STATIC_ROOT` | `estaticos_recolectados/` | Salida de `collectstatic` |
| staticfiles storage | WhiteNoise comprimido con manifest si no hay `DEBUG` | Cache-busting por hash; despliegue de un solo proceso |
| Sesión | 12 h desde la última actividad, cookie `HttpOnly`, `SameSite=Lax` | Reemplaza al JWT en localStorage |
| `LANGUAGE_CODE` / `TIME_ZONE` | `es-mx` / `America/Merida` | Horarios de sala y cortes son locales |
| Base de datos | **PostgreSQL, obligatorio, también en desarrollo** | `django-tenants` necesita schemas; el arranque **aborta** si `DATABASE_URL` no apunta a Postgres — ver ADR-0003 |
| `DATABASE_ROUTERS` | `django_tenants.routers.TenantSyncRouter` | Decide `public` vs. schema de feria según `SHARED_APPS`/`TENANT_APPS` |
| Caché | `LocMemCache` en desarrollo | Solo desarrollo — ver la advertencia de abajo |

Parámetros de negocio que viven en settings (no los hardcodees en el código):
`OTP_VIGENCIA_MINUTOS`, `OTP_INTENTOS_MAX`, `OTP_REENVIO_COOLDOWN_SEG`,
`OTP_VENTANA_MINUTOS`, `OTP_EMISIONES_MAX_VENTANA`, `OTP_FALLOS_MAX_VENTANA`,
`OTP_LOCKOUT_MINUTOS`, `LIMITES_PETICIONES`, `ADMIN_PISO_IDENTIFICAR_SEG`,
`ADMIN_PISO_OTP_SEG`, `URL_BASE`.

> [!warning] Antes de desplegar
> Con varios workers, `LocMemCache` parte en pedazos el límite por IP (`comun/limites.py`) y
> el estado señuelo del acceso administrativo (`services/senuelo.py`): cada proceso lleva su
> cuenta y el límite efectivo se multiplica. `manage.py check --deploy` lo rechaza
> (`comun.E001`) — hace falta `REDIS_URL` en producción.

## Multi-tenant: una feria, un schema (ADR-0003)

Cada feria vive en su propio schema de PostgreSQL, vía `django-tenants`. Esto no es un detalle
de infraestructura — cambia cómo se escribe cualquier app nueva:

- **La feria es el contexto de la conexión, no una columna.** Ninguna tabla de contenido lleva
  `feria_id` ni ninguna consulta filtra por feria a mano; el `search_path` de Postgres ya
  resuelve eso. Una app va en `SHARED_APPS` (schema `public`, una sola copia — `registros`,
  `ferias`) o en `TENANT_APPS` (un schema por feria — `convocatorias`, y ahí irán `eventos`,
  `talleres`, `stands`, `visitas` conforme se construyan). Una app en las dos duplica sus
  tablas en todos los schemas.
- **`TenantSubfolderMiddleware` corre antes que `AuthenticationMiddleware`.** Solo fija el
  schema según el prefijo `/f/<slug>/`; cuando corre no existe `request.user` todavía, así que
  **no puede comprobar permisos**. Eso lo hace `apps/ferias/permisos.py` después.
- **`Feria.objects` incluye una fila que no es una feria**: `django-tenants` exige un tenant
  `schema_name="public"` para servir todo lo que no cuelga de `/f/<slug>/`. Cualquier listado
  de ferias reales usa `Feria.reales`.
- **`manage.py migrate` no basta.** Hay que usar `migrate_schemas`, que migra `public` y cada
  schema de feria.

## Mapa de URLs vigente

Dos urlconfs, no uno — `django-tenants` decide cuál según si la petición cae dentro de
`/f/<slug>/`:

```text
config/urls_publicas.py   PUBLIC_SCHEMA_URLCONF — fuera de toda feria
config/urls_feria.py      ROOT_URLCONF — dentro de /f/<slug>/, django-tenants antepone el prefijo
```

```text
Fuera de una feria (urls_publicas.py):
  /django-admin/             admin interno de Django — también donde se da de alta una feria (CU-FER-001)
  /acceso, /acceso/registro, /acceso/codigo, /acceso/codigo/reenviar    participante (registros:)
  /admin/acceso, /admin/acceso/codigo, /admin/acceso/codigo/reenviar   administrador (registros:)
  /salir                     común (registros:)
  /ferias                    elegir feria — participante, CU-FER-010 (ferias:elegir)
  /admin/ferias              elegir feria — administrador, CU-FER-002 (ferias:mis_ferias)

Dentro de una feria (urls_feria.py, prefijo /f/<slug>/ puesto por django-tenants):
  /f/<slug>/                 catálogo de convocatorias — portada de la feria (convocatorias:catalogo)
  /f/<slug>/accesos/         panel de accesos de esta feria (accesos:panel)
  /f/<slug>/accesos/<id>/retirar/   retirar un administrador (accesos:retirar)
```

`registros:` y `ferias:` solo resuelven **fuera** de toda feria; `accesos:` y
`convocatorias:` solo **dentro**. Enlazar de una plantilla de feria hacia fuera (p. ej. al
login) necesita `{% load enlaces %}{% url_publica 'registros:acceso' %}`, no un `{% url %}`
normal — ver `comun/urls.py`.

> [!danger] `urls_feria.py` necesita declarar los cuatro `handler4xx`/`handler5xx` de fábrica
> `django-tenants` no monta ese módulo tal cual: lo envuelve en algo que resuelve atributos por
> `import_string`, y ante un atributo que no existe lanza `ImportError` **en vez de** devolver
> `None` (que es lo que Django espera al preguntar `getattr(urlconf, "handler500", None)`). Sin
> los cuatro declarados explícitamente, cualquier error dentro de una feria pierde su traza
> real: el log solo dice `ImportError: Module "config.urls_feria" does not define a
> "handler500"`. Ya están declarados — si agregas un urlconf nuevo bajo `/f/<slug>/`, cuida que
> siga siendo así.

## Añadir un dominio de contenido (EVT, TAL, STD, VIS…)

Los puntos de enganche ya existen; un módulo nuevo **no inventa** identidad, sesión, permisos,
aislamiento por feria ni maquetación.

1. `filey/apps/<dominio>/` con las capas de la sección 2 del SKILL.
2. Va en `TENANT_APPS` (contenido de una edición, no global) y se registra en `settings.py`.
3. Se monta en `config/urls_feria.py`, sin el prefijo `f/<slug>/` — lo antepone
   `django-tenants`.
4. Protege las vistas con `@requiere_admin_feria` / `@requiere_dueno_feria`
   (`apps/ferias/permisos.py`) para lo administrativo dentro de la feria, o
   `@requiere_participante` (`apps/registros/permisos.py`) para lo del participante. **No
   existe ya** un permiso por módulo (`requiere_modulo`) ni `RolPermiso`: el acceso
   administrativo es por feria completa, no por módulo — ver la nota en
   `apps/registros/permisos.py` y ADR-0004.
5. Las pantallas extienden `plantillas/layouts/panel.html`.
6. No hay ya un `apps/registros/catalogo.py` que declare a mano qué convocatorias mostrar: el
   catálogo de una feria lo sirve `apps.convocatorias`, y un dominio nuevo se integra ahí
   cuando tenga su propio modelo de convocatoria — no reescribiendo `registros`.

## Nomenclatura

Todo en español, incluidos los nombres de carpeta de Django. Sin eñes en identificadores ni
nombres de columna (`es_dueno`, no `es_dueño`).

| Cosa | Convención | Ejemplo |
| --- | --- | --- |
| Pantalla | `apps/<dom>/templates/<dom>/<pantalla>.html` | `registros/codigo.html` |
| Fragmento htmx | dentro de `parciales/` | `registros/parciales/estado_otp.html` |
| Layout compartido | `plantillas/layouts/` | `layouts/panel.html` |
| Nombre de URL | **snake_case**, con namespace de app | `{% url 'ferias:mis_ferias' %}`, `{% url 'accesos:panel' %}` |
| App | nombre del dominio en plural, español | `apps/registros/`, `apps/ferias/` |
| Pruebas | `apps/<dom>/pruebas/test_*.py` | `pruebas/test_otp.py` |
| Servicio | `apps/<dom>/services/<área>.py` o `servicios/<área>.py` (`ferias` usa el nombre español) | `services/otp.py`, `servicios/seleccion.py` |

Las vistas son funciones, no clases. Reciben `peticion`, no `request`.

## El chasis: `{% topbar %}`, no maquetación a mano

`plantillas/componentes/topbar.html` es la barra superior compartida, y la dibuja el
*inclusion tag* `{% topbar %}` de `apps/ferias/templatetags/chasis.py` — no un `{% include %}`
directo. Es un inclusion tag y no un context processor a propósito: un context processor
cobraría sus consultas en **toda** plantilla, incluidas las de acceso que no dibujan barra; así
solo paga quien la pinta. Resuelve tres variantes (anónimo, participante, administrador) leyendo
`apps/ferias/permisos.py` y `apps/ferias/servicios/seleccion.py`, y sus enlaces salen contra el
urlconf público. Una pantalla nueva extiende `layouts/panel.html` y no vuelve a maquetar esto.

## Autenticación: OTP para todos

No hay contraseñas de login para nadie. Participantes y administrativos entran por código de un
solo uso enviado por correo (CU-REG-002, CU-REG-003). La sesión la abre
`apps/registros/services/sesion.py` tras validar el código.

Si el correo no está configurado en `.env`, Django cae al backend de consola y el OTP se
imprime en la terminal. El `runserver` avisa con un recuadro en stderr, porque esa caída
silenciosa es la causa número uno de "el OTP no llega". En pruebas, `EMAIL_BACKEND` cambia a
`locmem`: ninguna prueba sale a la red aunque haya `RESEND_API_KEY` en el entorno — el correo
real en producción sale por Resend, detrás de `apps/notificaciones/backends.py`.

Defensas ya implementadas, no las reinventes:

- `comun/limites.py` — límite por IP (sustituye al throttling de DRF).
- `apps/registros/services/otp.py` — límites por cuenta destino: emisiones por ventana, lockout
  por fallos.
- `apps/registros/services/senuelo.py` — el acceso admin responde igual exista o no el correo
  (aunque ver la nota de abajo: esto se relajó parcialmente el 2026-08-19), y las respuestas se
  retienen hasta un piso de tiempo para que la latencia tampoco delate quién es administrador.

> [!note] El señuelo del login admin ya no es 100% indistinguible
> Un cambio del 2026-08-19 hizo que pedir un código con un correo que no es admin responda
> "Correo incorrecto" explícito, en vez de comportarse igual que un correo admin válido. Antes
> de asumir que el acceso admin no revela nada, confirma el estado actual de
> `apps/registros/views.py::admin_acceso`.

## Trampas verificadas

- **`{# … #}` es de una sola línea.** Multilínea se imprime en el HTML; usa `{% comment %}`.
- **`{% block %}` dentro de un `{% include %}` no es sobrescribible** por la plantilla que
  incluye. Los partials reciben datos por contexto o por `{% include ... with %}`.
- **htmx no sigue un 302**: reemplazaría el fragmento con la página entera. Usa
  `comun.htmx.redirigir`, que responde 204 + `HX-Redirect`.
- **`filey.js` debe cargarse antes que Alpine**: registra los componentes en `alpine:init`.
- **El CSRF de htmx** va una sola vez, en el `<body hx-headers=…>` de `base.html`. No lo
  repitas por formulario.
- **`reverse()`/`{% url %}` sin calificar, dentro de una feria, resuelve contra el urlconf
  equivocado.** Usa `url_publica()` / `{% url_publica %}` para salir del prefijo — ver arriba.
- **`Feria.objects` trae una fila fantasma.** Usa `Feria.reales` para cualquier listado visible.
- **Gmail solo deja enviar como la cuenta autenticada.** Un `DEFAULT_FROM_EMAIL` de otro
  dominio falla SPF/DMARC y acaba en spam; settings lo reescribe solo.
- **Puerto SMTP**: 587 es STARTTLS y 465 es SSL directo. Cruzarlos cuelga la conexión.

## Qué falta decidir

- Caché compartida (Redis) para producción — bloqueada por `manage.py check --deploy`.
- **ADR-0002 se cita en el código pero el archivo no está en `docs/adr/`** (solo hay
  `0000-template`, `0001`, `0003`, `0004` y el README). Conviene escribirlo o corregir las
  referencias.
- Falta el CRUD de convocatorias, `RegistroConvocatoria`, la transferencia de propiedad de una
  feria y `BitacoraFER` (ver "Estado actual" en `CLAUDE.md`).
- Portar los módulos verticales (`EVT`, `TAL`, `STD`, `VIS`, `PRG`, `SAL`). El prototipo sigue
  siendo la especificación visual.
- Reconciliar `filey/estaticos/css/filey.css` con las capas del prototipo (ver sección 6
  del SKILL).
