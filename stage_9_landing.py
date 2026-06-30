import pygame, sys

class ReverseThrustDecelerationGame:
    def __init__(self):
        self.target_hit = 18
        self.reset()
        
    def reset(self):
        self.hit_count = 0
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 10.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            if self.elapsed_time >= self.limit_time:
                if self.hit_count >= self.target_hit:
                    self.state = "SUCCESS"
                else:
                    self.state = "FAIL"
                    
    def handle_input(self):
        pass
        
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
            elif event.key == pygame.K_SPACE:
                self.hit_count += 1
                play_sfx("sfx_click")
                
    def draw(self, surface):
        from visual_effects import draw_terminal_hud
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        virtual_surf.fill((30, 5, 5))
        
        # Fonts
        font_large = pygame.font.SysFont("malgungothic", 35, bold=True)
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        font_sub = pygame.font.SysFont("malgungothic", 18)
        
        draw_terminal_hud(virtual_surf, "CRITICAL REVERSE THRUST ENGAGEMENT", self.limit_time, self.elapsed_time, (240, 50, 50))
        
        txt_alert = font_large.render("WARNING: GRAVITATIONAL PULL EXCEEDED BOUNDS", True, (240, 50, 50))
        txt_guide = font_sub.render(f"행성 중력권 브레이킹 매니폴드 연산 가동: 10초 내 [SPACEBAR]를 {self.target_hit}회 이상 연타하세요!", True, WHITE)
        virtual_surf.blit(txt_alert, (500 - txt_alert.get_width()//2, 180))
        virtual_surf.blit(txt_guide, (500 - txt_guide.get_width()//2, 250))
        
        # Hit counting interface
        txt_count = font_large.render(f"CURRENT STROKES: {self.hit_count} / {self.target_hit}", True, WHITE)
        virtual_surf.blit(txt_count, (500 - txt_count.get_width()//2, 340))
        
        # Gauge bar
        progress_ratio = min(1.0, self.hit_count / self.target_hit)
        pygame.draw.rect(virtual_surf, (10, 10, 10), (500 - 200, 440, 400, 30))
        pygame.draw.rect(virtual_surf, (240, 50, 50), (500 - 200, 440, int(progress_ratio * 400), 30))
        pygame.draw.rect(virtual_surf, WHITE, (500 - 200, 440, 400, 30), 2)
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((25, 5, 5, 230))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 대기권 역추진 감속 브레이크 안착 (SUCCESS) ■", True, (100, 255, 100))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 역추진 파쇄 가속 붕괴 (FAIL) 🚨", True, (240, 50, 50))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = ReverseThrustDecelerationGame()
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