@echo off
title Kashmir Apple Care - Web Interface
echo ===================================================
echo   Starting Kashmir Apple Care Vite Web Client
echo ===================================================
echo.

cd /d "%~dp0"

echo Launching Vite development server on http://localhost:5173 ...
echo.

call npx vite --host 0.0.0.0 --port 5173

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Vite failed to start.
    echo Please run: npm install
    pause
)

