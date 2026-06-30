import pygame, random, sys

class RogueRobotGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.robots = []
        for _ in range(5):
            rect = pygame.Rect(random.randint(200, 800), random.randint(200, 500), 45, 45)
            self.robots.append({
                "rect": rect, 
                "vx": random.choice([-5, -3, 3, 5]), 
                "vy": random.choice([-5, -3, 3, 5])
            })
        self.start_ticks = pygame.time.get_ticks()
        self.limit_time = 10.0
        self.elapsed_time = 0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            for r in self.robots:
                rect = r["rect"]
                rect.x += r["vx"]
                rect.y += r["vy"]
                if rect.left < 40 or rect.right > 960: r["vx"] *= -1
                if rect.top < 140 or rect.bottom > 660: r["vy"] *= -1
                
            if len(self.robots) == 0:
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
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Convert mouse pos to virtual coordinates
            vmx = int(mx * 1000 / settings.width)
            vmy = int(my * 700 / settings.height)
            for r in self.robots[:]:
                if r["rect"].collidepoint((vmx, vmy)):
                    self.robots.remove(r)
                    play_sfx("sfx_click")
                    break
                    
    def draw(self, surface):
        from visual_effects import draw_terminal_hud
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        virtual_surf.fill((30, 15, 5))
        
        # Fonts
        font_sub = pygame.font.SysFont("malgungothic", 18)
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        
        # Draw robots
        for r in self.robots:
            pygame.draw.rect(virtual_surf, (220, 60, 40), r["rect"])
            pygame.draw.rect(virtual_surf, (255, 240, 220), r["rect"], 2)
            pygame.draw.circle(virtual_surf, (255, 240, 220), r["rect"].center, 6)
            
        # Draw crosshair
        from main import settings
        mx, my = pygame.mouse.get_pos()
        vmx = int(mx * 1000 / settings.width)
        vmy = int(my * 700 / settings.height)
        pygame.draw.circle(virtual_surf, (255, 240, 220), (vmx, vmy), 18, 1)
        pygame.draw.circle(virtual_surf, (220, 60, 40), (vmx, vmy), 3)
        
        draw_terminal_hud(virtual_surf, "ROGUE MECHANIZATION TERMINATION", self.limit_time, self.elapsed_time, (235, 130, 40))
        txt_info = font_sub.render(f"POLICE PROTOCOL: 잔여 위협 개체 사살 수 -> {len(self.robots)}기 남음", True, (255, 240, 220))
        virtual_surf.blit(txt_info, (40, 60))
        
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