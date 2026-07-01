import pygame, random, math

class FireGame:
    def __init__(self):
        # Load assets once at startup
        self.bg_img = None
        try:
            import os
            bg_path = os.path.join("assets", "fire_map.png")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"fire_map.png 로드 실패: {e}")

        # Pre-cache different sizes of fire animation frames
        self.fire_frames_large = []
        self.fire_frames_medium = []
        self.fire_frames_small = []
        try:
            import os
            from PIL import Image, ImageSequence
            gif_path = os.path.join("assets", "fire.gif")
            if os.path.exists(gif_path):
                gif = Image.open(gif_path)
                for frame in ImageSequence.Iterator(gif):
                    frame_rgba = frame.convert("RGBA")
                    data = frame_rgba.tobytes("raw", "RGBA")
                    size = frame_rgba.size
                    surf = pygame.image.fromstring(data, size, "RGBA")
                    # Erase black background of fire gif
                    surf_conv = surf.convert()
                    surf_conv.set_colorkey((0, 0, 0))
                    
                    self.fire_frames_large.append(pygame.transform.scale(surf_conv, (230, 230)))
                    self.fire_frames_medium.append(pygame.transform.scale(surf_conv, (160, 160)))
                    self.fire_frames_small.append(pygame.transform.scale(surf_conv, (100, 100)))
        except Exception as e:
            print(f"fire.gif 로드 실패: {e}")

        self.water_sfx = None
        try:
            import os
            water_sfx_path = os.path.join("assets", "watersound.MP3")
            if os.path.exists(water_sfx_path):
                self.water_sfx = pygame.mixer.Sound(water_sfx_path)
        except Exception as e:
            print(f"watersound.MP3 로드 실패: {e}")

        self.reset()
        
    def reset(self):
        self.fires = []
        self.start_ticks = pygame.time.get_ticks()
        self.last_update_ticks = self.start_ticks
        self.elapsed_time = 0
        self.limit_time = 15.0
        self.state = "COUNTDOWN" # "COUNTDOWN", "PLAYING", "SUCCESS", "FAIL"
        self.spawned_count = 6
        self.sfx_timer = 0.0
        for _ in range(6):
            self.spawn_fire()
        
    def spawn_fire(self):
        # Pick a random size choice: L (9 clicks), M (5 clicks)
        size_choice = random.choice(["L", "M"])
        if size_choice == "L":
            hp = 9.0
        else:
            hp = 5.0
            
        # Pick a random location within safe boundaries of 1000x700
        self.fires.append({
            "x": random.randint(100, 900),
            "y": random.randint(100, 600),
            "hp": hp
        })
        
    def update(self):
        current_ticks = pygame.time.get_ticks()
        if self.state == "COUNTDOWN":
            self.elapsed_time = 0
            self.last_update_ticks = current_ticks
            countdown_elapsed = current_ticks - self.start_ticks
            if countdown_elapsed >= 3000:
                self.state = "PLAYING"
                self.play_start_ticks = current_ticks
                self.last_update_ticks = current_ticks
        elif self.state == "PLAYING":
            dt = (current_ticks - self.last_update_ticks) / 1000.0
            self.last_update_ticks = current_ticks
            
            self.elapsed_time = (current_ticks - self.play_start_ticks) / 1000.0
            
            # Check mouse hold down to extinguish fires
            mouse_pressed = pygame.mouse.get_pressed()[0]
            if mouse_pressed:
                mx, my = pygame.mouse.get_pos()
                from main import settings, play_sfx
                vmx = int(mx * 1000 / settings.width)
                vmy = int(my * 700 / settings.height)
                
                hit_any = False
                for f in self.fires[:]:
                    r_hit = 130 if f["hp"] > 5 else (95 if f["hp"] > 3 else 65)
                    if math.hypot(vmx - f["x"], vmy - f["y"]) < r_hit:
                        f["hp"] -= dt * 8.0
                        hit_any = True
                        if f["hp"] <= 0:
                            self.fires.remove(f)
                        break
                        
                if hit_any:
                    self.sfx_timer -= dt
                    if self.sfx_timer <= 0:
                        if self.water_sfx:
                            from main import settings
                            self.water_sfx.set_volume(settings.volume * 0.8)  # 20% volume reduction
                            self.water_sfx.play()
                        else:
                            play_sfx("sfx_click")
                        self.sfx_timer = 0.15
                else:
                    self.sfx_timer = 0.0
            else:
                self.sfx_timer = 0.0
                
            # If player extinguished all spawned fires and at least one has spawned, victory!
            if self.elapsed_time > 0.5 and len(self.fires) == 0 and self.spawned_count > 0:
                self.state = "SUCCESS"
            elif self.elapsed_time >= self.limit_time:
                # Timer ended! Must extinguish all fires to clear, otherwise it's a FAIL.
                if len(self.fires) > 0:
                    self.state = "FAIL"
                    try:
                        from main import play_music_track, GAMEOVER_MUSIC_PATH
                        play_music_track(GAMEOVER_MUSIC_PATH, fade_ms=0, loops=0)
                    except Exception as e:
                        print(f"게임오버 음악 재생 실패: {e}")
                else:
                    self.state = "SUCCESS"
                
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        from main import settings, go_to_minigames, play_sfx, keyboard_sfx
        if self.state not in ["PLAYING", "COUNTDOWN"]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play_sfx("sfx_end")
                    go_to_minigames()
                elif event.key == pygame.K_RETURN:
                    self.reset()
                    if keyboard_sfx:
                        keyboard_sfx.set_volume(settings.volume)
                        keyboard_sfx.play()
                    try:
                        from main import play_music_track, FIRE_MUSIC_PATH
                        play_music_track(FIRE_MUSIC_PATH, fade_ms=0)
                    except Exception as e:
                        print(f"화재진압 음악 재생 실패: {e}")
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                play_sfx("sfx_end")
                go_to_minigames()
                
        pass
                
    def draw(self, surface):
        from visual_effects import draw_terminal_hud
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # Apply same dark warm overlay as the meteor shower game
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((15, 10, 8, 170))  # R, G, B, Alpha (170 = ~66% opacity)
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill((30, 20, 10))
        
        for f in self.fires:
            # Select scaled frames based on current remaining clicks (HP)
            if f["hp"] > 5:
                frames = self.fire_frames_large
                fallback_r = 100
            elif f["hp"] > 3:
                frames = self.fire_frames_medium
                fallback_r = 70
            else:
                frames = self.fire_frames_small
                fallback_r = 40
                
            if frames:
                frame_idx = (pygame.time.get_ticks() // 80) % len(frames)
                fire_surf = frames[frame_idx]
                rect = fire_surf.get_rect(center=(f["x"], f["y"]))
                virtual_surf.blit(fire_surf, rect)
            else:
                pygame.draw.circle(virtual_surf, (220, 60, 40), (f["x"], f["y"]), fallback_r)
        
        # Countdown overlay rendering
        if self.state == "COUNTDOWN":
            elapsed = pygame.time.get_ticks() - self.start_ticks
            num = 3 - (elapsed // 1000)
            num_str = str(num) if num > 0 else "START!"
            
            # Pulse size
            pulse = 1.0 + (elapsed % 1000) / 1000.0 * 0.3
            font_num = pygame.font.SysFont("malgungothic", int(48 * pulse), bold=True)
            
            num_surf = font_num.render(num_str, True, (255, 255, 255))
            num_rect = num_surf.get_rect(center=(500, 350))
            
            box_w, box_h = 300, 120
            box_rect = pygame.Rect(500 - box_w//2, 350 - box_h//2, box_w, box_h)
            pygame.draw.rect(virtual_surf, (15, 8, 3, 220), box_rect)
            pygame.draw.rect(virtual_surf, (235, 130, 40), box_rect, 2)
            
            virtual_surf.blit(num_surf, num_rect)
            
        if self.state in ["SUCCESS", "FAIL"]:
            font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
            font_sub = pygame.font.SysFont("malgungothic", 18)
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((15, 10, 5, 210))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 화재 진압 성공 (SUCCESS) ■", True, (70, 220, 70))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 화재 제어 실패 - 원자로 과열 (FAIL) 🚨", True, (220, 60, 40))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)
        
        # Draw HUD directly on screen surface for perfect resolution and scaling (Matching stage_10_rocket style)
        from main import settings
        
        # 1. Draw game boundaries
        pygame.draw.rect(surface, CRT_GREEN, (15, 45, settings.width - 30, settings.height - 85), 2)
        
        # 2. Draw progress bar
        time_ratio = max(0.0, (self.limit_time - self.elapsed_time) / self.limit_time)
        bar_max_w = settings.width // 2 - 60
        bar_h = 16
        bar_x = 30
        bar_y = 22
        pygame.draw.rect(surface, CRT_GREEN, (bar_x, bar_y, bar_max_w, bar_h), 2)
        fill_w = int(bar_max_w * time_ratio)
        if fill_w > 0:
            bar_color = (100, 255, 100) if time_ratio > 0.5 else ((255, 120, 30) if time_ratio > 0.2 else (255, 60, 40))
            pygame.draw.rect(surface, bar_color, (bar_x + 2, bar_y + 2, fill_w - 4, bar_h - 4))
            
        # 3. Draw HUD energy blocks and text
        font_hud = get_scaled_font(16, is_korean=True)
        fires_text = "FIRES: "
        fires_lbl = font_hud.render(fires_text, True, CRT_GREEN)
        
        # Match layout of stage_10_rocket
        start_x = settings.width - 200
        fires_lbl_x = start_x - fires_lbl.get_width() - 10
        fires_lbl_y = 20
        surface.blit(fires_lbl, (fires_lbl_x, fires_lbl_y))
        
        for i in range(6):
            bx = start_x + i * 22
            by = 22
            block_color = (255, 120, 30) if i < len(self.fires) else (40, 20, 10)
            pygame.draw.rect(surface, block_color, (bx, by, 16, 12))
            pygame.draw.rect(surface, CRT_GREEN, (bx, by, 16, 12), 1)

if __name__ == "__main__":
    import sys
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = FireGame()
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