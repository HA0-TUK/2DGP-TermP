from pico2d import *
import time
import math
import random

class RhythmNote:
    """리듬 노트 클래스"""
    # 클래스 변수로 이미지 공유
    note_image = None
    
    @classmethod
    def load_images(cls):
        """노트 이미지 로드 (한 번만)"""
        if cls.note_image is None:
            try:
                cls.note_image = load_image('originSprite/Bow/NormalArrow.png')
                print("✓ NormalArrow.png 로드 완료")
            except Exception as e:
                print(f"노트 이미지 로드 실패: {e}")
                cls.note_image = None
    
    def __init__(self, beat_time, note_type='normal'):
        self.beat_time = beat_time  # 언제 쳐야 하는지
        self.note_type = note_type  # 노트 타입
        self.is_hit = False
        self.judgment = None  # 'perfect', 'good', 'bad', 'miss'
        
        # 시각적 표현
        self.x = 1080  # 화면 오른쪽 끝에서 시작
        self.y = 130  # 플레이어 y 위치에 맞춤
        self.target_x = 120  # 플레이어 위치
        
        # NormalArrow 원본 크기: 289x80
        # 가로세로 비율 유지하면서 스케일 조정
        self.arrow_width = 289
        self.arrow_height = 80
        self.scale = 0.25  # 스케일 팩터 (0.5의 절반 = 0.25)
        self.draw_width = int(self.arrow_width * self.scale)  # 72
        self.draw_height = int(self.arrow_height * self.scale)  # 20
        
        # 충돌박스도 스프라이트 크기에 맞춤 (정사각형이 아닌 직사각형)
        self.collision_width = self.draw_width
        self.collision_height = self.draw_height
        
        # 패링 상태
        self.is_parried = False  # 패링되었는지
        self.parry_speed = 300  # 패링 후 날아가는 속도 (픽셀/초)
        
        # 이미지가 로드되지 않았으면 로드
        if RhythmNote.note_image is None:
            RhythmNote.load_images()
    
    def get_collision_box(self):
        """충돌박스 반환 (left, bottom, right, top)"""
        half_w = self.collision_width // 2
        half_h = self.collision_height // 2
        return (
            self.x - half_w,
            self.y - half_h,
            self.x + half_w,
            self.y + half_h
        )
        
    def update(self, dt, current_time):
        """노트 업데이트"""
        if self.is_parried:
            # 패링된 화살표는 오른쪽으로 날아감
            self.x += self.parry_speed * dt
            # 화면 밖으로 나가면 제거 대상
            if self.x > 1200:
                self.is_hit = True
        else:
            # 노트가 목표 지점으로 이동
            time_to_beat = self.beat_time - current_time
            if time_to_beat > 0:
                # 2초 전부터 노트가 나타남
                progress = max(0, (2.0 - time_to_beat) / 2.0)
                self.x = 1080 - (990 * progress)  # 1080에서 90까지 이동
            else:
                self.x = self.target_x
    
    def parry(self):
        """화살표를 패링함"""
        self.is_parried = True
        print(f"화살표 패링! 반대로 날아감")
    
    def draw(self, current_time):
        """노트 그리기"""
        if self.is_hit:
            return
        
        # 시간 계산 (패링 여부 관계없이)
        time_to_beat = self.beat_time - current_time
        
        # 패링되지 않은 경우에만 시간 체크
        if not self.is_parried:
            # 노트가 화면에 나타날 시간인지 확인
            if time_to_beat > 2.0:  # 2초 전부터 표시
                return
        
        # NormalArrow 이미지 그리기 (가로세로 비율 유지 + 좌우반전)
        if RhythmNote.note_image:
            # 패링 여부에 따라 방향 결정
            flip = '' if self.is_parried else 'h'  # 패링되면 정방향, 아니면 좌우반전
            
            RhythmNote.note_image.composite_draw(
                0, flip,
                int(self.x), int(self.y), 
                self.draw_width, self.draw_height
            )


class RhythmManager:
    """리듬 게임 관리자"""
    def __init__(self):
        self.bpm = 120  # 분당 박자 수
        self.beat_interval = 60.0 / self.bpm  # 박자 간격
        self.start_time = time.time()
        self.current_time = 0
        
        # 노트 리스트
        self.notes = []
        self.active_notes = []
        
        # 판정 관련
        self.perfect_window = 0.05  # ±0.05초
        self.good_window = 0.1     # ±0.1초
        self.bad_window = 0.1     # ±0.1초
        
        # 콜백
        self.on_miss_callback = None  # Miss 시 호출할 콜백
        
        # 점수
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        
        # 무한 생성을 위한 변수
        self.last_pattern_beat = 4  # 마지막으로 생성된 패턴의 박자 위치
        
        # 패턴 생성
        self.generate_initial_pattern()
    
    def generate_initial_pattern(self):
        """초기 리듬 패턴 생성 (리듬세상 스타일)"""
        for _ in range(3):  # 처음에 3개 패턴 생성
            self.add_pattern()
    
    def add_pattern(self):
        """새로운 패턴 추가 (무한 생성용)"""
        patterns = [
            # 기본 4박자
            [1, 2, 3, 4],
            # 빠른 연타
            [1, 1.5, 2, 2.5],
            # 신코페이션
            [1, 1.75, 2.5, 3.25],
            # 복잡한 패턴
            [1, 1.25, 1.75, 2.25, 3, 3.5]
        ]
        
        pattern = random.choice(patterns)
        for beat in pattern:
            note_time = self.start_time + (self.last_pattern_beat + beat) * self.beat_interval
            self.notes.append(RhythmNote(note_time))
        
        self.last_pattern_beat += 6  # 각 패턴 사이에 여유
    
    def update(self, dt):
        """리듬 매니저 업데이트"""
        self.current_time = time.time()
        
        # 활성 노트 업데이트
        for note in self.active_notes[:]:
            note.update(dt, self.current_time)
            
            # 놓친 노트 처리 (패링되지 않은 노트만)
            if not note.is_hit and not note.is_parried and self.current_time - note.beat_time > self.bad_window:
                note.judgment = 'miss'
                note.is_hit = True
                self.combo = 0
                # Miss 콜백 호출
                if self.on_miss_callback:
                    self.on_miss_callback()
                    print("Miss! 데미지")
                self.active_notes.remove(note)
        
        # 새로운 노트 활성화
        for note in self.notes[:]:
            if self.current_time >= note.beat_time - 2.0:  # 2초 전부터 활성화
                self.active_notes.append(note)
                self.notes.remove(note)
        
        # 노트가 부족하면 새 패턴 추가 (무한 생성)
        if len(self.notes) < 10:  # 대기 중인 노트가 10개 미만이면
            self.add_pattern()
    
    def try_hit(self, hit_time=None, player=None):
        """플레이어의 입력 처리 - 충돌 기반 패링"""
        if hit_time is None:
            hit_time = self.current_time
        
        # player와 충돌하는 노트 찾기
        parried_note = None
        
        if player:
            # 플레이어 충돌박스 (간단히 중심점 기준)
            player_left = player.x - 64
            player_right = player.x + 64
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
        
        # 패링 성공 - 화살표를 반대로 날림
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
        
        # 노트 판정 저장 (제거하지 않음 - 날아가는 모습을 봐야 함)
        parried_note.judgment = judgment
        
        return judgment, success, parried_note
    
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
        return len(self.notes) == 0 and len(self.active_notes) == 0
