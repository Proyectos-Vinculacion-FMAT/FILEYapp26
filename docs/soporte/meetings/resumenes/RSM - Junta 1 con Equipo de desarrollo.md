---
tags:
  - tipo/junta-resumen
  - tema/equipo-desarrollo
  - dom/std
  - dom/evt
  - dom/reg
  - tema/usuarios
  - tema/arquitectura
estado: propuesta
fecha: 2026-06-08
---
# Junta 1 con Equipo de desarrollo

## Contexto

Minuta preliminar sobre las necesidades detectadas para un posible sistema de registro y acceso.

> [!important]
> Esta nota no debe tratarse como especificación final. Faltan validar procesos manuales del cliente antes de definir automatizaciones, flujos completos o reglas de negocio.

## Necesidades confirmadas

- Se requiere acceso para arrendatarios de stand.
- Se requiere acceso para personas relacionadas con eventos.
- Se busca lograr un acceso único para ambos casos, si el proceso del cliente lo permite.
- Cada tipo de arrendatario puede requerir información distinta durante su registro.
- El sistema debe poder adaptarse dinámicamente a distintos tipos de registro.
- El alcance mínimo esperado es permitir el registro para que los arrendatarios puedan entrar al sistema.
- Se contemplan registros para visitantes, expositores y eventos.

## Tipos de usuario o participante por validar

En las notas se menciona que un participante puede ser:

- Expositor.
- Hacedor de eventos.

> [!question]
> Falta confirmar si estos perfiles son roles del sistema, tipos de registro, categorías comerciales o simplemente etiquetas operativas usadas por el cliente.

## Estructura preliminar de eventos

La estructura anotada fue:

```text
Exhibición
Evento
  - Tipo 1
  - Tipo 2
  - Tipo n
```

Esta estructura debe tomarse como una clasificación preliminar, no como una jerarquía definitiva.

> [!question]
> Falta validar cómo diferencia el cliente entre exhibición, evento y tipos de evento.

## Registro dinámico

El sistema debe permitir que distintos tipos de arrendatario o participante soliciten información distinta.

Aspectos pendientes de levantar:

- Qué tipos de arrendatario existen.
- Qué tipos de participante existen.
- Qué datos pide actualmente el cliente para cada caso.
- Qué datos son obligatorios y cuáles son opcionales.
- Qué datos cambian según stand, evento, exhibición u otra categoría.
- Quién puede editar o aprobar la información registrada.

## Horarios de eventos

Durante el registro de eventos se podrían seleccionar horarios tentativos.

El proceso actualmente entendido es:

1. Se registra un evento.
2. Se proponen horarios tentativos.
3. La administración revisa manualmente si existen solapamientos.
4. La administración reacomoda horarios cuando sea necesario.
5. Los horarios quedan confirmados y ordenados cuando termina la revisión manual.

> [!warning]
> No se debe asumir todavía un flujo automatizado de aprobación de horarios. Por ahora, el reacomodo queda como proceso manual del cliente.

### Estados de horario por validar

Estados que sí se pueden inferir de las notas:

- Tentativo.
- Confirmado.

Estados que no están definidos y tendrían que validarse antes de documentarlos como requisito:

- En revisión.
- Reacomodado.
- Cancelado.

## Funcionalidad opcional: contador demográfico

En casos excepcionales, si el tiempo de desarrollo lo permite, se podría implementar un contador demográfico de personas que logran entrar.

> [!info]
> Esta funcionalidad debe considerarse secundaria. No están definidos los datos exactos a capturar ni el nivel de detalle esperado.

Preguntas pendientes:

- Qué significa "demográfico" para el cliente.
- Si solo necesita conteo total de entradas.
- Si requiere categorías de visitantes.
- Si el conteo se hace por evento, exhibición, día, acceso o ubicación.
- Si el conteo debe ser manual, semiautomático o automatizado.

## Alcance mínimo

El alcance mínimo mencionado es:

- Registro para que los arrendatarios puedan entrar al sistema.

> [!question]
> Falta definir qué significa "entrar al sistema": crear cuenta, completar formulario, ser aprobado, pagar, recibir acceso físico/digital o aparecer en una lista operativa.

## Fechas tentativas

- Ventana mencionada: de agosto a noviembre.

> [!question]
> Falta confirmar si esta ventana representa fecha máxima de entrega, periodo de desarrollo, periodo de operación del evento o expectativa comercial.

## Pagos

Pendiente técnico/comercial:

- Revisar método de pago con OpenPay.

> [!warning]
> OpenPay no debe tomarse todavía como decisión técnica final. Primero hay que validar si el cliente ya lo usa, si es requisito, o si solo fue una opción mencionada.

## Consideraciones técnicas internas

Ideas a discutir para el stack:

- Debe ser web friendly.
- Debe ser flexible.
- Debe ser escalable.
- Debe ser mantenible.
- Conviene evaluar una solución con ORM o Supabase para soportar formularios y registros dinámicos.

> [!note]
> Esta sección corresponde a discusión técnica interna, no necesariamente a requisitos expresados por el cliente.

## Procesos manuales del cliente por verificar

Antes de automatizar, falta levantar cómo trabaja actualmente el cliente.

Procesos a documentar:

- Registro actual de arrendatarios de stand.
- Registro actual de visitantes.
- Registro actual de expositores.
- Registro actual de eventos.
- Revisión y aprobación de registros.
- Captura o validación de pagos.
- Asignación y reacomodo de horarios.
- Confirmación final de horarios.
- Control de acceso al evento o exhibición.
- Conteo de personas que ingresan.

## Supuestos que no deben tratarse como definidos

- Que exista un rol formal de organizador de eventos.
- Que todos los participantes sean arrendatarios.
- Que los horarios tengan estados como "en revisión", "reacomodado" o "cancelado".
- Que el contador demográfico registre hora, tipo de acceso, categoría o evento específico.
- Que OpenPay sea la pasarela definitiva.
- Que la estructura exhibición/evento/tipo sea una jerarquía final.
- Que exista un flujo automatizado de aprobación.

## Pendientes principales

- Confirmar tipos de usuarios, arrendatarios y participantes.
- Confirmar campos requeridos para cada tipo de registro.
- Confirmar qué procesos manuales se mantendrán y cuáles se automatizarán.
- Confirmar cómo se manejan pagos.
- Confirmar cómo se manejan horarios tentativos y confirmados.
- Confirmar si el contador demográfico entra en alcance.
- Confirmar fecha máxima de entrega y prioridades por etapa.
- Definir stack técnico después de validar procesos y alcance real.

## Documentos relacionados

- [Preguntas para la siguiente sesion](<../meeting notes/Preguntas para la siguiente sesion.md>)
