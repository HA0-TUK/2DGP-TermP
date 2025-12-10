from pico2d import *
import math
from player_state import StateMachine, FightIdleState, ParryState, RunState, DieState

class Player:
    def __init__(self):
        self.x = 90  # 화면 왼쪽
        self.y = 130  # y 위치
        self.width = 128
        self.height = 128
        
        # 패링 상태
        self.is_parrying = False
        self.parry_time = 0
        self.parry_duration = 0.4  # 공중 패링 애니메이션 시간 (8프레임 / 24fps = 0.33초)
        
        # 점프 동작
        self.is_jumping = False
        self.jump_speed = 150  # 점프 속도 (픽셀/초)
        self.jump_height = 40  # 점프 높이
        self.base_y = 130  # 기본 y 위치
        self.jump_time = 0
        self.jump_duration = 0.4  # 전체 점프 시간
        
        # 패링 단계 (스페이스 누를 때마다 5프레임씩)
        self.parry_phase = 0  # 0: 0-4프레임, 1: 5-9프레임, 2: 10-14프레임
        self.max_parry_phases = 3  # 총 3단계
        
        # 피격 상태
        self.is_hit = False
        self.hit_time = 0
        self.hit_duration = 0.5
        
        # 체력
        self.hp = 10
        self.max_hp = 10
        
        # 사망 상태
        self.is_dead = False
        
        # 애니메이션 프레임
        self.frame = 0
        self.frame_time = 0
        self.action = 'idle'  # idle, parry, hit
        
        # Nine Sols 스프라이트 시트 로드
        self.sprite_sheets = {}
        self.load_sprite_sheets()
        
        # 현재 애니메이션 설정
        self.current_anim = 'player_idle'  # 기본적으로 idle 애니메이션 시작
        self.anim_frame = 0
        self.anim_start_frame = 0  # 애니메이션 시작 프레임
        self.max_anim_frames = 0  # 재생할 최대 프레임 수 (0이면 전체 재생)
        
        # 이펙트 애니메이션 (패링 성공 시 추가로 재생)
        self.effect_anim = None
        self.effect_frame = 0
        self.effect_frame_time = 0
        self.is_effect_playing = False
        
        # 상태별 타임아웃 변수
        self.fight_idle_time = 0
        self.parry_input_time = 0
        self.run_time = 0
        
        # 상태 머신 초기화
        self.state_machine = StateMachine(self)
        self.state_machine.start(RunState)
    
    def load_sprite_sheets(self):
        """Nine Sols 패링 스프라이트 시트 로드"""
        try:
            # 플레이어 Idle 애니메이션 (Standingidle)
            self.sprite_sheets['player_idle'] = {
                'image': load_image('sprite_sheets/player_standing_idle.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 8,
                'total_frames': 8,
                'fps': 8
            }
            print(f"  - player_idle (Standingidle) 로드 완료")
            
            # 플레이어 Fighting Idle 애니메이션
            self.sprite_sheets['player_fighting_idle'] = {
                'image': load_image('sprite_sheets/player_fighting_idle.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 6,
                'total_frames': 6,
                'fps': 12
            }
            print(f"  - player_fighting_idle 로드 완료")
            
            # 플레이어 Run 애니메이션
            self.sprite_sheets['player_run'] = {
                'image': load_image('sprite_sheets/player_run.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 12,
                'total_frames': 12,
                'fps': 60
            }
            print(f"  - player_run 로드 완료")
            
            # 플레이어 Die 애니메이션
            self.sprite_sheets['player_die'] = {
                'image': load_image('sprite_sheets/player_die.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 24,  
                'total_frames': 24,
                'fps': 24
            }
            print(f"  - player_die 로드 완료 ")
            
            # 플레이어 피격 애니메이션 (Hurt_2: 0~10, 13~15 프레임)
            self.sprite_sheets['player_hurt_2'] = {
                'image': load_image('sprite_sheets/player_hurt_2.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 14,
                'total_frames': 14,
                'fps': 30  # 20에서 30으로 증가 (1.5배 빠르게)
            }
            print(f"  - player_hurt_2 로드 완료")
            
            # 플레이어 패링 ABC 애니메이션 (메인 패링 모션)
            self.sprite_sheets['player_parry'] = {
                'image': load_image('sprite_sheets/player_parry_abc.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 15,
                'total_frames': 15,
                'fps': 24
            }
            print(f"  - player_parry (ABC) 로드 완료")
            
            # 플레이어 공중 패링 애니메이션 (새로운!)
            self.sprite_sheets['player_parry_sky'] = {
                'image': load_image('sprite_sheets/player_parry_sky.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 8,
                'total_frames': 8,
                'fps': 24
            }
            print(f"  - player_parry_sky (공중 패링) 로드 완료")

            
            # 플레이어 공중 패링 애니메이션
            self.sprite_sheets['player_sky'] = {
                'image': load_image('sprite_sheets/player_parry_sky.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 14,
                'total_frames': 14,
                'fps': 24
            }
            
            # 플레이어 패링 카운터 애니메이션
            self.sprite_sheets['player_counter'] = {
                'image': load_image('sprite_sheets/player_parry_counter.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 14,
                'total_frames': 14,
                'fps': 24
            }
            
            # 패링 준비 이펙트
            self.sprite_sheets['prepare'] = {
                'image': load_image('sprite_sheets/ParryCounterPrepare_sheet.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 8,
                'total_frames': 16,
                'fps': 30
            }
            
            # 패링 성공 이펙트 (정확한 타이밍)
            self.sprite_sheets['accurate'] = {
                'image': load_image('sprite_sheets/ParrySparkAccurate_sheet.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 8,
                'total_frames': 7,
                'fps': 30
            }
            
            # 공중 패링 이펙트 (새로운!)
            self.sprite_sheets['parry_sky_effect'] = {
                'image': load_image('sprite_sheets/effect_parry_sky.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 6,
                'total_frames': 6,
                'fps': 30
            }
            print(f"  - parry_sky_effect (공중 패링 이펙트) 로드 완료")
            
            # 반격 이펙트
            self.sprite_sheets['counter_effect'] = {
                'image': load_image('sprite_sheets/ParryCounterAttack_sheet.png'),
                'sprite_width': 512,
                'sprite_height': 512,
                'sprites_per_row': 8,
                'total_frames': 9,
                'fps': 30
            }
            
            print("Nine Sols 패링 스프라이트 로드 완료")
            print(f"  총 {len(self.sprite_sheets)}개 스프라이트 시트 로드됨")
        except Exception as e:
            print(f"스프라이트 로드 실패: {e}")
            import traceback
            traceback.print_exc()
            self.sprite_sheets = {}
    
    def update(self, dt):
        # HP가 0 이하면 Die 상태로 전환
        if self.hp <= 0 and not self.is_dead:
            print(f"HP 0 도달! Die 이벤트 발생")
            self.state_machine.add_event(('DIE', 0))
        
        # 점프 동작 업데이트
        if self.is_jumping:
            self.jump_time += dt
            if self.jump_time >= self.jump_duration:
                # 점프 종료
                self.is_jumping = False
                self.y = self.base_y
                self.jump_time = 0
            else:
                # 포물선 점프 (사인 함수 사용)
                import math
                progress = self.jump_time / self.jump_duration
                self.y = self.base_y + math.sin(progress * math.pi) * self.jump_height
        
        # 상태 머신 업데이트
        self.state_machine.update()
        
        # 메인 애니메이션 프레임 업데이트
        if self.current_anim:
            anim_data = self.sprite_sheets.get(self.current_anim)
            if anim_data:
                self.frame_time += dt
                frame_duration = 1.0 / anim_data['fps']
                
                if self.frame_time >= frame_duration:
                    self.frame_time = 0
                    self.anim_frame += 1
                    
                    # max_anim_frames가 설정되어 있으면 시작 프레임 + max_frames까지만 재생
                    if self.max_anim_frames > 0:
                        frame_limit = self.anim_start_frame + self.max_anim_frames
                    else:
                        frame_limit = anim_data['total_frames']
                    
                    # 애니메이션 종료 체크
                    if self.anim_frame >= frame_limit:
                        # idle/run 애니메이션은 루프
                        if self.current_anim in ['player_idle', 'player_fighting_idle', 'player_run']:
                            self.anim_frame = 0  # 처음부터 다시 재생
                        elif self.current_anim == 'player_die':
                            self.anim_frame = frame_limit - 1
                            if not hasattr(self, '_die_anim_message_shown'):
                                print(f"Die 애니메이션 완료 - 사망")
                                self._die_anim_message_shown = True
                        elif self.current_anim == 'player_parry':
                            # 패링 애니메이션은 루프
                            self.anim_frame = frame_limit - 1
        
        # 이펙트 애니메이션 업데이트
        if self.is_effect_playing and self.effect_anim:
            effect_data = self.sprite_sheets.get(self.effect_anim)
            if effect_data:
                self.effect_frame_time += dt
                frame_duration = 1.0 / effect_data['fps']
                
                if self.effect_frame_time >= frame_duration:
                    self.effect_frame_time = 0
                    self.effect_frame += 1
                    
                    # 이펙트 종료 체크
                    if self.effect_frame >= effect_data['total_frames']:
                        self.is_effect_playing = False
                        self.effect_anim = None
                        self.effect_frame = 0
                        print(f"이펙트 종료")
        
        # 패링 상태 업데이트
        if self.is_parrying:
            self.parry_time += dt
            if self.parry_time >= self.parry_duration:
                self.is_parrying = False
                self.parry_time = 0
                if self.action == 'parry':
                    self.action = 'idle'
        
        # 피격 상태 업데이트
        if self.is_hit:
            self.hit_time += dt
            if self.hit_time >= self.hit_duration:
                self.is_hit = False
                self.hit_time = 0
                self.action = 'idle'
    
    def parry(self):
        """패링 액션 실행 - 상태 머신에 SPACE_DOWN 이벤트 전달"""
        if not self.is_dead:  # 죽지 않았을 때만 패링 가능
            self.state_machine.add_event(('SPACE_DOWN', 0))
            return True
        return False
    
    def parry_success(self, is_perfect=False):
        """패링 성공 시 호출 - 성공 이펙트 재생"""
        if is_perfect:
            # 완벽한 패링 - 반격 이펙트
            self.start_effect('counter_effect')
            print("Perfect 패링! 반격 이펙트")
        else:
            # 일반 패링 - 공중 패링 이펙트
            self.start_effect('parry_sky_effect')
            print("Good 패링! 공중 스파크 이펙트")
    
    def start_animation(self, anim_name, start_frame=0, max_frames=0):
        """애니메이션 시작
        
        Args:
            anim_name: 애니메이션 이름
            start_frame: 시작 프레임 번호
            max_frames: 재생할 최대 프레임 수 (0이면 전체 재생)
        """
        if anim_name in self.sprite_sheets:
            self.current_anim = anim_name
            self.anim_frame = start_frame
            self.anim_start_frame = start_frame
            self.frame_time = 0
            self.max_anim_frames = max_frames
            
            if max_frames > 0:
                frame_info = f"{start_frame}~{start_frame + max_frames - 1} 프레임"
            else:
                frame_info = f"전체 {self.sprite_sheets[anim_name]['total_frames']} 프레임"
            print(f"애니메이션 시작: {anim_name} ({frame_info})")
        else:
            print(f"애니메이션 '{anim_name}'를 찾을 수 없음. 사용 가능: {list(self.sprite_sheets.keys())}")
    
    def start_effect(self, effect_name):
        """이펙트 애니메이션 시작"""
        if effect_name in self.sprite_sheets:
            self.effect_anim = effect_name
            self.effect_frame = 0
            self.effect_frame_time = 0
            self.is_effect_playing = True
            print(f"이펙트 시작: {effect_name}")
        else:
            print(f"이펙트 '{effect_name}'를 찾을 수 없음")
    
    def take_damage(self):
        """피해를 받음 - HIT 이벤트 발생"""
        if not self.is_dead:  # 죽지 않았을 때만 피해
            # HIT 이벤트 발생 (HitState에서 실제 피해 처리)
            self.state_machine.add_event(('HIT', 0))
            return True
        return False
    
    def draw(self):
        """상태 머신에게 그리기 위임"""
        self.state_machine.draw()
        
        # 이펙트는 항상 그리기
        self.draw_effect()
    
    def draw_animation(self):
        """현재 애니메이션 그리기 (상태별로 호출됨)"""
        # 스프라이트 시트가 로드되었는지 확인
        if not self.sprite_sheets or self.current_anim not in self.sprite_sheets:
            return
        
        # Nine Sols 애니메이션 그리기
        anim_data = self.sprite_sheets[self.current_anim]
        sprite_sheet = anim_data['image']
        sprite_width = anim_data['sprite_width']
        sprite_height = anim_data['sprite_height']
        total_frames = anim_data['total_frames']
        
        # 프레임 범위 체크
        current_frame = min(self.anim_frame, total_frames - 1)
        
        # 현재 프레임의 위치 계산 (한 행에 모든 프레임이 있음)
        frame_x = current_frame * sprite_width
        
        # 스프라이트 그리기 (중앙 정렬, 크기 조절)
        draw_scale = 0.25  
        draw_width = int(sprite_width * draw_scale)
        draw_height = int(sprite_height * draw_scale)
        
        sprite_sheet.clip_draw(
            int(frame_x), 0, int(sprite_width), int(sprite_height),
            int(self.x), int(self.y), int(draw_width), int(draw_height)
        )
    
    def draw_effect(self):
        """이펙트 그리기 (플레이어 위에 오버레이)"""
        if not self.is_effect_playing or not self.effect_anim:
            return
            
        if self.effect_anim not in self.sprite_sheets:
            return
            
        effect_data = self.sprite_sheets[self.effect_anim]
        effect_sheet = effect_data['image']
        effect_width = effect_data['sprite_width']
        effect_height = effect_data['sprite_height']
        total_frames = effect_data['total_frames']
        
        # 프레임 범위 체크
        current_frame = min(self.effect_frame, total_frames - 1)
        
        # 현재 프레임의 위치 계산
        frame_x = current_frame * effect_width
        
        # 이펙트 그리기
        draw_scale = 0.5 
        draw_width = int(effect_width * draw_scale)
        draw_height = int(effect_height * draw_scale)
        
        effect_sheet.clip_draw(
            int(frame_x), 0, int(effect_width), int(effect_height),
            int(self.x), int(self.y), int(draw_width), int(draw_height)
        )
        

    
    def draw_hp_bar(self):
        pass
    
    def is_alive(self):
        return self.hp > 0
    
    def get_parry_window(self):
        return self.is_parrying
