@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"
echo ============================================================
echo [Meitai Demo] Starting Full Stack Application
echo ============================================================
echo.

:: ---- 1. Backend ----
echo [1/4] Starting backend...
start "Meitai Backend" cmd /k "scripts\back_start.bat"
timeout /t 2 /nobreak >nul

:: ---- 2. Ngrok ----
echo [2/4] Starting ngrok tunnel...

set "NGROK_EXE=%USERPROFILE%\ngrok\ngrok.exe"
if not exist "%NGROK_EXE%" (
    echo [WARNING] ngrok not found at %USERPROFILE%\ngrok\ngrok.exe
    echo [WARNING] Skipping ngrok, using localhost for API
    goto :start_frontend
)

taskkill /F /IM ngrok.exe >nul 2>&1

start "Meitai Ngrok" cmd /c "%NGROK_EXE% http 8000 --log=stdout"

:: ---- 3. Get ngrok URL ----
echo [3/4] Waiting for ngrok tunnel...

set "PUBLIC_URL="
for /l %%i in (1,1,15) do (
    timeout /t 1 /nobreak >nul
    for /f "delims=" %%u in ('node "scripts\ngrok_url.js" 2^>nul') do set "PUBLIC_URL=%%u"
    if not "!PUBLIC_URL!"=="" goto :ngrok_ok
)
echo [WARNING] Could not get ngrok URL, using localhost
goto :start_frontend

:ngrok_ok
echo        Public URL: !PUBLIC_URL!
echo NEXT_PUBLIC_API_BASE_URL=!PUBLIC_URL!> frontend\.env.local

:: ---- 4. Frontend ----
:start_frontend
echo [4/4] Starting frontend...
start "Meitai Frontend" cmd /k "scripts\front_start.bat"

:: ---- Done ----
echo.
echo ============================================================
echo [Meitai Demo] All services starting...
echo   Backend:   http://localhost:8000
if defined PUBLIC_URL echo   Ngrok:     !PUBLIC_URL!
echo   Frontend:  http://localhost:3001
echo ============================================================
echo.
echo Press any key to close this launcher (services keep running)
pause >nul
endlocal
