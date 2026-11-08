#!/usr/bin/env bash
# Convenience wrapper: runs the resume tailoring tool inside the project venv.
# Passes all arguments through to resume/tailor.py.
#
# Example:
#   bash resume/tailor.sh --company "Acme" --role "SWE Intern" \
#       --job resume/examples/software_engineering_intern.txt
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -x ".venv/bin/python" ]; then
  echo "Virtualenv missing; running install first..." >&2
  bash .cursor/install.sh
fi

# shellcheck disable=SC1091
source .venv/bin/activate
exec python resume/tailor.py "$@"
