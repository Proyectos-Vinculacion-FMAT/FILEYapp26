---
estado: propuesta
version: 0.4
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
  - admin
  - navegacion
fecha: 2026-06-30
fecha_actualizacion: 2026-08-26
id: CU-REG-006
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-006 Consultar los módulos de una feria y entrar a un panel

> [!important] Actualización 2026-08-21 — este CU se partió en dos, y perdió su parte de permisos
> La v0.2 respondía "¿a qué panel entro?" con una sola pregunta, resuelta contra `RolPermiso`.
> Con [ADR-0004](<../../adr/0004-acceso-administrativo-por-feria.md>) esa pregunta se parte:
>
> 1. **¿A qué feria?** → [CU-FER-002](<../FER/CU-FER-002 Consultar mis ferias y entrar a una.md>).
>    Ahí sí hay una comprobación de acceso: solo se listan las ferias que la cuenta administra.
> 2. **¿A qué módulo, dentro de esa feria?** → este CU. Aquí **ya no hay permisos que comprobar**:
>    quien entró a una feria puede operar todos sus módulos.
>
> En consecuencia esta pantalla deja de ser un control de acceso y pasa a ser **navegación**. Sus
> flujos A1 y A2 de la v0.2 —saltar la pantalla si solo hay un módulo permitido, y mostrar
> deshabilitados los módulos sin permiso— quedan **sin objeto**: todas las cuentas que llegan
> aquí ven los cuatro módulos y pueden entrar a los cuatro.

<!-- -->

> [!note] Actualización 2026-08-26 — el código llamaba «CU-REG-006» a otra cosa
> `filey/apps/registros/views.py` etiquetaba con este identificador la pantalla `/convocatorias`
> del **participante**, que no es lo que describe este documento. Esa pantalla —y el catálogo
> inventado que la alimentaba— desapareció: la sustituye
> [CU-FER-006](<../FER/CU-FER-006 Consultar el catalogo de convocatorias de mi feria.md>), que
> cuelga de una feria, y a esa feria se llega por
> [CU-FER-010](<../FER/CU-FER-010 Elegir la feria en la que quiero participar.md>).
>
> Lo que **este** documento describe —elegir módulo dentro de una feria— sigue sin construir: no
> hay ningún panel de módulo todavía.

## Objetivo

Dentro de una feria, mostrar al usuario administrativo los módulos de esa feria y dejarle entrar
al panel de uno.

## Alcance

Core Registros — navegación **dentro** de una feria. No cubre la autenticación (CU-REG-003), la
selección de feria (CU-FER-002) ni las funciones internas de cada panel (`EVT`/`TAL`/`STD`/`VIS`).
No aplica a usuarios externos.

## Actores

### Actor principal

- Usuario administrativo con acceso a la feria en la que se encuentra: dueño o administrador.
  Ambos ven exactamente lo mismo en esta pantalla — la única diferencia entre ellos, administrar
  accesos, vive en otra (CU-FER-003).

## Disparador

El usuario acaba de entrar a una feria (CU-FER-002, o el salto directo de su A1), o ya dentro de
un panel decide cambiar de módulo.

## Precondiciones

- El usuario tiene sesión activa y **acceso a esta feria** (`AdminFeria`).

## Postcondiciones

### En éxito

- El sistema abre el panel del módulo elegido, dentro de la feria activa.

### En fallo

- El usuario permanece en la pantalla de selección sin entrar a ningún panel.

## Flujo principal

1. El sistema muestra las tarjetas de los cuatro módulos de la feria: Actividades FILEY (`EVT`),
   Infantil/Juvenil (`TAL`), Stands (`STD`) y Visitas Escolares (`VIS`).
2. El sistema indica en cada tarjeta el estado de su convocatoria dentro de **esta** feria
   (abierta, cerrada, sin configurar). Dos ferias distintas muestran estados distintos: el dato
   sale del schema de la feria activa, no de un catálogo global.
3. El administrador selecciona un módulo.
4. El sistema abre el panel administrativo de ese módulo, dentro de la feria activa.

> [!note] Qué decide el servidor y qué la pantalla
> La pantalla dibuja lo que recibe. Los cuatro módulos y el estado de sus convocatorias los
> resuelve el servidor **dentro del schema de la feria activa**
> ([ADR-0003](<../../adr/0003-una-feria-por-schema.md>)); el navegador no elige feria ni consulta
> nada por su cuenta.

## Flujos alternos

### A1. Un módulo cuyo panel todavía no existe

1. El usuario selecciona un módulo que aún no está construido.
2. El sistema muestra la tarjeta pero no navega, avisando de que ese panel llegará en una entrega
   posterior.
3. Esto es una limitación **de construcción**, no de permisos: la tarjeta no está deshabilitada
   porque la cuenta no pueda, sino porque el panel no existe.

### A2. Volver a la selección de feria

1. El usuario elige cambiar de feria desde el menú.
2. El sistema lo lleva a CU-FER-002 y, al elegir otra feria, esta pantalla se vuelve a dibujar
   con los datos de la nueva.

## Flujos de excepción

### E1. La cuenta perdió el acceso a esta feria

1. A la cuenta se le retiró el acceso (CU-FER-004) o su sesión expiró mientras tenía la pantalla
   abierta.
2. El sistema **rechaza la consulta en el servidor** —no basta con ocultar las tarjetas— y la
   saca de la feria, según CU-FER-002 E2.
3. Esto cubre la revocación en caliente: deja de tener acceso en su siguiente consulta, sin
   esperar a que caduque nada.

## Datos relevantes

### Entradas

- Selección del módulo por parte del administrador.
- Feria activa, tomada del contexto de la sesión (no del navegador).

### Salidas

- Panel administrativo del módulo elegido, dentro de la feria activa.

> [!note] Nota de prototipo (maqueta de la vista del administrador — EVT)
> La maqueta se dibujó antes de que existiera el concepto de feria: presenta a Hipólito como
> "administrador general" viendo las tarjetas de módulo, con solo el panel de Eventos construido
> y las demás marcadas como "Próximamente". Esa pantalla sigue siendo válida como diseño de
> **esta** pantalla; lo que le falta es el paso anterior —la feria— y el rótulo que indique en
> cuál se está.

<!-- -->

> [!warning] Estado de la implementación funcional (2026-08-21)
> Lo construido hoy corresponde a la **v0.2** de este CU: la pantalla lista módulos según
> `RolPermiso` y marca como no navegables los que la cuenta no tiene, sin ninguna noción de
> feria. Al elegir una tarjeta, el sistema avisa de que ese panel llegará después: **ningún panel
> de módulo está conectado todavía**. Alinear la implementación con esta versión es parte de la
> migración a `AdminFeria`.
