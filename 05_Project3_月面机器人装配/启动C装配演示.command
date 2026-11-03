#!/bin/zsh
set -e
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
exec .venv/bin/python C_仿真与装配/run_preloaded_tray_assembly_fast.py --gui "$@"
