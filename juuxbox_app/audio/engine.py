"""
Audio Engine
============
miniaudio를 활용한 오디오 재생 엔진
"""

import logging
import threading
import time
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
        
        # 위치 추적
        self._position_thread: Optional[threading.Thread] = None
        self._position_running = False
        self._playback_start_time: float = 0.0
        self._paused_position: float = 0.0
        
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
            self._audio_info.position_seconds = 0.0
            self._paused_position = 0.0
            self._playback_start_time = time.time()
            
            # 위치 추적 스레드 시작
            self._start_position_tracking()
            
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
            # 현재 위치 저장
            self._paused_position = self._audio_info.position_seconds
            self._stop_position_tracking()
            
            self._device.stop()
            self._state = PlaybackState.PAUSED
            logger.info(f"일시정지 (위치: {self._paused_position:.1f}초)")
            
            if self._on_state_change:
                self._on_state_change(self._state)

    def resume(self):
        """재개"""
        if self._device and self._state == PlaybackState.PAUSED:
            self._device.start(self._stream)
            self._state = PlaybackState.PLAYING
            
            # 위치 추적 재개
            self._playback_start_time = time.time()
            self._start_position_tracking()
            
            logger.info(f"재생 재개 (위치: {self._paused_position:.1f}초)")
            
            if self._on_state_change:
                self._on_state_change(self._state)

    def stop(self):
        """정지"""
        self._stop_flag.set()
        self._stop_position_tracking()
        
        if self._device:
            try:
                self._device.stop()
                self._device.close()
            except:
                pass
            self._device = None
        
        self._stream = None
        self._state = PlaybackState.STOPPED
        self._audio_info.position_seconds = 0.0
        self._paused_position = 0.0
        logger.info("정지")
        
        if self._on_state_change:
            self._on_state_change(self._state)

    def seek(self, position_seconds: float):
        """특정 위치로 이동 (UI 표시용 - 실제 오디오는 미지원)"""
        # miniaudio 스트리밍에서는 실제 탐색이 어렵지만
        # UI 표시용으로 위치를 업데이트
        if 0 <= position_seconds <= self._audio_info.duration_seconds:
            self._audio_info.position_seconds = position_seconds
            self._paused_position = position_seconds
            if self._state == PlaybackState.PLAYING:
                self._playback_start_time = time.time()
            logger.info(f"탐색 위치 업데이트: {position_seconds:.1f}초 (UI만 변경, 실제 오디오 미지원)")

    def set_on_state_change(self, callback: Callable[[PlaybackState], None]):
        self._on_state_change = callback

    def set_on_position_update(self, callback: Callable[[float], None]):
        self._on_position_update = callback

    def set_on_track_end(self, callback: Callable[[], None]):
        self._on_track_end = callback

    def _start_position_tracking(self):
        """재생 위치 추적 스레드 시작"""
        self._position_running = True
        
        def track_position():
            while self._position_running and self._state == PlaybackState.PLAYING:
                elapsed = time.time() - self._playback_start_time
                self._audio_info.position_seconds = self._paused_position + elapsed
                
                # 재생 완료 체크
                if self._audio_info.position_seconds >= self._audio_info.duration_seconds:
                    self._audio_info.position_seconds = self._audio_info.duration_seconds
                    self._position_running = False
                    # 트랙 종료 콜백
                    if self._on_track_end:
                        self._on_track_end()
                    break
                
                time.sleep(0.1)  # 100ms 간격
        
        self._position_thread = threading.Thread(target=track_position, daemon=True)
        self._position_thread.start()
    
    def _stop_position_tracking(self):
        """재생 위치 추적 중지"""
        self._position_running = False
        if self._position_thread and self._position_thread.is_alive():
            self._position_thread.join(timeout=0.5)
        self._position_thread = None

    def cleanup(self):
        """리소스 정리"""
        self.stop()
        logger.info("AudioEngine 정리 완료")
