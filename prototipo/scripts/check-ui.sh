#!/usr/bin/env bash
# check-ui.sh — Verifica las reglas de UI que un skill no puede garantizar por sí solo.
#
#   ./prototipo/scripts/check-ui.sh            # verifica
#   ./prototipo/scripts/check-ui.sh --baseline # recalcula el trinquete de deuda tolerada
#
# ERRORES (rompen, exit 1)
#   E1  var(--token) sin definición y sin fallback
#   E2  <svg> con width/height en un asset (el tamaño lo fija CSS)
#   E3  color hex suelto en una regla CSS (fuera de :root)
#
# AVISOS con trinquete (rompen solo si CRECEN respecto a prototipo/scripts/.ui-baseline)
#   W1  style="..." inline en HTML
#   W2  clase usada en HTML/JS sin definición en ningún CSS ni bloque <style>
#   W4  líneas de CSS embebido en <style> dentro de HTML (debe vivir en una capa)
#
# INFORMATIVO
#   W3  clase definida en CSS sin uso en HTML/JS
#
# E3 solo mira archivos .css: el hex dentro de un <style> embebido ya lo cubre W4,
# que exige mover ese bloque a una capa (donde E3 sí lo revisará).

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROTO="$ROOT/prototipo"
BASE="$PROTO/scripts/.ui-baseline"
MODE="${1:-check}"

# Arrays null-delimitados: hay assets con espacios en el nombre.
#
# Se llenan con `while read -r -d ''` y no con `mapfile`, que es de bash 4:
# macOS trae bash 3.2 de fábrica y ahí el script moría en esta línea.
leer_en() {  # leer_en <nombre_de_array> < flujo_null_delimitado
  local destino="$1" f
  eval "$destino=()"
  while IFS= read -r -d '' f; do eval "$destino+=(\"\$f\")"; done
}

leer_en css_files  < <(find "$PROTO" -name '*.css'  -not -path '*/STD/*' -print0)
leer_en html_files < <(find "$PROTO" -name '*.html' -not -path '*/STD/*' -print0)
leer_en js_files   < <(find "$PROTO" -name '*.js'   -not -path '*/STD/*' -print0)
leer_en svg_files  < <(find "$PROTO" -name '*.svg'  -not -path '*/STD/*' -print0)

# En bash 3.2, con `set -u`, expandir un array vacío aborta el script. Un
# prototipo sin CSS o sin HTML no es un caso que este verificador deba
# tratar de sobrevivir: es un error de bulto y se dice así.
[ ${#css_files[@]}  -gt 0 ] || { echo "❌ No hay ningún .css bajo $PROTO"  >&2; exit 1; }
[ ${#html_files[@]} -gt 0 ] || { echo "❌ No hay ningún .html bajo $PROTO" >&2; exit 1; }

web_files=("${css_files[@]}" "${html_files[@]}")
[ ${#js_files[@]}  -gt 0 ] && web_files+=("${js_files[@]}")

errors=0
say()   { printf '%s\n' "$*"; }
# `wc -l` en macOS rellena con espacios. Sin quitarlos, el trinquete se
# escribía como `inline_styles=     221`, que al hacer `source` asigna
# vacío e intenta ejecutar `221` como comando: el techo se perdía y la
# comprobación pasaba siempre.
contar() { tr -d ' '; }
head2() { printf '\n\033[1m%s\033[0m\n' "$*"; }

# ---------------------------------------------------------------- E1
# La lista de tokens definidos va por archivo y no por `-v def="$defined"`:
# el awk de macOS (BSD) aborta ante un `-v` con saltos de línea, y al no
# emitir nada dejaba E1 en verde SIEMPRE, dijera lo que dijera el CSS.
tokens_definidos="$(mktemp)"
trap 'rm -f "$tokens_definidos"' EXIT

grep -ho -- '--[A-Za-z0-9_-]\+[[:space:]]*:' "${css_files[@]}" 2>/dev/null \
  | sed 's/[[:space:]]*:$//' | sort -u > "$tokens_definidos"

e1=$(grep -Hno -- 'var([[:space:]]*--[A-Za-z0-9_-]\+[[:space:]]*)' "${web_files[@]}" 2>/dev/null \
     | sed 's/var([[:space:]]*/var(/; s/[[:space:]]*)$/)/' \
     | awk -F: -v def="$tokens_definidos" '
       BEGIN { while ((getline linea < def) > 0) if (linea != "") ok[linea] = 1 }
       { tok = $NF; sub(/^var\(/, "", tok); sub(/\)$/, "", tok)
         if (!(tok in ok)) print $1 ":" $2 "  " tok }' | sort -u)

head2 "E1 · var(--token) sin definición"
if [ -n "$e1" ]; then
  say "$e1" | sed "s|$ROOT/||"
  say "→ $(printf '%s\n' "$e1" | wc -l | contar) referencia(s) rota(s). Usa el nombre correcto del inventario."
  errors=$((errors + 1))
else
  say "ok"
fi

# ---------------------------------------------------------------- E2
# `/dev/null` extra: sin él, un prototipo sin SVGs dejaría a grep sin
# argumentos de archivo, leyendo de la entrada estándar y colgando.
e2=$(grep -Hln '<svg[^>]*\(width\|height\)=' /dev/null ${svg_files[@]+"${svg_files[@]}"} 2>/dev/null)

head2 "E2 · <svg> con width/height hardcodeado"
if [ -n "$e2" ]; then
  say "$e2" | sed "s|$ROOT/||"
  say "→ $(printf '%s\n' "$e2" | wc -l | contar) asset(s). Deja solo viewBox; el tamaño lo fija CSS."
  errors=$((errors + 1))
else
  say "ok"
fi

# ---------------------------------------------------------------- E3
e3=$(awk '
  { line = $0
    if (incom) { if (sub(/.*\*\//, "", line)) incom = 0; else next }
    gsub(/\/\*[^*]*\*\//, "", line)
    if (sub(/\/\*.*$/, "", line)) incom = 1
    if (line ~ /:root/) inroot = 1
    if (inroot) { if (line ~ /}/) inroot = 0; next }
    if (line ~ /#[0-9a-fA-F]{3,8}([^0-9a-zA-Z]|$)/) print FILENAME ":" FNR "  " line
  }' "${css_files[@]}" 2>/dev/null)

head2 "E3 · hex suelto en regla CSS (debe ser token)"
if [ -n "$e3" ]; then
  say "$e3" | sed "s|$ROOT/||"
  say "→ $(printf '%s\n' "$e3" | wc -l | contar) regla(s)."
  errors=$((errors + 1))
else
  say "ok"
fi

# ---------------------------------------------------------------- W1 / W2 / W4
w1=$(grep -o 'style="' "${html_files[@]}" 2>/dev/null | wc -l | contar)

embedded=$(awk '/<style/{s=1;next} /<\/style>/{s=0} s' "${html_files[@]}" 2>/dev/null)
w4=$(printf '%s\n' "$embedded" | sed '/^$/d' | wc -l | contar)

used=$(grep -ho 'class="[^"]*"' "${html_files[@]}" ${js_files[@]+"${js_files[@]}"} 2>/dev/null \
       | sed 's/class="//; s/"$//' | tr ' ' '\n' | sed '/^$/d' | sort -u)
declared=$( { grep -ho '\.[A-Za-z0-9_-]\+' "${css_files[@]}" 2>/dev/null
              printf '%s\n' "$embedded" | grep -o '\.[A-Za-z0-9_-]\+' 2>/dev/null
            } | sed 's/^\.//' | sort -u)
undef=$(comm -23 <(printf '%s\n' "$used") <(printf '%s\n' "$declared"))
w2=$(printf '%s\n' "$undef" | sed '/^$/d' | wc -l | contar)
w3=$(comm -13 <(printf '%s\n' "$used") <(printf '%s\n' "$declared") | sed '/^$/d' | wc -l | contar)

write_baseline() {
  printf 'inline_styles=%s\nclases_indefinidas=%s\ncss_embebido=%s\n' "$w1" "$w2" "$w4" > "$BASE"
}

if [ "$MODE" = "--baseline" ]; then
  write_baseline
  say ""
  say "✅ Trinquete actualizado (inline_styles=$w1, clases_indefinidas=$w2, css_embebido=$w4)"
  exit 0
fi

if [ -f "$BASE" ]; then
  . "$BASE"
  : "${inline_styles:=$w1}" "${clases_indefinidas:=$w2}" "${css_embebido:=$w4}"
else
  inline_styles=$w1; clases_indefinidas=$w2; css_embebido=$w4
  write_baseline
  say ""; say "ℹ️  Creado prototipo/scripts/.ui-baseline con los valores actuales."
fi

ratchet() { # nombre, actual, techo, pista
  head2 "$1"
  say "$2 (tolerado: $3)"
  if [ "$2" -gt "$3" ]; then
    say "→ Creció en $(($2 - $3)). $4"
    errors=$((errors + 1))
  elif [ "$2" -lt "$3" ]; then
    say "→ Bajó. Corre ./prototipo/scripts/check-ui.sh --baseline para fijar el nuevo techo."
  fi
}

ratchet "W1 · style= inline en HTML (trinquete)" "$w1" "$inline_styles" \
        "Mueve los estilos nuevos a una clase del inventario."

ratchet "W2 · clase usada sin definición CSS (trinquete)" "$w2" "$clases_indefinidas" \
        "Puede ser una clase inventada o un hook JS sin estilo."
if [ "$w2" -gt "$clases_indefinidas" ]; then
  printf '%s\n' "$undef" | sed '/^$/d' | head -20 | sed 's/^/    ./'
fi

ratchet "W4 · líneas de CSS embebido en <style> (trinquete)" "$w4" "$css_embebido" \
        "El CSS nuevo va a una capa, no a un <style> del HTML."

head2 "W3 · clase definida sin uso (informativo)"
say "$w3 candidatas a borrarse — ver columna 'usada en' del inventario"

printf '\n'
if [ "$errors" -gt 0 ]; then
  say "❌ $errors comprobación(es) fallida(s)."
  exit 1
fi
say "✅ UI en verde."
