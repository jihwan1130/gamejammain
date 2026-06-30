# visual_effects.py
import pygame
import math

class TerminalFilter:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # 스캔라인 오버레이 생성
        self.scanline = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(0, height, 3):
            pygame.draw.line(self.scanline, (0, 0, 0, 100), (0, y), (width, y), 1)
            
        # 비네팅 오버레이 생성
        self.vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        for radius in range(0, int(width * 0.75), 4):
            alpha = min(255, int((radius / (width * 0.75)) ** 2 * 180))
            pygame.draw.circle(self.vignette, (0, 0, 0, alpha // 6), (width//2, height//2), radius, 4)

    def apply(self, surface):
        surface.blit(self.vignette, (0, 0))
        surface.blit(self.scanline, (0, 0))

def draw_terminal_hud(screen, title, limit_time, elapsed, color=(235, 130, 40)):
    """우주선 모니터 스타일의 테두리와 HUD를 그립니다."""
    width, height = screen.get_size()
    # 외부 프레임 테두리
    pygame.draw.rect(screen, color, (10, 10, width - 20, height - 20), 2)
    pygame.draw.rect(screen, color, (15, 15, width - 30, height - 30), 1)
    
    # 상단 바 정보
    font = pygame.font.SysFont("malgungothic", 20, bold=True)
    remain = max(0.0, limit_time - elapsed)
    
    title_text = font.render(f"■ SYSTEM ALERT: {title} ■", True, color)
    time_text = font.render(f"TIME REMAINING: {remain:.1f}s", True, (220, 60, 40) if remain < 4 else color)
    
    screen.blit(title_text, (30, 25))
    screen.blit(time_text, (width - 250, 25))