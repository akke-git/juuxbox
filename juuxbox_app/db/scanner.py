"""
Library Scanner
===============
음원 폴더 스캔 및 메타데이터 추출
"""

import logging
import hashlib
from pathlib import Path
from typing import Callable, Optional
import mutagen
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.id3 import ID3

logger = logging.getLogger(__name__)

AUDIO_EXTENSIONS = {".flac", ".wav", ".m4a", ".aiff", ".aif", ".dsf", ".dff", ".mp3"}

# 커버 이미지 파일명 (우선순위 순)
COVER_FILENAMES = [
    "cover.jpg", "cover.jpeg", "cover.png",
    "folder.jpg", "folder.jpeg", "folder.png",
    "front.jpg", "front.jpeg", "front.png",
    "album.jpg", "album.jpeg", "album.png",
    "albumart.jpg", "albumart.jpeg", "albumart.png",
    "0.jpg", "0.jpeg", "0.png",
    "1.jpg", "1.jpeg", "1.png",
]

# 커버 이미지 캐시 폴더
COVERS_DIR = Path.home() / ".juuxbox" / "covers"


class LibraryScanner:
    """라이브러리 스캐너"""

    def __init__(self, on_progress: Optional[Callable[[int, int], None]] = None):
        self._on_progress = on_progress
        # 캐시 폴더 생성
        COVERS_DIR.mkdir(parents=True, exist_ok=True)

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

            # 1. 임베디드 앨범아트 추출 시도 (우선)
            cover_path = self._extract_embedded_cover(file_path)
            
            # 2. 없으면 폴더 내 이미지 파일 탐색
            if not cover_path:
                cover_path = self._find_cover_image(file_path.parent)

            return {
                "file_path": str(file_path),
                "title": self._get_tag(audio, "title", file_path.stem),
                "artist": self._get_tag(audio, "artist", "Unknown"),
                "album": self._get_tag(audio, "album", "Unknown"),
                "album_artist": self._get_tag(audio, "albumartist", ""),
                "folder_name": file_path.parent.name,
                "cover_path": cover_path,
                "track_number": self._parse_track_number(self._get_tag(audio, "tracknumber", "")),
                "genre": self._get_tag(audio, "genre", ""),
                "composer": self._get_tag(audio, "composer", ""),
                "conductor": self._get_tag(audio, "conductor", ""),
                "performer": self._get_tag(audio, "performer", ""),
                "duration_seconds": audio.info.length if audio.info else 0,
                "sample_rate": getattr(audio.info, "sample_rate", 0),
                "bit_depth": getattr(audio.info, "bits_per_sample", 16),
                "bitrate": getattr(audio.info, "bitrate", 0),
                "channels": getattr(audio.info, "channels", 2),
                "format": file_path.suffix.upper().replace(".", ""),
            }
        except Exception as e:
            logger.warning(f"메타데이터 추출 실패: {file_path} - {e}")
            return None

    def _extract_embedded_cover(self, file_path: Path) -> Optional[str]:
        """파일 내장 앨범아트 추출"""
        try:
            suffix = file_path.suffix.lower()
            artwork_data = None
            
            # FLAC
            if suffix == ".flac":
                audio = FLAC(str(file_path))
                if audio.pictures:
                    artwork_data = audio.pictures[0].data
                    
            # MP3 (ID3)
            elif suffix == ".mp3":
                audio = MP3(str(file_path), ID3=ID3)
                if audio.tags:
                    for key in audio.tags.keys():
                        if key.startswith("APIC"):
                            artwork_data = audio.tags[key].data
                            break
                            
            # M4A / AAC (MP4)
            elif suffix == ".m4a":
                audio = MP4(str(file_path))
                if "covr" in audio.tags:
                    covers = audio.tags["covr"]
                    if covers:
                        artwork_data = bytes(covers[0])
            
            # 이미지 데이터가 있으면 캐시에 저장
            if artwork_data:
                # 파일 경로 해시로 고유 이름 생성
                file_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:12]
                cache_path = COVERS_DIR / f"{file_hash}.jpg"
                
                if not cache_path.exists():
                    cache_path.write_bytes(artwork_data)
                    logger.debug(f"임베디드 커버 추출: {cache_path}")
                
                return str(cache_path)
                
        except Exception as e:
            logger.debug(f"임베디드 커버 추출 실패: {file_path} - {e}")
        
        return None

    def _find_cover_image(self, folder: Path) -> Optional[str]:
        """폴더 내 커버 이미지 탐색"""
        # 우선순위 순으로 검색
        for filename in COVER_FILENAMES:
            cover_file = folder / filename
            if cover_file.exists():
                logger.debug(f"커버 이미지 발견: {cover_file}")
                return str(cover_file)
        
        # 없으면 폴더 내 첫 번째 이미지 파일 사용
        for ext in [".jpg", ".jpeg", ".png"]:
            images = list(folder.glob(f"*{ext}"))
            if images:
                logger.debug(f"대체 이미지 사용: {images[0]}")
                return str(images[0])
        
        return None

    @staticmethod
    def _get_tag(audio, key: str, default: str) -> str:
        """태그 값 가져오기 (한글 인코딩 수정 포함)"""
        value = audio.get(key)
        if value:
            text = value[0] if isinstance(value, list) else str(value)
            return LibraryScanner._fix_encoding(text)
        return default

    @staticmethod
    def _fix_encoding(text: str) -> str:
        """잘못된 인코딩 수정 (Latin-1로 해석된 CP949/EUC-KR 복원)"""
        if not text:
            return text
        
        # 이미 정상적인 한글이면 그대로 반환
        try:
            # 깨진 문자가 있는지 확인 (Latin-1 범위의 비ASCII)
            has_broken = False
            for c in text:
                if '\x80' <= c <= '\xff':
                    has_broken = True
                    break
            
            if has_broken:
                # Latin-1로 인코딩 후 CP949로 디코딩 시도
                try:
                    fixed = text.encode('latin-1').decode('cp949')
                    return fixed
                except (UnicodeDecodeError, UnicodeEncodeError):
                    # EUC-KR 시도
                    try:
                        fixed = text.encode('latin-1').decode('euc-kr')
                        return fixed
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        pass
        except Exception:
            pass
        
        return text

    @staticmethod
    def _parse_track_number(track_str: str) -> int:
        """트랙 번호 파싱 (예: '5/12' → 5)"""
        if not track_str:
            return 0
        try:
            # "5/12" 형식 처리
            if "/" in track_str:
                return int(track_str.split("/")[0])
            return int(track_str)
        except (ValueError, TypeError):
            return 0
