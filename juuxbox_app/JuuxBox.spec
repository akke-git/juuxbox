# -*- mode: python ; coding: utf-8 -*-
"""
JuuxBox PyInstaller Spec File
Build command: pyinstaller JuuxBox.spec
"""

import os
from pathlib import Path

block_cipher = None

# 현재 디렉토리
BASE_DIR = Path(SPECPATH)

a = Analysis(
    ['app.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=[
        ('webui', 'webui'),  # 웹 UI 폴더 전체 포함
        ('install_prerequisites.bat', '.'),  # 설치 스크립트
        ('README_DEPLOY.txt', '.'),  # 배포용 README
        ('installers', 'installers'),  # 설치 파일들 (VC++, WebView2)
    ],
    hiddenimports=[
        'miniaudio',
        'mutagen',
        'mutagen.mp3',
        'mutagen.flac',
        'mutagen.mp4',
        'mutagen.oggvorbis',
        'mutagen.wave',
        'mutagen.aiff',
        'webview',
        'webview.platforms.edgechromium',  # Windows Edge WebView2
        'clr_loader',
        'pythonnet',
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
    [],
    exclude_binaries=True,
    name='JuuxBox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 앱이므로 콘솔 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘 파일 경로 (예: 'icon.ico')
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JuuxBox',
)
