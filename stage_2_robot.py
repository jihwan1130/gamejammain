import pygame
import os
import random

def get_main_val(name, default=None):
    try:
        import sys
        main_mod = sys.modules.get('main') or sys.modules.get('__main__')
        if main_mod and hasattr(main_mod, name):
            return getattr(main_mod, name)
    except:
        pass
    return default

def load_gif_frames(filepath):
    frames = []
    try:
        from PIL import Image, ImageSequence
        gif = Image.open(filepath)
        for frame in ImageSequence.Iterator(gif):
            frame_rgba = frame.convert("RGBA")
            data = frame_rgba.tobytes("raw", "RGBA")
            size = frame_rgba.size
            surf = pygame.image.fromstring(data, size, "RGBA")
            surf_conv = surf.convert_alpha()
            frames.append(surf_conv)
    except Exception as e:
        print(f"GIF 프레임 로드 실패: {e}")
    return frames

class RogueRobotGame:
    def __init__(self):
        # 1. 배경 이미지 로드
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "Stage_2.png")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"Stage_2.png 로드 실패: {e}")
            
        # 2. 로봇 에셋 로드 (ai1, ai3)
        self.ai1_frames = []
        self.ai3_frames = []
        try:
            self.ai1_frames = load_gif_frames(os.path.join("assets", "ai1.gif"))
            self.ai3_frames = load_gif_frames(os.path.join("assets", "ai3.gif"))
        except Exception as e:
            print(f"로봇 GIF 에셋 로드 실패: {e}")
            
        # 3. 총 발사 효과음 로드
        self.gun2_sfx = None
        try:
            gun2_path = os.path.join("assets", "gun2.MP3")
            if os.path.exists(gun2_path):
                self.gun2_sfx = pygame.mixer.Sound(gun2_path)
        except Exception as e:
            print(f"gun2.MP3 로드 실패: {e}")
            
        self.reset()
            
    def reset(self):
        self.robots = []
        size = 112  # 로봇 캐릭터 크기
        # 로봇 개수 총 10개 생성
        for _ in range(10):
            rect = pygame.Rect(random.randint(200, 800), random.randint(200, 500), size, size)
            self.robots.append({
                "rect": rect, 
                # 속도를 기존보다 1.2배 더 빠르게 [-7, -5, 5, 7]로 적용
                "vx": random.choice([-7, -5, 5, 7]), 
                "vy": random.choice([-7, -5, 5, 7]),
                "type": random.choice(["ai1", "ai3"]),
                "frame_offset": random.randint(0, 100)
            })
        self.start_ticks = pygame.time.get_ticks()
        self.limit_time = 8.0  # 시간 2초 단축 (10.0 -> 8.0)
        self.elapsed_time = 0
        self.state = "PLAYING"
        self.penalty_selected = None
        self.has_police = False
        self.fail_time = 0
        
    def on_fail(self):
        self.penalty_selected = None
        self.fail_time = pygame.time.get_ticks()
        settings = get_main_val('settings')
        resources_game = getattr(settings, 'resources_game', None) if settings else None
        self.has_police = False
        if resources_game and hasattr(resources_game, 'my_crew'):
            if "경찰" in resources_game.my_crew:
                self.has_police = True

    def apply_penalty(self):
        settings = get_main_val('settings')
        resources_game = getattr(settings, 'resources_game', None) if settings else None
        if not resources_game:
            return
        if self.penalty_selected == 1:
            if hasattr(resources_game, 'my_crew') and "경찰" in resources_game.my_crew:
                resources_game.my_crew.remove("경찰")
                print("[PENALTY] Police (경찰) died.")
        elif self.penalty_selected == 2:
            if hasattr(resources_game, 'resources') and "전기" in resources_game.resources:
                resources_game.resources["전기"] = max(0, resources_game.resources["전기"] - 50)
                print(f"[PENALTY] Electric decreased by 50. Current: {resources_game.resources['전기']}")

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
                self.on_fail()
        elif self.state == "FAIL":
            if not self.has_police:
                now = pygame.time.get_ticks()
                if now - self.fail_time >= 2500:
                    go_to_main_menu = get_main_val('go_to_main_menu')
                    if go_to_main_menu:
                        go_to_main_menu()
                    else:
                        pygame.quit()
                        import sys
                        sys.exit()
                
    def handle_input(self):
        pass
            
    def draw(self, surface):
        WHITE = get_main_val('WHITE', (255, 255, 255))
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        
        # Draw background
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 분위기에 맞게 어두운 보라톤 오버레이 적용
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((28, 12, 40, 180))
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill((20, 10, 30))
        
        # Fonts
        font_sub = pygame.font.SysFont("malgungothic", 18)
        font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
        
        # Draw robots (using cached GIF frames)
        for r in self.robots:
            rtype = r.get("type", "ai1")
            offset = r.get("frame_offset", 0)
            frames = self.ai1_frames if rtype == "ai1" else self.ai3_frames
            
            if frames:
                frame_idx = ((pygame.time.get_ticks() + offset * 50) // 100) % len(frames)
                img = frames[frame_idx]
                scaled_img = pygame.transform.scale(img, (r["rect"].width, r["rect"].height))
                virtual_surf.blit(scaled_img, r["rect"])
            else:
                pygame.draw.rect(virtual_surf, (220, 60, 40), r["rect"])
                pygame.draw.rect(virtual_surf, (255, 240, 220), r["rect"], 2)
                pygame.draw.circle(virtual_surf, (255, 240, 220), r["rect"].center, 6)
            
        # Draw crosshair
        settings = get_main_val('settings')
        width = settings.width if settings else surface.get_width()
        height = settings.height if settings else surface.get_height()
        
        mx, my = pygame.mouse.get_pos()
        vmx = int(mx * 1000 / width)
        vmy = int(my * 700 / height)
        pygame.draw.circle(virtual_surf, (180, 100, 255), (vmx, vmy), 18, 1)
        pygame.draw.circle(virtual_surf, (255, 60, 150), (vmx, vmy), 3)
        
        # 3. HUD 및 시간 프로그레스 바 렌더링
        COLOR_PURPLE = (120, 40, 180)
        
        pygame.draw.rect(virtual_surf, COLOR_PURPLE, (10, 10, 980, 680), 2)
        pygame.draw.rect(virtual_surf, COLOR_PURPLE, (15, 15, 970, 670), 1)
        
        # 프로그레스 바 시간 표시
        time_ratio = max(0.0, (self.limit_time - self.elapsed_time) / self.limit_time)
        bar_max_w = 400
        bar_h = 16
        bar_x = 30
        bar_y = 25
        
        pygame.draw.rect(virtual_surf, COLOR_PURPLE, (bar_x, bar_y, bar_max_w, bar_h), 2)
        fill_w = int(bar_max_w * time_ratio)
        if fill_w > 0:
            bar_color = (150, 80, 220) if time_ratio > 0.5 else ((220, 100, 150) if time_ratio > 0.2 else (255, 60, 40))
            pygame.draw.rect(virtual_surf, bar_color, (bar_x + 2, bar_y + 2, fill_w - 4, bar_h - 4))
        
        # 4. 로봇 잔여 수량 인디케이터 그리기
        alive_count = len(self.robots)
        total_count = 10
        indicator_w = 18
        indicator_h = 14
        gap = 6
        start_x = 1000 - 30 - (total_count * (indicator_w + gap))
        indicator_y = 26
        
        for i in range(total_count):
            bx = start_x + i * (indicator_w + gap)
            if i < alive_count:
                color = (180, 100, 255)
            else:
                color = (10, 5, 20)
                
            pygame.draw.rect(virtual_surf, color, (bx, indicator_y, indicator_w, indicator_h))
            pygame.draw.rect(virtual_surf, COLOR_PURPLE, (bx, indicator_y, indicator_w, indicator_h), 1)
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((15, 10, 5, 210))
            virtual_surf.blit(overlay, (0, 0))
            
            is_campaign = False
            settings = get_main_val('settings')
            if settings and settings.is_campaign:
                is_campaign = True
                
            if is_campaign:
                sub_control_text = "[ ENTER: 결과 확인 및 계속 진행 ]"
            else:
                sub_control_text = "[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]"
                
            if self.state == "SUCCESS":
                msg = font_main.render("■ 위협 로봇 전원 사살 (SUCCESS) ■", True, (70, 220, 70))
                sub = font_sub.render("경찰 크루의 신속한 저격으로 거주 구역이 개방되었습니다.", True, WHITE)
                sub_control = font_sub.render(sub_control_text, True, WHITE)
                virtual_surf.blit(msg, (500 - msg.get_width()//2, 300))
                virtual_surf.blit(sub, (500 - sub.get_width()//2, 350))
                virtual_surf.blit(sub_control, (500 - sub_control.get_width()//2, 400))
            else:
                msg = font_main.render("🚨 거주 구역 전면 폐쇄 (FAIL) 🚨", True, (220, 60, 40))
                virtual_surf.blit(msg, (500 - msg.get_width()//2, 260))
                
                if not self.has_police:
                    lbl_warning = font_main.render("경찰관이 없어 로봇에게 전기를 뺏겼습니다.", True, (255, 100, 100))
                    lbl_subwarning = font_sub.render("잠시 후 타이틀 화면으로 이동합니다... (게임 오버)", True, (200, 200, 200))
                    virtual_surf.blit(lbl_warning, (500 - lbl_warning.get_width()//2, 330))
                    virtual_surf.blit(lbl_subwarning, (500 - lbl_subwarning.get_width()//2, 380))
                else:
                    if self.penalty_selected is None:
                        desc_text = "다음 패널티 중 하나를 반드시 선택해야 진행할 수 있습니다. (1번 또는 2번 키/클릭)"
                    else:
                        selected_name = "경찰관 사망" if self.penalty_selected == 1 else "전기 -50"
                        desc_text = f"선택 완료: [{selected_name}] - {sub_control_text}"
                        
                    lbl_desc = font_sub.render(desc_text, True, (250, 200, 100))
                    virtual_surf.blit(lbl_desc, (500 - lbl_desc.get_width()//2, 320))
                    
                    # 버튼 그리기
                    btn1_rect = pygame.Rect(200, 400, 260, 90)
                    btn2_rect = pygame.Rect(540, 400, 260, 90)
                    
                    scr_w, scr_h = surface.get_size()
                    mx, my = pygame.mouse.get_pos()
                    vmx = int(mx * 1000.0 / scr_w)
                    vmy = int(my * 700.0 / scr_h)
                    
                    hover_btn1 = btn1_rect.collidepoint(vmx, vmy)
                    hover_btn2 = btn2_rect.collidepoint(vmx, vmy)
                    
                    # 버튼 1: 경찰관 사망
                    b1_color = (80, 20, 20) if self.penalty_selected == 1 else ((40, 10, 10) if hover_btn1 else (20, 5, 5))
                    pygame.draw.rect(virtual_surf, b1_color, btn1_rect)
                    pygame.draw.rect(virtual_surf, (220, 60, 40), btn1_rect, 2 if self.penalty_selected == 1 else 1)
                    
                    b1_title = font_main.render("1. 경찰관의 희생", True, (255, 200, 200))
                    b1_desc = font_sub.render("사망: [경찰]", True, (240, 100, 100))
                    virtual_surf.blit(b1_title, (330 - b1_title.get_width()//2, 415))
                    virtual_surf.blit(b1_desc, (330 - b1_desc.get_width()//2, 450))
                    
                    # 버튼 2: 전기 감소
                    b2_color = (40, 40, 80) if self.penalty_selected == 2 else ((20, 20, 40) if hover_btn2 else (10, 10, 20))
                    pygame.draw.rect(virtual_surf, b2_color, btn2_rect)
                    pygame.draw.rect(virtual_surf, (150, 80, 220), btn2_rect, 2 if self.penalty_selected == 2 else 1)
                    
                    b2_title = font_main.render("2. 전기 강탈", True, (200, 200, 255))
                    b2_desc = font_sub.render("전기 -50", True, (180, 100, 255))
                    virtual_surf.blit(b2_title, (670 - b2_title.get_width()//2, 415))
                    virtual_surf.blit(b2_desc, (670 - b2_desc.get_width()//2, 450))
                    
                    if self.penalty_selected is not None:
                        lbl_enter = font_sub.render(sub_control_text, True, WHITE)
                        virtual_surf.blit(lbl_enter, (500 - lbl_enter.get_width()//2, 520))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)
            
    def handle_event(self, event):
        settings = get_main_val('settings')
        vol = settings.volume if settings else 0.5
        width = settings.width if settings else 1000
        height = settings.height if settings else 700
        play_sfx = get_main_val('play_sfx')
        go_to_minigames = get_main_val('go_to_minigames') or get_main_val('go_to_main_menu')
        keyboard_sfx = get_main_val('keyboard_sfx')
        
        if self.state == "FAIL":
            if not self.has_police:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                vmx = int(mx * 1000.0 / width)
                vmy = int(my * 700.0 / height)
                btn1_rect = pygame.Rect(200, 400, 260, 90)
                btn2_rect = pygame.Rect(540, 400, 260, 90)
                if btn1_rect.collidepoint(vmx, vmy):
                    self.penalty_selected = 1
                    if play_sfx:
                        play_sfx("sfx_click")
                elif btn2_rect.collidepoint(vmx, vmy):
                    self.penalty_selected = 2
                    if play_sfx:
                        play_sfx("sfx_click")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if play_sfx:
                        play_sfx("sfx_end")
                    if go_to_minigames:
                        go_to_minigames()
                elif event.key == pygame.K_1:
                    self.penalty_selected = 1
                    if play_sfx:
                        play_sfx("sfx_click")
                elif event.key == pygame.K_2:
                    self.penalty_selected = 2
                    if play_sfx:
                        play_sfx("sfx_click")
                elif event.key == pygame.K_RETURN:
                    if self.penalty_selected is None:
                        return
                    self.apply_penalty()
                    settings_inst = get_main_val('settings')
                    if settings_inst and not settings_inst.is_campaign:
                        self.reset()
                        if keyboard_sfx:
                            keyboard_sfx.set_volume(vol)
                            keyboard_sfx.play()
            return
            
        elif self.state == "SUCCESS":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if play_sfx:
                        play_sfx("sfx_end")
                    if go_to_minigames:
                        go_to_minigames()
                elif event.key == pygame.K_RETURN:
                    settings_inst = get_main_val('settings')
                    if settings_inst and not settings_inst.is_campaign:
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
            if self.gun2_sfx:
                self.gun2_sfx.set_volume(vol)
                self.gun2_sfx.play()
                
            mx, my = event.pos
            vmx = int(mx * 1000 / width)
            vmy = int(my * 700 / height)
            for r in self.robots[:]:
                if r["rect"].collidepoint((vmx, vmy)):
                    self.robots.remove(r)
                    break

if __name__ == "__main__":
    import sys
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