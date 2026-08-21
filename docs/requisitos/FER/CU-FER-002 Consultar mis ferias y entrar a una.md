---
estado: propuesta
version: "0.1"
tags:
  - tipo/caso-de-uso
  - dom/fer
  - tema/permisos
  - tema/navegacion
fecha: 2026-08-21
fecha_actualizacion: 2026-08-21
id: CU-FER-002
dominio: FER
responsable: Hugo Janssen
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-FER-002 Consultar las ferias que administro y entrar a una

## Objetivo

Tras iniciar sesión, mostrar al usuario administrativo las ferias que puede administrar y
dejarle entrar a una. A partir de ese momento, todo lo que ve y modifica pertenece a esa feria.

## Alcance

Core Ferias — navegación posterior al login administrativo. Es el paso que **antes ocupaba la
selección de módulo** (CU-REG-006): primero se elige feria, y ya dentro de ella se elige módulo.
No cubre la autenticación (CU-REG-003) ni las funciones internas de cada panel.

> [!important] Este CU es la primera mitad de lo que era CU-REG-006
> Con el acceso otorgado por feria ([ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>)),
> la pregunta "¿a qué panel entro?" se parte en dos: **a qué feria** (este CU) y, dentro de
> ella, **a qué módulo** (CU-REG-006, reformulado). Quien administra una sola feria no debería
> ver esta pantalla — ver A1.

## Actores

### Actor principal

- Usuario administrativo: cualquier persona con al menos una fila en `AdminFeria`, sea dueña o
  administradora.

## Disparador

El usuario termina de autenticarse por el acceso administrativo (CU-REG-003), o ya dentro de una
feria decide cambiar a otra.

## Precondiciones

- El usuario tiene sesión activa.
- El usuario tiene al menos una fila en `AdminFeria`.

## Postcondiciones

### En éxito

- La feria elegida queda fijada como contexto de la sesión, y el sistema entra a su panel.
- Toda consulta posterior de esa sesión se resuelve **dentro del schema de esa feria**
  ([ADR-0003](<../../adr/0003-una-feria-por-schema.md>)).

### En fallo

- El usuario permanece sin contexto de feria y no entra a ningún panel.

## Flujo principal

1. El sistema consulta las ferias en las que la cuenta tiene acceso.
2. El sistema muestra una tarjeta por feria, con su nombre, su estado (`en preparación`,
   `activa`, `archivada`) y una marca visible en aquellas de las que la persona es **dueña**
   —porque en esas puede además administrar accesos—.
3. El usuario elige una feria.
4. El sistema fija esa feria como contexto de la sesión y abre su panel.

> [!note] Quién decide la lista
> La lista la arma el servidor a partir de `AdminFeria`, nunca la pantalla. Una feria a la que
> la cuenta no tiene acceso **no aparece**: a diferencia de los módulos en CU-REG-006, aquí no
> se muestran opciones deshabilitadas — que exista una feria ajena no es información que este
> usuario deba recibir.

## Flujos alternos

### A1. La cuenta administra una sola feria

1. En el paso 1 el sistema detecta una única fila en `AdminFeria`.
2. El sistema **omite esta pantalla** y entra directamente al panel de esa feria.
3. La pantalla sigue accesible desde el menú, por si más adelante la cuenta gana acceso a otra.

> [!warning] Este salto directo es requisito desde el principio, a diferencia de CU-REG-006 A1
> El caso normal previsto es justamente ese: cada persona del equipo administra **una** feria, la
> vigente. Si el salto no se implementa, prácticamente todos los administradores verán siempre
> una pantalla intermedia con una sola tarjeta. En CU-REG-006 el mismo salto quedó pendiente y
> era tolerable; aquí no lo es.

### A2. Cambiar de feria estando dentro de una

1. El usuario, ya en el panel de una feria, elige volver a esta pantalla desde el menú.
2. Elige otra feria; el sistema cambia el contexto de la sesión y abre el panel de la nueva.
3. Nada del contexto de la feria anterior sobrevive al cambio: ni filtros, ni selección, ni
   listados en curso.

## Flujos de excepción

### E1. La cuenta no administra ninguna feria

1. La cuenta tiene sesión válida pero ninguna fila en `AdminFeria` — nunca tuvo acceso, o se lo
   retiraron (CU-FER-004).
2. El sistema no muestra ninguna feria y explica que la cuenta no administra ninguna, ofreciendo
   ir al portal de participante, que sí le corresponde.
3. No se revela qué ferias existen ni quién las administra.

### E2. Se pide una feria a la que no se tiene acceso

1. El usuario llega directo a la URL de una feria (`/f/<slug>/…`) escribiéndola o desde un
   enlace viejo, sin tener fila en `AdminFeria` para ella — incluye el caso de que se le haya
   retirado el acceso mientras tenía la sesión abierta.
2. El sistema **rechaza la petición en el servidor**, antes de tocar el contenido de esa feria,
   y devuelve el mismo resultado tanto si la feria no existe como si existe y no es suya.
3. El usuario vuelve a la lista de sus ferias.

> [!important] Esta comprobación no es de pantalla, es de cada petición
> Ocultar la tarjeta no protege nada. Quien tenga la URL puede pedirla directamente, así que el
> servidor comprueba `AdminFeria` **en cada petición**, antes de fijar el schema de la feria. Es
> lo mismo que exige CU-REG-006 E1 para los permisos revocados en caliente, y la razón por la
> que "no existe" y "no es tuya" se responden igual: distinguirlas diría a un extraño qué ferias
> hay en el sistema.

## Datos relevantes

### Entradas

- Selección de feria por parte del usuario (o el `slug` en la URL).

### Salidas

- Contexto de feria fijado en la sesión.
- Panel de la feria elegida, abierto.
