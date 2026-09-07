#!/bin/bash
# Genera index.html per GitHub Pages dal sorgente unico e pusha sul repo Giulioat/storie-abf.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)/impaginatore-storie-abf.html"
SITE="$HOME/Documents/storie-abf-site"
mkdir -p "$SITE"
{
  printf '<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Storie ABF"><meta name="theme-color" content="#fbf8f6"><link rel="icon" href="data:image/svg+xml,<svg xmlns=%%22http://www.w3.org/2000/svg%%22 viewBox=%%220 0 100 100%%22><rect width=%%22100%%22 height=%%22100%%22 rx=%%2222%%22 fill=%%22%%23ffc1c1%%22/><rect x=%%2228%%22 y=%%2216%%22 width=%%2244%%22 height=%%2268%%22 rx=%%228%%22 fill=%%22%%232B2622%%22/></svg>"><style>img{max-width:100%%}[hidden]{display:none!important}</style></head><body style="margin:0">'
  cat "$SRC"
  printf '</body></html>'
} > "$SITE/index.html"
cp "$SITE/index.html" "$SITE/index.html.bak" 2>/dev/null || true
rm -f "$SITE/index.html.bak"
# copia i sorgenti nel repo (src/), così chi clona ha tutto
mkdir -p "$SITE/src"
PROJ="$(cd "$(dirname "$0")" && pwd)"
cp "$PROJ/impaginatore-storie-abf.html" "$PROJ/build-site.sh" "$PROJ/build-top-stories.py" "$PROJ/supabase-schema.sql" "$PROJ/README.md" "$SITE/src/" 2>/dev/null || true
cp "$PROJ/HANDOFF.md" "$SITE/README.md" 2>/dev/null || true
cd "$SITE"
[ -d .git ] || git init -q -b main
git add -A
git -c user.name="Giulio Andrea Tartufoli" -c user.email="tartufoli.giulioandrea@gmail.com" commit -q -m "Aggiorna impaginatore storie" || true
git push -q origin main 2>/dev/null || echo "push: remote non ancora configurato"
echo "Sito aggiornato: $SITE/index.html"
