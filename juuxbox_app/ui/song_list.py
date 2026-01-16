"""
Song List View
==============
곡 목록 뷰 (테이블 형태) - 체크박스 선택 지원
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QAbstractItemView, QMenu, QCheckBox, QPushButton
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction

logger = logging.getLogger(__name__)


class SongListView(QWidget):
    """곡 목록 뷰"""

    song_double_clicked = Signal(str)  # file_path
    song_delete_requested = Signal(str)  # file_path (단일)
    songs_delete_requested = Signal(list)  # file_paths (복수)
    all_songs_delete_requested = Signal()  # 전체 삭제

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        # 헤더 영역
        header_layout = QHBoxLayout()

        self._header = QLabel("모든 곡")
        self._header.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self._header)

        header_layout.addStretch()

        # 선택 삭제 버튼
        self._delete_selected_btn = QPushButton("🗑️ 선택 삭제")
        self._delete_selected_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #282828;
                color: #666666;
            }
        """)
        self._delete_selected_btn.setEnabled(False)
        self._delete_selected_btn.clicked.connect(self._on_delete_selected)
        header_layout.addWidget(self._delete_selected_btn)

        layout.addLayout(header_layout)

        # 전체 선택 체크박스 (테이블 위)
        select_all_layout = QHBoxLayout()
        self._select_all_checkbox = QCheckBox("전체 선택")
        self._select_all_checkbox.setStyleSheet("""
            QCheckBox {
                color: #B3B3B3;
                font-size: 12px;
                spacing: 8px;
            }
        """)
        self._select_all_checkbox.stateChanged.connect(self._on_select_all_changed)
        select_all_layout.addWidget(self._select_all_checkbox)

        self._selection_count_label = QLabel("")
        self._selection_count_label.setStyleSheet("color: #1DB954; font-size: 12px; margin-left: 16px;")
        select_all_layout.addWidget(self._selection_count_label)

        select_all_layout.addStretch()
        layout.addLayout(select_all_layout)

        # 테이블
        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(["✓", "#", "제목", "아티스트", "앨범", "폴더", "시간"])

        # 컬럼 크기 설정
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self._table.setColumnWidth(0, 40)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self._table.setColumnWidth(1, 40)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self._table.setColumnWidth(6, 60)

        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                color: #FFFFFF;
                outline: none;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #282828;
            }
            QTableWidget::item:selected {
                background-color: #282828;
                color: #FFFFFF;
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

        self._table.itemChanged.connect(self._on_item_changed)
        self._table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._table, 1)

    def set_header(self, text: str):
        """헤더 텍스트 설정"""
        self._header.setText(text)

    def add_song(self, index: int, title: str, artist: str, album: str,
                 folder_name: str, duration: str, file_path: str):
        """곡 추가"""
        row = self._table.rowCount()
        self._table.insertRow(row)

        # 체크박스 아이템 (첫 번째 컬럼)
        check_item = QTableWidgetItem()
        check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        check_item.setCheckState(Qt.Unchecked)
        check_item.setData(Qt.UserRole, file_path)  # 파일 경로 저장
        self._table.setItem(row, 0, check_item)

        # 나머지 컬럼
        items = [
            QTableWidgetItem(str(index)),
            QTableWidgetItem(title),
            QTableWidgetItem(artist),
            QTableWidgetItem(album),
            QTableWidgetItem(folder_name),
            QTableWidgetItem(duration),
        ]

        for col, item in enumerate(items):
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._table.setItem(row, col + 1, item)

    def clear_songs(self):
        """모든 곡 제거"""
        self._table.setRowCount(0)
        self._select_all_checkbox.blockSignals(True)
        self._select_all_checkbox.setChecked(False)
        self._select_all_checkbox.blockSignals(False)
        self._update_selection_count()

    def _on_item_changed(self, item):
        """아이템 변경 (체크박스 상태 변경 감지)"""
        if item.column() == 0:
            self._update_selection_count()

    def _on_cell_double_clicked(self, row: int, col: int):
        """셀 더블클릭"""
        if col == 0:
            return  # 체크박스 컬럼 무시
        item = self._table.item(row, 0)
        if item:
            file_path = item.data(Qt.UserRole)
            if file_path:
                self.song_double_clicked.emit(file_path)
                logger.debug(f"곡 선택: {file_path}")

    def _on_select_all_changed(self, state):
        """전체 선택 체크박스 변경"""
        is_checked = (state == Qt.Checked)
        self._table.blockSignals(True)  # 개별 아이템 변경 시그널 차단
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item:
                item.setCheckState(Qt.Checked if is_checked else Qt.Unchecked)
        self._table.blockSignals(False)
        self._update_selection_count()

    def _update_selection_count(self):
        """선택된 항목 수 업데이트"""
        selected = self.get_selected_file_paths()
        count = len(selected)
        total = self._table.rowCount()

        if count > 0:
            self._selection_count_label.setText(f"({count}/{total}개 선택됨)")
            self._delete_selected_btn.setEnabled(True)
        else:
            self._selection_count_label.setText("")
            self._delete_selected_btn.setEnabled(False)

        # 전체 선택 체크박스 상태 동기화
        self._select_all_checkbox.blockSignals(True)
        if total > 0 and count == total:
            self._select_all_checkbox.setChecked(True)
        else:
            self._select_all_checkbox.setChecked(False)
        self._select_all_checkbox.blockSignals(False)

    def get_selected_file_paths(self) -> list:
        """선택된 곡들의 파일 경로 목록"""
        selected = []
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                file_path = item.data(Qt.UserRole)
                if file_path:
                    selected.append(file_path)
        return selected

    def select_by_file_path(self, file_path: str):
        """파일 경로로 해당 행 선택"""
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item and item.data(Qt.UserRole) == file_path:
                self._table.selectRow(row)
                self._table.scrollToItem(item)
                logger.debug(f"행 선택: {row}")
                return True
        return False

    def _show_context_menu(self, position):
        """우클릭 컨텍스트 메뉴"""
        item = self._table.itemAt(position)
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #282828;
                color: #FFFFFF;
                border: 1px solid #404040;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
            }
            QMenu::item:selected {
                background-color: #404040;
            }
        """)

        # 선택된 항목들 삭제
        selected = self.get_selected_file_paths()
        if selected:
            delete_selected_action = QAction(f"🗑️ 선택한 {len(selected)}곡 삭제", self)
            delete_selected_action.triggered.connect(self._on_delete_selected)
            menu.addAction(delete_selected_action)
            menu.addSeparator()

        if item:
            # 클릭한 곡 삭제
            row = item.row()
            check_item = self._table.item(row, 0)
            if check_item:
                file_path = check_item.data(Qt.UserRole)
                title_item = self._table.item(row, 2)
                title = title_item.text() if title_item else "Unknown"

                delete_action = QAction(f"🗑️ '{title}' 삭제", self)
                delete_action.triggered.connect(lambda: self._on_delete_song(file_path))
                menu.addAction(delete_action)
                menu.addSeparator()

        # 전체 삭제
        if self._table.rowCount() > 0:
            delete_all_action = QAction("🗑️ 전체 삭제", self)
            delete_all_action.triggered.connect(self._on_delete_all)
            menu.addAction(delete_all_action)

        if menu.actions():
            menu.exec_(self._table.viewport().mapToGlobal(position))

    def _on_delete_song(self, file_path: str):
        """곡 삭제 요청"""
        logger.debug(f"삭제 요청: {file_path}")
        self.song_delete_requested.emit(file_path)

    def _on_delete_selected(self):
        """선택된 곡들 삭제 요청"""
        selected = self.get_selected_file_paths()
        if selected:
            logger.debug(f"선택 삭제 요청: {len(selected)}곡")
            self.songs_delete_requested.emit(selected)

    def _on_delete_all(self):
        """전체 삭제 요청"""
        logger.debug("전체 삭제 요청")
        self.all_songs_delete_requested.emit()
