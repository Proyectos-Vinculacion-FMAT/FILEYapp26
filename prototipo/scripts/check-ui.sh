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
#   E4  `hidden` sobre un elemento cuya clase fija `display` (no lo esconde)
#   E5  var(--token) sin definición en la copia de Django (filey/estaticos/css)
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

# ---------------------------------------------------------------- E4
# El atributo `hidden` vale `display: none` en la hoja del NAVEGADOR, así
# que cualquier regla de autor con `display` lo pisa y el elemento se
# queda a la vista. No da error, no avisa nada: solo no se esconde.
#
# Pasó tres veces al construir EVT (`.btn`, `.grid-2`, `.evt-persona`), y
# las tres se descubrieron mirando la pantalla. La cura es una regla
# acotada al componente —`.btn[hidden] { display: none }`—, no un
# `!important` global.
#
# Se mira solo el caso estático: un elemento que trae `hidden` escrito en
# el HTML. El que lo recibe desde JavaScript (`el.hidden = true`) no se
# puede ver desde aquí, así que la regla del skill sigue haciendo falta.
clases_con_display="$(mktemp)"
trap 'rm -f "$tokens_definidos" "$clases_con_display"' EXIT

awk '
  # Se quitan los comentarios ANTES de mirar nada. Sin esto, una nota que
  # mencione `.btn[hidden]` cuenta como si la regla existiera y la
  # comprobación se queda callada para siempre — pasó al escribirla.
  { linea = $0
    if (incom) { if (sub(/.*\*\//, "", linea)) incom = 0; else next }
    gsub(/\/\*[^*]*\*\//, "", linea)
    if (sub(/\/\*.*$/, "", linea)) incom = 1 }

  # Clases que fijan `display` en su propio bloque, que puede ocupar
  # varias líneas.
  linea ~ /^\.[A-Za-z0-9_-]+[[:space:]]*\{/ { sel = linea; sub(/[[:space:]]*\{.*/, "", sel); dentro = 1; tiene = 0 }
  dentro && linea ~ /display[[:space:]]*:/ { tiene = 1 }
  dentro && linea ~ /\}/ { if (tiene) print substr(sel, 2); dentro = 0 }

  # Y las que ya traen su escape.
  linea ~ /\[hidden\]/ { resto = linea; while (match(resto, /\.[A-Za-z0-9_-]+\[hidden\]/)) {
      print "OK:" substr(resto, RSTART + 1, RLENGTH - 9)
      resto = substr(resto, RSTART + RLENGTH) } }
' "${css_files[@]}" 2>/dev/null | sort -u > "$clases_con_display"

e4=$(grep -Hno -E '<[a-z][^>]*[[:space:]]hidden([[:space:]][^>]*)?>' "${html_files[@]}" 2>/dev/null \
     | awk -F: -v lista="$clases_con_display" '
       BEGIN { while ((getline l < lista) > 0) {
                 if (l ~ /^OK:/) escapada[substr(l, 4)] = 1; else fija[l] = 1 } }
       { etiqueta = $0
         sub(/^[^:]*:[0-9]*:/, "", etiqueta)
         if (match(etiqueta, /class="[^"]*"/) == 0) next
         clases = substr(etiqueta, RSTART + 7, RLENGTH - 8)
         n = split(clases, partes, /[[:space:]]+/)
         for (i = 1; i <= n; i++)
           if (partes[i] in fija && !(partes[i] in escapada))
             print $1 ":" $2 "  ." partes[i] " fija display y el `hidden` no la esconde" }' \
     | sort -u)

head2 "E4 · hidden que no esconde (la clase fija display)"
if [ -n "$e4" ]; then
  say "$e4" | sed "s|$ROOT/||"
  say "→ $(printf '%s
' "$e4" | wc -l | contar) elemento(s). Añade \`.clase[hidden] { display: none }\`."
  errors=$((errors + 1))
else
  say "ok"
fi

# ---------------------------------------------------------------- E5
# La copia a mano de `filey/estaticos/css/filey.css` (ver `filey-render`
# §6) puede quedarse con un `var()` que solo existe en el prototipo. El
# fallo no se ve al arrancar: se ve como un color que falta en una
# pantalla que nadie abrió todavía.
#
# Se salta sin protestar si no hay monolito en esta rama.
css_django="$ROOT/filey/estaticos/css"
head2 "E5 · var(--token) sin definición en la copia de Django"
if [ -d "$css_django" ]; then
  django_files=()
  while IFS= read -r -d '' f; do django_files+=("$f"); done     < <(find "$css_django" -name '*.css' -print0 2>/dev/null)

  if [ ${#django_files[@]} -eq 0 ]; then
    say "ok (sin hojas)"
  else
    tokens_django="$(mktemp)"
    grep -ho -- '--[A-Za-z0-9_-]\+[[:space:]]*:' "${django_files[@]}" 2>/dev/null       | sed 's/[[:space:]]*:$//' | sort -u > "$tokens_django"

    e5=$(grep -Hno -- 'var([[:space:]]*--[A-Za-z0-9_-]\+[[:space:]]*)' "${django_files[@]}" 2>/dev/null          | sed 's/var([[:space:]]*/var(/; s/[[:space:]]*)$/)/'          | awk -F: -v def="$tokens_django" '
           BEGIN { while ((getline linea < def) > 0) if (linea != "") ok[linea] = 1 }
           { tok = $NF; sub(/^var\(/, "", tok); sub(/\)$/, "", tok)
             if (!(tok in ok)) print $1 ":" $2 "  " tok }' | sort -u)
    rm -f "$tokens_django"

    if [ -n "$e5" ]; then
      say "$e5" | sed "s|$ROOT/||"
      say "→ $(printf '%s
' "$e5" | wc -l | contar) referencia(s) rota(s) del lado de Django."
      errors=$((errors + 1))
    else
      say "ok"
    fi
  fi
else
  say "ok (no hay monolito en esta rama)"
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
