---
estado: aceptada
version: "1.0"
tags:
  - tipo/adr
  - dom/reg
  - tema/arquitectura
  - tema/permisos
fecha: 2026-08-21
fecha_actualizacion: 2026-08-21
id: ADR-0002
responsable: Juan Manuel Miranda
supersede:
reemplazado_por:
---
# ADR-0002. Migrar el Core Registros de Django REST + JWT + Angular al monolito, y sustituir el JWT por sesión de Django

## Estado

`Aceptado` — la decisión se tomó y **se ejecutó el 2026-08-11** (primer commit del monolito
bajo `filey/`). Este documento se escribe el 2026-08-21, **después** de la ejecución, para
cerrar el hueco que él mismo describe: el código ya cita "ADR-0002" en tres lugares
(`filey/requirements.txt`, `filey/comun/limites.py` y el skill `filey-render`) pero el ADR no
existía. Se registra ahora tal como se decidió entonces, sin reescribir el pasado.

> [!note] Por qué se documenta tarde y por qué importa
> Es exactamente el caso que el [README de ADRs](<README.md>#por-qué-esto-nos-sirve-a-nosotros-en-concreto)
> advierte: decisiones que se toman, se ejecutan y no se cierran formalmente. Diez días después
> nadie del equipo podía explicar desde el repositorio por qué `registro/` ya no existe, por
> qué desapareció el JWT, o por qué los casos de uso siguen hablando de *access token* y
> *refresh token* que el sistema ya no emite.

## Contexto

[ADR-0001](<0001-arquitectura-monolito-vs-separado.md>) (aceptado el 2026-08-06) decidió que
FILEY se construye como **monolito Django**, y dejó explícitamente fuera de su alcance una
tarea: migrar `registro/` —el único módulo ya construido— desde el patrón que ese mismo ADR
descartaba. Sus "Consecuencias" la nombran como trabajo aparte, no como efecto colateral.

Lo que había que migrar, tal como lo describe ADR-0001:

- **Backend:** Django + Django REST Framework, con `djangorestframework-simplejwt` (access +
  refresh, rotación y *blacklist* de refresh tokens) y `django-cors-headers`.
- **Frontend:** un proyecto **Angular** aparte (`registro/frontend/`) con seis pantallas
  —`acceso`, `admin-acceso`, `admin-modulos`, `codigo`, `convocatorias`, `registro`—, su
  `proxy.conf.json`, su interceptor de autenticación y sus guards de ruta.
- **Sesión:** el par access/refresh vivía en el `localStorage` del navegador; el **flujo de
  acceso a medio camino** (qué correo se está verificando entre la pantalla del correo y la del
  código) vivía en el `sessionStorage` del navegador.

Fuerzas que había que resolver al ejecutar la migración, y que ADR-0001 no cerraba:

1. **Qué hacer con el JWT.** El monolito no necesita tokens —no hay cliente ajeno que
   autenticar—, pero migrar "solo el frontend" y conservar el JWT era posible. Había que
   decidirlo explícitamente porque cambia el modelo de sesión de todo el sistema, y con él lo
   que dicen CU-REG-002, CU-REG-003 y CU-REG-004.
2. **Qué hacer con las defensas que aportaba DRF.** El `ScopedRateThrottle` de DRF era la única
   capa de límite por IP del acceso. Retirar DRF sin más dejaba los endpoints de OTP sin ninguna
   defensa por origen — un retroceso de seguridad frente a lo que ya estaba en producción de
   pruebas.
3. **Dónde vive el flujo de acceso.** Mantenerlo en el navegador (como en Angular) o moverlo al
   servidor. No es cosmético: mientras el correo a verificar lo elija el cliente en cada paso,
   el paso de identificación se puede saltar mandando otro correo en la petición del código.
4. **Cuánta superficie se rehace de una vez.** `registro/` tenía ya un comportamiento
   trabajado —OTP con cool-down, topes por cuenta, lockout, señuelo anti-enumeración de
   administradores (auditoría del 2026-08-02)— que no debía perderse en la traducción.

## Opciones consideradas

### Opción A: migrar `registro/` completo al monolito y sustituir el JWT por sesión de Django

Reescribir las seis pantallas de Angular como plantillas Django + htmx/Alpine, retirar DRF,
SimpleJWT y CORS, y cambiar el modelo de sesión al de Django (cookie `HttpOnly`, datos en el
servidor).

- **A favor:**
  - Es lo que ADR-0001 pide, sin dejar una excepción permanente en el módulo base del sistema.
  - Quita el token del `localStorage`: deja de ser robable por cualquier XSS.
  - **Cerrar sesión pasa a ser inmediato y total.** Con JWT, el *access token* seguía válido
    hasta caducar (1 h) y hacía falta una lista de revocación para el *refresh*; con sesión de
    Django no queda nada que revocar ni credencial que siga sirviendo.
  - Mover el flujo de acceso a la sesión del servidor **cierra un hueco real**: el correo a
    verificar deja de ser un dato que el cliente elige en cada paso.
  - `registros` es la base de identidad de todos los demás módulos (`EVT`, `TAL`, `STD`, `VIS`):
    si se queda en el patrón viejo, cada módulo nuevo hereda dos formas de autenticar.
- **En contra:**
  - Hay que rehacer las seis pantallas y **reimplementar lo que DRF daba gratis**: los
    *serializers* pasan a `forms.py` y el *throttling* por IP hay que escribirlo
    (`comun/limites.py`).
  - Los casos de uso CU-REG-002/003/004 quedan describiendo un mecanismo (JWT, *access* y
    *refresh*, lista de revocados) que el sistema deja de tener — hay que actualizarlos aparte.

### Opción B: migrar solo el frontend y conservar la API con JWT

Servir las pantallas desde Django, pero dejando DRF + SimpleJWT como capa de autenticación
contra la que las plantillas hablan.

- **A favor:**
  - Migración más corta: no se toca la capa de autenticación ya probada.
  - Los CU-REG-002/003/004 seguirían siendo literalmente ciertos, sin trabajo de documentación.
- **En contra:**
  - Conserva **el peor de los dos mundos**: la complejidad del token (rotación, *blacklist*,
    caducidad, CORS) sin la razón que la justificaba (un cliente separado que autenticar).
  - Deja el token accesible desde JavaScript, es decir, mantiene viva la exposición a XSS que
    ADR-0001 quería eliminar.
  - Cerrar sesión seguiría sin ser inmediato — una nota de "riesgo conocido" permanente en
    CU-REG-004 por una arquitectura que ya nadie quiere.

### Opción C: dejar `registro/` como está y aplicar el monolito solo a los módulos nuevos

- **A favor:** cero costo inmediato; el trabajo ya hecho no se toca.
- **En contra:** el módulo **base** del sistema queda siendo la única excepción a la
  arquitectura, y es justo el que los demás importan para autenticar. En la práctica significa
  mantener dos stacks para siempre: el de `registros` y el de todo lo demás.

## Decisión

**Migramos el Core Registros completo al monolito Django y sustituimos el JWT por la sesión de
Django** (cookie `HttpOnly`, estado en el servidor). Se retiran `djangorestframework`,
`djangorestframework-simplejwt` y `django-cors-headers`; el proyecto Angular `registro/frontend/`
desaparece y sus seis pantallas se rehacen como plantillas con htmx y Alpine servidos localmente.

Lo que DRF aportaba se reconstruye explícitamente y no se pierde:

| Lo que daba DRF | Dónde vive ahora |
| --- | --- |
| *Serializers* de validación | `filey/apps/registros/forms.py` |
| `ScopedRateThrottle` (límite por IP) | `filey/comun/limites.py` |
| Autenticación por token | Sesión de Django — `filey/apps/registros/services/sesion.py` |
| Permisos de vista (`permission_classes`) | Decoradores — `filey/apps/registros/permisos.py` |

El **flujo de acceso** (correo y contexto de quien está a medio entrar) pasa del
`sessionStorage` del navegador a la sesión del servidor.

## Consecuencias

**Positivas**

- Un solo proyecto, un solo proceso, un solo despliegue — ADR-0001 queda aplicado sin
  excepciones, incluido su módulo base.
- La credencial de sesión sale del alcance de JavaScript (`HttpOnly`), y `login()` rota el
  identificador de sesión, que es la defensa estándar contra fijación de sesión.
- **Cerrar sesión es inmediato y total** (CU-REG-004): no hay lista de revocados que mantener
  ni *access token* vivo durante una hora después.
- El correo a verificar ya no lo elige el cliente entre un paso y el siguiente.
- Desaparecen CORS y `proxy.conf.json` como piezas que mantener correctas.

**Negativas / riesgos aceptados**

- **CU-REG-002, CU-REG-003 y CU-REG-004 quedan desactualizados** desde el mismo día de la
  migración: siguen describiendo JWT, *access*/*refresh token* y lista de revocados, que el
  sistema ya no emite. Actualizarlos es trabajo pendiente, no un efecto de este ADR.
- Las dos defensas que dependen de caché —el señuelo anti-enumeración (`services/senuelo.py`) y
  el límite por IP (`comun/limites.py`)— quedan configuradas sobre `LocMemCache`, que **cada
  proceso ve por separado**. Con varios *workers* en producción, el límite real se multiplica
  por el número de procesos y el señuelo deja de responder de forma consistente. Es
  exactamente el "Requisito de despliegue" que exige CU-REG-003: **hay que configurar una caché
  compartida (Redis/Memcached) antes de servir con más de un proceso.**
- Cualquier interacción rica de `registro/` que Angular resolvía de fábrica hay que
  construirla; en REG resultó barato (seis pantallas de formulario), pero no dice nada sobre
  `PRG` y `STD`, cuyo riesgo sigue abierto en ADR-0001.
- El límite por IP escrito a mano es una reimplementación con la misma limitación conocida que
  la de DRF (ventana fija: en el filo entre dos ventanas caben hasta el doble de peticiones).

**Qué queda descartado por esta decisión**

- El proyecto `registro/frontend/` (Angular) y su `proxy.conf.json`.
- DRF, SimpleJWT y `django-cors-headers` como dependencias del proyecto.
- Autenticar cualquier módulo futuro con tokens en el cliente. Un módulo que necesite una API
  para un consumidor externo real (no para su propio frontend) requiere un ADR nuevo.

## Referencias

- [ADR-0001](<0001-arquitectura-monolito-vs-separado.md>) — la decisión de monolito que este ADR
  ejecuta; su sección "Próximos pasos" nombra esta migración.
- [`CU-REG-002`](<../requisitos/REG/CU-REG-002 Iniciar sesion como usuario externo (OTP).md>),
  [`CU-REG-003`](<../requisitos/REG/CU-REG-003 Iniciar sesion como usuario administrativo (OTP).md>),
  [`CU-REG-004`](<../requisitos/REG/CU-REG-004 Cerrar sesion.md>) — los casos de uso que esta
  migración deja desactualizados en su mecanismo de sesión.
- [`Modelo de datos - Registros`](<../requisitos/REG/Modelo de datos - Registros.md>) — las
  entidades `Persona`, `RolPermiso` y `SesionOTP` que la migración conserva sin cambios.
- Código: `filey/comun/limites.py` y `filey/requirements.txt` citan este ADR en sus
  comentarios de cabecera.
