import pygame, random, sys

class CoreThermalStabilizerGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.core_x = 500
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 15.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        self.press_count = 0  # 키 연타 횟수 카운터
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # Physics: Core slides away from center
            center_dist = (self.core_x - 500) / 350.0
            jitter = random.choice([-10, -5, 5, 10])
            push_force = center_dist * (8.0 + self.elapsed_time * 0.5)
            self.core_x += (jitter + push_force)
            
            # Boundary check
            if self.core_x < 150 or self.core_x > 850:
                self.state = "FAIL"
            elif self.elapsed_time >= self.limit_time:
                self.state = "SUCCESS"
                
    def handle_input(self):
        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.core_x -= 12
            if keys[pygame.K_d]:
                self.core_x += 12
                
    def handle_event(self, event):
        from main import settings, go_to_minigames, play_sfx, keyboard_sfx
        if self.state != "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play_sfx("sfx_end")
                    go_to_minigames()
                elif event.key == pygame.K_RETURN:
                    self.reset()
                    if keyboard_sfx:
                        keyboard_sfx.set_volume(settings.volume)
                        keyboard_sfx.play()
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                play_sfx("sfx_end")
                go_to_minigames()
            elif event.key in [pygame.K_a, pygame.K_d]:
                self.press_count += 1
                if self.press_count >= 18:
                    self.state = "SUCCESS"
                
    def draw(self, surface):
        from visual_effects import draw_terminal_hud
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        virtual_surf.fill((35, 10, 10))
        
        # Fonts
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        font_sub = pygame.font.SysFont("malgungothic", 18)
        
        # Draw safe zones & core line
        pygame.draw.rect(virtual_surf, (50, 20, 20), (150, 350 - 25, 700, 50))
        pygame.draw.rect(virtual_surf, (60, 220, 100), (500 - 60, 350 - 25, 120, 50), 2) # Target zone
        pygame.draw.line(virtual_surf, (220, 50, 40), (150, 350), (850, 350), 3)
        
        # Draw moving core circle
        pygame.draw.circle(virtual_surf, (220, 50, 40), (int(self.core_x), 350), 22)
        pygame.draw.circle(virtual_surf, (245, 240, 235), (int(self.core_x), 350), 10)
        
        # Draw HUD info
        draw_terminal_hud(virtual_surf, "CORE THERMAL STABILIZER SEQUENCE", self.limit_time, self.elapsed_time, (220, 50, 40))
        txt_guide = font_sub.render("DEVELOPER JOB: [A]/[D] 키로 중심 유지 (18회 키 입력 시 긴급 수동 안정화 가능)", True, (245, 240, 235))
        virtual_surf.blit(txt_guide, (40, 60))
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((25, 5, 5, 230))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 코어 온도 안정화 제어 성공 (SUCCESS) ■", True, (100, 255, 150))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 코어 과열 용해 파손 (FAIL) 🚨", True, (220, 50, 40))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = CoreThermalStabilizerGame()
    from visual_effects import TerminalFilter
    filter_crt = TerminalFilter(1000, 700)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        game.update()
        game.handle_input()
        game.draw(screen)
        filter_crt.apply(screen)
        pygame.display.flip()
        clock.tick(60)