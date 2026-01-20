"""
Detail View
===========
플레이 중인 음악의 상세 화면 (전체화면)
- 참조 디자인: Music_Sample/screen_1.jpg
"""

import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QSlider, QSizePolicy,
    QCheckBox, QListWidget, QListWidgetItem, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QUrl, QThread, QObject
from PySide6.QtGui import QPixmap, QFont, QDesktopServices

# WebEngineView는 선택적 (일부 환경에서 미지원)
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    QWebEngineView = None

logger = logging.getLogger(__name__)


class DetailView(QWidget):
    """
    음악 상세 뷰 (전체화면)
    
    Layout (참조 이미지 기반):
    ┌──────────────────────────────────────────────────────┐
    │  ←                                                   │
    ├─────────────────────────┬────────────────────────────┤
    │                         │                            │
    │      ┌─────────┐        │   🎵 기본 정보             │
    │      │ Album   │        │   🎤 아티스트 정보         │
    │      │  Art    │        │   🎧 오디오 정보           │
    │      │(Resize) │        │                            │
    │      └─────────┘        │   📺 YouTube 가져오기      │
    │                         │                            │
    │    Plastic Flower       │                            │
    │       박정현             │                            │
    │       Op.4              │                            │
    │                         │                            │
    │   ━━━━━━━━━○━━━━━━━     │                            │
    │   3:35   M4A   -5:05    │                            │
    │                         │                            │
    │      ⏸   ⏹   ⏭         │                            │
    │                         │                            │
    │  장르: Ballad | 44.1kHz │                            │
    │  작곡: 박정현 | Stereo  │                            │
    └─────────────────────────┴────────────────────────────┘
    """

    back_clicked = Signal()
    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    next_clicked = Signal()
    prev_clicked = Signal()
    seek_changed = Signal(int)
    youtube_clicked = Signal()

    def __init__(self):
        super().__init__()
        self._current_track = {}
        self._is_playing = False
        self._duration_seconds = 0
        # YouTube 관련 속성 초기화
        self._web_available = False
        self._current_title = ""
        self._current_artist = ""
        self._current_album = ""
        self._search_results = []
        self._selected_video_url = ""
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        # 전체 화면 그라데이션 배경
        self.setStyleSheet("""
            DetailView {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(60, 80, 100, 220),
                    stop:0.4 rgba(35, 45, 55, 240),
                    stop:1 rgba(20, 20, 25, 255)
                );
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 상단: 뒤로가기 버튼
        header = self._create_header()
        main_layout.addWidget(header)

        # 본문: 좌우 분할
        content = QWidget()
        content.setStyleSheet("background: transparent;")  # 부모 그라데이션 상속
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 좌측: 새로운 디자인
        left_panel = self._create_left_panel()
        content_layout.addWidget(left_panel, 1)

        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: rgba(60, 60, 60, 100);")
        separator.setFixedWidth(1)
        content_layout.addWidget(separator)

        # 우측: 메타데이터 그룹 + YouTube
        right_panel = self._create_right_panel()
        content_layout.addWidget(right_panel, 1)

        main_layout.addWidget(content, 1)

    def _create_header(self) -> QWidget:
        """상단 헤더 (뒤로가기)"""
        header = QWidget()
        header.setFixedHeight(50)
        header.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)

        # 뒤로가기 버튼 (< 스타일)
        back_btn = QPushButton("<")
        back_btn.setFixedSize(40, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                font-size: 24px;
                font-weight: 300;
            }
            QPushButton:hover {
                color: #1DB954;
            }
        """)
        back_btn.clicked.connect(self.back_clicked.emit)
        layout.addWidget(back_btn)
        layout.addStretch()

        return header

    def _create_left_panel(self) -> QWidget:
        """좌측 패널: 앨범아트 + 정보 + 프로그레스 + 컨트롤 + 메타 요약"""
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")  # 부모 그라데이션 상속
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 20, 40, 30)
        layout.setSpacing(12)

        # 앨범 아트 (1.5배 크게, 윈도우 크기에 맞게 조절)
        self._album_art = QLabel()
        self._album_art.setMinimumSize(350, 350)
        self._album_art.setMaximumSize(700, 700)
        self._album_art.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._album_art.setStyleSheet("""
            background-color: #282828;
            border-radius: 8px;
        """)
        self._album_art.setAlignment(Qt.AlignCenter)
        self._album_art.setText("🎵")
        font = self._album_art.font()
        font.setPixelSize(80)
        self._album_art.setFont(font)
        self._album_art.setScaledContents(False)
        layout.addWidget(self._album_art, 1, Qt.AlignCenter)

        # 곡 정보
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(4)
        info_layout.setContentsMargins(0, 0, 0, 0)

        # 제목 (큰 폰트)
        self._title_label = QLabel("No Track")
        self._title_label.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: 600;")
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setWordWrap(True)
        info_layout.addWidget(self._title_label)

        # 아티스트
        self._artist_label = QLabel("")
        self._artist_label.setStyleSheet("color: #B3B3B3; font-size: 14px;")
        self._artist_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self._artist_label)

        # 앨범
        self._album_label = QLabel("")
        self._album_label.setStyleSheet("color: #808080; font-size: 13px;")
        self._album_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self._album_label)

        layout.addWidget(info_widget)

        # 프로그레스 바
        progress_widget = self._create_progress_bar()
        layout.addWidget(progress_widget)

        # 재생 컨트롤
        controls = self._create_controls()
        layout.addWidget(controls)

        # 메타 정보 요약 (2줄)
        meta_summary = self._create_meta_summary()
        layout.addWidget(meta_summary)

        return panel

    def _create_progress_bar(self) -> QWidget:
        """프로그레스 바 + 시간"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(6)
        layout.setContentsMargins(40, 16, 40, 0)  # 좌우 여백 크게

        # 슬라이더 (더 두껍게)
        self._progress_slider = QSlider(Qt.Horizontal)
        self._progress_slider.setRange(0, 1000)
        self._progress_slider.setValue(0)
        self._progress_slider.setFixedHeight(20)  # 슬라이더 전체 높이
        self._progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: rgba(80, 80, 80, 150);
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: rgba(200, 200, 200, 200);
                border-radius: 3px;
            }
        """)
        self._progress_slider.sliderMoved.connect(self._on_slider_moved)
        layout.addWidget(self._progress_slider)

        # 시간 + 포맷
        time_row = QHBoxLayout()
        time_row.setContentsMargins(0, 0, 0, 0)

        self._current_time_label = QLabel("0:00")
        self._current_time_label.setStyleSheet("color: #B3B3B3; font-size: 11px;")
        time_row.addWidget(self._current_time_label)

        time_row.addStretch()

        self._format_tag = QLabel("")
        self._format_tag.setStyleSheet("color: #808080; font-size: 11px;")
        time_row.addWidget(self._format_tag)

        time_row.addStretch()

        self._remaining_time_label = QLabel("-0:00")
        self._remaining_time_label.setStyleSheet("color: #B3B3B3; font-size: 11px;")
        time_row.addWidget(self._remaining_time_label)

        layout.addLayout(time_row)

        return widget

    def _create_controls(self) -> QWidget:
        """재생 컨트롤 버튼들 (이미지 참조 스타일)"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(32)
        layout.setContentsMargins(0, 8, 0, 8)

        ctrl_btn_style = """
            QPushButton {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                font-size: 28px;
            }
            QPushButton:hover {
                color: #1DB954;
            }
        """

        # 일시정지/재생
        self._play_btn = QPushButton("▐▐")  # 일시정지 모양
        self._play_btn.setFixedSize(56, 56)
        self._play_btn.setStyleSheet(ctrl_btn_style + "QPushButton { font-size: 24px; }")
        self._play_btn.clicked.connect(self._on_play_clicked)
        layout.addWidget(self._play_btn)

        # 정지
        stop_btn = QPushButton("■")
        stop_btn.setFixedSize(56, 56)
        stop_btn.setStyleSheet(ctrl_btn_style)
        stop_btn.clicked.connect(self.stop_clicked.emit)
        layout.addWidget(stop_btn)

        # 다음
        next_btn = QPushButton("▶▶")
        next_btn.setFixedSize(56, 56)
        next_btn.setStyleSheet(ctrl_btn_style + "QPushButton { font-size: 20px; }")
        next_btn.clicked.connect(self.next_clicked.emit)
        layout.addWidget(next_btn)

        return widget

    def _create_meta_summary(self) -> QWidget:
        """메타 정보 1줄 요약 (포맷 | 샘플레이트 | 비트덱스 | 비트레이트)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 4, 0, 0)

        # 1줄: 포맷 | 샘플레이트 | 비트덱스 | 비트레이트
        self._meta_line1 = QLabel("")
        self._meta_line1.setStyleSheet("color: #9B9B9B; font-size: 11px;")
        self._meta_line1.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._meta_line1)

        return widget

    def _create_right_panel(self) -> QWidget:
        """우측 패널: YouTube 검색 UI"""
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # === 상단: YouTube 검색 옵션 ===
        search_group = QWidget()
        search_layout = QVBoxLayout(search_group)
        search_layout.setSpacing(12)
        search_layout.setContentsMargins(0, 0, 0, 0)

        # 제목
        title_label = QLabel("📺 YouTube 검색")
        title_label.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 600;")
        search_layout.addWidget(title_label)

        # 체크박스 옵션
        checkbox_row = QHBoxLayout()
        checkbox_row.setSpacing(16)

        self._check_title = QCheckBox("곡명")
        self._check_title.setChecked(True)
        self._check_title.setStyleSheet("color: #B3B3B3; font-size: 12px;")
        checkbox_row.addWidget(self._check_title)

        self._check_artist = QCheckBox("가수명")
        self._check_artist.setChecked(True)
        self._check_artist.setStyleSheet("color: #B3B3B3; font-size: 12px;")
        checkbox_row.addWidget(self._check_artist)

        self._check_album = QCheckBox("앨범명")
        self._check_album.setChecked(False)
        self._check_album.setStyleSheet("color: #B3B3B3; font-size: 12px;")
        checkbox_row.addWidget(self._check_album)

        checkbox_row.addStretch()
        search_layout.addLayout(checkbox_row)

        # 검색 버튼
        self._youtube_search_btn = QPushButton("🔍 검색")
        self._youtube_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #CC0000;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        self._youtube_search_btn.clicked.connect(self._on_youtube_search)
        search_layout.addWidget(self._youtube_search_btn, 0, Qt.AlignLeft)

        layout.addWidget(search_group)

        # === 중간: 검색 결과 리스트 ===
        self._search_status = QLabel("")
        self._search_status.setStyleSheet("color: #808080; font-size: 11px;")
        layout.addWidget(self._search_status)

        self._result_list = QListWidget()
        self._result_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(30, 30, 30, 180);
                border: 1px solid #404040;
                border-radius: 6px;
                color: #FFFFFF;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:selected {
                background-color: rgba(255, 0, 0, 100);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 30);
            }
        """)
        self._result_list.setMinimumHeight(150)
        self._result_list.setMaximumHeight(200)
        self._result_list.itemClicked.connect(self._on_result_selected)
        layout.addWidget(self._result_list)

        # === 하단: 선택된 영상 정보 ===
        video_label = QLabel("🎥 선택된 영상")
        video_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 600; margin-top: 8px;")
        layout.addWidget(video_label)

        # 썸네일 + 영상 정보 표시
        preview_container = QWidget()
        preview_layout = QHBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(16)

        # 썸네일 이미지
        self._video_thumbnail = QLabel()
        self._video_thumbnail.setFixedSize(120, 68)
        self._video_thumbnail.setStyleSheet("""
            background-color: #282828;
            border-radius: 4px;
        """)
        self._video_thumbnail.setAlignment(Qt.AlignCenter)
        self._video_thumbnail.setText("📺")
        preview_layout.addWidget(self._video_thumbnail)

        # 영상 정보
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        self._video_title_label = QLabel("영상을 선택하세요")
        self._video_title_label.setStyleSheet("color: #FFFFFF; font-size: 12px; font-weight: 600;")
        self._video_title_label.setWordWrap(True)
        info_layout.addWidget(self._video_title_label)

        self._video_info_label = QLabel("")
        self._video_info_label.setStyleSheet("color: #9B9B9B; font-size: 10px;")
        info_layout.addWidget(self._video_info_label)

        info_layout.addStretch()
        preview_layout.addWidget(info_widget, 1)

        layout.addWidget(preview_container)

        # 안내 메시지
        notice = QLabel("💡 영상을 보려면 '브라우저로 열기' 버튼을 클릭하세요")
        notice.setStyleSheet("color: #666666; font-size: 10px; padding: 8px 0;")
        notice.setAlignment(Qt.AlignCenter)
        layout.addWidget(notice)

        layout.addStretch()

        # 외부 브라우저로 열기 버튼
        self._open_browser_btn = QPushButton("🌐 브라우저로 열기")
        self._open_browser_btn.setStyleSheet("""
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
                background-color: #333333;
                color: #666666;
            }
        """)
        self._open_browser_btn.setEnabled(False)
        self._open_browser_btn.clicked.connect(self._on_open_browser)
        layout.addWidget(self._open_browser_btn, 0, Qt.AlignRight)

        # 검색 결과 저장용
        self._search_results = []
        self._selected_video_url = ""

        return panel

    def _create_metadata_group(self, title: str, fields: list) -> QWidget:
        """메타데이터 그룹 위젯 생성"""
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # 그룹 제목
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 600;")
        layout.addWidget(title_label)

        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #3d3d3d;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # 필드들
        for label_text, attr_name in fields:
            row = QHBoxLayout()
            row.setSpacing(16)

            key_label = QLabel(label_text)
            key_label.setStyleSheet("color: #808080; font-size: 12px;")
            key_label.setFixedWidth(90)
            row.addWidget(key_label)

            value_label = QLabel("-")
            value_label.setStyleSheet("color: #FFFFFF; font-size: 12px;")
            value_label.setWordWrap(True)
            row.addWidget(value_label, 1)

            setattr(self, attr_name + "_label", value_label)

            layout.addLayout(row)

        return group

    def _on_play_clicked(self):
        """재생/일시정지 토글"""
        self._is_playing = not self._is_playing
        if self._is_playing:
            self._play_btn.setText("▐▐")  # 일시정지 모양
            self.play_clicked.emit()
        else:
            self._play_btn.setText("▶")  # 재생 모양
            self.pause_clicked.emit()

    def _on_slider_moved(self, value: int):
        """슬라이더 드래그"""
        if self._duration_seconds > 0:
            seek_seconds = int((value / 1000) * self._duration_seconds)
            self.seek_changed.emit(seek_seconds)

    def _format_time(self, seconds: float) -> str:
        """초를 M:SS 형식으로 변환"""
        if seconds is None or seconds < 0:
            return "0:00"
        mins, secs = divmod(int(seconds), 60)
        return f"{mins}:{secs:02d}"

    def set_progress(self, current_seconds: int, total_seconds: int):
        """재생 진행률 업데이트"""
        self._duration_seconds = total_seconds
        if total_seconds > 0:
            progress = int((current_seconds / total_seconds) * 1000)
            if not self._progress_slider.isSliderDown():
                self._progress_slider.setValue(progress)
            
            self._current_time_label.setText(self._format_time(current_seconds))
            remaining = total_seconds - current_seconds
            self._remaining_time_label.setText(f"-{self._format_time(remaining)}")

    def set_track_info(self, title: str = "", artist: str = "", album: str = "",
                       folder: str = "", audio_format: str = "", cover_path: str = None,
                       album_artist: str = "", track_number: int = 0, genre: str = "",
                       composer: str = "", conductor: str = "", performer: str = "",
                       duration_seconds: float = 0, sample_rate: int = 0,
                       bit_depth: int = 0, bitrate: int = 0, channels: int = 0):
        """트랙 정보 설정"""
        # 좌측 기본 정보
        self._title_label.setText(title or "Unknown")
        self._artist_label.setText(artist or "Unknown Artist")
        self._album_label.setText(album or "")
        self._format_tag.setText(audio_format.upper() if audio_format else "")

        # 앨범 아트 로드 (리사이즈 가능하게)
        if cover_path and Path(cover_path).exists():
            self._cover_pixmap = QPixmap(cover_path)
            self._update_album_art()
        else:
            self._cover_pixmap = None
            self._album_art.setPixmap(QPixmap())
            self._album_art.setText("🎵")

        # 메타 요약 1줄 (포맷 | 샘플레이트 | 비트뎁스 | 비트레이트)
        meta_parts = []
        if audio_format:
            meta_parts.append(audio_format.upper())
        if sample_rate and sample_rate > 0:
            sr_khz = sample_rate / 1000
            meta_parts.append(f"{sr_khz:.1f} kHz")
        if bit_depth:
            meta_parts.append(f"{bit_depth} bit")
        if bitrate and bitrate > 0:
            meta_parts.append(f"{bitrate} kbps")
        self._meta_line1.setText("  |  ".join(meta_parts) if meta_parts else "")

        # YouTube 검색용 현재 트랙 정보 저장
        self._current_title = title or ""
        self._current_artist = artist or ""
        self._current_album = album or ""

        # 재생 시간 설정
        self._duration_seconds = duration_seconds or 0
        if duration_seconds and duration_seconds > 0:
            mins, secs = divmod(int(duration_seconds), 60)
            self._remaining_time_label.setText(f"-{mins}:{secs:02d}")

        # YouTube 검색 결과 초기화 (UI 요소 존재 시에만)
        if hasattr(self, '_result_list'):
            self._result_list.clear()
        if hasattr(self, '_search_status'):
            self._search_status.setText("")
        if hasattr(self, '_video_title_label'):
            self._video_title_label.setText("영상을 선택하세요")
        if hasattr(self, '_video_info_label'):
            self._video_info_label.setText("")
        if hasattr(self, '_video_thumbnail'):
            self._video_thumbnail.setPixmap(QPixmap())
            self._video_thumbnail.setText("📺")
        if hasattr(self, '_open_browser_btn'):
            self._open_browser_btn.setEnabled(False)

        logger.debug(f"상세 뷰 트랙 정보 설정: {title}")

    def _update_album_art(self):
        """앨범 아트 리사이즈"""
        if hasattr(self, '_cover_pixmap') and self._cover_pixmap:
            size = min(self._album_art.width(), self._album_art.height(), 500)
            if size < 200:
                size = 200
            scaled = self._cover_pixmap.scaled(
                size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._album_art.setPixmap(scaled)
            self._album_art.setText("")

    def resizeEvent(self, event):
        """윈도우 리사이즈 시 앨범아트 업데이트"""
        super().resizeEvent(event)
        self._update_album_art()

    def set_playing_state(self, is_playing: bool):
        """재생 상태 동기화"""
        self._is_playing = is_playing
        if is_playing:
            self._play_btn.setText("▐▐")  # 일시정지
        else:
            self._play_btn.setText("▶")  # 재생

    def _on_youtube_search(self):
        """YouTube 검색 실행"""
        from utils.youtube_search import search_youtube, build_search_query, YOUTUBE_AVAILABLE
        
        if not YOUTUBE_AVAILABLE:
            self._search_status.setText("⚠️ youtube-search-python 라이브러리를 설치하세요")
            return
        
        # 검색어 조합
        query = build_search_query(
            title=self._current_title,
            artist=self._current_artist,
            album=self._current_album,
            use_title=self._check_title.isChecked(),
            use_artist=self._check_artist.isChecked(),
            use_album=self._check_album.isChecked()
        )
        
        if not query.strip():
            self._search_status.setText("⚠️ 검색할 항목을 선택하세요")
            return
        
        self._search_status.setText(f"🔍 검색 중: {query}")
        self._youtube_search_btn.setEnabled(False)
        self._result_list.clear()
        
        # 검색 실행 (백그라운드 스레드 권장하지만 간단히 동기 처리)
        try:
            results = search_youtube(query, limit=5)
            self._search_results = results
            
            if results:
                self._search_status.setText(f"✅ {len(results)}개 결과 (조회수 상위)")
                for video in results:
                    item_text = f"🎬 {video['title']}\n   {video['channel']} • {video['duration']} • {video['views']}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, video)
                    self._result_list.addItem(item)
            else:
                self._search_status.setText("❌ 검색 결과 없음")
                
        except Exception as e:
            self._search_status.setText(f"❌ 검색 오류: {e}")
            logger.error(f"YouTube 검색 오류: {e}")
        finally:
            self._youtube_search_btn.setEnabled(True)

    def _on_result_selected(self, item: QListWidgetItem):
        """검색 결과 선택 시 영상 정보 표시"""
        video = item.data(Qt.UserRole)
        if not video:
            return
        
        self._selected_video_url = video.get('url', '')
        
        # 영상 정보 표시
        self._video_title_label.setText(video.get('title', 'Unknown'))
        info_text = f"{video.get('channel', '')} • {video.get('duration', '')} • {video.get('views', '')}"
        self._video_info_label.setText(info_text)
        
        # 썸네일 로드 (비동기 권장하지만 간단히 동기 처리)
        thumbnail_url = video.get('thumbnail', '')
        if thumbnail_url:
            try:
                import urllib.request
                data = urllib.request.urlopen(thumbnail_url, timeout=3).read()
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                scaled = pixmap.scaled(120, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self._video_thumbnail.setPixmap(scaled)
                self._video_thumbnail.setText("")
            except Exception as e:
                logger.debug(f"썸네일 로드 실패: {e}")
                self._video_thumbnail.setText("📺")
        
        self._open_browser_btn.setEnabled(bool(self._selected_video_url))
        logger.info(f"YouTube 영상 선택: {video.get('title')}")

    def _on_open_browser(self):
        """외부 브라우저로 열기"""
        if self._selected_video_url:
            QDesktopServices.openUrl(QUrl(self._selected_video_url))
