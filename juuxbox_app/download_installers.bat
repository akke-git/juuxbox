@echo off
REM JuuxBox - Download Deployment Installers
REM This script downloads VC++ Redistributable and WebView2 for deployment

echo ========================================
echo JuuxBox Installer Downloader
echo ========================================
echo.
echo This will download:
echo   1. Visual C++ Redistributable 2015-2022 (x64)
echo   2. Microsoft Edge WebView2 Runtime
echo.
echo Target folder: installers\
echo.
pause

REM Create installers folder
set SCRIPT_DIR=%~dp0
set INSTALLERS_DIR=%SCRIPT_DIR%installers
if not exist "%INSTALLERS_DIR%" mkdir "%INSTALLERS_DIR%"

echo.
echo ========================================
echo 1/2: Downloading VC++ Redistributable...
echo ========================================

if exist "%INSTALLERS_DIR%\vc_redist.x64.exe" (
    echo Already downloaded: vc_redist.x64.exe
) else (
    echo Downloading...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile '%INSTALLERS_DIR%\vc_redist.x64.exe'}"
    
    if exist "%INSTALLERS_DIR%\vc_redist.x64.exe" (
        echo Download complete: vc_redist.x64.exe
    ) else (
        echo Download failed!
        echo Manual download: https://aka.ms/vs/17/release/vc_redist.x64.exe
    )
)

echo.
echo ========================================
echo 2/2: Downloading Edge WebView2...
echo ========================================

if exist "%INSTALLERS_DIR%\MicrosoftEdgeWebview2Setup.exe" (
    echo Already downloaded: MicrosoftEdgeWebview2Setup.exe
) else (
    echo Downloading...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/?linkid=2124701' -OutFile '%INSTALLERS_DIR%\MicrosoftEdgeWebview2Setup.exe'}"
    
    if exist "%INSTALLERS_DIR%\MicrosoftEdgeWebview2Setup.exe" (
        echo Download complete: MicrosoftEdgeWebview2Setup.exe
    ) else (
        echo Download failed!
        echo Manual download: https://go.microsoft.com/fwlink/?linkid=2124701
    )
)

echo.
echo ========================================
echo FFmpeg (Optional for M4A playback)
echo ========================================
echo.
echo FFmpeg is not downloaded automatically (large file ~100MB).
echo If you need M4A/AAC playback support:
echo.
echo 1. Visit: https://www.gyan.dev/ffmpeg/builds/
echo 2. Download: ffmpeg-release-essentials.zip
echo 3. Extract: bin\ffmpeg.exe
echo 4. Copy to: same folder as JuuxBox.exe
echo.

echo.
echo ========================================
echo Download Complete!
echo ========================================
echo.
dir "%INSTALLERS_DIR%"
echo.
echo These files will be included in the build package.
echo.
pause
