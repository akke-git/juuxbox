"""
Logger Setup
============
로깅 설정
"""

import logging
import logging.handlers
from pathlib import Path


def setup_logging(level: int = logging.INFO):
    """로깅 설정"""
    log_dir = Path.home() / ".juuxbox" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "juuxbox.log"

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 파일 핸들러
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info("로깅 설정 완료")
