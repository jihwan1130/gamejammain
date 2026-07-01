import pygame
import sys
import random
import os

def get_main_val(name, default=None):
    try:
        import sys
        main_mod = sys.modules.get('main') or sys.modules.get('__main__')
        if main_mod and hasattr(main_mod, name):
            return getattr(main_mod, name)
    except:
        pass
    return default

from visual_effects import draw_terminal_hud

class PathogenQuarantineGame:
    def __init__(self):
        # 색상 상수 정의
        self.DARK_MINT = (5, 20, 10)
        self.MINT = (80, 220, 140)
        self.WHITE = (240, 250, 245)
        self.RED = (255, 75, 75)
        self.BLUE = (75, 140, 255)
        self.GRAY = (60, 60, 60)
        
        self.bg_img = None
        
        # 폰트 로드 및 정적 텍스트 캐싱
        get_scaled_font = get_main_val('get_scaled_font')
        if get_scaled_font:
            self.font_main = get_scaled_font(24, is_korean=True)
            self.font_sub = get_scaled_font(18, is_korean=True)
        else:
            self.font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
            self.font_sub = pygame.font.SysFont("malgungothic", 18)
            
        # 정적 텍스트 렌더링 캐싱
        self.txt_guide_surf = self.font_main.render("SYSTEM VIRUS INTRUSION DETECTED", True, self.WHITE)
        self.txt_job_surf = self.font_sub.render("CONTROLS: [F] 위쪽 바이러스 | [J] 아래쪽 바이러스", True, self.MINT)
        self.txt_life_title_surf = self.font_sub.render("DEFENSE SECURITY LEVEL : ", True, self.WHITE)
        
        # 판정 영역 크기 설정
        self.lane_top_y = 280
        self.lane_bottom_y = 440
        self.hit_zone_x = 200
        self.hit_radius = 42
        self.miss_zone_radius = 80
        
        self.reset()
        
    def reset(self):
        self.viruses = []
        self.spawn_timer = 0
        self.spawn_delay = 32  # 프레임 단위 (약 0.5초 간격)
        
        # 목숨 시스템
        self.max_lives = 3
        self.lives = 3
        
        # 시간 추적
        self.start_ticks = pygame.time.get_ticks()
        self.limit_time = 30.0  # 30초 동안 방어
        self.elapsed_time = 0.0
        
        self.state = "PLAYING"  # PLAYING, SUCCESS, FAIL
        self.penalty_selected = None
        
        # 입력 상태 및 판정 피드백 캐싱
        self.top_pressed = False
        self.bottom_pressed = False
        self.hit_feedback = ""
        self.feedback_timer = 0
        self.cached_feedback_text = ""
        self.cached_feedback_surf = None
        
    def on_fail(self):
        self.penalty_selected = 1

    def apply_penalty(self):
        resources_game = get_main_val('resources_game')
        if not resources_game:
            return
        if hasattr(resources_game, 'resources'):
            if "산소" in resources_game.resources:
                resources_game.resources["산소"] = max(0, resources_game.resources["산소"] - 50)
                print(f"[PENALTY] Pathogen control failed. Oxygen decreased by 50. Current: {resources_game.resources['산소']}")
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # 1. 바이러스 생성
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0
                lane = random.choice(["top", "bottom"])
                self.viruses.append([1000 + 20, lane, False])
                
            # 2. 바이러스 이동 및 노치고 지나간 경우 처리
            for v in self.viruses:
                v[0] -= 6  # 이동 속도
                
                # 타이밍을 놓쳐서 판정선을 완전히 지나쳐 버린 경우
                if v[0] < self.hit_zone_x - self.hit_radius and not v[2]:
                    v[2] = True
                    self.lives -= 1
                    self.set_feedback("MISS (MISSED)")
                    
            # 화면 밖으로 완전히 나간 바이러스 정리
            if self.viruses and self.viruses[0][0] <= 50:
                self.viruses = [v for v in self.viruses if v[0] > 50]
                
            # 3. 승리/패배 조건 확인
            if self.elapsed_time >= self.limit_time and self.lives > 0:
                self.state = "SUCCESS"
            elif self.lives <= 0:
                self.state = "FAIL"
                self.on_fail()
                
    def set_feedback(self, text):
        self.hit_feedback = text
        self.feedback_timer = 30
        if self.cached_feedback_text != text:
            self.cached_feedback_text = text
            fb_color = self.GREEN if "PERFECT" in text else (self.RED if "MISS" in text else self.BLUE)
            self.cached_feedback_surf = self.font_main.render(text, True, fb_color)
            
    def check_hit(self, lane):
        play_sfx = get_main_val('play_sfx')
        target = [v for v in self.viruses if v[1] == lane and not v[2]]
        
        if target:
            closest = min(target, key=lambda x: abs(x[0] - self.hit_zone_x))
            distance = abs(closest[0] - self.hit_zone_x)
            
            if distance <= self.hit_radius:  # PERFECT
                closest[2] = True
                self.set_feedback("PERFECT")
                if play_sfx:
                    play_sfx("sfx_click")
            elif distance <= self.miss_zone_radius:  # BAD
                closest[2] = True
                self.lives -= 1
                self.set_feedback("BAD")
            else:
                self.lives -= 1
                self.set_feedback("MISS (EMPTY PRESS)")
        else:
            self.lives -= 1
            self.set_feedback("MISS (EMPTY PRESS)")
            
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        settings = get_main_val('settings')
        vol = settings.volume if settings else 0.5
        play_sfx = get_main_val('play_sfx')
        go_to_minigames = get_main_val('go_to_minigames') or get_main_val('go_to_main_menu')
        keyboard_sfx = get_main_val('keyboard_sfx')
        
        is_campaign = False
        if settings and settings.is_campaign:
            is_campaign = True
            
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_f:
                self.top_pressed = False
            if event.key == pygame.K_j:
                self.bottom_pressed = False
                
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
            elif event.key == pygame.K_f:
                self.top_pressed = True
                self.check_hit("top")
            elif event.key == pygame.K_j:
                self.bottom_pressed = True
                self.check_hit("bottom")
                
    def draw(self, surface):
        WHITE = get_main_val('WHITE', (255, 255, 255))
        
        virtual_surf = pygame.Surface((1000, 700))
        virtual_surf.fill(self.DARK_MINT)
        
        # 타이틀 및 가이드 출력
        virtual_surf.blit(self.txt_guide_surf, (500 - self.txt_guide_surf.get_width()//2, 80))
        virtual_surf.blit(self.txt_job_surf, (500 - self.txt_job_surf.get_width()//2, 130))
        
        # 기회(Defense Security Level) 표시부 그리기
        life_str = "".join(["■ " for _ in range(max(0, self.lives))]) + "".join(["X " for _ in range(self.max_lives - max(0, self.lives))])
        txt_life = self.font_main.render(life_str, True, self.RED if self.lives == 1 else self.MINT)
        
        title_w = self.txt_life_title_surf.get_width()
        life_w = txt_life.get_width()
        total_w = title_w + life_w
        start_x = 500 - total_w // 2
        
        virtual_surf.blit(self.txt_life_title_surf, (start_x, 180))
        virtual_surf.blit(txt_life, (start_x + title_w, 176))
        
        # 레인 판정선 그리기
        pygame.draw.line(virtual_surf, self.GRAY, (100, self.lane_top_y), (900, self.lane_top_y), 2)
        pygame.draw.line(virtual_surf, self.GRAY, (100, self.lane_bottom_y), (900, self.lane_bottom_y), 2)
        
        pygame.draw.circle(virtual_surf, self.MINT, (self.hit_zone_x, self.lane_top_y), self.hit_radius, 2)
        pygame.draw.circle(virtual_surf, self.MINT, (self.hit_zone_x, self.lane_bottom_y), self.hit_radius, 2)
        
        # 키 입력 순간 판정선 임팩트 효과
        if self.top_pressed:
            pygame.draw.circle(virtual_surf, self.WHITE, (self.hit_zone_x, self.lane_top_y), 28, 3)
        if self.bottom_pressed:
            pygame.draw.circle(virtual_surf, self.WHITE, (self.hit_zone_x, self.lane_bottom_y), 28, 3)
            
        # 다가오는 바이러스(노트) 그리기
        for v in self.viruses:
            if not v[2]:
                y_pos = self.lane_top_y if v[1] == "top" else self.lane_bottom_y
                color = self.RED if v[1] == "top" else self.BLUE
                pygame.draw.circle(virtual_surf, color, (v[0], y_pos), 15)
                pygame.draw.rect(virtual_surf, self.WHITE, (v[0]-4, y_pos-19, 8, 38), 1)
                pygame.draw.rect(virtual_surf, self.WHITE, (v[0]-19, y_pos-4, 38, 8), 1)
                
        # 판정 피드백 텍스트 출력
        if self.feedback_timer > 0 and self.cached_feedback_surf:
            virtual_surf.blit(self.cached_feedback_surf, (self.hit_zone_x - self.cached_feedback_surf.get_width()//2, self.lane_top_y - 90))
            self.feedback_timer -= 1
            
        # 공통 터미널 HUD 그리기
        draw_terminal_hud(virtual_surf, "ANTI-VIRUS DEFENSE SYSTEM", self.limit_time, self.elapsed_time, self.MINT)
        
        # 게임 결과 오버레이
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((5, 20, 10, 220))
            virtual_surf.blit(overlay, (0, 0))
            
            is_campaign = False
            settings = get_main_val('settings')
            if settings and settings.is_campaign:
                is_campaign = True
                
            if is_campaign:
                sub_control_text = "[ ENTER: 계속 진행 ]"
            else:
                sub_control_text = "[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]"
                
            sub_control = self.font_sub.render(sub_control_text, True, WHITE)
            
            if self.state == "SUCCESS":
                msg = self.font_main.render("■ 방화벽 유지 성공 (SUCCESS) ■", True, self.MINT)
                sub = self.font_sub.render("30초 동안 메인프레임을 안전하게 방어해 냈습니다.", True, WHITE)
            else:
                msg = self.font_main.render("🚨 방어선 돌파 - 시스템 멜트다운 (FAIL) 🚨", True, self.RED)
                sub = self.font_sub.render("환자가 과호흡이 와 산소가 소모됐습니다. (산소 -50)", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 300))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 350))
            virtual_surf.blit(sub_control, (500 - sub_control.get_width()//2, 400))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = PathogenQuarantineGame()
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