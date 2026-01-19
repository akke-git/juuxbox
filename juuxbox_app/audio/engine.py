"""
Audio Engine
============
miniaudio를 활용한 오디오 재생 엔진
"""

import logging
import threading
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
    오디오 재생 엔진
    
    Features:
    - miniaudio 기반 재생
    - 실시간 오디오 정보 피드백
    """

    def __init__(self, device_name: Optional[str] = None):
        self._device_name = device_name
        self._state = PlaybackState.STOPPED
        self._current_file: Optional[str] = None
        self._audio_info = AudioInfo()
        self._volume: float = 1.0
        
        # 재생 관련
        self._device: Optional[miniaudio.PlaybackDevice] = None
        self._stream = None
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        
        # 콜백
        self._on_state_change: Optional[Callable[[PlaybackState], None]] = None
        self._on_position_update: Optional[Callable[[float], None]] = None
        self._on_track_end: Optional[Callable[[], None]] = None
        
        logger.info(f"AudioEngine 초기화 완료 (장치: {device_name or '기본'})")

    @property
    def state(self) -> PlaybackState:
        return self._state

    @property
    def audio_info(self) -> AudioInfo:
        return self._audio_info

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = max(0.0, min(1.0, value))
        logger.debug(f"볼륨 설정: {self._volume:.2f}")

    def load(self, file_path: str) -> bool:
        """오디오 파일 로드"""
        try:
            # 기존 재생 중지
            self.stop()
            
            # mutagen으로 파일 정보 가져오기 (유니코드 경로 지원)
            import mutagen
            audio = mutagen.File(file_path)
            if audio is None:
                raise ValueError("지원하지 않는 포맷")
            
            sample_rate = getattr(audio.info, 'sample_rate', 44100)
            channels = getattr(audio.info, 'channels', 2)
            duration = audio.info.length if audio.info else 0
            bit_depth = getattr(audio.info, 'bits_per_sample', 16)
            
            self._audio_info = AudioInfo(
                sample_rate=sample_rate,
                bit_depth=bit_depth or 16,
                channels=channels,
                duration_seconds=duration,
                position_seconds=0.0
            )
            
            # 파일을 bytes로 읽기 (유니코드 경로 지원)
            with open(file_path, 'rb') as f:
                self._file_bytes = f.read()
            
            self._current_file = file_path
            logger.info(f"파일 로드: {file_path} ({sample_rate}Hz, {channels}ch)")
            return True
            
        except Exception as e:
            logger.error(f"파일 로드 실패: {file_path} - {e}")
            import traceback
            traceback.print_exc()
            return False

    def play(self) -> bool:
        """재생 시작"""
        if not self._current_file or not hasattr(self, '_file_bytes'):
            logger.warning("재생할 파일이 없습니다")
            return False
        
        try:
            # 이미 재생 중이면 중지
            self.stop()
            self._stop_flag.clear()
            
            # bytes로 스트림 생성 (원본 파일 데이터 사용)
            self._stream = miniaudio.stream_memory(
                self._file_bytes,
                output_format=miniaudio.SampleFormat.SIGNED16
            )
            
            # 재생 장치 생성 및 시작
            self._device = miniaudio.PlaybackDevice(
                output_format=miniaudio.SampleFormat.SIGNED16,
                nchannels=self._audio_info.channels,
                sample_rate=self._audio_info.sample_rate
            )
            self._device.start(self._stream)
            
            self._state = PlaybackState.PLAYING
            logger.info(f"재생 시작: {self._current_file}")
            
            if self._on_state_change:
                self._on_state_change(self._state)
            
            return True
            
        except Exception as e:
            logger.error(f"재생 실패: {e}")
            import traceback
            traceback.print_exc()
            self._state = PlaybackState.STOPPED
            return False

    def pause(self):
        """일시정지"""
        if self._device and self._state == PlaybackState.PLAYING:
            self._device.stop()
            self._state = PlaybackState.PAUSED
            logger.info("일시정지")
            
            if self._on_state_change:
                self._on_state_change(self._state)

    def resume(self):
        """재개"""
        if self._device and self._state == PlaybackState.PAUSED:
            self._device.start(self._stream)
            self._state = PlaybackState.PLAYING
            logger.info("재생 재개")
            
            if self._on_state_change:
                self._on_state_change(self._state)

    def stop(self):
        """정지"""
        self._stop_flag.set()
        
        if self._device:
            try:
                self._device.stop()
                self._device.close()
            except:
                pass
            self._device = None
        
        self._stream = None
        self._state = PlaybackState.STOPPED
        logger.info("정지")
        
        if self._on_state_change:
            self._on_state_change(self._state)

    def seek(self, position_seconds: float):
        """특정 위치로 이동 (현재 미지원)"""
        logger.warning("탐색 기능은 아직 지원되지 않습니다")

    def set_on_state_change(self, callback: Callable[[PlaybackState], None]):
        self._on_state_change = callback

    def set_on_position_update(self, callback: Callable[[float], None]):
        self._on_position_update = callback

    def set_on_track_end(self, callback: Callable[[], None]):
        self._on_track_end = callback

    def cleanup(self):
        """리소스 정리"""
        self.stop()
        logger.info("AudioEngine 정리 완료")
