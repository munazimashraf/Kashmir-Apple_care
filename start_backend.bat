@echo off
title Kashmir Apple Care - Backend API
echo ===================================================
echo   Starting Kashmir Apple Care FastAPI Backend Server
echo ===================================================
echo.

cd /d "%~dp0"

REM Configure standard Python environment paths
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python315" (
    set "PYTHONHOME=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python315"
)
set "PYTHONPATH=%~dp0.venv\Lib\site-packages;%~dp0backend"

if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
) else if exist "C:\Python315\python.exe" (
    set "PYTHON_EXE=C:\Python315\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Using Python: %PYTHON_EXE%
echo Environment: Local VGG19 Inference Engine
echo Server URL: http://127.0.0.1:8000
echo Docs URL  : http://127.0.0.1:8000/docs
echo.

cd backend
"%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Backend stopped or failed to launch.
    pause
)
