#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
uv run --locked python dashboard/tools/export_parquet.py "$@"
uv run --locked python dashboard/tools/build_wheel.py
uv run --locked python dashboard/tools/export_notebooks.py
