@echo off
echo ========================================
echo JuuxBox Build Script
echo ========================================
echo.

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM PyInstaller 설치 확인
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM 빌드 디렉토리로 이동
cd juuxbox_app

REM 이전 빌드 정리
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM PyInstaller 실행
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
