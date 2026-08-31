#!/usr/bin/env bash
# Idempotent dependency setup for the profile README dev environment.
# Creates a local Python virtualenv and installs the dev tooling
# (Markdown preview server + linter). Safe to run repeatedly.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

VENV_DIR=".venv"

ensure_venv_support() {
  if python3 -c 'import ensurepip' >/dev/null 2>&1; then
    return 0
  fi
  echo "==> python3 venv/ensurepip missing; installing python3-venv"
  local apt="apt-get"
  if command -v sudo >/dev/null 2>&1; then
    apt="sudo apt-get"
  fi
  $apt update -qq
  $apt install -y -qq python3-venv || $apt install -y -qq python3.12-venv
}

ensure_venv_support

if [ ! -x "${VENV_DIR}/bin/python" ]; then
  echo "==> Creating virtualenv at ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "==> Upgrading pip"
python -m pip install --upgrade pip >/dev/null

echo "==> Installing dev dependencies"
pip install -r requirements-dev.txt

echo "==> Install complete. Tooling versions:"
python -c "from importlib.metadata import version; print('Flask', version('Flask'), '| Markdown', version('Markdown'), '| Pygments', version('Pygments'))"
pymarkdown version
