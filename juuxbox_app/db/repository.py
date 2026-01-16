"""
Repository
==========
CRUD 함수
"""

import logging
from typing import Optional
from .models import get_connection

logger = logging.getLogger(__name__)


class TrackRepository:
    """트랙 CRUD"""

    @staticmethod
    def insert(track_data: dict) -> int:
        """트랙 추가"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO tracks
            (file_path, title, artist, album, folder_name, duration_seconds, sample_rate, bit_depth, format)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            track_data.get("file_path"),
            track_data.get("title"),
            track_data.get("artist"),
            track_data.get("album"),
            track_data.get("folder_name"),
            track_data.get("duration_seconds"),
            track_data.get("sample_rate"),
            track_data.get("bit_depth"),
            track_data.get("format"),
        ))
        conn.commit()
        track_id = cursor.lastrowid
        conn.close()
        return track_id

    @staticmethod
    def get_all() -> list[dict]:
        """모든 트랙 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks ORDER BY artist, album, track_number")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_by_album(album: str) -> list[dict]:
        """앨범별 트랙 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks WHERE album = ? ORDER BY track_number", (album,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows


class PlaylistRepository:
    """플레이리스트 CRUD"""

    @staticmethod
    def create(name: str) -> int:
        """플레이리스트 생성"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
        conn.commit()
        playlist_id = cursor.lastrowid
        conn.close()
        return playlist_id

    @staticmethod
    def get_all() -> list[dict]:
        """모든 플레이리스트 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM playlists")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
