#!/usr/bin/env bash
# sync-proto.sh — sincroniza prototipo/ entre main-isaac y main sin tocar STD
#
# Uso (desde cualquier rama):
#   ./scripts/sync-proto.sh push   # main-isaac → main  (y dispara deploy gh-pages)
#   ./scripts/sync-proto.sh pull   # main → main-isaac

set -e

MODE=$1
FEATURE_BRANCH="main-isaac"
MAIN_BRANCH="main"

# ---------- helpers ----------
die()  { echo "❌ $*" >&2; exit 1; }
info() { echo "→  $*"; }

# ---------- validaciones ----------
CURRENT=$(git rev-parse --abbrev-ref HEAD)

if [ -n "$(git status --porcelain)" ]; then
  die "Hay cambios sin commitear. Haz commit o stash primero."
fi

# ---------- push: main-isaac → main ----------
if [ "$MODE" = "push" ]; then
  [ "$CURRENT" = "$FEATURE_BRANCH" ] || die "Debes estar en $FEATURE_BRANCH para hacer push."

  info "Cambiando a $MAIN_BRANCH..."
  git checkout "$MAIN_BRANCH"
  git pull origin "$MAIN_BRANCH" --quiet

  info "Copiando prototipo/ desde $FEATURE_BRANCH (excepto STD)..."
  git checkout "$FEATURE_BRANCH" -- prototipo/
  git checkout HEAD -- prototipo/STD/       # restaura STD a la versión de main

  if [ -z "$(git diff --cached --name-only)" ]; then
    info "Sin cambios nuevos en prototipo/. Nada que commitear."
    git checkout "$FEATURE_BRANCH"
    exit 0
  fi

  CHANGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
  info "Commiteando $CHANGED archivos en $MAIN_BRANCH..."
  git commit -m "sync(prototipo): actualiza desde $FEATURE_BRANCH — sin STD

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

  info "Pusheando $MAIN_BRANCH → dispara deploy a gh-pages..."
  git push origin "$MAIN_BRANCH"

  info "Volviendo a $FEATURE_BRANCH..."
  git checkout "$FEATURE_BRANCH"
  echo "✅ Push completo. Deploy en curso en GitHub Actions."

# ---------- pull: main → main-isaac ----------
elif [ "$MODE" = "pull" ]; then
  [ "$CURRENT" = "$FEATURE_BRANCH" ] || die "Debes estar en $FEATURE_BRANCH para hacer pull."

  git fetch origin "$MAIN_BRANCH" --quiet
  info "Copiando prototipo/ desde $MAIN_BRANCH (excepto STD)..."
  git checkout "origin/$MAIN_BRANCH" -- prototipo/
  git checkout HEAD -- prototipo/STD/       # restaura STD a la versión de main-isaac

  if [ -z "$(git diff --cached --name-only)" ]; then
    info "Sin cambios nuevos desde $MAIN_BRANCH. Nada que commitear."
    exit 0
  fi

  CHANGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
  info "Commiteando $CHANGED archivos en $FEATURE_BRANCH..."
  git commit -m "sync(prototipo): trae cambios desde $MAIN_BRANCH — sin STD

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

  info "Pusheando $FEATURE_BRANCH..."
  git push origin "$FEATURE_BRANCH"
  echo "✅ Pull completo. $FEATURE_BRANCH sincronizado con $MAIN_BRANCH."

else
  echo "Uso: $0 [push|pull]"
  echo "  push  — sube prototipo/ de $FEATURE_BRANCH a $MAIN_BRANCH (dispara deploy)"
  echo "  pull  — baja prototipo/ de $MAIN_BRANCH a $FEATURE_BRANCH"
  exit 1
fi
