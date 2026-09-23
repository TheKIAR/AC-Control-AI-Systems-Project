"""Single source of truth for the project versions.

Shown in the GUI title bars so the two executables can be told apart,
and mirrored in ``setup.py`` (which tracks the main app).
"""

MAIN_VERSION = "2.0.0"
BASIC_VERSION = "1.0.0"

# Backwards-compatible alias: the main app version.
__version__ = MAIN_VERSION
