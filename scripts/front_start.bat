@echo off
setlocal

cd /d "%~dp0..\frontend"
echo [Meitai Demo] Starting frontend on http://localhost:3000

if not exist "node_modules" (
  echo [Meitai Demo] node_modules not found, running npm install first...
  call npm install
  if errorlevel 1 pause
)

call npm run dev

if errorlevel 1 pause
endlocal
