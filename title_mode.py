"""
타이틀 화면 모드
"""
from pico2d import *
import game_framework
import song_select_mode

class TitleMode:
    def __init__(self):
        self.font = None
        self.start_text = "SPACE 키를 눌러 시작"
        self.blink_time = 0
        self.show_start_text = True
        self.background = None
        self.title_logo = None
        
    def enter(self):
        """타이틀 모드 진입"""
        print("타이틀 화면 진입")
        # 기본 폰트 사용 (None)
        self.font = None
        # 배경 이미지 로드
        if self.background is None:
            self.background = load_image('background.png')
        # 타이틀 로고 로드
        if self.title_logo is None:
            try:
                self.title_logo = load_image('title_logo.png')
            except:
                print("title_logo.png 파일이 없습니다. 텍스트로 대체합니다.")
                self.title_logo = None
        
    def exit(self):
        """타이틀 모드 종료"""
        pass
        
    def handle_event(self, event):
        """이벤트 처리"""
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_SPACE:
                # 곡 선택 화면으로 전환
                game_framework.change_mode(song_select_mode.SongSelectMode())
                
    def update(self):
        """업데이트"""
        import game_framework
        dt = game_framework.game_state.dt
        # 깜빡이는 텍스트
        self.blink_time += dt
        if self.blink_time > 0.5:
            self.show_start_text = not self.show_start_text
            self.blink_time = 0
            
    def draw(self):
        """화면 그리기"""
        clear_canvas()
        
        # 화면 크기 가져오기
        canvas_width = get_canvas_width()
        canvas_height = get_canvas_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # 배경 이미지
        if self.background:
            self.background.draw(center_x, center_y)
        
        # 타이틀 로고 이미지 (중앙에 배치, 크기 50%로 축소)
        if self.title_logo:
            logo_width = self.title_logo.w // 2
            logo_height = self.title_logo.h // 2
            self.title_logo.draw(center_x, center_y + 100, logo_width, logo_height)
        else:
            # 로고 파일이 없으면 텍스트로 표시
            if self.font is None:
                self.font = load_font('C:\\Windows\\Fonts\\malgun.ttf', 60)
            title_text = "NINE SOLS"
            title_width = len(title_text) * 40
            self.font.draw(center_x - title_width // 2, center_y + 100, title_text, (255, 215, 0))
        
        # 시작 안내 텍스트 (Windows 기본 폰트 사용)
        from pico2d import load_font
        if self.font is None:
            self.font = load_font('C:\\Windows\\Fonts\\malgun.ttf', 40)
        
        # 시작 안내 텍스트 (깜빡임, 가운데 정렬)
        if self.show_start_text:
            start_width = len(self.start_text) * 20
            self.font.draw(center_x - start_width // 2, center_y - 100, self.start_text, (200, 200, 200))
        
        update_canvas()
