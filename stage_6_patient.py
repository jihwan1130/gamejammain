import pygame, random, sys

class PathogenQuarantineGame:
    def __init__(self):
        self.judge_y = 530
        self.reset()
        
    def reset(self):
        self.germs = []
        self.spawn_counter = 0
        self.killed_score = 0
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 12.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # Spawn germs
            self.spawn_counter += 1
            if self.spawn_counter % 22 == 0:
                self.germs.append({
                    "x": random.randint(150, 850),
                    "y": 80,
                    "speed": random.randint(6, 11)
                })
                
            # Scroll germs
            for g in self.germs[:]:
                g["y"] += g["speed"]
                if g["y"] > 620:
                    self.germs.remove(g)
                    
            if self.elapsed_time >= self.limit_time:
                if self.killed_score >= 6:
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
                # Fire quarantine laser to clear germs in the judge zone
                hit = False
                for g in self.germs[:]:
                    if self.judge_y - 25 <= g["y"] <= self.judge_y + 25:
                        self.germs.remove(g)
                        self.killed_score += 1
                        play_sfx("sfx_click")
                        hit = True
                        break
                        
    def draw(self, surface):
        from visual_effects import draw_terminal_hud
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        virtual_surf.fill((5, 25, 25))
        
        # Fonts
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        font_sub = pygame.font.SysFont("malgungothic", 18)
        
        # Draw judge bar
        pygame.draw.rect(virtual_surf, (20, 50, 45), (40, self.judge_y - 20, 1000 - 80, 40))
        pygame.draw.line(virtual_surf, (60, 210, 190), (40, self.judge_y), (1000 - 40, self.judge_y), 3)
        
        # Draw germs
        for g in self.germs:
            pygame.draw.circle(virtual_surf, (240, 60, 80), (g["x"], int(g["y"])), 15)
            pygame.draw.circle(virtual_surf, WHITE, (g["x"], int(g["y"])), 6)
            
        draw_terminal_hud(virtual_surf, "ANTIBODY INCUBATION INJECTOR", self.limit_time, self.elapsed_time, (60, 210, 190))
        txt_hud = font_sub.render(f"바이러스 제압 현황: {self.killed_score} / 6 (TARGET)", True, WHITE)
        virtual_surf.blit(txt_hud, (40, 60))
        
        # Helper guide text
        txt_space = font_sub.render("🧬 의사 긴급 수술 프로토콜: 스패너 선 분자 매칭 구간 진입 시 [SPACEBAR] 격추!", True, (60, 210, 190))
        virtual_surf.blit(txt_space, (40, 700 - 50))
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((5, 15, 15, 220))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 생체 면역 격리 완료 (SUCCESS) ■", True, (100, 255, 150))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 생체 신호 정지 (FAIL) 🚨", True, (240, 60, 80))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = PathogenQuarantineGame()
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