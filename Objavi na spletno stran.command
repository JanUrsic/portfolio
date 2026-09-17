#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Objavi na spletno stran — enoklikni sinhronizacija PORTFOLIO
#
# Dvojni klik v Finderju sproži skripto ~/Documents/PORTFOLIO/sinhronizacija.py:
#   1) Resize + optimizira fotke iz ~/Desktop/PORTFOLIO
#   2) Skopira v ~/Documents/PORTFOLIO (repo)
#   3) Generira HTML za nove projekte + regenerira kategorije
#   4) Pušne na GitHub
#
# Če vidiš "Operation not permitted" pri prvem zagonu:
#   Sistem → Sistemske nastavitve → Privatnost in varnost → "Open Anyway".
#
# Za praktičnost: pravi alias tega fajla postavi na Desktop
# (right-click v Finderju → Make Alias → povleci alias na Desktop).
# ═══════════════════════════════════════════════════════════════

cd "$HOME/Documents/PORTFOLIO" || {
  echo "❌ Ne najdem ~/Documents/PORTFOLIO"
  echo ""
  read -n 1 -s -r -p "Pritisni katerokoli tipko za zapreti okno..."
  exit 1
}

if [ ! -f "sinhronizacija.py" ]; then
  echo "❌ Ne najdem sinhronizacija.py v ~/Documents/PORTFOLIO/"
  echo ""
  read -n 1 -s -r -p "Pritisni katerokoli tipko za zapreti okno..."
  exit 1
fi

/usr/bin/python3 sinhronizacija.py
EXIT_CODE=$?

echo ""
echo "═══════════════════════════════════════════════════════════════"
if [ $EXIT_CODE -eq 0 ]; then
  echo "  Končano. Pritisni katerokoli tipko za zapreti okno."
else
  echo "  ⚠  Prišlo je do napake. Preberi izpis zgoraj."
  echo "  Pritisni katerokoli tipko za zapreti okno."
fi
echo "═══════════════════════════════════════════════════════════════"
read -n 1 -s -r
