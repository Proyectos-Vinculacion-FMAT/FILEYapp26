---
estado: acpetado
version: 0.1
tags:
  - caso-de-uso
  - autenticacion
  - core-registros
fecha: 2026-06-22
id: CU-REG-001
dominio: CORE-REG
responsable: Juan Manuel Hernandez Miranda
reglas_de_negocio: []
diagramas_relacionados: []
trazabilidad:
  ddr: []
---
# CU-REG-001 Registrar nueva cuenta de usuario externo

## Objetivo

Permitir que una persona que nunca ha usado el sistema FILEY cree su cuenta con datos mínimos (correo, teléfono, nombre), quedando lista para autenticarse con OTP y acceder al módulo correspondiente.

## Alcance

Core Registros. Aplica a proponentes (EVE), talleristas (TAL) y representantes escolares (TAL). No aplica a usuarios administrativos — sus cuentas las crea el administrador general.

## Actores

### Actor principal

- Usuario externo (persona sin cuenta previa en el sistema)

## Disparador

El usuario ingresa su correo en la pantalla de acceso y el sistema no lo reconoce como cuenta existente.

## Precondiciones

- El correo ingresado no está registrado en la entidad `Persona`.
- El sistema tiene al menos un módulo con convocatoria activa (no se puede registrar si no hay nada abierto).

## Postcondiciones

### En éxito

- Se crea un nuevo registro en `Persona` con estado `activa`.
- El sistema dispara inmediatamente CU-REG-002 para autenticar la sesión recién creada.

### En fallo

- No se crea ningún registro. El correo queda disponible para un nuevo intento.

## Flujo principal

1. El usuario ingresa su correo electrónico en la pantalla de acceso.
2. El sistema verifica que el correo no existe en `Persona`.
3. El sistema presenta el formulario de registro con los campos: nombre completo y teléfono (el correo ya está precargado del paso 1).
4. El usuario completa nombre completo y teléfono y confirma.
5. El sistema valida formato de correo y teléfono.
6. El sistema verifica que el teléfono no esté ya asociado a otra cuenta.
7. El sistema crea el registro en `Persona` (`estado = activa`, `fecha_registro = ahora`).
8. El sistema continúa automáticamente en CU-REG-002 (envío de OTP para autenticar la sesión).

## Flujos alternos

### A1. Correo ya registrado

1. En el paso 2, el sistema detecta que el correo ya existe en `Persona`.
2. El sistema informa al usuario que ya tiene cuenta y redirige al flujo de CU-REG-002 sin mostrar el formulario de registro.

## Flujos de excepción

### E1. Formato de correo o teléfono inválido

1. En el paso 5, el sistema detecta que el formato es incorrecto.
2. El sistema resalta el campo en error con un mensaje descriptivo.
3. El flujo no avanza hasta que el campo sea válido.

### E2. Teléfono ya asociado a otra cuenta con correo distinto

1. En el paso 6, el sistema detecta el conflicto.
2. El sistema advierte al usuario que ese teléfono ya está registrado con otro correo.
3. El sistema ofrece dos opciones: usar otro teléfono, o contactar a soporte para resolver el duplicado.
4. El flujo no crea ningún registro hasta resolver el conflicto.

## Datos relevantes

### Entradas

- Correo electrónico
- Nombre completo
- Teléfono

### Salidas

- Registro `Persona` creado (id, correo, teléfono, nombre_completo, tipo, fecha_registro, estado)
- Disparo de CU-REG-002
