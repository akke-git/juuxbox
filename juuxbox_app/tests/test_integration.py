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
                file_path=track.get('file_path', ''),
                audio_format=track.get('format'),
                cover_path=track.get('cover_path')
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
        self._sidebar.add_files_clicked.connect(self._on_files_added)

        # 곡 목록: 삭제
        self._song_list.song_delete_requested.connect(self._on_song_delete)
        self._song_list.songs_delete_requested.connect(self._on_songs_delete)
        self._song_list.all_songs_delete_requested.connect(self._on_all_songs_delete)

        # 플레이바 클릭 → 상세 뷰 전환
        self._player_bar.clicked.connect(self._show_detail_view)

        # 상세 뷰 시그널
        self._detail_view.back_clicked.connect(self.show_main_view)
        self._detail_view.play_clicked.connect(self._on_toggle_play)
        self._detail_view.pause_clicked.connect(self._on_toggle_play)
        self._detail_view.stop_clicked.connect(self._controller.stop)
        self._detail_view.next_clicked.connect(self._controller.next_track)
        self._detail_view.prev_clicked.connect(self._controller.previous_track)
        self._detail_view.seek_changed.connect(self._on_seek)
        
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
            artist=track.get('artist', 'Unknown'),
            album_art_path=track.get('cover_path')
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

        # 상세 뷰에 트랙 정보 설정
        self._current_track = track
        self._detail_view.set_track_info(
            title=track.get('title', 'Unknown'),
            artist=track.get('artist', 'Unknown'),
            album=track.get('album', ''),
            folder=track.get('folder_name', ''),
            audio_format=track.get('format', ''),
            cover_path=track.get('cover_path'),
            album_artist=track.get('album_artist', ''),
            track_number=track.get('track_number', 0),
            genre=track.get('genre', ''),
            composer=track.get('composer', ''),
            conductor=track.get('conductor', ''),
            performer=track.get('performer', ''),
            duration_seconds=track.get('duration_seconds', 0),
            sample_rate=track.get('sample_rate', 0),
            bit_depth=track.get('bit_depth', 0),
            bitrate=track.get('bitrate', 0),
            channels=track.get('channels', 0),
        )
        self._detail_view.set_playing_state(True)

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
            # 상세뷰 프로그레스바도 업데이트
            self._detail_view.set_progress(
                int(self._playback_position),
                int(self._playback_duration)
            )
        elif self._controller.state == PlaybackState.STOPPED:
            self._playback_position = 0.0
            self._player_bar.set_progress(0, int(self._playback_duration))
            self._detail_view.set_progress(0, int(self._playback_duration))
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
        # 상세뷰 버튼 상태 동기화
        is_playing = self._player_bar._is_playing
        self._detail_view.set_playing_state(is_playing)

    def _show_detail_view(self):
        """상세 뷰로 전환"""
        # 현재 트랙 정보가 있으면 상세뷰에 표시
        if hasattr(self, '_current_track') and self._current_track:
            track = self._current_track
            self._detail_view.set_track_info(
                title=track.get('title', 'Unknown'),
                artist=track.get('artist', 'Unknown'),
                album=track.get('album', ''),
                folder=track.get('folder_name', ''),
                audio_format=track.get('format', ''),
                cover_path=track.get('cover_path'),
                album_artist=track.get('album_artist', ''),
                track_number=track.get('track_number', 0),
                genre=track.get('genre', ''),
                composer=track.get('composer', ''),
                conductor=track.get('conductor', ''),
                performer=track.get('performer', ''),
                duration_seconds=track.get('duration_seconds', 0),
                sample_rate=track.get('sample_rate', 0),
                bit_depth=track.get('bit_depth', 0),
                bitrate=track.get('bitrate', 0),
                channels=track.get('channels', 0),
            )
            self._detail_view.set_playing_state(self._player_bar._is_playing)
        self.show_detail_view()
        
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
        
        # 중복 필터링 (이미 DB에 있는 파일 스킵)
        new_tracks = [t for t in tracks if not TrackRepository.exists_by_file_path(t["file_path"])]
        skipped_count = len(tracks) - len(new_tracks)
        
        if not new_tracks:
            QMessageBox.information(
                self,
                "스캔 결과",
                f"모든 파일이 이미 라이브러리에 있습니다.\n(스캔됨: {len(tracks)}, 스킵: {skipped_count})"
            )
            return
        
        # DB 저장
        for track in new_tracks:
            TrackRepository.insert(track)
        
        print(f"✅ {len(new_tracks)}개 트랙 추가됨 (스킵: {skipped_count})")
        
        # UI 업데이트
        self._refresh_song_list()
        
        # 결과 알림
        msg = f"✅ {len(new_tracks)}개 트랙이 추가되었습니다!"
        if skipped_count > 0:
            msg += f"\n(스킵: {skipped_count}개 - 이미 존재)"
        QMessageBox.information(self, "스캔 완료", msg)

    def _on_files_added(self, file_paths: list):
        """개별 파일들 추가"""
        from pathlib import Path
        from PySide6.QtWidgets import QMessageBox
        
        scanner = LibraryScanner()
        added_count = 0
        skipped_count = 0
        
        for file_path in file_paths:
            # 중복 체크
            if TrackRepository.exists_by_file_path(file_path):
                skipped_count += 1
                continue
            
            track = scanner._extract_metadata(Path(file_path))
            if track:
                TrackRepository.insert(track)
                added_count += 1
        
        if added_count > 0:
            print(f"✅ {added_count}개 파일 추가됨 (스킵: {skipped_count})")
            self._refresh_song_list()
            
            msg = f"✅ {added_count}개 파일이 추가되었습니다!"
            if skipped_count > 0:
                msg += f"\n(스킵: {skipped_count}개 - 이미 존재)"
            QMessageBox.information(self, "파일 추가 완료", msg)
        elif skipped_count > 0:
            QMessageBox.information(
                self,
                "파일 추가",
                f"모든 파일이 이미 라이브러리에 있습니다.\n(스킵: {skipped_count}개)"
            )
        else:
            QMessageBox.warning(
                self,
                "파일 추가 실패",
                "선택한 파일에서 오디오 정보를 추출할 수 없습니다."
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
                file_path=track.get('file_path', ''),
                audio_format=track.get('format'),
                cover_path=track.get('cover_path')
            )

    def _on_song_delete(self, file_path: str):
        """곡 삭제"""
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "곡 삭제",
            "선택한 곡을 라이브러리에서 삭제하시겠습니까?\n(파일은 삭제되지 않습니다)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            TrackRepository.delete_by_file_path(file_path)
            print(f"🗑️ 삭제됨: {file_path}")
            self._refresh_song_list()

    def _on_songs_delete(self, file_paths: list):
        """선택된 곡들 삭제"""
        from PySide6.QtWidgets import QMessageBox

        count = len(file_paths)
        reply = QMessageBox.question(
            self,
            "선택 삭제",
            f"선택한 {count}곡을 라이브러리에서 삭제하시겠습니까?\n(파일은 삭제되지 않습니다)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            deleted = TrackRepository.delete_by_file_paths(file_paths)
            print(f"🗑️ 선택 삭제: {deleted}개")
            self._refresh_song_list()

    def _on_all_songs_delete(self):
        """전체 곡 삭제"""
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "전체 삭제",
            "모든 곡을 라이브러리에서 삭제하시겠습니까?\n(파일은 삭제되지 않습니다)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            count = TrackRepository.delete_all()
            print(f"🗑️ 전체 삭제: {count}개")
            self._refresh_song_list()


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
