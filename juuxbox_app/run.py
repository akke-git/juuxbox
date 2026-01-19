#!/usr/bin/env python3
"""
JuuxBox - Hi-Fi Music Player
============================
WASAPI Exclusive 모드를 지원하는 하이파이 뮤직 플레이어

Usage:
    python run.py              # 앱 실행
    python run.py --scan DIR   # 폴더 스캔 후 실행
"""

import sys
import argparse
from pathlib import Path

# 프로젝트 경로 설정
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication

from db.models import create_tables
from db.scanner import LibraryScanner
from db.repository import TrackRepository
from utils.logger import setup_logging
from utils.config import load_config
from utils.error_handler import get_error_handler


def scan_folder(folder_path: str):
    """폴더 스캔 및 DB 저장"""
    print(f"📁 스캔 중: {folder_path}")
    
    scanner = LibraryScanner(
        on_progress=lambda c, t: print(f"   {c}/{t}")
    )
    tracks = scanner.scan_folder(folder_path)
    
    for track in tracks:
        TrackRepository.insert(track)
    
    print(f"✅ {len(tracks)}개 트랙 저장 완료")


def main():
    parser = argparse.ArgumentParser(description="JuuxBox Hi-Fi Music Player")
    parser.add_argument("--scan", metavar="DIR", help="스캔할 음악 폴더")
    parser.add_argument("--debug", action="store_true", help="디버그 모드")
    args = parser.parse_args()
    
    # 로깅 설정
    import logging
    level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level)
    
    # DB 초기화
    create_tables()
    
    # 폴더 스캔 (옵션)
    if args.scan:
        scan_folder(args.scan)
    
    # 에러 핸들러
    error_handler = get_error_handler()
    
    # Qt 앱 생성
    app = QApplication(sys.argv)
    app.setApplicationName("JuuxBox")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("JuuxBox")
    
    # 폰트 설정 (한글 지원)
    from PySide6.QtGui import QFont, QFontDatabase
    
    # 사용 가능한 한글 폰트 확인
    korean_fonts = ["Malgun Gothic", "맑은 고딕", "NanumGothic", "나눔고딕", "Gulim", "굴림"]
    available_fonts = QFontDatabase.families()
    
    selected_font = None
    for kf in korean_fonts:
        if kf in available_fonts:
            selected_font = kf
            break
    
    if selected_font:
        font = QFont(selected_font, 9)
    else:
        font = QFont("Sans Serif", 9)
    
    app.setFont(font)
    print(f"📝 폰트: {font.family()}")
    
    # 설정 로드
    config = load_config()
    
    # 메인 윈도우 (통합 버전)
    from tests.test_integration import IntegratedMainWindow
    window = IntegratedMainWindow(config)
    window.show()
    
    print("\n🎵 JuuxBox 시작!")
    print("   - 곡을 더블클릭하면 재생됩니다")
    print("   - 스페이스바: 재생/일시정지")
    print("   - 좌/우 화살표: 이전/다음 곡\n")
    
    # 이벤트 루프
    exit_code = app.exec()
    
    # 정리
    error_handler.cleanup()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
