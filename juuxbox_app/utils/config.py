"""
Config Manager
==============
설정 파일 관리
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_PATH = Path.home() / ".juuxbox" / "config.json"

DEFAULT_CONFIG = {
    "audio": {
        "output_device": None,
        "exclusive_mode": True,
        "software_volume": 100,
        "gapless_enabled": True
    },
    "library": {
        "scan_paths": [],
        "auto_scan_on_startup": True
    },
    "ui": {
        "theme": "spotify_dark",
        "language": "ko",
        "show_audio_specs": True
    },
    "playback": {
        "shuffle": False,
        "repeat_mode": "off",
        "remember_position": True
    }
}


def load_config() -> dict:
    """설정 로드"""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                logger.info("설정 로드 완료")
                return {**DEFAULT_CONFIG, **config}
        except Exception as e:
            logger.warning(f"설정 로드 실패: {e}")
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """설정 저장"""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    logger.info("설정 저장 완료")
