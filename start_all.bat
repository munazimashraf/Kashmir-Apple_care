@echo off
title Kashmir Apple Care - Full System Launcher
echo =================================================================
echo   KASHMIR APPLE CARE — Local VGG19 Vision & SKUAST-K Advisory
echo =================================================================
echo.
echo Launching Backend and Frontend in separate windows...
echo.

start "Kashmir Apple Care Backend" cmd /c "start_backend.bat"
timeout /t 2 >nul
start "Kashmir Apple Care Frontend" cmd /c "start_frontend.bat"

echo.
echo Both services are booting up!
echo Frontend will be accessible at : http://localhost:5173
echo Backend API will be accessible at: http://localhost:8000
echo.
pause
