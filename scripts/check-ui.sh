#!/usr/bin/env bash
# check-ui.sh — Verifica las reglas de UI que un skill no puede garantizar por sí solo.
#
#   ./scripts/check-ui.sh            # verifica
#   ./scripts/check-ui.sh --baseline # recalcula el trinquete de deuda tolerada
#
# ERRORES (rompen, exit 1)
#   E1  var(--token) sin definición y sin fallback
#   E2  <svg> con width/height en un asset (el tamaño lo fija CSS)
#   E3  color hex suelto en una regla CSS (fuera de :root)
#
# AVISOS con trinquete (rompen solo si CRECEN respecto a scripts/.ui-baseline)
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

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROTO="$ROOT/prototipo"
BASE="$ROOT/scripts/.ui-baseline"
MODE="${1:-check}"

# Arrays null-delimitados: hay assets con espacios en el nombre.
mapfile -d '' css_files  < <(find "$PROTO" -name '*.css'  -not -path '*/STD/*' -print0)
mapfile -d '' html_files < <(find "$PROTO" -name '*.html' -not -path '*/STD/*' -print0)
mapfile -d '' js_files   < <(find "$PROTO" -name '*.js'   -not -path '*/STD/*' -print0)
mapfile -d '' svg_files  < <(find "$PROTO" -name '*.svg'  -not -path '*/STD/*' -print0)
web_files=("${css_files[@]}" "${html_files[@]}" "${js_files[@]}")

errors=0
say()   { printf '%s\n' "$*"; }
head2() { printf '\n\033[1m%s\033[0m\n' "$*"; }

# ---------------------------------------------------------------- E1
defined=$(grep -ho -- '--[A-Za-z0-9_-]\+[[:space:]]*:' "${css_files[@]}" 2>/dev/null \
          | sed 's/[[:space:]]*:$//' | sort -u)

e1=$(grep -Hno -- 'var([[:space:]]*--[A-Za-z0-9_-]\+[[:space:]]*)' "${web_files[@]}" 2>/dev/null \
     | sed 's/var([[:space:]]*/var(/; s/[[:space:]]*)$/)/' \
     | awk -v def="$defined" -F: '
       BEGIN { n = split(def, d, "\n"); for (i = 1; i <= n; i++) if (d[i] != "") ok[d[i]] = 1 }
       { tok = $NF; sub(/^var\(/, "", tok); sub(/\)$/, "", tok)
         if (!(tok in ok)) print $1 ":" $2 "  " tok }' | sort -u)

head2 "E1 · var(--token) sin definición"
if [ -n "$e1" ]; then
  say "$e1" | sed "s|$ROOT/||"
  say "→ $(printf '%s\n' "$e1" | wc -l) referencia(s) rota(s). Usa el nombre correcto del inventario."
  errors=$((errors + 1))
else
  say "ok"
fi

# ---------------------------------------------------------------- E2
e2=$(grep -Hln '<svg[^>]*\(width\|height\)=' "${svg_files[@]}" 2>/dev/null)

head2 "E2 · <svg> con width/height hardcodeado"
if [ -n "$e2" ]; then
  say "$e2" | sed "s|$ROOT/||"
  say "→ $(printf '%s\n' "$e2" | wc -l) asset(s). Deja solo viewBox; el tamaño lo fija CSS."
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
  say "→ $(printf '%s\n' "$e3" | wc -l) regla(s)."
  errors=$((errors + 1))
else
  say "ok"
fi

# ---------------------------------------------------------------- W1 / W2 / W4
w1=$(grep -o 'style="' "${html_files[@]}" 2>/dev/null | wc -l)

embedded=$(awk '/<style/{s=1;next} /<\/style>/{s=0} s' "${html_files[@]}" 2>/dev/null)
w4=$(printf '%s\n' "$embedded" | sed '/^$/d' | wc -l)

used=$(grep -ho 'class="[^"]*"' "${html_files[@]}" "${js_files[@]}" 2>/dev/null \
       | sed 's/class="//; s/"$//' | tr ' ' '\n' | sed '/^$/d' | sort -u)
declared=$( { grep -ho '\.[A-Za-z0-9_-]\+' "${css_files[@]}" 2>/dev/null
              printf '%s\n' "$embedded" | grep -o '\.[A-Za-z0-9_-]\+' 2>/dev/null
            } | sed 's/^\.//' | sort -u)
undef=$(comm -23 <(printf '%s\n' "$used") <(printf '%s\n' "$declared"))
w2=$(printf '%s\n' "$undef" | sed '/^$/d' | wc -l)
w3=$(comm -13 <(printf '%s\n' "$used") <(printf '%s\n' "$declared") | sed '/^$/d' | wc -l)

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
  say ""; say "ℹ️  Creado scripts/.ui-baseline con los valores actuales."
fi

ratchet() { # nombre, actual, techo, pista
  head2 "$1"
  say "$2 (tolerado: $3)"
  if [ "$2" -gt "$3" ]; then
    say "→ Creció en $(($2 - $3)). $4"
    errors=$((errors + 1))
  elif [ "$2" -lt "$3" ]; then
    say "→ Bajó. Corre ./scripts/check-ui.sh --baseline para fijar el nuevo techo."
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
