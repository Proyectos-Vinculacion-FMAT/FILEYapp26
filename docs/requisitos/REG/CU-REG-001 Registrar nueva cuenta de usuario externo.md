---
estado: aceptado
version: "0.3"
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
fecha: 2026-06-22
fecha_actualizacion: 2026-08-25
id: CU-REG-001
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-001 Registrar nueva cuenta de usuario externo

## Objetivo

Permitir que una persona que nunca ha usado el sistema FILEY cree su cuenta con datos mínimos (correo, teléfono, nombre y apellidos, país y —dentro de México— estado y ciudad), quedando lista para autenticarse con OTP y acceder al módulo correspondiente.

> [!success] Implementado el 2026-08-25
> El formulario de alta pide ya los cinco campos (`nombre`, `primer_apellido`,
> `segundo_apellido`, `telefono`, `pais`) y los guarda por separado. El país es un `<select>`
> con el catálogo ISO 3166-1 (`filey/apps/registros/paises.py`) renderizado en el servidor, así
> que la pantalla sigue funcionando sin JavaScript. Lo único de este CU que **no** está
> implementado es la segunda precondición — ver el aviso más abajo.

> [!success] Estado y ciudad, añadidos el 2026-08-31
> Dos campos más, **condicionados al país**: solo se piden si es México. Un catálogo de 32
> entidades mexicanas no describe una dirección en Bogotá, y una ciudad sin estado que la
> sitúe tampoco. El estado es un `<select>` con las entidades federativas
> (`filey/apps/registros/estados_mx.py`), **Yucatán por omisión**; la ciudad es texto libre y
> **opcional**.
>
> Los esconde Alpine al cambiar el país, pero la regla no vive ahí: `RegistroForm.clean` los
> descarta si el país no es México, porque un POST fabricado a mano no pasa por la pantalla.
> Sin JavaScript se ven siempre — se pintan de más, no de menos, y el servidor decide igual.

> [!warning] En el código el campo se llama `entidad`, no `estado`
> `Persona.estado` ya existe y es **el estado de la cuenta** (`activa`/`suspendida`). El nuevo
> se llama `entidad` —el término oficial es «entidad federativa»— y su etiqueta en pantalla y
> en este documento sigue siendo «Estado». Por lo mismo, `Persona.estado` pasó a rotularse
> «estado de la cuenta» en el admin.

> [!note] Se guarda el código, no el nombre
> `YUC`, no «Yucatán» — igual que el país guarda `MX` (ISO 3166-2:MX sin el prefijo). El
> nombre de una entidad se escribe de varias formas —«Ciudad de México», «CDMX», «Distrito
> Federal»— y un catálogo libre acaba con cuatro filas para la misma entidad en el mismo
> informe. `Persona.estado_nombre` devuelve el nombre para las fichas que lo guardan como
> texto, como el domicilio fiscal de `STD`.

## Alcance

Core Registros. Aplica a proponentes (EVT), talleristas (TAL), representantes escolares (VIS) y expositores (STD). No aplica a usuarios administrativos — sus cuentas las crea el administrador general (CU-REG-005).

## Actores

### Actor principal

- Usuario externo (persona sin cuenta previa en el sistema)

## Disparador

El usuario ingresa su correo en la pantalla de acceso y el sistema no lo reconoce como cuenta existente.

## Precondiciones

- El correo ingresado no está registrado en la entidad `Persona`.
- El sistema tiene al menos un módulo con convocatoria activa (no se puede registrar si no hay nada abierto).

> [!warning] La segunda precondición **no está implementada** (verificado el 2026-08-05)
> Hoy cualquiera puede crear una cuenta aunque no haya ninguna convocatoria abierta. No es
> exigible todavía: el estado de las convocatorias es un catálogo fijo provisional y no habrá
> dato real hasta que los dominios EVT/TAL/STD/VIS expongan el suyo. **Queda pendiente** decidir
> si se aplica de verdad — vale la pena preguntarse si conviene: bloquear el registro fuera de
> convocatoria impide que alguien prepare su cuenta con antelación, y no aporta seguridad.

## Postcondiciones

### En éxito

- Se crea un nuevo registro en `Persona` con estado `activa`.
- El sistema dispara inmediatamente CU-REG-002 para autenticar la sesión recién creada.

### En fallo

- No se crea ningún registro. El correo queda disponible para un nuevo intento.

## Flujo principal

1. El usuario ingresa su correo electrónico en la pantalla de acceso.
2. El sistema verifica que el correo no existe en `Persona`.
3. El sistema presenta el formulario de registro con los campos: nombre, primer apellido, segundo apellido, teléfono y país (el correo ya está precargado del paso 1). Con **México** seleccionado —que es el valor por omisión— muestra además estado y ciudad.
4. El usuario completa esos campos y confirma. **El segundo apellido y la ciudad son opcionales**; el resto es obligatorio. Si cambia el país a uno distinto de México, estado y ciudad desaparecen y no se piden (A2).
5. El sistema valida formato de correo y teléfono.
6. El sistema verifica que el teléfono no esté ya asociado a otra cuenta.
7. El sistema crea el registro en `Persona` (`estado = activa`, `fecha_registro = ahora`).
8. El sistema continúa automáticamente en CU-REG-002 (envío de OTP para autenticar la sesión).

## Flujos alternos

### A2. País distinto de México

En el paso 4 el usuario elige un país que no es México.

1. El sistema oculta estado y ciudad.
2. La cuenta se crea con los dos campos **vacíos**, que es información correcta y no un hueco:
   nunca se le preguntaron.
3. Si los valores llegan de todos modos —un POST que no pasó por la pantalla— el sistema los
   descarta en vez de guardarlos. Guardar «Yucatán» en la ficha de alguien que vive en Madrid
   haría que una consulta por entidad contara personas que no viven ahí.

### A1. Correo ya registrado

1. En el paso 2, el sistema detecta que el correo ya existe en `Persona`.
2. El sistema informa al usuario que ya tiene cuenta y redirige al flujo de CU-REG-002 sin mostrar el formulario de registro.

## Flujos de excepción

### E1. Formato de correo o teléfono inválido

1. En el paso 5, el sistema detecta que el formato es incorrecto.
2. El sistema resalta el campo en error con un mensaje descriptivo.
3. El flujo no avanza hasta que el campo sea válido.

**Criterios de validación vigentes** (todo es obligatorio salvo el segundo apellido):

| Campo | Regla |
| --- | --- |
| Correo | Formato de correo válido; se normaliza a minúsculas y sin espacios sobrantes. Es la identidad única de la cuenta. |
| Nombre | Mínimo 2 caracteres. Obligatorio. |
| Primer apellido | Mínimo 2 caracteres. Obligatorio. |
| Segundo apellido | **Opcional.** No puede exigirse: hay personas que no lo tienen y la mayoría de los participantes extranjeros usan un solo apellido. |
| País | Obligatorio. Dato de perfil, se reutiliza en cualquier convocatoria de cualquier feria. |
| Estado | Obligatorio **solo si el país es México**; fuera de México no se pide y se guarda vacío. Desplegable de las 32 entidades federativas, con Yucatán por omisión. Se guarda el código de tres letras (`YUC`). |
| Ciudad | **Opcional**, y solo si el país es México. Texto libre: no hay catálogo de municipios que valga la pena mantener para esto, y exigirla dejaría fuera a quien escribe desde una localidad cuyo nombre oficial no conoce. Lo que sitúa a la persona es el estado. |
| Teléfono | Al menos 10 dígitos; se guardan solo los dígitos, descartando espacios, guiones y paréntesis. |

> [!note] Correo y teléfono son **ambos** obligatorios
> El índice de CU-REG dejaba esta pregunta abierta ("¿basta con el correo?"). La implementación
> los exige a los dos, y así queda documentado. Nótese que el alta de cuentas **administrativas**
> (CU-REG-005) sí permite omitir el teléfono — son flujos distintos a propósito.

### E2. Teléfono ya asociado a otra cuenta con correo distinto

1. En el paso 6, el sistema detecta el conflicto.
2. El sistema advierte al usuario que ese teléfono ya está registrado con otro correo.
3. El sistema ofrece dos opciones: usar otro teléfono, o contactar a soporte para resolver el duplicado.
4. El flujo no crea ningún registro hasta resolver el conflicto.

## Datos relevantes

### Entradas

- Correo electrónico
- Nombre, primer apellido y segundo apellido (este último opcional)
- País
- Estado y ciudad, **solo si el país es México** (la ciudad, opcional)
- Teléfono

### Salidas

- Registro `Persona` creado (id, correo, teléfono, nombre, primer_apellido, segundo_apellido, pais, entidad, ciudad, fecha_registro, estado)
- Disparo de CU-REG-002

> [!note] No existe un campo `tipo` en la cuenta
> La v0.1 listaba un atributo `tipo` (externo/administrativo). No se implementó, y a propósito:
> lo que distingue a un administrador es **tener al menos un `RolPermiso`**, no una etiqueta en
> la cuenta. Guardar ambas cosas abriría la puerta a que se contradijeran. Una misma persona
> puede ser proponente y administradora sin ambigüedad (ver CU-REG-005 A1).
