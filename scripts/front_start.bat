@echo off
setlocal

pushd "%~dp0..\frontend"
echo [Meitai Demo] Starting frontend...

:: Check if dependencies need installation
if not exist "node_modules\next" (
  echo [Meitai Demo] Dependencies not found, running npm install...
  call npm install
  if errorlevel 1 (
    echo [Meitai Demo] ERROR: npm install failed
    pause
    popd
    exit /b 1
  )
)

:: Resolve port and clean up a stale local frontend if needed
for /f "usebackq delims=" %%p in (`powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0resolve_frontend_port.ps1" -PreferredPort 3001 -FrontendDir "%CD%"`) do set "PORT=%%p"

if not defined PORT (
  echo [Meitai Demo] ERROR: failed to resolve frontend port
  pause
  popd
  exit /b 1
)

echo [Meitai Demo] Frontend - http://localhost:%PORT%
call npx next dev -p %PORT%

if errorlevel 1 pause
popd
endlocal
