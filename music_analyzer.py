"""
음악 분석 모듈 - librosa를 사용하여 리듬 게임 채보 생성
"""
import librosa
import numpy as np
import os
import json
import hashlib

class MusicAnalyzer:
    """음악 파일을 분석하여 리듬 게임 채보 데이터를 생성하는 클래스"""
    
    def __init__(self, music_path):
        """
        Args:
            music_path: 음악 파일 경로 (mp3, wav 등)
        """
        self.music_path = music_path
        self.y = None  # 오디오 시계열 데이터
        self.sr = None  # 샘플링 레이트
        self.tempo = None  # BPM
        self.beat_times = []  # 비트 타이밍 (초 단위)
        self.onset_times = []  # 온셋 타이밍 (초 단위)
        self.duration = 0  # 음악 길이 (초)
        
        self.is_loaded = False
        
        # 캠싱 관련
        self.cache_dir = 'charts_cache'
        self.cache_file = None
        
    def get_cache_filename(self):
        """음악 파일의 캠시 파일명 생성 (MD5 해시 기반)"""
        # 파일 내용을 해싱하여 유니크한 이름 생성
        try:
            with open(self.music_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            filename = os.path.basename(self.music_path)
            name_without_ext = os.path.splitext(filename)[0]
            return f"{name_without_ext}_{file_hash[:8]}.json"
        except:
            # 해싱 실패 시 파일명만 사용
            filename = os.path.basename(self.music_path)
            name_without_ext = os.path.splitext(filename)[0]
            return f"{name_without_ext}_cache.json"
    
    def load_from_cache(self):
        """캠시에서 분석 데이터 로드"""
        if not os.path.exists(self.cache_dir):
            return False
        
        cache_filename = self.get_cache_filename()
        self.cache_file = os.path.join(self.cache_dir, cache_filename)
        
        if not os.path.exists(self.cache_file):
            return False
        
        try:
            print(f"캠시에서 로드 중: {cache_filename}")
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.tempo = data['tempo']
            self.beat_times = np.array(data['beat_times'])
            self.onset_times = np.array(data['onset_times'])
            self.duration = data['duration']
            self.sr = data['sr']
            self.is_loaded = True
            
            print(f"✓캠시 로드 성공!")
            return True
        except Exception as e:
            print(f"캠시 로드 실패: {e}")
            return False
    
    def save_to_cache(self):
        """분석 데이터를 캠시에 저장"""
        if not self.is_loaded:
            return False
        
        try:
            # 캠시 디렉토리 생성
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)
                print(f"캠시 디렉토리 생성: {self.cache_dir}")
            
            cache_filename = self.get_cache_filename()
            self.cache_file = os.path.join(self.cache_dir, cache_filename)
            
            data = {
                'music_file': os.path.basename(self.music_path),
                'tempo': float(self.tempo),
                'beat_times': self.beat_times.tolist(),
                'onset_times': self.onset_times.tolist(),
                'duration': float(self.duration),
                'sr': int(self.sr)
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print(f"캠시 저장 완료: {cache_filename}")
            return True
        except Exception as e:
            print(f"캠시 저장 실패: {e}")
            return False
        
    def load_and_analyze(self):
        """음악 파일을 로드하고 분석"""
        if not os.path.exists(self.music_path):
            print(f"음악 파일을 찾을 수 없음: {self.music_path}")
            return False
        
        # 캠시에서 먼저 로드 시도
        if self.load_from_cache():
            return True
        
        try:
            print(f"🎵 음악 분석 시작: {os.path.basename(self.music_path)}")
            
            # 음악 파일 로드
            print("  - 파일 로딩 중...")
            self.y, self.sr = librosa.load(self.music_path, sr=22050)
            self.duration = librosa.get_duration(y=self.y, sr=self.sr)
            print(f"  ✓ 로드 완료: {self.duration:.2f}초, 샘플링 레이트: {self.sr}Hz")
            
            # BPM 추출
            print("  - BPM 분석 중...")
            tempo, beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr)
            self.tempo = float(tempo)
            self.beat_times = librosa.frames_to_time(beat_frames, sr=self.sr)
            print(f"  ✓ BPM: {self.tempo:.1f}, 비트 수: {len(self.beat_times)}")
            
            # 온셋(타격 지점) 감지
            print("  - 온셋 분석 중...")
            onset_frames = librosa.onset.onset_detect(
                y=self.y, 
                sr=self.sr,
                hop_length=512,
                backtrack=True,
                units='frames'
            )
            self.onset_times = librosa.frames_to_time(onset_frames, sr=self.sr)
            print(f"  온셋 수: {len(self.onset_times)}")
            
            self.is_loaded = True
            print("음악 분석 완료!")
            
            # 캠시에 저장
            self.save_to_cache()
            
            return True
            
        except Exception as e:
            print(f"음악 분석 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_chart(self, difficulty='normal', start_delay=2.0):
        """
        리듬 게임 채보 생성
        
        Args:
            difficulty: 난이도 ('easy', 'normal', 'hard', 'expert')
            start_delay: 게임 시작 전 대기 시간 (초)
            
        Returns:
            list: 노트 타이밍 리스트 (초 단위)
        """
        if not self.is_loaded:
            print("음악이 로드되지 않음. load_and_analyze()를 먼저 호출하세요.")
            return []
        
        chart = []
        
        if difficulty == 'easy':
            # Easy: 주요 비트만 사용 (2박자마다)
            chart = [t + start_delay for i, t in enumerate(self.beat_times) if i % 2 == 0]
            
        elif difficulty == 'normal':
            # Normal: 온셋 중심으로 리듬 구성 (단순 비트 제외)
            # 온셋이 실제 악기/보컬 타이밍을 더 잘 반영함
            
            all_onsets = list(self.onset_times)
            all_beats = list(self.beat_times)
            
            # 1. 온셋 중심 선택
            selected_notes = []
            
            # 2. 비트는 선택적으로만 사용 (4박자마다 또는 강한 비트만)
            for i, beat in enumerate(all_beats):
                # 4박자마다만 비트 추가 (너무 반복적이지 않게)
                if i % 4 == 0:
                    selected_notes.append(beat)
            
            # 3. 온셋 중 비트와 겹치지 않는 것들 추가 (복잡한 리듬)
            for onset in all_onsets:
                min_beat_dist = min([abs(onset - bt) for bt in all_beats]) if all_beats else 1.0
                # 비트에서 0.15초 이상 떨어진 온셋 (실제 악기 타이밍)
                if min_beat_dist >= 0.15:
                    selected_notes.append(onset)
            
            selected_notes = sorted(selected_notes)
            
            # 최소 간격 필터 (0.2초 - 더 여유있게)
            filtered = []
            last_time = -1
            for t in selected_notes:
                if last_time < 0 or t - last_time >= 0.2:
                    filtered.append(t + start_delay)
                    last_time = t
            chart = filtered
            
        elif difficulty == 'hard':
            # Hard: 온셋 기반 + 복잡한 리듬 패턴
            
            all_onsets = list(self.onset_times)
            all_beats = list(self.beat_times)
            
            selected_notes = []
            
            # 1. 2박자마다 비트 추가 (기본 구조)
            for i, beat in enumerate(all_beats):
                if i % 2 == 0:
                    selected_notes.append(beat)
            
            # 2. 모든 중요한 온셋 추가 (비트에서 떨어진 것들)
            for onset in all_onsets:
                min_beat_dist = min([abs(onset - bt) for bt in all_beats]) if all_beats else 1.0
                # 비트에서 0.1초 이상 떨어진 온셋
                if min_beat_dist >= 0.1:
                    selected_notes.append(onset)
            
            selected_notes = sorted(selected_notes)
            
            # 최소 간격 (0.1초 - 빠른 리듬 허용)
            filtered = []
            last_time = -1
            for t in selected_notes:
                if last_time < 0 or t - last_time >= 0.1:
                    filtered.append(t + start_delay)
                    last_time = t
            chart = filtered
            
        elif difficulty == 'expert':
            # Expert: 모든 비트 + 모든 온셋 + 중간 보간 (0.1초 간격)
            combined = list(self.beat_times) + list(self.onset_times)
            
            # 비트 사이에 추가 노트 생성 (비트의 1/2 지점)
            beat_intervals = []
            for i in range(len(self.beat_times) - 1):
                beat_intervals.append((self.beat_times[i] + self.beat_times[i+1]) / 2)
            
            combined.extend(beat_intervals)
            combined = sorted(set(combined))
            
            # 0.1초 이상 간격
            filtered = []
            last_time = -1
            for t in combined:
                if t - last_time >= 0.1:
                    filtered.append(t + start_delay)
                    last_time = t
            chart = filtered
            
        else:
            print(f"알 수 없는 난이도: {difficulty}, normal로 설정")
            chart = [t + start_delay for t in self.beat_times]
        
        # 롱 노트 생성 (긴 비트 간격에 추가)
        chart_with_type = []
        if len(chart) > 1:
            for i in range(len(chart)):
                note_time = chart[i]
                
                # 다음 노트와의 간격이 1.5초 이상이면 롱 노트로 변환
                if i < len(chart) - 1:
                    interval = chart[i + 1] - note_time
                    if interval >= 1.5 and interval <= 3.0:
                        # 롱 노트 (간격의 70% 길이)
                        duration = interval * 0.7
                        chart_with_type.append({'time': note_time, 'type': 'long', 'duration': duration})
                        continue
                
                # 일반 노트
                chart_with_type.append({'time': note_time, 'type': 'normal', 'duration': 0})
        else:
            # 롱 노트 없이 일반 노트만
            chart_with_type = [{'time': t, 'type': 'normal', 'duration': 0} for t in chart]
        
        normal_count = sum(1 for n in chart_with_type if n['type'] == 'normal')
        long_count = sum(1 for n in chart_with_type if n['type'] == 'long')
        print(f"채보 생성 완료: 난이도={difficulty}, 일반 노트={normal_count}개, 롱 노트={long_count}개")
        return chart_with_type
    
    def get_bpm(self):
        """BPM 반환"""
        return self.tempo if self.is_loaded else 120
    
    def get_duration(self):
        """음악 길이 반환 (초)"""
        return self.duration if self.is_loaded else 0
    
    def print_info(self):
        """분석 정보 출력"""
        if not self.is_loaded:
            print("음악이 로드되지 않음")
            return
        
        print("\n" + "="*50)
        print(f"🎵 음악 정보: {os.path.basename(self.music_path)}")
        print("="*50)
        print(f"길이: {self.duration:.2f}초")
        print(f"BPM: {self.tempo:.1f}")
        print(f"비트 수: {len(self.beat_times)}")
        print(f"온셋 수: {len(self.onset_times)}")
        print(f"샘플링 레이트: {self.sr}Hz")
        print("="*50 + "\n")


def test_analyzer():
    """테스트 함수"""
    music_path = 'music/Lady Ethereal.mp3'
    
    # 분석기 생성
    analyzer = MusicAnalyzer(music_path)
    
    # 음악 분석
    if analyzer.load_and_analyze():
        # 정보 출력
        analyzer.print_info()
        
        # 난이도별 채보 생성
        for difficulty in ['easy', 'normal', 'hard']:
            chart = analyzer.generate_chart(difficulty=difficulty)
            print(f"{difficulty.upper()}: 첫 10개 노트 타이밍 = {chart[:10]}")


if __name__ == '__main__':
    test_analyzer()
