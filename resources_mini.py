import pygame
import random
import sys
import os

class ResourcesGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.state = "MENU"
        self.current_stage = 1
        self.selected_planet = ""
        self.dead_count = 0
        
        self.crew_base = ["의사", "기술자", "경찰", "천문학자"]
        self.crew_farmable = ["정치인", "생명 유지장치 기술자", "개발자", "전기 기술자"]
        self.resources = {"산소": 100, "전기": 100, "정신력": 100}
        self.my_crew = list(self.crew_base)
        
        # 맵 데이터 설정
        self.MAP_WIDTH, self.MAP_HEIGHT = 2600, 2000  
        self.PLAYER_SIZE = 36
        self.player_rect = pygame.Rect(self.MAP_WIDTH//2, self.MAP_HEIGHT//2, self.PLAYER_SIZE, self.PLAYER_SIZE)
        
        self.items = []
        self.obstacles = []       
        self.city_blocks = []     
        self.crosswalks = []      
        self.farm_start_time = 0
        
        # 미니게임 내부 데이터 변수
        self.minigame_duration = 10000  # 10초 무조건 내부 타이머 작동
        self.minigame_start_time = 0
        self.analog_gauge = 0.0         # 0.0 ~ 100.0 변동형 가변 게이지
        
        # 행성 마우스 히트박스 영역 정의 (정규화된 초기값)
        self.planet_rect_a = pygame.Rect(0, 0, 200, 200)
        self.planet_rect_b = pygame.Rect(0, 0, 200, 200)
        self.planet_rect_c = pygame.Rect(0, 0, 200, 200)
        
    def update_hitboxes(self):
        from main import settings
        w, h = settings.width, settings.height
        pw, ph = int(w * 0.20), int(w * 0.20)
        py_y = int(h * 0.35)
        self.planet_rect_a = pygame.Rect(int(w * 0.15), py_y, pw, ph)
        self.planet_rect_b = pygame.Rect(int(w * 0.40), py_y, pw, ph)
        self.planet_rect_c = pygame.Rect(int(w * 0.65), py_y, pw, ph)
        
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
            inner_area = block.inflate(-30, -30)
            
            self.crosswalks.append(pygame.Rect(block.right, block.top + 60, 250, 50))
            self.crosswalks.append(pygame.Rect(block.left + 60, block.bottom, 50, 200))
            
            num_buildings = random.randint(6, 9)
            for _ in range(num_buildings):
                for attempt in range(60):
                    bw = random.randint(80, 180) 
                    bh = random.randint(80, 160)
                    bx = random.randint(inner_area.left, inner_area.right - bw)
                    by = random.randint(inner_area.top, inner_area.bottom - bh)
                    
                    new_building = pygame.Rect(bx, by, bw, bh)
                    if new_building.colliderect(player_spawn_zone): continue
                        
                    if not any(new_building.inflate(38, 38).colliderect(obs) for obs in self.obstacles):
                        self.obstacles.append(new_building)
                        break
                        
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
                    
        for _ in range(24):
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
        from main import settings, go_to_minigames, play_sfx
        if self.state == "MENU" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.init_farming()
                self.state = "FARMING"
                play_sfx("sfx_click")
            elif event.key == pygame.K_ESCAPE:
                go_to_minigames()
                play_sfx("sfx_end")
                
        elif self.state == "STAGE_ANNOUNCE" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.current_stage == 1:
                    self.state = "STAGE_1_FIRE"
                    self.minigame_start_time = pygame.time.get_ticks()
                    self.analog_gauge = 0.0
                elif self.current_stage == 7:
                    self.state = "PLANET_SELECT"
                elif self.current_stage == 9:
                    self.state = "STAGE_9_LANDING"
                    self.minigame_start_time = pygame.time.get_ticks()
                    self.analog_gauge = 20.0
                else:
                    self.current_stage += 1
                play_sfx("sfx_click")
            elif event.key == pygame.K_ESCAPE:
                go_to_minigames()
                play_sfx("sfx_end")
                
        elif self.state == "PLANET_SELECT":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                self.update_hitboxes()
                if self.planet_rect_a.collidepoint(mouse_pos):
                    self.selected_planet = "A"
                    self.current_stage = 9
                    self.state = "STAGE_ANNOUNCE"
                    play_sfx("sfx_click")
                elif self.planet_rect_b.collidepoint(mouse_pos):
                    self.selected_planet = "B"
                    self.current_stage = 9
                    self.state = "STAGE_ANNOUNCE"
                    play_sfx("sfx_click")
                elif self.planet_rect_c.collidepoint(mouse_pos):
                    self.selected_planet = "C"
                    self.current_stage = 9
                    self.state = "STAGE_ANNOUNCE"
                    play_sfx("sfx_click")
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                go_to_minigames()
                play_sfx("sfx_end")
                
        elif self.state == "STAGE_9_LANDING" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.analog_gauge = min(100.0, self.analog_gauge + 6.5)
                play_sfx("sfx_change")
            elif event.key == pygame.K_ESCAPE:
                go_to_minigames()
                play_sfx("sfx_end")
                
        elif self.state in ["FARMING", "STAGE_1_FIRE"] and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                go_to_minigames()
                play_sfx("sfx_end")
                
        elif self.state == "ENDING" and event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                go_to_minigames()
                play_sfx("sfx_end")
                
    def handle_input(self):
        if self.state != "FARMING":
            return
            
        keys = pygame.key.get_pressed()
        speed = 5
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
        from main import settings, play_sfx
        if self.state == "FARMING":
            elapsed = (pygame.time.get_ticks() - self.farm_start_time) / 1000
            remain = 30 - elapsed
            if remain <= 0:
                self.state = "STAGE_ANNOUNCE"
                self.current_stage = 1
                
            for item in self.items[:]:
                if self.player_rect.colliderect(item["rect"]):
                    if item["type"] == "crew" and len(self.my_crew) < 8:
                        self.my_crew.append(item["name"])
                        play_sfx("sfx_change")
                    elif item["type"] == "resource":
                        self.resources[item["name"]] = min(150, self.resources[item["name"]] + 10)
                        play_sfx("sfx_change")
                    self.items.remove(item)
                    
        elif self.state == "STAGE_1_FIRE":
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            if current_time - self.minigame_start_time >= self.minigame_duration:
                self.resources["산소"] -= 30
                if "기술자" in self.my_crew:
                    self.my_crew.remove("기술자")
                    self.dead_count += 1
                self.current_stage = 7
                self.state = "STAGE_ANNOUNCE"
                
            if keys[pygame.K_SPACE]:
                self.analog_gauge = min(100.0, self.analog_gauge + 0.8)
                if pygame.time.get_ticks() % 150 < 30:
                    play_sfx("sfx_change")
            else:
                self.analog_gauge = max(0.0, self.analog_gauge - 0.4)
                
            if self.analog_gauge >= 100.0:
                self.current_stage = 7
                self.state = "STAGE_ANNOUNCE"
                
        elif self.state == "STAGE_9_LANDING":
            current_time = pygame.time.get_ticks()
            if current_time - self.minigame_start_time >= self.minigame_duration:
                if self.my_crew:
                    self.my_crew.pop()
                    self.dead_count += 1
                self.state = "ENDING"
                
            self.analog_gauge = max(0.0, self.analog_gauge - 0.45)
            
            if self.analog_gauge >= 90.0:
                self.resources["산소"] = 1
                self.resources["전기"] = 1
                self.resources["정신력"] = 1
                self.state = "ENDING"
                
    def draw_text(self, surface, text, font, color, x, y, center=False):
        img = font.render(text, True, color)
        rect = img.get_rect()
        if center: rect.center = (x, y)
        else: rect.topleft = (x, y)
        surface.blit(img, rect)
        
    def draw(self, surface):
        from main import settings, get_scaled_font, CRT_GREEN, CRT_BRIGHT, WHITE, GRAY
        
        # 어두운 반투명 엠버 백드롭 시뮬레이션
        overlay = pygame.Surface((settings.width, settings.height), pygame.SRCALPHA)
        overlay.fill((15, 8, 3, 235))
        surface.blit(overlay, (0, 0))
        
        font_large = get_scaled_font(36, is_korean=True)
        font_main = get_scaled_font(22, is_korean=True)
        font_small = get_scaled_font(16, is_korean=True)
        
        COLOR_ORANGE = CRT_GREEN
        COLOR_RED = (220, 60, 40)
        COLOR_BLUE = (60, 120, 220)
        COLOR_GREEN = (70, 220, 70)
        COLOR_ROAD = (50, 42, 38)
        COLOR_SIDEWALK = (95, 82, 75)
        COLOR_BUILDING = (125, 110, 102)
        COLOR_SHADOW = (35, 30, 28)
        COLOR_LINE = (195, 175, 160)
        
        w, h = settings.width, settings.height
        
        if self.state == "MENU":
            self.draw_text(surface, "SPACE HARVEST", font_large, COLOR_ORANGE, w//2, h//3, center=True)
            self.draw_text(surface, "우주선 탑승 자원 수집", font_main, WHITE, w//2, h//3 + 55, center=True)
            self.draw_text(surface, "[ PRESS SPACE TO START ]", font_main, COLOR_ORANGE, w//2, h//2 + 30, center=True)
            self.draw_text(surface, "[ ESC: BACK TO MENU ]", font_small, GRAY, w//2, h - 80, center=True)
            
        elif self.state == "FARMING":
            elapsed = (pygame.time.get_ticks() - self.farm_start_time) / 1000
            remain = max(0.0, 30 - elapsed)
            
            camera_x = max(0, min(self.player_rect.centerx - w // 2, self.MAP_WIDTH - w))
            camera_y = max(0, min(self.player_rect.centery - h // 2, self.MAP_HEIGHT - h))
            
            # 미니 맵 그리기용 Surface
            map_surf = pygame.Surface((w, h))
            map_surf.fill(COLOR_ROAD)
            
            # 인도(시티 블록)
            for block in self.city_blocks:
                pygame.draw.rect(map_surf, COLOR_SIDEWALK, block.move(-camera_x, -camera_y))
                
            # 횡단보도
            for cw in self.crosswalks:
                if cw.right > self.MAP_WIDTH or cw.bottom > self.MAP_HEIGHT: continue
                screen_cw = cw.move(-camera_x, -camera_y)
                if cw.width > cw.height:
                    for lx in range(screen_cw.left, screen_cw.right, 35):
                        pygame.draw.rect(map_surf, COLOR_LINE, (lx, screen_cw.top, 15, screen_cw.height))
                else:
                    for ly in range(screen_cw.top, screen_cw.bottom, 35):
                        pygame.draw.rect(map_surf, COLOR_LINE, (screen_cw.left, ly, screen_cw.width, 15))
                        
            # 맵 외부 경계선
            pygame.draw.rect(map_surf, COLOR_ORANGE, pygame.Rect(-camera_x, -camera_y, self.MAP_WIDTH, self.MAP_HEIGHT), 8)
            
            # 장애물 건물
            for b in self.obstacles:
                screen_b = b.move(-camera_x, -camera_y)
                pygame.draw.rect(map_surf, COLOR_SHADOW, (screen_b.x, screen_b.y, screen_b.width, screen_b.height + 10))
                pygame.draw.rect(map_surf, COLOR_BUILDING, screen_b)
                pygame.draw.rect(map_surf, COLOR_SHADOW, screen_b, 2)
                
            # 아이템
            for item in self.items:
                color = COLOR_GREEN if item["type"] == "crew" else COLOR_ORANGE
                pygame.draw.rect(map_surf, color, item["rect"].move(-camera_x, -camera_y))
                
            # 플레이어
            pygame.draw.rect(map_surf, COLOR_BLUE, self.player_rect.move(-camera_x, -camera_y))
            
            surface.blit(map_surf, (0, 0))
            
            # HUD 바
            hud_bg = pygame.Surface((w, 130), pygame.SRCALPHA)
            hud_bg.fill((15, 8, 3, 200))
            surface.blit(hud_bg, (0, 0))
            pygame.draw.line(surface, COLOR_ORANGE, (0, 130), (w, 130), 2)
            
            self.draw_text(surface, f"FARMING TIME: {int(remain)}s", font_main, COLOR_ORANGE, 30, 20)
            self.draw_text(surface, f"CREW ({len(self.my_crew)}/8): {', '.join(self.my_crew)}", font_small, WHITE, 30, 55)
            self.draw_text(surface, f"OXYGEN: {self.resources['산소']} | POWER: {self.resources['전기']} | MIND: {self.resources['정신력']}", font_small, GRAY, 30, 85)
            
        elif self.state == "STAGE_ANNOUNCE":
            self.draw_text(surface, f"--- STAGE {self.current_stage} ---", font_large, COLOR_ORANGE, w//2, h//3, center=True)
            if self.current_stage == 1:
                self.draw_text(surface, "밀항자 수하물 발화! 화물칸에 문제가 생겼습니다.", font_main, WHITE, w//2, h//2, center=True)
            elif self.current_stage == 7:
                self.draw_text(surface, "목적지 부근 도달. 착륙할 행성을 선택하십시오.", font_main, WHITE, w//2, h//2, center=True)
            elif self.current_stage == 9:
                self.draw_text(surface, f"행성 {self.selected_planet} 궤도 진입. 역추진 시스템 가동 준비.", font_main, WHITE, w//2, h//2, center=True)
            self.draw_text(surface, "[ PRESS ENTER TO CONTINUE ]", font_small, COLOR_ORANGE, w//2, h - 120, center=True)
            self.draw_text(surface, "[ ESC: BACK TO MENU ]", font_small, GRAY, w//2, h - 80, center=True)
            
        elif self.state == "STAGE_1_FIRE":
            self.draw_text(surface, "WARNING: FIRE DETECTED", font_large, COLOR_RED, w//2, h//4, center=True)
            self.draw_text(surface, "스페이스바를 지속 조작하여 소화 압력을 유지하십시오!", font_main, WHITE, w//2, h//4 + 80, center=True)
            
            # 아날로그 바
            pygame.draw.rect(surface, (10, 5, 5), (w//2 - 200, h//2, 400, 35))
            pygame.draw.rect(surface, COLOR_ORANGE, (w//2 - 200, h//2, int(self.analog_gauge * 4), 35))
            pygame.draw.rect(surface, WHITE, (w//2 - 200, h//2, 400, 35), 2)
            
            self.draw_text(surface, "[ ESC: BACK TO MENU ]", font_small, GRAY, w//2, h - 80, center=True)
            
        elif self.state == "PLANET_SELECT":
            self.update_hitboxes()
            mouse_pos = pygame.mouse.get_pos()
            
            self.draw_text(surface, "[ SYSTEM: SELECT PLANET DESTINATION ]", font_large, COLOR_ORANGE, w//2, h//6, center=True)
            self.draw_text(surface, "마우스 커서로 목표 행성을 지정하십시오.", font_main, WHITE, w//2, h//6 + 60, center=True)
            
            # Planet A
            hover_a = self.planet_rect_a.collidepoint(mouse_pos)
            pygame.draw.circle(surface, (150, 30, 30) if not hover_a else (200, 50, 50), self.planet_rect_a.center, int(w*0.08))
            if hover_a: pygame.draw.circle(surface, WHITE, self.planet_rect_a.center, int(w*0.08) + 3, 2)
            self.draw_text(surface, "행성 A", font_main, COLOR_RED, self.planet_rect_a.centerx, self.planet_rect_a.bottom + 20, center=True)
            
            # Planet B
            hover_b = self.planet_rect_b.collidepoint(mouse_pos)
            pygame.draw.circle(surface, (30, 70, 160) if not hover_b else (50, 100, 220), self.planet_rect_b.center, int(w*0.065))
            pygame.draw.ellipse(surface, COLOR_BLUE if not hover_b else WHITE, (self.planet_rect_b.x - 20, self.planet_rect_b.y + int(w*0.045), int(w*0.24), 40), 4)
            if hover_b: pygame.draw.circle(surface, WHITE, self.planet_rect_b.center, int(w*0.065) + 3, 2)
            self.draw_text(surface, "행성 B", font_main, COLOR_BLUE, self.planet_rect_b.centerx, self.planet_rect_b.bottom + 20, center=True)
            
            # Planet C
            hover_c = self.planet_rect_c.collidepoint(mouse_pos)
            pygame.draw.circle(surface, (40, 140, 70) if not hover_c else (60, 190, 90), self.planet_rect_c.center, int(w*0.075))
            if hover_c: pygame.draw.circle(surface, WHITE, self.planet_rect_c.center, int(w*0.075) + 3, 2)
            self.draw_text(surface, "행성 C", font_main, COLOR_GREEN, self.planet_rect_c.centerx, self.planet_rect_c.bottom + 20, center=True)
            
            self.draw_text(surface, "[ ESC: BACK TO MENU ]", font_small, GRAY, w//2, h - 80, center=True)
            
        elif self.state == "STAGE_9_LANDING":
            self.draw_text(surface, "CRITICAL: REVERSE THRUST", font_large, COLOR_RED, w//2, h//8, center=True)
            self.draw_text(surface, "스페이스바 연타로 중력을 극복하고 역추진력을 유지하십시오!", font_main, WHITE, w//2, h//8 + 50, center=True)
            
            # Thruster gauge
            pygame.draw.rect(surface, (10, 5, 5), (w//2 - 40, h//2 - 150, 80, 300))
            gauge_height = int(self.analog_gauge * 3)
            pygame.draw.rect(surface, COLOR_RED, (w//2 - 40, h//2 + 150 - gauge_height, 80, gauge_height))
            pygame.draw.rect(surface, WHITE, (w//2 - 40, h//2 - 150, 80, 300), 3)
            
            pygame.draw.line(surface, COLOR_ORANGE, (w//2 - 50, h//2 - 110), (w//2 + 50, h//2 - 110), 4)
            
            self.draw_text(surface, "[ ESC: BACK TO MENU ]", font_small, GRAY, w//2, h - 80, center=True)
            
        elif self.state == "ENDING":
            self.draw_text(surface, f"--- FINAL LOG: PLANET {self.selected_planet} ---", font_large, COLOR_ORANGE, w//2, h//6, center=True)
            
            ending_text = ""
            if self.selected_planet == "A": ending_text = "[외계인 조우 엔딩] 기괴한 외계 생명체의 관찰 표본이 되었습니다."
            elif self.selected_planet == "B":
                if self.dead_count <= 4: ending_text = "[진(True) 해피엔딩] 찬란한 제2의 지구 문명을 건설했습니다!"
                else: ending_text = "[종말 엔딩] 노동력 부족으로 인류는 쓸쓸히 절멸했습니다."
            elif self.selected_planet == "C": ending_text = "[게임오버] 거대한 포식 생명체의 가축으로 전락했습니다."
                
            self.draw_text(surface, ending_text, font_main, WHITE, w//2, h//2 - 80, center=True)
            self.draw_text(surface, f"SURVIVORS: {', '.join(self.my_crew) if self.my_crew else 'NONE'}", font_main, COLOR_ORANGE, w//2, h//2 + 20, center=True)
            self.draw_text(surface, f"CASUALTIES: {self.dead_count}", font_main, COLOR_RED, w//2, h//2 + 70, center=True)
            self.draw_text(surface, "[ PRESS ESC OR ENTER TO EXIT ]", font_small, WHITE, w//2, h - 120, center=True)