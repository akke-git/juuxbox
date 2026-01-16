"""
WASAPI Exclusive Mode Controller
================================
Windows WASAPI Exclusive 모드 제어
"""

import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """오디오 장치 정보"""
    name: str
    id: str
    sample_rates: list[int]
    bit_depths: list[int]
    channels: int
    is_exclusive_capable: bool


class WasapiController:
    """
    WASAPI Exclusive 모드 컨트롤러
    
    Windows의 WASAPI를 통해 오디오 믹서를 우회하고
    DAC에 직접 Bit-Perfect 신호를 전송합니다.
    """

    def __init__(self):
        self._current_device: Optional[DeviceInfo] = None
        self._exclusive_mode: bool = False
        logger.info("WasapiController 초기화")

    def get_devices(self) -> list[DeviceInfo]:
        """
        사용 가능한 오디오 장치 목록 가져오기
        
        Returns:
            DeviceInfo 목록
        """
        # TODO: Windows API를 통해 장치 목록 가져오기
        # miniaudio.Devices() 또는 pyaudio 활용
        devices = []
        logger.debug(f"발견된 장치 수: {len(devices)}")
        return devices

    def select_device(self, device_id: str) -> bool:
        """
        출력 장치 선택
        
        Args:
            device_id: 장치 ID
            
        Returns:
            성공 여부
        """
        # TODO: 장치 선택 구현
        logger.info(f"장치 선택: {device_id}")
        return True

    def enable_exclusive_mode(self) -> bool:
        """
        WASAPI Exclusive 모드 활성화
        
        Returns:
            성공 여부 (다른 앱이 장치를 점유 중이면 실패)
        """
        # TODO: Exclusive 모드 활성화
        self._exclusive_mode = True
        logger.info("WASAPI Exclusive 모드 활성화")
        return True

    def disable_exclusive_mode(self):
        """WASAPI Exclusive 모드 비활성화"""
        self._exclusive_mode = False
        logger.info("WASAPI Exclusive 모드 비활성화")

    def is_exclusive_mode(self) -> bool:
        """Exclusive 모드 활성화 여부"""
        return self._exclusive_mode

    def get_current_device(self) -> Optional[DeviceInfo]:
        """현재 선택된 장치 정보"""
        return self._current_device

    def check_sample_rate_support(self, sample_rate: int) -> bool:
        """
        현재 장치가 특정 Sample Rate를 지원하는지 확인
        
        Args:
            sample_rate: 확인할 샘플레이트 (Hz)
            
        Returns:
            지원 여부
        """
        if not self._current_device:
            return False
        return sample_rate in self._current_device.sample_rates
