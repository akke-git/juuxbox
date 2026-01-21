/**
 * JuuxBox - Web UI Application
 */

// 전역 상태
const state = {
    tracks: [],
    filteredTracks: [],  // 검색/정렬 적용된 트랙
    currentTrack: null,
    isPlaying: false,
    playlist: [],
    playlistIndex: -1,
    selectedTracks: new Set(),
    viewMode: 'all',  // all, albums, artists, folders
    gridFilter: null,  // 그리드에서 선택한 필터값 (앨범명, 아티스트명, 폴더명)
    searchQuery: '',   // 검색어
    sortBy: 'title',   // 정렬 기준: title, artist, album, genre
    sortAsc: true      // 오름차순 정렬
};

// DOM 요소 캐싱
const elements = {};

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    cacheElements();
    bindEvents();
});

// pywebview API 준비 후 트랙 로드
window.addEventListener('pywebviewready', () => {
    console.log('pywebview API ready');
    loadTracks();
});

// DOM 요소 캐싱
function cacheElements() {
    elements.trackListBody = document.getElementById('track-list-body');
    elements.trackCount = document.getElementById('track-count');
    elements.emptyState = document.getElementById('empty-state');
    elements.selectAll = document.getElementById('select-all');
    elements.btnDeleteSelected = document.getElementById('btn-delete-selected');
    elements.btnAddFolder = document.getElementById('btn-add-folder');

    // 네비게이션
    elements.navItems = document.querySelectorAll('.nav-item');
    elements.views = document.querySelectorAll('.view');
    elements.btnBack = document.getElementById('btn-back');

    // 플레이어
    elements.playerTitle = document.getElementById('player-title');
    elements.playerArtist = document.getElementById('player-artist');
    elements.playerAlbumArt = document.getElementById('player-album-art');
    elements.btnPlay = document.getElementById('btn-play');
    elements.btnStop = document.getElementById('btn-stop');
    elements.btnPrev = document.getElementById('btn-prev');
    elements.btnNext = document.getElementById('btn-next');
    elements.progressBar = document.getElementById('progress-bar');
    elements.currentTime = document.getElementById('current-time');
    elements.totalTime = document.getElementById('total-time');
    elements.volumeBar = document.getElementById('volume-bar');
    elements.playerTrackInfo = document.getElementById('player-track-info');
    elements.playerBar = document.querySelector('.player-bar');

    // 지금 재생 중
    elements.npTitle = document.getElementById('np-title');
    elements.npArtist = document.getElementById('np-artist');
    elements.npAlbum = document.getElementById('np-album');
    elements.npFormat = document.getElementById('np-format');
    elements.npSampleRate = document.getElementById('np-sample-rate');
    elements.npBitDepth = document.getElementById('np-bit-depth');
    elements.albumArtImg = document.getElementById('album-art-img');

    // YouTube
    elements.btnYoutubeSearch = document.getElementById('btn-youtube-search');
    elements.youtubeStatus = document.getElementById('youtube-status');
    elements.youtubeResults = document.getElementById('youtube-results');
    elements.youtubePlayer = document.getElementById('youtube-player');
    elements.ytUseTitle = document.getElementById('yt-use-title');
    elements.ytUseArtist = document.getElementById('yt-use-artist');
    elements.ytUseAlbum = document.getElementById('yt-use-album');

    // 뷰 모드
    elements.viewTabs = document.querySelectorAll('.view-tab');
    elements.gridContainer = document.getElementById('grid-container');
    elements.trackListContainer = document.getElementById('track-list-container');
    elements.libraryTitle = document.getElementById('library-title');
    elements.btnGridBack = document.getElementById('btn-grid-back');

    // 설정
    elements.btnSettings = document.getElementById('btn-settings');
    elements.settingsModal = document.getElementById('settings-modal');
    elements.btnCloseSettings = document.getElementById('btn-close-settings');
    elements.audioDeviceSelect = document.getElementById('audio-device-select');
    elements.outputModeText = document.getElementById('output-mode-text');
    elements.audioOutputMode = document.getElementById('audio-output-mode');

    // 검색 & 정렬
    elements.searchInput = document.getElementById('search-input');
    elements.btnSort = document.getElementById('btn-sort');
    elements.sortMenu = document.getElementById('sort-menu');
    elements.sortOptions = document.querySelectorAll('.sort-option');
}

// 이벤트 바인딩
function bindEvents() {
    // 폴더 추가
    elements.btnAddFolder.addEventListener('click', addFolder);

    // 전체 선택
    elements.selectAll.addEventListener('change', toggleSelectAll);

    // 선택 삭제
    elements.btnDeleteSelected.addEventListener('click', deleteSelectedTracks);

    // 네비게이션
    elements.navItems.forEach(item => {
        item.addEventListener('click', () => switchView(item.dataset.view));
    });
    elements.btnBack.addEventListener('click', () => switchView('library'));

    // 플레이어 컨트롤
    elements.btnPlay.addEventListener('click', togglePlay);
    elements.btnStop.addEventListener('click', stopPlayback);
    elements.btnPrev.addEventListener('click', playPrevious);
    elements.btnNext.addEventListener('click', playNext);
    elements.progressBar.addEventListener('input', seekTo);
    elements.volumeBar.addEventListener('input', setVolume);

    // 플레이어 바 클릭 시 상세 뷰로 이동 (버튼, 슬라이더 제외)
    elements.playerBar.addEventListener('click', (e) => {
        // 버튼이나 슬라이더 클릭은 무시
        if (e.target.closest('button') || e.target.closest('input')) {
            return;
        }
        if (state.currentTrack) {
            switchView('nowplaying');
        }
    });

    // YouTube 검색
    elements.btnYoutubeSearch.addEventListener('click', searchYoutube);

    // 뷰 모드 탭
    elements.viewTabs.forEach(tab => {
        tab.addEventListener('click', () => switchViewMode(tab.dataset.mode));
    });

    // 그리드 뒤로가기
    elements.btnGridBack.addEventListener('click', backFromGrid);

    // ESC 키로 상세화면에서 뒤로가기 또는 모달 닫기
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            // 모달이 열려있으면 모달 닫기
            if (elements.settingsModal && elements.settingsModal.style.display !== 'none') {
                closeSettings();
                return;
            }
            const nowPlayingView = document.getElementById('view-nowplaying');
            if (nowPlayingView && nowPlayingView.classList.contains('active')) {
                switchView('library');
            } else if (state.gridFilter) {
                // 그리드 상세에서 그리드로 돌아가기
                backFromGrid();
            }
        }
    });

    // 설정
    elements.btnSettings.addEventListener('click', openSettings);
    elements.btnCloseSettings.addEventListener('click', closeSettings);
    elements.audioOutputMode.addEventListener('click', openSettings);
    elements.audioDeviceSelect.addEventListener('change', changeAudioDevice);

    // 모달 외부 클릭 시 닫기
    elements.settingsModal.addEventListener('click', (e) => {
        if (e.target === elements.settingsModal) {
            closeSettings();
        }
    });

    // 검색
    elements.searchInput.addEventListener('input', debounce(handleSearch, 300));

    // 정렬 버튼
    elements.btnSort.addEventListener('click', toggleSortMenu);

    // 정렬 옵션
    elements.sortOptions.forEach(option => {
        option.addEventListener('click', () => handleSort(option.dataset.sort));
    });

    // 정렬 메뉴 외부 클릭 시 닫기
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.sort-control')) {
            elements.sortMenu.classList.add('hidden');
        }
    });
}

// 트랙 목록 로드
async function loadTracks() {
    try {
        const tracks = await pywebview.api.get_all_tracks();
        state.tracks = tracks;
        applySearchAndSort();
    } catch (e) {
        console.error('트랙 로드 실패:', e);
    }
}

// 트랙 목록 렌더링
function renderTrackList() {
    const tbody = elements.trackListBody;
    tbody.innerHTML = '';

    const tracksToRender = state.filteredTracks;

    if (state.tracks.length === 0) {
        elements.emptyState.classList.add('show');
        elements.trackCount.textContent = '0곡';
        return;
    }

    elements.emptyState.classList.remove('show');

    // 필터링된 결과 표시
    if (state.searchQuery) {
        elements.trackCount.textContent = `${tracksToRender.length}/${state.tracks.length}곡`;
    } else {
        elements.trackCount.textContent = `${state.tracks.length}곡`;
    }

    tracksToRender.forEach((track, index) => {
        const tr = document.createElement('tr');
        tr.dataset.index = index;
        tr.dataset.path = track.file_path;

        if (state.currentTrack && state.currentTrack.file_path === track.file_path) {
            tr.classList.add('playing');
        }

        const formatClass = `format-${(track.audio_format || '').toLowerCase()}`;

        tr.innerHTML = `
            <td class="col-checkbox">
                <input type="checkbox" class="track-checkbox" data-path="${track.file_path}">
            </td>
            <td class="col-title" title="${escapeHtml(track.title)}">${escapeHtml(track.title)}</td>
            <td class="col-artist" title="${escapeHtml(track.artist)}">${escapeHtml(track.artist)}</td>
            <td class="col-album" title="${escapeHtml(track.album)}">${escapeHtml(track.album)}</td>
            <td class="col-format">
                <span class="format-badge ${formatClass}">${track.audio_format.toUpperCase()}</span>
            </td>
            <td class="col-duration">${formatDuration(track.duration)}</td>
            <td class="col-folder" title="${escapeHtml(track.folder_name)}">${escapeHtml(track.folder_name)}</td>
        `;

        // 더블클릭으로 재생 (filteredTracks 기준 인덱스 사용)
        tr.addEventListener('dblclick', () => playFilteredTrack(index));

        // 체크박스 클릭
        const checkbox = tr.querySelector('.track-checkbox');
        checkbox.addEventListener('change', (e) => {
            e.stopPropagation();
            toggleTrackSelection(track.file_path, checkbox.checked);
        });

        tbody.appendChild(tr);
    });

    // 플레이리스트 업데이트 (필터링된 트랙 기준)
    state.playlist = [...tracksToRender];
}

// 트랙 재생
async function playTrack(index) {
    const track = state.tracks[index];
    if (!track) return;

    // YouTube 재생 중지
    stopYoutubePlayback();

    try {
        console.log('재생 시도:', track.file_path);
        const result = await pywebview.api.play(track.file_path);
        console.log('재생 결과:', result);
        if (result.success) {
            state.currentTrack = track;
            state.isPlaying = true;
            state.playlistIndex = index;
            await pywebview.api.set_playlist(state.tracks, index);
            updatePlayerUI();
            updateNowPlayingUI();
            highlightPlayingTrack();
        } else {
            console.error('재생 실패:', result.error);
        }
    } catch (e) {
        console.error('재생 예외:', e);
    }
}

// 플레이어 UI 업데이트
function updatePlayerUI() {
    const track = state.currentTrack;
    if (!track) return;

    elements.playerTitle.textContent = track.title;
    elements.playerArtist.textContent = track.artist;

    loadCoverImage(track.cover_path, elements.playerAlbumArt);

    updatePlayButtonIcon();
    elements.totalTime.textContent = formatDuration(track.duration);
}

// 재생 버튼 아이콘 업데이트
function updatePlayButtonIcon() {
    if (state.isPlaying) {
        elements.btnPlay.classList.remove('icon-play');
        elements.btnPlay.classList.add('icon-pause');
    } else {
        elements.btnPlay.classList.remove('icon-pause');
        elements.btnPlay.classList.add('icon-play');
    }
}

// 지금 재생 중 UI 업데이트
function updateNowPlayingUI() {
    const track = state.currentTrack;
    if (!track) return;

    elements.npTitle.textContent = track.title;
    elements.npArtist.textContent = track.artist;
    elements.npAlbum.textContent = track.album;

    // 오디오 정보
    elements.npFormat.textContent = track.audio_format.toUpperCase();
    elements.npFormat.className = `format-badge format-${track.audio_format.toLowerCase()}`;

    if (track.sample_rate) {
        elements.npSampleRate.textContent = `${(track.sample_rate / 1000).toFixed(1)} kHz`;
    }
    if (track.bit_depth) {
        elements.npBitDepth.textContent = `${track.bit_depth} bit`;
    }

    // 앨범아트
    loadCoverImage(track.cover_path, elements.albumArtImg);

    // YouTube 검색 결과 초기화
    elements.youtubeResults.innerHTML = '';
    elements.youtubeStatus.textContent = '';
    elements.youtubePlayer.innerHTML = '<p class="placeholder">검색 결과에서 영상을 선택하세요</p>';
}

// 재생 중인 트랙 하이라이트
function highlightPlayingTrack() {
    document.querySelectorAll('.track-list tbody tr').forEach(tr => {
        tr.classList.remove('playing');
        if (state.currentTrack && tr.dataset.path === state.currentTrack.file_path) {
            tr.classList.add('playing');
        }
    });
}

// 재생/일시정지 토글
async function togglePlay() {
    if (!state.currentTrack) {
        if (state.tracks.length > 0) {
            playTrack(0);
        }
        return;
    }

    try {
        if (state.isPlaying) {
            await pywebview.api.pause();
            state.isPlaying = false;
        } else {
            // 재개 시 YouTube 정지
            stopYoutubePlayback();
            await pywebview.api.resume();
            state.isPlaying = true;
        }
        updatePlayButtonIcon();
    } catch (e) {
        console.error('재생/일시정지 실패:', e);
    }
}

// 정지
async function stopPlayback() {
    try {
        await pywebview.api.stop();
        state.isPlaying = false;
        updatePlayButtonIcon();
        elements.progressBar.value = 0;
        elements.currentTime.textContent = '0:00';
    } catch (e) {
        console.error('정지 실패:', e);
    }
}

// 이전 곡
async function playPrevious() {
    stopYoutubePlayback();
    try {
        const result = await pywebview.api.play_previous();
        if (result.success && result.track) {
            state.currentTrack = result.track;
            state.isPlaying = true;
            state.playlistIndex = state.tracks.findIndex(t => t.file_path === result.track.file_path);
            updatePlayerUI();
            updateNowPlayingUI();
            highlightPlayingTrack();
        }
    } catch (e) {
        console.error('이전 곡 실패:', e);
    }
}

// 다음 곡
async function playNext() {
    stopYoutubePlayback();
    try {
        const result = await pywebview.api.play_next();
        if (result.success && result.track) {
            state.currentTrack = result.track;
            state.isPlaying = true;
            state.playlistIndex = state.tracks.findIndex(t => t.file_path === result.track.file_path);
            updatePlayerUI();
            updateNowPlayingUI();
            highlightPlayingTrack();
        }
    } catch (e) {
        console.error('다음 곡 실패:', e);
    }
}

// 탐색
async function seekTo() {
    if (!state.currentTrack) return;
    const position = (elements.progressBar.value / 1000) * state.currentTrack.duration;
    try {
        await pywebview.api.seek(position);
    } catch (e) {
        console.error('탐색 실패:', e);
    }
}

// 볼륨 설정
async function setVolume() {
    const volume = elements.volumeBar.value / 100;
    try {
        await pywebview.api.set_volume(volume);
    } catch (e) {
        console.error('볼륨 설정 실패:', e);
    }
}

// 진행률 업데이트 (Python에서 호출)
window.onProgressUpdate = function (current, total) {
    if (total > 0) {
        const progress = (current / total) * 100;
        elements.progressBar.value = (current / total) * 1000;
        elements.progressBar.style.setProperty('--progress', progress + '%');
        elements.currentTime.textContent = formatDuration(current);
    }
};

// 폴더 추가
async function addFolder() {
    try {
        const folderPath = await pywebview.api.select_folder();
        if (folderPath) {
            elements.btnAddFolder.disabled = true;
            elements.btnAddFolder.querySelector('span:last-child').textContent = '스캔 중...';

            const result = await pywebview.api.scan_folder(folderPath);
            if (result.success) {
                await loadTracks();
                alert(`${result.count}개 트랙을 추가했습니다.`);
            } else {
                alert('스캔 실패: ' + result.error);
            }

            elements.btnAddFolder.disabled = false;
            elements.btnAddFolder.querySelector('span:last-child').textContent = '폴더 추가';
        }
    } catch (e) {
        console.error('폴더 추가 실패:', e);
        elements.btnAddFolder.disabled = false;
        elements.btnAddFolder.querySelector('span:last-child').textContent = '폴더 추가';
    }
}

// 전체 선택 토글
function toggleSelectAll() {
    const checked = elements.selectAll.checked;
    document.querySelectorAll('.track-checkbox').forEach(cb => {
        cb.checked = checked;
        toggleTrackSelection(cb.dataset.path, checked);
    });
}

// 트랙 선택 토글
function toggleTrackSelection(path, selected) {
    if (selected) {
        state.selectedTracks.add(path);
    } else {
        state.selectedTracks.delete(path);
    }
    elements.btnDeleteSelected.disabled = state.selectedTracks.size === 0;
}

// 선택된 트랙 삭제
async function deleteSelectedTracks() {
    if (state.selectedTracks.size === 0) return;

    if (!confirm(`${state.selectedTracks.size}개의 트랙을 Library에서 삭제하시겠습니까?`)) {
        return;
    }

    try {
        const paths = Array.from(state.selectedTracks);
        const result = await pywebview.api.delete_tracks(paths);
        if (result.success) {
            state.selectedTracks.clear();
            elements.selectAll.checked = false;
            await loadTracks();
        }
    } catch (e) {
        console.error('삭제 실패:', e);
    }
}

// 뷰 전환
function switchView(viewName) {
    elements.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.view === viewName);
    });

    elements.views.forEach(view => {
        view.classList.toggle('active', view.id === `view-${viewName}`);
    });
}

// YouTube 검색
async function searchYoutube() {
    if (!state.currentTrack) {
        elements.youtubeStatus.textContent = '재생 중인 곡이 없습니다.';
        return;
    }

    elements.btnYoutubeSearch.disabled = true;
    elements.youtubeStatus.textContent = '🔍 검색 중...';
    elements.youtubeResults.innerHTML = '';

    try {
        const result = await pywebview.api.search_youtube(
            state.currentTrack.title || '',
            state.currentTrack.artist || '',
            state.currentTrack.album || '',
            elements.ytUseTitle.checked,
            elements.ytUseArtist.checked,
            elements.ytUseAlbum.checked
        );

        if (!result.success) {
            elements.youtubeStatus.textContent = '❌ ' + result.error;
            return;
        }

        if (result.results.length === 0) {
            elements.youtubeStatus.textContent = '❌ 검색 결과 없음';
            return;
        }

        elements.youtubeStatus.textContent = `✅ ${result.results.length}개 결과 (조회수 상위)`;

        // 결과 목록 렌더링
        result.results.forEach((video, index) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div class="title">🎬 ${escapeHtml(video.title)}</div>
                <div class="meta">${escapeHtml(video.channel)} • ${video.duration} • ${video.views}</div>
            `;
            li.addEventListener('click', () => selectYoutubeVideo(video, li));
            elements.youtubeResults.appendChild(li);
        });

    } catch (e) {
        elements.youtubeStatus.textContent = '❌ 검색 실패: ' + e.message;
        console.error('YouTube 검색 오류:', e);
    } finally {
        elements.btnYoutubeSearch.disabled = false;
    }
}

// YouTube 영상 선택
async function selectYoutubeVideo(video, li) {
    // 선택 표시
    elements.youtubeResults.querySelectorAll('li').forEach(item => item.classList.remove('selected'));
    li.classList.add('selected');

    // 로컬 음악 재생 중지
    await stopPlayback();

    // YouTube 플레이어에 영상 로드 (iframe embed)
    if (video.video_id) {
        elements.youtubePlayer.innerHTML = `
            <iframe
                src="https://www.youtube.com/embed/${video.video_id}?autoplay=1&rel=0"
                allow="autoplay; encrypted-media; picture-in-picture"
                allowfullscreen>
            </iframe>
        `;
    }
}

// YouTube 재생 중지
function stopYoutubePlayback() {
    if (elements.youtubePlayer) {
        elements.youtubePlayer.innerHTML = '<p class="placeholder">검색 결과에서 영상을 선택하세요</p>';
    }
}

// 유틸리티 함수들
async function loadCoverImage(coverPath, imgElement) {
    if (!coverPath) {
        imgElement.classList.remove('show');
        return;
    }
    try {
        const result = await pywebview.api.get_cover_image(coverPath);
        if (result.success) {
            imgElement.src = result.data_uri;
            imgElement.classList.add('show');
        } else {
            imgElement.classList.remove('show');
        }
    } catch (e) {
        console.error('커버 이미지 로드 실패:', e);
        imgElement.classList.remove('show');
    }
}

function formatDuration(seconds) {
    if (!seconds || seconds < 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// debounce 유틸리티
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===== 검색 & 정렬 =====

// 검색 및 정렬 적용
function applySearchAndSort() {
    let filtered = [...state.tracks];

    // 검색 필터 적용
    if (state.searchQuery) {
        const query = state.searchQuery.toLowerCase();
        filtered = filtered.filter(track =>
            (track.title && track.title.toLowerCase().includes(query)) ||
            (track.artist && track.artist.toLowerCase().includes(query)) ||
            (track.album && track.album.toLowerCase().includes(query))
        );
    }

    // 정렬 적용
    filtered.sort((a, b) => {
        let valA, valB;

        switch (state.sortBy) {
            case 'artist':
                valA = (a.artist || '').toLowerCase();
                valB = (b.artist || '').toLowerCase();
                break;
            case 'album':
                valA = (a.album || '').toLowerCase();
                valB = (b.album || '').toLowerCase();
                break;
            case 'genre':
                valA = (a.genre || '').toLowerCase();
                valB = (b.genre || '').toLowerCase();
                break;
            case 'title':
            default:
                valA = (a.title || '').toLowerCase();
                valB = (b.title || '').toLowerCase();
                break;
        }

        if (valA < valB) return state.sortAsc ? -1 : 1;
        if (valA > valB) return state.sortAsc ? 1 : -1;
        return 0;
    });

    state.filteredTracks = filtered;
    renderTrackList();
}

// 검색 처리
function handleSearch() {
    state.searchQuery = elements.searchInput.value.trim();
    applySearchAndSort();
}

// 정렬 메뉴 토글
function toggleSortMenu(e) {
    e.stopPropagation();
    elements.sortMenu.classList.toggle('hidden');
}

// 정렬 처리
function handleSort(sortBy) {
    // 같은 기준이면 정렬 방향 토글
    if (state.sortBy === sortBy) {
        state.sortAsc = !state.sortAsc;
    } else {
        state.sortBy = sortBy;
        state.sortAsc = true;
    }

    // 활성 옵션 표시
    elements.sortOptions.forEach(option => {
        option.classList.toggle('active', option.dataset.sort === sortBy);
    });

    // 메뉴 닫기
    elements.sortMenu.classList.add('hidden');

    applySearchAndSort();
}

// 필터링된 트랙 재생
function playFilteredTrack(index) {
    const track = state.filteredTracks[index];
    if (!track) return;

    // 원본 트랙 배열에서의 인덱스 찾기
    const originalIndex = state.tracks.findIndex(t => t.file_path === track.file_path);
    if (originalIndex !== -1) {
        playTrack(originalIndex);
    }
}

// ===== 뷰 모드 전환 =====

// 뷰 모드 전환
async function switchViewMode(mode) {
    state.viewMode = mode;
    state.gridFilter = null;

    // 탭 활성화
    elements.viewTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.mode === mode);
    });

    // 뒤로가기 버튼 숨김
    elements.btnGridBack.style.display = 'none';
    elements.libraryTitle.textContent = 'Library';

    if (mode === 'all') {
        // 전체 트랙 리스트
        elements.gridContainer.style.display = 'none';
        elements.trackListContainer.style.display = 'block';
        loadTracks();
    } else if (mode === 'albums') {
        await loadAlbums();
    } else if (mode === 'artists') {
        await loadArtists();
    } else if (mode === 'folders') {
        await loadFolders();
    }
}

// 앨범 그리드 로드
async function loadAlbums() {
    elements.trackListContainer.style.display = 'none';
    elements.gridContainer.style.display = 'grid';
    elements.gridContainer.innerHTML = '';

    try {
        const albums = await pywebview.api.get_albums();
        elements.trackCount.textContent = `${albums.length}개 앨범`;

        albums.forEach(album => {
            const card = createGridCard(
                album.album || 'Unknown Album',
                album.artist || 'Unknown Artist',
                `${album.track_count}곡`,
                album.cover_path,
                () => showAlbumTracks(album.album)
            );
            elements.gridContainer.appendChild(card);
        });
    } catch (e) {
        console.error('앨범 로드 실패:', e);
    }
}

// 아티스트 그리드 로드
async function loadArtists() {
    elements.trackListContainer.style.display = 'none';
    elements.gridContainer.style.display = 'grid';
    elements.gridContainer.innerHTML = '';

    try {
        const artists = await pywebview.api.get_artists();
        elements.trackCount.textContent = `${artists.length}명 아티스트`;

        artists.forEach(artist => {
            const card = createGridCard(
                artist.artist || 'Unknown Artist',
                `${artist.album_count}개 앨범`,
                `${artist.track_count}곡`,
                artist.cover_path,
                () => showArtistTracks(artist.artist)
            );
            elements.gridContainer.appendChild(card);
        });
    } catch (e) {
        console.error('아티스트 로드 실패:', e);
    }
}

// 폴더 그리드 로드
async function loadFolders() {
    elements.trackListContainer.style.display = 'none';
    elements.gridContainer.style.display = 'grid';
    elements.gridContainer.innerHTML = '';

    try {
        const folders = await pywebview.api.get_folders();
        elements.trackCount.textContent = `${folders.length}개 폴더`;

        folders.forEach(folder => {
            const card = createGridCard(
                folder.folder_name || 'Unknown Folder',
                '',
                `${folder.track_count}곡`,
                folder.cover_path,
                () => showFolderTracks(folder.folder_name)
            );
            card.querySelector('.grid-card-image').innerHTML = '📁';  // 폴더 아이콘
            if (folder.cover_path) {
                loadCoverForCard(folder.cover_path, card.querySelector('.grid-card-image'));
            }
            elements.gridContainer.appendChild(card);
        });
    } catch (e) {
        console.error('폴더 로드 실패:', e);
    }
}

// 그리드 카드 생성
function createGridCard(title, subtitle, meta, coverPath, onClick) {
    const card = document.createElement('div');
    card.className = 'grid-card';
    card.innerHTML = `
        <div class="grid-card-image">🎵</div>
        <div class="grid-card-title">${escapeHtml(title)}</div>
        ${subtitle ? `<div class="grid-card-subtitle">${escapeHtml(subtitle)}</div>` : ''}
        <div class="grid-card-meta">${escapeHtml(meta)}</div>
    `;
    card.addEventListener('click', onClick);

    if (coverPath) {
        loadCoverForCard(coverPath, card.querySelector('.grid-card-image'));
    }

    return card;
}

// 카드에 커버 이미지 로드
async function loadCoverForCard(coverPath, imageContainer) {
    if (!coverPath) return;
    try {
        const result = await pywebview.api.get_cover_image(coverPath);
        if (result.success) {
            imageContainer.innerHTML = `<img src="${result.data_uri}" alt="">`;
        }
    } catch (e) {
        console.error('카드 커버 로드 실패:', e);
    }
}

// 앨범 트랙 표시
async function showAlbumTracks(album) {
    state.gridFilter = album;
    elements.libraryTitle.textContent = album;
    elements.btnGridBack.style.display = 'block';
    elements.gridContainer.style.display = 'none';
    elements.trackListContainer.style.display = 'block';

    try {
        const tracks = await pywebview.api.get_tracks_by_album(album);
        state.tracks = tracks;
        applySearchAndSort();
    } catch (e) {
        console.error('앨범 트랙 로드 실패:', e);
    }
}

// 아티스트 트랙 표시
async function showArtistTracks(artist) {
    state.gridFilter = artist;
    elements.libraryTitle.textContent = artist;
    elements.btnGridBack.style.display = 'block';
    elements.gridContainer.style.display = 'none';
    elements.trackListContainer.style.display = 'block';

    try {
        const tracks = await pywebview.api.get_tracks_by_artist(artist);
        state.tracks = tracks;
        applySearchAndSort();
    } catch (e) {
        console.error('아티스트 트랙 로드 실패:', e);
    }
}

// 폴더 트랙 표시
async function showFolderTracks(folderName) {
    state.gridFilter = folderName;
    elements.libraryTitle.textContent = folderName;
    elements.btnGridBack.style.display = 'block';
    elements.gridContainer.style.display = 'none';
    elements.trackListContainer.style.display = 'block';

    try {
        const tracks = await pywebview.api.get_tracks_by_folder(folderName);
        state.tracks = tracks;
        applySearchAndSort();
    } catch (e) {
        console.error('폴더 트랙 로드 실패:', e);
    }
}

// 그리드로 돌아가기
function backFromGrid() {
    state.gridFilter = null;
    elements.btnGridBack.style.display = 'none';
    elements.libraryTitle.textContent = 'Library';

    // 현재 뷰 모드에 따라 그리드 다시 로드
    switchViewMode(state.viewMode);
}

// ===== 테이블 컬럼 리사이즈 =====

function initColumnResize() {
    const table = document.querySelector('.track-list');
    if (!table) return;

    const headers = table.querySelectorAll('th');

    headers.forEach((th, index) => {
        // 체크박스 컬럼은 제외
        if (th.classList.contains('col-checkbox')) return;

        // 리사이즈 핸들 추가
        const handle = document.createElement('div');
        handle.className = 'resize-handle';
        th.appendChild(handle);

        let startX, startWidth;

        handle.addEventListener('mousedown', (e) => {
            startX = e.pageX;
            startWidth = th.offsetWidth;
            handle.classList.add('resizing');

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
            e.preventDefault();
        });

        function onMouseMove(e) {
            const diff = e.pageX - startX;
            const newWidth = Math.max(50, startWidth + diff);
            th.style.width = newWidth + 'px';
            th.style.minWidth = newWidth + 'px';
            th.style.maxWidth = newWidth + 'px';
        }

        function onMouseUp() {
            handle.classList.remove('resizing');
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        }
    });
}

// 페이지 로드 시 리사이즈 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 약간의 지연 후 초기화 (DOM이 완전히 렌더링된 후)
    setTimeout(initColumnResize, 100);
});

// ===== 설정 =====

async function openSettings() {
    elements.settingsModal.style.display = 'flex';
    await loadAudioDevices();
    await loadAudioSettings();
}

function closeSettings() {
    elements.settingsModal.style.display = 'none';
}

async function loadAudioDevices() {
    try {
        const result = await pywebview.api.get_audio_devices();
        if (result.success) {
            const select = elements.audioDeviceSelect;
            select.innerHTML = '<option value="System Default">System Default</option>';

            result.devices.forEach(device => {
                const option = document.createElement('option');
                option.value = device.name;
                option.textContent = device.name;
                if (device.name === result.current_device) {
                    option.selected = true;
                }
                select.appendChild(option);
            });
        }
    } catch (e) {
        console.error('오디오 장치 목록 로드 실패:', e);
    }
}

async function loadAudioSettings() {
    try {
        const settings = await pywebview.api.get_audio_settings();

        // 설정 모달 업데이트
        document.getElementById('setting-output-mode').textContent = settings.output_mode;
        document.getElementById('setting-sample-rate').textContent =
            settings.sample_rate ? `${settings.sample_rate} Hz` : '-';
        document.getElementById('setting-bit-depth').textContent =
            settings.bit_depth ? `${settings.bit_depth} bit` : '-';

        // 플레이어 바 출력 모드 업데이트
        elements.outputModeText.textContent = 'Shared';
    } catch (e) {
        console.error('오디오 설정 로드 실패:', e);
    }
}

async function changeAudioDevice() {
    const deviceName = elements.audioDeviceSelect.value;
    try {
        const result = await pywebview.api.set_audio_device(deviceName);
        if (result.success) {
            console.log('오디오 장치 변경:', deviceName);
            await loadAudioSettings();
        } else {
            alert('오디오 장치 변경 실패: ' + result.error);
        }
    } catch (e) {
        console.error('오디오 장치 변경 실패:', e);
    }
}
