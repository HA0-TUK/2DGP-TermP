from pico2d import *

class ParallaxLayer:
    """시차 스크롤 레이어"""
    
    def __init__(self, image_path, scroll_speed):
        """
        Args:
            image_path: 이미지 경로
            scroll_speed: 스크롤 속도 (픽셀/초)
        """
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
            print(f"✓ 레이어 이미지 로드 완료: {image_path} (Speed: {scroll_speed})")
        except Exception as e:
            print(f"! 레이어 이미지 로드 실패: {image_path} ({e})")
    
    def update(self, dt):
        """
        레이어 업데이트
        
        Args:
            dt: 델타 타임
        """
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
        """레이어 그리기"""
        if not self.image:
            return
        
        center_y = 304  # 화면 중앙 (608/2)
        self.image.draw(self.x1 + self.width / 2, center_y)
        self.image.draw(self.x2 + self.width / 2, center_y)
    
    def reset(self):
        """레이어 위치 초기화"""
        self.x1 = 0
        self.x2 = self.width


class Background:
    """시차 스크롤을 적용한 배경 관리 클래스"""
    
    def __init__(self, scroll_speed=200):
        """
        시차 스크롤링을 위한 3개 레이어 초기화
        
        Args:
            scroll_speed: 기본 스크롤 속도 (픽셀/초) - 가장 가까운 레이어 기준
        """
        self.base_scroll_speed = scroll_speed
        self.is_scrolling = True
        
        # 시차 스크롤 레이어 생성
        # 멀수록 느리게 스크롤 (깊이감 표현)
        self.back = ParallaxLayer('background-back.png', scroll_speed * 0.3)    # 먼 배경 (가장 느림)
        self.tree = ParallaxLayer('background-tree.png', scroll_speed * 0.6)    # 중간 배경
        self.grass = ParallaxLayer('background-grass.png', scroll_speed * 1.0)  # 가까운 배경 (가장 빠름)
        
        # 모든 레이어가 로드되었는지 확인
        self.all_layers = [self.back, self.tree, self.grass]
    
    def update(self, dt, should_scroll=True):
        """
        배경 업데이트
        
        Args:
            dt: 델타 타임
            should_scroll: 스크롤 여부 (RunState일 때만 True)
        """
        if not should_scroll:
            return
        
        # 모든 레이어 업데이트 (각자 다른 속도로)
        for layer in self.all_layers:
            layer.update(dt)
    
    def draw(self):
        """배경 그리기 (뒤에서 앞 순서)"""
        # 뒤에서부터 앞 순서로 렌더링하여 시차 효과 표현
        self.back.draw()   # 맨 뒤 (하늘 등)
        self.tree.draw()   # 중간 (나무)
        self.grass.draw()  # 맨 앞 (풀)
    
    def reset(self):
        """배경 위치 초기화"""
        for layer in self.all_layers:
            layer.reset()
