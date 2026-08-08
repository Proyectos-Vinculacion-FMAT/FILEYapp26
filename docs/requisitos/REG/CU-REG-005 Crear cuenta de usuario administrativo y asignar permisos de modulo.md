---
estado: aprobado
version: 0.3
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - admin
  - otp
fecha: 2026-06-22
fecha_actualizacion: 2026-08-05
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
> `RolPermiso`**. No se establece contraseña: la cuenta queda lista de inmediato para iniciar
> sesión por OTP. A partir de ese alta, el correo queda **reconocido como administrador** y
> recibe su OTP cuando la persona entra al login administrativo (CU-REG-003); un correo que el
> superusuario no ha dado de alta como administrador no recibe OTP en el acceso administrativo.

> [!important] Cambio 2026-08-05 — sí se envía un correo de aviso al dar de alta
> La v0.2 afirmaba que **no se envía ningún correo** al momento del alta. En la práctica eso
> dejaba a la persona sin enterarse de que ya tenía acceso: nadie le avisaba de que existía un
> panel ni por dónde entrar. Se decidió enviar un **correo de aviso de alta** con el enlace al
> acceso administrativo. Sigue siendo cierto lo esencial de la v0.2: **el OTP no se envía en
> este momento**, sino cuando la persona entra al login (CU-REG-003).
>
> El enlace del aviso **no lleva ningún token y no caduca**: lo que autentica es el OTP que
> llega a ese mismo correo al entrar. Por eso el enlace no es un secreto y no hay nada que
> revocar si el correo se reenvía o se filtra.

> [!warning] Estado de implementación — este CU está implementado **sin interfaz**
> El flujo principal descrito abajo (pantalla de gestión de usuarios en el panel de superadmin)
> es el **requisito objetivo**, y **todavía no existe**. Hoy el alta se realiza mediante un
> **comando de administración que se ejecuta en el servidor**, documentado en `registro/README.md`.
> Las diferencias de comportamiento respecto al flujo con pantalla están señaladas en cada paso.
> Construir la pantalla queda pendiente para una entrega posterior.

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
- La cuenta queda lista para iniciar sesión por OTP de inmediato.
- Se envía a la persona un **correo de aviso** con el enlace al acceso administrativo. **El OTP no se envía aquí**: se genera cuando la persona entra al login administrativo e ingresa su correo (CU-REG-003).
- A partir del alta, el correo queda reconocido como administrador ("activo"); un correo que no ha sido dado de alta como administrador no recibe OTP en el acceso administrativo (CU-REG-003 A3).

### En fallo

- No se crea ningún `RolPermiso`. Si se creó un registro `Persona` nuevo durante el flujo, se deja sin permiso hasta que el administrador lo resuelva.
- **Si lo que falla es únicamente el correo de aviso, el alta NO se deshace** (ver E2): el permiso ya es válido y la persona puede entrar igual, así que revertirlo causaría más daño que el aviso perdido. Esto es deliberadamente distinto de CU-REG-002 E3, donde un envío fallido sí anula el código — allí el correo *es* la credencial; aquí es solo cortesía informativa.

## Flujo principal

1. El administrador general accede a la sección "Gestión de usuarios" en el panel de superadmin.
2. El administrador selecciona "Nueva cuenta administrativa".
3. El sistema presenta el formulario con los campos: correo, nombre completo, teléfono, módulo (`EVT` / `TAL` / `STD` / `VIS` / `*`) y nivel (`lectura` / `edicion`).
4. El administrador completa el formulario y confirma.
5. El sistema verifica si el correo ya existe en `Persona`:
   - Si no existe: crea el registro en `Persona`.
   - Si ya existe (ej. la persona era antes un proponente externo): reutiliza el registro existente sin modificarlo.
6. El sistema crea el registro en `RolPermiso` con el módulo y nivel indicados.
7. El sistema envía a la persona el **correo de aviso de alta**, con el enlace al acceso administrativo. El OTP no se envía aquí: llegará cuando la persona entre al login (CU-REG-003).
8. El sistema muestra confirmación al administrador general con el estado "Cuenta creada — lista para iniciar sesión".

> [!note] Cómo se ejecuta hoy, sin la pantalla de los pasos 1-4
> El alta se hace con un comando en el servidor que recibe el correo, el nombre, el módulo y el
> nivel, y realiza los pasos 5 a 7 tal como están descritos. Solo cambia **quién y cómo se
> introducen los datos**, no lo que el sistema hace con ellos. El comando permite además omitir
> el aviso (útil en altas masivas) y reenviarlo por separado si falló.
>
> **Consecuencia a tener presente:** mientras no exista la pantalla, ningún cliente (Hipólito,
> Elvira) puede dar de alta administradores por sí mismo — depende siempre del equipo técnico.

## Flujos alternos

### A1. La persona ya tiene una cuenta de usuario externo

1. En el paso 5, el sistema detecta que el correo ya existe en `Persona` (era proponente o tallerista).
2. El sistema informa al administrador que la persona ya tiene cuenta externa y pregunta si desea agregarle el rol administrativo de todas formas.
3. El administrador confirma.
4. El sistema crea el `RolPermiso` sobre la `Persona` existente sin alterar sus datos base. Como excepción, si la cuenta existente no tenía nombre registrado, se completa con el indicado en el alta.
5. La persona usa el mismo correo y el mismo mecanismo (OTP) para todo; lo único que cambia es el destino tras iniciar sesión según sus `RolPermiso` (portal público para su módulo externo, panel administrativo para su nuevo rol).

> [!note] Sin la pantalla, no hay confirmación (pasos 2-3)
> El comando reutiliza la cuenta existente y añade el permiso **sin preguntar**, informando de
> lo que hizo. La confirmación es una salvaguarda de la interfaz pendiente; hoy la responsabilidad
> recae en quien ejecuta el comando.

### A2. Asignar permisos de solo lectura a un supervisor

1. El administrador selecciona `nivel = lectura` y `modulo = *` (o el módulo específico).
2. El flujo es idéntico al principal.
3. El usuario resultante puede iniciar sesión en el panel admin (CU-REG-003) pero no puede modificar ningún dato — solo visualizar.

## Flujos de excepción

### E1. Correo ya tiene RolPermiso en el mismo módulo

1. En el paso 6, el sistema detecta que ya existe un `RolPermiso` para esa persona en el mismo módulo.
2. El sistema informa al administrador del conflicto y pregunta si desea actualizar el nivel del permiso existente.
3. Si el administrador confirma, el sistema actualiza el `nivel` del `RolPermiso` existente en lugar de crear uno duplicado.
4. **No se vuelve a enviar el correo de aviso**: la persona ya fue notificada en su alta original y no hay nada nuevo que comunicarle. El aviso puede reenviarse aparte si hiciera falta.
5. La no duplicación está garantizada por el propio almacenamiento (un único permiso por persona y módulo), no solo por esta comprobación.

> [!note] Sin la pantalla, no hay confirmación (paso 2)
> El comando actualiza el nivel directamente e informa de que lo hizo.

### E2. Fallo en el envío del correo de aviso

1. En el paso 7, el servicio de correo devuelve error.
2. **El alta se conserva**: la `Persona` y el `RolPermiso` ya están creados y la cuenta puede iniciar sesión con normalidad.
3. El sistema advierte a quien ejecutó el alta de que el aviso no salió, e indica cómo reenviarlo.
4. Si el aviso nunca llega, la persona puede entrar igualmente en cuanto alguien le comparta la dirección del acceso administrativo.

## Datos relevantes

### Entradas

- Correo electrónico de la nueva cuenta
- Nombre completo
- Teléfono (opcional en el alta administrativa, a diferencia del registro externo de CU-REG-001, donde es obligatorio)
- Módulo (`EVT` / `TAL` / `STD` / `VIS` / `*`)
- Nivel de permiso (`lectura` / `edicion`)

### Salidas

- Registro `Persona` creado o reutilizado
- Registro `RolPermiso` creado (o actualizado en E1)
- Correo de aviso de alta enviado a la persona (con enlace al acceso administrativo, sin token)
- Cuenta lista para iniciar sesión por OTP (sin contraseña ni enlace de activación)

> [!note]
> La eliminación o desactivación de una cuenta administrativa (dar de baja a Hipólito, revocar permisos) es una acción distinta y se documentará en un CU posterior de administración de usuarios.
