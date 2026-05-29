#!/bin/zsh
# Publish pack changes so friends get them on next launch.
# Usage: ./publish.sh "what changed"
set -e
cd "$(dirname "$0")"
PACKWIZ="$HOME/go/bin/packwiz"

"$PACKWIZ" refresh
git add -A
git commit -m "${1:-update pack}"
git push origin main
echo ""
echo "Published. Friends receive it next time they launch."
echo "(raw.githubusercontent CDN can lag ~5 min, so don't panic if it's not instant.)"
