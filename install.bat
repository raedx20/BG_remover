@echo off
REM ============================================================================
REM Background Remover - Installation Script for Windows
REM CPU-Only Version - Works on Intel Iris Xe and all CPUs!
REM ============================================================================

echo.
echo ============================================================================
echo   Background Remover - White Product Edition
echo   Installation Script for Windows
echo ============================================================================
echo.
echo This will install all required libraries for CPU-based processing.
echo No dedicated GPU required - works great on Intel Iris Xe!
echo.
echo Press Ctrl+C to cancel, or
pause

REM Check if Python is installed
echo.
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

python --version
echo Python found!

REM Upgrade pip
echo.
echo [2/4] Upgrading pip to latest version...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Could not upgrade pip, continuing anyway...
)

REM Install requirements
echo.
echo [3/4] Installing required libraries...
echo This may take 5-10 minutes depending on your internet connection.
echo.
echo Installing: OpenCV, NumPy, Pillow, rembg, PyQt5, PyYAML, tqdm
echo.

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo Common solutions:
    echo 1. Run this script as Administrator
    echo 2. Check your internet connection
    echo 3. Try: python -m pip install --upgrade pip
    echo.
    pause
    exit /b 1
)

REM Download AI models (optional, can be done on first run)
echo.
echo [4/4] Testing installation...
python -c "import cv2, numpy, yaml, rembg; print('All libraries installed successfully!')"
if errorlevel 1 (
    echo.
    echo WARNING: Some libraries may not be properly installed.
    echo Try running the application anyway - it might still work!
    echo.
) else (
    echo.
    echo ============================================================================
    echo   SUCCESS! Installation Complete!
    echo ============================================================================
    echo.
    echo You can now run the application with:
    echo   python app.py
    echo.
    echo Or double-click:
    echo   run.bat
    echo.
    echo NOTE: On first run, AI models will be downloaded automatically
    echo       (100-200MB). This happens only once.
    echo.
    echo ============================================================================
)

echo.
pause
