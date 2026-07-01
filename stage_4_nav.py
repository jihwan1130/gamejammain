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

class StellarMemoryGame:
    def __init__(self):
        self.symbols = ["Ω", "Ψ", "Φ", "Ω", "Ψ", "Φ"]
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "ghost.png")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"ghost.png 로드 실패: {e}")
        self.reset()
        
    def reset(self):
        random.shuffle(self.symbols)
        self.cards = [{"val": self.symbols[i], "flipped": False, "matched": False} for i in range(6)]
        self.selected_indices = []
        self.delay_timer = 0
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 10.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        self.penalty_selected = None
        self.has_astronomer = False
        
    def on_fail(self):
        self.penalty_selected = None
        settings = get_main_val('settings')
        resources_game = getattr(settings, 'resources_game', None) if settings else None
        self.has_astronomer = False
        if resources_game and hasattr(resources_game, 'my_crew'):
            if "천문학자" in resources_game.my_crew:
                self.has_astronomer = True
        
        # 천문학자가 없다면 자동으로 전기 -50 패널티 설정
        if not self.has_astronomer:
            self.penalty_selected = 2

    def apply_penalty(self):
        settings = get_main_val('settings')
        resources_game = getattr(settings, 'resources_game', None) if settings else None
        if not resources_game:
            return
        if self.penalty_selected == 1:
            if hasattr(resources_game, 'my_crew') and "천문학자" in resources_game.my_crew:
                resources_game.my_crew.remove("천문학자")
                print("[PENALTY] Astronomer (천문학자) exiled.")
        elif self.penalty_selected == 2:
            if hasattr(resources_game, 'resources') and "전기" in resources_game.resources:
                resources_game.resources["전기"] = max(0, resources_game.resources["전기"] - 50)
                print(f"[PENALTY] Electric decreased by 50. Current: {resources_game.resources['전기']}")

    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # Non-blocking card comparison delay timer
            if len(self.selected_indices) == 2:
                self.delay_timer += 1
                if self.delay_timer >= 20: # ~0.3 seconds at 60fps
                    idx1, idx2 = self.selected_indices
                    if self.cards[idx1]["val"] == self.cards[idx2]["val"]:
                        self.cards[idx1]["matched"] = True
                        self.cards[idx2]["matched"] = True
                        play_sfx = get_main_val('play_sfx')
                        if play_sfx:
                            play_sfx("sfx_click")
                    else:
                        self.cards[idx1]["flipped"] = False
                        self.cards[idx2]["flipped"] = False
                    self.selected_indices = []
                    self.delay_timer = 0
                    
            if all(c["matched"] for c in self.cards):
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
        go_to_main_menu = get_main_val('go_to_main_menu')
        keyboard_sfx = get_main_val('keyboard_sfx')
        
        is_campaign = False
        if settings and settings.is_campaign:
            is_campaign = True
            
        if self.state == "FAIL":
            if self.has_astronomer:
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
            if len(self.selected_indices) < 2:
                mx, my = event.pos
                # Convert mouse pos to virtual coordinates
                vmx = int(mx * 1000 / width)
                vmy = int(my * 700 / height)
                
                for i in range(6):
                    col = i % 3
                    row = i // 3
                    card_rect = pygame.Rect(220 + col * 210, 200 + row * 190, 150, 150)
                    if card_rect.collidepoint((vmx, vmy)):
                        if not self.cards[i]["flipped"] and not self.cards[i]["matched"]:
                            self.cards[i]["flipped"] = True
                            self.selected_indices.append(i)
                            if play_sfx:
                                play_sfx("sfx_click")
                            break
                            
    def draw(self, surface):
        WHITE = get_main_val('WHITE', (255, 255, 255))
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 가독성을 높이기 위해 어두운 반투명 오버레이 추가
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((5, 10, 20, 160))  # R, G, B, Alpha
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill((5, 15, 30))
        
        # Fonts
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        font_sub = pygame.font.SysFont("malgungothic", 18)
        font_card = pygame.font.SysFont("consolas", 40, bold=True)
        
        # Draw cards
        for i in range(6):
            col = i % 3
            row = i // 3
            card_rect = pygame.Rect(220 + col * 210, 200 + row * 190, 150, 150)
            
            if self.cards[i]["matched"]:
                pygame.draw.rect(virtual_surf, (30, 160, 90), card_rect)
                pygame.draw.rect(virtual_surf, WHITE, card_rect, 2)
                txt = font_card.render(self.cards[i]["val"], True, WHITE)
                virtual_surf.blit(txt, (card_rect.centerx - txt.get_width()//2, card_rect.centery - txt.get_height()//2))
            elif self.cards[i]["flipped"]:
                pygame.draw.rect(virtual_surf, (40, 110, 210), card_rect)
                pygame.draw.rect(virtual_surf, WHITE, card_rect, 2)
                txt = font_card.render(self.cards[i]["val"], True, WHITE)
                virtual_surf.blit(txt, (card_rect.centerx - txt.get_width()//2, card_rect.centery - txt.get_height()//2))
            else:
                pygame.draw.rect(virtual_surf, (70, 85, 100), card_rect)
                pygame.draw.rect(virtual_surf, (40, 110, 210), card_rect, 2)
                pygame.draw.circle(virtual_surf, (40, 110, 210), card_rect.center, 12, 1)
                
        from visual_effects import draw_terminal_hud
        draw_terminal_hud(virtual_surf, "NAVIGATION MEMORY CONGRUENCE", self.limit_time, self.elapsed_time, (40, 110, 210))
        txt_info = font_sub.render("ASTRONOMER JOB BONUS: 서브루틴 오차 계산망 복사 완료. 동기화 매칭 유도", True, WHITE)
        virtual_surf.blit(txt_info, (40, 60))
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((5, 10, 20, 220))
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
                msg = font_main.render("■ 항로 좌표 복원 성공 (SUCCESS) ■", True, (80, 240, 120))
                sub = font_sub.render(sub_text, True, WHITE)
                virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
                virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            else:
                msg = font_main.render("🚨 매트릭스 백업 손실 (FAIL) 🚨", True, (240, 60, 60))
                virtual_surf.blit(msg, (500 - msg.get_width()//2, 260))
                
                if not self.has_astronomer:
                    lbl_warning = font_main.render("천문학자가 존재하지 않아 항로 이탈이 발생했습니다.", True, (255, 100, 100))
                    lbl_subwarning = font_sub.render("페널티: 전기 -50  |  " + sub_text, True, (200, 200, 200))
                    virtual_surf.blit(lbl_warning, (500 - lbl_warning.get_width()//2, 330))
                    virtual_surf.blit(lbl_subwarning, (500 - lbl_subwarning.get_width()//2, 380))
                else:
                    if self.penalty_selected is None:
                        desc_text = "다음 패널티 중 하나를 반드시 선택해야 진행할 수 있습니다. (1번 또는 2번 키/클릭)"
                    else:
                        selected_name = "천문학자 추방" if self.penalty_selected == 1 else "전기 -50"
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
                    
                    # 버튼 1: 천문학자 추방
                    b1_color = (80, 20, 20) if self.penalty_selected == 1 else ((40, 10, 10) if hover_btn1 else (20, 5, 5))
                    pygame.draw.rect(virtual_surf, b1_color, btn1_rect)
                    pygame.draw.rect(virtual_surf, (240, 60, 60), btn1_rect, 2 if self.penalty_selected == 1 else 1)
                    
                    b1_title = font_main.render("1. 천문학자 추방", True, (255, 200, 200))
                    b1_desc = font_sub.render("추방: [천문학자]", True, (240, 100, 100))
                    virtual_surf.blit(b1_title, (330 - b1_title.get_width()//2, 405))
                    virtual_surf.blit(b1_desc, (330 - b1_desc.get_width()//2, 440))
                    
                    # 버튼 2: 전기 감소
                    b2_color = (40, 40, 80) if self.penalty_selected == 2 else ((20, 20, 40) if hover_btn2 else (10, 10, 20))
                    pygame.draw.rect(virtual_surf, b2_color, btn2_rect)
                    pygame.draw.rect(virtual_surf, (40, 110, 210), btn2_rect, 2 if self.penalty_selected == 2 else 1)
                    
                    b2_title = font_main.render("2. 시스템 과부하", True, (200, 200, 255))
                    b2_desc = font_sub.render("전기 -50", True, (120, 180, 255))
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
    game = StellarMemoryGame()
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