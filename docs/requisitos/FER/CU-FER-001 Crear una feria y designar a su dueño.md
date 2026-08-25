---
estado: propuesta
version: "0.1"
tags:
  - tipo/caso-de-uso
  - dom/fer
  - tema/permisos
  - tema/arquitectura
fecha: 2026-08-21
fecha_actualizacion: 2026-08-21
id: CU-FER-001
dominio: FER
responsable: Hugo Janssen
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-FER-001 Crear una feria y designar a su dueño

## Objetivo

Dar de alta una edición de la feria: registrarla, crear el espacio de base de datos donde vivirá
todo su contenido, y designar a la persona que será su **dueña** — la única que podrá dar acceso
a los demás administradores de esa feria.

## Alcance

Core Ferias. Es la única operación del sistema que ocurre **fuera de toda feria**: quien la
ejecuta no es administrador de ninguna, sino operador de la plataforma. No cubre la
configuración de las convocatorias de la feria (eso es de cada dominio: CU-EVT-001, CU-TAL-001,
CU-STD-034) ni el alta de los demás administradores (CU-FER-003).

## Actores

### Actor principal

- **Operador de la plataforma** — el equipo técnico. No es un rol dentro de ninguna feria; es
  quien opera el sistema que las contiene.

### Actores secundarios

- **Sistema de correo** — avisa a la persona designada como dueña de que ya tiene acceso.

> [!warning] Estado de implementación — este caso de uso no tiene interfaz, y probablemente no la tenga
> Crear una feria no es insertar una fila: implica crear su schema y aplicarle las migraciones
> (ver Flujo principal). Se ejecuta con un **comando de administración en el servidor**, igual
> que hoy se dan de alta los administradores. A diferencia de CU-FER-003, aquí **no está
> previsto construir pantalla**: es una operación de infraestructura, poco frecuente (una al
> año) y que requiere acceso al servidor de todos modos.

## Disparador

El equipo prepara una nueva edición de la feria.

## Precondiciones

- No existe ninguna feria con el mismo `slug`.
- La persona que será dueña tiene correo; puede o no tener ya cuenta en el sistema.

## Postcondiciones

### En éxito

- Existe un registro `Feria` con estado `en_preparacion`.
- Existe su schema en la base de datos, con todas las migraciones de los dominios de contenido
  aplicadas.
- Existe una fila `AdminFeria` para la persona designada, con `es_dueño = verdadero` y
  `creado_por` nulo (nadie dentro de la feria le dio ese acceso).
- La persona dueña recibe un **correo de aviso** con el enlace al panel de su feria. El OTP no
  se envía aquí: llega cuando entra al acceso e ingresa su correo (CU-REG-003).

### En fallo

- No queda una feria a medias: o existen el registro, el schema migrado y el dueño, o no existe
  ninguno de los tres (ver E2).

## Flujo principal

1. El operador ejecuta el alta indicando: nombre de la edición, `slug`, correo de la persona
   dueña y, si la cuenta no existe todavía, su nombre.
2. El sistema valida el `slug`: sin acentos ni espacios, y no usado por ninguna otra feria.
3. El sistema crea el registro `Feria` con estado `en_preparacion`.
4. El sistema crea el schema `feria_<slug>` en la base de datos.
5. El sistema aplica **todas las migraciones de los dominios de contenido** sobre ese schema.
6. El sistema busca la `Persona` por correo: si no existe, la crea; si existe, la reutiliza sin
   modificar sus datos (es la misma cuenta que ya usa en otras ferias).
7. El sistema crea la fila `AdminFeria` con `es_dueño = verdadero`.
8. El sistema envía a la persona dueña el correo de aviso con el enlace a `/f/<slug>/`.
9. El sistema confirma al operador el alta, indicando el schema creado y quién quedó como dueño.

## Flujos alternos

### A1. La persona dueña ya tiene cuenta en el sistema

1. En el paso 6 el correo ya existe en `Persona` — por ejemplo, porque fue proponente en una
   edición anterior, o porque es dueña o administradora de otra feria.
2. El sistema reutiliza esa cuenta tal cual y solo crea la fila `AdminFeria`.
3. La persona entra con el mismo correo y el mismo OTP de siempre; lo único nuevo es que ahora
   le aparece esta feria entre las que administra (CU-FER-002).

### A2. Alta sin aviso por correo

1. El operador indica que no se envíe el correo (útil al preparar ediciones con antelación o al
   recrear un entorno).
2. Se ejecutan los pasos 1-7 y 9; se omite el 8. La feria y su dueño quedan igual de válidos.

## Flujos de excepción

### E1. El `slug` ya está en uso o no es válido

1. En el paso 2 el `slug` está tomado por otra feria, o contiene caracteres no permitidos.
2. El sistema rechaza el alta sin crear nada e indica el motivo.
3. No se toca la feria existente que ya usaba ese `slug`.

> [!important] Por qué el `slug` no se puede reutilizar ni cambiar
> Determina el prefijo de la URL (`/f/2027/…`) y el nombre del schema. Cambiarlo rompería todos
> los enlaces ya compartidos y dejaría el schema anterior huérfano; reutilizarlo apuntaría dos
> ferias al mismo contenido.

### E2. Falla la creación del schema o alguna migración

1. En los pasos 4-5 la base de datos rechaza la operación (permisos insuficientes, migración
   incompatible, conexión caída).
2. El sistema **deshace lo hecho**: no deja registro `Feria` sin schema, ni schema a medio
   migrar con un registro que lo dé por bueno.
3. El sistema informa el error real al operador. No se crea ningún `AdminFeria` ni se envía
   ningún correo.

> [!note] Por qué esta excepción se trata más duro que las demás
> Una feria registrada pero sin schema migrado es peor que no tenerla: sus administradores
> pueden entrar y la aplicación revienta contra tablas que no existen, a mitad de operación y
> sin una causa evidente.

### E3. Falla el envío del correo de aviso

1. En el paso 8 el servicio de correo devuelve error.
2. **El alta no se deshace**: la feria, su schema y su dueño ya son válidos y la persona puede
   entrar en cuanto conozca la dirección.
3. El sistema advierte al operador de que el aviso no salió e indica cómo reenviarlo.

*(Mismo criterio que CU-FER-003 E2 y que el alta administrativa previa: cuando el correo es
cortesía informativa y no una credencial, un fallo de envío no invalida lo hecho. Compárese con
CU-REG-002 E3, donde el correo **es** la credencial y por eso sí anula el código.)*

## Datos relevantes

### Entradas

- Nombre de la edición
- `slug` (prefijo de URL y nombre del schema)
- Correo de la persona dueña
- Nombre de la persona dueña (solo si la cuenta no existe todavía)

### Salidas

- Registro `Feria` (`estado = en_preparacion`)
- Schema `feria_<slug>` creado y migrado
- Registro `AdminFeria` con `es_dueño = verdadero` y `creado_por` nulo
- Correo de aviso a la persona dueña
- Registro `Persona` creado o reutilizado

> [!note] La feria nace vacía y cerrada al público
> Crear la feria no abre ninguna convocatoria. El estado `en_preparacion` deja entrar a sus
> administradores pero no la publica; cada dominio abre su propia convocatoria por separado, ya
> dentro de la feria.
