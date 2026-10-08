#!/usr/bin/env bash
# Launch Atelier Studio desktop on your local machine.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PATH="${HOME}/.local/bin:/usr/local/bin:${PATH}"

if ! command -v atelier >/dev/null 2>&1; then
  python3 -m pip install -e . -q
fi

exec atelier desktop "$@"
