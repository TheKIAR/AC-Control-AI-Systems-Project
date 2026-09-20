#!/bin/bash
# Run from project root: bash scripts/run_fuzzy.sh
# Windows PowerShell users: use run_gui.ps1 / run_gui.bat or: .venv/Scripts/python.exe run_gui.py
set -e
cd "$(dirname "$0")/.."
if [ -f ".venv/Scripts/activate" ]; then
  source ".venv/Scripts/activate"  # Git-Bash on Windows
elif [ -f ".venv/bin/activate" ]; then
  source ".venv/bin/activate"      # macOS/Linux
fi

# No --mode flag exists; console demo runs all systems:
python run_gui.py --help 2>/dev/null || true
python src/main.py --console