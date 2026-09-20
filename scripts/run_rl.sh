#!/bin/bash
# Run from project root: bash scripts/run_rl.sh
set -e
cd "$(dirname "$0")/.."
if [ -f ".venv/Scripts/activate" ]; then
  source ".venv/Scripts/activate"
elif [ -f ".venv/bin/activate" ]; then
  source ".venv/bin/activate"
fi

python src/main.py --console