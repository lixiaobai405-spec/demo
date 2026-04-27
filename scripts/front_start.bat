@echo off
setlocal

cd /d "%~dp0..\frontend"
<<<<<<< HEAD
echo [Meitai Demo] Starting frontend on http://localhost:3001
=======
echo [Meitai Demo] Starting frontend on http://localhost:3000
>>>>>>> 7c801e5cd2276d02a68da5a7f720b02c018936bd

if not exist "node_modules" (
  echo [Meitai Demo] node_modules not found, running npm install first...
  call npm install
  if errorlevel 1 pause
)

call npm run dev

if errorlevel 1 pause
endlocal
