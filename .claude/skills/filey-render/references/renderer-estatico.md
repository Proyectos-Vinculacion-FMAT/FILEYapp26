# Renderizador estático — `prototipo/`

Aplica a todo archivo bajo `prototipo/` excepto `prototipo/STD/`, que es una app Angular
aparte y queda fuera de este renderizador. Por ADR-0001, STD no se construye como Angular
separado: cuando le toque, se reconstruye como un módulo más del monolito, igual que el
resto. El Angular de `prototipo/STD/` es maqueta, no la implementación futura.

## Qué es

HTML plano sin build ni servidor de aplicación. Se abre por `file://` o se sirve estático,
y se despliega tal cual a GitHub Pages. El "backend" es `common/db.js`, un pseudo-backend en
localStorage que siembra datos desde JSON en `common/db/`.

## Restricciones que rigen el markup

1. **Nada de sintaxis de plantilla.** `{% static %}`, `{{ variable }}` y `{% url %}` salen
   impresos literalmente. Las rutas son relativas: `../styles.css`, `../../common/assets/x.svg`.
2. **Sin dependencias de red.** Ni CDN, ni Google Fonts, ni librerías externas. La tipografía
   sale de las fuentes del sistema vía `--font-filey`.
3. **`fetch()` a archivos locales falla por CORS en `file://`.** Por eso los JSON semilla de
   VIS obligan a servir por HTTP. Un SVG referenciado desde CSS con `url()` externo falla
   igual: por eso el caret va embebido como data-URI en un token.
4. **Cada HTML es autónomo.** No hay herencia de plantillas: topbar, footer y `<head>` se
   repiten en los 40 archivos. Es deuda aceptada del prototipo, y es exactamente lo que
   `base.html` resuelve al portar a Django. No intentes inventar un sistema de includes con
   JavaScript.

## Previsualizar

```bash
./scripts/preview-vis.sh        # puerto 8080
./scripts/preview-vis.sh 5500
```

Sirve `prototipo/` por HTTP con `Cache-Control: no-store`, que es necesario: sin eso el
navegador puede seguir mostrando CSS viejo aunque el archivo ya cambió en disco.

## Elementos propios del prototipo

- **`.proto-bar`** — barra superior que enumera los pasos del flujo y permite saltar entre
  pantallas. Es andamiaje de demo, no parte del producto: **no se porta a Django.** Al crear
  una pantalla nueva del prototipo, actualízala con el paso correspondiente.
- **`common/db.js`** — pseudo-backend. Expone `FileyDB.ready()`, el registro de íconos
  (`FileyDB.icon(nombre)`, que inyecta SVG inline para que CSS controle color y tamaño) y las
  semillas. Al portar a Django, cada lectura de `db.js` se convierte en una variable de
  contexto.
- **`common/demo-reset.js`** — reinicia el estado de la demo.

## Despliegue

`.github/workflows/deploy-pages.yml` publica `prototipo/` a la rama `gh-pages` en cada push a
`main` que toque `prototipo/**`. La sincronización entre ramas se hace con
`./scripts/sync-proto.sh push|pull`, que copia `prototipo/` entre `main-isaac` y `main`
excluyendo `STD/`.

Consecuencia práctica: **lo que se rompa en `prototipo/` se publica.** Corre
`./scripts/check-ui.sh` antes de un `sync-proto.sh push`.
