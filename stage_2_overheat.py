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

class CoreThermalStabilizerGame:
    def __init__(self):
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "red.jpg")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"red.jpg 로드 실패: {e}")
            
        self.font_name = "malgungothic" 
        self.init_fonts()
        self.reset()
        
    def init_fonts(self):
        self.font_main = pygame.font.SysFont(self.font_name, 24, bold=True)
        self.font_sub = pygame.font.SysFont(self.font_name, 18)
        self.font_hud_label = pygame.font.SysFont(self.font_name, 16, bold=True)
        self.font_intro_title = pygame.font.SysFont(self.font_name, 16, bold=True)
        self.font_intro_body = pygame.font.SysFont(self.font_name, 12)
        self.font_intro_button = pygame.font.SysFont(self.font_name, 13, bold=True)
        
    def reset(self):
        self.core_x = 500
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 10.0
        self.state = "INTRO" # INTRO, PLAYING, SUCCESS, FAIL
        self.press_count = 0
        self.penalty_selected = None
        self.has_mechanic = False
        self.fail_time = 0
        
    def on_fail(self):
        self.penalty_selected = None
        self.fail_time = pygame.time.get_ticks()
        settings = get_main_val('settings')
        resources_game = getattr(settings, 'resources_game', None) if settings else None
        self.has_mechanic = False
        if resources_game and hasattr(resources_game, 'my_crew'):
            if "기술자" in resources_game.my_crew:
                self.has_mechanic = True

    def apply_penalty(self):
        settings = get_main_val('settings')
        resources_game = getattr(settings, 'resources_game', None) if settings else None
        if not resources_game:
            return
        if self.penalty_selected == 1:
            if hasattr(resources_game, 'my_crew') and "기술자" in resources_game.my_crew:
                resources_game.my_crew.remove("기술자")
                print("[PENALTY] Mechanic (기술자) died.")
        elif self.penalty_selected == 2:
            if hasattr(resources_game, 'resources') and "산소" in resources_game.resources:
                resources_game.resources["산소"] = max(0, resources_game.resources["산소"] - 50)
                print(f"[PENALTY] Oxygen decreased by 50. Current: {resources_game.resources['산소']}")

    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # Physics: Core slides away from center
            center_dist = (self.core_x - 500) / 350.0
            jitter = random.choice([-10, -5, 5, 10])
            push_force = center_dist * (8.0 + self.elapsed_time * 0.5)
            self.core_x += (jitter + push_force)
            
            # Boundary check
            if self.core_x < 150 or self.core_x > 850:
                self.state = "FAIL"
                self.on_fail()
            elif self.elapsed_time >= self.limit_time:
                self.state = "SUCCESS"
        elif self.state == "FAIL":
            if not self.has_mechanic:
                now = pygame.time.get_ticks()
                if now - self.fail_time >= 2500:
                    go_to_main_menu = get_main_val('go_to_main_menu')
                    if go_to_main_menu:
                        go_to_main_menu()
                    else:
                        pygame.quit()
                        sys.exit()
                
    def handle_input(self):
        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.core_x -= 12
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.core_x += 12
                
    def handle_event(self, event):
        settings = get_main_val('settings')
        vol = settings.volume if settings else 0.5
        go_to_minigames = get_main_val('go_to_minigames') or get_main_val('go_to_main_menu')
        go_to_main_menu = get_main_val('go_to_main_menu')
        play_sfx = get_main_val('play_sfx')
        keyboard_sfx = get_main_val('keyboard_sfx')
        
        is_campaign = False
        if settings and settings.is_campaign:
            is_campaign = True
            
        if self.state == "INTRO":
            btn_w, btn_h = 220, 35
            btn_rect = pygame.Rect((1000 - btn_w)//2, 430, btn_w, btn_h)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if play_sfx:
                        play_sfx("sfx_end")
                    if go_to_minigames:
                        go_to_minigames()
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.state = "PLAYING"
                    self.start_ticks = pygame.time.get_ticks()
                    if play_sfx:
                        play_sfx("sfx_click")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    scr_w, scr_h = pygame.display.get_surface().get_size()
                    mx, my = event.pos
                    vmx = int(mx * (1000.0 / scr_w))
                    vmy = int(my * (700.0 / scr_h))
                    if btn_rect.collidepoint((vmx, vmy)):
                        self.state = "PLAYING"
                        self.start_ticks = pygame.time.get_ticks()
                        if play_sfx:
                            play_sfx("sfx_click")
            return
            
        if self.state == "FAIL":
            if not self.has_mechanic:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                scr_w, scr_h = pygame.display.get_surface().get_size()
                vmx = int(mx * 1000.0 / scr_w)
                vmy = int(my * 700.0 / scr_h)
                
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
                    if self.state == "FAIL":
                        if not self.has_mechanic:
                            if go_to_main_menu:
                                go_to_main_menu()
                            else:
                                pygame.quit()
                                sys.exit()
                            return
                        elif self.penalty_selected is None:
                            return
                        else:
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
                
    def draw(self, surface):
        WHITE = get_main_val('WHITE', (255, 255, 255))
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        theme_red = (220, 50, 40)
        
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((20, 5, 5, 160))
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill((35, 10, 10))
        
        # Draw safe zones & core line
        pygame.draw.rect(virtual_surf, (50, 20, 20), (150, 350 - 25, 700, 50))
        pygame.draw.rect(virtual_surf, (60, 220, 100), (500 - 60, 350 - 25, 120, 50), 2)
        pygame.draw.line(virtual_surf, theme_red, (150, 350), (850, 350), 3)
        
        # Draw moving core circle
        pygame.draw.circle(virtual_surf, theme_red, (int(self.core_x), 350), 22)
        pygame.draw.circle(virtual_surf, (245, 240, 235), (int(self.core_x), 350), 10)
        
        # Draw external frame borders
        pygame.draw.rect(virtual_surf, theme_red, (10, 10, 1000 - 20, 700 - 20), 2)
        pygame.draw.rect(virtual_surf, theme_red, (15, 15, 1000 - 30, 700 - 30), 1)
        
        # Draw time progress bar on the top-left
        remain_time = max(0.0, self.limit_time - self.elapsed_time)
        time_ratio = remain_time / self.limit_time
        
        time_label = self.font_hud_label.render("TIME", True, theme_red)
        virtual_surf.blit(time_label, (30, 23))
        
        pygame.draw.rect(virtual_surf, (30, 10, 10), (80, 25, 220, 20))
        pygame.draw.rect(virtual_surf, theme_red, (80, 25, 220, 20), 1)
        fill_w = int(216 * time_ratio)
        if fill_w > 0:
            pygame.draw.rect(virtual_surf, theme_red, (82, 27, fill_w, 16))
        
        if self.state == "INTRO":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            virtual_surf.blit(overlay, (0, 0))
            
            dialog_w, dialog_h = 500, 260
            dialog_rect = pygame.Rect((1000 - dialog_w)//2, (700 - dialog_h)//2, dialog_w, dialog_h)
            pygame.draw.rect(virtual_surf, (20, 20, 30), dialog_rect, border_radius=10)
            pygame.draw.rect(virtual_surf, theme_red, dialog_rect, width=3, border_radius=10)
            
            txt_title = self.font_intro_title.render("🚨 코어 온도 조절 장치 수동 제어", True, theme_red)
            virtual_surf.blit(txt_title, (500 - txt_title.get_width()//2, dialog_rect.top + 20))
            
            instructions = [
                "코어가 과열되어 중심을 잃고 폭주하려 합니다.",
                "[A] / [D] 또는 방향키로 코어의 중심을 안전 범위 내로 유지해 주세요.",
                "",
                "⏱️ 제한 시간: 10초",
                "🔴 붉은색 코어가 좌우 바운더리를 벗어나면 용해 폭발합니다.",
                "⌨️ 제어: A, D 또는 Left, Right 방향키"
            ]
            
            y_offset = dialog_rect.top + 60
            for line in instructions:
                color = WHITE
                if "제한 시간" in line:
                    color = (255, 150, 0)
                elif "붉은색 코어" in line:
                    color = theme_red
                
                txt_line = self.font_intro_body.render(line, True, color)
                virtual_surf.blit(txt_line, (500 - txt_line.get_width()//2, y_offset))
                y_offset += 20
                
            btn_w, btn_h = 220, 35
            btn_rect = pygame.Rect((1000 - btn_w)//2, dialog_rect.bottom - 50, btn_w, btn_h)
            
            scr_w, scr_h = surface.get_size()
            mx, my = pygame.mouse.get_pos()
            vmx = int(mx * (1000.0 / scr_w))
            vmy = int(my * (700.0 / scr_h))
            hover = btn_rect.collidepoint((vmx, vmy))
            
            btn_color = (200, 60, 50) if hover else (140, 30, 25)
            pygame.draw.rect(virtual_surf, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(virtual_surf, WHITE, btn_rect, width=2, border_radius=5)
            
            txt_btn = self.font_intro_button.render("시작하기 (Space/Enter)", True, WHITE)
            virtual_surf.blit(txt_btn, (500 - txt_btn.get_width()//2, btn_rect.centery - txt_btn.get_height()//2))
            
        elif self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((25, 5, 5, 230))
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
                msg = self.font_main.render("■ 코어 온도 안정화 제어 성공 (SUCCESS) ■", True, (100, 255, 150))
                sub = self.font_sub.render(sub_text, True, WHITE)
                virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
                virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            else:
                msg = self.font_main.render("🚨 코어 과열 용해 파손 (FAIL) 🚨", True, theme_red)
                virtual_surf.blit(msg, (500 - msg.get_width()//2, 260))
                
                if not self.has_mechanic:
                    lbl_warning = self.font_main.render("기계공이 없어서 수리가 불가합니다.", True, (255, 100, 100))
                    lbl_subwarning = self.font_sub.render("잠시 후 타이틀 화면으로 이동합니다... (게임 오버)", True, (200, 200, 200))
                    virtual_surf.blit(lbl_warning, (500 - lbl_warning.get_width()//2, 330))
                    virtual_surf.blit(lbl_subwarning, (500 - lbl_subwarning.get_width()//2, 380))
                else:
                    if self.penalty_selected is None:
                        desc_text = "다음 패널티 중 하나를 반드시 선택해야 진행할 수 있습니다. (1번 또는 2번 키/클릭)"
                    else:
                        selected_name = "기계공의 희생" if self.penalty_selected == 1 else "산소 -50"
                        desc_text = f"선택 완료: [{selected_name}] - {sub_text}"
                        
                    lbl_desc = self.font_sub.render(desc_text, True, (250, 200, 100))
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
                    
                    # 버튼 1: 기계공 사망
                    b1_color = (80, 20, 20) if self.penalty_selected == 1 else ((40, 10, 10) if hover_btn1 else (20, 5, 5))
                    pygame.draw.rect(virtual_surf, b1_color, btn1_rect)
                    pygame.draw.rect(virtual_surf, theme_red, btn1_rect, 2 if self.penalty_selected == 1 else 1)
                    
                    b1_title = self.font_main.render("1. 기계공의 희생", True, (255, 200, 200))
                    b1_desc = self.font_sub.render("사망: [기술자]", True, (240, 100, 100))
                    virtual_surf.blit(b1_title, (330 - b1_title.get_width()//2, 405))
                    virtual_surf.blit(b1_desc, (330 - b1_desc.get_width()//2, 440))
                    
                    # 버튼 2: 산소 감소
                    b2_color = (40, 40, 80) if self.penalty_selected == 2 else ((20, 20, 40) if hover_btn2 else (10, 10, 20))
                    pygame.draw.rect(virtual_surf, b2_color, btn2_rect)
                    pygame.draw.rect(virtual_surf, (100, 100, 255), btn2_rect, 2 if self.penalty_selected == 2 else 1)
                    
                    b2_title = self.font_main.render("2. 산소 유출", True, (200, 200, 255))
                    b2_desc = self.font_sub.render("산소 -50", True, (150, 150, 250))
                    virtual_surf.blit(b2_title, (670 - b2_title.get_width()//2, 405))
                    virtual_surf.blit(b2_desc, (670 - b2_desc.get_width()//2, 440))
                    
                    if self.penalty_selected is not None:
                        lbl_enter = self.font_sub.render(sub_text, True, WHITE)
                        virtual_surf.blit(lbl_enter, (500 - lbl_enter.get_width()//2, 510))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = CoreThermalStabilizerGame()
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