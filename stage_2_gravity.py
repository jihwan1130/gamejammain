import pygame, random, sys, os

class GravityHullRepairGame:
    def __init__(self):
        self.key_map = {pygame.K_d: 'D', pygame.K_f: 'F', pygame.K_j: 'J', pygame.K_k: 'K'}
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "atom.jpg")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"atom.jpg 로드 실패: {e}")
        self.reset()
        
    def get_new_target(self):
        new_key = random.choice(list(self.key_map.keys()))
        return new_key, self.key_map[new_key]
        
    def reset(self):
        self.target_key, self.target_name = self.get_new_target()
        self.gauge = 0.0
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 15.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # Constant decay
            self.gauge = max(0.0, self.gauge - 0.1)
            
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
            elif event.key == self.target_key:
                # Correct key pressed
                self.gauge = min(100.0, self.gauge + 6.0)
                self.target_key, self.target_name = self.get_new_target()
                play_sfx("sfx_click")
            elif event.key in self.key_map:
                # Incorrect key penalty
                self.gauge = max(0.0, self.gauge - 2.0)
                
    def draw(self, surface):
        from visual_effects import draw_terminal_hud
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 가독성을 높이기 위해 옅은 어두운 오버레이 추가
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((10, 15, 10, 160))  # R, G, B, Alpha
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill((5, 25, 10))
        
        # Fonts
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        font_sub = pygame.font.SysFont("malgungothic", 18)
        font_key = pygame.font.SysFont("consolas", 60, bold=True)
        
        # Draw indicator board
        pygame.draw.rect(virtual_surf, (10, 10, 10), (500 - 75, 200, 150, 150))
        pygame.draw.rect(virtual_surf, (70, 220, 70), (500 - 75, 200, 150, 150), 3)
        txt_key = font_key.render(self.target_name, True, (70, 220, 70))
        virtual_surf.blit(txt_key, (500 - txt_key.get_width()//2, 240))
        
        txt_under = font_sub.render("ENGINEER JOB ACTIVE: 화면에 뜨는 키를 순서대로 입력하십시오!", True, (255, 255, 240))
        virtual_surf.blit(txt_under, (500 - txt_under.get_width()//2, 380))
        
        # Draw gauge bar
        pygame.draw.rect(virtual_surf, (10, 10, 10), (500 - 250, 460, 500, 35))
        pygame.draw.rect(virtual_surf, (70, 220, 70), (500 - 250, 460, int(self.gauge * 5), 35))
        pygame.draw.rect(virtual_surf, (255, 255, 240), (500 - 250, 460, 500, 35), 2)
        
        draw_terminal_hud(virtual_surf, "GRAVITATIONAL ANOMALY HULL FIX", self.limit_time, self.elapsed_time, (70, 220, 70))
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((5, 15, 5, 220))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 선체 외부 격벽 복구 성공 (SUCCESS) ■", True, (70, 220, 70))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 구조 피로도 한계 도달 (FAIL) 🚨", True, (240, 60, 60))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = GravityHullRepairGame()
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