# FILEY 2027

Monolito Django (front y back en el mismo repo, separados por módulo) + `prototipo/`,
el mockup HTML estático que hoy sigue siendo el entregable vivo y la fuente del CSS.

## Qué skill aplica

| Vas a… | Skill |
| --- | --- |
| Elegir color, tipografía, radio, tono, o cuántos pasos/campos lleva una pantalla | `filey-identidad` |
| Escribir o editar CSS/markup, buscar si una clase ya existe | `filey-ui-componentes` |
| Tocar plantillas, vistas, URLs, estáticos, o portar del prototipo a Django | `filey-render` |

Cada hecho vive en **un solo** skill; los demás enlazan. No dupliques contenido entre ellos.

## Comandos

```bash
./scripts/gen-inventario.sh   # reindexa el CSS → inventario del skill de componentes
./scripts/check-ui.sh         # verifica tokens, SVGs, hex y trinquetes de deuda
./scripts/preview-vis.sh      # sirve prototipo/ en localhost:8080
./scripts/sync-proto.sh push  # main-isaac → main (dispara deploy a gh-pages)

.venv/Scripts/python.exe manage.py check
.venv/Scripts/python.exe manage.py runserver
```

Corre `check-ui.sh` antes de cualquier `sync-proto.sh push`: lo que se rompe en
`prototipo/` se publica.
