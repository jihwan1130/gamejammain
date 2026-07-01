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
        self.penalty_selected = None
        
    def on_fail(self):
        self.penalty_selected = None

    def apply_penalty(self):
        settings = get_main_val('settings')
        resources_game = getattr(settings, 'resources_game', None) if settings else None
        if not resources_game:
            return
        if self.penalty_selected == 1:
            if hasattr(resources_game, 'resources') and "산소" in resources_game.resources:
                resources_game.resources["산소"] = max(0, resources_game.resources["산소"] - 50)
                print(f"[PENALTY] Oxygen decreased by 50. Current: {resources_game.resources['산소']}")
        elif self.penalty_selected == 2:
            if hasattr(resources_game, 'resources') and "정신력" in resources_game.resources:
                resources_game.resources["정신력"] = max(0, resources_game.resources["정신력"] - 50)
                print(f"[PENALTY] Mental decreased by 50. Current: {resources_game.resources['정신력']}")

    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # Check win condition
            if all(x == 0 for x in self.grid):
                self.state = "SUCCESS"
            elif self.elapsed_time >= self.limit_time:
                self.state = "FAIL"
                self.on_fail()
                
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        settings = get_main_val('settings')
        vol = settings.volume if settings else 0.5
        width = settings.width if settings else 1000
        height = settings.height if settings else 700
        play_sfx = get_main_val('play_sfx')
        go_to_minigames = get_main_val('go_to_minigames') or get_main_val('go_to_main_menu')
        keyboard_sfx = get_main_val('keyboard_sfx')
        
        is_campaign = False
        if settings and settings.is_campaign:
            is_campaign = True
            
        if self.state == "FAIL":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                vmx = int(mx * 1000.0 / width)
                vmy = int(my * 700.0 / height)
                
                # 버튼 1 영역: (200, 390, 260, 90)
                # 버튼 2 영역: (540, 390, 260, 90)
                btn1_rect = pygame.Rect(200, 390, 260, 90)
                btn2_rect = pygame.Rect(540, 390, 260, 90)
                
                if btn1_rect.collidepoint(vmx, vmy):
                    self.penalty_selected = 1
                    if play_sfx:
                        play_sfx("sfx_click")
                elif btn2_rect.collidepoint(vmx, vmy):
                    self.penalty_selected = 2
                    if play_sfx:
                        play_sfx("sfx_click")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.penalty_selected = 1
                    if play_sfx:
                        play_sfx("sfx_click")
                elif event.key == pygame.K_2:
                    self.penalty_selected = 2
                    if play_sfx:
                        play_sfx("sfx_click")
        
        if self.state != "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if play_sfx:
                        play_sfx("sfx_end")
                    if go_to_minigames:
                        go_to_minigames()
                elif event.key == pygame.K_RETURN:
                    if self.state == "FAIL" and self.penalty_selected is None:
                        return
                    if self.state == "FAIL" and self.penalty_selected is not None:
                        self.apply_penalty()
                    if is_campaign:
                        pass
                    else:
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
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            vmx = int(mx * 1000 / width)
            vmy = int(my * 700 / height)
            
            for idx in range(9):
                col = idx % 3
                row = idx // 3
                grid_rect = pygame.Rect(320 + col * 120, 200 + row * 120, 100, 100)
                if grid_rect.collidepoint((vmx, vmy)):
                    self.grid[idx] = (self.grid[idx] + 90) % 360
                    if play_sfx:
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
            
            is_campaign = False
            settings = get_main_val('settings')
            if settings and settings.is_campaign:
                is_campaign = True
                
            if is_campaign:
                sub_text = "[ ENTER: 결과 확인 및 계속 진행 ]"
            else:
                sub_text = "[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]"
                
            if self.state == "SUCCESS":
                msg = font_main.render("■ 파이프라인 전력망 재라우팅 완수 (SUCCESS) ■", True, (100, 255, 150))
                sub = font_sub.render(sub_text, True, WHITE)
                virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
                virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            else:
                msg = font_main.render("🚨 회로 단선 배전반 파손 (FAIL) 🚨", True, (240, 50, 50))
                virtual_surf.blit(msg, (500 - msg.get_width()//2, 260))
                
                if self.penalty_selected is None:
                    desc_text = "다음 패널티 중 하나를 반드시 선택해야 진행할 수 있습니다. (1번 또는 2번 키/클릭)"
                else:
                    selected_name = "산소 -50" if self.penalty_selected == 1 else "정신력 -50"
                    desc_text = f"선택 완료: [{selected_name}] - {sub_text}"
                    
                lbl_desc = font_sub.render(desc_text, True, (250, 200, 100))
                virtual_surf.blit(lbl_desc, (500 - lbl_desc.get_width()//2, 320))
                
                # 버튼 그리기
                btn1_rect = pygame.Rect(200, 390, 260, 90)
                btn2_rect = pygame.Rect(540, 390, 260, 90)
                
                scr_w, scr_h = surface.get_size()
                mx, my = pygame.mouse.get_pos()
                vmx = int(mx * 1000.0 / scr_w)
                vmy = int(my * 700.0 / scr_h)
                
                hover_btn1 = btn1_rect.collidepoint(vmx, vmy)
                hover_btn2 = btn2_rect.collidepoint(vmx, vmy)
                
                # 버튼 1: 산소 감소
                b1_color = (80, 20, 20) if self.penalty_selected == 1 else ((40, 10, 10) if hover_btn1 else (20, 5, 5))
                pygame.draw.rect(virtual_surf, b1_color, btn1_rect)
                pygame.draw.rect(virtual_surf, (240, 50, 50), btn1_rect, 2 if self.penalty_selected == 1 else 1)
                
                b1_title = font_main.render("1. 생명유지 시스템 고장", True, (255, 200, 200))
                b1_desc = font_sub.render("산소 -50", True, (240, 100, 100))
                virtual_surf.blit(b1_title, (330 - b1_title.get_width()//2, 405))
                virtual_surf.blit(b1_desc, (330 - b1_desc.get_width()//2, 440))
                
                # 버튼 2: 정신력 감소
                b2_color = (40, 40, 80) if self.penalty_selected == 2 else ((20, 20, 40) if hover_btn2 else (10, 10, 20))
                pygame.draw.rect(virtual_surf, b2_color, btn2_rect)
                pygame.draw.rect(virtual_surf, (50, 180, 180), btn2_rect, 2 if self.penalty_selected == 2 else 1)
                
                b2_title = font_main.render("2. 정전 충격 피격", True, (200, 200, 255))
                b2_desc = font_sub.render("정신력 -50", True, (150, 200, 255))
                virtual_surf.blit(b2_title, (670 - b2_title.get_width()//2, 405))
                virtual_surf.blit(b2_desc, (670 - b2_desc.get_width()//2, 440))
                
                if self.penalty_selected is not None:
                    lbl_enter = font_sub.render(sub_text, True, WHITE)
                    virtual_surf.blit(lbl_enter, (500 - lbl_enter.get_width()//2, 510))
            
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