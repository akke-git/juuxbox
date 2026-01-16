"""
Database Models
===============
SQLite 테이블 정의
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path.home() / ".juuxbox" / "library.db"


def get_connection() -> sqlite3.Connection:
    """데이터베이스 연결"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """테이블 생성"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 트랙 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            title TEXT,
            artist TEXT,
            album TEXT,
            album_artist TEXT,
            folder_name TEXT,
            track_number INTEGER,
            disc_number INTEGER,
            year INTEGER,
            genre TEXT,
            duration_seconds REAL,
            sample_rate INTEGER,
            bit_depth INTEGER,
            channels INTEGER,
            format TEXT,
            file_size INTEGER,
            last_modified REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 플레이리스트 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 플레이리스트-트랙 연결 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist_tracks (
            playlist_id INTEGER,
            track_id INTEGER,
            position INTEGER,
            FOREIGN KEY (playlist_id) REFERENCES playlists(id),
            FOREIGN KEY (track_id) REFERENCES tracks(id),
            PRIMARY KEY (playlist_id, track_id)
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("데이터베이스 테이블 생성 완료")
