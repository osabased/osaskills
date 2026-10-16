#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

rokit install
pesde install --locked
stylua --check src
selene src
python scripts/check_guards.py
rojo build default.project.json -o build/coin-run.rbxlx
