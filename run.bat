@echo off
REM ============================================================================
REM Background Remover - Quick Launch Script
REM ============================================================================

echo.
echo ============================================================================
echo   Background Remover - White Product Edition
echo   Starting Application...
echo ============================================================================
echo.
echo NOTE: On first run, AI models will download automatically (100-200MB)
echo       This is normal and happens only once!
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please run install.bat first.
    pause
    exit /b 1
)

REM Run the application
python app.py

REM If the app exits with error
if errorlevel 1 (
    echo.
    echo ============================================================================
    echo   Application exited with an error
    echo ============================================================================
    echo.
    echo If you see "ModuleNotFoundError", run install.bat first.
    echo.
    pause
)
