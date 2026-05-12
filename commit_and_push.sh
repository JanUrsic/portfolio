#!/bin/bash
# Pošlje vse spremembe iz mape PORTFOLIO na GitHub.
# Uporaba: odpri Terminal in poženi:
#   cd ~/Documents/PORTFOLIO && bash commit_and_push.sh
# Lahko podaš tudi svoje commit sporočilo:
#   bash commit_and_push.sh "Popravil sem hero sekcijo"

set -e
cd "$(dirname "$0")"

echo "==> Čistim stare git lock fajle (če obstajajo)..."
rm -f .git/HEAD.lock .git/index.lock .git/tX8LFxg 2>/dev/null || true

echo ""
echo "==> Trenutno stanje:"
git status --short

# Če ni nobenih sprememb, izstopi
if [ -z "$(git status --porcelain)" ]; then
    echo ""
    echo "==> Ni sprememb za pushati. Vse je že na GitHubu."
    exit 0
fi

# Commit sporočilo: prvi argument, ali avtomatsko z datumom
MSG="${1:-Update site files ($(date '+%Y-%m-%d %H:%M'))}"

echo ""
echo "==> Dodajam VSE spremembe in commitam..."
git add -A
git commit -m "$MSG"

echo ""
echo "==> Pusham na origin/main..."
git push origin main

echo ""
echo "==> Končano! Preveri na https://github.com/JanUrsic/portfolio"
