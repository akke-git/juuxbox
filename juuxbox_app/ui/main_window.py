"""
Main Window
===========
JuuxBox 메인 윈도우
"""

import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QStackedWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

from .sidebar import Sidebar
from .player_bar import PlayerBar
from .album_view import AlbumView
from .song_list import SongListView

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    PureSound 메인 윈도우
    
    Layout:
    ┌─────────┬────────────────────┐
    │         │                    │
    │ Sidebar │    Main View       │
    │ (240px) │   (Album/Songs)    │
    │         │                    │
    ├─────────┴────────────────────┤
    │        Player Bar (90px)     │
    └──────────────────────────────┘
    """

    def __init__(self, config: dict = None):
        super().__init__()
        self._config = config or {}
        
        self._setup_window()
        self._setup_ui()
        self._setup_shortcuts()
        self._load_stylesheet()
        
        logger.info("MainWindow 초기화 완료")

    def _setup_window(self):
        """윈도우 기본 설정"""
        self.setWindowTitle("JuuxBox")
        self.setMinimumSize(1024, 600)
        self.resize(1280, 720)

    def _setup_ui(self):
        """UI 구성"""
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃 (수직)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 상단 영역 (사이드바 + 메인뷰)
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        # 사이드바 (왼쪽)
        self._sidebar = Sidebar()
        self._sidebar.setFixedWidth(240)
        self._sidebar.setObjectName("Sidebar")
        top_layout.addWidget(self._sidebar)

        # 메인 뷰 영역 (중앙)
        self._main_stack = QStackedWidget()
        self._album_view = AlbumView()
        self._song_list = SongListView()
        self._main_stack.addWidget(self._album_view)
        self._main_stack.addWidget(self._song_list)
        top_layout.addWidget(self._main_stack, 1)

        main_layout.addWidget(top_container, 1)

        # 플레이어 바 (하단)
        self._player_bar = PlayerBar()
        self._player_bar.setFixedHeight(90)
        main_layout.addWidget(self._player_bar)

    def _setup_shortcuts(self):
        """키보드 단축키 설정"""
        shortcuts = {
            "Space": self._on_play_pause,
            "Left": self._on_previous,
            "Right": self._on_next,
            "Up": self._on_volume_up,
            "Down": self._on_volume_down,
            "M": self._on_mute,
            "S": self._on_shuffle,
            "R": self._on_repeat,
        }
        
        for key, handler in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(handler)

    def _load_stylesheet(self):
        """QSS 스타일시트 로드"""
        # TODO: resources/styles/spotify_dark.qss 파일에서 로드
        qss = """
            QMainWindow {
                background-color: #121212;
                color: #FFFFFF;
            }
            QFrame#Sidebar {
                background-color: #000000;
                border-right: 1px solid #282828;
            }
        """
        self.setStyleSheet(qss)

    # 단축키 핸들러
    def _on_play_pause(self):
        logger.debug("단축키: 재생/일시정지")
        self._player_bar.toggle_play()

    def _on_previous(self):
        logger.debug("단축키: 이전 곡")

    def _on_next(self):
        logger.debug("단축키: 다음 곡")

    def _on_volume_up(self):
        logger.debug("단축키: 볼륨 증가")

    def _on_volume_down(self):
        logger.debug("단축키: 볼륨 감소")

    def _on_mute(self):
        logger.debug("단축키: 음소거")

    def _on_shuffle(self):
        logger.debug("단축키: 셔플")

    def _on_repeat(self):
        logger.debug("단축키: 반복")

    def closeEvent(self, event):
        """윈도우 종료 시 정리"""
        logger.info("JuuxBox 종료")
        # TODO: 오디오 엔진 정리
        event.accept()
