@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo [Meitai Demo] Full Stack with Ngrok Public URL
echo ============================================================
echo.

:: ── 1. Find ngrok ──
set "NGROK_EXE=%USERPROFILE%\ngrok\ngrok.exe"
if not exist "%NGROK_EXE%" set "NGROK_EXE=E:\ngrok-v3-stable-windows-amd64\ngrok.exe"
if not exist "%NGROK_EXE%" (
    echo [ERROR] ngrok not found!
    echo   Checked: %%USERPROFILE%%\ngrok\ngrok.exe
    echo   Checked: E:\ngrok-v3-stable-windows-amd64\ngrok.exe
    pause
    exit /b 1
)
echo [OK] ngrok found: %NGROK_EXE%

:: ── 2. Kill stale ngrok ──
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: ── 3. Start backend ──
echo.
echo [1/4] Starting backend (port 8000)...
start "Meitai Backend" cmd /k "scripts\back_start.bat"
timeout /t 3 /nobreak >nul
echo [OK] Backend window opened

:: ── 4. Start ngrok tunnel ──
echo.
echo [2/4] Starting ngrok tunnel to port 8000...
start "Meitai Ngrok" cmd /k "%NGROK_EXE% http 8000 --log=stdout"
echo [OK] ngrok window opened

:: ── 5. Wait for ngrok URL ──
echo.
echo [3/4] Waiting for ngrok public URL...

set "PUBLIC_URL="
for /l %%i in (1,1,20) do (
    timeout /t 2 /nobreak >nul
    for /f "delims=" %%u in ('node "scripts\ngrok_url.js" 2^>nul') do set "PUBLIC_URL=%%u"
    if not "!PUBLIC_URL!"=="" (
        echo        Public URL: !PUBLIC_URL!
        goto :ngrok_ready
    )
    echo        Waiting... (%%i/20)
)

echo [WARNING] Could not get ngrok URL after 40 seconds
echo           Check if ngrok is running at http://127.0.0.1:4040
echo           Falling back to localhost
set "PUBLIC_URL=http://localhost:8000"
goto :start_frontend

:ngrok_ready
:: Write public URL to frontend env
echo NEXT_PUBLIC_API_BASE_URL=!PUBLIC_URL!> frontend\.env.local
echo [OK] Written to frontend\.env.local

:: ── 6. Start frontend ──
:start_frontend
echo.
echo [4/4] Starting frontend (port 3001)...
start "Meitai Frontend" cmd /k "scripts\front_start.bat"
timeout /t 2 /nobreak >nul
echo [OK] Frontend window opened

:: ── Done ──
echo.
echo ============================================================
echo [Meitai Demo] All services starting!
echo.
echo   Backend:    http://localhost:8000
echo   Frontend:   http://localhost:3001
if not "!PUBLIC_URL!"=="http://localhost:8000" (
    echo   Ngrok:      !PUBLIC_URL!
)
echo   API Docs:   http://localhost:8000/docs
echo.
echo   The public ngrok URL changes each time ngrok restarts.
echo   Make sure frontend\.env.local contains the correct URL.
echo ============================================================
echo.
echo Close this window to stop ngrok only.
echo Backend and Frontend run in separate windows.
pause >nul
endlocal
