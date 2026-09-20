@echo off
REM Double-click this to open the GUI every time.
set ROOT=%~dp0
if exist "%ROOT%.venv\Scripts\python.exe" (
  "%ROOT%.venv\Scripts\python.exe" "%ROOT%run_gui.py"
) else (
  python "%ROOT%run_gui.py"
)
pause
