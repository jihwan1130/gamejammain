import pygame, random, sys, os

class EnergyGridGame:
    def __init__(self):
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "spacex.png")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"spacex.png 로드 실패: {e}")
        self.reset()
        
    def reset(self):
        self.grid = [random.choice([0, 90, 180, 270]) for _ in range(9)]
        if all(x == 0 for x in self.grid):
            self.grid[0] = 90
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 12.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # Check win condition
            if all(x == 0 for x in self.grid):
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
            
            for idx in range(9):
                col = idx % 3
                row = idx // 3
                grid_rect = pygame.Rect(320 + col * 120, 200 + row * 120, 100, 100)
                if grid_rect.collidepoint((vmx, vmy)):
                    self.grid[idx] = (self.grid[idx] + 90) % 360
                    play_sfx("sfx_click")
                    break
                    
    def draw(self, surface):
        from visual_effects import draw_terminal_hud
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 가독성을 높이기 위해 어두운 반투명 오버레이 추가
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((5, 20, 20, 160))  # R, G, B, Alpha
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill((5, 20, 20))
        
        # Fonts
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        font_sub = pygame.font.SysFont("malgungothic", 18)
        
        draw_terminal_hud(virtual_surf, "ENERGY REROUTING GRID DEFENSE", self.limit_time, self.elapsed_time, (50, 180, 180))
        txt_info = font_sub.render("각 회로 패널 노드를 클릭하여 모든 파이프 인디케이터 라인이 위쪽(0도)을 향하게 정렬하십시오.", True, WHITE)
        virtual_surf.blit(txt_info, (40, 60))
        
        # Draw grids
        for idx in range(9):
            col = idx % 3
            row = idx // 3
            grid_rect = pygame.Rect(320 + col * 120, 200 + row * 120, 100, 100)
            angle = self.grid[idx]
            
            node_color = (50, 180, 180) if angle == 0 else (80, 90, 90)
            pygame.draw.rect(virtual_surf, node_color, grid_rect)
            pygame.draw.rect(virtual_surf, WHITE, grid_rect, 2)
            
            cx, cy = grid_rect.center
            if angle == 0:
                pygame.draw.line(virtual_surf, (15, 15, 15), (cx, cy), (cx, grid_rect.top), 6)
            elif angle == 90:
                pygame.draw.line(virtual_surf, (15, 15, 15), (cx, cy), (grid_rect.right, cy), 6)
            elif angle == 180:
                pygame.draw.line(virtual_surf, (15, 15, 15), (cx, cy), (cx, grid_rect.bottom), 6)
            elif angle == 270:
                pygame.draw.line(virtual_surf, (15, 15, 15), (cx, cy), (grid_rect.left, cy), 6)
                
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((5, 15, 15, 220))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 파이프라인 전력망 재라우팅 완수 (SUCCESS) ■", True, (100, 255, 150))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 회로 단선 배전반 파손 (FAIL) 🚨", True, (240, 50, 50))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = EnergyGridGame()
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