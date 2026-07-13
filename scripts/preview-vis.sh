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
# Uso:
#   ./scripts/preview-vis.sh        # puerto 8080
#   ./scripts/preview-vis.sh 5500   # puerto a elección

set -e

PORT="${1:-8080}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../prototipo" && pwd)"

echo "→  Sirviendo $ROOT en http://localhost:$PORT"
echo "→  VIS (escuela): http://localhost:$PORT/VIS/aplicantes/convocatoria-vis.html"
echo "→  VIS (admin):   http://localhost:$PORT/VIS/administradores/admin-propuestas.html"
echo "→  Sin caché (Cache-Control: no-store) — cada recarga trae el archivo tal cual está en disco"
echo "→  Ctrl+C para detener — no queda nada que limpiar en el repo al cerrar"
echo

NO_CACHE_SERVER='
import http.server, sys
class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()
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
