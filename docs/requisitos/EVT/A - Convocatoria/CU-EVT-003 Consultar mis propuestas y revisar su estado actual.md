---
estado: construido
version: 0.2
tags:
  - tipo/caso-de-uso
  - dom/evt
fecha: 2026-06-24
id: CU-EVT-003
dominio: EVT
reglas_de_negocio: []
fecha_actualizacion: 2026-09-02
---
# CU-EVT-003 Consultar mis propuestas y revisar su estado actual

> [!note] Equivalente a CU-TAL-003 en la convocatoria de Elvira
> La misma necesidad de seguimiento existe en ambas convocatorias (Hipólito y Elvira), con
> implementaciones paralelas pero independientes — no hay un único CU compartido entre EVT y
> TAL, dado que cada convocatoria tiene su propio ciclo de estados.

## Objetivo

El aplicante revisa el estado actualizado de todas sus propuestas enviadas en la edición activa, incluyendo los mensajes del administrador cuando los haya, para saber si debe actuar o simplemente esperar.

## Alcance

Módulo EVT — vista de seguimiento del proponente. Muestra únicamente las propuestas asociadas a la cuenta con sesión activa. No cubre la edición de propuestas, que corresponde a CU-EVT-004.

## Actores

### Actor principal

- Aplicante

## Disparador

El aplicante desea conocer el estado actual de sus propuestas enviadas.

## Precondiciones

- El aplicante tiene sesión iniciada.

## Postcondiciones

### En éxito

- El aplicante visualiza el listado completo de sus propuestas con sus estados actuales y, cuando aplica, los mensajes del administrador asociados.

### En fallo

- No aplica; es un flujo de solo lectura.

## Flujo principal

1. El aplicante accede a la sección "Mis propuestas".
2. El sistema lista todas las propuestas del proponente para la edición activa, mostrando por cada una: folio, tipo de actividad, título y estado actual.
3. El aplicante selecciona una propuesta para ver su detalle.
4. El sistema muestra el detalle completo: todos los datos enviados, estado actual y —según el estado— la información adicional correspondiente:
   - Si `cambios_solicitados`: el `mensaje_cambios_solicitados` del administrador y acceso directo a CU-EVT-004.
   - Si `rechazada`: el `motivo_rechazo` registrado por el administrador.
   - Si `aceptada`: confirmación de aceptación; la sala y horario se comunicarán en una notificación posterior.
   - Si `pendiente`: indicación de que la propuesta está en revisión.

## Flujos de excepción

### E1. Sin propuestas registradas en la edición activa

1. En el paso 2, el sistema no encuentra propuestas del proponente en la edición activa.
2. El sistema muestra un mensaje informativo y ofrece acceso directo al formulario de envío de propuesta (CU-EVT-002).

## Datos relevantes

### Entradas

- Ninguna; el sistema deriva el listado de la sesión activa del proponente.

### Salidas

- Vista de listado: folio, tipo de actividad, título y estado de cada propuesta.
- Vista de detalle: todos los datos enviados más el mensaje o motivo del administrador cuando aplique.

## Notas de implementación (2026-09-02)

> [!note] Es la puerta del módulo, no una pantalla más
> `url_aplicar` del registro de módulos (`ADR-0006`) apunta aquí y ya no al formulario de
> `CU-EVT-002`. El catálogo dice «Continuar» a quien ya tiene registro, y eso llevaba a un
> formulario en blanco a quien ya había enviado tres propuestas. Quien no ha enviado ninguna
> cae en `E1`, que ofrece el formulario: es el mismo papel que `stands:inicio` cumple en `STD`.

> [!note] El alcance es la convocatoria, no la edición
> El objetivo dice «la edición activa», y una feria puede abrir más de una convocatoria de
> eventos —cada una con su prefijo de folio (§3.6)—. Las rutas llevan la convocatoria
> (`/f/<slug>/eventos/<id>/mis-propuestas/`) porque es lo que el contrato de `ADR-0006` le pasa
> al módulo, y porque la vista de edición completa ya la da el catálogo, que es de donde se
> entra. En la práctica hoy hay una sola por feria y las dos lecturas coinciden.

> [!note] El detalle es una página, no el modal del prototipo
> `prototipo/EVT/aplicantes/mis-propuestas.html` lo resuelve con un modal de cinco renglones.
> El paso 4 pide «todos los datos enviados», y en una presentación de libro son más de treinta
> campos —cinco autores con semblanza, dos presentadores, los adjuntos—: no caben en un modal
> sin darle scroll propio dentro de una página que ya hace scroll. El prototipo queda
> desactualizado en este punto.

> [!note] La columna «Categoría» del prototipo no está
> La asigna el administrador al dictaminar (`CU-EVT-009`, §3.1) y hoy saldría vacía en todas
> las filas. Tampoco está la tarjeta de «Mis constancias»: es `CU-EVT-005`, que no existe, y
> anunciar una fecha de descarga desde una pantalla que no puede cumplirla es peor que callar.

> [!note] La propuesta recién enviada llega resaltada, y el acuse ya no repite la lista
> Cambio del 2026-09-03. El acuse de `CU-EVT-002` llevaba dentro una tabla con lo ya enviado,
> que era esta misma lista sin poder abrir nada — y **sin** la propuesta que se acababa de
> mandar, que era la única que importaba en ese momento. Ahora el acuse hace lo que dibuja
> `prototipo/EVT/aplicantes/confirmacion.html`: el folio en grande y qué sigue. Su botón
> primario trae aquí con `?nueva=<id>`, y esa fila llega con el destello y la pastilla «nueva»
> del prototipo (`row-nueva`, `pill-nueva`, `filaEntra`, portados con esos mismos nombres).
>
> El id viaja en la barra de direcciones y no en la sesión: así el resalte se pierde al
> recargar, que es lo que tiene que pasar — una propuesta solo es nueva la primera vez que se
> mira. Un valor inventado no resalta nada y no da error: es un adorno, no una consulta.

> [!note] Los adjuntos se ven, no se leen
> El detalle enseña las portadas y los retratos como imágenes, no como nombres de archivo:
> «portada.jpg» no contesta la pregunta que trae quien abre esto, que es si subió la que era —
> dos versiones de la misma imagen se llaman igual, y `IMG_4471.jpg` no distingue nada. Se
> cargan diferidas (`loading="lazy"`), el marco tiene altura propia para que la página no dé un
> salto cuando llegan, y al pulsarlas se abren en grande y centradas.
>
> Al pulsarlas **crecen desde su marco hasta el centro** con la View Transitions API: el mismo
> `view-transition-name` en la miniatura antes del cambio y en la imagen grande después, y el
> navegador interpola posición y tamaño. Animarlo a mano sería el mismo efecto con cien líneas
> y un desfase en cuanto la página tenga scroll.
>
> Los **PDF también se ven ahí dentro**, con el visor del propio navegador y su scroll. Los
> `.docx` y `.odt` de la lista blanca no: ninguno los pinta, y prometer un visor que saldría en
> blanco es peor que mandar a otra pestaña. Quién es qué lo deciden `Documento.es_imagen` y
> `Documento.es_incrustable`, por la extensión de lo guardado y no por el nombre original.
>
> Todo degrada en escalones: sin `startViewTransition` el visor se abre sin crecer; con
> `prefers-reduced-motion` no se anima nada; sin JavaScript el marco es un `<a>` que abre el
> archivo en otra pestaña; y si el navegador no sabe pintar el PDF, el `<object>` enseña su
> contenido de respaldo con el enlace.

> [!warning] El visor obligó a tocar dos cabeceras, y solo en esa vista
> Las dos dejaban el marco en blanco **sin ningún error visible**, que es la peor forma de
> fallar.
>
> - **`X-Frame-Options`**: el proyecto manda `DENY` para todo, y con eso el navegador no pinta
>   ni un archivo propio dentro de un marco. La vista de entrega lleva ahora
>   `@xframe_options_sameorigin`. Sigue prohibido que una página ajena embeba estos archivos,
>   que es de lo que protege el encabezado; solo se relaja para nosotros mismos, y en esa vista
>   y no en los ajustes, para no aflojárselo de paso a las demás pantallas.
> - **`Content-Security-Policy`**: pasa de `sandbox` a `sandbox allow-same-origin`. **No abre
>   la puerta a ejecutar nada**: sigue sin `allow-scripts`, `allow-forms`, `allow-popups` ni
>   `allow-top-navigation`. Hacía falta porque el visor de PDF integrado trata un documento de
>   origen opaco como contenido ajeno y se niega a pintarlo. Lo que protege de verdad contra un
>   archivo disfrazado sigue siendo la lista blanca de `comun/almacenamiento.py` —que deja fuera
>   `.html` y `.svg`— más el `nosniff`.
>
> Hay una prueba que fija las tres cabeceras a la vez, `allow-scripts` incluido por su ausencia.

### Desviación abierta

El paso 4 manda dar «acceso directo a CU-EVT-004» cuando el estado es `cambios_solicitados`.
Esa pantalla no existe todavía, así que en su lugar hay un texto que dice qué hacer y menciona
el folio. No es un botón apagado a propósito: un control gris y sin explicación se lee como una
avería. Cuando exista `CU-EVT-004`, ese párrafo es el botón.
