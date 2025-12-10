"""
난이도 선택 모드
"""
from pico2d import *
import game_framework
import play_mode

class DifficultySelectMode:
    def __init__(self, selected_song):
        self.font = None
        self.background = None
        self.selected_song = selected_song
        self.difficulties = [
            {'name': 'EASY', 'value': 'easy', 'description': 'For beginners'},
            {'name': 'NORMAL', 'value': 'normal', 'description': 'Balanced experience'},
            {'name': 'HARD', 'value': 'hard', 'description': 'Expert challenge'}
        ]
        self.selected_index = 1  # 기본값: Normal
        
    def enter(self):
        """난이도 선택 모드 진입"""
        print(f"난이도 선택 화면 진입 - 선택된 곡: {self.selected_song['name']}")
        self.font = None
        self.title_font = None
        self.desc_font = None
        # 배경 이미지 로드
        if self.background is None:
            self.background = load_image('background.png')
        
    def exit(self):
        """난이도 선택 모드 종료"""
        pass
        
    def handle_event(self, event):
        """이벤트 처리"""
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                # 곡 선택 화면으로 돌아가기
                import song_select_mode
                game_framework.change_mode(song_select_mode.SongSelectMode())
            elif event.key == SDLK_UP:
                # 위로 이동
                self.selected_index = (self.selected_index - 1) % len(self.difficulties)
            elif event.key == SDLK_DOWN:
                # 아래로 이동
                self.selected_index = (self.selected_index + 1) % len(self.difficulties)
            elif event.key == SDLK_RETURN or event.key == SDLK_SPACE:
                # 선택 확정 - 게임 시작
                selected_difficulty = self.difficulties[self.selected_index]['value']
                print(f"게임 시작: {self.selected_song['name']} - {selected_difficulty}")
                game_framework.change_mode(
                    play_mode.PlayMode(
                        music_path=self.selected_song['file'],
                        difficulty=selected_difficulty
                    )
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
            self.title_font = load_font('C:\\Windows\\Fonts\\malgun.ttf', 40)
        if self.font is None:
            self.font = load_font('C:\\Windows\\Fonts\\malgun.ttf', 30)
        if self.desc_font is None:
            self.desc_font = load_font('C:\\Windows\\Fonts\\malgun.ttf', 20)
        
        # 제목
        self.title_font.draw(540 - 200, 520, "SELECT DIFFICULTY", (255, 255, 255))
        
        # 선택된 곡 표시
        self.desc_font.draw(540 - len(self.selected_song['name']) * 8, 470, 
                           f"Song: {self.selected_song['name']}", (150, 150, 255))
        
        # 난이도 목록
        for i, difficulty in enumerate(self.difficulties):
            y_pos = 380 - i * 80
            
            if i == self.selected_index:
                # 선택된 난이도 (밝게)
                self.font.draw(400, y_pos, f"> {difficulty['name']}", (255, 255, 0))
                # 설명
                self.desc_font.draw(450, y_pos - 30, difficulty['description'], (200, 200, 100))
            else:
                # 선택되지 않은 난이도
                self.font.draw(420, y_pos, difficulty['name'], (150, 150, 150))
        

        
        update_canvas()
