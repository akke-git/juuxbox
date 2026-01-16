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
from db.scanner import LibraryScanner
from db.repository import TrackRepository
from utils.config import load_config


class IntegratedMainWindow(MainWindow):
    """컨트롤러가 연결된 메인 윈도우"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        
        # 컨트롤러 생성
        self._controller = AppController()
        
        # 재생 위치 추적
        self._playback_position = 0.0
        self._playback_duration = 0.0
        
        # 진행바 업데이트 타이머 (100ms 간격 - 부드러운 이동)
        self._progress_timer = QTimer()
        self._progress_timer.setInterval(100)
        self._progress_timer.timeout.connect(self._update_progress)
        
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
                folder_name=track.get('folder_name', ''),
                duration=duration_str,
                file_path=track.get('file_path', '')
            )
        
        # 곡 목록 뷰로 전환
        self._main_stack.setCurrentWidget(self._song_list)
        
    def _connect_signals(self):
        """시그널 연결"""
        # 곡 더블클릭 → 재생
        self._song_list.song_double_clicked.connect(self._on_song_selected)
        
        # 플레이어 바 시그널 - play/pause/stop 연결
        self._player_bar.play_clicked.connect(self._on_toggle_play)
        self._player_bar.pause_clicked.connect(self._on_toggle_play)
        self._player_bar.stop_clicked.connect(self._controller.stop)
        self._player_bar.next_clicked.connect(self._controller.next_track)
        self._player_bar.prev_clicked.connect(self._controller.previous_track)
        self._player_bar.seek_changed.connect(self._on_seek)
        self._player_bar.volume_changed.connect(
            lambda v: self._controller.set_volume(v / 100.0)
        )
        
        # 컨트롤러 콜백
        self._controller.set_on_track_change(self._on_track_change)
        
        # 사이드바: 폴더 추가
        self._sidebar.add_folder_clicked.connect(self._on_folder_added)
        
    def _on_song_selected(self, file_path: str):
        """곡 선택 시 재생"""
        print(f"🎵 재생: {file_path}")
        self._controller.play_track(file_path)
        # 버튼 상태 동기화 (재생 중 → 일시정지 버튼 표시)
        self._player_bar._is_playing = True
        self._player_bar._play_btn.setText("⏸")
        
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
        
        # 곡 리스트에서 현재 곡 선택
        file_path = track.get('file_path', '')
        if file_path:
            self._song_list.select_by_file_path(file_path)
        
        # 버튼 상태 동기화 (재생 중 → 일시정지 버튼 표시)
        self._player_bar._is_playing = True
        self._player_bar._play_btn.setText("⏸")
        
        # 진행바 초기화 및 타이머 시작
        self._playback_position = 0.0
        self._playback_duration = track.get('duration_seconds', 0.0)
        self._player_bar.set_progress(0, int(self._playback_duration))
        self._progress_timer.start()

    def _update_progress(self):
        """진행바 업데이트 (타이머에 의해 호출)"""
        from audio.engine import PlaybackState
        
        if self._controller.state == PlaybackState.PLAYING:
            self._playback_position += 0.1  # 100ms 간격
            if self._playback_position >= self._playback_duration:
                self._playback_position = self._playback_duration
                self._progress_timer.stop()
            self._player_bar.set_progress(
                int(self._playback_position), 
                int(self._playback_duration)
            )
        elif self._controller.state == PlaybackState.STOPPED:
            self._playback_position = 0.0
            self._player_bar.set_progress(0, int(self._playback_duration))
            self._progress_timer.stop()
        
    def _on_play_pause(self):
        """재생/일시정지 (키보드 단축키용)"""
        self._on_toggle_play()

    def _on_seek(self, position_seconds: int):
        """진행바 드래그로 위치 이동"""
        self._playback_position = float(position_seconds)
        # 현재 miniaudio는 seek를 지원하지 않으므로 위치만 업데이트
        print(f"🔍 탐색: {position_seconds}초")

    def _on_toggle_play(self):
        """재생/일시정지 토글"""
        self._controller.toggle_play()
        
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

    def _on_folder_added(self, folder_path: str):
        """폴더 추가 시 스캔 및 UI 업데이트"""
        from PySide6.QtWidgets import QMessageBox
        
        print(f"📁 폴더 스캔 중: {folder_path}")
        
        # 스캔
        scanner = LibraryScanner()
        tracks = scanner.scan_folder(folder_path)
        
        if not tracks:
            QMessageBox.warning(
                self, 
                "스캔 결과", 
                f"폴더에서 지원되는 오디오 파일을 찾을 수 없습니다.\n\n"
                f"폴더: {folder_path}\n"
                f"지원 포맷: FLAC, WAV, M4A, AIFF, DSF, DFF"
            )
            return
        
        # DB 저장
        for track in tracks:
            TrackRepository.insert(track)
        
        print(f"✅ {len(tracks)}개 트랙 추가됨")
        
        # UI 업데이트
        self._refresh_song_list()
        
        # 결과 알림
        QMessageBox.information(
            self,
            "스캔 완료",
            f"✅ {len(tracks)}개 트랙이 추가되었습니다!"
        )

    def _refresh_song_list(self):
        """곡 목록 UI 새로고침"""
        self._song_list.clear_songs()
        tracks = self._controller.load_library()
        
        for i, track in enumerate(tracks):
            duration = track.get('duration_seconds', 0)
            duration_str = f"{int(duration//60)}:{int(duration%60):02d}"
            self._song_list.add_song(
                index=i + 1,
                title=track.get('title', 'Unknown'),
                artist=track.get('artist', 'Unknown'),
                album=track.get('album', 'Unknown'),
                folder_name=track.get('folder_name', ''),
                duration=duration_str,
                file_path=track.get('file_path', '')
            )


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
