---
estado: implementado
version: "1.0"
tags:
  - tipo/caso-de-uso
  - dom/fer
  - tema/permisos
fecha: 2026-08-21
fecha_actualizacion: 2026-08-26
id: CU-FER-004
dominio: FER
responsable: Hugo Janssen
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-FER-004 Retirar el acceso de un administrador de mi feria

## Objetivo

Permitir que el dueño de una feria quite el acceso administrativo de una persona sobre esa
feria, con efecto inmediato incluso si esa persona tiene la sesión abierta.

## Alcance

Core Ferias — panel de la feria, sección de accesos. Solo ejecutable por el dueño de la feria.
No borra la cuenta de la persona ni afecta a su acceso a otras ferias ni a su condición de
participante.

## Actores

### Actor principal

- **Dueño de la feria**.

## Disparador

Alguien deja el equipo de la feria, cambia de responsabilidad, o se dio acceso por error.

## Precondiciones

- El actor tiene sesión activa y es dueño de la feria en la que opera.
- La persona a retirar tiene una fila `AdminFeria` en esa feria y **no es la dueña**.

## Postcondiciones

### En éxito

- La fila `AdminFeria` de esa persona en esta feria deja de existir.
- La persona pierde el acceso al panel **en su siguiente petición**, aunque tenga la sesión
  abierta.
- La cuenta de la persona sigue existiendo, con su historial intacto, y conserva el acceso a
  cualquier otra feria que administre.

### En fallo

- El acceso permanece tal como estaba.

## Flujo principal

1. El dueño entra a la sección de accesos del panel de su feria.
2. El sistema muestra quién administra la feria.
3. El dueño elige retirar el acceso de una persona.
4. El sistema pide confirmación, indicando que la persona perderá el acceso a esta feria de
   inmediato y qué conserva (su cuenta y sus otras ferias).
5. El dueño confirma.
6. El sistema elimina la fila `AdminFeria` y actualiza la lista.

> [!note] Por qué la confirmación explica lo que **no** pasa
> Retirar un acceso se parece peligrosamente a borrar una cuenta. Decir en la confirmación que
> la persona conserva su cuenta y sus demás ferias evita que el dueño dude de si está causando
> un daño mayor del que quiere (ley de Postel aplicada al texto: ser explícito al emitir).

## Flujos alternos

### A1. La persona tenía la sesión abierta

1. La persona está dentro del panel de la feria cuando se le retira el acceso.
2. En su siguiente petición, el servidor comprueba `AdminFeria`, no lo encuentra y la saca del
   panel (CU-FER-002 E2).
3. No hace falta esperar a que caduque nada: la comprobación ocurre en cada petición, no al
   iniciar sesión.

## Flujos de excepción

### E1. Quien lo intenta no es el dueño

1. Un administrador de la feria intenta retirar a otro.
2. El sistema rechaza la operación en el servidor y explica que solo el dueño administra los
   accesos de la feria.

### E2. Se intenta retirar al dueño

1. El dueño intenta retirarse a sí mismo, o retirar la fila con `es_dueño = verdadero`.
2. El sistema lo rechaza: una feria no puede quedarse sin dueño, porque nadie podría volver a
   dar acceso a nadie.
3. El sistema indica que la salida es **transferir la propiedad** antes de retirarse.

> [!warning] La transferencia de propiedad todavía no existe
> Este flujo señala la salida correcta, pero el caso de uso que la implementa está **pendiente
> de decidir** (ver [`Modelo de datos - Ferias`](<Modelo de datos - Ferias.md>) §6). Mientras
> tanto, un dueño que deja el proyecto obliga a que el operador de la plataforma reasigne la
> propiedad por comando. Es una dependencia del equipo técnico que conviene quitar antes de que
> haya varias ferias en operación.

## Datos relevantes

### Entradas

- Persona a la que se retira el acceso.

### Salidas

- Registro `AdminFeria` eliminado.
- La cuenta `Persona` intacta, con sus demás accesos.

> [!note] Se elimina la fila, no se marca como inactiva
> El acceso a una feria no tiene estados: se tiene o no se tiene. Guardar filas retiradas
> obligaría a que cada comprobación recordara filtrarlas — el mismo tipo de error que
> [ADR-0003](<../../adr/0003-una-feria-por-schema.md>) evita con los schemas. Si más adelante
> hace falta saber quién tuvo acceso y cuándo, eso es una bitácora aparte, no un estado de esta
> tabla.

---

## Estado de implementación

Construido el 2026-08-26, junto con CU-FER-003 y sobre la misma pantalla.

| Pieza | Dónde |
| --- | --- |
| La regla, incluido E2 | `filey/apps/ferias/servicios/accesos.py::retirar_acceso` |
| La confirmación y el retiro | `filey/apps/ferias/views_accesos.py::retirar_acceso` |
| Quién puede (E1) | `filey/apps/ferias/permisos.py::requiere_dueno_feria` |
| Las pruebas | `filey/apps/ferias/pruebas/test_accesos.py` |

> [!important] La confirmación es una pantalla, no un `confirm()` del navegador
> Por dos motivos. Toda pantalla del sistema funciona sin JavaScript, y un diálogo del navegador
> no da sitio para explicar en qué **no** consiste esto — que es justo el trabajo del paso 4.
>
> El retiro ocurre en un **POST**. Si ocurriera en el GET de la confirmación, bastaría con que
> alguien precargara el enlace para quitarle el acceso a un administrador; hay una prueba que
> lo fija.

> [!note] El dueño no tiene botón de retiro, y la fila tampoco se puede retirar por POST
> En la lista, la columna de acciones del dueño dice *"La propiedad se transfiere, no se
> retira"*. El servicio rechaza igual el intento si el POST llega fabricado a mano: E2 no puede
> depender de que una plantilla se acuerde de esconder algo.

### Lo que quedó fuera

- **La transferencia de propiedad**, que es la salida que E2 señala, sigue sin existir (ver
  [`Modelo de datos - Ferias`](<Modelo de datos - Ferias.md>) §6). Hasta que exista, un dueño
  que deja el proyecto obliga a que el operador reasigne la propiedad por consola.
- **No hay bitácora** de accesos retirados: la fila se elimina, y eso es deliberado (ver la nota
  al final de *Datos relevantes*).
