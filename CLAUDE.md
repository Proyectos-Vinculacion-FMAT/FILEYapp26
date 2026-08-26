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
| Elegir color, tipografía, radio, tono, o cuántos pasos/campos lleva una pantalla | `filey-identidad` |
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
   `requiere_dueno_feria`). El middleware de feria **no comprueba permisos** —corre antes de
   `AuthenticationMiddleware`, así que no hay `request.user`—: solo fija el schema.
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
6. **Toda pantalla funciona sin JavaScript**, y **nada se carga de un CDN**.
7. Nombres en español, consistentes, tanto en código como en rutas de archivo. Sin eñes en
   identificadores ni nombres de columna (`es_dueno`, `contrasena`): la eñe arrastra
   fricción de codificación en cada herramienta que toque la base.

## Estado actual

- **Construido:** `REG` (Core Registros) — acceso por OTP de participante y de administrador,
  y alta de cuenta. `apps/registros/` es la app de referencia; `apps/notificaciones/` encapsula
  el envío de correo (Resend). `REG` acaba en cuanto hay sesión: lo que se ve después es de
  `FER`.
- **Construido:** `FER` (Core Ferias) — `apps/ferias/` (capa `public`: `Feria`, `AdminFeria`,
  el alta desde `/django-admin/` y las dos pantallas de elegir feria) y `apps/convocatorias/`
  (capa por feria: `Convocatoria` y su catálogo, que es la portada de `/f/<slug>/`). Falta el
  CRUD de convocatorias, `RegistroConvocatoria` y `BitacoraFER`.
- **Solo documentado:** `EVT`, `TAL`, `STD`, `VIS`, `PRG`, `SAL` — ver `docs/requisitos/`.
  Ningún panel de módulo está conectado todavía.
- **Solo en prototipo:** las pantallas de `REG`, `EVT` y `VIS` bajo `prototipo/`.

## Comandos

```bash
cd filey && python manage.py check && python manage.py runserver
cd filey && pytest                  # las pruebas viven en apps/<dom>/pruebas/, no en tests.py
cd filey && python manage.py migrate_schemas        # migra `public` Y cada feria
cd filey && python manage.py alta_feria --help      # crear una feria por consola (CU-FER-001)
./scripts/gen-inventario.sh         # reindexa el inventario CSS tras tocar un styles.css
./scripts/check-ui.sh               # verifica el prototipo (E1/E2/E3 rompen; W1/W2/W4 con trinquete)
./scripts/preview-vis.sh            # sirve prototipo/ por HTTP (los JSON de VIS usan fetch)
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
> llevar prefijo de edición.

> [!warning] La caché por defecto no vale para producción
> El límite por IP de `comun/limites.py` cuenta en la caché. Con `LocMemCache` cada worker lleva
> su cuenta y el límite se multiplica por el número de procesos. `manage.py check --deploy` lo
> rechaza (`comun.E001`): en producción hay que configurar `REDIS_URL`.
