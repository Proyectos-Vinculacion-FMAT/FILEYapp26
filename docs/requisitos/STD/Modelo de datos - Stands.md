---
estado: propuesta
version: 1.0
tags:
  - modelo-de-datos
  - stands
fecha: 2026-06-18
---
# Modelo de datos — Stands (reserva, pago y confirmación)

> Modelo **conceptual**: identifica las entidades y los datos que el sistema debe
> almacenar, sin comprometer aún tipos de base de datos, índices ni claves físicas.
> Las relaciones se describen en la sección 3.

---

## 1. Resumen de entidades

| Entidad | Propósito |
|---------|-----------|
| Cuenta | Acceso/autenticación y rol del usuario. |
| Editorial | Perfil de la entidad expositora (datos de la Ficha de Registro). |
| SelloEditorial | Sellos/fondos editoriales que representa una editorial. |
| Aplicacion | Solicitud para ser expositor y su revisión. |
| Documento | Archivos adjuntos (comprobantes, cartas, listas, etc.). |
| Evento | Edición de la feria (p. ej. FILEY 2026). |
| Stand | Espacio físico en el mapa del showfloor. |
| Reserva | Conjunto de stands reservados por una editorial y su estado de pago. |
| ReservaStand | Detalle (línea) de cada stand dentro de una reserva. |
| Movimiento | Pago/abono registrado contra una reserva. |
| DescuentoAplicado | Descuento aplicado a una reserva (pronto pago, local o especial). |
| Notificacion | Correos enviados al usuario/administrador. |
| ParametrosSistema | Configuración global (costo m², porcentajes, datos bancarios). |
| Bitacora *(opcional)* | Registro de auditoría de acciones del administrador. |

---

## 2. Detalle de entidades y atributos

### 2.1 Cuenta
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| correo | Correo de acceso (único). |
| contrasena_hash | Credencial. |
| rol | `usuario` / `administrador`. |
| estado | `activa` / `inactiva`. |
| es_recurrente | Marca de expositor recurrente *(fuera de alcance actual; previsto)*. |
| fecha_registro | Alta de la cuenta. |

NOTA: Cuenta es ilustrativo, está fuera del scope de este componente.

### 2.2 Editorial
> Datos provenientes de la Ficha de Registro para Expositores.

| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| cuenta_id | FK → Cuenta. |
| nombre | Nombre de la editorial. |
| domicilio_calle, domicilio_numero, domicilio_colonia | Domicilio. |
| cp, municipio, estado, pais | Domicilio (cont.). |
| director_general_nombre, director_general_email | Contacto. |
| director_comercial_nombre, director_comercial_email | Contacto. |
| director_editorial_nombre, director_editorial_email | Contacto. |
| director_promocion_nombre, director_promocion_email | Contacto. |
| responsable_stand | Responsable del stand. |
| giro | `Editor` / `Librero` / `Distribuidor`. |
| telefono_oficina, telefono_celular | Teléfonos. |
| correo_electronico | Correo de contacto. |
| nombre_antepecho | Nombre que aparecerá en el antepecho del stand. |
| num_personas_atienden | Personas que atenderán el módulo. |
| total_sellos | Total de sellos editoriales participantes. |
| cantidad_libros_aprox | Cantidad aproximada de libros. |
| cantidad_titulos_aprox | Cantidad aproximada de títulos. |
| materiales | Multivalor: Libro, Audiolibro, Revista, Material didáctico, Libros electrónicos, Otro. |
| tematicas | Multivalor: lista de temáticas (Administración, Arte, Infantil, …). |
| es_local | Booleano — elegibilidad al descuento del 15% (lo fija el admin al aceptar). |
| constancia_fiscal_id | FK → Documento — Constancia de Situación Fiscal. Permite validar la ubicación (sustenta `es_local`) y emitir facturas por fuera del sistema. |

### 2.3 SelloEditorial
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| editorial_id | FK → Editorial. |
| nombre | Nombre del sello/fondo editorial representado. |

### 2.4 Aplicacion
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| editorial_id | FK → Editorial. |
| evento_id | FK → Evento. |
| estado | `pendiente` / `aceptada` / `rechazada`. |
| fecha_envio | Fecha de envío. |
| fecha_revision | Fecha de revisión. |
| revisado_por | FK → Cuenta (administrador). |
| motivo_rechazo | Texto (si fue rechazada). |
| aplica_descuento_local | Booleano fijado al aceptar (alimenta `Editorial.es_local`). |

> *Nota de diseño:* la información del formulario se solapa con **Editorial**. Decidir con
> el equipo si la aplicación guarda una copia (snapshot) de los datos enviados o si
> referencia directamente a la editorial. Los **documentos** de la aplicación se modelan en `Documento`.

### 2.5 Documento
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| tipo | `comprobante_pago`, `carta_representacion`, `lista_titulos`, `constancia_fiscal`, `doc_abono`, `otro`. |
| archivo_url | Ubicación/almacenamiento del archivo. |
| fecha_carga | Fecha de carga. |
| entidad_tipo | Entidad relacionada (`editorial`, `aplicacion`, `movimiento`). |
| entidad_id | Id de la entidad relacionada. |

### 2.6 Evento
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| nombre | P. ej. "FILEY 2026". |
| edicion | Número de edición (XIV). |
| fecha_inicio, fecha_fin | Fechas del evento. |
| sede, salon | P. ej. Centro de Convenciones Yucatán Siglo XXI, Salón Chichén Itzá. |

### 2.7 Stand
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| evento_id | FK → Evento. |
| clave | Identificador visible en el mapa. |
| pos_x, pos_y | Ubicación/coordenadas en el mapa. |
| ancho, largo | Dimensiones. |
| metros_cuadrados | Superficie (base del cálculo de precio). |
| estado | `Disponible` / `Reservado` / `Ocupado`. |
| incluye | Descripción de lo que incluye (estructura, contactos, exhibidores, etc.). |

### 2.8 Reserva
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| editorial_id | FK → Editorial. |
| evento_id | FK → Evento. |
| estado | `Por confirmar` / `Confirmada` / `Pagada` / `Liberada` / `Cancelada`. |
| fecha_creacion | Inicio del plazo de 30 días. |
| fecha_vencimiento_anticipo | `fecha_creacion` + 30 días. |
| fecha_corte_pago_total | Fecha de bloqueo/límite de pago del 100% (modificable por admin). |
| monto_total | Suma de líneas, con descuento aplicado. |
| monto_abonado | Derivado de movimientos validados. |
| monto_pendiente | Derivado (`monto_total − monto_abonado`). |

### 2.9 ReservaStand
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| reserva_id | FK → Reserva. |
| stand_id | FK → Stand. |
| metros_cuadrados_snapshot | m² al momento de reservar. |
| precio_snapshot | Precio del stand al momento de reservar. |

### 2.10 Movimiento
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| reserva_id | FK → Reserva. |
| monto | Monto del abono. |
| metodo | `transferencia` / `deposito` / `cheque`. |
| origen | `usuario` / `admin_manual`. |
| estado | `pendiente_validacion` / `validado` / `rechazado`. |
| comprobante_id | FK → Documento (obligatorio en abono manual del admin). |
| registrado_por | FK → Cuenta. |
| fecha_registro | Fecha de registro. |
| validado_por | FK → Cuenta (administrador). |
| fecha_validacion | Fecha de validación. |

### 2.11 DescuentoAplicado
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| reserva_id | FK → Reserva. |
| tipo | `pronto_pago` (10%) / `local` (15%) / `especial`. |
| porcentaje | Porcentaje aplicado. |
| motivo | Obligatorio para `especial`. |
| aplicado_por | FK → Cuenta (sistema o administrador). |
| fecha | Fecha de aplicación. |

### 2.12 Notificacion
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| destinatario_id | FK → Cuenta. |
| tipo | `aplicacion_aceptada`, `aplicacion_rechazada`, `reserva_confirmada`, `reserva_pagada`, `posible_cancelacion`, `reserva_liberada`. |
| fecha_envio | Fecha de envío. |
| estado | `enviada` / `fallida`. |
| referencia_tipo, referencia_id | Entidad relacionada (aplicación / reserva). |

### 2.13 ParametrosSistema
| Atributo | Descripción |
|----------|-------------|
| costo_m2 | Costo por metro cuadrado (p. ej. $2,500). |
| porcentaje_anticipo | Porcentaje para confirmar (50%). |
| plazo_reserva_dias | Días de vigencia de la reserva (30). |
| descuento_pronto_pago | Porcentaje (10%). |
| fecha_limite_pronto_pago | Fecha límite del pronto pago. |
| descuento_local | Porcentaje (15%). |
| instrucciones_pago | Texto/datos bancarios (banco, cuenta, CLABE, sucursal, referencia). |

### 2.14 Bitacora
| Atributo | Descripción |
|----------|-------------|
| id | Identificador único. |
| cuenta_id | FK → Cuenta (quién ejecutó la acción). |
| accion | Acción (validar abono, prorrogar, descuento especial, editar mapa, etc.). |
| entidad_tipo, entidad_id | Objeto afectado. |
| detalle | Datos del cambio. |
| fecha | Marca de tiempo. |

---

## 3. Relaciones principales

- **Cuenta** 1—1 **Editorial** (una editorial por cuenta de usuario).
- **Editorial** 1—N **SelloEditorial**.
- **Editorial** 1—N **Aplicacion** (una por evento; permite reenvío tras rechazo).
- **Editorial** 1—1 **Documento** (Constancia de Situación Fiscal).
- **Aplicacion** 1—N **Documento**; **Movimiento** 1—1 **Documento** (comprobante).
- **Evento** 1—N **Stand**.
- **Editorial** 1—N **Reserva**; **Reserva** 1—N **ReservaStand** N—1 **Stand**
  (un stand pertenece a lo sumo a una reserva activa).
- **Reserva** 1—N **Movimiento**.
- **Reserva** 1—N **DescuentoAplicado** (sujeto a las reglas RN-06 y RN-07).
- **Cuenta** 1—N **Notificacion**.

---

## 4. Mapa entidad → caso de uso (trazabilidad)

| Entidad | Casos de uso relacionados |
|---------|---------------------------|
| Cuenta / Editorial / SelloEditorial | CU-STD-001, CU-STD-002, CU-STD-032, CU-STD-033 |
| Aplicacion / Documento | CU-STD-001–CU-STD-007, CU-STD-033 |
| Stand / Evento | CU-STD-008, CU-STD-009, CU-STD-034, CU-STD-035 |
| Reserva / ReservaStand | CU-STD-010–CU-STD-013, CU-STD-020, CU-STD-021, CU-STD-023, CU-STD-026–CU-STD-031 |
| Movimiento | CU-STD-014–CU-STD-018, CU-STD-031 |
| DescuentoAplicado | CU-STD-005, CU-STD-019, CU-STD-022 |
| Notificacion | CU-STD-007, CU-STD-013, CU-STD-024, CU-STD-025, CU-STD-028, CU-STD-029 |
| ParametrosSistema | CU-STD-009, CU-STD-022 (cálculos y descuentos) |

---

## 5. Temas abiertos del modelo

- Confirmar si **Aplicacion** guarda snapshot de datos o referencia a **Editorial**.
- Confirmar si **es_local** vive en Editorial (perfil) o por aplicación/evento.
- Definir estados de cierre adicionales si se requiere distinguir "Liberada" (auto) de
  "Cancelada" (admin) — actualmente ambos contemplados.
- Necesidad real de **Bitacora** (auditoría) — sugerida por las acciones sensibles del
  administrador (validar abono, descuento especial, prórroga).

---

## Reglas de negocio relacionadas

Las reglas RN-01 a RN-17 que rigen estos datos (cálculo por m², anticipo del 50% con
descuento, plazo de 30 días, descuentos no acumulables, estados de stand y reserva, etc.)
están documentadas en los requisitos del dominio y en el inventario de casos de uso
(`CU-STD Índice.md`).
