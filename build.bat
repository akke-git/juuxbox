@echo off
echo ========================================
echo JuuxBox Build Script
echo ========================================
echo.

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Navigate to build directory
cd juuxbox_app

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Run PyInstaller
echo.
echo Building JuuxBox...
pyinstaller JuuxBox.spec

echo.
echo ========================================
if exist "dist\JuuxBox\JuuxBox.exe" (
    echo Build SUCCESS!
    echo Output: juuxbox_app\dist\JuuxBox\
    echo.
    echo To run: dist\JuuxBox\JuuxBox.exe
) else (
    echo Build FAILED!
)
echo ========================================

cd ..
pause
