@echo off
setlocal

cd /d "%~dp0.."
echo [Meitai Demo] Starting backend...

:: Initialize conda for batch script
call E:\Anaconda3\Scripts\activate.bat
call conda activate rag-env
if errorlevel 1 (
  echo [Meitai Demo] ERROR: Failed to activate rag-env. Please check conda installation.
  pause
  exit /b 1
)

echo [Meitai Demo] Using conda environment: rag-env
echo [Meitai Demo] Python version:
python --version

call python backend\run.py 8000

if errorlevel 1 pause
endlocal
