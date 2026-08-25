---
estado: propuesta
version: "0.1"
tags:
  - tipo/caso-de-uso
  - dom/fer
  - dom/reg
  - tema/permisos
fecha: 2026-08-21
fecha_actualizacion: 2026-08-21
id: CU-FER-003
dominio: FER
responsable: Hugo Janssen
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-FER-003 Dar de alta un administrador en mi feria

> [!important] Reemplaza a CU-REG-005
> El alta de cuentas administrativas dejaba de tener sentido tal como estaba escrita: asignaba
> permisos de **módulo y nivel** sobre el sistema entero, y podía ejecutarla cualquier cuenta
> con `modulo = *`. Con [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>) el
> acceso se otorga **por feria** y solo lo concede **el dueño de esa feria**. Lo que sobrevive
> de CU-REG-005 es su mecánica de provisión —reutilizar la cuenta si ya existe, avisar por
> correo, y que el OTP no se envíe en este momento—; lo que se va es el modelo de permisos.

## Objetivo

Permitir que el dueño de una feria dé acceso administrativo a otra persona **sobre esa feria**,
dejándola lista para entrar al panel de inmediato con su OTP habitual.

## Alcance

Core Ferias — panel de la feria, sección de accesos. Solo ejecutable por el dueño de la feria en
la que se opera. No otorga acceso a ninguna otra feria, ni convierte a la persona en dueña.

## Actores

### Actor principal

- **Dueño de la feria** (fila en `AdminFeria` con `es_dueño = verdadero` para esta feria).

### Actores secundarios

- **Sistema de correo** — envía el aviso de alta.

> [!warning] Estado de implementación — hoy sin interfaz
> Igual que el alta administrativa anterior, mientras no exista la pantalla de accesos el alta se
> realiza con un **comando de administración en el servidor**. La diferencia respecto a
> CU-FER-001 es que aquí **sí está previsto construir la pantalla**: es una acción del cliente
> —del dueño de la feria—, no del equipo técnico, y mientras no exista, ningún dueño puede
> ejercer la responsabilidad que este modelo le asigna sin pedírselo al equipo.

## Disparador

El dueño necesita que otra persona (coordinador, asistente) pueda operar el panel de su feria.

## Precondiciones

- El actor tiene sesión activa **y es dueño de la feria en la que está operando**.
- La feria existe y no está `archivada`.

## Postcondiciones

### En éxito

- Existe (o se reutiliza) un registro `Persona` para el correo indicado.
- Existe una fila `AdminFeria` para esa persona y esta feria, con `es_dueño = falso` y
  `creado_por` = el dueño que la creó.
- La persona puede entrar al panel de esta feria de inmediato, con su OTP habitual.
- La persona recibe un **correo de aviso** con el enlace al panel de la feria. **El OTP no se
  envía aquí**: se genera cuando entra al acceso e ingresa su correo (CU-REG-003).

### En fallo

- No se crea ninguna fila `AdminFeria`. Si se creó una `Persona` nueva durante el flujo, queda
  sin acceso hasta que el dueño lo resuelva — es una cuenta de participante normal, no un cabo
  suelto con permisos.
- **Si lo único que falla es el correo de aviso, el alta NO se deshace** (ver E3).

## Flujo principal

1. El dueño entra a la sección de accesos del panel de su feria.
2. El sistema muestra quién administra hoy esa feria, marcando cuál es el dueño.
3. El dueño elige "Dar acceso" e indica el correo y, si la cuenta no existe, el nombre.
4. El sistema verifica si el correo ya existe en `Persona`: si no, crea el registro; si sí, lo
   reutiliza sin modificarlo.
5. El sistema crea la fila `AdminFeria` para esta feria, con `es_dueño = falso`.
6. El sistema envía el correo de aviso con el enlace al panel de la feria.
7. El sistema confirma al dueño, y la persona aparece ya en la lista del paso 2.

## Flujos alternos

### A1. La persona ya tiene cuenta en el sistema

1. En el paso 4 el correo ya existe: era proponente, o administra otra feria.
2. El sistema reutiliza la cuenta sin alterar sus datos. Como excepción, si no tenía nombre
   registrado, se completa con el indicado en el alta.
3. La persona entra con el mismo correo y el mismo OTP de siempre. Lo único que cambia es que
   ahora esta feria le aparece entre las que administra (CU-FER-002).

> [!note] Ser administrador de una feria no quita ser participante de otra
> La cuenta es global y no pertenece a ninguna feria. La misma persona puede administrar FILEY
> 2027 y, a la vez, presentar una propuesta como aplicante en FILEY 2028. No hay conflicto: lo
> que decide qué ve es la feria en la que entra y si tiene acceso administrativo **a esa**.

## Flujos de excepción

### E1. Quien lo intenta no es el dueño de la feria

1. Un administrador de la feria —con acceso legítimo a todo su contenido— intenta dar de alta a
   alguien.
2. El sistema **rechaza la operación en el servidor**, no solo ocultando el botón.
3. El sistema explica que solo el dueño de la feria administra sus accesos, e indica quién es.

> [!important] Es el límite que justifica que el dueño exista
> Sin esta comprobación, cualquier administrador podría crear administradores y la
> responsabilidad de quién tiene acceso volvería a diluirse — el problema que
> [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>) resuelve. Ocultar el botón en
> la pantalla no es la protección: la protección es rechazar la petición.

### E2. La persona ya tiene acceso a esta feria

1. En el paso 5 ya existe una fila `AdminFeria` para esa persona y esta feria.
2. El sistema informa de que ya tiene acceso y no crea nada. No hay nivel que actualizar: el
   acceso a una feria no tiene grados.
3. **No se reenvía el correo de aviso**: la persona ya fue notificada en su alta original.
4. La no duplicación está garantizada por el propio almacenamiento (único por feria y persona),
   no solo por esta comprobación.

### E3. Falla el envío del correo de aviso

1. En el paso 6 el servicio de correo devuelve error.
2. **El acceso se conserva**: la fila `AdminFeria` ya existe y la persona puede entrar con
   normalidad.
3. El sistema advierte al dueño de que el aviso no salió e indica cómo reenviarlo.
4. Si el aviso nunca llega, la persona entra igual en cuanto alguien le comparta la dirección
   del panel.

### E4. La feria está archivada

1. La feria tiene estado `archivada`.
2. El sistema rechaza el alta: una edición cerrada se consulta, no se opera, y darle
   administradores nuevos no tiene sentido.

## Datos relevantes

### Entradas

- Correo de la persona a la que se da acceso
- Nombre (solo si la cuenta no existe todavía)

### Salidas

- Registro `Persona` creado o reutilizado
- Registro `AdminFeria` creado (`es_dueño = falso`, `creado_por` = el dueño)
- Correo de aviso con el enlace al panel de la feria
- Cuenta lista para entrar por OTP, sin contraseña ni enlace de activación

> [!note] No se puede crear otro dueño
> Este caso de uso solo crea administradores. La propiedad de la feria se asigna al crearla
> (CU-FER-001) y transferirla es un tema abierto — ver
> [`Modelo de datos - Ferias`](<Modelo de datos - Ferias.md>) §6.
