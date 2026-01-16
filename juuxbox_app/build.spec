# JuuxBox - Hi-Fi Music Player
# Build configuration for PyInstaller

# PyInstaller spec file
# Usage: pyinstaller build.spec

import sys
from pathlib import Path

block_cipher = None

# 프로젝트 경로
project_path = Path(__file__).parent

a = Analysis(
    ['main.py'],
    pathex=[str(project_path)],
    binaries=[],
    datas=[
        ('resources/styles', 'resources/styles'),
        ('resources/icons', 'resources/icons'),
    ],
    hiddenimports=[
        'miniaudio',
        'mutagen',
        'mutagen.flac',
        'mutagen.mp4',
        'mutagen.aiff',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='JuuxBox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 앱이므로 콘솔 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/juuxbox.ico',  # 아이콘 (있는 경우)
)
