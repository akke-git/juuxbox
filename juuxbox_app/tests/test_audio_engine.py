#!/usr/bin/env python3
"""
Phase 1: Audio Engine Test
==========================
miniaudio와 mutagen을 사용한 오디오 재생 및 메타데이터 추출 테스트
"""

import sys
from pathlib import Path

# mutagen으로 메타데이터 추출
import mutagen
from mutagen.flac import FLAC

# miniaudio로 오디오 정보 확인
import miniaudio


def test_metadata_extraction(file_path: str):
    """메타데이터 추출 테스트"""
    print(f"\n{'='*60}")
    print(f"📋 메타데이터 추출 테스트: {Path(file_path).name}")
    print('='*60)
    
    try:
        audio = mutagen.File(file_path)
        
        if audio is None:
            print("❌ 파일을 읽을 수 없습니다")
            return None
        
        # 기본 정보
        info = audio.info
        print(f"\n🎵 파일 정보:")
        print(f"   포맷: {type(audio).__name__}")
        print(f"   길이: {info.length:.2f}초 ({int(info.length//60)}:{int(info.length%60):02d})")
        print(f"   Sample Rate: {info.sample_rate} Hz")
        print(f"   Channels: {info.channels}")
        
        # FLAC 전용 정보
        if hasattr(info, 'bits_per_sample'):
            print(f"   Bit Depth: {info.bits_per_sample} bit")
        if hasattr(info, 'bitrate'):
            print(f"   Bitrate: {info.bitrate} kbps")
        
        # 태그 정보
        print(f"\n🏷️ 태그 정보:")
        tags_to_show = ['title', 'artist', 'album', 'date', 'genre', 'tracknumber']
        for tag in tags_to_show:
            value = audio.get(tag)
            if value:
                print(f"   {tag.capitalize()}: {value[0] if isinstance(value, list) else value}")
        
        return {
            'sample_rate': info.sample_rate,
            'channels': info.channels,
            'bit_depth': getattr(info, 'bits_per_sample', 16),
            'duration': info.length
        }
        
    except Exception as e:
        print(f"❌ 에러: {e}")
        return None


def test_miniaudio_info(file_path: str):
    """miniaudio로 파일 정보 확인"""
    print(f"\n{'='*60}")
    print(f"🔊 miniaudio 파일 정보 테스트")
    print('='*60)
    
    try:
        info = miniaudio.get_file_info(file_path)
        print(f"\n📊 miniaudio 분석 결과:")
        print(f"   Sample Rate: {info.sample_rate} Hz")
        print(f"   Channels: {info.nchannels}")
        print(f"   Duration: {info.duration:.2f}초")
        print(f"   Sample Format: {info.sample_format.name}")
        print(f"   Sample Width: {info.sample_width} bytes")
        return info
    except Exception as e:
        print(f"❌ 에러: {e}")
        return None


def test_audio_devices():
    """사용 가능한 오디오 장치 확인"""
    print(f"\n{'='*60}")
    print(f"🎧 오디오 장치 목록")
    print('='*60)
    
    try:
        devices = miniaudio.Devices()
        playbacks = devices.get_playbacks()
        
        print(f"\n📢 재생 장치 ({len(playbacks)}개):")
        for i, dev in enumerate(playbacks):
            print(f"   [{i}] {dev['name']}")
        
        return playbacks
    except Exception as e:
        print(f"❌ 장치 목록 가져오기 실패: {e}")
        return []


def test_audio_playback(file_path: str, duration_seconds: float = 5.0):
    """오디오 재생 테스트 (처음 N초)"""
    print(f"\n{'='*60}")
    print(f"▶️ 오디오 재생 테스트 (처음 {duration_seconds}초)")
    print('='*60)
    
    try:
        # 파일 디코딩
        print(f"\n디코딩 중...")
        decoded = miniaudio.decode_file(file_path)
        
        print(f"   Sample Rate: {decoded.sample_rate} Hz")
        print(f"   Channels: {decoded.nchannels}")
        print(f"   Sample Format: {decoded.sample_format.name}")
        print(f"   Duration: {decoded.duration:.2f}초")
        
        # 재생 장치 생성
        print(f"\n🔊 재생 중... (Ctrl+C로 중단)")
        
        # 스트리밍 방식으로 재생
        stream = miniaudio.stream_file(file_path)
        
        with miniaudio.PlaybackDevice(
            output_format=stream.sample_format,
            nchannels=stream.nchannels,
            sample_rate=stream.sample_rate
        ) as device:
            device.start(stream)
            
            import time
            for i in range(int(duration_seconds)):
                time.sleep(1)
                print(f"   재생 중: {i+1}/{int(duration_seconds)}초")
            
        print("\n✅ 재생 테스트 완료!")
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ 재생 중단됨")
        return True
    except Exception as e:
        print(f"❌ 재생 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("\n" + "="*60)
    print("🎵 JuuxBox Audio Engine Test - Phase 1")
    print("="*60)
    
    # 샘플 파일 경로
    sample_dir = Path("/project/juuxbox/Music_Sample")
    sample_files = list(sample_dir.glob("*.flac"))
    
    if not sample_files:
        print("❌ 샘플 FLAC 파일을 찾을 수 없습니다!")
        print(f"   경로: {sample_dir}")
        sys.exit(1)
    
    print(f"\n📁 발견된 샘플 파일: {len(sample_files)}개")
    for f in sample_files:
        print(f"   - {f.name}")
    
    # 첫 번째 파일로 테스트
    test_file = str(sample_files[0])
    
    # 1. 메타데이터 추출 테스트
    metadata = test_metadata_extraction(test_file)
    
    # 2. miniaudio 정보 테스트
    audio_info = test_miniaudio_info(test_file)
    
    # 3. 오디오 장치 목록
    devices = test_audio_devices()
    
    # 4. 재생 테스트 (옵션)
    print(f"\n{'='*60}")
    print("재생 테스트를 실행하시겠습니까? (y/n): ", end="")
    
    # 자동 테스트 모드에서는 스킵
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        print("스킵 (--auto 모드)")
    else:
        try:
            response = input()
            if response.lower() == 'y':
                test_audio_playback(test_file, duration_seconds=5)
        except EOFError:
            print("스킵 (비대화형 모드)")
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("📊 테스트 결과 요약")
    print('='*60)
    
    if metadata:
        print(f"\n✅ 메타데이터 추출: 성공")
        print(f"   - {metadata['sample_rate']} Hz / {metadata['bit_depth']} bit / {metadata['channels']} ch")
    else:
        print(f"\n❌ 메타데이터 추출: 실패")
    
    if audio_info:
        print(f"✅ miniaudio 파일 분석: 성공")
    else:
        print(f"❌ miniaudio 파일 분석: 실패")
    
    if devices:
        print(f"✅ 오디오 장치 탐색: {len(devices)}개 발견")
    else:
        print(f"⚠️ 오디오 장치 탐색: 장치 없음")
    
    print("\n" + "="*60)
    print("🎉 Phase 1 테스트 완료!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
