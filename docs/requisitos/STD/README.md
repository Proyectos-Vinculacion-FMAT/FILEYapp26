---
estado: propuesta
version: "1.0"
tags:
  - tipo/referencia
  - dom/std
  - tema/mapa
  - tema/operacion
fecha: 2026-08-29
responsable: Hugo Janssen
---
# STD — Cómo se monta el showfloor de una edición

Los documentos de este directorio dicen **qué** hace el dominio. Éste dice **cómo se pone en
marcha**, que es lo que hay que hacer una vez por edición y no está en ningún caso de uso
completo: `CU-STD-039` cubre la importación, pero el mapa hay que tenerlo antes, y después hay
que poner el precio.

| Documento | Qué responde |
| --- | --- |
| [`CU-STD Índice.md`](<CU-STD Índice.md>) | Qué casos de uso existen |
| [`Modelo de datos - Stands.md`](<Modelo de datos - Stands.md>) | Qué se guarda |
| [`Reglas de negocio - Stands.md`](<Reglas de negocio - Stands.md>) | Qué reglas rigen |
| **Éste** | **Cómo se monta una edición** |

---

## El proceso, en cuatro pasos

> [!important] Sin los pasos 2 y 3 el módulo se ve entero y no se puede operar
> Las solicitudes entran, nadie puede reservar y todos los precios salen en cero. El panel del
> módulo (`/f/<slug>/stands/<id>/`) lo avisa arriba en cuanto falta alguno de los dos; es el
> primer sitio al que conviene ir después de crear la convocatoria.

### 1. Conseguir el JSON del mapa

El sistema **no dibuja mapas** ([ADR-0008](<../../adr/0008-el-mapa-corre-en-el-navegador.md>)):
recibe uno hecho fuera, en el formato de `event-stand-map`
(`docs/bridge_protocol.md` de ese repositorio) — `grid`, `stands` y `decorations`.

Hay dos formas de tenerlo:

- **Ya existe.** El de FILEY 2026 está en
  [`filey/apps/stands/mapas/filey-2026.json`](<../../../filey/apps/stands/mapas/filey-2026.json>):
  151 espacios, 2 628 m² vendibles, retícula de 167 × 59 m.
- **Hay que derivarlo de un plano en papel.** Es lo que se hizo con el de 2026, midiendo el PDF
  píxel a píxel. El procedimiento entero está en
  [`scripts/derivar-mapa/README.md`](<../../../scripts/derivar-mapa/README.md>), con sus tres
  pasos y las dos decisiones que lo sostienen.

### 2. Importarlo a la convocatoria

Tres puertas al mismo servicio. **La primera es la habitual.**

#### Desde el admin de la edición

```
/f/<slug>/django-admin/stands/mapashowfloor/importar/
```

Se elige la convocatoria, se sube el archivo y listo. **Solo el superusuario**: importar
reemplaza el showfloor entero de una convocatoria, y hasta que exista un editor con vista previa
el sitio correcto es la herramienta del equipo técnico
([ADR-0005](<../../adr/0005-el-operador-alcanza-cualquier-feria.md>)). Alguien con `is_staff`
—que sí abre el resto de ese admin— recibe un 403 aquí.

#### Desde la consola

```bash
cd filey
python manage.py importar_mapa \
    --feria feriota \
    --convocatoria 1 \
    --archivo apps/stands/mapas/filey-2026.json
```

```
Cargado: 151 espacios (2628 m² vendibles) y 10 decoraciones. — Mi convocatoria de stands
```

`--feria` es el **slug** de la edición, no su nombre: el mapa vive en el schema de esa feria
([ADR-0003](<../../adr/0003-una-feria-por-schema.md>)) y el comando tiene que entrar en él.
`--convocatoria` es el id, que se ve en la URL del panel.

#### Desde el servicio

`apps.stands.servicios.mapas.importar(convocatoria=…, datos=…)`, para una prueba o un comando
propio. Es a lo que llaman las otras dos.

### 3. Poner el precio

`costo_m2` **nace en cero** y nadie lo adivina por ti: no hay un precio por metro cuadrado
razonable que suponer, así que se pone antes de abrir la convocatoria.

```
/f/<slug>/django-admin/stands/configuracionsistema/
```

Ahí mismo están el porcentaje de anticipo (50 % por omisión, `RN-02`), el plazo de la reserva
(30 días, `RN-03`) y, si va a haber campaña, el descuento por pronto pago y **su fecha límite**
(`RN-04`) — sin fecha no hay descuento, aunque el porcentaje esté puesto.

> [!note] Es `CU-STD-034`, y su pantalla propia no existe todavía
> La pantalla A10 llega con la fase 7. Mientras tanto se hace desde el admin de la edición, y por
> eso el panel del módulo dice al pie dónde se ajusta.

### 4. Comprobar que quedó

Abre el panel del módulo:

```
/f/<slug>/stands/<id>/
```

Si los avisos de configuración desaparecieron y la barra de ocupación enseña la superficie
libre, está listo. El showfloor se ve en `Showfloor` (barra lateral), y quien tenga una
solicitud aceptada ya puede reservar.

---

## Reimportar un mapa que ya existe

Es una operación distinta y el sistema la trata como tal.

**Pide confirmación explícita.** Reemplazar borra todos los espacios del mapa anterior:

```
CommandError: «Mi convocatoria de stands» ya tiene un mapa con 151 espacios.
Reemplazarlo los borra todos; hay que confirmarlo.
```

Con `--confirmar` en la consola, o marcando la casilla en el admin.

> [!warning] Si algún espacio está reservado, **no hay confirmación que valga**
> El sistema rechaza la importación entera y nombra los espacios afectados. Borrar un stand
> reservado dejaría una reserva apuntando a un espacio que ya no existe, y con dinero abonado
> detrás. Antes hay que resolver esas reservas (`CU-STD-035`).

---

## Lo que el archivo trae y el sistema ignora

Tres campos se aceptan sin protestar —vienen en el formato del componente— y **no se guardan**:

| Campo | Por qué |
| --- | --- |
| `status` | Lo produce el sistema: un espacio nace `disponible` y cambia al reservarse (`RN-10`). Importarlo dejaría escrito que algo está reservado sin que exista la reserva que lo respalda. |
| `price` | Se deriva de la superficie y del `costo_m2` de la convocatoria (`RN-01`). |
| `dimensions_text` | La superficie sale de la forma y de `meters_per_cell`. |

El de 2026 trae además `ocupante_2026` —quién estuvo en cada espacio ese año— que tampoco se
importa: es quién estuvo, no quién está. Va en el archivo porque el plano es el único registro
que lo tiene.

> [!warning] Reimportar un `saveMap` del editor perdería dos campos
> `salon` e `includes` son de FILEY y no del contrato del componente, así que su exportación no
> los devuelve. Hoy no puede pasar —el editor está fuera de alcance por `CU-STD-039`— y el día
> que entre hay que resolverlo antes. Está anotado en `apps/stands/servicios/mapas.py`.

---

## Si algo falla

| Lo que ves | Qué pasa |
| --- | --- |
| `relation "stands_..." does not exist` | Faltan migraciones en el schema de esa feria. `python manage.py migrate_schemas` — con `migrate` a secas solo se toca `public` y las ferias se quedan igual. |
| `No hay ninguna feria con el slug «...»` | El slug, no el nombre. Se ve en la URL: `/f/<slug>/`. |
| `... no es JSON válido` | Se subió el PDF del plano, o el archivo equivocado. |
| `«X» y «Y» se pisan en la celda (c, f)` | Dos espacios ocupan la misma celda. El archivo se rechaza entero y no se escribe nada. |
| `El `id` «...» no sirve como clave` | La clave viaja dentro de una URL: solo letras, números, guion y guion bajo. |
| El mapa carga en blanco | El canvas no arrancó. Mira la consola del navegador: el puente registra los errores que le manda. |
| El mapa carga en producción y no en local (o al revés) | El build de Godot va **fuera del manifiesto** de estáticos (`comun/estaticos.py`). Si alguien lo mete, `index.js` pide un `.wasm` que ya no se llama así. |
