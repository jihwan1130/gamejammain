import pygame
import sys
import random
import os

from visual_effects import draw_terminal_hud

class PathogenQuarantineGame:
    def __init__(self):
        # 색상 정의
        self.MINT = (80, 220, 140)
        self.DARK_MINT = (5, 25, 15)
        self.WHITE = (240, 255, 245)
        self.SHADOW_BLACK = (10, 15, 10)
        self.RED = (240, 60, 60)
        self.BLUE = (60, 150, 240)
        
        # 폰트 로드 및 정적 텍스트 캐싱 (최적화: 매 프레임 렌더링 방지)
        try:
            from main import get_scaled_font
            self.font_main = get_scaled_font(24, is_korean=True)
            self.font_sub = get_scaled_font(18, is_korean=True)
        except Exception:
            self.font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
            self.font_sub = pygame.font.SysFont("malgungothic", 18)
            
        # 정적 가이드 텍스트 캐싱 (성능 향상)
        self.txt_guide_surf = self.font_main.render("SYSTEM VIRUS INTRUSION DETECTED", True, self.WHITE)
        self.txt_job_surf = self.font_sub.render("CONTROLS: [F] 위쪽 바이러스 | [J] 아래쪽 바이러스", True, self.MINT)
        self.txt_life_title_surf = self.font_sub.render("DEFENSE SECURITY LEVEL : ", True, self.WHITE)
        
        # 판정 피드백 캐시 변수
        self.cached_feedback_text = ""
        self.cached_feedback_surf = None
        
        # 밸런스 및 배치 계수
        self.lane_top_y = 320
        self.lane_bottom_y = 440
        self.hit_zone_x = 200      # 왼쪽 판정선 위치
        self.hit_radius = 30       # PERFECT/GREAT 판정 범위
        self.miss_zone_radius = 70 # 이 범위 밖에 있거나 없으면 허공 노트
        self.max_lives = 3
        self.limit_time = 30.0
        
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "plantspace.jpg")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"plantspace.jpg 로드 실패: {e}")
            
        self.reset()
        
    def reset(self):
        self.lives = self.max_lives
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
        self.viruses = []
        self.spawn_timer = 0
        self.spawn_delay = 45 # 바이러스 생성 주기 (프레임 단위)
        
        self.hit_feedback = ""
        self.feedback_timer = 0
        self.top_pressed = False
        self.bottom_pressed = False
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # 1. 바이러스 자동 생성
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0
                lane = random.choice(["top", "bottom"])
                # [x_pos, lane, processed_flag]
                self.viruses.append([1000 + 20, lane, False])
                
            # 2. 바이러스 이동 및 노치고 지나간 경우 처리
            for v in self.viruses:
                v[0] -= 6  # 이동 속도
                
                # 타이밍을 놓쳐서 판정선을 완전히 지나쳐 버린 경우
                if v[0] < self.hit_zone_x - self.hit_radius and not v[2]:
                    v[2] = True
                    self.lives -= 1
                    self.set_feedback("MISS (MISSED)")
                    
            # 화면 밖으로 완전히 나간 바이러스 정리 (최적화)
            if self.viruses and self.viruses[0][0] <= 50:
                self.viruses = [v for v in self.viruses if v[0] > 50]
                
            # 승리/패배 조건 확인
            if self.elapsed_time >= self.limit_time and self.lives > 0:
                self.state = "SUCCESS"
            elif self.lives <= 0:
                self.state = "FAIL"
                
    def set_feedback(self, text):
        """판정 피드백 텍스트를 캐싱하여 렌더링 부하를 줄임 (최적화)"""
        self.hit_feedback = text
        self.feedback_timer = 30
        if self.cached_feedback_text != text:
            self.cached_feedback_text = text
            fb_color = self.MINT if "PERFECT" in text else self.RED
            self.cached_feedback_surf = self.font_main.render(text, True, fb_color)
            
    def check_hit(self, lane):
        from main import play_sfx
        # 아직 처리되지 않은 해당 레인 바이러스 필터링
        target = [v for v in self.viruses if v[1] == lane and not v[2]]
        
        if target:
            # 판정선 HIT_ZONE_X(200)에 가장 가까운 바이러스 검출
            closest = min(target, key=lambda x: abs(x[0] - self.hit_zone_x))
            distance = abs(closest[0] - self.hit_zone_x)
            
            if distance <= self.hit_radius:  # PERFECT
                closest[2] = True
                self.set_feedback("PERFECT")
                play_sfx("sfx_click")
            elif distance <= self.miss_zone_radius:  # BAD
                closest[2] = True
                self.lives -= 1
                self.set_feedback("BAD")
            else:  # 허공 노트 (너무 멀 때)
                self.lives -= 1
                self.set_feedback("MISS (EMPTY PRESS)")
        else:  # 화면에 해당 채보가 아예 없는데 누른 경우
            self.lives -= 1
            self.set_feedback("MISS (EMPTY PRESS)")
            
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        from main import settings, go_to_minigames, play_sfx, keyboard_sfx
        
        # 키 감지 리셋 (임팩트 그리기용)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_f:
                self.top_pressed = False
            if event.key == pygame.K_j:
                self.bottom_pressed = False
                
        if self.state != "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play_sfx("sfx_end")
                    go_to_minigames()
                elif event.key == pygame.K_RETURN:
                    self.reset()
                    if keyboard_sfx:
                        keyboard_sfx.set_volume(settings.volume)
                        keyboard_sfx.play()
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                play_sfx("sfx_end")
                go_to_minigames()
            elif event.key == pygame.K_f:  # 위쪽 레인 키
                self.top_pressed = True
                self.check_hit("top")
            elif event.key == pygame.K_j:  # 아래쪽 레인 키
                self.bottom_pressed = True
                self.check_hit("bottom")
                
    def draw(self, surface):
        from main import settings, WHITE, get_scaled_font
        
        # 가상 서페이스 (1000x700) 생성 및 배경 그리기
        virtual_surf = pygame.Surface((1000, 700))
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 가독성을 높이기 위해 어두운 반투명 오버레이 추가
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((5, 20, 10, 160))  # R, G, B, Alpha
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill(self.DARK_MINT)
        
        # 캐싱된 정적 안내 텍스트 출력
        virtual_surf.blit(self.txt_guide_surf, (500 - self.txt_guide_surf.get_width()//2, 80))
        virtual_surf.blit(self.txt_job_surf, (500 - self.txt_job_surf.get_width()//2, 130))
        
        # 기회(Defense Security Level) 표시부 그리기 (동적 중앙 정렬로 겹침 방지)
        life_str = "".join(["■ " for _ in range(max(0, self.lives))]) + "".join(["X " for _ in range(self.max_lives - max(0, self.lives))])
        txt_life = self.font_main.render(life_str, True, self.RED if self.lives == 1 else self.MINT)
        
        title_w = self.txt_life_title_surf.get_width()
        life_w = txt_life.get_width()
        total_w = title_w + 10 + life_w
        start_x = 500 - total_w // 2
        
        virtual_surf.blit(self.txt_life_title_surf, (start_x, 190))
        virtual_surf.blit(txt_life, (start_x + title_w + 10, 185))
        
        # 두 개의 레인(트랙) 그리기
        pygame.draw.line(virtual_surf, self.SHADOW_BLACK, (0, self.lane_top_y), (1000, self.lane_top_y), 4)
        pygame.draw.line(virtual_surf, self.SHADOW_BLACK, (0, self.lane_bottom_y), (1000, self.lane_bottom_y), 4)
        
        # 판정선 서클
        pygame.draw.circle(virtual_surf, self.MINT, (self.hit_zone_x, self.lane_top_y), 20, 2)
        pygame.draw.circle(virtual_surf, self.MINT, (self.hit_zone_x, self.lane_bottom_y), 20, 2)
        
        # 키 입력 순간 판정선 임팩트 효과
        if self.top_pressed:
            pygame.draw.circle(virtual_surf, self.WHITE, (self.hit_zone_x, self.lane_top_y), 28, 3)
        if self.bottom_pressed:
            pygame.draw.circle(virtual_surf, self.WHITE, (self.hit_zone_x, self.lane_bottom_y), 28, 3)
            
        # 다가오는 바이러스(노트) 그리기
        for v in self.viruses:
            if not v[2]:  # 처리되지 않은 바이러스만 렌더링
                y_pos = self.lane_top_y if v[1] == "top" else self.lane_bottom_y
                color = self.RED if v[1] == "top" else self.BLUE
                pygame.draw.circle(virtual_surf, color, (v[0], y_pos), 15)
                # 십자 디테일 박스
                pygame.draw.rect(virtual_surf, self.WHITE, (v[0]-4, y_pos-19, 8, 38), 1)
                pygame.draw.rect(virtual_surf, self.WHITE, (v[0]-19, y_pos-4, 38, 8), 1)
                
        # 판정 피드백 텍스트 출력 (텍스트 렌더링 캐싱 최적화 적용)
        if self.feedback_timer > 0 and self.cached_feedback_surf:
            virtual_surf.blit(self.cached_feedback_surf, (self.hit_zone_x - self.cached_feedback_surf.get_width()//2, self.lane_top_y - 90))
            self.feedback_timer -= 1
            
        # HUD 테두리 및 진행 시간 드로잉
        draw_terminal_hud(virtual_surf, "ANTI-VIRUS DEFENSE SYSTEM", self.limit_time, self.elapsed_time, self.MINT)
        
        # 게임 결과 오버레이
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((5, 20, 10, 220))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = self.font_main.render("■ 방화벽 유지 성공 (SUCCESS) ■", True, self.MINT)
                sub = self.font_sub.render("30초 동안 메인프레임을 안전하게 방어해 냈습니다.", True, self.WHITE)
            else:
                msg = self.font_main.render("🚨 방어선 돌파 - 시스템 멜트다운 (FAIL) 🚨", True, self.RED)
                sub = self.font_sub.render("허용된 모든 보안 기회를 소진했습니다. 방화벽이 해제됩니다.", True, self.WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
        # 메인 게임 스케일링 블릿
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = PathogenQuarantineGame()
    from visual_effects import TerminalFilter
    filter_crt = TerminalFilter(1000, 700)
    
    # 임시 키 제어용 자체 루프
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