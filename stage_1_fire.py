import pygame, random, math

class FireGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.fires = []
        for _ in range(5):
            self.fires.append({
                "x": random.randint(100, 900),
                "y": random.randint(100, 600),
                "hp": 30
            })
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 20.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # Continuous mouse click to extinguish fires
            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                from main import settings
                # Convert mouse coordinates to virtual 1000x700 coordinates
                vmx = int(mx * 1000 / settings.width)
                vmy = int(my * 700 / settings.height)
                for f in self.fires[:]:
                    if math.hypot(vmx - f["x"], vmy - f["y"]) < 50:
                        f["hp"] -= 0.5
                    if f["hp"] <= 0:
                        self.fires.remove(f)
            
            if len(self.fires) == 0:
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
                
    def draw(self, surface):
        from visual_effects import draw_terminal_hud
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        virtual_surf.fill((30, 20, 10))
        
        for f in self.fires:
            pygame.draw.circle(virtual_surf, (220, 60, 40), (f["x"], f["y"]), 20)
            
        draw_terminal_hud(virtual_surf, "FIRE SUPPRESSION", self.limit_time, self.elapsed_time, (235, 130, 40))
        
        if self.state != "PLAYING":
            font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
            font_sub = pygame.font.SysFont("malgungothic", 18)
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((15, 10, 5, 210))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 화재 진압 성공 (SUCCESS) ■", True, (70, 220, 70))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 화재 제어 실패 - 원자로 과열 (FAIL) 🚨", True, (220, 60, 40))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    import sys
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = FireGame()
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