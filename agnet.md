# JuuxBox Hi-Fi Music Player

## 1. Project Overview

JuuxBox는 Windows 환경에서 DAC(Digital-to-Analog Converter)의 성능을 최대한 활용하기 위한 하이파이 전용 뮤직 플레이어입니다. Windows 오디오 믹서를 우회하는 Bit-Perfect(WASAPI Exclusive) 출력을 지원하며, 스포티파이의 미니멀한 UI 디자인을 지향합니다.

---

## 2. Core Architecture

### 2.1 Technology Stack

| Component | Technology | Version | Description |
|-----------|------------|---------|-------------|
| **Framework** | Python | 3.11+ | 메인 개발 언어 |
| **UI Framework** | PySide6 | 6.6+ | Qt for Python GUI 프레임워크 |
| **Audio Engine** | miniaudio | 1.1.1+ | WASAPI Exclusive 모드 지원 오디오 라이브러리 |
| **Database** | SQLite | 3.x | 음원 메타데이터 및 설정 저장 |
| **Metadata Parser** | mutagen | 1.47+ | 오디오 파일 태그 추출 |

> [!NOTE]
> ASIO는 사용하지 않으며, WASAPI Exclusive 모드만 지원합니다.

### 2.2 Audio Engine Specifications

#### 지원 오디오 포맷
| Format | Extension | Description |
|--------|-----------|-------------|
| FLAC | `.flac` | Free Lossless Audio Codec |
| WAV | `.wav` | Uncompressed PCM |
| ALAC | `.m4a` | Apple Lossless Audio Codec |
| AIFF | `.aiff` | Audio Interchange File Format |
| DSD | `.dsf`, `.dff` | DSD over PCM (DoP) 방식 지원 |

#### 오디오 스펙 지원 범위
| Spec | Range |
|------|-------|
| **Sample Rate** | 44.1kHz ~ 768kHz |
| **Bit-depth** | 16-bit ~ 32-bit |
| **DSD** | DSD64, DSD128, DSD256 (DoP 변환) |

### 2.3 Project Structure

```
juuxbox_app/
├── main.py                 # 애플리케이션 진입점
├── requirements.txt        # 의존성 목록
├── config.json             # 사용자 설정 파일
│
├── audio/                  # 오디오 엔진 모듈
│   ├── __init__.py
│   ├── engine.py           # 오디오 재생 엔진 (miniaudio)
│   ├── wasapi.py           # WASAPI Exclusive 제어
│   ├── decoder.py          # 오디오 디코딩 처리
│   └── gapless.py          # Gapless 재생 관리
│
├── ui/                     # Qt UI 컴포넌트
│   ├── __init__.py
│   ├── main_window.py      # 메인 윈도우
│   ├── sidebar.py          # 사이드바 (라이브러리, 플레이리스트)
│   ├── player_bar.py       # 하단 플레이어 바
│   ├── album_view.py       # 앨범 그리드 뷰
│   └── song_list.py        # 곡 목록 뷰
│
├── db/                     # 데이터베이스 레이어
│   ├── __init__.py
│   ├── models.py           # SQLite 모델 정의
│   ├── repository.py       # CRUD 함수
│   └── scanner.py          # 음원 스캔 및 태그 추출
│
├── utils/                  # 유틸리티
│   ├── __init__.py
│   ├── logger.py           # 로깅 설정
│   ├── config.py           # 설정 관리
│   └── helpers.py          # 공통 헬퍼 함수
│
├── resources/              # 리소스 파일
│   ├── icons/              # 아이콘 파일
│   ├── styles/             # QSS 스타일시트
│   │   └── spotify_dark.qss
│   └── fonts/              # 커스텀 폰트
│
└── tests/                  # 테스트 코드
    ├── __init__.py
    ├── test_audio_engine.py
    ├── test_database.py
    └── test_ui.py
```

---

## 3. Implementation Requirements

### A. Audio Engine (High Priority)

- **Bit-Perfect Output**
  - 시스템 기본 장치가 아닌, 사용자가 선택한 특정 오디오 장치(DAC)로 직접 스트리밍
  - WASAPI Exclusive 모드를 활성화하여 샘플링 레이트 변환(SRC) 방지

- **Gapless Playback**
  - 곡 전환 시 오디오 스트림 끊김 최소화
  - Pre-buffering 방식으로 다음 곡 준비

- **Real-time Info**
  - 현재 출력 중인 Bit-depth 및 Sample Rate를 엔진에서 실시간으로 피드백
  - UI에 `24bit/192kHz` 형태로 표시

### B. Functional Features

- **Library Scan**: 지정된 폴더의 음원을 스캔하여 아티스트/앨범별로 자동 분류
- **Playlist Management**: 현재 재생 목록(Queue) 관리 및 셔플/반복 기능
- **Volume Control**: 시스템 볼륨과 별개로 동작하는 정밀한 내부 소프트웨어 볼륨

---

## 4. UI/UX Design Specification (Spotify Style)

### Layout Structure

| Area | Position | Size | Description |
|------|----------|------|-------------|
| Sidebar | Left | 240px | Library, Playlists, Settings |
| Main View | Center | Flexible | Album Art Grid or Song List |
| Player Bar | Bottom | 90px | Track Info, Transport Controls, Audio Stats, Volume |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | 재생 / 일시정지 |
| `←` / `→` | 이전 곡 / 다음 곡 |
| `↑` / `↓` | 볼륨 증가 / 감소 |
| `M` | 음소거 토글 |
| `S` | 셔플 토글 |
| `R` | 반복 모드 변경 |
| `Ctrl+O` | 폴더 열기 |
| `Ctrl+Q` | 앱 종료 |

### QSS (Qt Style Sheets) Styling Guide

```css
/* 기본 배경 및 폰트 */
QMainWindow {
    background-color: #121212;
    color: #FFFFFF;
    font-family: 'Segoe UI', sans-serif;
}

/* 사이드바 및 섹션 구분 */
QFrame#Sidebar {
    background-color: #000000;
    border-right: 1px solid #282828;
}

/* 버튼 스타일 (스포티파이 그린 포인트) */
QPushButton#PlayButton {
    background-color: #1DB954;
    color: black;
    border-radius: 25px;
    font-weight: bold;
    padding: 10px;
}

QPushButton#PlayButton:hover {
    background-color: #1ed760;
    transform: scale(1.05);
}

/* 텍스트 스타일 */
QLabel#TrackTitle {
    font-size: 16px;
    font-weight: bold;
    color: #FFFFFF;
}

QLabel#ArtistName {
    font-size: 14px;
    color: #B3B3B3;
}

/* 하이파이 정보 태그 */
QLabel#AudioSpecTag {
    background-color: #282828;
    color: #1DB954;
    border: 1px solid #1DB954;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    font-family: 'Consolas';
}

/* 슬라이더(프로그레스 바) */
QSlider::groove:horizontal {
    border: 1px solid #262626;
    height: 4px;
    background: #404040;
    margin: 2px 0;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #FFFFFF;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}
```

---

## 5. Error Handling & Logging

### 5.1 Error Handling Strategy

| Error Type | Handling |
|------------|----------|
| **오디오 장치 연결 실패** | 사용 가능한 장치 목록 표시 후 재선택 유도 |
| **WASAPI Exclusive 모드 획득 실패** | 다른 앱이 장치 점유 중임을 알림, 재시도 버튼 제공 |
| **지원하지 않는 파일 포맷** | 해당 파일 스킵 및 로그 기록 |
| **Sample Rate 미지원 (DAC)** | 가장 가까운 지원 Sample Rate로 자동 리샘플링 경고 |
| **파일 읽기 실패** | 에러 토스트 표시 및 다음 곡 자동 재생 |

### 5.2 Logging Configuration

```python
# utils/logger.py 설정 예시
import logging

LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "juuxbox_app.log",
            "maxBytes": 5 * 1024 * 1024,  # 5MB
            "backupCount": 3,
            "formatter": "detailed"
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple"
        }
    },
    "loggers": {
        "audio": {"level": "DEBUG"},
        "ui": {"level": "INFO"},
        "db": {"level": "INFO"}
    }
}
```

| Log Level | Usage |
|-----------|-------|
| `DEBUG` | 오디오 엔진 상세 정보, 버퍼 상태 |
| `INFO` | 곡 재생 시작, 라이브러리 스캔 완료 |
| `WARNING` | 리샘플링 발생, 메타데이터 누락 |
| `ERROR` | 장치 연결 실패, 파일 디코딩 실패 |

---

## 6. Testing Strategy

### 6.1 Unit Tests

| Module | Test Coverage |
|--------|---------------|
| `audio/engine.py` | 재생, 일시정지, 정지, 탐색 기능 |
| `audio/decoder.py` | 각 포맷별 디코딩 정상 동작 |
| `db/scanner.py` | 메타데이터 추출 정확성 |
| `db/repository.py` | CRUD 작업 |

### 6.2 Integration Tests

- 오디오 엔진 ↔ UI 이벤트 연동
- 라이브러리 스캔 → DB 저장 → UI 표시 플로우
- Gapless 재생 연속성 검증

### 6.3 Test Commands

```bash
# 전체 테스트 실행
pytest tests/ -v

# 특정 모듈 테스트
pytest tests/test_audio_engine.py -v

# 커버리지 리포트
pytest tests/ --cov=juuxbox_app --cov-report=html
```

---

## 7. Settings & Configuration

### 7.1 Configuration File Structure

설정은 `config.json` 파일에 저장됩니다:

```json
{
  "audio": {
    "output_device": "USB DAC",
    "exclusive_mode": true,
    "software_volume": 100,
    "gapless_enabled": true
  },
  "library": {
    "scan_paths": [
      "D:/Music",
      "E:/FLAC Collection"
    ],
    "auto_scan_on_startup": true
  },
  "ui": {
    "theme": "spotify_dark",
    "language": "ko",
    "show_audio_specs": true,
    "album_art_cache_size_mb": 500
  },
  "playback": {
    "shuffle": false,
    "repeat_mode": "off",
    "remember_position": true
  }
}
```

### 7.2 Default Settings

| Setting | Default Value | Description |
|---------|---------------|-------------|
| `output_device` | System Default | 출력 장치 (첫 실행 시 선택 필요) |
| `exclusive_mode` | `true` | WASAPI Exclusive 모드 사용 |
| `software_volume` | `100` | 소프트웨어 볼륨 (0-100) |
| `auto_scan_on_startup` | `true` | 시작 시 자동 스캔 |
| `album_art_cache_size_mb` | `500` | 앨범 아트 캐시 크기 |

---

## 8. Development Roadmap (Milestones)

### Phase 1: Audio Engine Test ✅
- [ ] miniaudio를 활용해 특정 장치(WASAPI Exclusive)로 무손실 음원 재생 성공 확인
- [ ] 지원 Sample Rate 및 Bit-depth 확인 로직 구현

### Phase 2: Database & Scanner
- [ ] mutagen을 이용한 음원 태그 추출 구현
- [ ] SQLite 데이터베이스 스키마 설계 및 구현
- [ ] 폴더 스캔 및 변경 감지 로직

### Phase 3: Spotify-like UI Implementation
- [ ] QSS 가이드를 적용한 메인 윈도우 구현
- [ ] 사이드바 (라이브러리, 플레이리스트) 구현
- [ ] 하단 플레이어 바 UI 완성
- [ ] 앨범 그리드 뷰 및 곡 목록 뷰 구현

### Phase 4: Integration & Optimization
- [ ] UI 이벤트와 오디오 엔진 연결
- [ ] Gapless 재생 최적화
- [ ] 앨범 아트 캐싱 시스템 구현

### Phase 5: Polish & Release
- [ ] 에러 핸들링 및 로깅 완성
- [ ] 키보드 단축키 구현
- [ ] 시스템 트레이 지원
- [ ] 설치 패키지 생성 (PyInstaller)

---

## 9. Future Enhancements (Optional)

> [!TIP]
> 아래 기능들은 기본 버전 완성 후 추가 고려 사항입니다.

- **시스템 트레이**: 백그라운드 재생 시 트레이 아이콘 및 미니 컨트롤
- **업샘플링 옵션**: SoX 기반 업샘플링 (하이파이 유저 선택 기능)
- **다국어 지원 (i18n)**: Qt 번역 시스템 활용
- **Last.fm Scrobbling**: 재생 기록 연동
- **리모트 컨트롤**: 모바일 앱을 통한 원격 제어