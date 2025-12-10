import time
from pico2d import *

# 게임 상태 관리
class GameState:
    def __init__(self):
        self.running = True
        self.dt = 0
        self.last_time = 0

game_state = GameState()
stack = []

def init():
    open_canvas(1080, 608)  # 배경 이미지 크기에 맞춤
    game_state.last_time = time.time()

def quit():
    close_canvas()

def run(start_state):
    global stack
    stack = [start_state]
    start_state.enter()  # 초기 상태 진입
    
    current_time = time.time()
    
    while game_state.running:
        # 델타 타임 계산
        frame_time = time.time()
        game_state.dt = frame_time - current_time
        current_time = frame_time
        
        # 이벤트 처리
        events = get_events()
        for event in events:
            if event.type == SDL_QUIT:
                game_state.running = False
            else:
                stack[-1].handle_event(event)
        
        # 업데이트
        stack[-1].update()
        
        # 렌더링
        clear_canvas()
        stack[-1].draw()
        update_canvas()
        
        delay(0.01)  
    
    # 정리
    while len(stack) > 0:
        stack[-1].exit()
        stack.pop()

def change_state(state):
    global stack
    if len(stack) > 0:
        stack[-1].exit()
        stack.pop()
    stack.append(state)
    state.enter()

# change_mode는 change_state의 별칭
change_mode = change_state

def push_state(state):
    global stack
    if len(stack) > 0:
        stack[-1].pause()
    stack.append(state)
    state.enter()

def pop_state():
    global stack
    if len(stack) > 0:
        stack[-1].exit()
        stack.pop()
    if len(stack) > 0:
        stack[-1].resume()
