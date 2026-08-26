---
estado: implementado
version: "1.0"
tags:
  - tipo/caso-de-uso
  - dom/fer
  - tema/navegacion
  - tema/usuarios
fecha: 2026-08-26
fecha_actualizacion: 2026-08-26
id: CU-FER-010
dominio: FER
responsable: Hugo Janssen
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-FER-010 Elegir la feria en la que quiero participar

> [!important] Es el eslabón que faltaba entre `REG` y el contenido
> `REG` entrega una sesión y ahí acaba. Todo lo que un participante puede hacer —proponer una
> actividad, aplicar a expositor, solicitar una visita— ocurre **dentro de una feria**, y hasta
> el 2026-08-26 no había ningún paso que dijera **cuál**. El participante caía en un catálogo
> hardcodeado que no colgaba de ninguna edición.
>
> Este caso de uso cierra el punto *"Portal público y feria"* de
> [`Modelo de datos - Ferias`](<Modelo de datos - Ferias.md>) §6. Es el gemelo de CU-FER-002:
> lo mismo, para el otro público.

## Objetivo

Tras iniciar sesión como participante, dejar elegir en qué edición de FILEY quiere participar y
llevarlo al catálogo de convocatorias de esa edición.

## Alcance

Core Ferias — navegación posterior al acceso del participante. **No** cubre la autenticación
(CU-REG-001, CU-REG-002) ni el catálogo en sí (CU-FER-006), que es a donde lleva.

Tampoco responde *"¿dónde puedo participar hoy?"* cruzando ediciones: aquí se elige entre las
ferias abiertas, no se busca en todas a la vez. Esa consulta sigue abierta (§6 del modelo de
datos).

## Actores

### Actor principal

- **Participante** — cualquier persona con cuenta y sesión activa.

## Disparador

- El participante termina de autenticarse (CU-REG-002).
- O, ya dentro de una feria, decide cambiar a otra.

## Precondiciones

- El participante tiene sesión activa.

## Postcondiciones

### En éxito

- El participante está en el catálogo de convocatorias de una feria (`/f/<slug>/`, CU-FER-006).
- No queda nada guardado: la feria es el prefijo de la URL, **no un estado de la sesión**
  ([ADR-0003](<../../adr/0003-una-feria-por-schema.md>)). Dos pestañas pueden estar en dos
  ediciones distintas a la vez sin pisarse.

## Flujo principal

1. El participante termina de identificarse.
2. El sistema consulta las ediciones **`activa`**.
3. El sistema muestra una tarjeta por edición, con nombre, sede, edición y fechas.
4. El participante elige una.
5. El sistema abre el catálogo de convocatorias de esa feria (CU-FER-006).

> [!important] Solo las `activa`, y esa exclusión es la mitad del caso de uso
> Una feria `en_preparacion` todavía no tiene revisadas sus convocatorias: enseñarla sería
> invitar a alguien a una edición que no está lista para recibirlo. Es el mismo razonamiento
> por el que una convocatoria en `borrador` no se enseña (CU-FER-006).
>
> Una `archivada` tampoco: ya no admite a nadie. Consultar su catálogo sigue siendo posible por
> URL directa —CU-FER-006 E1—, pero no se ofrece como sitio al que entrar.

<!-- -->

> [!warning] Una feria nace `en_preparacion`, así que nace invisible
> Ni el alta por consola ni la de `/django-admin/` la activan (CU-FER-001). Hasta que alguien la
> pase a `activa`, el participante no la ve — y como con una sola feria activa el paso se salta
> (A1), el síntoma de olvidarlo no es "falta una tarjeta": es que **nadie puede entrar a
> ninguna feria**. Activar la edición es parte de ponerla en marcha.

## Flujos alternos

### A1. Solo hay una feria abierta

1. En el paso 2 el sistema encuentra una sola edición `activa`.
2. El sistema **omite esta pantalla** y lleva directo a su catálogo.
3. Cuando exista una segunda, la barra superior ofrece "Cambiar de feria" y esta pantalla vuelve
   a verse.

> [!important] Con una sola edición viva, el salto es el caso normal
> Preguntar entre una opción no es elegir: es un clic de peaje en el camino de todo el mundo. La
> pantalla solo se justifica el día que dos ediciones se solapan —que ocurre, porque la
> siguiente se monta mientras la actual sigue viva—.
>
> El salto obliga a su contrapartida: **tiene que haber una puerta de vuelta**. Sin ella, quien
> entró cuando solo había una feria no encontraría la segunda el día que se cree. Esa puerta es
> el enlace "Cambiar de feria" de la barra superior, que aparece solo cuando hay a dónde ir.

### A2. Cambiar de feria estando dentro de una

1. El participante, ya en el catálogo de una feria, usa "Cambiar de feria".
2. Vuelve a esta pantalla y elige otra.
3. Nada de la feria anterior sobrevive: no había nada que sobreviviera. La feria es la URL.

### A3. Se llega al catálogo de una feria sin pasar por aquí

1. Alguien abre `/f/2027/` directamente, desde un enlace compartido o un cartel.
2. El sistema sirve el catálogo **sin exigir nada** (CU-FER-006 A1): ni sesión, ni haber elegido.
3. Esta pantalla es una comodidad para quien llega sin saber a dónde va, no un peaje.

## Flujos de excepción

### E1. No hay ninguna feria abierta

1. No existe ninguna edición `activa` — todas están en preparación, archivadas, o no hay
   ninguna.
2. El sistema lo dice: no hay ediciones abiertas al público y aquí aparecerán cuando las haya.
3. **No** se enumeran las ediciones en preparación ni las archivadas. Que exista una edición que
   aún no se anuncia no es información pública.

### E2. Se entra sin sesión

1. Alguien llega a esta pantalla sin haberse identificado.
2. El sistema lo manda al acceso del participante (CU-REG-001 / CU-REG-002).

> [!note] Esta pantalla pide sesión y el catálogo no, y no es una incoherencia
> El catálogo es público porque mirar qué hay convocado es lo que trae a la gente al sistema. Esta
> pantalla, en cambio, **solo se llega desde el login**: es el paso que decide a dónde va quien
> acaba de entrar. Quien no tiene sesión no viene de ahí, y lo que necesita es identificarse.

## Datos relevantes

### Salidas

- Lista de `Feria` con `estado = activa`, excluida la fila de sistema (ver el modelo de datos).

---

## Estado de implementación

Construido el 2026-08-26.

| Pieza | Dónde |
| --- | --- |
| La consulta | `filey/apps/ferias/servicios/seleccion.py::ferias_para_participante` |
| La pantalla y el salto | `filey/apps/ferias/views.py::elegir_feria` (`/ferias/`) |
| La puerta de vuelta | `filey/apps/ferias/templatetags/chasis.py` |
| Las pruebas | `filey/apps/ferias/pruebas/test_seleccion_feria.py` |
