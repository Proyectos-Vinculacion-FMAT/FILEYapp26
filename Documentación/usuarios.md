# Aplicación `usuarios`

Gestiona la autenticación de la API mediante **códigos de un solo uso (OTP)**
enviados por correo electrónico. No se utilizan contraseñas: el acceso se
concede validando un código temporal y devolviendo tokens JWT
([SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)).

Existen dos tipos de cuenta, diferenciados por el campo `is_staff` del modelo
`User` de Django:

| Tipo de cuenta | `is_staff` | Rol en el token (`role`) | Cómo se crea |
| --- | --- | --- | --- |
| Usuario normal | `False` | `user` | Autorregistro (`/register/`) |
| Administrador | `True` | `admin` | Manualmente (`createsuperuser` o el panel `/admin/`) |

El frontend distingue el tipo de acceso leyendo la reivindicación (*claim*)
`role` incluida en el token JWT.

---

## Modelos

### `Profile`
Datos adicionales del usuario que no cubre el modelo `User` de Django.

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `user` | `OneToOneField(User)` | Usuario asociado. |
| `phone` | `CharField(20)` | Teléfono del usuario. |
| `created_at` | `DateTimeField` | Fecha de creación (automática). |

> El tipo de cuenta (admin/usuario) **no** se almacena aquí; se deriva de
> `User.is_staff`.

### `OTPCode`
Código de acceso temporal y de un solo uso, entregado por correo.

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `user` | `ForeignKey(User)` | Usuario al que pertenece el código. |
| `code` | `CharField(128)` | Código **hasheado** (nunca se guarda en texto plano). |
| `created_at` | `DateTimeField` | Fecha de emisión (automática). |
| `expires_at` | `DateTimeField` | Fecha de expiración. |
| `used` | `BooleanField` | Indica si el código ya fue utilizado. |

**Comportamiento clave:**
- Al solicitar un nuevo código, los códigos anteriores no usados se invalidan
  automáticamente.
- Cada código es de un solo uso y expira según `OTP_EXPIRY_MINUTES`
  (5 minutos por defecto).
- La longitud del código se controla con `OTP_CODE_LENGTH` (6 dígitos por
  defecto).

---

## Endpoints

Todos los endpoints cuelgan del prefijo **`/api/auth/`**.

| Método | Ruta | Autenticación | Descripción |
| --- | --- | --- | --- |
| `POST` | `/api/auth/register/` | Ninguna | Registro de usuario normal. |
| `POST` | `/api/auth/otp/request/` | Ninguna | Solicitar un código OTP. |
| `POST` | `/api/auth/login/` | Ninguna | Validar OTP y obtener tokens. |
| `POST` | `/api/auth/logout/` | Bearer (JWT) | Cerrar sesión / invalidar token. |
| `POST` | `/api/auth/refresh/` | Ninguna | Renovar el token de acceso. |

---

### 1. Registro — `POST /api/auth/register/`

Crea una cuenta de **usuario normal** (`is_staff=False`) y **envía
automáticamente** un código OTP al correo para poder iniciar sesión de
inmediato. No permite crear administradores.

**Cuerpo de la petición:**
```json
{
  "email": "usuario@ejemplo.com",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "phone": "9991234567"
}
```

**Respuesta `201 Created`:**
```json
{
  "detail": "Cuenta creada. Se ha enviado un código de acceso a tu correo.",
  "email": "usuario@ejemplo.com"
}
```

**Errores:**
- `400 Bad Request` — el correo ya está registrado, o faltan campos.
```json
{ "email": ["Ya existe una cuenta con este correo."] }
```

> Si el envío del correo falla, la cuenta se crea igualmente y el usuario puede
> volver a solicitar el código con `/otp/request/`.

---

### 2. Solicitar OTP — `POST /api/auth/otp/request/`

Genera y envía un código OTP a un correo **ya registrado**. Funciona tanto para
usuarios como para administradores.

**Cuerpo de la petición:**
```json
{ "email": "usuario@ejemplo.com" }
```

**Respuesta `200 OK` (siempre la misma):**
```json
{ "detail": "Si el correo está registrado, se ha enviado un código de acceso." }
```

> Por seguridad, la respuesta es **genérica e idéntica** exista o no la cuenta,
> para evitar revelar qué correos están registrados (*email enumeration*).

---

### 3. Iniciar sesión — `POST /api/auth/login/`

Valida el código OTP y devuelve los tokens. Sirve para ambos tipos de cuenta.

**Cuerpo de la petición:**
```json
{
  "email": "usuario@ejemplo.com",
  "code": "123456"
}
```

**Respuesta `200 OK`:**
```json
{
  "refresh": "<token_de_refresco>",
  "access": "<token_de_acceso>",
  "role": "user"
}
```

- `access` — token de acceso de corta duración (30 min), para autenticar
  peticiones con el encabezado `Authorization: Bearer <access>`.
- `refresh` — token de larga duración (7 días), para renovar el acceso.
- `role` — `"user"` o `"admin"`. También va incluido como *claim* dentro del JWT.

**Errores:**
- `400 Bad Request` — código o correo inválido, código expirado o ya usado.
```json
{ "non_field_errors": ["Código o correo inválido, o el código ha expirado."] }
```

---

### 4. Cerrar sesión — `POST /api/auth/logout/`

Invalida el token de refresco añadiéndolo a la *blacklist*. Requiere estar
autenticado con un token de acceso válido.

**Encabezados:** `Authorization: Bearer <access>`

**Cuerpo de la petición:**
```json
{ "refresh": "<token_de_refresco>" }
```

**Respuesta `205 Reset Content`** (sin cuerpo).

**Errores:**
- `401 Unauthorized` — no se envió un token de acceso válido.
- `400 Bad Request` — el token de refresco es inválido o ya expiró.

---

### 5. Renovar acceso — `POST /api/auth/refresh/`

Genera un nuevo token de acceso a partir de un token de refresco válido
(endpoint estándar de SimpleJWT). Con la rotación activada, también devuelve un
nuevo token de refresco e invalida el anterior.

**Cuerpo de la petición:**
```json
{ "refresh": "<token_de_refresco>" }
```

**Respuesta `200 OK`:**
```json
{
  "access": "<nuevo_token_de_acceso>",
  "refresh": "<nuevo_token_de_refresco>"
}
```

**Errores:**
- `401 Unauthorized` — el token de refresco es inválido, expiró o está en la
  *blacklist* (por ejemplo, tras cerrar sesión).

---

## Configuración relevante (`settings.py`)

| Ajuste | Valor por defecto | Descripción |
| --- | --- | --- |
| `ACCESS_TOKEN_LIFETIME` | 30 minutos | Duración del token de acceso. |
| `REFRESH_TOKEN_LIFETIME` | 7 días | Duración del token de refresco. |
| `ROTATE_REFRESH_TOKENS` | `True` | Emite un nuevo refresh en cada renovación. |
| `BLACKLIST_AFTER_ROTATION` | `True` | Invalida el refresh anterior al rotar. |
| `OTP_CODE_LENGTH` | `6` | Número de dígitos del código OTP. |
| `OTP_EXPIRY_MINUTES` | `5` | Minutos de validez del código OTP. |

---

## Flujo completo de autenticación

```
Usuario nuevo:
  register/  ──►  (correo con OTP)  ──►  login/  ──►  access + refresh
                                                          │
Uso normal:      Authorization: Bearer <access>  ◄────────┘
                                                          │
Al expirar el access:   refresh/  ──►  nuevo access ◄─────┘

Usuario/Admin existente:
  otp/request/  ──►  (correo con OTP)  ──►  login/  ──►  access + refresh

Cerrar sesión:
  logout/  (con Bearer + refresh)  ──►  refresh invalidado
```

Ver [`notificaciones.md`](./notificaciones.md) para el detalle del envío de
correos (Resend), del que depende este flujo.
