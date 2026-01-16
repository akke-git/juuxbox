"""
Album View
==========
앨범 그리드 뷰
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QScrollArea, QFrame
)
from PySide6.QtCore import Signal, Qt

logger = logging.getLogger(__name__)


class AlbumCard(QFrame):
    """단일 앨범 카드"""

    clicked = Signal(str)  # album_id

    def __init__(self, album_id: str, title: str, artist: str):
        super().__init__()
        self._album_id = album_id
        self._setup_ui(title, artist)

    def _setup_ui(self, title: str, artist: str):
        """UI 구성"""
        self.setFixedSize(180, 220)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            AlbumCard {
                background-color: #181818;
                border-radius: 8px;
                padding: 12px;
            }
            AlbumCard:hover {
                background-color: #282828;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # 앨범 아트
        art = QLabel("🎵")
        art.setFixedSize(156, 156)
        art.setAlignment(Qt.AlignCenter)
        art.setStyleSheet("""
            background-color: #282828;
            border-radius: 4px;
            font-size: 48px;
        """)
        layout.addWidget(art)

        # 앨범 제목
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 14px;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # 아티스트
        artist_label = QLabel(artist)
        artist_label.setStyleSheet("color: #B3B3B3; font-size: 12px;")
        layout.addWidget(artist_label)

    def mousePressEvent(self, event):
        """클릭 이벤트"""
        self.clicked.emit(self._album_id)
        super().mousePressEvent(event)


class AlbumView(QWidget):
    """앨범 그리드 뷰"""

    album_selected = Signal(str)  # album_id

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        # 헤더
        header = QLabel("앨범")
        header.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)

        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # 그리드 컨테이너
        container = QWidget()
        self._grid = QGridLayout(container)
        self._grid.setSpacing(16)
        scroll.setWidget(container)

        layout.addWidget(scroll, 1)

        # 샘플 앨범 추가 (테스트용)
        self._add_sample_albums()

    def _add_sample_albums(self):
        """샘플 앨범 추가 (테스트용)"""
        samples = [
            ("1", "Sample Album 1", "Artist A"),
            ("2", "Sample Album 2", "Artist B"),
            ("3", "Sample Album 3", "Artist C"),
        ]
        for i, (album_id, title, artist) in enumerate(samples):
            self.add_album(album_id, title, artist, i // 4, i % 4)

    def add_album(self, album_id: str, title: str, artist: str, row: int, col: int):
        """앨범 추가"""
        card = AlbumCard(album_id, title, artist)
        card.clicked.connect(self.album_selected.emit)
        self._grid.addWidget(card, row, col)

    def clear_albums(self):
        """모든 앨범 제거"""
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
