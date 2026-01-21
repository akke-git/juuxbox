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
            (file_path, title, artist, album, album_artist, folder_name, cover_path,
             track_number, genre, duration_seconds, sample_rate, bit_depth, channels, format)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            track_data.get("file_path"),
            track_data.get("title"),
            track_data.get("artist"),
            track_data.get("album"),
            track_data.get("album_artist", ""),
            track_data.get("folder_name"),
            track_data.get("cover_path"),
            track_data.get("track_number", 0),
            track_data.get("genre", ""),
            track_data.get("duration_seconds"),
            track_data.get("sample_rate"),
            track_data.get("bit_depth"),
            track_data.get("channels", 2),
            track_data.get("format"),
        ))
        conn.commit()
        track_id = cursor.lastrowid
        conn.close()
        return track_id

    @staticmethod
    def exists_by_file_path(file_path: str) -> bool:
        """파일 경로로 트랙 존재 여부 확인"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM tracks WHERE file_path = ?", (file_path,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    @staticmethod
    def get_by_file_path(file_path: str) -> dict | None:
        """파일 경로로 트랙 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

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

    @staticmethod
    def delete_by_file_path(file_path: str) -> bool:
        """파일 경로로 트랙 삭제"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracks WHERE file_path = ?", (file_path,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        if deleted:
            logger.info(f"트랙 삭제: {file_path}")
        return deleted

    @staticmethod
    def delete_by_file_paths(file_paths: list) -> int:
        """여러 트랙 삭제 (배치)"""
        if not file_paths:
            return 0
        conn = get_connection()
        cursor = conn.cursor()
        placeholders = ",".join("?" * len(file_paths))
        cursor.execute(f"DELETE FROM tracks WHERE file_path IN ({placeholders})", file_paths)
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        logger.info(f"선택 트랙 삭제: {deleted_count}개")
        return deleted_count

    @staticmethod
    def delete_all() -> int:
        """모든 트랙 삭제"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracks")
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        logger.info(f"전체 트랙 삭제: {deleted_count}개")
        return deleted_count

    @staticmethod
    def get_albums() -> list[dict]:
        """앨범별 그룹핑 조회 (앨범아트, 아티스트, 트랙 수 포함)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT album, artist, cover_path, COUNT(*) as track_count,
                   SUM(duration_seconds) as total_duration
            FROM tracks
            WHERE album IS NOT NULL AND album != ''
            GROUP BY album
            ORDER BY album
        """)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_artists() -> list[dict]:
        """아티스트별 그룹핑 조회 (대표 앨범아트, 앨범 수, 트랙 수 포함)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT artist, 
                   (SELECT cover_path FROM tracks t2 
                    WHERE t2.artist = tracks.artist AND t2.cover_path IS NOT NULL 
                    LIMIT 1) as cover_path,
                   COUNT(DISTINCT album) as album_count,
                   COUNT(*) as track_count
            FROM tracks
            WHERE artist IS NOT NULL AND artist != ''
            GROUP BY artist
            ORDER BY artist
        """)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_folders() -> list[dict]:
        """폴더별 그룹핑 조회 (대표 앨범아트, 트랙 수 포함)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT folder_name,
                   (SELECT cover_path FROM tracks t2 
                    WHERE t2.folder_name = tracks.folder_name AND t2.cover_path IS NOT NULL 
                    LIMIT 1) as cover_path,
                   COUNT(*) as track_count
            FROM tracks
            WHERE folder_name IS NOT NULL AND folder_name != ''
            GROUP BY folder_name
            ORDER BY folder_name
        """)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_tracks_by_album(album: str) -> list[dict]:
        """앨범별 트랙 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks WHERE album = ? ORDER BY track_number", (album,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_tracks_by_artist(artist: str) -> list[dict]:
        """아티스트별 트랙 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks WHERE artist = ? ORDER BY album, track_number", (artist,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def get_tracks_by_folder(folder_name: str) -> list[dict]:
        """폴더별 트랙 조회"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracks WHERE folder_name = ? ORDER BY title", (folder_name,))
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
