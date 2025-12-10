"""
곡 선택 모드
"""
from pico2d import *
import game_framework
import difficulty_select_mode

class SongSelectMode:
    def __init__(self):
        self.font = None
        self.background = None
        self.songs = [
            {'name': 'Lady Ethereal', 'file': 'music/Lady Ethereal.mp3'},
            {'name': 'M2U', 'file': 'music/M2U.mp3'},
            {'name': 'Shaolin Warrior', 'file': 'music/Shaolin Warrior.mp3'}
        ]
        self.selected_index = 0
        
    def enter(self):
        """곡 선택 모드 진입"""
        print("곡 선택 화면 진입")
        self.font = None
        self.title_font = None
        # 배경 이미지 로드
        if self.background is None:
            self.background = load_image('background.png')
        
    def exit(self):
        """곡 선택 모드 종료"""
        pass
        
    def handle_event(self, event):
        """이벤트 처리"""
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                # 타이틀 화면으로 돌아가기
                import title_mode
                game_framework.change_mode(title_mode.TitleMode())
            elif event.key == SDLK_UP:
                # 위로 이동
                self.selected_index = (self.selected_index - 1) % len(self.songs)
            elif event.key == SDLK_DOWN:
                # 아래로 이동
                self.selected_index = (self.selected_index + 1) % len(self.songs)
            elif event.key == SDLK_RETURN or event.key == SDLK_SPACE:
                # 선택 확정 - 난이도 선택으로 이동
                selected_song = self.songs[self.selected_index]
                game_framework.change_mode(
                    difficulty_select_mode.DifficultySelectMode(selected_song)
                )
                
    def update(self):
        """업데이트"""
        pass
            
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
        
        # 폰트 로드 (처음 한 번만)
        if self.title_font is None:
            self.title_font = load_font('C:\\Windows\\Fonts\\malgun.ttf', 50)
        if self.font is None:
            self.font = load_font('C:\\Windows\\Fonts\\malgun.ttf', 40)
        
        # 제목
        self.title_font.draw(540 - 150, 500, "SELECT SONG", (255, 255, 255))
        
        # 곡 목록
        for i, song in enumerate(self.songs):
            y_pos = 400 - i * 60
            
            if i == self.selected_index:
                # 선택된 곡 (밝게)
                self.font.draw(400, y_pos, f"> {song['name']}", (255, 255, 0))
            else:
                # 선택되지 않은 곡
                self.font.draw(420, y_pos, song['name'], (150, 150, 150))
        

        
        update_canvas()
