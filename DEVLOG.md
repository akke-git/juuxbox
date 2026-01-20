# 📝 JuuxBox Development Log

> 개발 과정에서의 질문, 요구사항, 결정사항, 처리 결과를 기록합니다.  
> 다음 세션 시작 시 `@DEVLOG.md` 를 참조하면 바로 맥락을 파악할 수 있습니다.

---

## 📅 2026-01-16

### 세션 1: 초기 개발 완료

#### ✅ 완료된 작업
| 항목 | 내용 |
|------|------|
| 프로젝트명 | PureSound → **JuuxBox** 변경 |
| 기술 스택 | Python 3.11+ / PySide6 / miniaudio / SQLite |
| Phase 1 | Audio Engine Test (miniaudio, WASAPI) |
| Phase 2 | Database & Scanner (SQLite, mutagen) |
| Phase 3 | Spotify-like UI (PySide6) |
| Phase 4 | Integration (AppController) |
| Phase 5 | Polish (error handling, packaging) |

#### 💡 주요 결정사항
- ASIO 미지원, **WASAPI Exclusive만** 사용
- 데이터 저장 경로: `~/.juuxbox/`
- UI 스타일: Spotify Dark Theme

#### 🔗 GitHub
- Repository: https://github.com/akke-git/juuxbox
- Initial commit: 42 files, 3345 lines

---

## 📋 진행 예정 (세부 체크 & 개선)

> 아래에 질문/요구사항과 처리 결과를 추가합니다.

### Q&A Log

### Q1: 폴더 열기 기능 구현
**날짜**: 2026-01-16
**요청**: 사이드바에 "폴더 추가" 버튼 → 폴더 선택 → 스캔 → 곡 목록 표시
**처리**:
- `sidebar.py`: "➕ 폴더 추가" 버튼 및 `add_folder_clicked` 시그널 추가
- `test_integration.py`: `_on_folder_added()`, `_refresh_song_list()` 메서드 추가
- 폴더 선택 다이얼로그 → 스캔 → DB 저장 → UI 새로고침 연결
**관련 파일**: `ui/sidebar.py`, `tests/test_integration.py`
**상태**: ✅ 완료

### Q2: 폴더명 표시 기능
**날짜**: 2026-01-16
**요청**: 곡 목록에서 앨범 우측에 폴더명 표시
**처리**:
- `db/models.py`: tracks 테이블에 `folder_name` 컬럼 추가
- `db/repository.py`: INSERT 쿼리에 `folder_name` 포함
- `db/scanner.py`: 이미 `folder_name` 추출 중 (parent.name)
- `ui/song_list.py`: "폴더" 컬럼 추가
**상태**: ✅ 완료

### Q3: 곡 삭제 기능 (우클릭 메뉴)
**날짜**: 2026-01-16
**요청**: 곡 목록에서 우클릭으로 삭제 가능하게
**처리**:
- `db/repository.py`: `delete_by_file_path()`, `delete_all()` 추가
- `ui/song_list.py`: 컨텍스트 메뉴 추가 (단일 삭제, 전체 삭제)
- `test_integration.py`: 삭제 핸들러 연결
**상태**: ✅ 완료

### Q4: 체크박스 선택 삭제 기능
**날짜**: 2026-01-16
**요청**: 체크박스로 곡 선택 후 삭제 (전체 선택 포함)
**처리**:
- `ui/song_list.py`: 체크박스 컬럼 추가, 전체 선택 체크박스, 선택 삭제 버튼
- `db/repository.py`: `delete_by_file_paths()` 배치 삭제 추가
- `test_integration.py`: `_on_songs_delete()` 핸들러 추가
**관련 파일**: `ui/song_list.py`, `db/repository.py`, `tests/test_integration.py`
**상태**: ✅ 완료
**비고**: Qt 네이티브 체크박스 사용 (QTableWidgetItem.setCheckState)

### Q5: 앨범 커버 이미지 탐색
**날짜**: 2026-01-19
**요청**: 폴더 스캔 시 커버 이미지(cover.jpg, folder.jpg 등) 탐색 및 저장
**처리**:
- `db/scanner.py`: `COVER_FILENAMES` 상수, `_find_cover_image()` 메서드 추가
- `db/models.py`: tracks 테이블에 `cover_path` 컬럼 추가
- `db/repository.py`: INSERT 쿼리에 `cover_path` 포함
**관련 파일**: `db/scanner.py`, `db/models.py`, `db/repository.py`
**상태**: ✅ 완료
**비고**: cover.jpg, folder.jpg, front.jpg, album.jpg 등 우선순위 순 탐색

### Q6: 앨범 커버 UI 표시
**날짜**: 2026-01-19
**요청**: 곡 목록과 플레이어 바에 앨범 커버 이미지 표시
**처리**:
- `ui/song_list.py`: 커버 컬럼 추가 (8컬럼), 40px 썸네일 캐싱
- `ui/player_bar.py`: 56px 앨범 아트 로드 구현
- `tests/test_integration.py`: `cover_path` 전달 추가
**관련 파일**: `ui/song_list.py`, `ui/player_bar.py`, `tests/test_integration.py`
**상태**: ✅ 완료

### Q7: 포맷 배지로 변경
**날짜**: 2026-01-19
**요청**: 리스트의 앨범아트 대신 파일 포맷을 색상 배지로 표시
**처리**:
- `ui/song_list.py`: 커버 컬럼 삭제, 포맷 컬럼 추가 (앨범 우측)
- 포맷별 색상: FLAC=녹색, WAV/AIFF=파란색, DSD=보라색, M4A=오렌지, MP3=빨간색
- `tests/test_integration.py`: `audio_format` 파라미터 전달 추가
**관련 파일**: `ui/song_list.py`, `tests/test_integration.py`
**상태**: ✅ 완료

### Q8: Notion 스타일 UI 리디자인
**날짜**: 2026-01-19
**요청**: 테이블 헤더 좌측정렬, Notion 스타일 포맷 태그, List/Table 뷰 토글
**처리**:
- `ui/song_list.py`: 
  - 헤더 좌측정렬 (`text-align: left`)
  - `FormatTagDelegate` 클래스 추가 (라운드 배경 태그)
  - List/Table 뷰 토글 버튼
  - Notion 스타일 호버/선택 효과
**관련 파일**: `ui/song_list.py`
**상태**: ✅ 완료

### Q9: 임베디드 앨범아트 추출
**날짜**: 2026-01-19
**요청**: 오디오 파일 내장 앨범아트 추출 기능 추가
**처리**:
- `db/scanner.py`:
  - `_extract_embedded_cover()` 메서드 추가
  - FLAC: `audio.pictures[0].data`
  - MP3: ID3 APIC 태그
  - M4A: MP4 covr atom
  - 캐시 폴더: `~/.juuxbox/covers/`
  - MP3 포맷 장 (`AUDIO_EXTENSIONS`)
**관련 파일**: `db/scanner.py`
**상태**: ✅ 완료
**비고**: 임베디드 아트 우선, 없으면 폴더 이미지 사용

### Q10: 음악 상세 뷰 구현
**날짜**: 2026-01-20
**요청**: 플레이바 클릭 시 전체화면 상세 뷰, 좌우 이등분 레이아웃
**처리**:
- `ui/detail_view.py`: 새 컴포넌트 생성
  - 좌측: **420px** 앨범아트 (1.5배 확대), 메타데이터, 재생 컨트롤
  - 우측: 3개 그룹별 메타데이터 표시 + YouTube 버튼
    - 🎵 기본 정보: 트랙 번호, 장르, 폴더
    - 🎤 아티스트 정보: 앨범 아티스트, 작곡가, 지휘자, 연주자
    - 🎧 오디오 정보: 재생시간, 포맷, 샘플레이트, 비트뎁스, 비트레이트, 채널
  - 상단: Back 버튼으로 메인화면 복귀
- `db/scanner.py`: 추가 메타데이터 추출 (album_artist, track_number, genre, composer, conductor, performer, bitrate, channels)
- `db/repository.py`: INSERT 쿼리 업데이트
- `ui/player_bar.py`: `clicked` 시그널 추가
- `ui/main_window.py`: `DetailView` 추가
- `tests/test_integration.py`: 상세 뷰 시그널 연결
**관련 파일**: `ui/detail_view.py`, `db/scanner.py`, `db/repository.py`, `ui/player_bar.py`, `ui/main_window.py`, `tests/test_integration.py`
**상태**: ✅ 완료
**업데이트 (14:12)**: 참조 이미지(screen_1.jpg) 기반 디자인 변경
  - 반응형 앨범아트 (윈도우 크기에 맞게 조절)
  - 프로그레스바 + 현재시간/남은시간/포맷 표시
  - 재생 컨트롤 아이콘 변경 (▐▐ ■ ▶▶)
  - 하단 2줄 메타 요약 (장르/샘플레이트, 작곡가/채널)

### Q11: YouTube 검색 기능 구현
**날짜**: 2026-01-20
**요청**: 상세화면에서 YouTube 검색, 체크박스로 검색 항목 선택, 영상 미리보기
**처리**:
- `utils/youtube_search.py`: YouTube 검색 유틸리티 생성 (youtube-search-python 라이브러리)
- `ui/detail_view.py`: 우측 패널 전면 재작성
  - 메타데이터 그룹 삭제, YouTube 검색 UI로 대체
  - 체크박스 옵션 (곡명/가수명/앨범명)
  - 조회수 상위 5개 결과 표시
  - QWebEngineView로 영상 임베드 미리보기
  - 외부 브라우저로 열기 버튼
**관련 파일**: `utils/youtube_search.py`, `ui/detail_view.py`
**상태**: ✅ 완료

---

## 🔖 참조 파일
- [프로젝트 명세서](./agnet.md)
- [진행 상태](./PROJECT_STATUS.md)
- [README](./README.md)

---

> 💡 **사용법**: 새 세션 시작 시 `@DEVLOG.md 확인하고 이어서 작업해줘` 입력
