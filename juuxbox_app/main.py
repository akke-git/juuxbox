"""
JuuxBox Hi-Fi Music Player
============================
Windows 환경에서 WASAPI Exclusive 모드를 지원하는 하이파이 뮤직 플레이어

Author: juuxbox
License: MIT
"""

import sys
import logging
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from utils.logger import setup_logging
from utils.config import load_config


def main():
    """애플리케이션 진입점"""
    # 로깅 설정
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("JuuxBox 시작...")

    # 설정 로드
    config = load_config()

    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationName("JuuxBox")
    app.setApplicationVersion("0.1.0")

    # 메인 윈도우 생성 및 표시
    window = MainWindow(config)
    window.show()

    logger.info("JuuxBox UI 초기화 완료")

    # 이벤트 루프 실행
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
