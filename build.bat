@echo off
echo ============================================
echo   World Clock - Windows Build Script
echo ============================================
echo.

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from python.org and try again.
    pause
    exit /b 1
)

:: Install dependencies
echo [1/3] Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller
echo.

:: Build the exe
echo [2/3] Building WorldClock.exe ...
pyinstaller worldclock.spec --noconfirm
echo.

:: Result
if exist "dist\WorldClock.exe" (
    echo [3/3] SUCCESS!
    echo.
    echo   Output: dist\WorldClock.exe
    echo   You can copy this single file anywhere and run it.
) else (
    echo [3/3] Build failed. Check the output above for errors.
)

echo.
pause
