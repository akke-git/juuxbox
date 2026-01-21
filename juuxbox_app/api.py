"""
JuuxBox API
===========
pywebview JavaScript-Python 브릿지 API
웹 UI에서 호출하는 Python 백엔드 함수들
"""

import base64
import logging
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any

from db.models import create_tables
from db.repository import TrackRepository
from db.scanner import LibraryScanner
from audio.engine import AudioEngine, PlaybackState
from utils.config import load_config
from utils.youtube_search import search_youtube, build_search_query, YOUTUBE_AVAILABLE

logger = logging.getLogger(__name__)


class JuuxBoxAPI:
    """pywebview에 노출되는 API 클래스"""

    def __init__(self):
        self._engine: Optional[AudioEngine] = None
        self._config = load_config()
        self._current_track: Optional[Dict] = None
        self._playlist: List[Dict] = []
        self._playlist_index: int = -1
        self._window = None  # pywebview window reference
        self._progress_thread: Optional[threading.Thread] = None
        self._running = True

        # DB 초기화
        create_tables()

        # 오디오 엔진 초기화
        self._init_audio_engine()

    def _init_audio_engine(self):
        """오디오 엔진 초기화"""
        try:
            device_name = self._config.get('audio', {}).get('device_name')
            self._engine = AudioEngine(device_name=device_name)
            logger.info("오디오 엔진 초기화 완료")
        except Exception as e:
            logger.error(f"오디오 엔진 초기화 실패: {e}")
            self._engine = None

    def set_window(self, window):
        """pywebview 윈도우 참조 설정"""
        self._window = window
        self._start_progress_thread()

    def _start_progress_thread(self):
        """재생 진행률 업데이트 스레드"""
        def update_progress():
            while self._running:
                if self._engine and self._engine.state == PlaybackState.PLAYING:
                    current = self._engine.audio_info.position_seconds
                    total = self._engine.audio_info.duration_seconds
                    if self._window and total > 0:
                        try:
                            self._window.evaluate_js(
                                f"window.onProgressUpdate && window.onProgressUpdate({current}, {total})"
                            )
                        except:
                            pass
                threading.Event().wait(0.1)  # 100ms 간격 (부드러운 업데이트)

        self._progress_thread = threading.Thread(target=update_progress, daemon=True)
        self._progress_thread.start()

    # ===== 라이브러리 관련 =====

    def get_all_tracks(self) -> List[Dict]:
        """모든 트랙 목록 반환"""
        try:
            tracks = TrackRepository.get_all()
            logger.info(f"트랙 조회: {len(tracks)}개")
            return [self._track_to_dict(t) for t in tracks]
        except Exception as e:
            logger.error(f"트랙 조회 실패: {e}")
            return []

    def get_albums(self) -> List[Dict]:
        """앨범 목록 반환 (그리드 뷰용)"""
        try:
            albums = TrackRepository.get_albums()
            logger.info(f"앨범 조회: {len(albums)}개")
            return albums
        except Exception as e:
            logger.error(f"앨범 조회 실패: {e}")
            return []

    def get_artists(self) -> List[Dict]:
        """아티스트 목록 반환 (그리드 뷰용)"""
        try:
            artists = TrackRepository.get_artists()
            logger.info(f"아티스트 조회: {len(artists)}개")
            return artists
        except Exception as e:
            logger.error(f"아티스트 조회 실패: {e}")
            return []

    def get_folders(self) -> List[Dict]:
        """폴더 목록 반환 (그리드 뷰용)"""
        try:
            folders = TrackRepository.get_folders()
            logger.info(f"폴더 조회: {len(folders)}개")
            return folders
        except Exception as e:
            logger.error(f"폴더 조회 실패: {e}")
            return []

    def get_tracks_by_album(self, album: str) -> List[Dict]:
        """앨범별 트랙 목록 반환"""
        try:
            tracks = TrackRepository.get_tracks_by_album(album)
            logger.info(f"앨범 '{album}' 트랙 조회: {len(tracks)}개")
            return [self._track_to_dict(t) for t in tracks]
        except Exception as e:
            logger.error(f"앨범 트랙 조회 실패: {e}")
            return []

    def get_tracks_by_artist(self, artist: str) -> List[Dict]:
        """아티스트별 트랙 목록 반환"""
        try:
            tracks = TrackRepository.get_tracks_by_artist(artist)
            logger.info(f"아티스트 '{artist}' 트랙 조회: {len(tracks)}개")
            return [self._track_to_dict(t) for t in tracks]
        except Exception as e:
            logger.error(f"아티스트 트랙 조회 실패: {e}")
            return []

    def get_tracks_by_folder(self, folder_name: str) -> List[Dict]:
        """폴더별 트랙 목록 반환"""
        try:
            tracks = TrackRepository.get_tracks_by_folder(folder_name)
            logger.info(f"폴더 '{folder_name}' 트랙 조회: {len(tracks)}개")
            return [self._track_to_dict(t) for t in tracks]
        except Exception as e:
            logger.error(f"폴더 트랙 조회 실패: {e}")
            return []

    def scan_folder(self, folder_path: str) -> Dict[str, Any]:
        """폴더 스캔"""
        try:
            scanner = LibraryScanner()
            tracks = scanner.scan_folder(folder_path)

            for track in tracks:
                TrackRepository.insert(track)

            return {"success": True, "count": len(tracks)}
        except Exception as e:
            logger.error(f"폴더 스캔 실패: {e}")
            return {"success": False, "error": str(e)}

    def delete_tracks(self, file_paths: List[str]) -> Dict[str, Any]:
        """트랙 삭제"""
        try:
            for path in file_paths:
                TrackRepository.delete_by_file_path(path)
            return {"success": True, "count": len(file_paths)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_all_tracks(self) -> Dict[str, Any]:
        """모든 트랙 삭제"""
        try:
            TrackRepository.delete_all()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_cover_image(self, cover_path: str) -> Dict[str, Any]:
        """커버 이미지를 base64로 반환"""
        if not cover_path:
            return {"success": False, "error": "경로 없음"}

        try:
            path = Path(cover_path)
            if not path.exists():
                return {"success": False, "error": "파일 없음"}

            # MIME 타입 결정
            suffix = path.suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(suffix, 'image/jpeg')

            # 이미지 읽어서 base64 인코딩
            with open(path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            return {
                "success": True,
                "data_uri": f"data:{mime_type};base64,{image_data}"
            }
        except Exception as e:
            logger.error(f"커버 이미지 로드 실패: {e}")
            return {"success": False, "error": str(e)}

    # ===== 재생 관련 =====

    def play(self, file_path: str) -> Dict[str, Any]:
        """음악 재생"""
        if not self._engine:
            return {"success": False, "error": "오디오 엔진 없음"}

        try:
            self._engine.load(file_path)
            self._engine.play()

            # 현재 트랙 정보 저장
            track = TrackRepository.get_by_file_path(file_path)
            if track:
                self._current_track = self._track_to_dict(track)

            logger.info(f"재생: {file_path}")
            return {"success": True, "track": self._current_track}
        except Exception as e:
            logger.error(f"재생 실패: {e}")
            return {"success": False, "error": str(e)}

    def pause(self) -> Dict[str, Any]:
        """일시정지"""
        if self._engine:
            self._engine.pause()
            return {"success": True}
        return {"success": False}

    def resume(self) -> Dict[str, Any]:
        """재생 재개"""
        if self._engine:
            self._engine.play()
            return {"success": True}
        return {"success": False}

    def stop(self) -> Dict[str, Any]:
        """정지"""
        if self._engine:
            self._engine.stop()
            return {"success": True}
        return {"success": False}

    def seek(self, position: float) -> Dict[str, Any]:
        """탐색 (초 단위)"""
        if self._engine:
            self._engine.seek(position)
            return {"success": True}
        return {"success": False}

    def set_volume(self, volume: float) -> Dict[str, Any]:
        """볼륨 설정 (0.0 ~ 1.0)"""
        if self._engine:
            self._engine.set_volume(volume)
            return {"success": True}
        return {"success": False}

    def get_playback_state(self) -> Dict[str, Any]:
        """재생 상태 반환"""
        if not self._engine:
            return {"playing": False, "position": 0, "duration": 0}

        return {
            "playing": self._engine.state == PlaybackState.PLAYING,
            "position": self._engine.audio_info.position_seconds,
            "duration": self._engine.audio_info.duration_seconds,
            "track": self._current_track
        }

    # ===== 오디오 설정 =====

    def get_audio_devices(self) -> Dict[str, Any]:
        """사용 가능한 오디오 장치 목록 반환"""
        try:
            devices = miniaudio.Devices()
            playback_devices = devices.get_playbacks()
            
            device_list = []
            for dev in playback_devices:
                device_list.append({
                    "id": dev["id"],
                    "name": dev["name"],
                    "is_default": dev.get("isDefault", False)
                })
            
            return {
                "success": True,
                "devices": device_list,
                "current_device": self._config.get('audio', {}).get('device_name', 'System Default')
            }
        except Exception as e:
            logger.error(f"오디오 장치 목록 조회 실패: {e}")
            return {"success": False, "devices": [], "error": str(e)}

    def get_audio_settings(self) -> Dict[str, Any]:
        """현재 오디오 설정 반환"""
        return {
            "output_mode": "miniaudio (shared)",  # miniaudio는 기본적으로 shared mode
            "device_name": self._config.get('audio', {}).get('device_name', 'System Default'),
            "sample_rate": self._engine.audio_info.sample_rate if self._engine else 0,
            "bit_depth": self._engine.audio_info.bit_depth if self._engine else 0,
            "channels": self._engine.audio_info.channels if self._engine else 0
        }

    def set_audio_device(self, device_name: str) -> Dict[str, Any]:
        """오디오 출력 장치 설정"""
        try:
            # 설정 저장
            if 'audio' not in self._config:
                self._config['audio'] = {}
            self._config['audio']['device_name'] = device_name
            
            # 엔진 재초기화 필요 (재생 중이면 중지)
            if self._engine:
                self._engine.stop()
                self._engine.cleanup()
            
            self._engine = AudioEngine(device_name=device_name if device_name != 'System Default' else None)
            logger.info(f"오디오 장치 변경: {device_name}")
            
            return {"success": True, "device_name": device_name}
        except Exception as e:
            logger.error(f"오디오 장치 설정 실패: {e}")
            return {"success": False, "error": str(e)}

    # ===== 플레이리스트 =====

    def set_playlist(self, tracks: List[Dict], start_index: int = 0) -> Dict[str, Any]:
        """플레이리스트 설정"""
        self._playlist = tracks
        self._playlist_index = start_index
        return {"success": True}

    def play_next(self) -> Dict[str, Any]:
        """다음 곡 재생"""
        if not self._playlist:
            return {"success": False, "error": "플레이리스트 없음"}

        self._playlist_index = (self._playlist_index + 1) % len(self._playlist)
        track = self._playlist[self._playlist_index]
        return self.play(track['file_path'])

    def play_previous(self) -> Dict[str, Any]:
        """이전 곡 재생"""
        if not self._playlist:
            return {"success": False, "error": "플레이리스트 없음"}

        self._playlist_index = (self._playlist_index - 1) % len(self._playlist)
        track = self._playlist[self._playlist_index]
        return self.play(track['file_path'])

    # ===== 유틸리티 =====

    def select_folder(self) -> Optional[str]:
        """폴더 선택 다이얼로그 (pywebview 내장)"""
        if self._window:
            result = self._window.create_file_dialog(
                dialog_type=20,  # FOLDER_DIALOG
                allow_multiple=False
            )
            if result and len(result) > 0:
                return result[0]
        return None

    def _track_to_dict(self, track: Dict) -> Dict[str, Any]:
        """Track 딕셔너리를 API 응답 형식으로 변환"""
        return {
            "id": track.get('id'),
            "title": track.get('title') or "Unknown",
            "artist": track.get('artist') or "Unknown Artist",
            "album": track.get('album') or "",
            "album_artist": track.get('album_artist', ''),
            "track_number": track.get('track_number', 0),
            "genre": track.get('genre', ''),
            "duration": track.get('duration_seconds') or 0,
            "sample_rate": track.get('sample_rate') or 0,
            "bit_depth": track.get('bit_depth') or 0,
            "channels": track.get('channels', 2),
            "file_path": track.get('file_path'),
            "folder_name": track.get('folder_name') or "",
            "audio_format": track.get('format') or "",
            "cover_path": track.get('cover_path') or ""
        }

    # ===== YouTube 관련 =====

    def search_youtube(self, title: str = "", artist: str = "", album: str = "",
                       use_title: bool = True, use_artist: bool = True,
                       use_album: bool = False) -> Dict[str, Any]:
        """YouTube 검색"""
        if not YOUTUBE_AVAILABLE:
            return {"success": False, "error": "youtube-search-python 라이브러리가 필요합니다", "results": []}

        try:
            query = build_search_query(title, artist, album, use_title, use_artist, use_album)
            logger.info(f"YouTube 검색 쿼리: '{query}' (제목={use_title}, 아티스트={use_artist}, 앨범={use_album})")
            if not query.strip():
                return {"success": False, "error": "검색어가 비어있습니다", "results": []}

            results = search_youtube(query, limit=5)
            return {"success": True, "query": query, "results": results}
        except Exception as e:
            logger.error(f"YouTube 검색 실패: {e}")
            return {"success": False, "error": str(e), "results": []}

    def cleanup(self):
        """정리"""
        self._running = False
        if self._engine:
            self._engine.stop()
