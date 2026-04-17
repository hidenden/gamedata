#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
VENV_DIR="${1:-$ROOT_DIR/.venv}"

if [ ! -d "$VENV_DIR" ]; then
  echo "[error] venv not found: $VENV_DIR" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "[error] uv command not found" >&2
  exit 1
fi

echo "[info] clear macOS hidden flags: $VENV_DIR"
chflags -R nohidden "$VENV_DIR"

echo "[info] reinstall editable package"
cd "$ROOT_DIR"
uv pip install -e .

echo "[info] verify import"
uv run python -c "import gamedata,sys; print(sys.executable); print(gamedata.__file__)"

echo "[ok] gamedata import is available"
