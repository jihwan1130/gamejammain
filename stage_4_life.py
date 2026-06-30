import pygame, sys

class LifeSupportGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.gauge = 0.0
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 10.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # Constant decay
            self.gauge = max(0.0, self.gauge - 0.6)
            
            if self.gauge >= 100.0:
                self.state = "SUCCESS"
            elif self.elapsed_time >= self.limit_time:
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
                self.gauge = min(100.0, self.gauge + 4.2)
                play_sfx("sfx_click")
                
    def draw(self, surface):
        from visual_effects import draw_terminal_hud
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        virtual_surf.fill((5, 25, 15))
        
        # Fonts
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        font_sub = pygame.font.SysFont("malgungothic", 18)
        
        txt_guide = font_main.render("OXYGEN PRESSURE DROP DETECTED", True, (240, 255, 245))
        txt_job = font_sub.render("LIFE SUPPORT ENGINEER BONUS: 장치 부하 복구 가동. [SPACEBAR] 연타!", True, (80, 220, 140))
        
        virtual_surf.blit(txt_guide, (500 - txt_guide.get_width()//2, 220))
        virtual_surf.blit(txt_job, (500 - txt_job.get_width()//2, 280))
        
        # Draw progress bar
        pygame.draw.rect(virtual_surf, (10, 15, 10), (500 - 250, 400, 500, 40))
        pygame.draw.rect(virtual_surf, (80, 220, 140), (500 - 250, 400, int(self.gauge * 5), 40))
        pygame.draw.rect(virtual_surf, (240, 255, 245), (500 - 250, 400, 500, 40), 2)
        
        draw_terminal_hud(virtual_surf, "LIFE SUPPORT RE-PRESSURIZATION", self.limit_time, self.elapsed_time, (80, 220, 140))
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((5, 20, 10, 220))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 산소 공급 장치 압력 정상화 (SUCCESS) ■", True, (80, 220, 140))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 산소 카트리지 전면 고갈 (FAIL) 🚨", True, (240, 60, 60))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = LifeSupportGame()
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
