import pygame
import random
import sys
import os
import math

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

def load_and_scale_gif(filepath, size):
    raw_frames = load_gif_frames(filepath)
    scaled_frames = []
    for f in raw_frames:
        scaled_frames.append(pygame.transform.scale(f, size))
    if not scaled_frames:
        fallback = pygame.Surface(size, pygame.SRCALPHA)
        fallback.fill((60, 120, 220)) # fallback to BLUE
        scaled_frames.append(fallback)
    return scaled_frames

class ResourcesGame:
    def __init__(self):
        # Cache for optimized text rendering
        self.text_cache = {}
        self.SPRITE_SIZE = 144
        self.HITBOX_SIZE = 12
        
        # Load player animations
        self.player_anims = {
            "up": load_and_scale_gif(os.path.join("assets", "up.gif"), (self.SPRITE_SIZE, self.SPRITE_SIZE)),
            "down": load_and_scale_gif(os.path.join("assets", "down.gif"), (self.SPRITE_SIZE, self.SPRITE_SIZE)),
            "left": load_and_scale_gif(os.path.join("assets", "left.gif"), (self.SPRITE_SIZE, self.SPRITE_SIZE)),
            "right": load_and_scale_gif(os.path.join("assets", "right.gif"), (self.SPRITE_SIZE, self.SPRITE_SIZE)),
            "stop": load_and_scale_gif(os.path.join("assets", "stop.gif"), (self.SPRITE_SIZE, self.SPRITE_SIZE)),
        }
        
        # Load sounds
        self.running_sound = None
        self.clear_sfx = None
        try:
            self.running_sound = pygame.mixer.Sound(os.path.join("assets", "runnnn.MP3"))
        except Exception as e:
            print(f"runnnn.MP3 로드 실패: {e}")
            
        try:
            self.clear_sfx = pygame.mixer.Sound(os.path.join("assets", "clearsoundd.MP3"))
        except Exception as e:
            print(f"clearsoundd.MP3 로드 실패: {e}")
            
        try:
            self.change_sfx = pygame.mixer.Sound(os.path.join("assets", "change.MP3"))
        except Exception as e:
            print(f"change.MP3 로드 실패: {e}")
            
        self.is_playing_run_sfx = False
        
        self.reset()
        
    def reset(self):
        # Game state parameters from 2.py
        self.state = "INTRO"
        
        # Colors from 2.py
        self.BLACK = (10, 5, 5)
        self.DARK_BG = (30, 20, 15)
        self.WHITE = (255, 240, 220)
        self.GRAY = (120, 100, 80)
        self.GREEN = (70, 220, 70)
        self.RED = (220, 60, 40)
        self.BLUE = (60, 120, 220)
        self.ORANGE = (235, 130, 40)
        
        self.COLOR_ROAD = (50, 55, 65)          
        self.COLOR_SIDEWALK = (95, 100, 110)    
        self.COLOR_BUILDING = (125, 135, 150)   
        self.COLOR_SHADOW = (35, 38, 45)        
        self.COLOR_LINE = (195, 200, 205)
        
        # Game data from 2.py
        self.crew_base = ["의사", "기술자", "경찰", "천문학자"]
        self.crew_farmable = ["정치인", "생명 유지장치 기술자", "개발자", "전기 기술자"]
        self.resources = {"산소": 80, "전기": 80, "정신력": 80}
        self.my_crew = list(self.crew_base)
        self.dead_count = 0
        
        self.MAP_WIDTH, self.MAP_HEIGHT = 2600, 2000  
        self.HITBOX_SIZE = 12
        self.SPRITE_SIZE = 144
        self.player_rect = pygame.Rect(self.MAP_WIDTH//2, self.MAP_HEIGHT//2, self.HITBOX_SIZE, self.HITBOX_SIZE)
        
        self.items = []
        self.obstacles = []       
        self.city_blocks = []     
        self.crosswalks = []      
        self.farm_start_time = pygame.time.get_ticks()
        self.is_cleared = False
        
        # Player movement and animation states
        self.current_direction = "stop"
        self.anim_index = 0
        self.anim_timer = pygame.time.get_ticks()
        self.stop_run_sound()
        
        # Initialize map elements
        self.init_farming()
        
        # Clear text cache
        self.text_cache.clear()

    def stop_run_sound(self):
        if hasattr(self, 'running_sound') and self.running_sound:
            self.running_sound.stop()
        self.is_playing_run_sfx = False

    def update_run_sound(self):
        if hasattr(self, 'running_sound') and self.running_sound:
            from main import settings
            self.running_sound.set_volume(settings.volume)
            should_play = (self.state == "PLAYING" and not self.is_cleared and self.current_direction != "stop")
            if should_play:
                if not self.is_playing_run_sfx:
                    self.running_sound.play(loops=-1)
                    self.is_playing_run_sfx = True
            else:
                if self.is_playing_run_sfx:
                    self.running_sound.stop()
                    self.is_playing_run_sfx = False

    def play_clearsoundd_sfx(self):
        if self.clear_sfx:
            from main import settings
            # 해당 게임 내에서만 볼륨을 2.0배 증폭 (최대 1.0)
            vol = min(1.0, settings.volume * 2.0)
            self.clear_sfx.set_volume(vol)
            self.clear_sfx.play()

    def play_change_sfx(self):
        if self.change_sfx:
            from main import settings
            # 해당 게임 내에서만 볼륨을 지금보다 2배 더 증폭 (최대 1.0, 4.0배)
            vol = min(1.0, settings.volume * 4.0)
            self.change_sfx.set_volume(vol)
            self.change_sfx.play()
        
    def generate_planned_city(self):
        self.obstacles.clear()
        self.city_blocks.clear()
        self.crosswalks.clear()
        block_definitions = [
            pygame.Rect(100, 100, 600, 450), pygame.Rect(950, 100, 700, 450), pygame.Rect(1900, 100, 600, 450),
            pygame.Rect(100, 750, 600, 500), pygame.Rect(950, 750, 700, 500), pygame.Rect(1900, 750, 600, 500),
            pygame.Rect(100, 1450, 600, 450), pygame.Rect(950, 1450, 700, 450), pygame.Rect(1900, 1450, 600, 450)
        ]
        player_spawn_zone = pygame.Rect(self.MAP_WIDTH//2 - 120, self.MAP_HEIGHT//2 - 120, 240, 240)
        
        for block in block_definitions:
            self.city_blocks.append(block)
            self.crosswalks.append(pygame.Rect(block.right, block.top + 60, 250, 50))
            self.crosswalks.append(pygame.Rect(block.left + 60, block.bottom, 50, 200))
            
            # Divide each city block into a neat grid of columns and rows
            cols = 3 if block.width >= 700 else 2
            rows = 2
            
            border_padding = 50
            inner_w = block.width - (border_padding * 2)
            inner_h = block.height - (border_padding * 2)
            
            slot_w = inner_w / cols
            slot_h = inner_h / rows
            
            # Gaps of 55px to ensure player (size 36) can easily walk through
            gap = 55
            building_w = int(slot_w - gap)
            building_h = int(slot_h - gap)
            
            for r in range(rows):
                for c in range(cols):
                    # Center the building within its grid slot
                    bx = int(block.left + border_padding + c * slot_w + (slot_w - building_w) / 2)
                    by = int(block.top + border_padding + r * slot_h + (slot_h - building_h) / 2)
                    
                    new_building = pygame.Rect(bx, by, building_w, building_h)
                    
                    # Prevent spawning on player
                    if new_building.colliderect(player_spawn_zone):
                        continue
                        
                    self.obstacles.append(new_building)
                        
    def init_farming(self):
        self.items.clear()
        self.generate_planned_city()
        self.player_rect.center = (self.MAP_WIDTH//2, self.MAP_HEIGHT//2)
        
        # Player spawn buffer zone to avoid spawning items on top of player
        player_buffer = self.player_rect.inflate(80, 80)
        
        for c in self.crew_farmable:
            placed = False
            while not placed:
                rx = random.randint(80, self.MAP_WIDTH - 80)
                ry = random.randint(80, self.MAP_HEIGHT - 80)
                temp_rect = pygame.Rect(rx, ry, 28, 28)
                # Check collision against obstacles, minimum distance of 100px from other items, and player spawn buffer
                if (not any(temp_rect.colliderect(b.inflate(10, 10)) for b in self.obstacles) and
                    not any(math.hypot(temp_rect.centerx - item["rect"].centerx, temp_rect.centery - item["rect"].centery) < 100 for item in self.items) and
                    not temp_rect.colliderect(player_buffer)):
                    self.items.append({"rect": temp_rect, "type": "crew", "name": c})
                    placed = True
                    
        # 주황색 자원 72개 배치 (초기 80/200에서 5점씩 72개를 모아야 세 자원 모두 200 충족)
        for _ in range(72):
            placed = False
            while not placed:
                rx = random.randint(80, self.MAP_WIDTH - 80)
                ry = random.randint(80, self.MAP_HEIGHT - 80)
                temp_rect = pygame.Rect(rx, ry, 20, 20)
                if (not any(temp_rect.colliderect(b.inflate(8, 8)) for b in self.obstacles) and
                    not any(math.hypot(temp_rect.centerx - item["rect"].centerx, temp_rect.centery - item["rect"].centery) < 100 for item in self.items) and
                    not temp_rect.colliderect(player_buffer)):
                    self.items.append({"rect": temp_rect, "type": "resource", "name": "resource"})
                    placed = True
                    
        self.farm_start_time = pygame.time.get_ticks()
        
    def handle_event(self, event):
        from main import go_to_minigames, play_sfx, settings
        if self.state == "INTRO":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                w, h = settings.width, settings.height
                dialog_w, dialog_h = 750, 400
                dialog_rect = pygame.Rect((w - dialog_w)//2, (h - dialog_h)//2, dialog_w, dialog_h)
                btn_w, btn_h = 320, 50
                btn_rect = pygame.Rect((w - btn_w)//2, dialog_rect.bottom - 75, btn_w, btn_h)
                if btn_rect.collidepoint(event.pos):
                    self.state = "PLAYING"
                    self.farm_start_time = pygame.time.get_ticks()
                    play_sfx("sfx_click")
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.state = "PLAYING"
                    self.farm_start_time = pygame.time.get_ticks()
                    play_sfx("sfx_click")
                elif event.key == pygame.K_ESCAPE:
                    self.stop_run_sound()
                    go_to_minigames()
                    play_sfx("sfx_end")
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.stop_run_sound()
                    go_to_minigames()
                    play_sfx("sfx_end")
                elif event.key == pygame.K_RETURN and self.is_clear_finished():
                    self.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.is_cleared:
                    w, h = settings.width, settings.height
                    dialog_w, dialog_h = 750, 420
                    dialog_rect = pygame.Rect((w - dialog_w)//2, (h - dialog_h)//2, dialog_w, dialog_h)
                    btn_w, btn_h = 320, 50
                    btn_rect = pygame.Rect((w - btn_w)//2, dialog_rect.bottom - 75, btn_w, btn_h)
                    if btn_rect.collidepoint(event.pos):
                        self.stop_run_sound()
                        go_to_minigames()
                        play_sfx("sfx_end")
                    
    def is_clear_finished(self):
        return self.is_cleared
        
    def handle_input(self):
        if self.state != "PLAYING" or self.is_cleared:
            return
            
        keys = pygame.key.get_pressed()
        speed = 5.8  # 난이도 조절: 최대한 열심히 움직여도 주황색 자원들을 평균 130정도까지 모을 수 있도록 속도 조절
        dx, dy = 0, 0
        
        # 대각선 이동 방지: 한 번에 한 축으로만 이동 가능하도록 설정
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -speed
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = speed
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -speed
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = speed
        
        self.player_rect.x += dx
        for b in self.obstacles:
            if self.player_rect.colliderect(b):
                if dx > 0:
                    self.player_rect.right = b.left
                elif dx < 0:
                    self.player_rect.left = b.right
                else:
                    # Resolve static overlap (e.g. from vertical correction)
                    if self.player_rect.centerx < b.centerx:
                        self.player_rect.right = b.left
                    else:
                        self.player_rect.left = b.right
                
        self.player_rect.y += dy
        for b in self.obstacles:
            if self.player_rect.colliderect(b):
                if dy > 0:
                    self.player_rect.bottom = b.top
                elif dy < 0:
                    self.player_rect.top = b.bottom
                else:
                    # Resolve static overlap (e.g. from horizontal correction)
                    if self.player_rect.centery < b.centery:
                        self.player_rect.bottom = b.top
                    else:
                        self.player_rect.top = b.bottom
                
        self.player_rect.clamp_ip(pygame.Rect(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT))
        
        # Determine movement direction for GIF animation
        new_dir = "stop"
        if dx < 0:
            new_dir = "left"
        elif dx > 0:
            new_dir = "right"
        elif dy < 0:
            new_dir = "up"
        elif dy > 0:
            new_dir = "down"
            
        if new_dir != self.current_direction:
            self.current_direction = new_dir
            self.anim_index = 0
            self.anim_timer = pygame.time.get_ticks()
        
    def update(self):
        if self.state == "PLAYING" and not self.is_cleared:
            # Update animation frame
            now = pygame.time.get_ticks()
            if now - self.anim_timer > 100:  # 100ms per frame
                self.anim_timer = now
                frames = self.player_anims[self.current_direction]
                self.anim_index = (self.anim_index + 1) % len(frames)
                
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.farm_start_time) / 1000
            remain = 30 - elapsed
            if remain <= 0:
                self.is_cleared = True
                
            for item in self.items[:]:
                # 컬렉션 판정 버퍼를 키워 자원을 더 쉽게 먹을 수 있도록 설정 (자원 60px, 크루 45px 확장 - 1.5배 증가)
                inflate_val = 60 if item["type"] == "resource" else 45
                if self.player_rect.colliderect(item["rect"].inflate(inflate_val, inflate_val)):
                    from main import play_sfx
                    if item["type"] == "crew" and len(self.my_crew) < 8:
                        self.my_crew.append(item["name"])
                        self.play_clearsoundd_sfx()
                    elif item["type"] == "resource":
                        # 산소, 전기, 정신력 중 200 미만인 자원을 무작위로 선택해 5점 증가 (초기자원 80/200, 자원당 5씩 수집)
                        available_res = [r for r in ["산소", "전기", "정신력"] if self.resources[r] < 200]
                        if not available_res:
                            available_res = ["산소", "전기", "정신력"]
                        chosen_res = random.choice(available_res)
                        self.resources[chosen_res] = min(200, self.resources[chosen_res] + 5)
                        self.play_change_sfx()
                    self.items.remove(item)
        self.update_run_sound()
                    
    def get_cached_text(self, text, font, color):
        cache_key = (text, id(font), color)
        if cache_key not in self.text_cache:
            self.text_cache[cache_key] = font.render(text, True, color)
        return self.text_cache[cache_key]
        
    def draw_text(self, surface, text, font, color, x, y, center=False):
        # Draw a small shadow for readability
        shadow_color = (0, 0, 0)
        img_shadow = self.get_cached_text(text, font, shadow_color)
        rect_shadow = img_shadow.get_rect()
        if center: 
            rect_shadow.center = (x + 1, y + 1)
        else: 
            rect_shadow.topleft = (x + 1, y + 1)
        surface.blit(img_shadow, rect_shadow)
        
        img = self.get_cached_text(text, font, color)
        rect = img.get_rect()
        if center: 
            rect.center = (x, y)
        else: 
            rect.topleft = (x, y)
        surface.blit(img, rect)
        
    def draw(self, surface):
        from main import settings, get_scaled_font, CRT_GREEN
        
        w, h = settings.width, settings.height
        
        camera_x = max(0, min(self.player_rect.centerx - w // 2, self.MAP_WIDTH - w))
        camera_y = max(0, min(self.player_rect.centery - h // 2, self.MAP_HEIGHT - h))
        viewport = pygame.Rect(camera_x, camera_y, w, h)
        
        map_surf = pygame.Surface((w, h))
        map_surf.fill(self.COLOR_ROAD)
        
        # Sidewalk blocks - culled
        for block in self.city_blocks:
            if block.colliderect(viewport):
                map_surf.fill(self.COLOR_SIDEWALK, block.move(-camera_x, -camera_y))
                
        # Crosswalk lines - culled
        for cw in self.crosswalks:
            if cw.right > self.MAP_WIDTH or cw.bottom > self.MAP_HEIGHT: 
                continue
            if cw.colliderect(viewport):
                screen_cw = cw.move(-camera_x, -camera_y)
                if cw.width > cw.height:
                    for lx in range(screen_cw.left, screen_cw.right, 35):
                        pygame.draw.rect(map_surf, self.COLOR_LINE, (lx, screen_cw.top, 15, screen_cw.height))
                else:
                    for ly in range(screen_cw.top, screen_cw.bottom, 35):
                        pygame.draw.rect(map_surf, self.COLOR_LINE, (screen_cw.left, ly, screen_cw.width, 15))
                        
        # Obstacles / Buildings - culled
        for b in self.obstacles:
            bound_rect = pygame.Rect(b.x, b.y, b.width, b.height + 10)
            if bound_rect.colliderect(viewport):
                screen_b = b.move(-camera_x, -camera_y)
                pygame.draw.rect(map_surf, self.COLOR_SHADOW, (screen_b.x, screen_b.y, screen_b.width, screen_b.height + 10))
                pygame.draw.rect(map_surf, self.COLOR_BUILDING, screen_b)
                
        # Items - culled
        for item in self.items:
            if item["rect"].colliderect(viewport):
                is_green_item = (item["type"] == "crew")
                color = self.GREEN if is_green_item else self.ORANGE
                pygame.draw.rect(map_surf, color, item["rect"].move(-camera_x, -camera_y))
                
                # Draw floating green arrow for on-screen green items
                if is_green_item:
                    bob = math.sin(pygame.time.get_ticks() * 0.012) * 4
                    screen_rect = item["rect"].move(-camera_x, -camera_y)
                    tx = screen_rect.centerx
                    ty = screen_rect.top - 8 + bob
                    # Arrow head pointing down
                    pygame.draw.polygon(map_surf, self.GREEN, [
                        (tx, ty),
                        (tx - 6, ty - 8),
                        (tx + 6, ty - 8)
                    ])
                    # Arrow shaft
                    pygame.draw.rect(map_surf, self.GREEN, (tx - 2, ty - 14, 4, 6))
                
        # Player (animated GIF centered over hitbox)
        frames = self.player_anims[self.current_direction]
        idx = self.anim_index % len(frames)
        current_frame = frames[idx]
        offset_x = (self.HITBOX_SIZE - self.SPRITE_SIZE) // 2
        offset_y = (self.HITBOX_SIZE - self.SPRITE_SIZE) // 2
        sprite_rect = self.player_rect.move(offset_x - camera_x, offset_y - camera_y)
        map_surf.blit(current_frame, sprite_rect)
        
        surface.blit(map_surf, (0, 0))
        
        # Draw off-screen green indicators pointing to off-screen green items
        px, py = self.player_rect.center
        offscreen_greens = []
        for item in self.items:
            is_green_item = (item["type"] == "crew")
            if is_green_item and not item["rect"].colliderect(viewport):
                ix, iy = item["rect"].center
                dist = math.hypot(ix - px, iy - py)
                offscreen_greens.append((dist, ix, iy))
                
        # Draw indicators for the nearest 5 off-screen green items
        offscreen_greens.sort(key=lambda x: x[0])
        for dist, ix, iy in offscreen_greens[:5]:
            dx = ix - px
            dy = iy - py
            angle = math.atan2(dy, dx)
            
            cx, cy = w / 2, h / 2
            margin = 35
            dist_x = cx - margin
            dist_y = cy - margin
            
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            if abs(cos_a) * dist_y > abs(sin_a) * dist_x:
                scale = dist_x / abs(cos_a)
            else:
                scale = dist_y / abs(sin_a)
                
            edge_x = cx + cos_a * scale
            edge_y = cy + sin_a * scale
            
            tip = (edge_x, edge_y)
            back_x = edge_x - cos_a * 12
            back_y = edge_y - sin_a * 12
            left = (back_x + sin_a * 6, back_y - cos_a * 6)
            right = (back_x - sin_a * 6, back_y + cos_a * 6)
            
            pygame.draw.polygon(surface, self.GREEN, [tip, left, right])
            # Draw shaft for the arrow pointing to offscreen items
            shaft_end_x = back_x - cos_a * 8
            shaft_end_y = back_y - sin_a * 8
            pygame.draw.line(surface, self.GREEN, (back_x, back_y), (shaft_end_x, shaft_end_y), 4)
            
        # HUD / Text Drawing (with scaling fonts)
        font_main = get_scaled_font(22, is_korean=True)
        font_small = get_scaled_font(16, is_korean=True)
        
        if self.state == "INTRO":
            remain = 30.0
        else:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.farm_start_time) / 1000
            remain = max(0.0, 30 - elapsed)
        
        # Removed HUD top banner background and line per user request
        pass
        
        if not self.is_cleared:
            self.draw_text(surface, "남은 시간:", font_main, self.ORANGE, 20, 20)
            
            # 시간 프로그레스 바 그리기 (길이를 550으로 확장)
            time_ratio = max(0.0, remain / 30.0)
            bar_max_w = 550
            bar_h = 18
            bar_x = 145
            bar_y = 25
            
            # 프로그레스 바 테두리
            pygame.draw.rect(surface, self.ORANGE, (bar_x, bar_y, bar_max_w, bar_h), 2)
            # 프로그레스 바 내부 채우기
            fill_w = int(bar_max_w * time_ratio)
            if fill_w > 0:
                # 남은 시간에 따라 색상 변경 (녹색 -> 주황색 -> 적색)
                bar_color = self.GREEN if time_ratio > 0.5 else (self.ORANGE if time_ratio > 0.2 else self.RED)
                pygame.draw.rect(surface, bar_color, (bar_x + 2, bar_y + 2, fill_w - 4, bar_h - 4))
        else:
            self.draw_text(surface, "★ 파밍 종료 (CLEAR) ★ - 다음 프로젝트 씬 연동 대기 중", font_main, self.GREEN, 20, 20)
            
        # 가독성과 비중첩을 위해 y좌표 간격을 넓혀서 조정
        self.draw_text(surface, f"탑승 인원: {', '.join(self.my_crew)}", font_small, self.WHITE, 20, 65)
        self.draw_text(surface, f"산소: {self.resources['산소']}/200 | 전기: {self.resources['전기']}/200 | 정신력: {self.resources['정신력']}/200", font_small, self.WHITE, 20, 95)
        
        # INTRO popup dialog overlay
        if self.state == "INTRO":
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            dialog_w, dialog_h = 750, 400
            dialog_rect = pygame.Rect((w - dialog_w)//2, (h - dialog_h)//2, dialog_w, dialog_h)
            
            pygame.draw.rect(surface, (20, 20, 30), dialog_rect, border_radius=10)
            pygame.draw.rect(surface, self.ORANGE, dialog_rect, width=3, border_radius=10)
            
            font_title = get_scaled_font(28, is_korean=True)
            font_body = get_scaled_font(18, is_korean=True)
            font_button = get_scaled_font(20, is_korean=True)
            
            self.draw_text(surface, "🚨 우주선 긴급 대피 경보", font_title, self.RED, w//2, dialog_rect.top + 40, center=True)
            
            instructions = [
                "현재 심각한 지구 오염으로 인해 우주선에 긴급 탑승해야 합니다.",
                "우주선에서 생존하는 데 필요한 자원과 인원을 수집해 주세요.",
                "",
                "⏱️ 제한 시간: 30초",
                "🟢 초록색 크루(직업)는 화살표가 위치를 안내합니다. (최대 4명)",
                "🟠 주황색 자원은 산소, 전기, 정신력 중 하나를 5점 채워줍니다.",
                "⌨️ 이동: WASD 또는 방향키"
            ]
            
            y_offset = dialog_rect.top + 100
            for line in instructions:
                color = self.WHITE
                if "제한 시간" in line:
                    color = self.ORANGE
                elif "초록색 크루" in line:
                    color = self.GREEN
                elif "주황색 자원" in line:
                    color = self.ORANGE
                self.draw_text(surface, line, font_body, color, w//2, y_offset, center=True)
                y_offset += 30
                
            btn_w, btn_h = 320, 50
            btn_rect = pygame.Rect((w - btn_w)//2, dialog_rect.bottom - 75, btn_w, btn_h)
            
            mouse_pos = pygame.mouse.get_pos()
            hover = btn_rect.collidepoint(mouse_pos)
            
            btn_color = (40, 180, 100) if hover else (30, 140, 80)
            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(surface, self.WHITE, btn_rect, width=2, border_radius=5)
            
            self.draw_text(surface, "시작하기 (Space/Enter)", font_button, self.WHITE, w//2, btn_rect.centery, center=True)

        # CLEAR popup dialog overlay
        if self.is_cleared:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            dialog_w, dialog_h = 750, 420
            dialog_rect = pygame.Rect((w - dialog_w)//2, (h - dialog_h)//2, dialog_w, dialog_h)
            
            pygame.draw.rect(surface, (20, 30, 20), dialog_rect, border_radius=10)
            pygame.draw.rect(surface, self.GREEN, dialog_rect, width=3, border_radius=10)
            
            font_title = get_scaled_font(28, is_korean=True)
            font_body = get_scaled_font(18, is_korean=True)
            font_button = get_scaled_font(20, is_korean=True)
            
            self.draw_text(surface, "🎉 긴급 파밍 종료 (CLEAR)", font_title, self.GREEN, w//2, dialog_rect.top + 40, center=True)
            
            # Crew summary
            crew_str = ", ".join(self.my_crew) if self.my_crew else "없음"
            
            summary_lines = [
                "우주선 긴급 대피를 위한 자원 및 인원 수집 결과입니다.",
                "",
                f"👥 탑승한 크루원 ({len(self.my_crew)}명):",
                f"   {crew_str}",
                "",
                "🔋 최종 수집 자원 상태:",
                f"   산소: {self.resources['산소']}/200  |  전기: {self.resources['전기']}/200  |  정신력: {self.resources['정신력']}/200",
            ]
            
            y_offset = dialog_rect.top + 100
            for line in summary_lines:
                color = self.WHITE
                if "수집 결과" in line:
                    color = self.WHITE
                elif "탑승한 크루원" in line:
                    color = self.GREEN
                elif "최종 수집 자원" in line:
                    color = self.ORANGE
                self.draw_text(surface, line, font_body, color, w//2, y_offset, center=True)
                y_offset += 30
                
            # Exit button guide
            btn_w, btn_h = 320, 50
            btn_rect = pygame.Rect((w - btn_w)//2, dialog_rect.bottom - 75, btn_w, btn_h)
            
            mouse_pos = pygame.mouse.get_pos()
            hover = btn_rect.collidepoint(mouse_pos)
            
            btn_color = (40, 150, 180) if hover else (30, 110, 140)
            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(surface, self.WHITE, btn_rect, width=2, border_radius=5)
            
            self.draw_text(surface, "종료하기 (ESC 키 입력)", font_button, self.WHITE, w//2, btn_rect.centery, center=True)

    @property
    def minigame_start_time(self):
        return self.farm_start_time

    @minigame_start_time.setter
    def minigame_start_time(self, value):
        self.farm_start_time = value