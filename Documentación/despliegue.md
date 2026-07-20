# Despliegue automático a servidor de pruebas (`backend-test`)

Cada vez que se hace *push* (o se fusiona un PR) a la rama **`backend-test`**,
un flujo de GitHub Actions se conecta por SSH al servidor de pruebas, actualiza
el código y reconstruye los contenedores con Docker Compose.

```
PR fusionado ──► push a backend-test ──► GitHub Actions ──► SSH al servidor
                                                              │
                                                              ├─ git reset --hard origin/backend-test
                                                              └─ docker compose up -d --build
```

## Archivos involucrados

| Archivo | Propósito |
| --- | --- |
| `.github/workflows/deploy-backend-test.yml` | Flujo de despliegue (se ejecuta en `push` a `backend-test`). |
| `Dockerfile` | Imagen del backend (gunicorn + `collectstatic` + `migrate`). |
| `docker-compose.yml` | Servicio `web` para el servidor de pruebas. |
| `.dockerignore` | Excluye `virtenv`, `.env`, `.git`, etc. de la imagen. |
| `.env` (solo en el servidor) | Variables sensibles; **no se versiona**. |

---

## 1. Generar la llave SSH de despliegue (dedicada)

Se usa una llave **exclusiva para CI**, revocable y de alcance limitado.
En tu máquina local:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ./filey_deploy_key -N ""
```

Esto genera dos archivos:
- `filey_deploy_key` → **llave privada** (va en un *secret* de GitHub).
- `filey_deploy_key.pub` → **llave pública** (va en el servidor).

### Autorizar la llave pública en el servidor

Copia el contenido de `filey_deploy_key.pub` al `authorized_keys` del usuario
de despliegue en el servidor de pruebas:

```bash
ssh-copy-id -i ./filey_deploy_key.pub usuario@servidor-de-pruebas
# o manualmente:
cat filey_deploy_key.pub | ssh usuario@servidor-de-pruebas \
  'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
```

Verifica que la conexión funcione con la llave nueva:

```bash
ssh -i ./filey_deploy_key usuario@servidor-de-pruebas 'echo OK'
```

> Tras configurar el *secret* en GitHub (paso 2), **borra la copia local** de la
> llave privada: `rm filey_deploy_key`.

---

## 2. Configurar los *secrets* en GitHub

En el repositorio: **Settings → Secrets and variables → Actions → New repository
secret**. Crea:

| Secret | Ejemplo | Descripción |
| --- | --- | --- |
| `TEST_SERVER_SSH_KEY` | *(contenido de `filey_deploy_key`)* | Llave **privada** completa, incluyendo las líneas `-----BEGIN/END-----`. |
| `TEST_SERVER_HOST` | `203.0.113.10` | IP o dominio del servidor de pruebas. |
| `TEST_SERVER_USER` | `deploy` | Usuario SSH en el servidor. |
| `TEST_SERVER_PORT` | `22` | Puerto SSH (opcional; por defecto `22`). |
| `TEST_SERVER_DEPLOY_PATH` | `/home/deploy/FILEYapp26` | Ruta del repositorio clonado en el servidor. |

> Pega la llave privada tal cual, con sus saltos de línea. No la envuelvas en
> comillas.

---

## 3. Preparar el servidor de pruebas (una sola vez)

### 3.1 Instalar Docker y Docker Compose

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker "$USER"   # permite usar docker sin sudo (reingresar)
# El plugin 'docker compose' viene incluido con Docker moderno.
docker compose version
```

### 3.2 Clonar el repositorio

El servidor necesita poder hacer `git pull`. Como el repo es privado, usa una
**llave de despliegue de solo lectura** de GitHub (distinta de la llave SSH del
servidor) o un token de acceso:

```bash
# Opción A: HTTPS con token de solo lectura
git clone https://<TOKEN>@github.com/Proyectos-Vinculacion-FMAT/FILEYapp26.git \
  /home/deploy/FILEYapp26

# Opción B: SSH con una deploy key del repo (recomendada)
#  - Genera una llave en el servidor:  ssh-keygen -t ed25519 -f ~/.ssh/filey_repo
#  - Agrega ~/.ssh/filey_repo.pub como Deploy Key (read-only) en GitHub:
#    Settings → Deploy keys → Add deploy key
git clone git@github.com:Proyectos-Vinculacion-FMAT/FILEYapp26.git \
  /home/deploy/FILEYapp26
```

La ruta usada aquí debe coincidir con `TEST_SERVER_DEPLOY_PATH`.

### 3.3 Crear el archivo `.env` en el servidor

Dentro de la ruta del repo (junto a `docker-compose.yml`), crea `.env`. Estas
son las **variables de entorno del servidor** (nunca se versionan):

```dotenv
# Django
DJANGO_SECRET_KEY=<clave-larga-y-aleatoria>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=servidor-de-pruebas.ejemplo.com,203.0.113.10

# CORS (orígenes del frontend permitidos)
CORS_ALLOWED_ORIGINS=https://frontend-de-pruebas.ejemplo.com

# Resend (envío de correos / OTP)
RESEND_API_KEY=re_xxxxxxsu_clave
DEFAULT_FROM_EMAIL=no-reply@tudominio-verificado.com
```

Genera un `DJANGO_SECRET_KEY` seguro con:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(64))'
```

> `DJANGO_DEBUG=False` en el servidor implica que `DJANGO_ALLOWED_HOSTS`
> **debe** incluir el dominio/IP del servidor, o Django rechazará las
> peticiones.

### 3.4 Primer despliegue manual (verificación)

```bash
cd /home/deploy/FILEYapp26
git checkout backend-test
docker compose up -d --build
docker compose logs -f web   # revisar arranque, migraciones y gunicorn
```

Prueba la API:

```bash
curl -X POST http://localhost:8000/api/auth/otp/request/ \
  -H "Content-Type: application/json" -d '{"email":"prueba@ejemplo.com"}'
```

---

## 4. Cómo funciona el flujo automático

1. Se fusiona un PR (o se hace *push*) a `backend-test`.
2. GitHub Actions ejecuta `deploy-backend-test.yml`:
   - Carga la llave privada desde `TEST_SERVER_SSH_KEY`.
   - Confía en el *host key* del servidor (`ssh-keyscan`).
   - Se conecta por SSH y ejecuta en el servidor:
     ```bash
     cd $TEST_SERVER_DEPLOY_PATH
     git fetch --all --prune
     git checkout backend-test
     git reset --hard origin/backend-test
     docker compose up -d --build
     docker image prune -f
     ```
3. Al reconstruirse, el contenedor aplica migraciones (`migrate`) y arranca
   gunicorn automáticamente.

También puedes lanzarlo manualmente desde la pestaña **Actions → Deploy
backend-test → Run workflow** (gracias a `workflow_dispatch`).

### `concurrency`
El flujo usa un grupo de concurrencia para evitar dos despliegues simultáneos
sobre el mismo servidor.

---

## 5. Datos y persistencia

- La base de datos SQLite se guarda en el volumen Docker `fileyapp_data`
  (montado en `/data`), por lo que **sobrevive a los redepliegues**.
- Los archivos estáticos (admin de Django + DRF) se sirven con **WhiteNoise**
  desde el propio contenedor; no se necesita Nginx para el servidor de pruebas.

> Para producción se recomienda migrar a PostgreSQL (ya está `psycopg2-binary`
> en `requirements.txt`) y colocar un proxy inverso (Nginx/Caddy) con HTTPS al
> frente.

---

## 6. Solución de problemas

| Síntoma | Causa probable / solución |
| --- | --- |
| Actions falla en el paso SSH | Revisa `TEST_SERVER_*`; la llave privada debe estar completa. Prueba `ssh -i llave user@host`. |
| `Permission denied (publickey)` | La llave pública no está en `~/.ssh/authorized_keys` del servidor. |
| `git reset` falla en el servidor | El repo del servidor no puede autenticarse con GitHub (deploy key/token). |
| `DisallowedHost` en las respuestas | Falta el host en `DJANGO_ALLOWED_HOSTS` del `.env`. |
| No llegan los correos OTP | `RESEND_API_KEY` inválida o dominio remitente no verificado en Resend. |
| El admin se ve sin estilos | La imagen no ejecutó `collectstatic` o WhiteNoise no está en el `MIDDLEWARE`. |
