#!/usr/bin/env bash
# Install Atelier Studio for LOCAL use on your Mac or Linux machine.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Atelier Studio · local setup"
echo "    $ROOT"

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python 3.11+ required. Install python3 and retry."
  exit 1
fi

"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -e .

# Tk on Debian/Ubuntu if missing
if "$PYTHON" -c "import tkinter" 2>/dev/null; then
  echo "==> tkinter OK"
else
  if command -v apt-get >/dev/null 2>&1; then
    echo "==> installing python3-tk (needs sudo)"
    sudo apt-get update -qq && sudo apt-get install -y -qq python3-tk
  else
    echo "WARN: tkinter missing — on macOS use python.org or brew python with Tk"
  fi
fi

export PATH="${HOME}/.local/bin:/usr/local/bin:${PATH}"

echo "==> checking Blender"
if "$PYTHON" - <<'PY'
from atelier.runtime import find_blender, blender_hint
import sys
b = find_blender()
if not b:
    print(blender_hint(), file=sys.stderr)
    raise SystemExit(1)
print(b)
PY
then
  echo "==> Blender OK"
else
  echo "WARN: Blender not found — install it, then re-run or set ATELIER_BLENDER=/path/to/blender"
fi

mkdir -p customs renders/desktop
chmod +x "$ROOT/scripts/run-atelier.sh" "$ROOT/Atelier.command" 2>/dev/null || true

echo ""
echo "Done. Start the desktop app on THIS machine with:"
echo "  $ROOT/scripts/run-atelier.sh"
echo "or:"
echo "  atelier desktop"
echo ""
