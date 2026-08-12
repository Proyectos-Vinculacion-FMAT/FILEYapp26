# Renderizador Django — `config/`, `apps/`, `frontend/`

Estado: **andamiaje verificado, sin pantallas reales portadas.** `manage.py check` pasa sin
issues y la portada renderiza con el CSS del prototipo servido por staticfiles
(Python 3.14 + Django 6.1, comprobado el 2026-08-11).

## Arrancar

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe manage.py check
.venv/Scripts/python.exe manage.py runserver
```

Variables de entorno reconocidas: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`1`/`0`),
`DJANGO_ALLOWED_HOSTS` (lista separada por comas).

## Decisiones ya tomadas en `config/settings.py`

| Ajuste | Valor | Por qué |
| --- | --- | --- |
| `TEMPLATES["DIRS"]` | `frontend/templates` | Frontend como módulo, no como anexo de cada app |
| `APP_DIRS` | `False` | Impide que aparezcan templates dentro de apps por descuido |
| `STATICFILES_DIRS` | `frontend/static` **y** `prototipo` | Fuente única de CSS: sin copias que diverjan |
| `LANGUAGE_CODE` | `es-mx` | — |
| `TIME_ZONE` | `America/Merida` | Los horarios de sala y los cortes de reserva son locales |
| Base de datos | SQLite | Suficiente para desarrollo; decisión de producción pendiente |

`STATIC_ROOT = staticfiles/` está configurado pero **no** hay `ManifestStaticFilesStorage`
todavía: se activa cuando exista despliegue real, para cache-busting.

## Añadir un dominio

1. `apps/{dom}/` con `__init__.py`, `apps.py` (`name = "apps.{dom}"`), `models.py`,
   `views.py`, `urls.py` (con `app_name = "{dom}"`).
2. Registrar `"apps.{dom}"` en `INSTALLED_APPS`.
3. Montar en `config/urls.py` con namespace:
   `path("{ruta}/", include(("apps.{dom}.urls", "{dom}"), namespace="{dom}"))`.
4. `frontend/templates/{dom}/aplicantes/` y `frontend/templates/{dom}/administradores/`.
5. Si el dominio tiene capa CSS propia, la plantilla base del dominio sobrescribe el bloque
   `estilos`. No hace falta enlazar también `common/`: lo trae el `@import` de la capa:

   ```django
   {% block estilos %}<link rel="stylesheet" href="{% static 'VIS/styles.css' %}">{% endblock %}
   ```

## Nomenclatura

| Cosa | Convención | Ejemplo |
| --- | --- | --- |
| Plantilla de pantalla | `{dom}/{rol}/{pantalla}.html` | `vis/administradores/propuestas.html` |
| Fragmento htmx | guion bajo inicial | `vis/_tabla-propuestas.html` |
| Componente reusable | `components/{clase-css}.html` | `components/conv-card.html` |
| Nombre de URL | kebab-case, sin el dominio | `{% url 'vis:admin-propuestas' %}` |
| App | prefijo de caso de uso en minúsculas | `apps/vis/` ← `CU-VIS-*` |

Los prefijos de app corresponden a `docs/requisitos/{DOM}/`: REG, EVT, VIS, STD, TAL, PRG, SAL.

## Trampas verificadas

- **`{# … #}` es de una sola línea.** Un comentario multilínea con esa sintaxis se imprime
  tal cual en el HTML. Usa `{% comment %}…{% endcomment %}`.
- **`{% block %}` dentro de un `{% include %}` no es sobrescribible** por la plantilla que
  incluye. Los partials reciben datos por contexto o por `{% include ... with %}`; para
  variar el chasis, se sobrescribe el bloque en `base.html` (`topbar`, `footer`, `estilos`).
- **`ALLOWED_HOSTS`** no trae `testserver`, así que el `Client` de pruebas devuelve 400 salvo
  que se añada por entorno. En tests reales, usa `@override_settings(ALLOWED_HOSTS=["testserver"])`.
- **Nombres de asset sin espacios.** El logotipo se llamaba `filey-logotipo-azul 1.svg`
  (artefacto de descarga duplicada) y obligaba a escribirlo `%201` en el prototipo y con
  espacio literal en `{% static %}`. Se renombró a `filey-logotipo-azul.svg`. Si añades un
  asset, quítale el espacio antes de referenciarlo.

## Qué falta decidir

- **htmx todavía no está en el proyecto.** El patrón de fragmentos está documentado en el
  SKILL, pero no hay `htmx.min.js`. Como no se permiten CDN, habrá que versionar el archivo
  en `frontend/static/js/` cuando se porte la primera pantalla con filtros.
- Motor de base de datos y despliegue de producción.
- Autenticación real: el prototipo usa OTP por correo para aplicantes y contraseña para
  administrativos (`CU-REG-002`, `CU-REG-003`); no hay implementación todavía.
- Qué pasa con `prototipo/STD/` (Angular + WASM de Godot): portar o montar como isla.
