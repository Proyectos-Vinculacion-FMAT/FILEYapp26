---
estado: vigente
version: 1.0
tags:
  - tipo/referencia
  - dom/reg
  - tema/permisos
  - tema/arquitectura
fecha: 2026-08-25
---
# Mecanismo de sesión y control de acceso (REG)

> Cómo funciona **hoy, en el código desplegado**, lo que ocurre después de que el OTP se acierta:
> qué recibe el navegador, qué manda de vuelta en cada petición y quién decide si pasa.
> Complementa a [`CU-REG-002`](<CU-REG-002 Iniciar sesion como usuario externo (OTP).md>) y
> [`CU-REG-003`](<CU-REG-003 Iniciar sesion como usuario administrativo (OTP).md>), que describen
> el flujo desde el punto de vista del usuario, y a
> [ADR-0002](<../../adr/0002-migracion-de-registro-al-monolito.md>), que decidió abandonar el JWT.
>
> Este documento **describe**, no decide. Si algo de aquí cambia, cambia porque lo cambió un ADR
> o un caso de uso.

---

## 1. No hay token

Es lo primero que hay que desaprender de la versión Angular: **el navegador no guarda ninguna
credencial**. El OTP demuestra la identidad **una sola vez** y después desaparece; lo único que
queda en el cliente es una cookie `sessionid` cuyo contenido es una cadena aleatoria de 32
caracteres sin significado propio. Todo el estado —quién eres, con qué backend te autenticaste—
vive en la base de datos, en la tabla `django_session`.

Consecuencia práctica: **no existe nada que robar del cliente**. Un XSS no puede leer la cookie
(`HttpOnly`), y aunque pudiera copiarla, cerrar sesión la mata de inmediato del lado del servidor,
sin listas de revocación ni esperas a que un token caduque.

## 2. Qué pasa al acertar el código

`apps/registros/views.py:463` llama a `sesion_service.iniciar(...)`, y ese servicio
(`apps/registros/services/sesion.py:102`) hace una sola cosa relevante:

```python
login(peticion, persona, backend=BACKEND)
```

`login()` de Django encadena tres efectos:

| Efecto | Para qué |
| --- | --- |
| **Rota el identificador de sesión** (`cycle_key`) | Defensa contra fijación de sesión: el `sessionid` que el navegador traía mientras estaba a medio entrar deja de existir. |
| Escribe `_auth_user_id`, `_auth_user_backend` y `_auth_user_hash` **en el servidor** | Es lo que convierte una sesión anónima en una sesión con dueño. |
| Emite la cookie `sessionid` con la llave nueva | Lo único que viaja al navegador. |

Además, `iniciar()` **borra el flujo de acceso** (`flujo_acceso`) para que el paso intermedio de un
acceso ya consumado no se pueda reutilizar, y estampa `persona.ultimo_acceso`.

Propiedades de la cookie (`filey/config/settings.py:128-135` y `:296-297`):

| Ajuste | Valor | Efecto |
| --- | --- | --- |
| `SESSION_COOKIE_AGE` | 12 h | Misma duración que tenía el *refresh token* al que sustituye. |
| `SESSION_SAVE_EVERY_REQUEST` | `True` | La cuenta corre desde la última actividad, no desde el login. |
| `SESSION_COOKIE_HTTPONLY` | `True` | JavaScript no la puede leer. |
| `SESSION_COOKIE_SAMESITE` | `Lax` | No viaja en peticiones cross-site. |
| `SESSION_COOKIE_SECURE` | `True` *(solo `DEBUG=False`)* | Solo por HTTPS. |

## 3. Qué manda el navegador en cada petición

Dos cosas, y ninguna es una credencial de larga vida:

1. **`Cookie: sessionid=…`** — automática. `AuthenticationMiddleware` la resuelve a `request.user`
   consultando `django_session` y luego `Persona`.
2. **El token CSRF**, porque la autenticación va en una cookie ambiental y sin esto cualquier sitio
   podría disparar acciones en nombre de quien tenga sesión abierta. Viaja por dos caminos, uno por
   cada modo de la interfaz:
   - `plantillas/base.html:32` — `<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>`, así
     toda petición htmx lo lleva.
   - `{% csrf_token %}` en los formularios, para el camino sin JavaScript (regla 5 de `CLAUDE.md`).

   Por eso `salir` es `@require_POST` (`views.py:578`): un cierre de sesión por GET sería forjable
   desde cualquier página.

## 4. Quién decide si pasa

**El permiso no viaja en la cookie: se vuelve a preguntar a la base de datos en cada petición.**
Los decoradores de `apps/registros/permisos.py` son el único contrato; ningún módulo de dominio
implementa lo suyo.

| Decorador | Comprueba | Si falla |
| --- | --- | --- |
| `requiere_participante` | `peticion.user.is_authenticated` | Redirige a `registros:acceso` |
| `requiere_admin` | Además, `es_administrativa` (`models.py:109` → `roles.exists()`) | `PermissionDenied` (403), no redirección |
| `requiere_modulo(mod, nivel)` | Además, `puede_administrar(...)` (`models.py:120`) | 403 |

Que se recalcule cada vez tiene una ventaja concreta: **revocar un permiso surte efecto al
siguiente clic**, sin esperar a que caduque nada.

> [!warning] Esta capa está derogada en el diseño, no en el código
> `RolPermiso`, `es_administrativa` y `requiere_modulo` los sustituye `AdminFeria` por
> [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>). La pregunta por petición pasará
> de *"¿tiene algún rol?"* a *"¿administra **esta** feria?"*. El mecanismo de sesión descrito arriba
> **no cambia**: lo que cambia es a qué se le pregunta el permiso, no cómo se sostiene la sesión.
> Cuando llegue el middleware de `search_path` ([ADR-0003](<../../adr/0003-una-feria-por-schema.md>))
> tendrá que ir **después** de `AuthenticationMiddleware`, porque necesita saber quién pregunta.

## 5. Por qué el acceso administrativo no revela quién es administrador

Es la pieza no obvia. Tanto la puerta pública como la administrativa admiten que un correo **tiene
cuenta** (la pública lo hace por diseño, al bifurcar entre entrar y registrarse, `CU-REG-001`). Lo
que ninguna de las dos admite es **si esa cuenta administra algo**: esa comprobación ocurre en
`views.py:453`, **después** de acertar el OTP.

El orden es la garantía. Comprobándolo antes, un intento por correo bastaba para levantar la lista
de las cuentas con más poder del sistema. Comprobándolo después, para averiguarlo hay que leer ese
buzón — que es exactamente el requisito que ya impone entrar.

## 6. Las capas que sostienen el OTP

Resumidas, porque cada una está documentada donde se implementa:

- **Del código:** 6 dígitos de `secrets` (CSPRNG), guardado con PBKDF2 —nunca en claro—, un solo
  uso, 3 intentos, 15 minutos, y verificación bajo `select_for_update` para que la concurrencia no
  regale intentos (`services/otp.py`).
- **Por cuenta destino** (resisten el abuso distribuido): 60 s de cool-down entre emisiones, 5
  emisiones por ventana de 15 min, y *lockout* de 15 min a los 10 fallos acumulados —que un acceso
  exitoso reinicia— (`config/settings.py:247-256`).
- **Por IP** (`comun/limites.py`): 20/min para identificar, 10/min para el OTP. Es la capa
  deliberadamente más débil; ver §7.
- **Fail-closed en el correo:** si el envío falla, el código se marca usado. Un OTP que nadie
  recibió no queda vivo.
- **Cuenta inactiva:** `_persona_por_correo` (`views.py:52`) filtra por `estado = activa`, así que
  una cuenta dada de baja no puede ni pedir código.

---

## 7. Lo que este mecanismo **no** cubre

No son defectos del diseño de sesión —que es correcto— sino huecos reales en lo que lo rodea.
Se listan aquí para que nadie los descubra dos veces.

| # | Hueco | Impacto | Dónde |
| --- | --- | --- | --- |
| 1 | **`X-Forwarded-For` se toma por la izquierda.** La mayoría de los proxies *añaden* la IP real por la derecha en vez de reescribir la cabecera; si el de producción es de esos, el primer valor es el que mandó el cliente y cualquiera puede rotarlo para esquivar el límite por IP desde una sola máquina. **Falta verificar qué hace el proxy de Render**; lo robusto es contar desde la derecha con un número conocido de proxies de confianza. | El límite por IP es evadible; los límites por cuenta destino (§6) siguen en pie y son los que de verdad frenan el abuso. | `comun/limites.py:59-62` |
| 2 | **`LocMemCache` en producción.** Cada worker lleva su propio contador, así que con `--workers 3` el límite real se triplica. | Igual que arriba: debilita solo la capa por IP. | `comun.E001` lo rechaza en `check --deploy`, pero `start.sh` no configura `REDIS_URL`. |
| 3 | **No hay forma de cerrar las sesiones de una cuenta.** Poner `estado = inactiva` impide **nuevos** accesos, pero las sesiones ya abiertas siguen vivas hasta 12 h: los decoradores miran `is_authenticated` (`is_active`), un campo distinto que nada escribe. Y como las cuentas no tienen contraseña, `get_session_auth_hash` nunca cambia, así que tampoco existe el "cerrar sesión en todas partes" que Django da gratis. | Dar de baja a alguien no es inmediato. Hoy la única vía es borrar sus filas de `django_session`. | `models.py:94`, `permisos.py:46/58` |
| 4 | **Sesión de 12 h deslizante y sin tope absoluto.** Con `SESSION_SAVE_EVERY_REQUEST` se renueva indefinidamente mientras haya actividad. | Largo para un panel administrativo, sobre todo en equipos compartidos. | `settings.py:128-129` |
| 5 | **`/django-admin/` se autentica con contraseña y sin límite de intentos.** Es la única contraseña del sistema y da acceso total a los datos; Django no trae *throttling* en esa pantalla. | La cuenta más poderosa está protegida por el mecanismo más débil, justo el que el resto del sistema evita. | `config/urls.py`, `management/commands/ensure_superuser.py` |
| 6 | **El teléfono se comprueba sin restricción en base de datos** (`registro`, E2). Dos altas simultáneas con el mismo teléfono pasan las dos. | Integridad de datos, no seguridad. También admite si un teléfono ya está registrado. | `views.py` (`registro`) |

Lo que sí está bien atado y conviene no tocar sin pensarlo: `DEBUG` cae a `False` por omisión, el
arranque **aborta** si `DJANGO_SECRET_KEY` sigue siendo la de ejemplo (`settings.py:35-41`), y en
producción se activan HSTS con `preload`, redirección a HTTPS, `nosniff`, `Referrer-Policy` y
cookies `Secure`.

---

## Documentos relacionados

- [`CU-REG-002`](<CU-REG-002 Iniciar sesion como usuario externo (OTP).md>) · [`CU-REG-003`](<CU-REG-003 Iniciar sesion como usuario administrativo (OTP).md>) · [`CU-REG-004`](<CU-REG-004 Cerrar sesion.md>)
- [`Modelo de datos - Registros`](<Modelo de datos - Registros.md>) — `Persona`, `SesionOTP`
- [ADR-0002](<../../adr/0002-migracion-de-registro-al-monolito.md>) — por qué se fue el JWT
- [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>) — a dónde va el control de acceso
