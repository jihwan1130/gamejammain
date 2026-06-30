import pygame, random, sys

class HighVoltageSparkDodgeGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.player_x = 500
        self.sparks = []
        self.spawn_timer = 0
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 20.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # Spawn sparks
            self.spawn_timer += 1
            if self.spawn_timer % 12 == 0:
                self.sparks.append(pygame.Rect(random.randint(60, 920), 120, 20, 40))
                
            p_rect = pygame.Rect(self.player_x - 20, 560, 40, 40)
            
            # Update sparks and check collisions
            for sp in self.sparks[:]:
                sp.y += 9
                if p_rect.colliderect(sp):
                    self.state = "FAIL"
                    from main import play_sfx
                    play_sfx("sfx_click")
                    break
                if sp.y > 640:
                    self.sparks.remove(sp)
                    
            if self.elapsed_time >= self.limit_time:
                self.state = "SUCCESS"
                
    def handle_input(self):
        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.player_x = max(50, self.player_x - 9)
            if keys[pygame.K_d]:
                self.player_x = min(950, self.player_x + 9)
                
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
        virtual_surf.fill((25, 20, 5))
        
        # Fonts
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        font_sub = pygame.font.SysFont("malgungothic", 18)
        
        # Draw player
        p_rect = pygame.Rect(self.player_x - 20, 560, 40, 40)
        pygame.draw.rect(virtual_surf, (50, 130, 240), p_rect)
        pygame.draw.rect(virtual_surf, WHITE, p_rect, 2)
        
        # Draw sparks
        for sp in self.sparks:
            pygame.draw.rect(virtual_surf, (235, 210, 40), sp)
            pygame.draw.rect(virtual_surf, WHITE, sp, 1)
            
        draw_terminal_hud(virtual_surf, "ELECTRIC SPARKS EVASION MANEUVER", self.limit_time, self.elapsed_time, (235, 210, 40))
        txt_desc = font_sub.render("ELECTRICIAN MISSION: [A] / [D] 키로 좌우 조종하여 상단에서 떨어지는 전류 스파크 피격 방지!", True, WHITE)
        virtual_surf.blit(txt_desc, (40, 60))
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((20, 15, 5, 220))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 고전압 그리드 방어 완료 (SUCCESS) ■", True, (100, 240, 120))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 변전소 낙뢰 충격 피격 (FAIL) 🚨", True, (240, 50, 50))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = HighVoltageSparkDodgeGame()
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