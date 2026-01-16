"""
Library Scanner
===============
음원 폴더 스캔 및 메타데이터 추출
"""

import logging
from pathlib import Path
from typing import Callable, Optional
import mutagen

logger = logging.getLogger(__name__)

AUDIO_EXTENSIONS = {".flac", ".wav", ".m4a", ".aiff", ".aif", ".dsf", ".dff"}


class LibraryScanner:
    """라이브러리 스캐너"""

    def __init__(self, on_progress: Optional[Callable[[int, int], None]] = None):
        self._on_progress = on_progress

    def scan_folder(self, folder_path: str) -> list[dict]:
        """폴더 스캔"""
        folder = Path(folder_path)
        if not folder.exists():
            logger.error(f"폴더 없음: {folder_path}")
            return []

        audio_files = [f for f in folder.rglob("*") if f.suffix.lower() in AUDIO_EXTENSIONS]
        total = len(audio_files)
        logger.info(f"스캔 시작: {total}개 파일")

        tracks = []
        for i, file_path in enumerate(audio_files):
            track = self._extract_metadata(file_path)
            if track:
                tracks.append(track)
            if self._on_progress:
                self._on_progress(i + 1, total)

        logger.info(f"스캔 완료: {len(tracks)}개 트랙")
        return tracks

    def _extract_metadata(self, file_path: Path) -> Optional[dict]:
        """메타데이터 추출"""
        try:
            audio = mutagen.File(str(file_path), easy=True)
            if audio is None:
                return None

            return {
                "file_path": str(file_path),
                "title": self._get_tag(audio, "title", file_path.stem),
                "artist": self._get_tag(audio, "artist", "Unknown"),
                "album": self._get_tag(audio, "album", "Unknown"),
                "folder_name": file_path.parent.name,  # 폴더명
                "duration_seconds": audio.info.length if audio.info else 0,
                "sample_rate": getattr(audio.info, "sample_rate", 0),
                "bit_depth": getattr(audio.info, "bits_per_sample", 16),
                "format": file_path.suffix.upper().replace(".", ""),
            }
        except Exception as e:
            logger.warning(f"메타데이터 추출 실패: {file_path} - {e}")
            return None

    @staticmethod
    def _get_tag(audio, key: str, default: str) -> str:
        """태그 값 가져오기"""
        value = audio.get(key)
        if value:
            return value[0] if isinstance(value, list) else str(value)
        return default
