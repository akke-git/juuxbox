#!/usr/bin/env python3
"""
JuuxBox - Hi-Fi Music Player (pywebview UI)
============================================
WASAPI Exclusive 모드를 지원하는 하이파이 뮤직 플레이어
pywebview 기반 웹 UI

Usage:
    python app.py              # 앱 실행
    python app.py --debug      # 디버그 모드
"""

import sys
import logging
from pathlib import Path

# 프로젝트 경로 설정
sys.path.insert(0, str(Path(__file__).parent))

import webview
from api import JuuxBoxAPI
from utils.logger import setup_logging

# 로깅 설정
setup_logging(logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """메인 함수"""
    # 디버그 모드 확인
    debug_mode = '--debug' in sys.argv

    if debug_mode:
        setup_logging(logging.DEBUG)
        logger.info("디버그 모드 활성화")

    # API 인스턴스 생성
    api = JuuxBoxAPI()

    # 웹 UI 경로
    webui_path = Path(__file__).parent / "webui" / "index.html"

    if not webui_path.exists():
        logger.error(f"웹 UI 파일을 찾을 수 없습니다: {webui_path}")
        sys.exit(1)

    # pywebview 창 생성
    window = webview.create_window(
        title="JuuxBox - Hi-Fi Music Player",
        url=str(webui_path),
        width=1280,
        height=800,
        min_size=(900, 600),
        resizable=True,
        confirm_close=False,
        js_api=api  # Python API를 JavaScript에서 사용 가능하게
    )

    # API에 윈도우 참조 전달
    api.set_window(window)

    logger.info("JuuxBox 시작!")

    # pywebview 실행 (Windows: Edge WebView2)
    webview.start(debug=debug_mode)

    # 정리
    api.cleanup()
    logger.info("JuuxBox 종료")


if __name__ == "__main__":
    main()
