#!/usr/bin/env python3
"""
Phase 3: UI Test
================
PySide6 기반 Spotify 스타일 UI 테스트
"""

import sys
from pathlib import Path

# 프로젝트 모듈 import
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from ui.main_window import MainWindow
from db.models import create_tables
from db.repository import TrackRepository
from utils.config import load_config


def main():
    """UI 테스트 메인"""
    print("\n" + "="*60)
    print("🎵 JuuxBox UI Test - Phase 3")
    print("="*60)
    
    # DB 초기화
    create_tables()
    
    # 저장된 트랙 확인
    tracks = TrackRepository.get_all()
    print(f"\n📁 저장된 트랙: {len(tracks)}개")
    for t in tracks:
        print(f"   - {t.get('title', 'Unknown')} by {t.get('artist', 'Unknown')}")
    
    # Qt 앱 생성
    app = QApplication(sys.argv)
    app.setApplicationName("JuuxBox")
    app.setApplicationVersion("0.1.0")
    
    # 설정 로드
    config = load_config()
    
    # 메인 윈도우 생성
    window = MainWindow(config)
    
    # 트랙 목록을 UI에 로드
    if hasattr(window, '_song_list'):
        for i, track in enumerate(tracks):
            duration = track.get('duration_seconds', 0)
            duration_str = f"{int(duration//60)}:{int(duration%60):02d}"
            window._song_list.add_song(
                index=i + 1,
                title=track.get('title', 'Unknown'),
                artist=track.get('artist', 'Unknown'),
                album=track.get('album', 'Unknown'),
                duration=duration_str,
                file_path=track.get('file_path', '')
            )
    
    window.show()
    
    print("\n✅ UI 윈도우가 열렸습니다!")
    print("   창을 닫으면 테스트가 종료됩니다.")
    print("="*60 + "\n")
    
    # 이벤트 루프 실행
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
