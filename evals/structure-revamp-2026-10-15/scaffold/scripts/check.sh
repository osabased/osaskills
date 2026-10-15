#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

rokit install
wally install
stylua --check src
selene src
rojo build default.project.json -o build/arena.rbxlx
