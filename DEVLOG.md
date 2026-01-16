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

---

## 🔖 참조 파일
- [프로젝트 명세서](./agnet.md)
- [진행 상태](./PROJECT_STATUS.md)
- [README](./README.md)

---

> 💡 **사용법**: 새 세션 시작 시 `@DEVLOG.md 확인하고 이어서 작업해줘` 입력
