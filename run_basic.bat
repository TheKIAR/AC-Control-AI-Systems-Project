@echo off
REM Double-click this to open the basic GUI every time.
set ROOT=%~dp0
if exist "%ROOT%.venv\Scripts\python.exe" (
  "%ROOT%.venv\Scripts\python.exe" "%ROOT%run_basic.py"
) else (
  python "%ROOT%run_basic.py"
)
pause
