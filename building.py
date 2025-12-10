from pico2d import *
import time
from music_analyzer import MusicAnalyzer
import pygame

class RhythmNote:
    note_image = None
    long_note_effect = None  # 롱 노트 이펙트 이미지
    
    @classmethod
    def load_images(cls):
        if cls.note_image is None:
            try:
                cls.note_image = load_image('originSprite/Bow/NormalArrow.png')
            except Exception as e:
                print(f"노트 이미지 로드 실패: {e}")
                cls.note_image = None
        
        if cls.long_note_effect is None:
            try:
                cls.long_note_effect = load_image('originSprite/Bow/Lv1光束.png')
            except Exception as e:
                print(f"롱 노트 이펙트 로드 실패: {e}")
                cls.long_note_effect = None
    
    def __init__(self, beat_time, note_type='normal', duration=0):
        self.beat_time = beat_time  # 언제 쳐야 하는지
        self.note_type = note_type  # 노트 타입 
        self.duration = duration  # 롱 노트 지속 시간 
        self.is_hit = False
        self.judgment = None  # 'perfect', 'good', 'bad', 'miss'
        
        # 롱 노트 상태
        self.is_holding = False  # 홀딩 중인지
        self.hold_start_time = 0  # 홀딩 시작 시간
        self.hold_completed = False  # 홀딩 완료 여부
        
        # 시각적 표현
        self.x = 1080  
        self.y = 130 
        self.target_x = 120  # 플레이어 위치
        
        self.arrow_width = 289
        self.arrow_height = 80
        self.scale = 0.25 
        self.draw_width = int(self.arrow_width * self.scale)  
        self.draw_height = int(self.arrow_height * self.scale)  
        
        self.collision_width = self.draw_width
        self.collision_height = self.draw_height
        
        # 패링 상태
        self.is_parried = False  # 패링되었는지
        self.parry_speed = 1800  
        self.parry_alpha = 0.5  

        if RhythmNote.note_image is None:
            RhythmNote.load_images()
    
    def get_collision_box(self):
        half_w = self.collision_width // 2
        half_h = self.collision_height // 2
        return (
            self.x - half_w,
            self.y - half_h,
            self.x + half_w,
            self.y + half_h
        )
        
    def update(self, dt, current_time):
        if self.is_parried:
            # 패링된 화살표는 오른쪽으로 날아감
            self.x += self.parry_speed * dt
            # 화면 밖으로 나가면 제거 대상
            if self.x > 1200:
                self.is_hit = True
        elif self.is_holding:
            # 롱 노트 홀딩 중 - 판정선에서 흡수됨
            # 노트는 판정선(target_x)에 고정
            self.x = self.target_x
            
            # 홀딩 시간 체크
            hold_elapsed = current_time - self.hold_start_time
            if hold_elapsed >= self.duration:
                # 홀딩 완료 - 노트 제거 및 완료 플래그 설정
                self.is_hit = True
                self.judgment = 'perfect'
                self.hold_completed = True  # 홀딩 완료 플래그
        else:
            # 노트가 목표 지점으로 이동
            time_to_beat = self.beat_time - current_time
            if time_to_beat > 0:
                progress = max(0, (2.0 - time_to_beat) / 2.0)
                self.x = 1080 - (1800 * progress) 
            else:
                self.x = self.target_x
    
    def parry(self):
        self.is_parried = True
    
    def draw(self, current_time):
        if self.is_hit:
            return
        
        time_to_beat = self.beat_time - current_time
        
        if not self.is_parried:
            if time_to_beat > 2.0:  
                return
        
        if RhythmNote.note_image:
            flip = '' if self.is_parried else 'h'  # 패링되면 정방향, 아니면 좌우반전

            # 롱 노트
            if self.note_type == 'long' and self.duration > 0 and RhythmNote.long_note_effect:
                # 홀딩 중일 때는 남은 시간만큼만 그리기
                if self.is_holding and not self.hold_completed:
                    # 남은 시간 계산
                    hold_elapsed = current_time - self.hold_start_time
                    remaining_time = max(0, self.duration - hold_elapsed)
                    
                    # 남은 시간에 비례하는 길이
                    visible_length = int(remaining_time * 900)
                    
                    if visible_length > 10:  # 최소 길이
                        effect_center_x = int(self.x + visible_length / 2)
                        effect_center_y = int(self.y)
                        effect_height = int(RhythmNote.long_note_effect.h * 0.25)
                        
                        RhythmNote.long_note_effect.composite_draw(
                            0, 'h',
                            effect_center_x, effect_center_y,
                            visible_length, effect_height
                        )
                elif not self.is_parried and not self.is_holding:
                    # 일반 
                    full_effect_length = int(self.duration * 900)  
                    effect_center_x = int(self.x + full_effect_length / 2)
                    effect_center_y = int(self.y)
                    effect_height = int(RhythmNote.long_note_effect.h * 0.25)
                    
                    RhythmNote.long_note_effect.composite_draw(
                        0, 'h',
                        effect_center_x, effect_center_y,
                        full_effect_length, effect_height
                    )
            # 일반 노트
            if self.note_type != 'long' or self.is_parried:
                if self.is_parried:
                    RhythmNote.note_image.opacify(self.parry_alpha)
                    RhythmNote.note_image.composite_draw(
                        0, flip,
                        int(self.x), int(self.y), 
                        self.draw_width, self.draw_height
                    )
                    RhythmNote.note_image.opacify(1.0)  # 투명도 원상복구
                else:
                    RhythmNote.note_image.composite_draw(
                        0, flip,
                        int(self.x), int(self.y), 
                        self.draw_width, self.draw_height
                    )


class RhythmManager:
    """리듬 게임 관리자 - 음악 분석 기반"""
    def __init__(self, music_path='music/M2U.mp3', difficulty='hard'):
        """
        Args:
            music_path: 음악 파일 경로
            difficulty: 난이도 ('easy', 'normal', 'hard')
        """
        self.music_path = music_path
        self.difficulty = difficulty
        self.start_time = None  
        self.current_time = 0
        self.music_start_delay = 3.0  
        
        # 음악 분석
        self.analyzer = MusicAnalyzer(music_path)
        self.bpm = 120  # 기본값
        self.duration = 0
        
        # 노트 리스트
        self.notes = []
        self.active_notes = []
        self.chart_data = []  # 채보 데이터 (초 단위)
        
        # 판정 관련
        self.perfect_window = 0.05 
        self.good_window = 0.1    
        self.bad_window = 0.15   
        
        # 콜백
        self.on_miss_callback = None  # Miss 시 호출할 콜백
        self.on_hold_complete_callback = None  # 홀딩 완료 시 호출할 콜백
        self.player_ref = None  # 홀딩 완료 시 상태 전환용
        
        # 점수
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        
        # 음악 재생
        self.music_loaded = False
        self.music_playing = False
        
        # 음악 분석 및 채보 생성
        self.load_music_and_generate_chart()
    
    def load_music_and_generate_chart(self):
        """음악 로드 및 채보 생성"""
        # 음악 분석
        if self.analyzer.load_and_analyze():
            self.bpm = self.analyzer.get_bpm()
            self.duration = self.analyzer.get_duration()
            
            # 채보 생성
            self.chart_data = self.analyzer.generate_chart(
                difficulty=self.difficulty,
                start_delay=self.music_start_delay
            )
            
            
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

                
                pygame.mixer.music.load(self.music_path)
                self.music_loaded = True
            except Exception as e:
                self.music_loaded = False
        else:
            # 분석 실패 시 기본 패턴 생성
            self.generate_fallback_pattern()
    
    def generate_fallback_pattern(self):
        self.bpm = 120
        beat_interval = 60.0 / self.bpm
        
        for i in range(40):
            note_time = self.music_start_delay + i * beat_interval
            self.chart_data.append(note_time)
        
    
    def start_music(self):
        if self.music_loaded and not self.music_playing:
            try:
                # 음악 재생 
                pygame.mixer.music.play(0)  # 0 = 한 번만 재생
                self.music_playing = True
                return True
            except Exception as e:
                print(f"음악 재생 실패: {e}")
                return False
        return False
    
    def update(self, dt):
        # 첫 업데이트에서 타이머 시작 
        if self.start_time is None:
            self.start_time = time.time()
            # 채보 데이터로 노트 생성
            self.create_notes_from_chart()
        
        # 현재 시간 업데이트 
        elapsed_time = time.time() - self.start_time
        
        # 음악 시작 전이면 current_time을 음수로 설정
        self.current_time = elapsed_time - self.music_start_delay
        
        # music_start_delay 후에 음악 재생
        if not self.music_playing and elapsed_time >= self.music_start_delay:
            self.start_music()
        
        # 활성 노트 업데이트
        for note in self.active_notes[:]:
            note.update(dt, self.current_time)
            
            # 홀딩 완료 체크
            if note.is_holding and hasattr(note, 'hold_completed') and note.hold_completed:
                # 홀딩 완료 - RunState로 전환
                if self.player_ref:
                    from player_state import RunState
                    self.player_ref.state_machine.add_event(('HOLD_COMPLETE', 0))
                    print("롱 노트 홀딩 완료! RunState로 전환")
                note.hold_completed = False  # 플래그 리셋
            
            # 놓친 노트 처리 (패링되지 않은 노트만)
            if not note.is_hit and not note.is_parried and not note.is_holding:

                if note.x < 26:  # 플레이어 패리 범위의 왼쪽 경계
                    note.judgment = 'miss'
                    note.is_hit = True  # 즉시 사라지도록 표시
                    self.combo = 0
                    # Miss 콜백 호출
                    if self.on_miss_callback:
                        self.on_miss_callback()
                        print("Miss! 데미지")
                    self.active_notes.remove(note)
                # 시간 기반 Miss 판정 
                else:
                    time_passed = self.current_time - note.beat_time
                    if time_passed > self.bad_window:
                        note.judgment = 'miss'
                        note.is_hit = True
                        self.combo = 0
                        if self.on_miss_callback:
                            self.on_miss_callback()
                            print("Miss! 데미지")
                        self.active_notes.remove(note)
        
        # 새로운 노트 활성화
        for note in self.notes[:]:
            if self.current_time >= note.beat_time - 2.0:
                self.active_notes.append(note)
                self.notes.remove(note)
    
    def create_notes_from_chart(self):
        """채보 데이터로부터 노트 생성"""
        self.notes = []
        for note_data in self.chart_data:
            if isinstance(note_data, dict):
                # 새로운 형식: {'time': float, 'type': str, 'duration': float}
                self.notes.append(RhythmNote(
                    beat_time=note_data['time'],
                    note_type=note_data.get('type', 'normal'),
                    duration=note_data.get('duration', 0)
                ))
            else:
                # 이전 형식: float (시간만)
                self.notes.append(RhythmNote(beat_time=note_data))
        
        normal_count = sum(1 for n in self.notes if n.note_type == 'normal')
        long_count = sum(1 for n in self.notes if n.note_type == 'long')
        print(f"✓ 노트 생성 완료: 일반 {normal_count}개, 롱 {long_count}개")
    
    def try_hit(self, hit_time=None, player=None):
        """플레이어의 입력 처리 - 충돌 기반 패링"""
        if hit_time is None:
            hit_time = self.current_time
        
        # player와 충돌하는 노트 찾기
        parried_note = None
        
        if player:
            # 플레이어 충돌박스 (오른쪽으로 확장하여 패링 범위 증가)
            player_left = player.x - 64
            player_right = player.x + 120  # 64 -> 120으로 확장 (오른쪽 범위 증가)
            player_bottom = player.y - 64
            player_top = player.y + 64
            
            for note in self.active_notes:
                if not note.is_hit and not note.is_parried:
                    # 노트 충돌박스
                    note_box = note.get_collision_box()
                    
                    # AABB 충돌 체크
                    if (player_left < note_box[2] and player_right > note_box[0] and
                        player_bottom < note_box[3] and player_top > note_box[1]):
                        parried_note = note
                        break
        
        if parried_note is None:
            return 'miss', False, None
        
        # 롱 노트인 경우 홀딩 시작
        if parried_note.note_type == 'long' and not parried_note.is_holding:
            parried_note.is_holding = True
            parried_note.hold_start_time = hit_time
            print(f"롱 노트 홀딩 시작! 길이: {parried_note.duration:.2f}초")
            return 'holding', True, parried_note
        
        # 일반 노트 패링 - 화살표를 반대로 날림
        parried_note.parry()
        
        # 판정 계산 (타이밍 기반)
        time_diff = abs(hit_time - parried_note.beat_time)
        
        if time_diff <= self.perfect_window:
            judgment = 'perfect'
            points = 300
            success = True
        elif time_diff <= self.good_window:
            judgment = 'good'
            points = 200
            success = True
        elif time_diff <= self.bad_window:
            judgment = 'bad'
            points = 100
            success = True  # 패링은 성공했지만 타이밍이 나쁨
        else:
            judgment = 'good'  # 충돌했으면 최소 good
            points = 150
            success = True
        
        # 점수 및 콤보 처리
        if success:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            combo_bonus = min(self.combo * 10, 500)
            self.score += points + combo_bonus
        else:
            self.combo = 0
        
        # 노트 판정 저장 (패링된 화살은 제거하지 않고 반대로 날아감)
        parried_note.judgment = judgment
        # is_hit은 설정하지 않음 - 패링된 화살은 계속 날아가야 함
        # active_notes에서도 제거하지 않음 - update()에서 화면 밖으로 나갈 때 제거됨
        
        return judgment, success, parried_note
    
    def release_hold(self):
        """홀딩 중인 롱 노트 릴리즈 처리"""
        for note in self.active_notes:
            if note.is_holding:
                # 홀딩 중이던 노트를 실패 처리
                note.is_holding = False
                note.is_hit = True
                note.judgment = 'miss'
                self.combo = 0
                print("롱 노트 홀딩 실패!")
                # Miss 콜백 호출
                if self.on_miss_callback:
                    self.on_miss_callback()
                break
    
    def draw(self):
        """리듬 시스템 그리기"""
        # 활성 노트 그리기
        for note in self.active_notes:
            note.draw(self.current_time)
        
        # UI 정보
        self.draw_ui()
    
    def draw_ui(self):
        """UI 정보 그리기"""
        # UI는 필요시 추가
        pass
    
    def get_current_beat(self):
        """현재 박자 위치 반환"""
        elapsed = self.current_time - self.start_time
        return elapsed / self.beat_interval
    
    def is_finished(self):
        """패턴이 모두 끝났는지 확인"""
        # 모든 노트가 처리되었고, 음악도 끝났는지 체크
        all_notes_done = len(self.notes) == 0 and len(self.active_notes) == 0
        
        # 음악이 재생 중인지 확인
        music_finished = False
        if self.music_loaded and self.music_playing:
            music_finished = not pygame.mixer.music.get_busy()
        
        return all_notes_done or (self.music_playing and music_finished)
    
    def stop_music(self):
        """음악 정지"""
        if self.music_loaded and self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
            print("🔇 음악 정지")
