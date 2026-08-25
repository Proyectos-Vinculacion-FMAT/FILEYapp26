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

El administrador establece las reglas y valores (costos, porcentajes, plazos y cuentas bancarias) que el sistema utilizará como plantilla base para todas las nuevas reservas de **esta feria**. Cada edición tiene sus propios parámetros: el costo por m² y la fecha límite de pronto pago cambian cada año.

## Actores

- **Actor principal:** Administrador (coordinador del showfloor)

## Precondiciones

- El administrador tiene acceso a la feria en la que opera (`AdminFeria`).

## Disparador

El administrador ingresa a la vista de "Configuración del Evento" (vista A10).

## Flujo principal

1. El administrador ingresa a la sección de configuración.
2. El sistema despliega el formulario con los datos cargados desde la entidad `ConfiguracionSistema`.
3. El administrador puede editar:
   - **Costo base por m²** (aplica a todos los stands que no tengan un precio manual).
   - **Porcentaje de anticipo** (por defecto 50%).
   - **Plazo de reserva** en días (por defecto 30).
   - **Descuento por pronto pago** (10%) y su **Fecha límite**.
   - **Instrucciones de pago** y datos bancarios que aparecerán a los usuarios.
4. El administrador aplica los cambios y guarda.
5. El sistema actualiza el registro en `ConfiguracionSistema` y registra la acción en la `Bitacora`.
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
