"""
App Controller
==============
UI와 오디오 엔진을 연결하는 컨트롤러
"""

import logging
from pathlib import Path
from typing import Optional

from audio.engine import AudioEngine, PlaybackState
from audio.gapless import GaplessManager
from db.repository import TrackRepository

logger = logging.getLogger(__name__)


class AppController:
    """
    애플리케이션 컨트롤러
    
    UI 이벤트를 처리하고 오디오 엔진을 제어합니다.
    """

    def __init__(self):
        self._engine = AudioEngine()
        self._gapless = GaplessManager()
        self._current_track: Optional[dict] = None
        self._tracks: list[dict] = []
        
        # 콜백 설정
        self._on_track_change: Optional[callable] = None
        self._on_state_change: Optional[callable] = None
        self._on_position_update: Optional[callable] = None
        
        logger.info("AppController 초기화 완료")

    def load_library(self):
        """라이브러리에서 트랙 로드"""
        self._tracks = TrackRepository.get_all()
        track_paths = [t['file_path'] for t in self._tracks]
        self._gapless.set_queue(track_paths)
        logger.info(f"라이브러리 로드: {len(self._tracks)}개 트랙")
        return self._tracks

    def play_track(self, file_path: str) -> bool:
        """특정 트랙 재생"""
        # 트랙 정보 찾기
        for track in self._tracks:
            if track['file_path'] == file_path:
                self._current_track = track
                break
        
        if self._engine.load(file_path):
            success = self._engine.play()
            if success and self._on_track_change and self._current_track:
                self._on_track_change(self._current_track)
            return success
        return False

    def play_track_by_index(self, index: int) -> bool:
        """인덱스로 트랙 재생"""
        if 0 <= index < len(self._tracks):
            return self.play_track(self._tracks[index]['file_path'])
        return False

    def toggle_play(self):
        """재생/일시정지 토글"""
        if self._engine.state == PlaybackState.PLAYING:
            self._engine.pause()
        elif self._engine.state == PlaybackState.PAUSED:
            self._engine.play()
        elif self._engine.state == PlaybackState.STOPPED and self._tracks:
            # 정지 상태에서 첫 곡 재생
            self.play_track_by_index(0)

    def stop(self):
        """정지"""
        self._engine.stop()

    def next_track(self):
        """다음 트랙"""
        next_path = self._gapless.get_next_track()
        if next_path:
            self.play_track(next_path)

    def previous_track(self):
        """이전 트랙"""
        prev_path = self._gapless.get_previous_track()
        if prev_path:
            self.play_track(prev_path)

    def seek(self, position_seconds: float):
        """특정 위치로 이동"""
        self._engine.seek(position_seconds)

    def set_volume(self, volume: float):
        """볼륨 설정 (0.0 ~ 1.0)"""
        self._engine.volume = volume

    @property
    def current_track(self) -> Optional[dict]:
        """현재 트랙"""
        return self._current_track

    @property
    def state(self) -> PlaybackState:
        """재생 상태"""
        return self._engine.state

    @property
    def audio_info(self):
        """오디오 정보"""
        return self._engine.audio_info

    def set_on_track_change(self, callback: callable):
        """트랙 변경 콜백"""
        self._on_track_change = callback

    def set_on_state_change(self, callback: callable):
        """상태 변경 콜백"""
        self._on_state_change = callback
        self._engine.set_on_state_change(callback)

    def set_on_position_update(self, callback: callable):
        """위치 업데이트 콜백"""
        self._on_position_update = callback
        self._engine.set_on_position_update(callback)

    def cleanup(self):
        """정리"""
        self._engine.cleanup()
        logger.info("AppController 정리 완료")
