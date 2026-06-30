import pygame
import random
import math
import os

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
            surf_conv = surf.convert()
            surf_conv.set_colorkey((0, 0, 0))
            frames.append(surf_conv)
    except Exception as e:
        print(f"GIF 프레임 로드 실패: {e}")
    return frames

class MeteorGame:
    def __init__(self):
        self.bg_img = None
        self.meteor_frames = []
        self.rocket_img = None
        self.load_assets()
        self.reset()
        
    def load_assets(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            self.bg_img = pygame.image.load(os.path.join(base_dir, "assets", "meteor_view.png")).convert()
        except Exception as e:
            print(f"배경 이미지를 로드할 수 없습니다: {e}")
            
        self.meteor_frames = load_gif_frames(os.path.join(base_dir, "assets", "meteor2.gif"))
            
        try:
            self.rocket_img = pygame.image.load(os.path.join(base_dir, "assets", "rocket.png")).convert()
            self.rocket_img.set_colorkey((0, 0, 0))
        except Exception as e:
            print(f"로켓 이미지를 로드할 수 없습니다: {e}")

    def reset(self):
        from main import settings
        self.player_x = settings.width // 2
        self.player_y = settings.height - 120
        self.player_size = 48  # 2배 증가 (24 -> 48)
        self.hp = 3
        self.max_hp = 3
        self.invincible_timer = 0
        self.meteors = []
        self.particles = []
        self.state = "COUNTDOWN"  # "COUNTDOWN", "PLAYING", "WON", "LOST"
        self.start_ticks = pygame.time.get_ticks()
        self.play_start_ticks = 0
        self.elapsed_time = 0
        self.game_duration = 30000  # 30초 플레이 타임
        self.shake_intensity = 0
        
        # Initialize vertical speed lines for warp speed sensation
        import random
        self.speed_lines = []
        for _ in range(40):
            self.speed_lines.append({
                "x": random.randint(10, settings.width - 10),
                "y": random.randint(-settings.height, settings.height),
                "length": random.randint(40, 110),
                "speed": random.uniform(15.0, 32.0),
                "alpha": random.randint(50, 150)
            })
        
    def handle_event(self, event):
        return False
        
    def update(self):
        from main import settings, progress, click_sfx
        current_ticks = pygame.time.get_ticks()
        
        # Screen shake dampening
        if self.shake_intensity > 0:
            self.shake_intensity -= 1
            
        if self.state == "COUNTDOWN":
            self.elapsed_time = 0
            countdown_elapsed = current_ticks - self.start_ticks
            if countdown_elapsed >= 3000:  # 3 seconds countdown
                self.state = "PLAYING"
                self.play_start_ticks = current_ticks
                self.meteors = []
        elif self.state == "PLAYING":
            self.elapsed_time = current_ticks - self.play_start_ticks
            if self.elapsed_time >= self.game_duration:
                self.state = "WON"
                progress.unlock_achievement("meteor_survivor")
                
            # Invincibility frame countdown
            if self.invincible_timer > 0:
                self.invincible_timer -= 1
                
            # Spawn meteors - spawn rate increases over time (밸런스 재조정)
            spawn_chance = 0.06 + (self.elapsed_time / self.game_duration) * 0.07
            if random.random() < spawn_chance:
                # 난이도 완화 (동시 생성 개수 축소: 초중반 무조건 1개, 극후반 70% 이후 가끔 2개)
                num_spawn = 1
                if (self.elapsed_time / self.game_duration) >= 0.7:
                    num_spawn = 2 if random.random() < 0.3 else 1
                    
                for _ in range(num_spawn):
                    # 거대 운석의 빈도를 낮추고 소형 운석의 비율을 늘림 (지수 스케일링: 최솟값 1.5배 증가 24, 최댓값 1.2배 감소 80)
                    size = int(24 + (random.random() ** 1.8) * 56)
                    m_x = random.randint(30, settings.width - 30)
                    m_y = -size
                    
                    # [크기-속도 연동 물리 법칙] 큰 운석은 느리고 묵직하게 길목을 막고, 작은 운석은 빠르게 떨어짐!
                    if size >= 58:
                        base_speed_y = random.uniform(2.2, 3.8)
                        speed_x = random.uniform(-0.8, 0.8)  # 거대 운석은 거의 직선 낙하
                    elif size >= 38:
                        base_speed_y = random.uniform(3.8, 5.8)
                        speed_x = random.uniform(-1.8, 1.8)
                    else:
                        base_speed_y = random.uniform(5.8, 8.8)
                        speed_x = random.uniform(-2.8, 2.8)  # 초소형 운석은 날렵하게 꺾임
                        
                    # 시간 경과에 따른 가속
                    speed_y = base_speed_y + (self.elapsed_time / self.game_duration) * 2.0
                    self.meteors.append({
                        "x": m_x,
                        "y": m_y,
                        "size": size,
                        "speed_x": speed_x,
                        "speed_y": speed_y,
                        "frame_offset": random.randint(0, 1000)
                    })
                
            # Update meteors
            for m in self.meteors[:]:
                m["x"] += m["speed_x"]
                m["y"] += m["speed_y"]
                
                # Check collision with player
                dist = math.hypot(m["x"] - self.player_x, m["y"] - self.player_y)
                if dist < (m["size"] * 0.85 + self.player_size * 0.75):
                    if self.invincible_timer == 0:
                        self.hp -= 1
                        self.invincible_timer = 60  # 1 second invincibility
                        self.shake_intensity = 15
                        # Create explosion particles
                        for _ in range(15):
                            self.particles.append({
                                "x": self.player_x,
                                "y": self.player_y,
                                "vx": random.uniform(-4, 4),
                                "vy": random.uniform(-4, 4),
                                "life": random.randint(15, 30),
                                "color": (255, 120, 30)
                            })
                        if click_sfx:
                            click_sfx.set_volume(settings.volume)
                            click_sfx.play()
                        if self.hp <= 0:
                            self.state = "LOST"
                    # Remove the hit meteor
                    self.meteors.remove(m)
                    continue
                    
                # Remove if off-screen
                if m["y"] > settings.height + 50 or m["x"] < -50 or m["x"] > settings.width + 50:
                    self.meteors.remove(m)
                    
        # Update particles
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0:
                self.particles.remove(p)
                
        # Update vertical speed lines (only when not paused/active)
        if self.state in ["PLAYING", "COUNTDOWN"]:
            import random
            for line in self.speed_lines:
                line["y"] += line["speed"]
                if line["y"] > settings.height:
                    line["x"] = random.randint(10, settings.width - 10)
                    line["y"] = random.randint(-150, -50)
                    line["length"] = random.randint(40, 110)
                    line["speed"] = random.uniform(15.0, 32.0)
                    line["alpha"] = random.randint(50, 150)

    def handle_input(self):
        from main import settings
        if self.state != "PLAYING":
            return
            
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            
        # Normalize diagonal speed
        if dx != 0 and dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            
        speed = 6.0
        self.player_x += dx * speed
        self.player_y += dy * speed
        
        # Constrain to screen boundaries
        self.player_x = max(20 + self.player_size, min(settings.width - 20 - self.player_size, self.player_x))
        self.player_y = max(50 + self.player_size, min(settings.height - 50 - self.player_size, self.player_y))

    def draw(self, surface):
        from main import settings, CRT_GREEN, CRT_BRIGHT, get_scaled_font
        
        # Shake offset
        ox, oy = 0, 0
        if self.shake_intensity > 0:
            ox = random.randint(-self.shake_intensity, self.shake_intensity)
            oy = random.randint(-self.shake_intensity, self.shake_intensity)
            
        # Draw background image
        if self.bg_img:
            if not hasattr(self, '_scaled_bg') or self._scaled_bg.get_size() != (settings.width, settings.height):
                self._scaled_bg = pygame.transform.scale(self.bg_img, (settings.width, settings.height))
            surface.blit(self._scaled_bg, (ox, oy))
            
            # Apply dark warm overlay to dim contrast and lower saturation for better readability
            dim_overlay = pygame.Surface((settings.width, settings.height), pygame.SRCALPHA)
            dim_overlay.fill((15, 10, 8, 170))  # R, G, B, Alpha (170 = ~66% opacity)
            surface.blit(dim_overlay, (0, 0))
        else:
            # Fallback dark backdrop
            overlay = pygame.Surface((settings.width, settings.height), pygame.SRCALPHA)
            overlay.fill((12, 6, 3, 230))
            surface.blit(overlay, (0, 0))
            
            # Draw retro grid
            grid_w = 40
            for x in range(0, settings.width, grid_w):
                pygame.draw.line(surface, (40, 20, 10), (x + ox, 0), (x + ox, settings.height), 1)
            for y in range(0, settings.height, grid_w):
                pygame.draw.line(surface, (40, 20, 10), (ox, y + oy), (settings.width + ox, y + oy), 1)
                
        # Draw vertical speed lines for hyper-speed immersion
        for line in self.speed_lines:
            factor = line["alpha"] / 255.0
            # Warm amber/light orange speed lines to match the CRT theme
            color = (int(255 * factor), int(160 * factor), int(60 * factor))
            pygame.draw.line(surface, color, (line["x"] + ox, int(line["y"] + oy)), (line["x"] + ox, int(line["y"] + oy + line["length"])), 1)
            
        # Draw Meteors
        for m in self.meteors:
            mx, my = int(m["x"] + ox), int(m["y"] + oy)
            r = m["size"]
            if self.meteor_frames:
                frame_idx = ((pygame.time.get_ticks() + m.get("frame_offset", 0)) // 60) % len(self.meteor_frames)
                img = self.meteor_frames[frame_idx]
                diameter = r * 2
                scaled_meteor = pygame.transform.scale(img, (diameter, diameter))
                
                # Calculate diagonal fall angle from speed_x and speed_y
                angle_deg = math.degrees(math.atan2(m["speed_x"], m["speed_y"]))
                
                # Rotate the meteor image around its center
                rotated_meteor = pygame.transform.rotate(scaled_meteor, angle_deg)
                rect = rotated_meteor.get_rect(center=(mx, my))
                
                surface.blit(rotated_meteor, rect)
            else:
                pygame.draw.circle(surface, (140, 70, 30), (mx, my), r)
                pygame.draw.circle(surface, CRT_BRIGHT, (mx, my), r, 2)
                # Crater details
                pygame.draw.line(surface, CRT_BRIGHT, (mx - r//2, my - r//3), (mx - r//4, my - r//4), 2)
                pygame.draw.line(surface, CRT_BRIGHT, (mx + r//3, my + r//4), (mx + r//2, my + r//5), 2)
            
        # Draw Particles
        for p in self.particles:
            px, py = int(p["x"] + ox), int(p["y"] + oy)
            pygame.draw.rect(surface, p["color"], (px, py, 4, 4))
            
        # Draw Player Ship
        if self.invincible_timer == 0 or (self.invincible_timer // 4) % 2 == 0:
            px, py = int(self.player_x + ox), int(self.player_y + oy)
            
            # Jet flame animation (scaled 1.5x to match 1.5x rocket)
            if self.state == "PLAYING" and pygame.time.get_ticks() % 100 < 50:
                flame = [
                    (px - 18, py + 30),
                    (px, py + 72),
                    (px + 18, py + 30)
                ]
                pygame.draw.polygon(surface, (255, 120, 30), flame)
                
            if self.rocket_img:
                rw = int(self.player_size * 2.4)
                rh = int(self.player_size * 2.4)
                scaled_rocket = pygame.transform.scale(self.rocket_img, (rw, rh))
                rect = scaled_rocket.get_rect(center=(px, py))
                surface.blit(scaled_rocket, rect)
            else:
                points = [
                    (px, py - 44),       # 로켓 상단 팁 (2배 확대)
                    (px - 36, py + 32),  # 좌측 하단 날개
                    (px - 16, py + 16),  # 좌측 안쪽 인덴트
                    (px + 16, py + 16),  # 우측 안쪽 인덴트
                    (px + 36, py + 32)   # 우측 하단 날개
                ]
                pygame.draw.polygon(surface, (100, 255, 100), points)
                pygame.draw.polygon(surface, CRT_GREEN, points, 2)
                
        # Draw HUD elements
        font_hud = get_scaled_font(16, is_korean=True)
        
        # [요구사항 1] Time remaining progress bar
        time_ratio = max(0.0, (self.game_duration - self.elapsed_time) / self.game_duration)
        bar_max_w = settings.width // 2 - 60 # 프로그레스 바 최대 너비
        bar_h = 16
        bar_x = 30
        bar_y = 22

        # 프로그레스 바 테두리
        pygame.draw.rect(surface, CRT_GREEN, (bar_x, bar_y, bar_max_w, bar_h), 2)
        # 프로그레스 바 내부 채우기
        fill_w = int(bar_max_w * time_ratio)
        if fill_w > 0:
            # 남은 시간에 따라 색상 변경 (녹색 -> 주황색 -> 적색)
            bar_color = CRT_BRIGHT if time_ratio > 0.5 else ((255, 120, 30) if time_ratio > 0.2 else (255, 60, 40))
            pygame.draw.rect(surface, bar_color, (bar_x + 2, bar_y + 2, fill_w - 4, bar_h - 4))

        # Shield health bar
        shield_text = "SHIELDS: "
        shield_lbl = font_hud.render(shield_text, True, CRT_GREEN)
        surface.blit(shield_lbl, (settings.width - 240, 20))
        
        # Draw shield energy blocks
        for hp_i in range(self.max_hp):
            bx = settings.width - 140 + hp_i * 22
            by = 22
            color = (100, 255, 100) if hp_i < self.hp else (40, 20, 10)
            pygame.draw.rect(surface, color, (bx, by, 16, 12))
            pygame.draw.rect(surface, CRT_GREEN, (bx, by, 16, 12), 1)
            
        # Draw game boundaries
        pygame.draw.rect(surface, CRT_GREEN, (15 + ox, 45 + oy, settings.width - 30, settings.height - 85), 2)
            
        # Countdown overlay rendering
        if self.state == "COUNTDOWN":
            font_title = get_scaled_font(36, is_korean=True)
            elapsed = pygame.time.get_ticks() - self.start_ticks
            num = 3 - (elapsed // 1000)
            num_str = str(num) if num > 0 else "START!"
            
            # Pulse size
            pulse = 1.0 + (elapsed % 1000) / 1000.0 * 0.3
            font_num = get_scaled_font(int(48 * pulse), is_korean=True)
            
            num_surf = font_num.render(num_str, True, CRT_BRIGHT)
            num_rect = num_surf.get_rect(center=(settings.width // 2, settings.height // 2))
            
            box_w, box_h = 300, 120
            box_rect = pygame.Rect(settings.width//2 - box_w//2, settings.height//2 - box_h//2, box_w, box_h)
            pygame.draw.rect(surface, (15, 8, 3, 220), box_rect)
            pygame.draw.rect(surface, CRT_GREEN, box_rect, 2)
            
            surface.blit(num_surf, num_rect)
            
        # End results overlay rendering
        elif self.state in ["WON", "LOST"]:
            font_end = get_scaled_font(28, is_korean=True)
            font_sub = get_scaled_font(15, is_korean=True)
            
            msg = "MISSION SUCCESS" if self.state == "WON" else "SHIELD COLLAPSE - GAME OVER"
            color = (100, 255, 100) if self.state == "WON" else (255, 60, 40)
            
            msg_surf = font_end.render(msg, True, color)
            msg_rect = msg_surf.get_rect(center=(settings.width // 2, settings.height // 2 - 30))
            
            sub_text = "[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]"
            sub_surf = font_sub.render(sub_text, True, (255, 255, 255))
            sub_rect = sub_surf.get_rect(center=(settings.width // 2, settings.height // 2 + 30))
            
            box_w = int(settings.width * 0.6)
            box_h = 160
            box_rect = pygame.Rect(settings.width//2 - box_w//2, settings.height//2 - box_h//2, box_w, box_h)
            
            pygame.draw.rect(surface, (15, 8, 3, 240), box_rect)
            pygame.draw.rect(surface, color, box_rect, 2)
            pygame.draw.rect(surface, color, (box_rect.x + 4, box_rect.y + 4, box_rect.width - 8, box_rect.height - 8), 1)
            
            surface.blit(msg_surf, msg_rect)
            surface.blit(sub_surf, sub_rect)
