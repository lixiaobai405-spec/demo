@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"
echo ============================================================
echo   Meitai Demo - Full Stack Application
echo ============================================================
echo.

:: ---- 1. Backend ----
echo [1/3] Starting backend (port 8000)...
start "Meitai Backend" cmd /k "cd /d %~dp0 && call E:\Anaconda3\Scripts\activate.bat && conda activate rag-env && python backend\run.py 8000"
timeout /t 3 /nobreak >nul
echo        Backend:  http://localhost:8000

:: ---- 2. Ngrok (optional) ----
echo.
echo [2/3] Ngrok tunnel (optional)...

set "NGROK_EXE=%USERPROFILE%\ngrok\ngrok.exe"
if not exist "%NGROK_EXE%" (
    echo        Ngrok not found - using localhost only
    goto :start_frontend
)

taskkill /F /IM ngrok.exe >nul 2>&1
start "Meitai Ngrok" cmd /c "%NGROK_EXE% http 8000 --log=stdout"

echo        Waiting for public URL...
set "PUBLIC_URL="
for /l %%i in (1,1,15) do (
    timeout /t 1 /nobreak >nul
    for /f "delims=" %%u in ('node "scripts\ngrok_url.js" 2^>nul') do set "PUBLIC_URL=%%u"
    if not "!PUBLIC_URL!"=="" goto :ngrok_ok
)
echo        Could not get ngrok URL - using localhost
goto :start_frontend

:ngrok_ok
echo        Public:   !PUBLIC_URL!
echo NEXT_PUBLIC_API_BASE_URL=!PUBLIC_URL!> frontend\.env.local

:: ---- 3. Frontend ----
:start_frontend
echo.
echo [3/3] Starting frontend (port 3001)...

if not exist "frontend\node_modules\next" (
    echo        Installing npm dependencies...
    pushd frontend
    call npm install
    popd
)

start "Meitai Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
timeout /t 2 /nobreak >nul

:: ---- Done ----
echo.
echo ============================================================
echo   All services starting!
echo.
echo   Backend:   http://localhost:8000
if defined PUBLIC_URL echo   Ngrok:     !PUBLIC_URL!
echo   Frontend:  http://localhost:3001
echo ============================================================
echo.
echo Press any key to close this window (services keep running)
pause >nul
endlocal
