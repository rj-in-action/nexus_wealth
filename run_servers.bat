@echo off
setlocal

:: Configured ports
set BACKEND_PORT=8000
set FRONTEND_PORT=3000

:: Kill any process listening on the backend/frontend ports
echo Checking for existing servers on ports %BACKEND_PORT% and %FRONTEND_PORT%...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R "LISTENING.*:%BACKEND_PORT%\|LISTENING.*:%FRONTEND_PORT%"') do (
    echo Stopping existing process %%p
    taskkill /F /PID %%p >nul 2>&1
)

:: Start backend server
echo Starting backend server on port %BACKEND_PORT%...
start "Nexus Wealth Backend" cmd /k "cd /d "%~dp0backend" && uvicorn main:app --reload --port %BACKEND_PORT%"

:: Start frontend local file server
echo Starting frontend server on port %FRONTEND_PORT%...
start "Nexus Wealth Frontend" cmd /k "cd /d "%~dp0frontend" && python -m http.server %FRONTEND_PORT%"

:: Open browser to frontend dashboard
echo Opening frontend in your default browser...
start "" "http://127.0.0.1:%FRONTEND_PORT%/index.html"

:: Done
echo Servers started. Press any key to close this launcher window.
pause >nul
endlocal
