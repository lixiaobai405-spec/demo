@echo off
setlocal

cd /d "%~dp0.."
echo [Meitai Demo] Starting backend on http://localhost:8000
echo [Meitai Demo] Using Python: E:\Anaconda3\envs\rag-env\python.exe

E:\Anaconda3\envs\rag-env\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000

if errorlevel 1 pause
endlocal
