#!/usr/bin/env bash
# Launches the offline README preview server in the foreground.
# Used by the `readme-preview` terminal (and as the build `start` command).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -x ".venv/bin/python" ]; then
  echo "Virtualenv missing; running install first..."
  bash .cursor/install.sh
fi

# shellcheck disable=SC1091
source .venv/bin/activate

export PREVIEW_HOST="${PREVIEW_HOST:-0.0.0.0}"
export PREVIEW_PORT="${PREVIEW_PORT:-6419}"

exec python .cursor/preview_server.py
