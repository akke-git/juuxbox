#!/bin/bash
# JuuxBox Build Script
# 실행 파일 빌드를 위한 스크립트

set -e

echo "🎵 JuuxBox 빌드 시작..."

# 가상환경 확인
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  가상환경을 활성화하세요 (권장)"
fi

# 의존성 설치
echo "📦 의존성 설치 중..."
pip install -r requirements.txt
pip install pyinstaller

# 리소스 폴더 확인
mkdir -p resources/icons
mkdir -p resources/fonts

# 빌드
echo "🔨 빌드 중..."
cd "$(dirname "$0")"
pyinstaller build.spec --clean

echo ""
echo "✅ 빌드 완료!"
echo "   실행 파일: dist/JuuxBox"
echo ""
