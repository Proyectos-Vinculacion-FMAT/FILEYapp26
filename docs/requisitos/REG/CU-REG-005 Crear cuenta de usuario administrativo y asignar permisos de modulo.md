---
estado: aprobado
version: 0.2
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - admin
  - otp
fecha: 2026-06-22
fecha_actualizacion: 2026-07-22
id: CU-REG-005
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-005 Crear cuenta de usuario administrativo y asignar permisos de módulo

> [!important] Cambio de decisión (2026-07-22) — provisión por OTP, sin contraseña ni enlace de activación
> En la versión 0.1 este CU enviaba al nuevo administrador un **enlace de activación para
> establecer contraseña** (48 h). Con la unificación del acceso por OTP (ver CU-REG-003),
> provisionar una cuenta administrativa se reduce a **crear la `Persona` (si no existe) y su
> `RolPermiso`**. No se establece contraseña ni se envía ningún correo al momento del alta: la
> cuenta queda lista de inmediato para iniciar sesión por OTP. A partir de ese alta, el correo
> queda **reconocido como administrador** (es decir, "activo" para el acceso administrativo) y
> recibe su OTP cuando la persona entra al login administrativo (CU-REG-003); un correo que el
> superusuario no ha dado de alta como administrador no recibe OTP en el acceso administrativo.

## Objetivo

Permitir al administrador general dar de alta una cuenta para un usuario con rol administrativo (ej. Hipólito, Elvira, supervisores de solo lectura) y asignarle los permisos de módulo correspondientes. Los usuarios administrativos no se auto-registran — sus cuentas son provisionadas por el administrador general antes de que empiecen a operar.

## Alcance

Core Registros — panel de superadmin. Solo ejecutable por una cuenta con `RolPermiso.modulo = *` (administrador general). No aplica a usuarios externos (ver CU-REG-001).

## Actores

### Actor principal

- Administrador general (cuenta con `modulo = *`)

## Disparador

El administrador general necesita dar acceso al panel administrativo a una persona (coordinador, asistente, supervisor).

## Precondiciones

- El actor tiene sesión activa como administrador general (`modulo = *`).
- El correo de la nueva cuenta no está ya registrado en `Persona` con un `RolPermiso` conflictivo.

## Postcondiciones

### En éxito

- Se crea (o reutiliza) un registro en `Persona` para la cuenta nueva.
- Se crea un registro en `RolPermiso` vinculando la persona al módulo y nivel indicados.
- La cuenta queda lista para iniciar sesión por OTP de inmediato. **No se envía ningún correo** al momento del alta: el OTP se genera solo cuando la persona entra al login administrativo e ingresa su correo (CU-REG-003).
- A partir del alta, el correo queda reconocido como administrador ("activo"); un correo que no ha sido dado de alta como administrador no recibe OTP en el acceso administrativo.

### En fallo

- No se crea ningún `RolPermiso`. Si se creó un registro `Persona` nuevo durante el flujo, se deja sin permiso hasta que el admin lo resuelva.

## Flujo principal

1. El administrador general accede a la sección "Gestión de usuarios" en el panel de superadmin.
2. El administrador selecciona "Nueva cuenta administrativa".
3. El sistema presenta el formulario con los campos: correo, nombre completo, teléfono, módulo (`EVE` / `TAL` / `STD` / `*`) y nivel (`lectura` / `edicion`).
4. El administrador completa el formulario y confirma.
5. El sistema verifica si el correo ya existe en `Persona`:
   - Si no existe: crea el registro en `Persona`.
   - Si ya existe (ej. la persona era antes un proponente externo): reutiliza el registro existente sin modificarlo.
6. El sistema crea el registro en `RolPermiso` con el módulo y nivel indicados.
7. El sistema deja la cuenta lista para iniciar sesión por OTP. No se envía ningún correo en este paso: el nuevo administrador podrá acceder cuando entre al login administrativo (CU-REG-003), momento en el que el sistema le enviará su OTP.
8. El sistema muestra confirmación al administrador general con el estado "Cuenta creada — lista para iniciar sesión".

## Flujos alternos

### A1. La persona ya tiene una cuenta de usuario externo

1. En el paso 5, el sistema detecta que el correo ya existe en `Persona` (era proponente o tallerista).
2. El sistema informa al administrador que la persona ya tiene cuenta externa y pregunta si desea agregarle el rol administrativo de todas formas.
3. El administrador confirma.
4. El sistema crea el `RolPermiso` sobre la `Persona` existente sin alterar sus datos base.
5. La persona usa el mismo correo y el mismo mecanismo (OTP) para todo; lo único que cambia es el destino tras iniciar sesión según sus `RolPermiso` (portal público para su módulo externo, panel administrativo para su nuevo rol).

### A2. Asignar permisos de solo lectura a un supervisor

1. El administrador selecciona `nivel = lectura` y `modulo = *` (o el módulo específico).
2. El flujo es idéntico al principal.
3. El usuario resultante puede iniciar sesión en el panel admin (CU-REG-003) pero no puede modificar ningún dato — solo visualizar.

## Flujos de excepción

### E1. Correo ya tiene RolPermiso en el mismo módulo

1. En el paso 6, el sistema detecta que ya existe un `RolPermiso` para esa persona en el mismo módulo.
2. El sistema informa al administrador del conflicto y pregunta si desea actualizar el nivel del permiso existente.
3. Si el administrador confirma, el sistema actualiza el `nivel` del `RolPermiso` existente en lugar de crear uno duplicado.

## Datos relevantes

### Entradas

- Correo electrónico de la nueva cuenta
- Nombre completo
- Teléfono
- Módulo (`EVE` / `TAL` / `STD` / `*`)
- Nivel de permiso (`lectura` / `edicion`)

### Salidas

- Registro `Persona` creado o reutilizado
- Registro `RolPermiso` creado (o actualizado en E1)
- Cuenta lista para iniciar sesión por OTP (sin correo de activación ni contraseña)

> [!note]
> La eliminación o desactivación de una cuenta administrativa (dar de baja a Hipólito, revocar permisos) es una acción distinta y se documentará en un CU posterior de administración de usuarios.
