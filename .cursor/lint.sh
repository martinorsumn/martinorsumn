#!/usr/bin/env bash
# Lints Markdown files with PyMarkdown using the repo's .pymarkdown.json config.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -x ".venv/bin/python" ]; then
  echo "Virtualenv missing; run bash .cursor/install.sh first." >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

exec pymarkdown --config .pymarkdown.json scan "${@:-README.md}"
