#!/usr/bin/env python3
"""
Phase 4: Integration Test
=========================
UI와 오디오 엔진 연결 테스트
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from ui.main_window import MainWindow
from app_controller import AppController
from db.models import create_tables
from utils.config import load_config


class IntegratedMainWindow(MainWindow):
    """컨트롤러가 연결된 메인 윈도우"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        
        # 컨트롤러 생성
        self._controller = AppController()
        
        # 트랙 로드 및 UI 연결
        self._load_tracks()
        self._connect_signals()
        
    def _load_tracks(self):
        """트랙 로드 및 UI 표시"""
        tracks = self._controller.load_library()
        
        # 곡 목록에 추가
        for i, track in enumerate(tracks):
            duration = track.get('duration_seconds', 0)
            duration_str = f"{int(duration//60)}:{int(duration%60):02d}"
            self._song_list.add_song(
                index=i + 1,
                title=track.get('title', 'Unknown'),
                artist=track.get('artist', 'Unknown'),
                album=track.get('album', 'Unknown'),
                duration=duration_str,
                file_path=track.get('file_path', '')
            )
        
        # 곡 목록 뷰로 전환
        self._main_stack.setCurrentWidget(self._song_list)
        
    def _connect_signals(self):
        """시그널 연결"""
        # 곡 더블클릭 → 재생
        self._song_list.song_double_clicked.connect(self._on_song_selected)
        
        # 플레이어 바 시그널
        self._player_bar.play_clicked.connect(self._controller.toggle_play)
        self._player_bar.next_clicked.connect(self._controller.next_track)
        self._player_bar.prev_clicked.connect(self._controller.previous_track)
        self._player_bar.volume_changed.connect(
            lambda v: self._controller.set_volume(v / 100.0)
        )
        
        # 컨트롤러 콜백
        self._controller.set_on_track_change(self._on_track_change)
        
    def _on_song_selected(self, file_path: str):
        """곡 선택 시 재생"""
        print(f"🎵 재생: {file_path}")
        self._controller.play_track(file_path)
        
    def _on_track_change(self, track: dict):
        """트랙 변경 시 UI 업데이트"""
        self._player_bar.set_track_info(
            title=track.get('title', 'Unknown'),
            artist=track.get('artist', 'Unknown')
        )
        self._player_bar.set_audio_spec(
            bit_depth=track.get('bit_depth', 16),
            sample_rate=track.get('sample_rate', 44100)
        )
        
    def _on_play_pause(self):
        """재생/일시정지"""
        self._controller.toggle_play()
        self._player_bar.toggle_play()
        
    def _on_previous(self):
        """이전 곡"""
        self._controller.previous_track()
        
    def _on_next(self):
        """다음 곡"""
        self._controller.next_track()
        
    def closeEvent(self, event):
        """종료 시 정리"""
        self._controller.cleanup()
        super().closeEvent(event)


def main():
    print("\n" + "="*60)
    print("🎵 JuuxBox Integration Test - Phase 4")
    print("="*60)
    
    # DB 초기화
    create_tables()
    
    # Qt 앱
    app = QApplication(sys.argv)
    app.setApplicationName("JuuxBox")
    
    # 통합 윈도우
    config = load_config()
    window = IntegratedMainWindow(config)
    window.show()
    
    print("\n✅ 통합 테스트 윈도우 실행!")
    print("   - 곡을 더블클릭하면 재생됩니다")
    print("   - 스페이스바: 재생/일시정지")
    print("   - 좌/우 화살표: 이전/다음 곡")
    print("="*60 + "\n")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
