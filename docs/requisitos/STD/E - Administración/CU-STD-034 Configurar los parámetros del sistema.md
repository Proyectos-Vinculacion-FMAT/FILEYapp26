---
estado: propuesta
version: 0.1
tags:
  - tipo/caso-de-uso
  - dom/std
fecha: 2026-06-22
id: CU-STD-034
modulo: E. Administración
actor_principal: Administrador
requisitos_relacionados: []
dependencias: []
---
# CU-STD-034 Configurar los parámetros del sistema

## Descripción

El administrador establece las reglas y valores (costos, porcentajes, plazos y cuentas bancarias) que el sistema aplicará a las reservas de **una convocatoria de stands**.

> [!important] La configuración es **de una convocatoria**, no de la feria
> Hasta el 2026-08-27 este caso de uso decía "de esta feria", y era cierto cuando había una sola
> convocatoria de stands por edición. Ya no: una feria puede abrir una convocatoria general y
> otra para un pabellón concreto, **con `costo_m2` y plazos distintos** (RN-19). El formulario
> edita la configuración de la convocatoria en la que se está operando, y editarla no toca a las
> demás.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene acceso a la feria en la que opera (`AdminFeria`).
- Está operando sobre una convocatoria de stands concreta.

## Disparador

El administrador ingresa a la vista de "Configuración de la convocatoria" (vista A10).

## Flujo principal

1. El administrador ingresa a la sección de configuración.
2. El sistema despliega el formulario con los datos de la `ConfiguracionSistema` **de esta convocatoria**.
3. El administrador puede editar:
   - **Costo por m²**, del que se deriva el precio de **todos** los stands de esta convocatoria
     (RN-01). No hay precio manual por stand: la zona no fija tarifa, y pabellones a precios
     distintos son convocatorias distintas (RN-19).
   - **Porcentaje de anticipo** (por defecto 50%).
   - **Plazo de reserva** en días (por defecto 30).
   - **Descuento por pronto pago** (10%) y su **Fecha límite**.
   - **Instrucciones de pago** y datos bancarios que aparecerán a los usuarios.
4. El administrador aplica los cambios y guarda.
5. El sistema actualiza la `ConfiguracionSistema` de esta convocatoria y registra la acción en la `Bitacora`.

> [!warning] Cambiar el `costo_m2` no recalcula lo ya cobrado (RN-01)
> Las reservas existentes conservan su `monto_total`. Lo que sí cambia es el **desglose por
> stand**, que se recalcula con el valor nuevo y puede dejar de cuadrar con ese total.
6. El sistema notifica que la configuración fue actualizada con éxito.
7. El caso de uso termina.

## Flujos alternativos

> [!note] Opcional
> Sin flujos alternos.

## Excepciones

### E1. Validación de campos obligatorios
1. En el paso 4, el administrador deja en blanco campos críticos (ej. porcentaje de anticipo o costo base).
2. El sistema impide guardar y marca en rojo los campos faltantes, solicitando su corrección.

## Postcondiciones

- **Éxito:** Las nuevas reglas y costos aplicarán a todas las reservas y cálculos creados a partir de este momento.
- **Fallo:** La configuración previa permanece intacta.

## Reglas de negocio relacionadas

- **RN-01:** (Derivada) Al modificar el costo por m² o los porcentajes, **no** se ven afectadas retroactivamente las reservas existentes: cada una guarda su `monto_total`, calculado con los valores vigentes al crearla. El desglose por stand sí se recalcula, así que puede dejar de cuadrar con ese total (ver `Modelo de datos - Stands` §3.7).
