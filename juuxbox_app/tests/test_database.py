#!/usr/bin/env python3
"""
Phase 2: Database & Scanner Test
=================================
SQLite 데이터베이스 및 라이브러리 스캐너 테스트
"""

import sys
from pathlib import Path

# 프로젝트 모듈 import를 위해 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.models import create_tables, get_connection, DB_PATH
from db.scanner import LibraryScanner
from db.repository import TrackRepository, PlaylistRepository


def test_database_setup():
    """데이터베이스 설정 테스트"""
    print(f"\n{'='*60}")
    print(f"🗄️ 데이터베이스 설정 테스트")
    print('='*60)
    
    try:
        # 테이블 생성
        create_tables()
        print(f"\n✅ 테이블 생성 완료")
        print(f"   경로: {DB_PATH}")
        
        # 테이블 확인
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"\n📋 생성된 테이블:")
        for table in tables:
            print(f"   - {table}")
        
        return True
    except Exception as e:
        print(f"❌ 에러: {e}")
        return False


def test_library_scanner(scan_path: str):
    """라이브러리 스캐너 테스트"""
    print(f"\n{'='*60}")
    print(f"🔍 라이브러리 스캐너 테스트")
    print('='*60)
    
    def on_progress(current, total):
        print(f"   스캔 중: {current}/{total}")
    
    try:
        scanner = LibraryScanner(on_progress=on_progress)
        tracks = scanner.scan_folder(scan_path)
        
        print(f"\n✅ 스캔 완료: {len(tracks)}개 트랙 발견")
        
        for i, track in enumerate(tracks):
            print(f"\n   [{i+1}] {track.get('title', 'Unknown')}")
            print(f"       아티스트: {track.get('artist', 'Unknown')}")
            print(f"       앨범: {track.get('album', 'Unknown')}")
            print(f"       Sample Rate: {track.get('sample_rate', 0)} Hz")
            print(f"       Bit Depth: {track.get('bit_depth', 0)} bit")
            print(f"       길이: {track.get('duration_seconds', 0):.1f}초")
        
        return tracks
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_track_repository(tracks: list):
    """트랙 저장소 테스트"""
    print(f"\n{'='*60}")
    print(f"💾 트랙 저장소 테스트")
    print('='*60)
    
    try:
        # 트랙 저장
        for track in tracks:
            track_id = TrackRepository.insert(track)
            print(f"   저장됨: ID={track_id}, {track.get('title')}")
        
        # 모든 트랙 조회
        all_tracks = TrackRepository.get_all()
        print(f"\n✅ 저장된 트랙 조회: {len(all_tracks)}개")
        
        return True
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_playlist_repository():
    """플레이리스트 저장소 테스트"""
    print(f"\n{'='*60}")
    print(f"📁 플레이리스트 저장소 테스트")
    print('='*60)
    
    try:
        # 플레이리스트 생성
        playlist_id = PlaylistRepository.create("Test Playlist")
        print(f"   생성됨: ID={playlist_id}, 'Test Playlist'")
        
        # 모든 플레이리스트 조회
        playlists = PlaylistRepository.get_all()
        print(f"\n✅ 플레이리스트 조회: {len(playlists)}개")
        for pl in playlists:
            print(f"   - [{pl['id']}] {pl['name']}")
        
        return True
    except Exception as e:
        print(f"❌ 에러: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("\n" + "="*60)
    print("🎵 JuuxBox Database & Scanner Test - Phase 2")
    print("="*60)
    
    # 샘플 폴더 경로
    sample_dir = "/project/juuxbox/Music_Sample"
    
    # 1. 데이터베이스 설정 테스트
    db_ok = test_database_setup()
    
    # 2. 라이브러리 스캐너 테스트
    tracks = test_library_scanner(sample_dir)
    
    # 3. 트랙 저장소 테스트
    repo_ok = test_track_repository(tracks) if tracks else False
    
    # 4. 플레이리스트 저장소 테스트
    playlist_ok = test_playlist_repository()
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("📊 테스트 결과 요약")
    print('='*60)
    
    print(f"\n{'✅' if db_ok else '❌'} 데이터베이스 설정: {'성공' if db_ok else '실패'}")
    print(f"{'✅' if tracks else '❌'} 라이브러리 스캔: {len(tracks)}개 트랙")
    print(f"{'✅' if repo_ok else '❌'} 트랙 저장소: {'성공' if repo_ok else '실패'}")
    print(f"{'✅' if playlist_ok else '❌'} 플레이리스트: {'성공' if playlist_ok else '실패'}")
    
    print("\n" + "="*60)
    print("🎉 Phase 2 테스트 완료!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
