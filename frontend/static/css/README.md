# frontend/static/css/

Está vacío **a propósito**.

Las capas CSS (`common/styles-base.css` y `{DOM}/styles.css`) siguen viviendo en
`prototipo/`, que `config/settings.py` sirve como directorio de estáticos. Así hay
**una sola copia** de cada archivo: el prototipo y la app Django renderizan con el
mismo CSS y no pueden divergir.

No copies CSS aquí. Cuando la última pantalla del prototipo esté portada, se mueven
los archivos con `git mv` y se quita la entrada `prototipo/` de `STATICFILES_DIRS`.
