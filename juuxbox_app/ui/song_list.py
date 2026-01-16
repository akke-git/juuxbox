"""
Song List View
==============
곡 목록 뷰 (테이블 형태)
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel
)
from PySide6.QtCore import Signal, Qt

logger = logging.getLogger(__name__)


class SongListView(QWidget):
    """곡 목록 뷰"""

    song_double_clicked = Signal(str)  # file_path

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        # 헤더
        self._header = QLabel("모든 곡")
        self._header.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold;")
        layout.addWidget(self._header)

        # 테이블
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["#", "제목", "아티스트", "앨범", "시간"])
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                color: #FFFFFF;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #282828;
            }
            QTableWidget::item:selected {
                background-color: #282828;
            }
            QTableWidget::item:hover {
                background-color: #1a1a1a;
            }
            QHeaderView::section {
                background-color: transparent;
                color: #B3B3B3;
                border: none;
                border-bottom: 1px solid #282828;
                padding: 8px;
                font-size: 11px;
            }
        """)
        self._table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self._table, 1)

    def set_header(self, text: str):
        """헤더 텍스트 설정"""
        self._header.setText(text)

    def add_song(self, index: int, title: str, artist: str, album: str, 
                 duration: str, file_path: str):
        """곡 추가"""
        row = self._table.rowCount()
        self._table.insertRow(row)

        self._table.setItem(row, 0, QTableWidgetItem(str(index)))
        self._table.setItem(row, 1, QTableWidgetItem(title))
        self._table.setItem(row, 2, QTableWidgetItem(artist))
        self._table.setItem(row, 3, QTableWidgetItem(album))
        self._table.setItem(row, 4, QTableWidgetItem(duration))

        # 파일 경로를 첫 번째 셀에 저장
        self._table.item(row, 0).setData(Qt.UserRole, file_path)

    def clear_songs(self):
        """모든 곡 제거"""
        self._table.setRowCount(0)

    def _on_double_click(self, index):
        """더블클릭 핸들러"""
        row = index.row()
        file_path = self._table.item(row, 0).data(Qt.UserRole)
        if file_path:
            self.song_double_clicked.emit(file_path)
            logger.debug(f"곡 선택: {file_path}")
