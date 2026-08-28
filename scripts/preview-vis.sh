#!/usr/bin/env bash
# preview-vis.sh — levanta un servidor estático temporal para previsualizar prototipo/
#
# Necesario porque los JSON semilla de VIS se cargan con fetch(), y fetch() a archivos
# locales falla por CORS si el HTML se abre directo por file://. Sirviendo por HTTP
# (aunque sea localhost) se comporta igual que en GitHub Pages.
#
# No deja nada en el repo: no crea node_modules, cachés locales ni archivos temporales.
# Basta con Ctrl+C para apagarlo — el working tree queda intacto, no hace falta limpiar nada.
#
# El servidor manda Cache-Control: no-store en cada respuesta. Sin esto, el navegador
# cachea CSS/SVG/JS por su cuenta (python -m http.server solo manda Last-Modified, sin
# Cache-Control) y puede seguir mostrando una versión vieja aunque el archivo ya haya
# cambiado en disco y hayas reiniciado el servidor — el problema es el caché del
# navegador, no el servidor ni el proceso.
#
# STD no vive en el árbol de prototipo/ de todas las ramas (sigue publicado aparte en
# gh-pages). Los enlaces "STD ↗" que quedan en REG/EVT apuntan a /STD/ igual — en vez de
# dejar que truene con un 404 crudo del navegador, el servidor local responde ahí con una
# página aviso. Solo aplica a la ruta Python; el fallback de npx no la tiene.
#
# Uso:
#   ./scripts/preview-vis.sh        # puerto 8080
#   ./scripts/preview-vis.sh 5500   # puerto a elección

set -e

PORT="${1:-8080}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../prototipo" && pwd)"

echo "→  Sirviendo $ROOT en http://localhost:$PORT"
echo "→  Flujo REG → EVT:"
echo "     Inicio:            http://localhost:$PORT/"
echo "     Acceso aplicante:  http://localhost:$PORT/REG/aplicantes/aplicantes-login.html"
echo "     Registro:          http://localhost:$PORT/REG/aplicantes/registro.html"
echo "     OTP:               http://localhost:$PORT/REG/aplicantes/otp.html"
echo "     Convocatorias:     http://localhost:$PORT/REG/aplicantes/convocatorias.html"
echo "     EVT (aplicante):   http://localhost:$PORT/EVT/aplicantes/index.html"
echo "     EVT (formulario):  http://localhost:$PORT/EVT/aplicantes/formulario.html"
echo "     Acceso admin:      http://localhost:$PORT/REG/administradores/admin-login.html"
echo "     EVT (admin):       http://localhost:$PORT/EVT/administradores/admin-evt-propuestas.html"
echo "→  VIS (escuela): http://localhost:$PORT/VIS/aplicantes/convocatoria-vis.html"
echo "→  VIS (admin):   http://localhost:$PORT/VIS/administradores/admin-propuestas.html"
echo "→  STD no está en esta rama — los enlaces \"STD ↗\" muestran un aviso en vez de 404 crudo"
echo "→  Sin caché (Cache-Control: no-store) — cada recarga trae el archivo tal cual está en disco"
echo "→  Ctrl+C para detener — no queda nada que limpiar en el repo al cerrar"
echo

NO_CACHE_SERVER='
import http.server, sys, os

STD_PLACEHOLDER = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>STD no está en esta rama</title>
<style>body{font-family:system-ui,sans-serif;max-width:38rem;margin:4rem auto;padding:0 1rem;line-height:1.5}</style>
</head><body>
<h1>STD no está en esta rama</h1>
<p>El prototipo de Stands sigue publicado en GitHub Pages (deploy previo, ver
<code>deploy-pages.yml</code> con <code>keep_files: true</code>), pero no está en el árbol de
<code>prototipo/</code> de esta rama.</p>
<p><a href="/">&larr; Volver al inicio</a></p>
</body></html>""".encode("utf-8")

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def do_GET(self):
        local_path = self.translate_path(self.path)
        if self.path.startswith("/STD") and not os.path.exists(local_path):
            body = STD_PLACEHOLDER
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
http.server.test(HandlerClass=NoCacheHandler, port=port)
'

if command -v python3 >/dev/null 2>&1; then
  cd "$ROOT" && exec python3 -c "$NO_CACHE_SERVER" "$PORT"
elif command -v python >/dev/null 2>&1; then
  cd "$ROOT" && exec python -c "$NO_CACHE_SERVER" "$PORT"
elif command -v npx >/dev/null 2>&1; then
  # http-server sí soporta desactivar caché con -c-1 (a diferencia de "serve").
  # npx lo cachea en el perfil de npm del usuario, no en el repo.
  exec npx --yes http-server "$ROOT" -p "$PORT" -c-1
else
  echo "No se encontró python ni npx en PATH. Instala alguno para previsualizar en local." >&2
  exit 1
fi
