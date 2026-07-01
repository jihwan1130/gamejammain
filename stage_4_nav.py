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
            if self.state == "SUCCESS":
                msg = font_main.render("■ 항로 좌표 복원 성공 (SUCCESS) ■", True, (80, 240, 120))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 매트릭스 백업 손실 (FAIL) 🚨", True, (240, 60, 60))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
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