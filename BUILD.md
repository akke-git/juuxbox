# JuuxBox 빌드 가이드

## Windows 실행 파일(.exe) 빌드 방법

### 사전 요구사항 (빌드 PC)
- Python 3.10 이상
- pip (Python 패키지 관리자)
- Windows 10/11 (WSL 아님!)
- 모든 의존성 설치: `pip install -r juuxbox_app/requirements.txt`

---

## 방법 1: build.bat 사용 (권장)

```powershell
# Windows PowerShell 또는 CMD에서 실행
cd D:\path\to\juuxbox
.\build.bat
```

이 스크립트는 자동으로:
1. PyInstaller 설치 확인 및 설치
2. 이전 빌드 정리 (`dist/`, `build/` 삭제)
3. `JuuxBox.spec` 기반 빌드 실행
4. 빌드 성공 여부 확인

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
│   ├── index.html
│   ├── css\
│   └── js\
├── _internal\           # Python 런타임, 라이브러리
└── ...
```

---

## 다른 PC에서 실행하기

### 배포 방법
1. `dist\JuuxBox\` 폴더 전체를 ZIP으로 압축
2. 대상 PC에서 압축 해제 (경로에 **한글/특수문자 없는 곳**을 권장)
3. `JuuxBox.exe` 더블클릭으로 실행

---

## 필수 요구사항 (대상 PC)

### 1. Windows 10/11 (64-bit)

### 2. Microsoft Edge WebView2 런타임
대부분의 Windows 10/11에는 기본 설치되어 있음.  
설치되어 있지 않으면:
- 다운로드: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
- **Evergreen Bootstrapper** 또는 **Evergreen Standalone Installer** 중 선택

### 3. Visual C++ 재배포 가능 패키지 (중요!)
Python 3.10 이상의 PyInstaller 빌드는 **Visual C++ Redistributable**이 필요합니다.

#### 설치 여부 확인 방법
1. `제어판` → `프로그램 및 기능`
2. "Microsoft Visual C++ 2015-2022 Redistributable" 항목 확인

#### 설치되어 있지 않은 경우
다운로드: https://aka.ms/vs/17/release/vc_redist.x64.exe

> [!IMPORTANT]
> Python 라이브러리가 없는 깨끗한 PC에서는 **VC++ Redistributable이 반드시 필요**합니다!  
> 설치하지 않으면 실행 시 `VCRUNTIME140.dll` 오류가 발생할 수 있습니다.

### 4. FFmpeg (선택 사항 - M4A/AAC 재생용)
MP3, FLAC, WAV는 FFmpeg 없이 재생 가능하지만, **M4A 파일**을 재생하려면 FFmpeg 필요.

#### FFmpeg 설치 방법 (옵션 A)
```powershell
# winget 사용
winget install FFmpeg

# 또는 chocolatey 사용
choco install ffmpeg
```

#### FFmpeg 포함 배포 (옵션 B - 권장)
`ffmpeg.exe`를 JuuxBox 폴더에 함께 복사:
```
JuuxBox\
├── JuuxBox.exe
├── ffmpeg.exe          # FFmpeg 실행 파일 추가
├── webui\
└── _internal\
```

---

## 빌드 후 테스트 체크리스트

배포 전에 **반드시** 다음을 확인하세요:

### 1. 로컬 빌드 PC에서 테스트
- [ ] `dist\JuuxBox\JuuxBox.exe` 실행 확인
- [ ] MP3 파일 추가 및 재생
- [ ] FLAC 파일 재생
- [ ] M4A 파일 재생 (FFmpeg 있는 경우)
- [ ] 한글 경로 파일 재생 확인
- [ ] YouTube 검색 기능 확인
- [ ] 데이터베이스 생성 확인 (`juuxbox.db` 파일 생성됨)

### 2. 깨끗한 테스트 PC에서 확인 (중요!)
- [ ] Python 미설치 상태에서 실행
- [ ] VC++ Redistributable 설치 확인
- [ ] Edge WebView2 설치 확인
- [ ] 첫 실행 시 데이터베이스 자동 생성 확인
- [ ] 모든 기능 정상 작동 확인

### 3. 파일 경로 테스트
- [ ] 영문 경로에서 실행
- [ ] 한글 경로에서 실행 (예: `C:\내문서\JuuxBox\`)
- [ ] 공백 포함 경로에서 실행 (예: `C:\Program Files\JuuxBox\`)

---

## 문제 해결

### 1. Edge WebView2 런타임 오류
**증상**: "WebView2 runtime is not installed" 오류

**해결**:
- https://developer.microsoft.com/en-us/microsoft-edge/webview2/ 에서 다운로드
- Evergreen Standalone Installer 설치 권장

---

### 2. VCRUNTIME140.dll 오류
**증상**: "The program can't start because VCRUNTIME140.dll is missing"

**해결**:
- Visual C++ Redistributable 설치 필요
- https://aka.ms/vs/17/release/vc_redist.x64.exe

---

### 3. 데이터베이스 생성 실패
**증상**: "Unable to open database file" 오류

**원인**: 
- 실행 파일 경로에 쓰기 권한 없음
- 경로에 특수문자/한글 포함

**해결**:
1. JuuxBox를 쓰기 가능한 폴더에 설치 (예: `C:\JuuxBox\`)
2. 관리자 권한으로 실행하지 말 것 (일반 사용자 권한으로 실행)

> [!NOTE]
> 데이터베이스(`juuxbox.db`)는 첫 실행 시 `JuuxBox.exe`와 같은 폴더에 자동 생성됩니다.

---

### 4. 한글 경로 MP3 재생 실패
**증상**: 한글이 포함된 파일 경로의 음악이 재생되지 않음

**해결**:
- Python 3.10+ 버전의 miniaudio 라이브러리 사용 확인
- `JuuxBox.spec`의 `hiddenimports`에 `miniaudio` 포함 확인

---

### 5. 빌드 실패 시
```powershell
# 캐시 정리 후 재빌드
cd juuxbox_app
rmdir /s /q build dist
pyinstaller JuuxBox.spec --clean
```

---

### 6. Hidden import 오류
**증상**: 빌드는 성공하지만 실행 시 "ModuleNotFoundError" 발생

**해결**:
`JuuxBox.spec` 파일의 `hiddenimports` 리스트에 누락된 모듈 추가

현재 포함된 모듈:
- `miniaudio`, `mutagen` (오디오)
- `webview.platforms.edgechromium` (UI)
- `pythonnet`, `clr_loader` (Windows 통합)

---

## 배포 파일 구조

최종 배포 시 다음 구조를 유지하세요:

```
JuuxBox_v1.0/
├── JuuxBox.exe          # 메인 실행 파일
├── ffmpeg.exe           # (선택) M4A 재생용
├── README.txt           # 사용자 안내문
├── webui/               # 웹 UI 리소스 (자동 포함됨)
│   ├── index.html
│   ├── css/
│   └── js/
└── _internal/           # Python 런타임 (자동 포함됨)
    ├── python310.dll
    ├── (기타 라이브러리들)
    └── ...
```

첫 실행 후 자동 생성:
```
JuuxBox_v1.0/
├── juuxbox.db           # SQLite 데이터베이스 (자동 생성)
└── logs/                # 로그 폴더 (선택적)
```

---

## 배포 권장사항

### 버전 관리
1. 빌드 시 버전 번호를 폴더명에 포함: `JuuxBox_v1.0.0.zip`
2. `README.txt` 파일 포함 (시스템 요구사항 명시)

### README.txt 예시
```
JuuxBox v1.0.0 - Hi-Fi Music Player
=====================================

시스템 요구사항:
- Windows 10/11 (64-bit)
- Microsoft Edge WebView2 런타임
- Visual C++ 2015-2022 Redistributable (x64)

선택 사항:
- FFmpeg (M4A 파일 재생용)

실행 방법:
1. 전체 폴더를 원하는 위치에 압축 해제
2. JuuxBox.exe 더블클릭

문제 발생 시:
- WebView2 설치: https://go.microsoft.com/fwlink/?linkid=2124701
- VC++ Redistributable 설치: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

---

## 주의사항

> [!WARNING]
> - **WSL에서 빌드하면 Linux용 바이너리가 생성됨!**
> - **반드시 Windows PowerShell/CMD에서 빌드할 것**

> [!CAUTION]
> - 빌드 후 `dist\JuuxBox\` **폴더 전체**가 필요 (exe 파일만 복사하면 안 됨!)
> - `_internal/` 폴더와 `webui/` 폴더도 함께 배포해야 함

> [!TIP]
> - 배포 전 깨끗한 가상 머신(VM)에서 테스트 권장
> - 한글 경로 지원 확인 필수
> - 첫 실행 시 데이터베이스가 자동 생성되는지 확인
