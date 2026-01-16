# 🎵 JuuxBox - Hi-Fi Music Player

Windows 환경에서 WASAPI Exclusive 모드를 지원하는 하이파이 전용 뮤직 플레이어입니다.

## ✨ Features

- **Bit-Perfect 출력**: WASAPI Exclusive 모드로 오디오 믹서 우회
- **무손실 포맷 지원**: FLAC, WAV, ALAC, AIFF, DSD (DoP)
- **Sample Rate**: 44.1kHz ~ 768kHz
- **Bit-depth**: 16-bit ~ 32-bit
- **Spotify 스타일 UI**: 미니멀한 다크 테마
- **Gapless 재생**: 곡 전환 시 끊김 없는 재생

## 🛠️ Tech Stack

- **Python 3.11+**
- **PySide6** - Qt for Python GUI
- **miniaudio** - WASAPI 오디오 엔진
- **mutagen** - 메타데이터 파싱
- **SQLite** - 라이브러리 데이터베이스

## 🚀 Quick Start

```bash
# 의존성 설치
cd juuxbox_app
pip install -r requirements.txt

# 앱 실행
python run.py

# 음악 폴더 스캔 후 실행
python run.py --scan ~/Music
```

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | 재생 / 일시정지 |
| `←` / `→` | 이전 / 다음 곡 |
| `↑` / `↓` | 볼륨 조절 |
| `M` | 음소거 |
| `S` | 셔플 |
| `R` | 반복 |

## 📁 Project Structure

```
juuxbox_app/
├── run.py              # 앱 런처
├── main.py             # 진입점
├── app_controller.py   # UI-엔진 연결
├── audio/              # 오디오 엔진
├── ui/                 # Qt UI 컴포넌트
├── db/                 # SQLite 데이터베이스
├── utils/              # 유틸리티
└── resources/          # 스타일시트, 아이콘
```

## 📄 License

MIT License
