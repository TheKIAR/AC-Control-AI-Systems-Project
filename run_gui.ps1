# Always use the project venv (Python 3.12, has matplotlib + tkinter).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Py)) { $Py = "python" }
& $Py (Join-Path $Root "run_gui.py")
