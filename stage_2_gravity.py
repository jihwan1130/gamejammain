import pygame, random, sys, os

def get_main_val(name, default=None):
    try:
        import sys
        main_mod = sys.modules.get('main') or sys.modules.get('__main__')
        if main_mod and hasattr(main_mod, name):
            return getattr(main_mod, name)
    except:
        pass
    return default

class GravityHullRepairGame:
    def __init__(self):
        import string
        self.key_map = {}
        for char in string.ascii_lowercase:
            key_code = getattr(pygame, f"K_{char}", None)
            if key_code is not None:
                self.key_map[key_code] = char.upper()
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
        self.current_round = 0
        self.total_rounds = 12
        self.target_key, self.target_name = self.get_new_target()
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 10.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            if self.current_round >= self.total_rounds:
                self.state = "SUCCESS"
            elif self.elapsed_time >= self.limit_time:
                self.state = "FAIL"
                
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        settings = get_main_val('settings')
        vol = settings.volume if settings else 0.5
        go_to_minigames = get_main_val('go_to_minigames') or get_main_val('go_to_main_menu')
        play_sfx = get_main_val('play_sfx')
        keyboard_sfx = get_main_val('keyboard_sfx')
            
        if self.state != "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if play_sfx:
                        play_sfx("sfx_end")
                    if go_to_minigames:
                        go_to_minigames()
                elif event.key == pygame.K_RETURN:
                    self.reset()
                    if keyboard_sfx:
                        keyboard_sfx.set_volume(vol)
                        keyboard_sfx.play()
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if play_sfx:
                    play_sfx("sfx_end")
                if go_to_minigames:
                    go_to_minigames()
            elif event.key == self.target_key:
                # Correct key pressed
                self.current_round += 1
                if play_sfx:
                    play_sfx("sfx_click")
                if self.current_round >= self.total_rounds:
                    self.state = "SUCCESS"
                else:
                    self.target_key, self.target_name = self.get_new_target()
            elif event.key in self.key_map:
                # Incorrect key penalty
                pass
                
    def draw(self, surface):
        CRT_GREEN = get_main_val('CRT_GREEN', (0, 255, 0))
        WHITE = get_main_val('WHITE', (255, 255, 255))
        get_scaled_font = get_main_val('get_scaled_font')
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        theme_purple = (180, 100, 250)
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 가독성을 높이기 위해 옅은 어두운 오버레이 추가
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((15, 10, 20, 160))  # R, G, B, Alpha
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill((15, 5, 25))
        
        # Fonts
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        font_sub = pygame.font.SysFont("malgungothic", 18)
        font_key = pygame.font.SysFont("consolas", 60, bold=True)
        
        # Draw indicator board
        pygame.draw.rect(virtual_surf, (10, 10, 10), (500 - 75, 200, 150, 150))
        pygame.draw.rect(virtual_surf, theme_purple, (500 - 75, 200, 150, 150), 3)
        txt_key = font_key.render(self.target_name, True, theme_purple)
        virtual_surf.blit(txt_key, (500 - txt_key.get_width()//2, 240))
        
        txt_under = font_sub.render(f"ENGINEER JOB ACTIVE: 화면에 뜨는 키를 순서대로 입력하십시오! ({self.current_round} / {self.total_rounds})", True, (255, 255, 240))
        virtual_surf.blit(txt_under, (500 - txt_under.get_width()//2, 380))
        
        # Draw gauge bar
        progress_ratio = self.current_round / self.total_rounds
        pygame.draw.rect(virtual_surf, (10, 10, 10), (500 - 250, 460, 500, 35))
        pygame.draw.rect(virtual_surf, theme_purple, (500 - 250, 460, int(progress_ratio * 500), 35))
        pygame.draw.rect(virtual_surf, (255, 255, 240), (500 - 250, 460, 500, 35), 2)
        
        # Custom Terminal HUD
        pygame.draw.rect(virtual_surf, theme_purple, (10, 10, 1000 - 20, 700 - 20), 2)
        pygame.draw.rect(virtual_surf, theme_purple, (15, 15, 1000 - 30, 700 - 30), 1)
        
        # Draw time progress bar on the top-left
        remain = max(0.0, self.limit_time - self.elapsed_time)
        time_ratio = remain / self.limit_time
        
        font_hud_label = pygame.font.SysFont("malgungothic", 16, bold=True)
        time_label = font_hud_label.render("TIME", True, theme_purple)
        virtual_surf.blit(time_label, (30, 23))
        
        pygame.draw.rect(virtual_surf, (20, 10, 30), (80, 25, 220, 20))
        pygame.draw.rect(virtual_surf, theme_purple, (80, 25, 220, 20), 1)
        fill_w = int(216 * time_ratio)
        if fill_w > 0:
            pygame.draw.rect(virtual_surf, theme_purple, (82, 27, fill_w, 16))
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((15, 5, 20, 220))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 선체 외부 격벽 복구 성공 (SUCCESS) ■", True, theme_purple)
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