---
estado: aprobado
version: 0.1
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - admin
fecha: 2026-06-22
id: CU-REG-005
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-005 Crear cuenta de usuario administrativo y asignar permisos de módulo

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
- El sistema envía al correo de la cuenta nueva las instrucciones para establecer su contraseña (enlace de activación con expiración de 48 horas).

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
7. El sistema envía al correo de la nueva cuenta un enlace de activación para que establezca su contraseña (expiración: 48 horas).
8. El sistema muestra confirmación al administrador general con el estado "Cuenta creada — pendiente de activación".

## Flujos alternos

### A1. La persona ya tiene una cuenta de usuario externo

1. En el paso 5, el sistema detecta que el correo ya existe en `Persona` (era proponente o tallerista).
2. El sistema informa al administrador que la persona ya tiene cuenta externa y pregunta si desea agregarle el rol administrativo de todas formas.
3. El administrador confirma.
4. El sistema crea el `RolPermiso` sobre la `Persona` existente sin alterar sus datos base.
5. La persona podrá iniciar sesión tanto por OTP (para su módulo externo) como por contraseña (para el panel admin) con el mismo correo.

### A2. Reenviar enlace de activación

1. Si el enlace de activación expiró sin que la persona lo usara, el administrador general puede seleccionar la cuenta y presionar "Reenviar enlace de activación".
2. El sistema invalida el enlace anterior y emite uno nuevo con expiración de 48 horas.

### A3. Asignar permisos de solo lectura a un supervisor

1. El administrador selecciona `nivel = lectura` y `modulo = *` (o el módulo específico).
2. El flujo es idéntico al principal.
3. El usuario resultante puede iniciar sesión en el panel admin (CU-REG-003) pero no puede modificar ningún dato — solo visualizar.

## Flujos de excepción

### E1. Correo ya tiene RolPermiso en el mismo módulo

1. En el paso 6, el sistema detecta que ya existe un `RolPermiso` para esa persona en el mismo módulo.
2. El sistema informa al administrador del conflicto y pregunta si desea actualizar el nivel del permiso existente.
3. Si el administrador confirma, el sistema actualiza el `nivel` del `RolPermiso` existente en lugar de crear uno duplicado.

### E2. Enlace de activación no usado en 48 horas

1. La persona no establece contraseña dentro del plazo.
2. El enlace expira automáticamente.
3. La cuenta queda en estado "pendiente de activación" — la persona no puede iniciar sesión hasta que el administrador reenvíe el enlace (flujo A2).

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
- Correo de activación enviado a la nueva cuenta

> [!note]
> La eliminación o desactivación de una cuenta administrativa (dar de baja a Hipólito, revocar permisos) es una acción distinta y se documentará en un CU posterior de administración de usuarios.
