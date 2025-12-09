from pico2d import *
import game_framework
from player import Player
from building import RhythmManager
from background import Background

class PlayMode:
    def __init__(self):
        self.player = None
        self.rhythm_manager = None
        self.background = None
        self.game_over = False
        self.victory = False
        self.last_judgment = None
        self.judgment_time = 0
        self.die_animation_finished = False 
        
    def enter(self):
        self.player = Player()
        self.rhythm_manager = RhythmManager()
        self.background = Background(scroll_speed=200)
        self.game_over = False
        self.victory = False
        self.die_animation_finished = False
        
        # Miss 콜백 설정
        self.rhythm_manager.on_miss_callback = self.player.take_damage
        
    def exit(self):
        pass
        
    def pause(self):
        pass
        
    def resume(self):
        pass
    
    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            # Die 애니메이션이 끝났으면 아무 키나 눌러서 종료
            if self.die_animation_finished:
                self.game_over = True
                return
            
            if event.key == SDLK_SPACE:
                # 스페이스바로 패링 시도
                if self.player.parry():
                    # 리듬 판정 (player 충돌 기반)
                    judgment, success, parried_note = self.rhythm_manager.try_hit(player=self.player)
                    
                    # 패링 성공 시 이펙트 애니메이션
                    if success and parried_note:
                        is_perfect = (judgment == 'perfect')
                        self.player.parry_success(is_perfect)
                        print(f"패링 성공! {judgment}")
                        self.last_judgment = judgment
                        self.judgment_time = 0

                        
            elif event.key == SDLK_r and (self.game_over or self.victory):
                # 게임 재시작
                self.__init__()
                self.enter()
                
            elif event.key == SDLK_ESCAPE:
                game_framework.quit()
    
    def update(self):
        if self.game_over or self.victory:
            return
            
        dt = game_framework.game_state.dt
        
        # 배경 업데이트 (RunState일 때만 스크롤)
        from player_state import RunState
        should_scroll = (self.player.state_machine.cur_state == RunState)
        self.background.update(dt, should_scroll)
        
        # 플레이어 업데이트
        self.player.update(dt)
        
        # Die 상태가 아닐 때만 리듬 시스템 업데이트 (화살표 생성)
        if not self.player.is_dead:
            self.rhythm_manager.update(dt)
        
        # 판정 텍스트 시간 업데이트
        if self.last_judgment:
            self.judgment_time += dt
            if self.judgment_time > 1.0:  # 1초 후 사라짐
                self.last_judgment = None
        
        # Die 애니메이션 완료 체크
        if self.player.is_dead and self.player.current_anim == 'player_die':
            # Die 애니메이션이 마지막 프레임(23번)에 도달했는지 확인
            anim_data = self.player.sprite_sheets.get('player_die')
            if anim_data and self.player.anim_frame >= anim_data['total_frames'] - 1:
                self.die_animation_finished = True
                # 아무 키나 눌러서 종료하라는 메시지 (한 번만 출력)
                if not hasattr(self, '_die_message_shown'):
                    print("Die 애니메이션 완료 - 아무 키나 눌러서 종료")
                    self._die_message_shown = True
        
        # 승리 체크
        if self.rhythm_manager.is_finished() and self.player.is_alive():
            self.victory = True
    
    def draw(self):
        clear_canvas()
        
        # 배경 그리기
        self.background.draw()
        
        # 게임 요소들 그리기
        if not self.game_over:  # 게임 오버가 아니면 플레이어와 화살표 그리기
            self.rhythm_manager.draw()
            self.player.draw()
            
            # 판정 결과 표시
            if self.last_judgment:
                self.draw_judgment()
        
        # UI 그리기
        self.draw_ui()
        
        # 게임 오버/승리 화면
        if self.game_over:
            self.draw_game_over()
        elif self.victory:
            self.draw_victory()
    
    def draw_judgment(self):
        """판정 결과 그리기"""
        # 판정 표시는 제거 (필요시 텍스트로 추가)
        pass
    
    def draw_ui(self):
        """UI 그리기"""
        # UI 표시 제거
        pass
    
    def draw_game_over(self):
        """게임 오버 화면"""
        # 게임 오버 화면은 필요시 추가
        pass
    
    def draw_victory(self):
        """승리 화면"""
        # 승리 화면은 필요시 추가
        pass

