"""
Audio Engine
============
miniaudio를 활용한 WASAPI Exclusive 모드 오디오 재생 엔진
"""

import logging
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

import miniaudio

logger = logging.getLogger(__name__)


class PlaybackState(Enum):
    """재생 상태"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


@dataclass
class AudioInfo:
    """현재 재생 중인 오디오 정보"""
    sample_rate: int = 0
    bit_depth: int = 0
    channels: int = 0
    duration_seconds: float = 0.0
    position_seconds: float = 0.0


class AudioEngine:
    """
    WASAPI Exclusive 모드 오디오 엔진
    
    Features:
    - Bit-Perfect 출력 (WASAPI Exclusive)
    - Gapless 재생 지원
    - 실시간 오디오 정보 피드백
    """

    def __init__(self, device_name: Optional[str] = None):
        """
        Args:
            device_name: 출력 장치 이름 (None이면 기본 장치)
        """
        self._device_name = device_name
        self._state = PlaybackState.STOPPED
        self._current_file: Optional[str] = None
        self._audio_info = AudioInfo()
        self._volume: float = 1.0
        
        # 콜백
        self._on_state_change: Optional[Callable[[PlaybackState], None]] = None
        self._on_position_update: Optional[Callable[[float], None]] = None
        self._on_track_end: Optional[Callable[[], None]] = None
        
        # miniaudio 장치 (나중에 초기화)
        self._device: Optional[miniaudio.PlaybackDevice] = None
        
        logger.info(f"AudioEngine 초기화 완료 (장치: {device_name or '기본'})")

    @property
    def state(self) -> PlaybackState:
        """현재 재생 상태"""
        return self._state

    @property
    def audio_info(self) -> AudioInfo:
        """현재 오디오 정보"""
        return self._audio_info

    @property
    def volume(self) -> float:
        """볼륨 (0.0 ~ 1.0)"""
        return self._volume

    @volume.setter
    def volume(self, value: float):
        """볼륨 설정"""
        self._volume = max(0.0, min(1.0, value))
        logger.debug(f"볼륨 설정: {self._volume:.2f}")

    def get_available_devices(self) -> list[str]:
        """사용 가능한 오디오 장치 목록"""
        # TODO: miniaudio에서 장치 목록 가져오기
        devices = []
        logger.debug(f"사용 가능한 장치: {devices}")
        return devices

    def load(self, file_path: str) -> bool:
        """
        오디오 파일 로드
        
        Args:
            file_path: 오디오 파일 경로
            
        Returns:
            성공 여부
        """
        # TODO: 파일 로드 구현
        logger.info(f"파일 로드: {file_path}")
        self._current_file = file_path
        return True

    def play(self) -> bool:
        """재생 시작"""
        # TODO: 재생 구현
        self._state = PlaybackState.PLAYING
        logger.info("재생 시작")
        return True

    def pause(self):
        """일시정지"""
        # TODO: 일시정지 구현
        self._state = PlaybackState.PAUSED
        logger.info("일시정지")

    def stop(self):
        """정지"""
        # TODO: 정지 구현
        self._state = PlaybackState.STOPPED
        logger.info("정지")

    def seek(self, position_seconds: float):
        """
        특정 위치로 이동
        
        Args:
            position_seconds: 이동할 위치 (초)
        """
        # TODO: 탐색 구현
        logger.info(f"탐색: {position_seconds:.1f}초")

    def set_on_state_change(self, callback: Callable[[PlaybackState], None]):
        """상태 변경 콜백 설정"""
        self._on_state_change = callback

    def set_on_position_update(self, callback: Callable[[float], None]):
        """위치 업데이트 콜백 설정"""
        self._on_position_update = callback

    def set_on_track_end(self, callback: Callable[[], None]):
        """트랙 종료 콜백 설정"""
        self._on_track_end = callback

    def cleanup(self):
        """리소스 정리"""
        self.stop()
        if self._device:
            self._device.close()
        logger.info("AudioEngine 정리 완료")
