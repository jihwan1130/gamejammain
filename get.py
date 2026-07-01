import pygame
import random
import sys
import os
import math

class ResourcesGame:
    def __init__(self):
        # Cache for optimized text rendering
        self.text_cache = {}
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
        self.PLAYER_SIZE = 36
        self.player_rect = pygame.Rect(self.MAP_WIDTH//2, self.MAP_HEIGHT//2, self.PLAYER_SIZE, self.PLAYER_SIZE)
        
        self.items = []
        self.obstacles = []       
        self.city_blocks = []     
        self.crosswalks = []      
        self.farm_start_time = pygame.time.get_ticks()
        self.is_cleared = False
        
        # Initialize map elements
        self.init_farming()
        
        # Clear text cache
        self.text_cache.clear()
        
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
                # Check collision against obstacles, already placed items (with buffer), and player spawn buffer
                if (not any(temp_rect.colliderect(b.inflate(10, 10)) for b in self.obstacles) and
                    not any(temp_rect.colliderect(item["rect"].inflate(15, 15)) for item in self.items) and
                    not temp_rect.colliderect(player_buffer)):
                    self.items.append({"rect": temp_rect, "type": "crew", "name": c})
                    placed = True
                    
        for _ in range(48):
            res_type = random.choice(["산소", "전기", "정신력"])
            placed = False
            while not placed:
                rx = random.randint(80, self.MAP_WIDTH - 80)
                ry = random.randint(80, self.MAP_HEIGHT - 80)
                temp_rect = pygame.Rect(rx, ry, 20, 20)
                # Check collision against obstacles, already placed items (with buffer), and player spawn buffer
                if (not any(temp_rect.colliderect(b.inflate(8, 8)) for b in self.obstacles) and
                    not any(temp_rect.colliderect(item["rect"].inflate(15, 15)) for item in self.items) and
                    not temp_rect.colliderect(player_buffer)):
                    self.items.append({"rect": temp_rect, "type": "resource", "name": res_type})
                    placed = True
                    
        self.farm_start_time = pygame.time.get_ticks()
        
    def handle_event(self, event):
        from main import go_to_minigames, play_sfx, settings
        if self.state == "INTRO":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                w, h = settings.width, settings.height
                dialog_w, dialog_h = 620, 360
                dialog_rect = pygame.Rect((w - dialog_w)//2, (h - dialog_h)//2, dialog_w, dialog_h)
                btn_w, btn_h = 220, 50
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
                    go_to_minigames()
                    play_sfx("sfx_end")
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    go_to_minigames()
                    play_sfx("sfx_end")
                elif event.key == pygame.K_RETURN and self.is_clear_finished():
                    self.reset()
                    
    def is_clear_finished(self):
        return self.is_cleared
        
    def handle_input(self):
        if self.state != "PLAYING" or self.is_cleared:
            return
            
        keys = pygame.key.get_pressed()
        speed = 6.3  # 7 * 0.9 = 6.3
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = speed
        
        self.player_rect.x += dx
        for b in self.obstacles:
            if self.player_rect.colliderect(b):
                if dx > 0: self.player_rect.right = b.left
                if dx < 0: self.player_rect.left = b.right
                
        self.player_rect.y += dy
        for b in self.obstacles:
            if self.player_rect.colliderect(b):
                if dy > 0: self.player_rect.bottom = b.top
                if dy < 0: self.player_rect.top = b.bottom
                
        self.player_rect.clamp_ip(pygame.Rect(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT))
        
    def update(self):
        if self.state == "PLAYING" and not self.is_cleared:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.farm_start_time) / 1000
            remain = 30 - elapsed
            if remain <= 0:
                self.is_cleared = True
                
            for item in self.items[:]:
                if self.player_rect.colliderect(item["rect"]):
                    from main import play_sfx
                    if item["type"] == "crew" and len(self.my_crew) < 8:
                        self.my_crew.append(item["name"])
                        play_sfx("sfx_change")
                    elif item["type"] == "resource":
                        # 초기자원 80/200, 자원당 2씩 수집
                        self.resources[item["name"]] = min(200, self.resources[item["name"]] + 2)
                        play_sfx("sfx_change")
                    self.items.remove(item)
                    
    def get_cached_text(self, text, font, color):
        cache_key = (text, id(font), color)
        if cache_key not in self.text_cache:
            self.text_cache[cache_key] = font.render(text, True, color)
        return self.text_cache[cache_key]
        
    def draw_text(self, surface, text, font, color, x, y, center=False):
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
                is_green_item = (item["type"] == "crew" or (item["type"] == "resource" and item["name"] == "산소"))
                color = self.GREEN if is_green_item else self.ORANGE
                pygame.draw.rect(map_surf, color, item["rect"].move(-camera_x, -camera_y))
                
                # Draw floating green arrow for on-screen green items
                if is_green_item:
                    bob = math.sin(pygame.time.get_ticks() * 0.012) * 4
                    screen_rect = item["rect"].move(-camera_x, -camera_y)
                    tx = screen_rect.centerx
                    ty = screen_rect.top - 8 + bob
                    pygame.draw.polygon(map_surf, self.GREEN, [
                        (tx, ty),
                        (tx - 6, ty - 10),
                        (tx + 6, ty - 10)
                    ])
                
        # Player
        pygame.draw.rect(map_surf, self.BLUE, self.player_rect.move(-camera_x, -camera_y))
        
        surface.blit(map_surf, (0, 0))
        
        # Draw off-screen green indicators pointing to off-screen green items
        px, py = self.player_rect.center
        offscreen_greens = []
        for item in self.items:
            is_green_item = (item["type"] == "crew" or (item["type"] == "resource" and item["name"] == "산소"))
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
            
        # HUD / Text Drawing (with scaling fonts)
        font_main = get_scaled_font(22, is_korean=True)
        font_small = get_scaled_font(16, is_korean=True)
        
        if self.state == "INTRO":
            remain = 30.0
        else:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.farm_start_time) / 1000
            remain = max(0.0, 30 - elapsed)
        
        hud_bg = pygame.Surface((w, 130), pygame.SRCALPHA)
        hud_bg.fill((15, 8, 3, 200))
        surface.blit(hud_bg, (0, 0))
        pygame.draw.line(surface, self.ORANGE, (0, 130), (w, 130), 2)
        
        if not self.is_cleared:
            self.draw_text(surface, f"남은 시간: {int(remain)}초", font_main, self.ORANGE, 20, 20)
        else:
            self.draw_text(surface, "★ 파밍 종료 (CLEAR) ★ - 다음 프로젝트 씬 연동 대기 중", font_main, self.GREEN, 20, 20)
            
        self.draw_text(surface, f"탑승 인원: {', '.join(self.my_crew)}", font_small, self.WHITE, 20, 60)
        self.draw_text(surface, f"산소: {self.resources['산소']}/200 | 전기: {self.resources['전기']}/200 | 정신력: {self.resources['정신력']}/200", font_small, self.WHITE, 20, 90)
        
        # INTRO popup dialog overlay
        if self.state == "INTRO":
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            dialog_w, dialog_h = 620, 360
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
                "🟢 초록색 자원(산소 및 크루)은 화살표가 위치를 안내합니다.",
                "⌨️ 이동: WASD 또는 방향키"
            ]
            
            y_offset = dialog_rect.top + 100
            for line in instructions:
                color = self.WHITE
                if "제한 시간" in line:
                    color = self.ORANGE
                elif "초록색 자원" in line:
                    color = self.GREEN
                self.draw_text(surface, line, font_body, color, w//2, y_offset, center=True)
                y_offset += 30
                
            btn_w, btn_h = 220, 50
            btn_rect = pygame.Rect((w - btn_w)//2, dialog_rect.bottom - 75, btn_w, btn_h)
            
            mouse_pos = pygame.mouse.get_pos()
            hover = btn_rect.collidepoint(mouse_pos)
            
            btn_color = (40, 180, 100) if hover else (30, 140, 80)
            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(surface, self.WHITE, btn_rect, width=2, border_radius=5)
            
            self.draw_text(surface, "시작하기 (Space/Enter)", font_button, self.WHITE, w//2, btn_rect.centery, center=True)