# CLAUDE.md — FILEY

Contexto y reglas de arquitectura para trabajar en este repositorio. Léelo antes de escribir o
recomendar código para cualquier módulo del sistema FILEY (Feria Internacional de la Lectura
Yucatán).

## Qué es este repositorio

Dos cosas conviven aquí:

- **`docs/`** — especificación funcional: dominios, casos de uso (`CU-DOM-NNN`) y decisiones de
  arquitectura (`docs/adr/`). Es la fuente de verdad de **qué** construye el sistema y **por
  qué** se construye de cierta forma.
- **`filey/`** — la implementación real en código: el **monolito Django**. Hoy contiene un solo
  dominio, el Core de Registros (`apps/registros/`): alta de cuenta, login por OTP, roles
  administrativos. `EVT`, `STD`, `TAL`, `VIS` todavía no existen como código, solo como
  especificación en `docs/requisitos/`.

Empieza por [`Filey.md`](<Filey.md>) (portada) si necesitas orientarte en la estructura completa.

## Arquitectura: monolito Django

> [!important] Decisión vigente — [ADR-0001](<docs/adr/0001-arquitectura-monolito-vs-separado.md>)
> **Todo el sistema se construye como un monolito Django**: un solo proyecto, un solo
> lenguaje, backend y frontend servidos desde la misma aplicación Django (templates +
> HTMX/Alpine.js para interactividad). **No se separa frontend y backend en proyectos
> distintos** — nada de API REST + SPA aparte, salvo que un ADR posterior lo autorice
> explícitamente para un caso puntual.

**Estado real:** la migración **ya está hecha** — [ADR-0002](<docs/adr/0002-migracion-de-registro-al-monolito.md>).
El Core de Registros se reconstruyó como proyecto nuevo `filey/` y la carpeta `registro/`
(DRF + JWT + Angular) ya no existe. En `filey/` no hay `rest_framework`, `simplejwt` ni
`corsheaders`: la autenticación es sesión de Django con cookie `HttpOnly` y las pantallas son
plantillas Django con HTMX/Alpine.

**Todo módulo nuevo** (`EVT`, `STD`, `TAL`, `VIS`) se construye ya bajo el patrón monolito desde
su primera línea de código: sin DRF, sin JWT, sin proyecto Angular propio. Autenticación por
sesión de Django con cookie `HttpOnly`, reutilizando lo que ya expone `apps/registros/`.

## Estructura de capas

Cada app de dominio (`apps/registros/`, y las que se abran para `EVT`/`STD`/`TAL`/`VIS`) sigue
las mismas capas, cada una con una única responsabilidad:

```text
filey/
├── config/          → settings, urls raíz, wsgi/asgi
├── comun/           → código transversal, de ningún dominio (htmx.py, limites.py)
├── plantillas/      → base.html + layouts compartidos por todos los módulos
├── estaticos/       → css, js (HTMX y Alpine versionados aquí), imágenes
└── apps/<dominio>/
    ├── models.py       → datos + invariantes que la BD debe garantizar (fat models)
    ├── services/        → casos de uso y reglas de negocio — aquí vive la lógica de cada CU
    ├── views.py         → traduce HTTP ↔ servicio. Sin lógica de negocio (thin views)
    ├── urls.py          → rutas de la app
    └── templates/<dominio>/  → presentación (Django templates + fragmentos HTMX)
```

Ya está así en `apps/registros/` — sigue siendo el ejemplo de referencia:
`services/otp.py` y `services/notificaciones.py` tienen las reglas (cool-down, lockout,
generación/verificación de OTP); `views.py` solo valida el request, llama al servicio y
traduce el resultado a una respuesta; `models.py` (`Persona`, `RolPermiso`, `SesionOTP`) trae
la lógica de dominio que le pertenece a los datos (`es_administrativa`,
`modulos_administrables`, `codigo_coincide`).

**Regla dura:** la lógica de negocio **nunca** vive en `views.py` ni en un template. Si una
regla no se puede llamar desde un comando de `manage.py` sin pasar por HTTP, está en el lugar
equivocado — debe estar en `services/`.

## Regla de dependencias

Las dependencias entre apps de dominio van **en una sola dirección**, nunca al revés:

```text
apps/registros/  ←  apps/eventos/, apps/stands/, apps/talleres/, apps/visitas/
     (base: Persona, RolPermiso, sesión)      (dominios verticales)
```

- `apps/registros/` no importa de ningún módulo de dominio. Es la base (identidad, sesión,
  permisos) de la que todos los demás dependen.
- Los módulos de dominio (`eventos`, `stands`, `talleres`, `visitas`) pueden depender de
  `registros`, nunca al revés.
- **Entre hermanos** (p. ej. `talleres` necesitando algo de `eventos`, como ya ocurre porque un
  taller se anexa al calendario maestro de `EVT` — ver `docs/requisitos/README.md`, sección
  "Relación entre dominios"): la dependencia debe ser explícita y en una sola dirección
  declarada, nunca circular. Si dos módulos necesitan depender mutuamente, esa lógica
  compartida se saca a un módulo común, no se referencian entre sí.
- **Sin imports circulares**, nunca. Es la regla que más fácil rompe un agente de IA al
  resolver una tarea aislada sin ver el grafo completo — por eso queda escrita aquí.

## Cómo se conecta un módulo nuevo (EVT, TAL, STD, VIS)

Los puntos de enganche ya existen. Un módulo nuevo **no inventa** identidad, sesión, permisos
ni maquetación: los toma de aquí.

1. **Permisos — `apps/registros/permisos.py`.** Es el contrato. Ningún módulo implementa su
   propia autenticación; importa los decoradores:

   ```python
   from apps.registros.models import NivelPermiso
   from apps.registros.permisos import requiere_modulo, requiere_participante

   @requiere_participante
   def convocatoria(peticion): ...              # zona del participante

   @requiere_modulo("EVT")                       # basta con poder leer
   def panel(peticion): ...

   @requiere_modulo("EVT", NivelPermiso.EDICION)
   def dictaminar(peticion, propuesta_id): ...
   ```

2. **Maquetación — `plantillas/layouts/panel.html`.** Toda pantalla posterior al login extiende
   este layout y hereda barra superior y pie. Se renderiza con `{"zona_admin": True}` para la
   variante administrativa.

3. **Rutas — `config/urls.py`.** Cada dominio se monta bajo su propio prefijo (`eventos/`,
   `talleres/`…). `registros` va en la raíz por ser la puerta de entrada.

4. **Registrar la app** en `INSTALLED_APPS` (`config/settings.py`) y añadir su código de módulo
   a `Modulo` en `apps/registros/models.py` si aún no está.

5. **`apps/registros/catalogo.py` es temporal.** Hoy declara a mano las convocatorias y los
   módulos que se pintan tras el login. Cuando un dominio tenga backend propio, **su** estado de
   convocatoria sale de ahí y se retira del catálogo — REG no es dueño de ese contenido.

Y las dos reglas de frontend que aplican a todo el monolito, no solo a REG:

- **Toda pantalla funciona sin JavaScript.** La vista responde página completa o fragmento según
  la cabecera `HX-Request` (helpers en `comun/htmx.py`). HTMX mejora la experiencia; no es
  requisito para poder usar el sistema.
- **Nada se carga de un CDN.** HTMX y Alpine viven en `estaticos/js/`.

## Dónde vive cada tipo de decisión

- **Qué hace el sistema** (por dominio, casos de uso) → `docs/requisitos/`.
- **Cómo se construye** (arquitectura, stack, decisiones técnicas transversales y su porqué) →
  `docs/adr/`. Antes de proponer un cambio de arquitectura, revisa si ya hay un ADR sobre eso —
  y si lo hay y sigue `Aceptado`, no se contradice sin escribir uno nuevo que lo reemplace (ver
  regla de inmutabilidad en `docs/adr/README.md`).

## Contexto y actualizaciones recientes

> [!note] Mantener esta sección al día
> Cuando se cierre un ADR nuevo o cambie algo de arquitectura, añade una línea aquí — es lo que
> le da a cualquiera que abra este archivo el estado actual sin tener que leer todo `docs/adr/`.

- **2026-07-20** — Backend del sistema: **Django**, no NestJS (recomendación inicial descartada).
- **2026-08-05** — Junta con asesor externo: se descarta Supabase; se plantea arquitectura
  monolítica.
- **2026-08-06** — [ADR-0001](<docs/adr/0001-arquitectura-monolito-vs-separado.md>) `Aceptado`:
  el sistema se construye como **monolito Django** (templates + HTMX/Alpine, sin Angular
  separado).
- **2026-08-07** — [ADR-0002](<docs/adr/0002-migracion-de-registro-al-monolito.md>) `Aceptado`
  y ejecutado: el Core de Registros se **reconstruyó** como proyecto nuevo `filey/`; `registro/`
  (DRF + JWT + Angular) desapareció. Se reimplantaron por cuenta propia las piezas que aportaba
  DRF (el throttling por IP, ahora en `comun/limites.py`), la sesión dura 12 h desde la última
  actividad, y WhiteNoise sirve los estáticos para que el despliegue sea un solo servicio.
  **75 pruebas** pasando.

> [!warning] Antes de desplegar
> `filey/` corre con **SQLite** y **`LocMemCache`**. Con varios workers, la caché local parte en
> pedazos el límite por IP (`comun/limites.py`) y el estado señuelo del acceso administrativo
> (`services/senuelo.py`): cada proceso lleva su propia cuenta y el límite efectivo se
> multiplica. Hay que configurar una caché compartida (Redis/Memcached) y una base de datos de
> producción antes de exponer esto.
