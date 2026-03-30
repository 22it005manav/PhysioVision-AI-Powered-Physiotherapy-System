@echo off
REM Creates backend_env_310 with Python 3.10 for MediaPipe legacy "solutions" (pose).
REM Python 3.13 Mediapipe wheels do NOT include mp.solutions on Windows.

cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
  echo Python launcher ^(py^) not found. Install Python 3.10 from https://www.python.org/downloads/
  echo During setup, enable "Add Python to PATH" and "py launcher".
  pause
  exit /b 1
)

py -3.10 -c "import sys; print(sys.version)" >nul 2>&1
if errorlevel 1 (
  echo Python 3.10 is not installed. Install it from https://www.python.org/downloads/
  echo Then re-run this script.
  pause
  exit /b 1
)

echo Creating venv backend_env_310 with Python 3.10 ...
py -3.10 -m venv backend_env_310
backend_env_310\Scripts\python.exe -m pip install --upgrade pip
backend_env_310\Scripts\pip.exe install -r requirements.txt
echo.
echo Done. Start the vision server with:
echo   backend_env_310\Scripts\python.exe main.py
echo.
pause
