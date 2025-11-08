@echo off
echo ============================================================================
echo   Background Remover - ONNXRUNTIME DLL FIX
echo ============================================================================
echo.
echo This will fix the "DLL load failed" error with onnxruntime.
echo.
echo STEP 1: Installing/Upgrading onnxruntime
echo ============================================================================
echo.

echo Uninstalling any existing onnxruntime versions...
pip uninstall -y onnxruntime onnxruntime-gpu

echo.
echo Installing onnxruntime 1.16.3 (stable version)...
pip install onnxruntime==1.16.3

echo.
echo ============================================================================
echo STEP 2: IMPORTANT - Install Visual C++ Redistributables
echo ============================================================================
echo.
echo The error you're seeing is because Windows is missing required DLL files.
echo.
echo YOU MUST INSTALL VISUAL C++ REDISTRIBUTABLES:
echo.
echo   1. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
echo   2. Run the installer
echo   3. Click "Install"
echo   4. RESTART YOUR COMPUTER
echo   5. Then run this application again
echo.
echo Press any key to open the download page in your browser...
pause
start https://aka.ms/vs/17/release/vc_redist.x64.exe

echo.
echo ============================================================================
echo STEP 3: After installing Visual C++ and restarting
echo ============================================================================
echo.
echo Run: test.bat
echo.
echo This will verify the installation is working correctly.
echo.
echo ============================================================================
pause
