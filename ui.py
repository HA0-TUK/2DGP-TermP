from pico2d import *

class HPBar:
    """체력 바 UI"""
    
    def __init__(self, x=50, y=580, width=200, height=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # 1x1 픽셀 이미지 로드
        try:
            self.white_img = load_image('white.png')
            print("✓ HP 바 이미지 로드 완료")
        except:
            print("! HP 바 이미지 로드 실패")
            self.white_img = None
        
        # 하트 애니메이션 로드
        try:
            self.heart_sheet = load_image('sprite_sheets/heart_animation.png')
            self.heart_frame = 0
            self.heart_frame_time = 0
            self.heart_sprite_width = 256
            self.heart_sprite_height = 256
            self.heart_total_frames = 7
            self.heart_fps = 10
            self.heart_scale = 0.15  # 하트 크기 조절
            print("✓ 하트 애니메이션 로드 완료")
        except:
            print("! 하트 애니메이션 로드 실패")
            self.heart_sheet = None
    
    def update(self, dt):
        """하트 애니메이션 업데이트"""
        if not self.heart_sheet:
            return
        
        self.heart_frame_time += dt
        frame_duration = 1.0 / self.heart_fps
        
        if self.heart_frame_time >= frame_duration:
            self.heart_frame_time = 0
            self.heart_frame = (self.heart_frame + 1) % self.heart_total_frames

    
    def draw(self, current_hp, max_hp):
        """체력 바 그리기"""
        if self.heart_sheet:
            heart_x = self.x - 20  
            heart_y = self.y - self.height / 2
            
            frame_x = self.heart_frame * self.heart_sprite_width
            draw_width = int(self.heart_sprite_width * self.heart_scale)
            draw_height = int(self.heart_sprite_height * self.heart_scale)
            
            self.heart_sheet.clip_draw(
                frame_x, 0, 
                self.heart_sprite_width, self.heart_sprite_height,
                heart_x, heart_y, 
                draw_width, draw_height
            )
        
        if not self.white_img:
            return
        
        # 중심점 계산
        center_x = self.x + self.width / 2
        center_y = self.y - self.height / 2
        
        # 흰색 현재 체력
        if current_hp > 0:
            hp_width = (current_hp / max_hp) * self.width
            hp_center_x = self.x + hp_width / 2
            self.white_img.draw(hp_center_x, center_y, hp_width, self.height)
        
        # 흰색 테두리
        border_thickness = 2
        # 상단
        self.white_img.draw(center_x, self.y, self.width, border_thickness)
        # 하단
        self.white_img.draw(center_x, self.y - self.height, self.width, border_thickness)
        # 좌측
        self.white_img.draw(self.x, center_y, border_thickness, self.height)
        # 우측
        self.white_img.draw(self.x + self.width, center_y, border_thickness, self.height)
