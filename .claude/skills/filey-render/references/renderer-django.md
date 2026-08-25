# Renderizador Django — `filey/`

Estado al 2026-08-11: **implementación real, no andamiaje.** El Core de Registros
(`apps/registros/`) está construido y con pruebas: alta de cuenta, acceso por OTP para
participantes y administrativos, roles por módulo. `EVT`, `TAL`, `STD` y `VIS` todavía no
existen como código, solo como especificación en `docs/requisitos/`.

El código vive en la rama `feature/registro-otp`. Antes de trabajar sobre él, lee su
`CLAUDE.md` y `docs/adr/`: mandan sobre este archivo.

## Arrancar

```bash
cd filey
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env          # editar antes de usar
python manage.py migrate
python manage.py runserver
```

Dependencias de ejecución: `Django>=5.2,<6`, `python-dotenv`, `whitenoise`.
**Sin DRF, sin SimpleJWT, sin corsheaders** — se retiraron con la API REST (ADR-0002) y no
vuelven sin un ADR que lo autorice.

Comandos propios: `python manage.py alta_admin`, `python manage.py probar_correo <destino>`.

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
| Base de datos | SQLite | Solo desarrollo |
| Caché | `LocMemCache` | Solo desarrollo — ver la advertencia de abajo |

Parámetros de negocio que viven en settings (no los hardcodees en el código):
`OTP_VIGENCIA_MINUTOS`, `OTP_INTENTOS_MAX`, `OTP_REENVIO_COOLDOWN_SEG`,
`OTP_VENTANA_MINUTOS`, `OTP_EMISIONES_MAX_VENTANA`, `OTP_FALLOS_MAX_VENTANA`,
`OTP_LOCKOUT_MINUTOS`, `LIMITES_PETICIONES`, `ADMIN_PISO_IDENTIFICAR_SEG`,
`ADMIN_PISO_OTP_SEG`, `URL_BASE`.

> [!warning] Antes de desplegar
> Con varios workers, `LocMemCache` parte en pedazos el límite por IP (`comun/limites.py`) y
> el estado señuelo del acceso administrativo (`services/senuelo.py`): cada proceso lleva su
> cuenta y el límite efectivo se multiplica. Hace falta caché compartida (Redis/Memcached) y
> una base de datos de producción.

## Autenticación: OTP para todos

No hay contraseñas de login para nadie. Participantes y administrativos entran por código
de un solo uso enviado por correo (CU-REG-002, CU-REG-003; decisión del equipo 2026-06-30).
La sesión la abre `apps/registros/services/sesion.py` tras validar el código.

Si el correo no está configurado en `.env`, Django cae al backend de consola y el OTP se
imprime en la terminal. El `runserver` avisa con un recuadro en stderr, porque esa caída
silenciosa es la causa número uno de "el OTP no llega".

Defensas ya implementadas, no las reinventes:

- `comun/limites.py` — límite por IP (sustituye al throttling de DRF).
- `services/otp.py` — límites por cuenta destino: emisiones por ventana, lockout por fallos.
- `services/senuelo.py` — el acceso admin responde igual exista o no el correo, y las
  respuestas se retienen hasta un piso de tiempo para que la latencia tampoco delate quién
  es administrador.

## Mapa de URLs vigente

`registros` va montado en la raíz porque es la puerta de entrada. Los módulos verticales se
montarán bajo su prefijo (`eventos/`, `talleres/`, `stands/`, `visitas/`).

```text
Participante:  /acceso → /acceso/registro → /acceso/codigo → /convocatorias
Administrador: /admin/acceso → /admin/acceso/codigo → /admin/modulos
Común:         /salir
Django admin:  /django-admin/     (bajo prefijo propio, no choca con el panel FILEY)
```

## Añadir un dominio

Los puntos de enganche ya existen; un módulo nuevo **no inventa** identidad, sesión,
permisos ni maquetación.

1. `filey/apps/<dominio>/` con las capas de la sección 2 del SKILL.
2. Registrar `"apps.<dominio>"` en `INSTALLED_APPS`.
3. Montar en `config/urls.py` bajo su prefijo.
4. Añadir el código de módulo a `Modulo` en `apps/registros/models.py` si falta.
5. Proteger las vistas con `@requiere_modulo("EVT")` / `@requiere_participante`.
6. Las pantallas extienden `plantillas/layouts/panel.html`.
7. `apps/registros/catalogo.py` declara hoy a mano las convocatorias y módulos que se pintan
   tras el login. **Es temporal**: cuando el dominio tenga backend propio, su estado de
   convocatoria sale de ahí — REG no es dueño de ese contenido.

## Nomenclatura

Todo en español, incluidos los nombres de carpeta de Django.

| Cosa | Convención | Ejemplo |
| --- | --- | --- |
| Pantalla | `apps/<dom>/templates/<dom>/<pantalla>.html` | `registros/codigo.html` |
| Fragmento htmx | dentro de `parciales/` | `registros/parciales/estado_otp.html` |
| Layout compartido | `plantillas/layouts/` | `layouts/panel.html` |
| Nombre de URL | **snake_case**, con namespace de app | `{% url 'registros:admin_modulos' %}` |
| App | nombre del dominio en plural, español | `apps/registros/`, `apps/eventos/` |
| Pruebas | `apps/<dom>/pruebas/test_*.py` | `pruebas/test_otp.py` |
| Servicio | `apps/<dom>/services/<área>.py` | `services/otp.py` |

Las vistas son funciones, no clases. Reciben `peticion`, no `request`.

## Trampas verificadas

- **`{# … #}` es de una sola línea.** Multilínea se imprime en el HTML; usa `{% comment %}`.
- **`{% block %}` dentro de un `{% include %}` no es sobrescribible** por la plantilla que
  incluye. Los partials reciben datos por contexto o por `{% include ... with %}`.
- **htmx no sigue un 302**: reemplazaría el fragmento con la página entera. Usa
  `comun.htmx.redirigir`, que responde 204 + `HX-Redirect`.
- **`filey.js` debe cargarse antes que Alpine**: registra los componentes en `alpine:init`.
- **El CSRF de htmx** va una sola vez, en el `<body hx-headers=…>` de `base.html`. No lo
  repitas por formulario.
- **Gmail solo deja enviar como la cuenta autenticada.** Un `DEFAULT_FROM_EMAIL` de otro
  dominio falla SPF/DMARC y acaba en spam; settings lo reescribe solo.
- **Puerto SMTP**: 587 es STARTTLS y 465 es SSL directo. Cruzarlos cuelga la conexión.

## Qué falta decidir

- Motor de base de datos y caché compartida para producción.
- **ADR-0002 se cita en el código pero el archivo no está en `docs/adr/`** (solo hay
  `0000-template`, `0001` y el README). Conviene escribirlo o corregir las referencias.
- Portar los módulos verticales. El prototipo sigue siendo la especificación visual.
- Reconciliar `filey/estaticos/css/filey.css` con las capas del prototipo (ver sección 6
  del SKILL).
