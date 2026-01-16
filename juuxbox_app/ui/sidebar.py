"""
Sidebar
=======
라이브러리, 플레이리스트 사이드바
"""

import logging
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog
)
from PySide6.QtCore import Signal

logger = logging.getLogger(__name__)


class Sidebar(QFrame):
    """
    사이드바 위젯
    
    Sections:
    - 라이브러리 (홈, 검색)
    - 플레이리스트 목록
    - 설정
    """

    # 시그널
    library_clicked = Signal()
    playlist_selected = Signal(str)  # playlist_id
    settings_clicked = Signal()
    add_folder_clicked = Signal(str)  # folder_path

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 로고
        logo = QLabel("🎵 JuuxBox")
        logo.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #FFFFFF;
            padding: 8px 0;
        """)
        layout.addWidget(logo)

        # 라이브러리 섹션
        library_label = QLabel("라이브러리")
        library_label.setStyleSheet("color: #B3B3B3; font-size: 11px; padding-top: 16px;")
        layout.addWidget(library_label)

        home_btn = QPushButton("🏠 홈")
        home_btn.setFlat(True)
        home_btn.clicked.connect(self.library_clicked.emit)
        layout.addWidget(home_btn)

        search_btn = QPushButton("🔍 검색")
        search_btn.setFlat(True)
        layout.addWidget(search_btn)

        # 폴더 추가 버튼
        add_folder_btn = QPushButton("➕ 폴더 추가")
        add_folder_btn.setFlat(True)
        add_folder_btn.setStyleSheet("""
            QPushButton {
                color: #1DB954;
                font-weight: bold;
                padding: 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #282828;
                border-radius: 4px;
            }
        """)
        add_folder_btn.clicked.connect(self._on_add_folder_clicked)
        layout.addWidget(add_folder_btn)

        # 플레이리스트 섹션
        playlist_label = QLabel("플레이리스트")
        playlist_label.setStyleSheet("color: #B3B3B3; font-size: 11px; padding-top: 16px;")
        layout.addWidget(playlist_label)

        self._playlist_list = QListWidget()
        self._playlist_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                color: #FFFFFF;
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #282828;
            }
            QListWidget::item:selected {
                background-color: #1DB954;
            }
        """)
        self._playlist_list.itemClicked.connect(self._on_playlist_clicked)
        layout.addWidget(self._playlist_list, 1)

        # 설정
        settings_btn = QPushButton("⚙️ 설정")
        settings_btn.setFlat(True)
        settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(settings_btn)

    def add_playlist(self, name: str, playlist_id: str):
        """플레이리스트 추가"""
        item = QListWidgetItem(f"📁 {name}")
        item.setData(100, playlist_id)  # 커스텀 데이터
        self._playlist_list.addItem(item)

    def _on_playlist_clicked(self, item: QListWidgetItem):
        """플레이리스트 클릭 핸들러"""
        playlist_id = item.data(100)
        self.playlist_selected.emit(playlist_id)
        logger.debug(f"플레이리스트 선택: {playlist_id}")

    def _on_add_folder_clicked(self):
        """폴더 추가 버튼 클릭 핸들러"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "음악 폴더 선택",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder_path:
            logger.info(f"폴더 선택됨: {folder_path}")
            self.add_folder_clicked.emit(folder_path)
