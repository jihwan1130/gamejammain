import pygame
import os
import random

from stage_1_robot import RogueRobotGame as BaseRogueRobotGame

def load_gif_frames(filepath):
    frames = []
    try:
        from PIL import Image, ImageSequence
        gif = Image.open(filepath)
        for frame in ImageSequence.Iterator(gif):
            frame_rgba = frame.convert("RGBA")
            data = frame_rgba.tobytes("raw", "RGBA")
            size = frame_rgba.size
            surf = pygame.image.fromstring(data, size, "RGBA")
            surf_conv = surf.convert_alpha()
            frames.append(surf_conv)
    except Exception as e:
        print(f"GIF 프레임 로드 실패: {e}")
    return frames

class RogueRobotGame(BaseRogueRobotGame):
    def __init__(self):
        super().__init__()
        
        # 1. 배경 이미지 로드
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "Stage_2.png")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
            else:
                print(f"Stage_2.png 파일이 존재하지 않습니다: {bg_path}")
        except Exception as e:
            print(f"Stage_2.png 로드 실패: {e}")
            
        # 2. 로봇 에셋 로드 (ai1, ai3)
        self.ai1_frames = []
        self.ai3_frames = []
        try:
            self.ai1_frames = load_gif_frames(os.path.join("assets", "ai1.gif"))
            self.ai3_frames = load_gif_frames(os.path.join("assets", "ai3.gif"))
        except Exception as e:
            print(f"로봇 GIF 에셋 로드 실패: {e}")
            
    def reset(self):
        self.robots = []
        size = 112  # 로봇 캐릭터 크기
        # 로봇 개수 총 10개 생성
        for _ in range(10):
            rect = pygame.Rect(random.randint(200, 800), random.randint(200, 500), size, size)
            self.robots.append({
                "rect": rect, 
                # 속도를 기존보다 1.2배 더 빠르게 [-7, -5, 5, 7]로 적용
                "vx": random.choice([-7, -5, 5, 7]), 
                "vy": random.choice([-7, -5, 5, 7]),
                "type": random.choice(["ai1", "ai3"]),
                "frame_offset": random.randint(0, 100)
            })
        self.start_ticks = pygame.time.get_ticks()
        self.limit_time = 8.0  # 시간 2초 단축 (10.0 -> 8.0)
        self.elapsed_time = 0
        self.state = "PLAYING"
            
    def draw(self, surface):
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        
        # Draw background
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 분위기에 맞게 어두운 보라톤 오버레이 적용 (기존 주황색/브라운 톤에서 변경)
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((28, 12, 40, 180))  # R, G, B, Alpha (어두운 보라색 톤)
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill((20, 10, 30))  # 단색 배경도 어두운 보라색 톤으로 설정
        
        # Fonts
        font_sub = pygame.font.SysFont("malgungothic", 18)
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        
        # Draw robots (using cached GIF frames)
        for r in self.robots:
            rtype = r.get("type", "ai1")
            offset = r.get("frame_offset", 0)
            frames = self.ai1_frames if rtype == "ai1" else self.ai3_frames
            
            if frames:
                # 시간에 따라 프레임 인덱스 계산
                frame_idx = ((pygame.time.get_ticks() + offset * 50) // 100) % len(frames)
                img = frames[frame_idx]
                scaled_img = pygame.transform.scale(img, (r["rect"].width, r["rect"].height))
                virtual_surf.blit(scaled_img, r["rect"])
            else:
                # 에셋 로드 실패 시 폴백 (빨간 상자)
                pygame.draw.rect(virtual_surf, (220, 60, 40), r["rect"])
                pygame.draw.rect(virtual_surf, (255, 240, 220), r["rect"], 2)
                pygame.draw.circle(virtual_surf, (255, 240, 220), r["rect"].center, 6)
            
        # Draw crosshair (보라색 톤에 맞춘 네온 핑크/퍼플 크로스헤어로 변경)
        from main import settings
        mx, my = pygame.mouse.get_pos()
        vmx = int(mx * 1000 / settings.width)
        vmy = int(my * 700 / settings.height)
        pygame.draw.circle(virtual_surf, (180, 100, 255), (vmx, vmy), 18, 1)
        pygame.draw.circle(virtual_surf, (255, 60, 150), (vmx, vmy), 3)
        
        # 3. HUD 및 시간 프로그레스 바 렌더링 (운석 소나기 스타일)
        # 테두리 색상: 어두운 보라색 톤
        COLOR_PURPLE = (120, 40, 180)
        
        # 외부 프레임 테두리 직접 그리기
        pygame.draw.rect(virtual_surf, COLOR_PURPLE, (10, 10, 980, 680), 2)
        pygame.draw.rect(virtual_surf, COLOR_PURPLE, (15, 15, 970, 670), 1)
        
        # 프로그레스 바 시간 표시 (운석 소나기 스타일 - 왼쪽 정렬)
        time_ratio = max(0.0, (self.limit_time - self.elapsed_time) / self.limit_time)
        bar_max_w = 400
        bar_h = 16
        bar_x = 30
        bar_y = 25
        
        pygame.draw.rect(virtual_surf, COLOR_PURPLE, (bar_x, bar_y, bar_max_w, bar_h), 2)
        fill_w = int(bar_max_w * time_ratio)
        if fill_w > 0:
            # 시간에 따른 게이지 색상 변경 (보라색 -> 네온 핑크 -> 빨간색)
            bar_color = (150, 80, 220) if time_ratio > 0.5 else ((220, 100, 150) if time_ratio > 0.2 else (255, 60, 40))
            pygame.draw.rect(virtual_surf, bar_color, (bar_x + 2, bar_y + 2, fill_w - 4, bar_h - 4))
        
        # 4. 로봇 잔여 수량 인디케이터 그리기 (목숨 개수 스타일)
        alive_count = len(self.robots)
        total_count = 10
        indicator_w = 18
        indicator_h = 14
        gap = 6
        start_x = 1000 - 30 - (total_count * (indicator_w + gap))
        indicator_y = 26
        
        for i in range(total_count):
            bx = start_x + i * (indicator_w + gap)
            # 살아있는 로봇은 보라색, 죽은 로봇은 검정색으로 표시
            if i < alive_count:
                color = (180, 100, 255)  # 보라색
            else:
                color = (10, 5, 20)      # 검정색
                
            pygame.draw.rect(virtual_surf, color, (bx, indicator_y, indicator_w, indicator_h))
            pygame.draw.rect(virtual_surf, COLOR_PURPLE, (bx, indicator_y, indicator_w, indicator_h), 1)
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((15, 10, 5, 210))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 위협 로봇 전원 사살 (SUCCESS) ■", True, (70, 220, 70))
                sub = font_sub.render("경찰 크루의 신속한 저격으로 거주 구역이 개방되었습니다.", True, WHITE)
            else:
                msg = font_main.render("🚨 거주 구역 전면 폐쇄 (FAIL) 🚨", True, (220, 60, 40))
                sub = font_sub.render("시간 초과로 경찰이 부상을 입었으며 선내 정신력이 파손되었습니다.", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    import sys
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = RogueRobotGame()
    from visual_effects import TerminalFilter
    filter_crt = TerminalFilter(1000, 700)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        game.update()
        game.draw(screen)
        filter_crt.apply(screen)
        pygame.display.flip()
        clock.tick(60)