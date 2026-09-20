#!/bin/bash

# This script runs the data generation methods (console mode).
set -e
cd "$(dirname "$0")/.."
if [ -f ".venv/Scripts/activate" ]; then
  source ".venv/Scripts/activate"
elif [ -f ".venv/bin/activate" ]; then
  source ".venv/bin/activate"
fi

python src/main.py --console

echo "Data generation completed."