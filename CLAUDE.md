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
   hay JWT, ni tokens en el cliente, ni CORS. Ningún módulo implementa su propia autenticación:
   importa los decoradores de `apps/registros/permisos.py`.
3. **Capas por app:** `models.py` (datos e invariantes, modelos gordos) → `services/` (reglas de
   negocio) → `views.py` (traduce HTTP ↔ servicio, vistas delgadas) → plantillas.
   Si una regla no se puede llamar desde un comando de `manage.py` sin pasar por HTTP, está en
   el lugar equivocado: va a `services/`.
4. **Las dependencias van en una sola dirección.** Los dominios verticales (`eventos`,
   `talleres`, `stands`, `visitas`) importan de `registros` —que es la base de identidad—,
   nunca al revés, y nunca en círculo entre hermanos.
5. **Toda pantalla funciona sin JavaScript**, y **nada se carga de un CDN**.
6. Nombres en español, consistentes, tanto en código como en rutas de archivo.

## Estado actual

- **Construido:** `REG` (Core Registros) — acceso por OTP de participante y de administrador,
  alta de cuenta, convocatorias y selección de módulo. `apps/registros/` es la app de
  referencia; `apps/notificaciones/` encapsula el envío de correo (Resend).
- **Solo documentado:** `EVT`, `TAL`, `STD`, `VIS`, `PRG`, `SAL` — ver `docs/requisitos/`.
  Ningún panel de módulo está conectado todavía.
- **Solo en prototipo:** las pantallas de `REG`, `EVT` y `VIS` bajo `prototipo/`.

## Comandos

```bash
cd filey && python manage.py check && python manage.py runserver
cd filey && pytest                  # las pruebas viven en apps/<dom>/pruebas/, no en tests.py
./scripts/gen-inventario.sh         # reindexa el inventario CSS tras tocar un styles.css
./scripts/check-ui.sh               # verifica el prototipo (E1/E2/E3 rompen; W1/W2/W4 con trinquete)
./scripts/preview-vis.sh            # sirve prototipo/ por HTTP (los JSON de VIS usan fetch)
```

> [!note] Todo el correo sale por `django.core.mail`
> Resend está detrás de un backend de correo (`apps/notificaciones/backends.py`), así que quién
> entrega lo decide `EMAIL_BACKEND`. En pruebas Django lo sustituye por `locmem`: ninguna prueba
> puede salir a la red aunque haya `RESEND_API_KEY` en el entorno. Si escribes un envío nuevo,
> hazlo con `EmailMultiAlternatives`, nunca llamando a Resend directamente.

> [!warning] La caché por defecto no vale para producción
> El límite por IP de `comun/limites.py` cuenta en la caché. Con `LocMemCache` cada worker lleva
> su cuenta y el límite se multiplica por el número de procesos. `manage.py check --deploy` lo
> rechaza (`comun.E001`): en producción hay que configurar `REDIS_URL`.
