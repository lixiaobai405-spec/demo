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

:: Find available port (auto-fallback)
for /f "usebackq delims=" %%p in (`node "%~dp0find_port.js" 3001`) do set "PORT=%%p"

echo [Meitai Demo] Frontend - http://localhost:%PORT%
call npx next dev -p %PORT%

if errorlevel 1 pause
popd
endlocal
