---
estado: aceptada
version: "1.0"
tags:
  - tipo/adr
  - tema/arquitectura
fecha: 2026-08-06
fecha_actualizacion: 2026-08-06
id: ADR-0001
responsable: Juan Manuel Miranda
supersede:
reemplazado_por:
---
# ADR-0001. Arquitectura del sistema FILEY: monolito Django vs. Django API + Angular separado

## Estado

`Aceptado` — 2026-08-06. Se elige la **Opción A: monolito Django**. Ver "Decisión" abajo para
la frase de decisión y "Consecuencias" para lo que implica en la práctica, incluida la
migración pendiente de `registro/frontend/`.

## Contexto

El backend de FILEY se construye en **Django** (Python) — decisión ya tomada el 2026-07-20,
que reemplazó una recomendación inicial de Angular + NestJS + PostgreSQL + Prisma. Esa parte
no está en discusión aquí.

Lo que sí quedó abierto es **cómo se relaciona el frontend con ese backend**. Hoy existe un
único módulo construido, `registro/` (Core de Registros: alta de cuenta, login por OTP,
gestión de roles administrativos), con esta forma:

- **Backend:** Django + Django REST Framework, autenticación por **JWT** (`djangorestframework-simplejwt`,
  con rotación y blacklist de refresh tokens), CORS habilitado (`django-cors-headers`) para
  aceptar peticiones del frontend.
- **Frontend:** proyecto **Angular** aparte (`registro/frontend/`), servido en desarrollo con
  un proxy (`proxy.conf.json`) hacia la API, con su propio interceptor de autenticación y
  guards de ruta.
- Son **dos proyectos, dos `package.json`/`requirements.txt`, dos procesos** que hay que
  levantar para tener el sistema funcionando en local.

El 2026-08-05, en junta con un asesor técnico externo (ver transcripción de la junta del
05-ago), se planteó lo contrario: construir el sistema como un **monolito** — un solo
lenguaje, un solo proyecto, backend/frontend/base de datos desplegados juntos — con el
argumento de que, trabajando con agentes de IA, un solo contexto de proyecto reduce el costo y
la fricción de cada tarea (menos *context switching* entre "modo backend" y "modo frontend",
un solo lenguaje que el agente debe dominar, un solo deploy). El asesor mencionó Ruby on
Rails, Laravel y Phoenix como ejemplos de framework monolítico, y confirmó explícitamente que
**Django cumple el mismo rol** — por lo que esta decisión no reabre la elección de lenguaje/
framework backend (ya cerrada, ver arriba), solo si el frontend se separa o no.

Restricciones a considerar:

- Solo `registro/` está construido; es el momento más barato para decidir esto, antes de que
  existan tres o cuatro módulos más sobre el mismo patrón.
- El equipo ya tiene experiencia reciente con Angular (usado en `registro/frontend/`).
- El roadmap de FILEY incluye interacciones de UI no triviales próximamente: programación de
  actividades por arrastre (drag & drop) en `PRG`, mapa interactivo de stands en `STD`.
- El proyecto se construye fuertemente asistido por agentes de IA (Claude), y el argumento
  central del asesor es específicamente sobre cómo ese modo de trabajo cambia el cálculo
  costo/beneficio de separar frontend y backend.

## Opciones consideradas

### Opción A: Monolito Django (templates + HTMX/Alpine.js)

Un solo proyecto Django. El frontend se sirve con el sistema de templates de Django,
con HTMX para interactividad parcial (peticiones AJAX que devuelven fragmentos de HTML,
sin reescribir la página) y Alpine.js para estado puramente de UI en el cliente.

- **A favor:**
  - Un solo proceso, un solo deploy, una sola base de código para el agente de IA — es el
    argumento central de la junta del 05-ago.
  - Elimina JWT + CORS + proxy de desarrollo: la autenticación pasa a sesión de Django con
    cookie `HttpOnly`, lo cual además es más seguro (el token de sesión no vive expuesto en
    `localStorage` frente a XSS).
  - Transacciones que cruzan "módulos" (p. ej. inscribir a alguien, generar su pago y
    notificarlo) son una sola función Python con `transaction.atomic()`, no una coreografía
    entre dos sistemas.
  - Tests de extremo a extremo corren contra la base de datos real, sin mocks de red entre
    frontend y backend.
- **En contra:**
  - Hay que **reescribir** las 6 páginas ya construidas en Angular
    (`acceso`, `admin-acceso`, `admin-modulos`, `codigo`, `convocatorias`, `registro`) a
    templates + HTMX. Trabajo de migración inmediato, aunque acotado mientras solo exista
    `registro/`.
  - El equipo tiene que aprender/adoptar HTMX y Alpine si no los conoce ya.
  - Para interacciones ricas (drag & drop de `PRG`, mapa de `STD`) HTMX + Alpine puede quedar
    corto frente a lo que ya resuelve un framework SPA de fábrica; hay que validarlo con una
    prueba concreta antes de comprometerse (ver "Decisión" más abajo).

### Opción B: Django API (DRF) + Angular separado — arquitectura actual de `registro/`

Se mantiene el patrón ya implementado: Django expone una API REST con DRF, Angular consume esa
API como SPA independiente.

- **A favor:**
  - Es lo que ya existe y funciona en `registro/`; cero costo de migración.
  - Angular aporta de fábrica componentes, animaciones, formularios reactivos y manejo de
    estado que en HTMX/Alpine habría que construir o conseguir aparte.
  - Separación de responsabilidades más clásica: el equipo que conozca Angular puede trabajar
    en el frontend sin tocar Python.
- **En contra:**
  - Dos proyectos, dos lenguajes, dos sesiones/contextos — el costo que señaló el asesor
    específicamente para el modo de trabajo con agentes de IA: cada tarea que toca ambas capas
    paga el cambio de contexto dos veces.
  - Superficie de seguridad más grande: JWT en el cliente, CORS que hay que mantener correcto,
    dos capas de configuración de despliegue en vez de una.
  - Dos pipelines de build/deploy en vez de uno.

## Decisión

**FILEY se construye como un monolito Django**: un solo proyecto, un solo lenguaje, backend y
frontend servidos desde la misma aplicación Django (templates + HTMX/Alpine.js para
interactividad), sin frontend Angular separado. Esto aplica a todos los módulos futuros
(`EVT`, `STD`, `TAL`, `VIS`) desde su primera línea de código.

`registro/` —el único módulo ya construido bajo la Opción B (Django API + Angular)— se
**migra** a este mismo patrón. La migración es trabajo aparte, no un efecto colateral de otra
tarea (ver "Consecuencias" y "Próximos pasos").

## Consecuencias

**Positivas**

- Un solo proceso, un solo deploy, una sola base de código por delante del agente de IA en
  cada tarea — el argumento que motivó esta decisión.
- La autenticación deja de depender de JWT en el cliente: pasa a **sesión de Django con
  cookie `HttpOnly`**, lo que además reduce la superficie de ataque frente a XSS (el token de
  sesión ya no vive accesible desde JavaScript).
- Desaparecen `django-cors-headers`, `djangorestframework-simplejwt` y `proxy.conf.json` como
  piezas necesarias — existían solo por tener el frontend separado.
- Operaciones que cruzan varias entidades (inscribir, cobrar, notificar) se vuelven una sola
  función Python con `transaction.atomic()`, en vez de una coreografía entre dos sistemas.
- Un solo `requirements.txt`/entorno que levantar en desarrollo, no dos.

**Negativas / riesgos aceptados**

- El equipo necesita familiarizarse con HTMX/Alpine si no los ha usado antes.
- **Riesgo abierto, no resuelto por este ADR:** las interacciones más ricas del roadmap —
  programación por arrastre en `PRG`, mapa interactivo de stands en `STD` — no están todavía
  validadas con HTMX/Alpine. Se acepta el riesgo con la condición de hacer una prueba de
  concepto concreta de esos dos casos **antes** de comprometer su implementación final (ver
  "Próximos pasos"). Si alguno de los dos resulta inviable en HTMX/Alpine puro, la salida es
  una isla de JavaScript/Alpine más rica en esa página puntual, no volver a levantar un SPA
  aparte.

**Qué queda descartado por esta decisión**

- La Opción B (Django API + Angular separado) tal como existe hoy en `registro/`.
- Cualquier propuesta futura de separar frontend y backend en un módulo nuevo, salvo que un
  ADR posterior reemplace este (ver regla de inmutabilidad en `docs/adr/README.md`).

### Próximos pasos (fuera del alcance de este ADR, quedan como tareas)


1. Prueba de concepto de HTMX/Alpine para el arrastre de actividades (`PRG`) y el mapa de
   stands (`STD`) antes de construir esas pantallas "en serio".
2. ~~Actualizar `CLAUDE.md` del proyecto con la regla de arquitectura resultante (capas
   `models/services/views/templates`, sin API REST salvo que se justifique un caso puntual).~~
   **Hecho el 2026-08-06** — ver [`CLAUDE.md`](<../../CLAUDE.md>) en la raíz del repositorio.

