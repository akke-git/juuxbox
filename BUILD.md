# JuuxBox 빌드 가이드

## Windows 실행 파일(.exe) 빌드 방법

### 사전 요구사항
- Python 3.10 이상
- pip (Python 패키지 관리자)
- Windows 10/11

---

## 방법 1: build.bat 사용 (간단)

```powershell
# Windows PowerShell 또는 CMD에서 실행
cd D:\path\to\juuxbox
.\build.bat
```

---

## 방법 2: 수동 빌드

### 1. PyInstaller 설치
```powershell
pip install pyinstaller
```

### 2. 프로젝트 폴더로 이동
```powershell
cd D:\path\to\juuxbox\juuxbox_app
```

### 3. 빌드 실행
```powershell
pyinstaller JuuxBox.spec --clean
```

### 4. 결과물 확인
```
juuxbox_app\dist\JuuxBox\
├── JuuxBox.exe          # 메인 실행 파일
├── webui\               # 웹 UI 파일들
├── _internal\           # Python 런타임, 라이브러리
└── ...
```

---

## 다른 PC에서 실행하기

### 배포 방법
1. `dist\JuuxBox\` 폴더 전체를 ZIP으로 압축
2. 다른 PC에서 압축 해제
3. `JuuxBox.exe` 실행

### 필수 요구사항 (대상 PC)
| 항목 | 설명 |
|------|------|
| Windows 10/11 | Edge WebView2 런타임 필요 (대부분 기본 설치됨) |
| FFmpeg | M4A 파일 재생 시 필요 (선택) |

### FFmpeg 설치 (M4A 재생용)
```powershell
# winget 사용
winget install FFmpeg

# 또는 chocolatey 사용
choco install ffmpeg
```

### FFmpeg 포함 배포 (선택)
M4A 재생이 필요하면 `ffmpeg.exe`를 JuuxBox 폴더에 함께 복사:
```
JuuxBox\
├── JuuxBox.exe
├── ffmpeg.exe          # FFmpeg 실행 파일 추가
├── webui\
└── _internal\
```

---

## 문제 해결

### Edge WebView2 런타임 오류
WebView2 런타임이 없는 경우:
- https://developer.microsoft.com/en-us/microsoft-edge/webview2/ 에서 다운로드

### 빌드 실패 시
```powershell
# 캐시 정리 후 재빌드
pyinstaller JuuxBox.spec --clean
```

### Hidden import 오류
`JuuxBox.spec` 파일의 `hiddenimports` 리스트에 누락된 모듈 추가

---

## 주의사항

- **WSL에서 빌드하면 Linux용** 바이너리가 생성됨
- **반드시 Windows PowerShell/CMD**에서 빌드할 것
- 빌드 후 `dist\JuuxBox\` 폴더 전체가 필요 (exe 파일만 복사하면 안 됨)
