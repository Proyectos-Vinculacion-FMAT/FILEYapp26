#!/usr/bin/env bash
# gen-inventario.sh — Índice de tokens y componentes CSS del prototipo FILEY.
#
#   ./scripts/gen-inventario.sh
#
# Salida: .claude/skills/filey-ui-componentes/references/inventario.md
#
# El inventario es GENERADO. No lo edites a mano: este script lo sobrescribe.
# Regenéralo cada vez que cambies un styles.css y comitea el resultado.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROTO="$ROOT/prototipo"
OUT="$ROOT/.claude/skills/filey-ui-componentes/references/inventario.md"

# ---------- capas CSS ----------
capas=()
[ -f "$PROTO/common/styles-base.css" ] && capas+=("common|$PROTO/common/styles-base.css")
for d in REG EVT VIS TAL PRG SAL; do
  [ -f "$PROTO/$d/styles.css" ] && capas+=("$d|$PROTO/$d/styles.css")
done
[ ${#capas[@]} -eq 0 ] && { echo "❌ No se encontró ningún CSS bajo $PROTO" >&2; exit 1; }

usos="$(mktemp)"; defs="$(mktemp)"; toks="$(mktemp)"
trap 'rm -f "$usos" "$defs" "$toks"' EXIT

# ---------- 1. uso de clases en HTML/JS, por dominio ----------
find "$PROTO" -type f \( -name '*.html' -o -name '*.js' \) -not -path '*/STD/*' -print0 \
| xargs -0 awk -v proto="$PROTO/" '
  {
    fn = FILENAME; sub(proto, "", fn); split(fn, p, "/"); dom = p[1]
    s = $0
    while (match(s, /class="[^"]*"/)) {
      v = substr(s, RSTART + 7, RLENGTH - 8)
      n = split(v, cs, /[ \t]+/)
      for (i = 1; i <= n; i++) if (cs[i] != "") print cs[i] "\t" dom
      s = substr(s, RSTART + RLENGTH)
    }
    s = $0
    while (match(s, /classList\.(add|remove|toggle|contains)\([^)]*\)/)) {
      st = RSTART; len = RLENGTH          # el match interno pisa RSTART/RLENGTH
      v = substr(s, st, len)
      while (match(v, /['"'"'"][A-Za-z0-9_-]+['"'"'"]/)) {
        print substr(v, RSTART + 1, RLENGTH - 2) "\t" dom
        v = substr(v, RSTART + RLENGTH)
      }
      s = substr(s, st + len)
    }
  }' 2>/dev/null | sort -u > "$usos"

# ---------- 2. clases definidas, por capa ----------
for entry in "${capas[@]}"; do
  capa="${entry%%|*}"; file="${entry#*|}"
  awk -v capa="$capa" '
    function emit(sel,   s, cls) {
      if (sel ~ /^[ \t]*@/) return
      s = sel
      while (match(s, /\.[A-Za-z0-9_-]+/)) {
        cls = substr(s, RSTART + 1, RLENGTH - 1)
        if (!(cls in seen)) { seen[cls] = 1; print cls "\t" capa "\t" ln }
        s = substr(s, RSTART + RLENGTH)
      }
    }
    {
      line = $0
      gsub(/\/\*[^*]*\*\//, "", line)
      t = line; gsub(/^[ \t]+/, "", t); gsub(/[ \t]+$/, "", t)
      if (index(line, "{") > 0) {
        ln = (pend == "" ? NR : pendln)
        emit(pend substr(line, 1, index(line, "{") - 1))
        pend = ""
      } else if (t ~ /,$/ && t !~ /[;}]/ && t !~ /^\// && t !~ /\(/) {
        if (pend == "") pendln = NR
        pend = pend t
      } else pend = ""
    }' "$file"
done > "$defs"

# ---------- 3. tokens definidos, por capa ----------
for entry in "${capas[@]}"; do
  capa="${entry%%|*}"; file="${entry#*|}"
  awk -v capa="$capa" '
    /^[ \t]*--[A-Za-z0-9_-]+[ \t]*:/ {
      i = index($0, ":")
      name = substr($0, 1, i - 1); gsub(/[ \t]/, "", name)
      val = substr($0, i + 1); sub(/;[ \t]*$/, "", val)
      gsub(/^[ \t]+/, "", val); gsub(/[ \t]+$/, "", val)
      if (length(val) > 44) val = substr(val, 1, 44) "…"
      gsub(/\|/, "\\|", val)
      print name "\t" capa "\t" val
    }' "$file"
done > "$toks"

n_tok=$(wc -l < "$toks"); n_cls=$(wc -l < "$defs")
n_huerf=$(awk -F'\t' -v u="$usos" 'BEGIN{while((getline l<u)>0){split(l,a,"\t");d[a[1]]=1}} !($1 in d){c++} END{print c+0}' "$defs")

# ---------- 4. componer ----------
mkdir -p "$(dirname "$OUT")"
{
  echo "<!-- GENERADO por scripts/gen-inventario.sh — no editar a mano. -->"
  echo "# Inventario CSS del prototipo"
  echo
  echo "Regenerar con \`./scripts/gen-inventario.sh\` tras cualquier cambio en un \`styles.css\`."
  echo "Fuente: \`prototipo/common/styles-base.css\` + \`prototipo/{DOM}/styles.css\`."
  echo
  echo "**$n_tok tokens · $n_cls definiciones de clase · $n_huerf sin uso detectado en HTML/JS.**"
  echo
  echo "## Cómo usar este archivo"
  echo
  echo "1. Antes de escribir CSS, busca aquí la clase o el token. Si existe, reúsalo."
  echo "2. Columna **capa**: \`common\` = todos los dominios; \`REG\`/\`EVT\`/\`VIS\` = solo ese dominio."
  echo "3. Columna **usada en**: dominios donde aparece en HTML/JS. \`—\` = definida pero sin uso"
  echo "   (candidata a borrarse)."
  echo "4. Una clase listada dos veces (\`common\` + un dominio) es un **override intencional**, no un duplicado."
  echo "   Solo es candidata a **promover** a \`common\` si su única definición está en una capa de dominio"
  echo "   y la columna *usada en* nombra dos o más dominios."
  echo "5. Este índice reemplaza leer los \`.css\` completos. Ábrelos solo cuando necesites las reglas exactas."
  echo
  echo "## Tokens"
  echo
  echo "| token | capa | valor |"
  echo "| --- | --- | --- |"
  awk -F'\t' '{printf "| `%s` | %s | `%s` |\n", $1, $2, $3}' "$toks"
  echo
  echo "## Componentes"
  echo
  echo "| clase | capa | línea | usada en |"
  echo "| --- | --- | --- | --- |"
  awk -F'\t' -v usosf="$usos" '
    BEGIN {
      while ((getline l < usosf) > 0) {
        split(l, a, "\t")
        u[a[1]] = (a[1] in u ? u[a[1]] ", " a[2] : a[2])
      }
    }
    { printf "| `.%s` | %s | %s | %s |\n", $1, $2, $3, ($1 in u ? u[$1] : "—") }
  ' "$defs"
} > "$OUT"

echo "✅ $OUT"
echo "   $n_tok tokens · $n_cls clases · $n_huerf sin uso"
