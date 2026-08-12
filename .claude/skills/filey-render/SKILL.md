---
name: filey-render
description: Cómo una pantalla de FILEY llega al navegador — estructura del monolito Django (apps de backend vs. frontend centralizado), herencia de plantillas, partials como componentes, {% static %} y la fuente única de CSS, contrato vista↔template, htmx para actualizaciones parciales, ruteo de pantallas por rol, y el procedimiento para portar una pantalla del prototipo HTML a plantilla Django. Úsalo al crear o editar templates, vistas que rendericen HTML, URLs, archivos estáticos, o cualquier HTML del prototipo. Cubre los dos renderizadores que hoy coexisten.
---

# FILEY — del componente a la pantalla servida

Este skill responde **¿cómo llega al navegador?**. Los otros dos:

| Necesitas | Skill |
| --- | --- |
| Elegir color, radio, tono, cuántos pasos lleva el flujo | `filey-identidad` |
| Saber si una clase existe y en qué capa va el CSS | `filey-ui-componentes` |

## 0. ¿Qué renderizador aplica?

Míralo por la ruta del archivo. **No asumas** — hoy coexisten los dos.

| El archivo está en… | Renderizador | Referencia |
| --- | --- | --- |
| `prototipo/` | HTML estático sobre `file://` + pseudo-backend `db.js` | [references/renderer-estatico.md](references/renderer-estatico.md) |
| `frontend/`, `apps/`, `config/` | Django | [references/renderer-django.md](references/renderer-django.md) |

Errores típicos por confundirlos: `{% static %}` en un HTML del prototipo (no se procesa,
sale literal) o rutas relativas `../styles.css` en una plantilla Django (rompen al cambiar
la URL, que no corresponde a la profundidad de carpetas).

---

## 1. Estructura del monolito

> [!important] Esta estructura es la recomendada, no una imposición
> Si al abrir el repo encuentras que ya existe otra organización, **trabaja con la que
> existe**: sigue sus convenciones y no la migres a esta sin pedirlo explícitamente.
> Lo de abajo aplica cuando no hay nada establecido en contra.

```
config/          settings, urls raíz, wsgi/asgi
apps/            Python puro — sin templates, sin static
  core/          base, auth, mixins compartidos
  reg/ evt/ vis/ std/ tal/ prg/ sal/    un app por prefijo de caso de uso
    models.py services.py views.py urls.py
frontend/        todo lo que el navegador ve
  templates/
    base.html
    partials/    topbar, footer — piezas del chasis
    components/  tarjetas, badges, notas — 1:1 con componentes CSS
    {dom}/aplicantes/   {dom}/administradores/
  static/
    css/ js/
prototipo/       congelado como referencia visual; sigue siendo la fuente del CSS
```

**Por qué el frontend está centralizado y no dentro de cada app** (que es la convención
Django): el requisito es separación modular front/back. Templates dentro de las apps
esparce la UI en siete carpetas y hace que cada cambio visual toque módulos de backend.
Con `TEMPLATES["DIRS"]` apuntando a `frontend/templates/`, las apps quedan Python puro y
`frontend/templates/{dom}/{rol}/` espeja exactamente `prototipo/{DOM}/{rol}/`, de modo que
portar una pantalla es mecánico. `APP_DIRS` está en `False` a propósito — no lo actives.

### Fuente única de CSS

`STATICFILES_DIRS` incluye `prototipo/`, así que `{% static 'VIS/styles.css' %}` resuelve al
archivo real del prototipo y su `@import '../common/styles-base.css'` sigue funcionando.

**No copies CSS a `frontend/static/css/`.** Dos copias divergen; es precisamente lo que
esta arquitectura evita. Cuando la última pantalla esté portada, los archivos se mueven con
`git mv` y se quita la entrada `prototipo/` de `STATICFILES_DIRS`: un solo cambio.

## 2. Ruteo de pantalla por rol

La regla del prototipo se conserva tal cual:

| ¿Quién usa la pantalla? | Prototipo | Django |
| --- | --- | --- |
| Solo aplicantes | `{DOM}/aplicantes/x.html` | `frontend/templates/{dom}/aplicantes/x.html` |
| Solo administradores | `{DOM}/administradores/x.html` | `frontend/templates/{dom}/administradores/x.html` |
| Ambos roles | `{DOM}/x.html` | `frontend/templates/{dom}/x.html` |

En Django el rol además se aplica con `LoginRequiredMixin` / `UserPassesTestMixin` en la
vista y con namespace de URL (`{% url 'vis:admin-propuestas' %}`). La carpeta documenta;
el mixin protege. Nunca solo la carpeta.

## 3. Contrato vista ↔ template

Una vista expone **nombres de dominio, no de presentación**: `propuestas`, `cupo_restante`,
`puede_dictaminar` — no `filas`, `color_badge`, `texto_boton`.

- La decisión de *qué clase CSS* corresponde a un estado se toma en el template
  (`{% if propuesta.estado == "aceptada" %}badge-accepted{% endif %}`) o en un filtro,
  nunca en la vista devolviendo `"badge-accepted"`.
- Formateo de fecha, moneda y cupo va en filtros de template, no en la vista.
- Todo template documenta su contrato en un `{% comment %}` al inicio: qué variables espera.
  Los partials sobre todo — son los que se reusan sin ver la vista.

`{% comment %}…{% endcomment %}` para varias líneas. `{# … #}` es de **una sola línea**:
si lo usas multilínea, el texto sale impreso en el HTML.

## 4. Componente CSS ↔ partial

Correspondencia 1:1 y greppable: la clase `.conv-card` vive en
`frontend/templates/components/conv-card.html`. Si un componente del inventario se usa en
dos pantallas, tiene partial; si se usa una vez, puede quedarse inline.

```django
{% include "components/conv-card.html" with convocatoria=c abierta=True %}
```

Usa `{% include ... with ... only %}` cuando el partial no deba ver el contexto completo.
Empieza con includes planos: **sin librerías de componentes**. Si un include llega a más de
4 parámetros o necesita slots, entonces evalúa `django-cotton` — no antes.

## 5. htmx para actualizaciones parciales

El JS del prototipo ya es "recalcular una lista y volver a pintarla", que es exactamente lo
que htmx hace contra el servidor. Patrón:

```django
{# lista completa #}
<div id="propuestas">{% include "evt/_tabla-propuestas.html" %}</div>

{# el filtro pide solo el fragmento #}
<select name="estado" hx-get="{% url 'evt:propuestas' %}" hx-target="#propuestas"></select>
```

```python
def propuestas(request):
    ctx = {"propuestas": Propuesta.objects.filtrar(request.GET)}
    plantilla = "evt/_tabla-propuestas.html" if request.headers.get("HX-Request") else "evt/propuestas.html"
    return render(request, plantilla, ctx)
```

El markup de la tabla existe **una sola vez** y sirve para la página completa y para el
swap. Ese es el contrato entre lo visual y el renderizador.

Reglas: el fragmento se llama `_nombre.html` (guion bajo inicial). Nada de estado de UI en
el servidor que no esté en la URL — un filtro aplicado debe sobrevivir a un refresh.
JS propio solo para estado local (abrir/cerrar un modal); no reimplementes htmx a mano.

## 6. Portar una pantalla del prototipo

1. Localiza el HTML en `prototipo/{DOM}/{rol}/` y **no lo leas completo**: `grep -n` las
   secciones que necesitas (ver protocolo de lectura en `filey-ui-componentes`).
2. Crea `frontend/templates/{dom}/{rol}/{pantalla}.html` con `{% extends "base.html" %}`.
3. Copia solo el contenido de `<main>`; topbar, footer y `<head>` ya los da `base.html`.
4. Sustituye:
   - `href="otra.html"` → `{% url 'dom:vista' %}`
   - `src="../../common/assets/x.svg"` → `{% static 'common/assets/x.svg' %}`
   - datos de `db.js` → variables de contexto
   - `<script>` de re-render → htmx, o un `_fragmento.html`
5. Si el HTML traía un `<style>` embebido, ese CSS **no viaja al template**: va a la capa
   que corresponda según `filey-ui-componentes`. Es la ocasión de bajar esa deuda.
6. Sobrescribe `{% block estilos %}` con la capa del dominio si la tiene.
7. La pantalla del prototipo se queda como estaba hasta que todo el dominio esté portado.

## 7. Checklist

```bash
.venv/Scripts/python.exe manage.py check
.venv/Scripts/python.exe manage.py runserver
./scripts/check-ui.sh          # el CSS servido es el mismo del prototipo: sigue aplicando
```

- [ ] La plantilla extiende `base.html`; no repite `<head>`, topbar ni footer
- [ ] Cero rutas relativas: `{% url %}` y `{% static %}`
- [ ] La vista expone nombres de dominio, no de presentación
- [ ] El rol está protegido por mixin, no solo por la carpeta
- [ ] Los comentarios multilínea usan `{% comment %}`
- [ ] No se copió CSS a `frontend/static/css/`
