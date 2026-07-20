# Aplicación `notificaciones`

Concentra **toda la lógica de envío de correos electrónicos** del proyecto. El
resto de las aplicaciones nunca construyen mensajes ni hablan directamente con
el proveedor de correo: importan las funciones de servicio de esta app.

Proveedor de correo: **[Resend](https://resend.com/docs)**.

> Esta app **no expone endpoints HTTP**. Es una capa de servicios interna que
> otras aplicaciones (por ejemplo, [`usuarios`](./usuarios.md)) utilizan.

---

## Estructura

```
notificaciones/
└── services/
    ├── resend_client.py   # Transporte de bajo nivel (habla con Resend)
    └── email.py           # API pública: contenido/plantillas de los correos
```

**Dirección de dependencia:** `usuarios → notificaciones → Resend`.

Si en el futuro se cambia Resend por otro proveedor, **solo cambia
`resend_client.py`**; el resto del proyecto no se ve afectado.

---

## `services/resend_client.py` — transporte de bajo nivel

Único módulo del proyecto que se comunica directamente con Resend.

### `EmailDeliveryError`
Excepción que se lanza cuando un correo no pudo entregarse (falta la API key o
Resend rechaza el envío). Las aplicaciones que llaman al servicio deben
manejarla.

### `send_email(*, to, subject, html, text=None)`
Envía un único correo a través de Resend.

| Parámetro | Tipo | Descripción |
| --- | --- | --- |
| `to` | `str` o lista | Destinatario(s). |
| `subject` | `str` | Asunto. |
| `html` | `str` | Cuerpo en HTML. |
| `text` | `str` (opcional) | Cuerpo en texto plano. |

- **Devuelve:** el `id` del mensaje de Resend si el envío fue exitoso.
- **Lanza:** `EmailDeliveryError` si falta `RESEND_API_KEY` o si Resend rechaza
  el envío.

---

## `services/email.py` — API pública de correos

Módulo que **posee el contenido** de los correos (asunto, cuerpo, plantillas).
Es la superficie que otras apps importan.

### `send_otp_email(to, code)`
Envía un código de acceso (OTP) de inicio de sesión.

| Parámetro | Tipo | Descripción |
| --- | --- | --- |
| `to` | `str` | Correo del destinatario. |
| `code` | `str` | Código OTP a incluir. |

- **Devuelve:** el `id` del mensaje de Resend.
- **Lanza:** `EmailDeliveryError` si la entrega falla.

**Asunto:** `Tu código de acceso FILEY`

El correo se envía en formato **HTML y texto plano**, mostrando el código de
forma destacada e indicando que expira en unos minutos.

**Ejemplo de uso desde otra aplicación:**
```python
from notificaciones.services.email import send_otp_email, EmailDeliveryError

try:
    send_otp_email("usuario@ejemplo.com", "123456")
except EmailDeliveryError:
    # Registrar el error; la operación puede continuar y reintentar el envío.
    ...
```

---

## Configuración (`settings.py` / `.env`)

| Variable | Ubicación | Descripción |
| --- | --- | --- |
| `RESEND_API_KEY` | `.env` | Clave de API de Resend. **Obligatoria para enviar.** |
| `DEFAULT_FROM_EMAIL` | `.env` | Dirección remitente. |

Las variables se leen del archivo `.env` en la raíz del repositorio (un nivel
por encima de `BASE_DIR`). Ver `.env.example` como plantilla.

### Notas sobre el remitente y el dominio

- **Desarrollo:** puede usarse el remitente de pruebas de Resend
  `onboarding@resend.dev`, pero **solo entrega correos a la dirección de correo
  dueña de la cuenta de Resend**.
- **Producción:** es necesario **verificar un dominio** en el panel de Resend y
  usar una dirección de ese dominio (por ejemplo `no-reply@tudominio.com`).

### Manejo de fallos

Si `RESEND_API_KEY` no está configurada o Resend rechaza el envío, se lanza
`EmailDeliveryError`. Las aplicaciones que llaman deciden cómo reaccionar; por
ejemplo, en el registro de `usuarios` el error se registra en el log pero **no
bloquea** la creación de la cuenta: el usuario puede volver a solicitar el
código.

---

## Extensiones futuras

Esta app es el lugar natural para toda nueva notificación por correo del
proyecto (avisos de eventos, alertas a administradores, etc.). El patrón a
seguir:

1. Añadir una función en `services/email.py` que construya el contenido.
2. Reutilizar `send_email(...)` de `resend_client.py` como transporte.
3. (Opcional) Registrar los envíos en un modelo `EmailLog` si se requiere
   auditoría.
