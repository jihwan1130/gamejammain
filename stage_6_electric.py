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

class HighVoltageSparkDodgeGame:
    def __init__(self):
        self.thunder_img = None
        self.thunder2_img = None
        self.bg_img = None
        try:
            t_path = os.path.join("assets", "thunder.png")
            t2_path = os.path.join("assets", "thunder2.png")
            if os.path.exists(t_path):
                self.thunder_img = pygame.image.load(t_path).convert()
                self.thunder_img.set_colorkey((0, 0, 0))
            if os.path.exists(t2_path):
                self.thunder2_img = pygame.image.load(t2_path).convert()
                self.thunder2_img.set_colorkey((0, 0, 0))
                
            bg_path = os.path.join("assets", "thunderback.jpg")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"이미지 에셋 로드 실패: {e}")
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
                self.sparks.append({
                    "rect": pygame.Rect(random.randint(60, 920), 120, 30, 60),
                    "type": random.choice(["thunder", "thunder2"])
                })
                
            p_rect = pygame.Rect(self.player_x - 20, 560, 40, 40)
            
            # Update sparks and check collisions
            for sp in self.sparks[:]:
                sp["rect"].y += 9
                if p_rect.colliderect(sp["rect"]):
                    self.state = "FAIL"
                    play_sfx = get_main_val('play_sfx')
                    if play_sfx:
                        play_sfx("sfx_click")
                    break
                if sp["rect"].y > 640:
                    self.sparks.remove(sp)
                    
            if self.elapsed_time >= self.limit_time:
                self.state = "SUCCESS"
                
    def handle_input(self):
        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player_x = max(50, self.player_x - 9)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player_x = min(950, self.player_x + 9)
                
    def handle_event(self, event):
        settings = get_main_val('settings')
        vol = settings.volume if settings else 0.5
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
                
    def draw(self, surface):
        WHITE = get_main_val('WHITE', (255, 255, 255))
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 가독성을 높이기 위해 어두운 반투명 오버레이 추가
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((20, 15, 10, 160))  # R, G, B, Alpha
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
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
            img = self.thunder_img if sp["type"] == "thunder" else self.thunder2_img
            if img:
                scaled_img = pygame.transform.scale(img, (sp["rect"].width, sp["rect"].height))
                virtual_surf.blit(scaled_img, sp["rect"])
            else:
                pygame.draw.rect(virtual_surf, (235, 210, 40), sp["rect"])
                pygame.draw.rect(virtual_surf, WHITE, sp["rect"], 1)
            
        from visual_effects import draw_terminal_hud
        draw_terminal_hud(virtual_surf, "ELECTRIC SPARKS EVASION MANEUVER", self.limit_time, self.elapsed_time, (235, 210, 40))
        txt_desc = font_sub.render("ELECTRICIAN MISSION: [A]/[D] 또는 [방향키]로 좌우 조종하여 전류 스파크를 회피하십시오!", True, WHITE)
        virtual_surf.blit(txt_desc, (40, 60))
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((20, 15, 5, 220))
            virtual_surf.blit(overlay, (0, 0))
            
            is_campaign = False
            settings = get_main_val('settings')
            if settings and settings.is_campaign:
                is_campaign = True
                
            if is_campaign:
                sub_text = "[ ENTER: 계속 진행 ]"
            else:
                sub_text = "[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]"
                
            if self.state == "SUCCESS":
                msg = font_main.render("■ 고전압 그리드 방어 완료 (SUCCESS) ■", True, (100, 240, 120))
                sub = font_sub.render(sub_text, True, WHITE)
            else:
                msg = font_main.render("🚨 변전소 낙뢰 충격 피격 (FAIL) 🚨", True, (240, 50, 50))
                sub = font_sub.render(sub_text, True, WHITE)
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