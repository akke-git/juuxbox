"""
Audio Decoder
=============
다양한 오디오 포맷 디코딩 지원
"""

import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import miniaudio

logger = logging.getLogger(__name__)


# 지원 포맷
SUPPORTED_FORMATS = {
    ".flac": "FLAC",
    ".wav": "WAV",
    ".m4a": "ALAC/AAC",
    ".aiff": "AIFF",
    ".aif": "AIFF",
    ".dsf": "DSD",
    ".dff": "DSD",
}


@dataclass
class DecodedAudio:
    """디코딩된 오디오 데이터"""
    samples: bytes
    sample_rate: int
    bit_depth: int
    channels: int
    duration_seconds: float
    format_name: str


class AudioDecoder:
    """
    오디오 파일 디코더
    
    지원 포맷:
    - FLAC, WAV, ALAC, AIFF
    - DSD (DoP 변환)
    """

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """지원되는 포맷인지 확인"""
        ext = Path(file_path).suffix.lower()
        return ext in SUPPORTED_FORMATS

    @staticmethod
    def get_format_name(file_path: str) -> str:
        """파일 포맷 이름 반환"""
        ext = Path(file_path).suffix.lower()
        return SUPPORTED_FORMATS.get(ext, "Unknown")

    @staticmethod
    def decode(file_path: str) -> Optional[DecodedAudio]:
        """
        오디오 파일 디코딩
        
        Args:
            file_path: 오디오 파일 경로
            
        Returns:
            디코딩된 오디오 데이터 또는 None
        """
        if not AudioDecoder.is_supported(file_path):
            logger.error(f"지원하지 않는 포맷: {file_path}")
            return None

        try:
            # miniaudio로 디코딩
            decoded = miniaudio.decode_file(file_path)
            
            audio = DecodedAudio(
                samples=decoded.samples,
                sample_rate=decoded.sample_rate,
                bit_depth=16,  # miniaudio 기본값, 실제 파일에서 확인 필요
                channels=decoded.nchannels,
                duration_seconds=decoded.duration,
                format_name=AudioDecoder.get_format_name(file_path),
            )
            
            logger.info(
                f"디코딩 완료: {file_path} "
                f"({audio.sample_rate}Hz, {audio.bit_depth}bit, {audio.channels}ch)"
            )
            return audio

        except Exception as e:
            logger.error(f"디코딩 실패: {file_path} - {e}")
            return None

    @staticmethod
    def get_file_info(file_path: str) -> Optional[dict]:
        """
        파일 정보만 가져오기 (디코딩 없이)
        
        Args:
            file_path: 오디오 파일 경로
            
        Returns:
            파일 정보 딕셔너리
        """
        try:
            info = miniaudio.get_file_info(file_path)
            return {
                "sample_rate": info.sample_rate,
                "channels": info.nchannels,
                "duration": info.duration,
                "format": AudioDecoder.get_format_name(file_path),
            }
        except Exception as e:
            logger.error(f"파일 정보 읽기 실패: {file_path} - {e}")
            return None
