"""
Song List View
==============
곡 목록 뷰 (테이블 형태) - 체크박스 선택 지원
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QAbstractItemView, QMenu, QCheckBox, QPushButton,
    QStyledItemDelegate, QStyle
)
from PySide6.QtCore import Signal, Qt, QRect
from PySide6.QtGui import QAction, QColor, QBrush, QPainter, QPen, QFont

logger = logging.getLogger(__name__)


class FormatTagDelegate(QStyledItemDelegate):
    """Notion 스타일 포맷 태그 렌더링"""
    
    FORMAT_COLORS = {
        "FLAC": ("#1DB954", "#0d5c2a"),   # 녹색 (Lossless)
        "WAV": ("#1E90FF", "#0d4a8a"),    # 파란색 (Lossless)
        "AIFF": ("#1E90FF", "#0d4a8a"),
        "AIF": ("#1E90FF", "#0d4a8a"),
        "DSF": ("#9B59B6", "#5c3470"),    # 보라색 (DSD)
        "DFF": ("#9B59B6", "#5c3470"),
        "M4A": ("#FF9500", "#8a5200"),    # 오렌지 (AAC/ALAC)
        "ALAC": ("#FF9500", "#8a5200"),
        "MP3": ("#E74C3C", "#8a2d22"),    # 빨간색 (Lossy)
        "OGG": ("#E74C3C", "#8a2d22"),
    }
    
    def paint(self, painter: QPainter, option, index):
        text = index.data(Qt.DisplayRole)
        if not text:
            return super().paint(painter, option, index)
        
        fmt = text.upper()
        colors = self.FORMAT_COLORS.get(fmt, ("#888888", "#444444"))
        bg_color = QColor(colors[1])
        text_color = QColor(colors[0])
        
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 태그 배경 (라운드 사각형)
        tag_text = fmt
        font = QFont()
        font.setPixelSize(11)
        font.setBold(True)
        painter.setFont(font)
        
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(tag_text)
        tag_width = text_width + 12
        tag_height = 20
        
        # 중앙 정렬
        x = option.rect.x() + (option.rect.width() - tag_width) // 2
        y = option.rect.y() + (option.rect.height() - tag_height) // 2
        
        tag_rect = QRect(x, y, tag_width, tag_height)
        
        # 배경 그리기
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(tag_rect, 4, 4)
        
        # 텍스트 그리기
        painter.setPen(QPen(text_color))
        painter.drawText(tag_rect, Qt.AlignCenter, tag_text)
        
        painter.restore()


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
        header_layout = QVBoxLayout()
        header_layout.setSpacing(16)  # 제목과 버튼 사이 간격

        # 제목 행
        title_row = QHBoxLayout()
        self._header = QLabel("All Songs")
        self._header.setStyleSheet("color: #FFFFFF; font-size: 28px; font-weight: 600;")
        title_row.addWidget(self._header)
        title_row.addStretch()
        header_layout.addLayout(title_row)

        # 컨트롤 행 (뷰 토글 + 삭제 버튼)
        control_row = QHBoxLayout()

        # 뷰 토글 버튼 (Notion 스타일)
        toggle_btn_style = """
            QPushButton {
                background-color: transparent;
                color: #9B9B9B;
                border: none;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            }
            QPushButton:checked {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """
        
        self._list_view_btn = QPushButton("☰ List")
        self._list_view_btn.setCheckable(True)
        self._list_view_btn.setChecked(False)
        self._list_view_btn.setStyleSheet(toggle_btn_style)
        self._list_view_btn.clicked.connect(lambda: self._switch_view("list"))
        control_row.addWidget(self._list_view_btn)

        self._table_view_btn = QPushButton("⊞ Table")
        self._table_view_btn.setCheckable(True)
        self._table_view_btn.setChecked(True)  # 기본값: Table
        self._table_view_btn.setStyleSheet(toggle_btn_style)
        self._table_view_btn.clicked.connect(lambda: self._switch_view("table"))
        control_row.addWidget(self._table_view_btn)

        control_row.addStretch()

        # 선택 삭제 버튼
        self._delete_selected_btn = QPushButton("🗑️ Delete")
        self._delete_selected_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #9B9B9B;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                color: #FFFFFF;
            }
            QPushButton:disabled {
                color: #555555;
                border-color: #333333;
            }
        """)
        self._delete_selected_btn.setEnabled(False)
        self._delete_selected_btn.clicked.connect(self._on_delete_selected)
        control_row.addWidget(self._delete_selected_btn)

        # 선택 카운트 라벨
        self._selection_count_label = QLabel("")
        self._selection_count_label.setStyleSheet("color: #1DB954; font-size: 12px; margin-left: 8px;")
        control_row.addWidget(self._selection_count_label)

        header_layout.addLayout(control_row)
        layout.addLayout(header_layout)

        # 테이블
        self._table = QTableWidget()
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels(["✓", "#", "제목", "아티스트", "앨범", "포맷", "폴더", "시간"])

        # 포맷별 색상 정의
        self._format_colors = {
            "FLAC": "#1DB954",    # 녹색 (Lossless)
            "WAV": "#1E90FF",     # 파란색 (Lossless)
            "AIFF": "#1E90FF",    # 파란색 (Lossless)
            "AIF": "#1E90FF",     # 파란색 (Lossless)
            "DSF": "#9B59B6",     # 보라색 (DSD)
            "DFF": "#9B59B6",     # 보라색 (DSD)
            "M4A": "#FF9500",     # 오렌지 (AAC/ALAC)
            "ALAC": "#FF9500",    # 오렌지 (ALAC)
            "MP3": "#E74C3C",     # 빨간색 (Lossy)
            "OGG": "#E74C3C",     # 빨간색 (Lossy)
        }

        # 컬럼 크기 설정
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self._table.setColumnWidth(0, 40)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self._table.setColumnWidth(1, 40)
        # 나머지 컬럼은 사용자가 조절 가능 (Interactive)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self._table.setColumnWidth(2, 200)  # 제목
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self._table.setColumnWidth(3, 150)  # 아티스트
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        self._table.setColumnWidth(4, 150)  # 앨범
        self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Interactive)
        self._table.setColumnWidth(5, 60)   # 포맷
        self._table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Interactive)
        self._table.setColumnWidth(6, 150)  # 폴더
        self._table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Interactive)
        self._table.setColumnWidth(7, 60)   # 시간
        
        # 마지막 컬럼 늘리기
        self._table.horizontalHeader().setStretchLastSection(False)

        # 헤더 좌측정렬 (Qt에서 명시적 설정)
        self._table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

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
                padding: 8px 12px;
                border-bottom: 1px solid #2d2d2d;
            }
            QTableWidget::item:selected {
                background-color: rgba(255, 255, 255, 0.05);
                color: #FFFFFF;
            }
            QTableWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.03);
            }
            QHeaderView::section {
                background-color: transparent;
                color: #9B9B9B;
                border: none;
                border-bottom: 1px solid #2d2d2d;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
                text-align: left;
            }
        """)

        # 포맷 컬럼에 Notion 스타일 태그 델리게이트 적용
        self._format_delegate = FormatTagDelegate()
        self._table.setItemDelegateForColumn(5, self._format_delegate)

        self._table.itemChanged.connect(self._on_item_changed)
        self._table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._table, 1)

    def set_header(self, text: str):
        """헤더 텍스트 설정"""
        self._header.setText(text)

    def add_song(self, index: int, title: str, artist: str, album: str,
                 folder_name: str, duration: str, file_path: str, 
                 audio_format: str = None, cover_path: str = None):
        """곡 추가"""
        row = self._table.rowCount()
        self._table.insertRow(row)

        # 체크박스 아이템 (첫 번째 컬럼)
        check_item = QTableWidgetItem()
        check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        check_item.setCheckState(Qt.Unchecked)
        check_item.setData(Qt.UserRole, file_path)  # 파일 경로 저장
        self._table.setItem(row, 0, check_item)

        # 번호 컬럼
        num_item = QTableWidgetItem(str(index))
        num_item.setFlags(num_item.flags() & ~Qt.ItemIsEditable)
        self._table.setItem(row, 1, num_item)

        # 제목, 아티스트, 앨범
        title_item = QTableWidgetItem(title)
        title_item.setFlags(title_item.flags() & ~Qt.ItemIsEditable)
        self._table.setItem(row, 2, title_item)

        artist_item = QTableWidgetItem(artist)
        artist_item.setFlags(artist_item.flags() & ~Qt.ItemIsEditable)
        self._table.setItem(row, 3, artist_item)

        album_item = QTableWidgetItem(album)
        album_item.setFlags(album_item.flags() & ~Qt.ItemIsEditable)
        self._table.setItem(row, 4, album_item)

        # 포맷 배지 컬럼 (색상 적용)
        fmt = audio_format.upper() if audio_format else "?"
        color = self._format_colors.get(fmt, "#888888")
        format_item = QTableWidgetItem(fmt)
        format_item.setFlags(format_item.flags() & ~Qt.ItemIsEditable)
        format_item.setTextAlignment(Qt.AlignCenter)
        format_item.setForeground(QBrush(QColor(color)))
        self._table.setItem(row, 5, format_item)

        # 폴더, 시간
        folder_item = QTableWidgetItem(folder_name)
        folder_item.setFlags(folder_item.flags() & ~Qt.ItemIsEditable)
        self._table.setItem(row, 6, folder_item)

        duration_item = QTableWidgetItem(duration)
        duration_item.setFlags(duration_item.flags() & ~Qt.ItemIsEditable)
        self._table.setItem(row, 7, duration_item)

    def clear_songs(self):
        """모든 곡 제거"""
        self._table.setRowCount(0)
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
            self._selection_count_label.setText(f"({count} selected)")
            self._delete_selected_btn.setEnabled(True)
        else:
            self._selection_count_label.setText("")
            self._delete_selected_btn.setEnabled(False)

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

    def _switch_view(self, view_type: str):
        """뷰 모드 전환 (list/table)"""
        if view_type == "list":
            self._list_view_btn.setChecked(True)
            self._table_view_btn.setChecked(False)
            # List 뷰: 간소화된 컬럼만 표시
            self._table.setColumnHidden(1, True)   # # 숨김
            self._table.setColumnHidden(4, True)   # 앨범 숨김
            self._table.setColumnHidden(6, True)   # 폴더 숨김
        else:
            self._list_view_btn.setChecked(False)
            self._table_view_btn.setChecked(True)
            # Table 뷰: 모든 컬럼 표시
            self._table.setColumnHidden(1, False)
            self._table.setColumnHidden(4, False)
            self._table.setColumnHidden(6, False)
        logger.debug(f"뷰 모드 전환: {view_type}")
