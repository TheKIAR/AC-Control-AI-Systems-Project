"""One-click GUI launcher. Double-click or run: python run_gui.py"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
for p in (str(SRC), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from src.main import console_demo, launch_gui  # noqa: E402

if __name__ == "__main__":
    if "--console" in sys.argv or "--no-gui" in sys.argv:
        console_demo()
    elif "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python run_gui.py [--console|--no-gui]")
        print("  No args (or double-click) opens the GUI every time.")
    else:
        sys.exit(0 if launch_gui() else 1)
