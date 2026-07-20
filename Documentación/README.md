# Documentación de la API — FILEY

Guía de referencia de la API REST (Django + Django REST Framework) del proyecto
FILEY. La API se organiza por aplicaciones; cada una tiene su propio documento.

## Índice

| Aplicación | Documento | Descripción |
| --- | --- | --- |
| `usuarios` | [usuarios.md](./usuarios.md) | Autenticación por OTP (sin contraseña) y emisión de tokens JWT. |
| `notificaciones` | [notificaciones.md](./notificaciones.md) | Capa de servicios de correo electrónico (Resend). |
| Infraestructura | [despliegue.md](./despliegue.md) | Despliegue automático a `backend-test` (GitHub Actions + Docker + SSH). |

## Visión general

- **Framework:** Django 6 + Django REST Framework.
- **Autenticación:** códigos de un solo uso (OTP) enviados por correo +
  tokens JWT ([SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)).
  No se usan contraseñas.
- **Tipos de cuenta:** usuario normal (`role: user`) y administrador
  (`role: admin`), diferenciados por `User.is_staff`. El frontend lee el *claim*
  `role` del token JWT.
- **Correo:** todo el envío de correos vive en la app `notificaciones`
  (proveedor Resend).

## Prefijos de rutas

| Prefijo | Aplicación |
| --- | --- |
| `/api/auth/` | `usuarios` |
| `/admin/` | Panel de administración de Django |

## Puesta en marcha (desarrollo)

```bash
# 1. Dependencias
pip install -r requirements.txt

# 2. Variables de entorno (copiar y completar)
cp .env.example .env
#   -> definir RESEND_API_KEY y DEFAULT_FROM_EMAIL

# 3. Migraciones
python fileyapp/manage.py migrate

# 4. Crear un administrador (is_staff=True)
python fileyapp/manage.py createsuperuser

# 5. Levantar el servidor
python fileyapp/manage.py runserver
```

La API queda disponible en `http://127.0.0.1:8000/`.

## Ejemplo rápido de flujo (con `curl`)

```bash
# 1. Registro de un usuario (envía OTP automáticamente)
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@ejemplo.com","first_name":"Nombre","last_name":"Apellido","phone":"9991234567"}'

# 2. (Alternativa) Solicitar un OTP para una cuenta existente
curl -X POST http://127.0.0.1:8000/api/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@ejemplo.com"}'

# 3. Iniciar sesión con el código recibido
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@ejemplo.com","code":"123456"}'
#   -> devuelve access, refresh y role

# 4. Renovar el token de acceso
curl -X POST http://127.0.0.1:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<token_de_refresco>"}'

# 5. Cerrar sesión (invalida el refresh)
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access>" \
  -d '{"refresh":"<token_de_refresco>"}'
```

Consulta cada documento por aplicación para el detalle de cuerpos de petición,
respuestas y errores.
