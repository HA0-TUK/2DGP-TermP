from pico2d import *
import time

# 상태 정의
class FightIdleState:
      
    def enter(player, e):
        player.current_anim = 'player_fighting_idle'
        player.anim_frame = 0
        player.max_anim_frames = 0
        player.fight_idle_time = time.time()
        print("FightIdleState 진입")
    
      
    def exit(player, e):
        pass
    
      
    def do(player):
        # 0.3초 후
        if time.time() - player.fight_idle_time > 0.3:
            player.state_machine.add_event(('TIME_OUT', 0))
    
      
    def draw(player):
        # Fighting Idle 애니메이션 그리기
        if 'player_fighting_idle' in player.sprite_sheets:
            anim_data = player.sprite_sheets['player_fighting_idle']
            sprite_sheet = anim_data['image']
            sprite_width = anim_data['sprite_width']
            sprite_height = anim_data['sprite_height']
            total_frames = anim_data['total_frames']
            
            current_frame = min(player.anim_frame, total_frames - 1)
            frame_x = current_frame * sprite_width
            
            draw_scale = 0.25
            draw_width = int(sprite_width * draw_scale)
            draw_height = int(sprite_height * draw_scale)
            
            sprite_sheet.clip_draw(
                int(frame_x), 0, int(sprite_width), int(sprite_height),
                int(player.x), int(player.y), int(draw_width), int(draw_height)
            )

class RunState:
      
    def enter(player, e):
        player.current_anim = 'player_run'
        player.anim_frame = 0
        player.max_anim_frames = 0

        player.run_time = time.time()
        print("RunState 진입")
    
      
    def exit(player, e):
        pass
    
      
    def do(player):
        # Run 애니메이션은 계속 루프
        pass
    
      
    def draw(player):
        # Run 애니메이션 그리기
        if 'player_run' in player.sprite_sheets:
            anim_data = player.sprite_sheets['player_run']
            sprite_sheet = anim_data['image']
            sprite_width = anim_data['sprite_width']
            sprite_height = anim_data['sprite_height']
            total_frames = anim_data['total_frames']
            
            current_frame = min(player.anim_frame, total_frames - 1)
            frame_x = current_frame * sprite_width
            
            draw_scale = 0.25
            draw_width = int(sprite_width * draw_scale)
            draw_height = int(sprite_height * draw_scale)
            
            sprite_sheet.clip_draw(
                int(frame_x), 0, int(sprite_width), int(sprite_height),
                int(player.x), int(player.y), int(draw_width), int(draw_height)
            )

class DieState:
      
    def enter(player, e):
        player.current_anim = 'player_die'
        player.anim_frame = 0
        player.max_anim_frames = 0  # 전체 프레임 재생
        player.is_dead = True
        print("DieState 진입 - 게임 오버")
    
      
    def exit(player, e):
        pass

      
    def do(player):
        # Die 애니메이션은 한 번만 재생되고 마지막 프레임에서 멈춤
        pass
    
      
    def draw(player):
        # Die 애니메이션 그리기
        if 'player_die' in player.sprite_sheets:
            anim_data = player.sprite_sheets['player_die']
            sprite_sheet = anim_data['image']
            sprite_width = anim_data['sprite_width']
            sprite_height = anim_data['sprite_height']
            total_frames = anim_data['total_frames']
            
            current_frame = min(player.anim_frame, total_frames - 1)
            frame_x = current_frame * sprite_width
            
            draw_scale = 0.25
            draw_width = int(sprite_width * draw_scale)
            draw_height = int(sprite_height * draw_scale)
            
            sprite_sheet.clip_draw(
                int(frame_x), 0, int(sprite_width), int(sprite_height),
                int(player.x), int(player.y), int(draw_width), int(draw_height)
            )

class ParryState:

    def enter(player, e):
        player.is_parrying = True
        import time
        player.parry_input_time = time.time()  # 마지막 입력 시간 기록 또는 갱신
        
        # 공중 패링 애니메이션 사용 (전체 재생)
        player.current_anim = 'player_parry_sky'
        player.anim_frame = 0
        player.anim_start_frame = 0
        player.max_anim_frames = 0  # 전체 프레임 재생
        
        # 점프 시작
        player.is_jumping = True
        player.jump_time = 0
        
        print(f"ParryState 진입 - 공중 패링!")
    
      
    def exit(player, e):
        player.is_parrying = False
    
      
    def do(player):
        # 애니메이션이 끝나면 Run 상태로 전환
        if player.current_anim == 'player_parry_sky':
            anim_data = player.sprite_sheets.get('player_parry_sky')
            if anim_data and player.anim_frame >= anim_data['total_frames'] - 1:
                player.state_machine.add_event(('TIME_OUT', 0))
    
      
    def draw(player):
        # 공중 Parry 애니메이션 그리기
        if 'player_parry_sky' in player.sprite_sheets:
            anim_data = player.sprite_sheets['player_parry_sky']
            sprite_sheet = anim_data['image']
            sprite_width = anim_data['sprite_width']
            sprite_height = anim_data['sprite_height']
            total_frames = anim_data['total_frames']
            
            current_frame = min(player.anim_frame, total_frames - 1)
            frame_x = current_frame * sprite_width
            
            draw_scale = 0.25
            draw_width = int(sprite_width * draw_scale)
            draw_height = int(sprite_height * draw_scale)
            
            sprite_sheet.clip_draw(
                int(frame_x), 0, int(sprite_width), int(sprite_height),
                int(player.x), int(player.y), int(draw_width), int(draw_height)
            )

class HitState:
      
    def enter(player, e):
        # 피해 처리 (HIT 이벤트일 때만)
        if e[0] == 'HIT':
            player.hp -= 1
            print(f"피격당함! 남은 HP: {player.hp}/{player.max_hp}")
        
        player.is_hit = True
        player.hit_time = time.time()
        
        # 피격 애니메이션 설정 (처음부터 재생)
        player.current_anim = 'player_hurt_2'
        player.anim_frame = 0
        player.max_anim_frames = 14  # 14프레임 재생
        print("HitState 진입 - 피격 애니메이션 재생")
    
      
    def exit(player, e):
        pass
    
      
    def do(player):
        # 애니메이션이 끝나면 RunState로 전환
        if player.anim_frame >= 13:  # 14프레임(0~13) 완료
            player.state_machine.add_event(('TIME_OUT', 0))
    
      
    def draw(player):
        # Hurt 애니메이션 그리기
        if 'player_hurt_2' in player.sprite_sheets:
            anim_data = player.sprite_sheets['player_hurt_2']
            sprite_sheet = anim_data['image']
            sprite_width = anim_data['sprite_width']
            sprite_height = anim_data['sprite_height']
            total_frames = anim_data['total_frames']
            
            current_frame = min(player.anim_frame, total_frames - 1)
            frame_x = current_frame * sprite_width
            
            draw_scale = 0.25
            draw_width = int(sprite_width * draw_scale)
            draw_height = int(sprite_height * draw_scale)
            
            sprite_sheet.clip_draw(
                int(frame_x), 0, int(sprite_width), int(sprite_height),
                int(player.x), int(player.y), int(draw_width), int(draw_height)
            )

# 이벤트 정의
SPACE_DOWN = 0
SPACE_UP = 1
TIME_OUT = 2
DIE = 3
HIT = 4

# 상태 전이 테이블
transitions = {
    FightIdleState: {
        SPACE_DOWN: ParryState,
        TIME_OUT: RunState,  # 0.3초 후 Run으로 전환
        HIT: HitState,  # 피격 시 HitState로 전환
        DIE: DieState  # HP 0 시 Die로 전환
    },
    ParryState: {
        SPACE_DOWN: ParryState,  # 연속 패링 가능
        TIME_OUT: RunState,  # 패링 애니메이션 종료 후 바로 Run으로
        HIT: HitState,  # 피격 시 HitState로 전환
        DIE: DieState  # HP 0 시 Die로 전환
    },
    RunState: {
        SPACE_DOWN: ParryState,  # Run 중에도 패링 가능
        HIT: HitState,  # 피격 시 HitState로 전환
        DIE: DieState  # HP 0 시 Die로 전환
    },
    HitState: {
        SPACE_DOWN: ParryState,  # 피격 중 space 입력 시 패링으로 전환
        HIT: HitState,  # 연속 피격 시 애니메이션 처음부터 재생
        TIME_OUT: RunState,  # 피격 애니메이션 후 RunState로 복귀
        DIE: DieState  # HP 0 시 Die로 전환
    },
    DieState: {
        # Die 상태에서는 어떤 이벤트도 처리하지 않음 (게임 오버)
    }
}

class StateMachine:
    def __init__(self, player):
        self.player = player
        self.cur_state = RunState  # Run으로 시작
        self.event_queue = []
    
    def start(self, start_state):
        self.cur_state = start_state
        self.cur_state.enter(self.player, ('START', 0))
    
    def add_event(self, event):
        self.event_queue.append(event)
    
    def update(self):
        # 이벤트를 먼저 처리 
        if self.event_queue:
            event = self.event_queue.pop(0)
            self.handle_event(event)
        
        # 그 다음 현재 상태의 do() 실행
        self.cur_state.do(self.player)
    
    def handle_event(self, event):
        event_type = event[0] if isinstance(event, tuple) else event
        
        # 문자열 이벤트를 숫자로 변환
        if event_type == 'SPACE_DOWN':
            event_type = SPACE_DOWN
        elif event_type == 'TIME_OUT':
            event_type = TIME_OUT
        elif event_type == 'DIE':
            event_type = DIE
        elif event_type == 'HIT':
            event_type = HIT
        
        # 상태 전이 체크
        if event_type in transitions[self.cur_state]:
            next_state = transitions[self.cur_state][event_type]
            self.cur_state.exit(self.player, event)
            print(f"상태 전환: {self.cur_state.__name__} -> {next_state.__name__}")
            self.cur_state = next_state
            self.cur_state.enter(self.player, event)
    
    def draw(self):
        self.cur_state.draw(self.player)
