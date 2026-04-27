@echo off
setlocal

cd /d "%~dp0.."
echo [Meitai Demo] Starting backend on http://localhost:8000
<<<<<<< HEAD

set "PYTHON_CMD=python"
where %PYTHON_CMD% >nul 2>nul
if errorlevel 1 (
  set "PYTHON_CMD=py -3"
)

echo [Meitai Demo] Using Python command: %PYTHON_CMD%

call %PYTHON_CMD% -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
=======
echo [Meitai Demo] Using Python: E:\Anaconda3\envs\rag-env\python.exe

E:\Anaconda3\envs\rag-env\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
>>>>>>> 7c801e5cd2276d02a68da5a7f720b02c018936bd

if errorlevel 1 pause
endlocal
