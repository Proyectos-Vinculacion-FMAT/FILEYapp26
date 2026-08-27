---
estado: propuesta
version: "1.0"
tags:
  - tipo/caso-de-uso
  - dom/std
  - tema/mapa
fecha: 2026-08-27
id: CU-STD-039
dominio: STD
responsable: Hugo Janssen
reglas_de_negocio:
  - RN-01
  - RN-10
  - RN-19
---
# CU-STD-039 Importar el mapa de una convocatoria desde un JSON externo

> [!important] Alcance deliberadamente corto
> Por ahora el sistema **no dibuja mapas**: recibe un JSON hecho fuera, lo traduce a filas y a
> partir de ahí lo vuelve a generar él (CU-STD-037, CU-STD-038). El modo editor del componente y
> su mensaje `saveMap` **quedan fuera de alcance**; el día que entren, este caso de uso es el que
> tendrán que reemplazar o acompañar.
>
> Es lo que convierte el mapa en un dato del sistema en vez de un archivo suelto: hoy
> `filey-map.json` es la fuente y nadie sabe qué versión está viva. Después de importarlo, la
> fuente es la base y el JSON es un formato de intercambio.

## Objetivo

Cargar el showfloor de una convocatoria a partir de un archivo JSON en el formato del componente
de mapa, dejándolo en la base como `MapaShowfloor`, `Stand` y `DecoracionMapa`.

## Alcance

Componente de Stands — administración de la plataforma. Se ejecuta desde el admin de Django de
la edición (`/f/<slug>/django-admin/`). No cubre dibujar ni editar el mapa dentro del sistema.

## Actores

### Actor principal

- **Operador de la plataforma** — superusuario de Django. **No** el dueño de la feria ni sus
  administradores.

> [!note] Por qué solo el superusuario
> Importar un mapa reemplaza el showfloor entero de una convocatoria. Es una operación de
> montaje, no de operación diaria, y hasta que exista un editor con confirmaciones y vista
> previa, el sitio correcto es la herramienta del equipo técnico. `is_superuser` alcanza
> cualquier feria sin fila en `AdminFeria`
> ([ADR-0005](<../../../adr/0005-el-operador-alcanza-cualquier-feria.md>)).

## Disparador

Se recibe el plano del showfloor de una edición, ya convertido a JSON, y hay que dejarlo cargado
antes de abrir la convocatoria.

## Precondiciones

- El actor es superusuario de Django.
- Existe la convocatoria, es de tipo `STD` y **no está archivada**.
- El JSON está en el formato del componente de mapa (retícula, stands y decoraciones).

## Postcondiciones

### En éxito

- La convocatoria tiene su `MapaShowfloor` con la retícula del archivo.
- Existe un `Stand` por cada stand del archivo, con su forma en celdas, su zona y su etiqueta.
- Existe una `DecoracionMapa` por cada decoración.
- **Todos los stands nuevos quedan en `Disponible`** (RN-10), sea cual sea el estado que
  trajera el archivo — ver el paso 5.
- El mapa ya se puede servir a los dos públicos (CU-STD-037, CU-STD-038) sin volver a leer el
  archivo.

### En fallo

- **No se importa nada.** El mapa anterior, si lo había, queda intacto. Una importación a
  medias dejaría un showfloor con la mitad de los espacios.

## Flujo principal

1. El operador entra al admin de la edición y elige la convocatoria de stands.
2. El operador aporta el archivo JSON.
3. El sistema valida la estructura: retícula presente, cada stand con clave y forma, cada forma
   dentro de los límites de la retícula, claves sin repetir.
4. El sistema crea o reemplaza el `MapaShowfloor` de esa convocatoria con la retícula del
   archivo.
5. El sistema crea un `Stand` por entrada, **en estado `Disponible`**, con su clave, etiqueta,
   zona, forma en celdas o lista de rectángulos, y lo que incluye.
6. El sistema crea las decoraciones.
7. El sistema informa qué se cargó: cuántos stands, cuántas decoraciones y qué superficie total.

> [!important] Lo que el archivo trae y el sistema **ignora**
> | Campo del JSON | Por qué se ignora |
> | --- | --- |
> | `status` | El estado de un stand lo produce el sistema: nace `Disponible` y cambia al reservarse o pagarse (RN-10). Importarlo dejaría escrito que un espacio está reservado sin que exista la reserva que lo respalda. |
> | `price` | El precio se deriva de la superficie y del `costo_m2` de la convocatoria (RN-01). Un precio en el archivo sería una segunda fuente para la misma cifra. |
> | `dimensions_text` | La superficie se deriva de la forma y de `metros_por_celda`. |
>
> Los tres se aceptan sin protestar —vienen en el formato del componente— pero no se guardan.
> Al volver a generar el JSON, los tres salen calculados.

## Flujos alternos

### A1. La convocatoria ya tenía mapa

1. En el paso 4 la convocatoria ya tiene un `MapaShowfloor`.
2. El sistema **exige una confirmación explícita**, diciendo cuántos stands se van a reemplazar.
3. Confirmado, el mapa anterior se reemplaza entero. Sin confirmar, no se toca nada.

## Flujos de excepción

### E1. Algún stand del mapa actual está reservado

1. En el paso 4, al reemplazar un mapa existente, hay stands que pertenecen a una `Reserva`.
2. **El sistema rechaza la importación completa** y nombra los stands afectados y sus reservas.
3. No hay confirmación que lo permita: borrar un stand reservado dejaría una reserva apuntando a
   un espacio que ya no existe, y con dinero abonado detrás. Antes hay que resolver esas
   reservas (CU-STD-035).

### E2. El archivo no cumple el formato

1. En el paso 3 falla alguna validación: falta la retícula, una clave repetida, una forma fuera
   de los límites, o un rectángulo sin dimensiones.
2. El sistema **no importa nada** y señala qué entrada del archivo está mal y por qué.

### E3. La convocatoria está archivada

1. La convocatoria pertenece a una edición archivada.
2. El sistema rechaza la importación: una edición cerrada se consulta, no se remonta.

## Datos relevantes

### Entradas

- La convocatoria de stands destino.
- Archivo JSON con `grid`, `stands[]` y `decorations[]`.

### Salidas

- `MapaShowfloor` con su retícula, y los `Stand` y `DecoracionMapa` de la convocatoria.
- Resumen de lo importado: espacios, decoraciones y superficie total.

## Reglas de negocio aplicables

- **RN-01:** el precio se deriva; el archivo no lo fija.
- **RN-10:** un stand importado nace `Disponible`.
- **RN-19:** el mapa es de la convocatoria; importar en una no toca a las demás.
