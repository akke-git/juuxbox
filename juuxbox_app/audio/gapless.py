"""
Gapless Playback Manager
========================
곡 전환 시 끊김 없는 재생을 위한 관리자
"""

import logging
from typing import Optional, Callable
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QueuedTrack:
    """대기열 트랙 정보"""
    file_path: str
    preloaded: bool = False


class GaplessManager:
    """
    Gapless 재생 관리자
    
    다음 곡을 미리 버퍼에 로드하여 곡 전환 시 끊김을 최소화합니다.
    """

    def __init__(self, prebuffer_count: int = 1):
        """
        Args:
            prebuffer_count: 미리 로드할 곡 수
        """
        self._prebuffer_count = prebuffer_count
        self._queue: deque[QueuedTrack] = deque()
        self._current_index: int = -1
        
        # 콜백
        self._on_track_change: Optional[Callable[[str], None]] = None
        
        logger.info(f"GaplessManager 초기화 (prebuffer: {prebuffer_count})")

    def set_queue(self, tracks: list[str]):
        """
        재생 대기열 설정
        
        Args:
            tracks: 트랙 파일 경로 목록
        """
        self._queue = deque(QueuedTrack(path) for path in tracks)
        self._current_index = -1
        logger.info(f"대기열 설정: {len(tracks)}곡")

    def add_to_queue(self, track: str):
        """대기열에 트랙 추가"""
        self._queue.append(QueuedTrack(track))
        logger.debug(f"대기열 추가: {track}")

    def get_next_track(self) -> Optional[str]:
        """
        다음 트랙 가져오기
        
        Returns:
            다음 트랙 경로 또는 None
        """
        if self._current_index + 1 < len(self._queue):
            self._current_index += 1
            track = self._queue[self._current_index]
            logger.info(f"다음 트랙: {track.file_path}")
            return track.file_path
        return None

    def get_previous_track(self) -> Optional[str]:
        """
        이전 트랙 가져오기
        
        Returns:
            이전 트랙 경로 또는 None
        """
        if self._current_index > 0:
            self._current_index -= 1
            track = self._queue[self._current_index]
            logger.info(f"이전 트랙: {track.file_path}")
            return track.file_path
        return None

    def preload_next(self):
        """다음 곡 미리 로드 (백그라운드)"""
        # TODO: 비동기로 다음 곡 디코딩
        next_index = self._current_index + 1
        if next_index < len(self._queue):
            track = self._queue[next_index]
            if not track.preloaded:
                logger.debug(f"미리 로드 시작: {track.file_path}")
                # 실제 로드 로직
                track.preloaded = True

    def get_current_track(self) -> Optional[str]:
        """현재 트랙 경로"""
        if 0 <= self._current_index < len(self._queue):
            return self._queue[self._current_index].file_path
        return None

    def get_queue_length(self) -> int:
        """대기열 길이"""
        return len(self._queue)

    def clear_queue(self):
        """대기열 초기화"""
        self._queue.clear()
        self._current_index = -1
        logger.info("대기열 초기화")
