@echo off
REM PhysioVision Complete Project Startup Script
REM This script starts all services in separate windows

echo.
echo ════════════════════════════════════════════════════════════════════
echo   PhysioVision AI-Powered Physiotherapy System
echo   Complete Startup Script
echo ════════════════════════════════════════════════════════════════════
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running with administrator privileges
) else (
    echo ⚠️  Warning: Consider running as Administrator for best results
)

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo 📋 Starting MongoDB...
echo ────────────────────────────────────────────────────────────────────
REM Check if MongoDB is running
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ MongoDB is already running
) else (
    echo ⚠️  MongoDB not detected. Starting...
    REM Attempt to start MongoDB (adjust path if needed)
    sc start MongoDB >nul 2>&1
    if %errorLevel% == 0 (
        echo ✅ MongoDB service started
        timeout /t 3 /nobreak
    ) else (
        echo ⚠️  Could not start MongoDB service
        echo    Make sure MongoDB is installed: https://www.mongodb.com/try/download/community
    )
)

echo.
echo 🚀 Starting Backend API Server...
echo ────────────────────────────────────────────────────────────────────
start "PhysioVision Backend" cmd /k "cd /d "%SCRIPT_DIR%Backend\Backend" && echo Activating virtual environment... && call venv\Scripts\activate.bat && echo. && echo ✅ Backend environment ready && echo Starting FastAPI server on http://localhost:8002 && python app\main.py"

timeout /t 5 /nobreak

echo.
echo 🎥 Starting Vision WebSocket Server...
echo ────────────────────────────────────────────────────────────────────
start "PhysioVision Vision Backend" cmd /k "cd /d "%SCRIPT_DIR%Backend_Vision" && if exist backend_env_310\Scripts\python.exe (echo Using Python 3.10 env backend_env_310 && backend_env_310\Scripts\python.exe main.py) else if exist venv\Scripts\python.exe (echo Using local venv && venv\Scripts\python.exe main.py) else (echo Using system Python && python main.py)"

timeout /t 5 /nobreak

echo.
echo 🌐 Starting Frontend Dev Server...
echo ────────────────────────────────────────────────────────────────────
start "PhysioVision Frontend" cmd /k "cd /d "%SCRIPT_DIR%" && echo Installing dependencies if needed... && npm install >nul 2>&1 && echo Starting Next.js on http://localhost:3001 && npm run dev -- -p 3001"

timeout /t 5 /nobreak

echo.
echo ════════════════════════════════════════════════════════════════════
echo ✨ All Services Started!
echo ════════════════════════════════════════════════════════════════════
echo.
echo 📍 Access Points:
echo    Frontend:     http://localhost:3001
echo    Backend API:  http://localhost:8002
echo    API Docs:     http://localhost:8002/docs
echo    Vision WS:    ws://localhost:8765
echo.
echo 🛠️  Services Running:
echo    ✅ MongoDB       localhost:27017
echo    ✅ Backend API   localhost:8002
echo    ✅ Vision WS     localhost:8765
echo    ✅ Frontend UI   localhost:3001
echo.
echo 💡 Tips:
echo    - Sign-in/Register: Use the forms on http://localhost:3001
echo    - Test API: Visit http://localhost:8002/docs
echo    - Close windows to stop services
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

pause
