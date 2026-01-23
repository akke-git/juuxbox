JuuxBox v1.0 - Hi-Fi Music Player
=====================================

JuuxBox는 WASAPI Exclusive 모드를 지원하는 하이파이 음악 플레이어입니다.
YouTube 검색 통합 기능과 고품질 오디오 재생을 지원합니다.

지원 포맷: MP3, FLAC, WAV, M4A (FFmpeg 필요), AAC

=====================================
시스템 요구사항
=====================================

필수 요구사항:
- Windows 10/11 (64-bit)
- Microsoft Edge WebView2 런타임 (대부분 기본 설치됨)
- Visual C++ 2015-2022 Redistributable (x64)

선택 사항:
- FFmpeg (M4A/AAC 파일 재생용)

=====================================
설치 방법
=====================================

1. 전체 폴더를 원하는 위치에 압축 해제
   권장 경로: C:\JuuxBox\ 또는 C:\Program Files\JuuxBox\

2. JuuxBox.exe 더블클릭으로 실행

3. 첫 실행 시 데이터베이스 파일(juuxbox.db)이 자동으로 생성됩니다.

=====================================
필수 구성요소 설치
=====================================

▶ Edge WebView2 런타임
   대부분의 Windows 10/11에는 이미 설치되어 있습니다.
   설치되어 있지 않다면:
   https://go.microsoft.com/fwlink/?linkid=2124701

▶ Visual C++ Redistributable
   Python 라이브러리 실행에 필요합니다.
   설치되어 있지 않다면:
   https://aka.ms/vs/17/release/vc_redist.x64.exe

▶ FFmpeg (선택 사항)
   M4A/AAC 파일 재생에 필요합니다.
   - FFmpeg.exe가 이 폴더에 포함되어 있다면 → 추가 설치 불필요
   - 포함되어 있지 않다면 → https://www.ffmpeg.org/ 에서 다운로드

=====================================
사용 방법
=====================================

1. 음악 추가하기:
   - "Add Files" 버튼으로 개별 파일 추가
   - "Add Folder" 버튼으로 폴더 일괄 추가

2. 재생하기:
   - 곡 목록에서 더블클릭하여 재생
   - 재생 컨트롤로 일시정지/정지/이전곡/다음곡

3. YouTube 검색:
   - 검색창에 키워드 입력
   - YouTube에서 음악 검색 및 정보 확인

=====================================
문제 해결
=====================================

Q: 실행 시 "VCRUNTIME140.dll을 찾을 수 없습니다" 오류
A: Visual C++ Redistributable을 설치하세요.
   https://aka.ms/vs/17/release/vc_redist.x64.exe

Q: "WebView2 runtime is not installed" 오류
A: Edge WebView2를 설치하세요.
   https://go.microsoft.com/fwlink/?linkid=2124701

Q: M4A 파일이 재생되지 않습니다
A: FFmpeg가 필요합니다. FFmpeg.exe를 JuuxBox.exe와 같은 폴더에 넣으세요.

Q: 한글 경로의 음악 파일이 재생되지 않습니다
A: Python 3.10+ 버전으로 빌드된 정품 버전을 사용하세요.
   문제가 지속되면 파일을 영문 경로로 이동해보세요.

Q: 데이터베이스를 찾을 수 없다는 오류
A: JuuxBox를 쓰기 가능한 폴더에 설치하세요.
   관리자 권한으로 실행하지 마세요.

=====================================
라이선스 및 저작권
=====================================

© 2026 JuuxBox
오픈소스 라이브러리 사용: miniaudio, mutagen, pywebview

=====================================
지원 및 문의
=====================================

GitHub: https://github.com/yourusername/juuxbox
이메일: support@juuxbox.com

버전: 1.0
빌드 날짜: 2026-01-22
