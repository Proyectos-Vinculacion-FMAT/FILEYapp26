---
estado: propuesta
version: 0.1
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - admin
fecha: 2026-06-22
id: CU-REG-003
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-003 Iniciar sesión como usuario administrativo (usuario + contraseña)

## Objetivo

Autenticar a un usuario con rol administrativo (Hipólito, Elvira, administrador general) mediante correo y contraseña, otorgando una sesión persistente con permisos acotados a su módulo. Este mecanismo aplica porque los administradores acceden diariamente durante meses — el OTP de un solo uso generaría fricción innecesaria para ese perfil.

## Alcance

Core Registros — panel de administración. Aplica únicamente a cuentas con `RolPermiso` registrado (`nivel = edicion` o `nivel = lectura`). No aplica a usuarios externos (ver CU-REG-002).

## Actores

### Actor principal

- Usuario administrativo (Hipólito — EVE, Elvira — TAL, Administrador general — todos los módulos)

## Disparador

El usuario accede a la URL del panel de administración (ruta diferenciada del portal público, ej. `/admin`).

## Precondiciones

- El usuario tiene una cuenta en `Persona` con al menos un `RolPermiso` registrado.
- Las credenciales (contraseña) fueron configuradas previamente por el administrador general.

## Postcondiciones

### En éxito

- El sistema emite un JWT de sesión con `persona_id`, `modulo` y `nivel` del `RolPermiso`.
- El usuario es redirigido al panel de su módulo:
  - `modulo = EVE` → panel de Hipólito (gestión de propuestas y programa general).
  - `modulo = TAL` → panel de Elvira (talleres y visitas escolares).
  - `modulo = *` → panel de administrador general (visión de todos los módulos).
  - `modulo = EVE, nivel = lectura` → panel de solo lectura (para "la maestra" u otros supervisores).

### En fallo

- No se emite ningún JWT. El usuario permanece sin sesión en el panel de administración.

## Flujo principal

1. El usuario accede a la URL del panel de administración.
2. El sistema muestra la pantalla de inicio de sesión administrativo (separada visualmente del portal público).
3. El usuario ingresa su correo y contraseña.
4. El sistema verifica que el correo existe en `Persona` y tiene al menos un `RolPermiso`.
5. El sistema valida la contraseña contra el hash almacenado (bcrypt).
6. El sistema emite un JWT de sesión firmado con `persona_id`, `modulo` y `nivel` del permiso.
7. El sistema registra la fecha/hora de último acceso en `Persona`.
8. El sistema redirige al panel correspondiente al módulo del usuario.

## Flujos alternos

### A1. Usuario con permisos en múltiples módulos

1. En el paso 6, el sistema detecta más de un `RolPermiso` para la persona.
2. El sistema presenta una pantalla de selección de módulo ("¿A qué sección deseas entrar?").
3. El usuario selecciona el módulo.
4. El sistema emite el JWT con el módulo seleccionado y redirige.

### A2. Contraseña olvidada

1. El usuario presiona "Olvidé mi contraseña" en la pantalla del paso 2.
2. El sistema solicita el correo registrado.
3. El sistema envía un enlace de restablecimiento de contraseña al correo, con expiración de 30 minutos.
4. El usuario sigue el enlace, ingresa una nueva contraseña y confirma.
5. El sistema actualiza el hash y redirige a la pantalla de inicio de sesión del paso 2.

## Flujos de excepción

### E1. Credenciales incorrectas

1. El correo no existe en `Persona`, no tiene `RolPermiso`, o la contraseña no coincide.
2. El sistema muestra un mensaje genérico ("Correo o contraseña incorrectos") sin especificar cuál falló.
3. El sistema registra el intento fallido. Tras 5 intentos consecutivos fallidos, bloquea la cuenta por 15 minutos.
4. Al desbloquearse, el usuario puede intentar de nuevo o usar el flujo A2.

### E2. Cuenta bloqueada

1. El usuario intenta iniciar sesión mientras la cuenta está bloqueada.
2. El sistema informa que la cuenta está bloqueada temporalmente e indica el tiempo restante.
3. Opcionalmente, el usuario puede usar A2 (restablecer contraseña) para desbloquear de inmediato.

### E3. Cuenta sin RolPermiso administrativo

1. El correo existe en `Persona` pero no tiene ningún `RolPermiso` registrado.
2. El sistema rechaza el acceso al panel y redirige al portal público (donde aplica CU-REG-002).

## Datos relevantes

### Entradas

- Correo electrónico
- Contraseña

### Salidas

- JWT de sesión (persona_id, modulo, nivel, expiración)
- Actualización de último acceso en `Persona`

> [!note]
> La creación de cuentas administrativas y la asignación de `RolPermiso` no forman parte de este CU. Es una acción que realiza el administrador general desde el panel de superadmin y se documentará en un CU de administración de usuarios.
