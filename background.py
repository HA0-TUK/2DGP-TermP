from pico2d import *

class ParallaxLayer:
    
    def __init__(self, image_path, scroll_speed):
        self.scroll_speed = scroll_speed
        self.x1 = 0
        self.x2 = 0
        self.width = 0
        self.height = 0
        self.image = None
        
        try:
            self.image = load_image(image_path)
            self.width = self.image.w
            self.height = self.image.h
            # 무한 스크롤을 위한 두 배경 위치
            self.x1 = 0
            self.x2 = self.width
        except Exception as e:
            print(f"레이어 이미지 로드 실패: {image_path} ({e})")
    
    def update(self, dt):
        if not self.image:
            return
        
        # 배경을 왼쪽으로 이동
        self.x1 -= self.scroll_speed * dt
        self.x2 -= self.scroll_speed * dt
        
        # 첫 번째 배경이 화면 밖으로 나가면 오른쪽으로 재배치
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        
        # 두 번째 배경이 화면 밖으로 나가면 오른쪽으로 재배치
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width
    
    def draw(self):
        if not self.image:
            return
        
        center_y = 304  # 화면 중앙 (608/2)
        self.image.draw(self.x1 + self.width / 2, center_y)
        self.image.draw(self.x2 + self.width / 2, center_y)
    
    def reset(self):
        self.x1 = 0
        self.x2 = self.width


class Background:
    
    def __init__(self, scroll_speed=200):
        self.base_scroll_speed = scroll_speed
        self.is_scrolling = True
        
        # 시차 스크롤 레이어 생성

        self.back = ParallaxLayer('background-back.png', scroll_speed * 0.3)    # 먼
        self.tree = ParallaxLayer('background-tree.png', scroll_speed * 0.6)    # 중간 
        self.grass = ParallaxLayer('background-grass.png', scroll_speed * 1.0)  # 가까운 
        
        # 모든 레이어가 로드되었는지 확인
        self.all_layers = [self.back, self.tree, self.grass]
    
    def update(self, dt, should_scroll=True):
        if not should_scroll:
            return
        
        # 모든 레이어 업데이트 
        for layer in self.all_layers:
            layer.update(dt)
    
    def draw(self):
        # 뒤에서부터 앞 순서로 렌더링하여 시차 효과 표현
        self.back.draw()   
        self.tree.draw()   
        self.grass.draw()  
    
    def reset(self):
        for layer in self.all_layers:
            layer.reset()
