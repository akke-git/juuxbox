"""
Player Bar
==========
하단 플레이어 바 (재생 컨트롤, 트랙 정보, 오디오 스펙)
"""

import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSlider, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

logger = logging.getLogger(__name__)


class PlayerBar(QFrame):
    """
    하단 플레이어 바
    
    Layout:
    ┌────────────┬────────────────────┬────────────┐
    │ Track Info │ Transport Controls │ Volume/Spec│
    │  (left)    │     (center)       │  (right)   │
    └────────────┴────────────────────┴────────────┘
    """

    # 시그널
    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    next_clicked = Signal()
    prev_clicked = Signal()
    seek_changed = Signal(int)  # position in seconds
    volume_changed = Signal(int)  # 0-100

    def __init__(self):
        super().__init__()
        self._is_playing = False
        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        self.setStyleSheet("""
            PlayerBar {
                background-color: #181818;
                border-top: 1px solid #282828;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        # 왼쪽: 트랙 정보
        self._track_info = self._create_track_info()
        layout.addWidget(self._track_info, 1)

        # 중앙: 재생 컨트롤
        self._controls = self._create_controls()
        layout.addWidget(self._controls, 2)

        # 오른쪽: 볼륨 & 오디오 스펙
        self._right_section = self._create_right_section()
        layout.addWidget(self._right_section, 1)

    def _create_track_info(self) -> QWidget:
        """트랙 정보 영역"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 앨범 아트 (플레이스홀더)
        self._album_art = QLabel("🎵")
        self._album_art.setFixedSize(56, 56)
        self._album_art.setStyleSheet("""
            background-color: #282828;
            border-radius: 4px;
            font-size: 24px;
        """)
        self._album_art.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._album_art)

        # 텍스트 정보
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self._title_label = QLabel("재생 중인 곡 없음")
        self._title_label.setObjectName("TrackTitle")
        self._title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        text_layout.addWidget(self._title_label)

        self._artist_label = QLabel("")
        self._artist_label.setObjectName("ArtistName")
        self._artist_label.setStyleSheet("font-size: 12px; color: #B3B3B3;")
        text_layout.addWidget(self._artist_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        return widget

    def _create_controls(self) -> QWidget:
        """재생 컨트롤 영역"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(4)

        # 버튼 행
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(12)

        # 공통 버튼 스타일
        ctrl_btn_style = """
            QPushButton {
                background-color: transparent;
                color: #B3B3B3;
                border: none;
                font-size: 16px;
                font-family: 'Segoe UI Symbol', 'Arial';
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        """

        # 이전 곡
        prev_btn = QPushButton("⏮")
        prev_btn.setFixedSize(40, 40)
        prev_btn.setStyleSheet(ctrl_btn_style + "QPushButton { font-size: 20px; }")
        prev_btn.setToolTip("이전 곡 (←)")
        prev_btn.clicked.connect(self.prev_clicked.emit)
        btn_layout.addWidget(prev_btn)

        # 정지
        self._stop_btn = QPushButton("⏹")
        self._stop_btn.setFixedSize(40, 40)
        self._stop_btn.setStyleSheet(ctrl_btn_style + "QPushButton { font-size: 18px; }")
        self._stop_btn.setToolTip("정지 (S)")
        self._stop_btn.clicked.connect(self.stop_clicked.emit)
        btn_layout.addWidget(self._stop_btn)

        # 재생/일시정지 (메인 버튼)
        self._play_btn = QPushButton("▶")
        self._play_btn.setObjectName("PlayButton")
        self._play_btn.setFixedSize(52, 52)
        self._play_btn.setStyleSheet("""
            QPushButton#PlayButton {
                background-color: #1DB954;
                color: #000000;
                border-radius: 26px;
                font-size: 22px;
                font-family: 'Segoe UI Symbol', 'Arial';
            }
            QPushButton#PlayButton:hover {
                background-color: #1ed760;
                transform: scale(1.05);
            }
        """)
        self._play_btn.setToolTip("재생/일시정지 (Space)")
        self._play_btn.clicked.connect(self.toggle_play)
        btn_layout.addWidget(self._play_btn)

        # 다음 곡
        next_btn = QPushButton("⏭")
        next_btn.setFixedSize(40, 40)
        next_btn.setStyleSheet(ctrl_btn_style + "QPushButton { font-size: 20px; }")
        next_btn.setToolTip("다음 곡 (→)")
        next_btn.clicked.connect(self.next_clicked.emit)
        btn_layout.addWidget(next_btn)

        main_layout.addLayout(btn_layout)

        # 프로그레스 바
        progress_layout = QHBoxLayout()

        self._current_time = QLabel("0:00")
        self._current_time.setStyleSheet("color: #B3B3B3; font-size: 11px;")
        progress_layout.addWidget(self._current_time)

        self._progress_slider = QSlider(Qt.Horizontal)
        self._progress_slider.setRange(0, 1000)  # 더 세밀한 제어를 위해 1000 단위
        self._progress_slider.setValue(0)
        self._progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #404040;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #1DB954;
                border-radius: 2px;
            }
        """)
        self._progress_slider.sliderMoved.connect(self._on_slider_moved)
        self._progress_slider.sliderPressed.connect(self._on_slider_pressed)
        progress_layout.addWidget(self._progress_slider, 1)

        self._total_time = QLabel("0:00")
        self._total_time.setStyleSheet("color: #B3B3B3; font-size: 11px;")
        progress_layout.addWidget(self._total_time)

        main_layout.addLayout(progress_layout)

        return widget

    def _create_right_section(self) -> QWidget:
        """오른쪽 섹션 (볼륨, 오디오 스펙)"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignRight)

        # 오디오 스펙 태그
        self._spec_label = QLabel("")
        self._spec_label.setObjectName("AudioSpecTag")
        self._spec_label.setStyleSheet("""
            background-color: #282828;
            color: #1DB954;
            border: 1px solid #1DB954;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 10px;
            font-family: 'Consolas';
        """)
        layout.addWidget(self._spec_label)

        # 볼륨
        volume_icon = QLabel("🔊")
        layout.addWidget(volume_icon)

        self._volume_slider = QSlider(Qt.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(100)
        self._volume_slider.setFixedWidth(100)
        self._volume_slider.valueChanged.connect(self.volume_changed.emit)
        layout.addWidget(self._volume_slider)

        return widget

    def toggle_play(self):
        """재생/일시정지 토글"""
        self._is_playing = not self._is_playing
        if self._is_playing:
            # 재생 상태 → 일시정지 버튼 표시
            self._play_btn.setText("⏸")
            self.play_clicked.emit()
        else:
            # 정지/일시정지 상태 → 재생 버튼 표시
            self._play_btn.setText("▶")
            self.pause_clicked.emit()

    def set_track_info(self, title: str, artist: str, album_art_path: str = None):
        """트랙 정보 설정"""
        self._title_label.setText(title)
        self._artist_label.setText(artist)
        
        # 앨범 아트 로드
        if album_art_path and Path(album_art_path).exists():
            pixmap = QPixmap(album_art_path).scaled(
                56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._album_art.setPixmap(pixmap)
            self._album_art.setText("")  # 이모지 제거
        else:
            self._album_art.setPixmap(QPixmap())  # 픽스맵 클리어
            self._album_art.setText("🎵")

    def set_audio_spec(self, bit_depth: int, sample_rate: int):
        """오디오 스펙 표시"""
        if sample_rate >= 1000:
            rate_str = f"{sample_rate // 1000}kHz"
        else:
            rate_str = f"{sample_rate}Hz"
        self._spec_label.setText(f"{bit_depth}bit/{rate_str}")

    def set_progress(self, current_seconds: int, total_seconds: int):
        """재생 진행률 업데이트"""
        self._total_seconds = total_seconds
        if total_seconds > 0:
            progress = int((current_seconds / total_seconds) * 1000)
            # 슬라이더가 드래그 중이 아닐 때만 업데이트
            if not self._progress_slider.isSliderDown():
                self._progress_slider.setValue(progress)

        self._current_time.setText(self._format_time(current_seconds))
        self._total_time.setText(self._format_time(total_seconds))

    def _on_slider_moved(self, value: int):
        """슬라이더 드래그 시"""
        if hasattr(self, '_total_seconds') and self._total_seconds > 0:
            seek_seconds = int((value / 1000) * self._total_seconds)
            self._current_time.setText(self._format_time(seek_seconds))
            self.seek_changed.emit(seek_seconds)

    def _on_slider_pressed(self):
        """슬라이더 클릭 시"""
        pass  # sliderMoved에서 처리

    @staticmethod
    def _format_time(seconds: int) -> str:
        """초를 M:SS 형식으로 변환"""
        m, s = divmod(seconds, 60)
        return f"{m}:{s:02d}"
