@echo off
REM JuuxBox - Install Prerequisites
REM Installs required components if not already installed

echo ========================================
echo JuuxBox Prerequisites Installer
echo ========================================
echo.
echo This script will install required components:
echo   1. Visual C++ Redistributable 2015-2022 (x64)
echo   2. Microsoft Edge WebView2 Runtime
echo.
echo Already installed components will be skipped.
echo.
pause

REM Check for administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] This script requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Get script directory
set SCRIPT_DIR=%~dp0
set INSTALLERS_DIR=%SCRIPT_DIR%installers

echo.
echo ========================================
echo 1/2: Checking Visual C++ Redistributable...
echo ========================================

REM Check if VC++ Redistributable is installed
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" /v Version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Visual C++ Redistributable is already installed.
    echo      Skipping...
) else (
    echo [NOT FOUND] Visual C++ Redistributable is not installed.
    
    if exist "%INSTALLERS_DIR%\vc_redist.x64.exe" (
        echo.
        echo Installing... (A window will appear, please follow instructions)
        "%INSTALLERS_DIR%\vc_redist.x64.exe" /install /quiet /norestart
        
        if %errorlevel% equ 0 (
            echo [OK] Visual C++ Redistributable installed successfully!
        ) else (
            echo [WARNING] Installation may have failed (error code: %errorlevel%)
            echo           Manual installation may be required.
        )
    ) else (
        echo.
        echo [WARNING] Installer not found: %INSTALLERS_DIR%\vc_redist.x64.exe
        echo.
        echo Please download manually:
        echo https://aka.ms/vs/17/release/vc_redist.x64.exe
    )
)

echo.
echo ========================================
echo 2/2: Checking Edge WebView2 Runtime...
echo ========================================

REM Check if WebView2 is installed
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Edge WebView2 Runtime is already installed.
    echo      Skipping...
) else (
    echo [NOT FOUND] Edge WebView2 Runtime is not installed.
    
    if exist "%INSTALLERS_DIR%\MicrosoftEdgeWebview2Setup.exe" (
        echo.
        echo Installing... (Please wait)
        "%INSTALLERS_DIR%\MicrosoftEdgeWebview2Setup.exe" /silent /install
        
        if %errorlevel% equ 0 (
            echo [OK] Edge WebView2 Runtime installed successfully!
        ) else (
            echo [WARNING] Installation may have failed (error code: %errorlevel%)
            echo           Manual installation may be required.
        )
    ) else (
        echo.
        echo [WARNING] Installer not found: %INSTALLERS_DIR%\MicrosoftEdgeWebview2Setup.exe
        echo.
        echo Please download manually:
        echo https://go.microsoft.com/fwlink/?linkid=2124701
    )
)

echo.
echo ========================================
echo FFmpeg (Optional - for M4A playback)
echo ========================================

if exist "%SCRIPT_DIR%ffmpeg.exe" (
    echo [OK] FFmpeg.exe is included.
    echo      M4A/AAC playback is supported.
) else (
    echo [NOT FOUND] FFmpeg.exe is not included.
    echo             Only MP3, FLAC, WAV playback is supported.
    echo.
    echo If you need M4A playback, download ffmpeg.exe
    echo and place it in the same folder as JuuxBox.exe
    echo.
    echo Download: https://www.gyan.dev/ffmpeg/builds/
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run JuuxBox.exe
echo.
pause
