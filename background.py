from pico2d import *

class Background:
    """배경 스크롤 관리 클래스"""
    
    def __init__(self, image_path='background.png', scroll_speed=200):
        """
        Args:
            image_path: 배경 이미지 경로
            scroll_speed: 스크롤 속도 (픽셀/초)
        """
        self.scroll_speed = scroll_speed
        self.is_scrolling = True  # 스크롤 활성화 여부
        
        # 배경 이미지 로드
        try:
            self.image = load_image(image_path)
            self.width = self.image.w
            self.height = self.image.h
            print(f"✓ 배경 이미지 로드 완료: {image_path}")
        except:
            print(f"! 배경 이미지 로드 실패: {image_path}")
            self.image = None
            self.width = 1080
            self.height = 608
        
        # 무한 스크롤을 위한 두 배경 위치
        self.x1 = 0
        self.x2 = self.width
    
    def update(self, dt, should_scroll=True):
        """
        배경 업데이트
        
        Args:
            dt: 델타 타임
            should_scroll: 스크롤 여부 (RunState일 때만 True)
        """
        if not should_scroll:
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
        """배경 그리기"""
        if not self.image:
            return
        
        # 두 개의 배경을 나란히 그려서 무한 스크롤 효과
        center_y = 304  # 화면 중앙 (608/2)
        self.image.draw(self.x1 + self.width / 2, center_y)
        self.image.draw(self.x2 + self.width / 2, center_y)
    
    def reset(self):
        """배경 위치 초기화"""
        self.x1 = 0
        self.x2 = self.width
