"""
YouTube Search Utility
======================
YouTube 검색 기능 (youtube-search-python 라이브러리 사용)
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# youtube-search-python 라이브러리 사용
try:
    from youtubesearchpython import VideosSearch
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    logger.warning("youtube-search-python 라이브러리가 설치되지 않았습니다. pip install youtube-search-python")


def search_youtube(query: str, limit: int = 5) -> list[dict]:
    """
    YouTube 검색 (조회수 기준 상위 결과)
    
    Args:
        query: 검색어
        limit: 결과 개수 (기본 5개)
    
    Returns:
        [
            {
                'title': '영상 제목',
                'channel': '채널명',
                'duration': '3:45',
                'views': '1,234,567 views',
                'view_count': 1234567,  # 정렬용
                'thumbnail': 'https://...',
                'video_id': 'abc123',
                'url': 'https://www.youtube.com/watch?v=abc123'
            },
            ...
        ]
    """
    if not YOUTUBE_AVAILABLE:
        logger.error("youtube-search-python 라이브러리가 필요합니다")
        return []
    
    if not query or not query.strip():
        return []
    
    try:
        logger.info(f"YouTube 검색: {query}")
        
        # 검색 (더 많이 가져와서 조회수로 정렬)
        search = VideosSearch(query, limit=limit * 2)
        results = search.result().get('result', [])
        
        videos = []
        for item in results:
            try:
                # 조회수 파싱
                view_text = item.get('viewCount', {}).get('text', '0 views')
                view_count = parse_view_count(view_text)
                
                videos.append({
                    'title': item.get('title', 'Unknown'),
                    'channel': item.get('channel', {}).get('name', 'Unknown'),
                    'duration': item.get('duration', ''),
                    'views': view_text,
                    'view_count': view_count,
                    'thumbnail': item.get('thumbnails', [{}])[0].get('url', ''),
                    'video_id': item.get('id', ''),
                    'url': item.get('link', '')
                })
            except Exception as e:
                logger.debug(f"결과 파싱 오류: {e}")
                continue
        
        # 조회수 기준 정렬 후 상위 limit개 반환
        videos.sort(key=lambda x: x['view_count'], reverse=True)
        result = videos[:limit]
        
        logger.info(f"YouTube 검색 결과: {len(result)}개")
        return result
        
    except Exception as e:
        logger.error(f"YouTube 검색 오류: {e}")
        return []


def parse_view_count(view_text: str) -> int:
    """조회수 텍스트를 숫자로 변환"""
    if not view_text:
        return 0
    
    try:
        # "1,234,567 views" -> 1234567
        # "1.2M views" -> 1200000
        # "500K views" -> 500000
        text = view_text.lower().replace(',', '').replace(' views', '').replace(' view', '').strip()
        
        if 'b' in text:  # Billion
            return int(float(text.replace('b', '')) * 1_000_000_000)
        elif 'm' in text:  # Million
            return int(float(text.replace('m', '')) * 1_000_000)
        elif 'k' in text:  # Thousand
            return int(float(text.replace('k', '')) * 1_000)
        else:
            return int(text)
    except (ValueError, TypeError):
        return 0


def build_search_query(title: str = "", artist: str = "", album: str = "",
                       use_title: bool = True, use_artist: bool = True, 
                       use_album: bool = False) -> str:
    """검색어 조합"""
    parts = []
    if use_title and title:
        parts.append(title)
    if use_artist and artist:
        parts.append(artist)
    if use_album and album:
        parts.append(album)
    
    return " ".join(parts)
