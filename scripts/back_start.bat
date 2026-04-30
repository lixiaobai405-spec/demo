@echo off
setlocal

cd /d "%~dp0.."
echo [Meitai Demo] Starting backend on http://localhost:8000

set "PYTHON_CMD=python"
where %PYTHON_CMD% >nul 2>nul
if errorlevel 1 (
  set "PYTHON_CMD=py -3"
)

echo [Meitai Demo] Using Python command: %PYTHON_CMD%

call %PYTHON_CMD% -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000

if errorlevel 1 pause
endlocal
