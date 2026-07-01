import pygame
import sys
import math
import random
import os

from visual_effects import draw_terminal_hud

def get_main_val(name, default=None):
    try:
        import sys
        main_mod = sys.modules.get('main') or sys.modules.get('__main__')
        if main_mod and hasattr(main_mod, name):
            return getattr(main_mod, name)
    except:
        pass
    return default

class CrankLandingGame:
    def __init__(self):
        # 색상 정의
        self.MINT = (80, 220, 140)
        self.DARK_MINT = (5, 25, 15)
        self.WHITE = (240, 255, 245)
        self.SHADOW_BLACK = (10, 15, 10)
        self.RED = (240, 60, 60)
        self.METAL_GRAY = (150, 155, 155)
        self.DARK_GRAY = (80, 85, 85)
        self.PLASTIC_BLACK = (25, 25, 25)
        
        # 폰트 로드 및 텍스트 캐싱 최적화
        try:
            from main import get_scaled_font
            self.font_main = get_scaled_font(24, is_korean=True)
            self.font_sub = get_scaled_font(18, is_korean=True)
        except Exception:
            self.font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
            self.font_sub = pygame.font.SysFont("malgungothic", 18)
            
        # 정적 텍스트 캐싱 (최적화)
        self.txt_guide_surf = self.font_main.render("FINAL DILEMMA: 역추진 크랭크 제어 장치 수동 연동", True, self.WHITE)
        self.txt_job_surf = self.font_sub.render("조작법: 마우스 [좌클릭]을 꾹 누른 상태로 중심축 주변을 시계방향(↻)으로 크게 돌리세요!", True, self.MINT)
        
        self.txt_status_spinning = self.font_main.render("⚙️ SPINNING!", True, self.MINT)
        self.txt_status_hold = self.font_main.render("⚙️ HOLD & TURN", True, self.WHITE)
        
        # 딜레마 관련 문구 캐싱
        self.txt_critical_fail = self.font_main.render("🚨 역추진 압력 부족 - 시스템 잠김 (CRITICAL FAIL) 🚨", True, self.RED)
        self.txt_instruction = self.font_sub.render("누군가 체중으로 레버를 내리눌러야만 합니다. 희생할 승무원을 고르십시오. [↑/↓ 이동, Enter 확정]", True, self.WHITE)
        self.txt_ending_title = self.font_main.render("🚨 착륙 강행 완료 - 무거운 대가 🚨", True, self.RED)
        
        # 기하학적 상수
        self.crank_center = (500, 400) # 가상 해상도 1000x700의 중앙 하단부
        self.arm_length = 115
        self.handle_radius = 22
        self.limit_time = 20.0
        
        # 직업 리스트
        self.all_jobs = ["의사", "정치인", "기술자", "경찰", "천문학자", "시민", "개발자", "전기 기술자"]
        
        self.reset()
        
    def reset(self):
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0.0
        self.state = "PLAYING" # PLAYING, SUCCESS, SELECT_SACRIFICE, FAIL (최종 실패)
        
        # 랜덤 4명 승무원
        self.crew_list = random.sample(self.all_jobs, 4)
        self.selected_crew_idx = 0
        
        # 크랭크 조작 변수
        self.visual_angle = 0.0
        self.progress_gauge = 0.0
        self.current_sector = -1
        self.spin_feedback_timer = 0
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # 마우스 입력 체크 (가상 좌표로 변환)
            from main import settings
            mouse_down = pygame.mouse.get_pressed()[0]
            mx_raw, my_raw = pygame.mouse.get_pos()
            
            vmx = int(mx_raw * 1000 / settings.width)
            vmy = int(my_raw * 700 / settings.height)
            
            if mouse_down:
                mx = vmx - self.crank_center[0]
                my = vmy - self.crank_center[1]
                dist = math.hypot(mx, my)
                
                # 조작 반경 판정 (40~250px)
                if 40 <= dist <= 250:
                    # 각 분면 섹터 결정
                    if mx >= 0 and my < 0:      next_sector = 0  # 우상
                    elif mx >= 0 and my >= 0:    next_sector = 1  # 우하
                    elif mx < 0 and my >= 0:     next_sector = 2  # 좌하
                    else:                        next_sector = 3  # 좌상
                    
                    if self.current_sector == -1:
                        self.current_sector = next_sector
                        
                    # 시계 방향 순서 밟았는지 판정
                    if (self.current_sector == 0 and next_sector == 1) or \
                       (self.current_sector == 1 and next_sector == 2) or \
                       (self.current_sector == 2 and next_sector == 3) or \
                       (self.current_sector == 3 and next_sector == 0):
                        
                        self.progress_gauge = min(100.0, self.progress_gauge + 3.5)
                        self.visual_angle += 0.4
                        self.spin_feedback_timer = 10
                        self.current_sector = next_sector
                    elif self.current_sector != next_sector:
                        self.current_sector = next_sector
            else:
                self.current_sector = -1
                if self.progress_gauge > 0:
                    self.progress_gauge = max(0.0, self.progress_gauge - 0.15)
                    self.visual_angle -= 0.02
                    
            # 승리/실패 조건 분기
            if self.progress_gauge >= 100.0:
                self.state = "SUCCESS"
                settings = get_main_val('settings')
                if settings and hasattr(settings, 'resources_game') and settings.resources_game:
                    res = settings.resources_game.resources
                    for k in res:
                        res[k] = 1
            elif self.elapsed_time >= self.limit_time:
                self.state = "SELECT_SACRIFICE"
                
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        from main import settings, go_to_minigames, play_sfx, keyboard_sfx
        
        # 일시정지나 비활성 시 공통 처리
        if self.state in ["SUCCESS", "FAIL"]:
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
            
        if self.state == "SELECT_SACRIFICE":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_crew_idx = (self.selected_crew_idx - 1) % len(self.crew_list)
                    play_sfx("sfx_click")
                elif event.key == pygame.K_DOWN:
                    self.selected_crew_idx = (self.selected_crew_idx + 1) % len(self.crew_list)
                    play_sfx("sfx_click")
                elif event.key == pygame.K_RETURN:
                    self.state = "FAIL" # 최종 실패 판정으로 전환
                    play_sfx("sfx_end")
            return
            
        # 플레이 중 ESC 처리
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                play_sfx("sfx_end")
                go_to_minigames()
                
    def draw(self, surface):
        from main import settings, WHITE, get_scaled_font
        
        # 1000x700 가상 해상도 드로잉
        virtual_surf = pygame.Surface((1000, 700))
        virtual_surf.fill(self.DARK_MINT)
        
        # 기본 HUD 및 텍스트 그리기
        draw_terminal_hud(virtual_surf, "STAGE 9 - RETRO-ROCKET LANDING", self.limit_time, self.elapsed_time, self.MINT)
        virtual_surf.blit(self.txt_guide_surf, (500 - self.txt_guide_surf.get_width()//2, 60))
        virtual_surf.blit(self.txt_job_surf, (500 - self.txt_job_surf.get_width()//2, 100))
        
        if self.state in ["PLAYING", "SUCCESS"]:
            # 1. 궤적 회전 가이드라인
            for a in range(0, 360, 15):
                rad = math.radians(a)
                gx = self.crank_center[0] + int(math.cos(rad) * self.arm_length)
                gy = self.crank_center[1] + int(math.sin(rad) * self.arm_length)
                pygame.draw.circle(virtual_surf, self.DARK_GRAY, (gx, gy), 2)
                
            handle_x = self.crank_center[0] + int(math.cos(self.visual_angle) * self.arm_length)
            handle_y = self.crank_center[1] + int(math.sin(self.visual_angle) * self.arm_length)
            
            # 2. 옛날 자동차 창문 레버(크랭크) 디자인
            pygame.draw.circle(virtual_surf, self.SHADOW_BLACK, self.crank_center, 55)
            pygame.draw.circle(virtual_surf, self.DARK_GRAY, self.crank_center, 55, 3)
            
            arm_width = 20
            perp_angle = self.visual_angle + math.pi / 2
            dx_perp = math.cos(perp_angle) * (arm_width // 2)
            dy_perp = math.sin(perp_angle) * (arm_width // 2)
            
            point1 = (self.crank_center[0] + dx_perp, self.crank_center[1] + dy_perp)
            point2 = (self.crank_center[0] - dx_perp, self.crank_center[1] - dy_perp)
            point3 = (handle_x - dx_perp, handle_y - dy_perp)
            point4 = (handle_x + dx_perp, handle_y + dy_perp)
            
            pygame.draw.polygon(virtual_surf, self.METAL_GRAY, [point1, point2, point3, point4])
            pygame.draw.polygon(virtual_surf, self.DARK_GRAY, [point1, point2, point3, point4], 2)
            
            pygame.draw.circle(virtual_surf, self.METAL_GRAY, self.crank_center, 22)
            pygame.draw.circle(virtual_surf, self.PLASTIC_BLACK, self.crank_center, 10)
            
            pygame.draw.circle(virtual_surf, self.PLASTIC_BLACK, (handle_x, handle_y), self.handle_radius)
            pygame.draw.circle(virtual_surf, self.METAL_GRAY, (handle_x, handle_y), self.handle_radius - 7)
            pygame.draw.circle(virtual_surf, self.DARK_GRAY, (handle_x, handle_y), self.handle_radius, 2)
            
            # 3. 작동 상태 텍스트 피드백
            if self.spin_feedback_timer > 0:
                txt_status = self.txt_status_spinning
                self.spin_feedback_timer -= 1
            else:
                txt_status = self.txt_status_hold
            virtual_surf.blit(txt_status, (self.crank_center[0] - txt_status.get_width()//2, self.crank_center[1] - 90))
            
            # 4. 하단 게이지바
            display_gauge = min(100, int(self.progress_gauge))
            pygame.draw.rect(virtual_surf, self.SHADOW_BLACK, (500 - 250, 700 - 120, 500, 25))
            pygame.draw.rect(virtual_surf, self.MINT, (500 - 250, 700 - 120, int(display_gauge * 5), 25))
            pygame.draw.rect(virtual_surf, self.WHITE, (500 - 250, 700 - 120, 500, 25), 1)
            
            txt_prog = self.font_sub.render(f"역추진 크랭크 축 연동 제어: {display_gauge}%", True, self.WHITE)
            virtual_surf.blit(txt_prog, (500 - txt_prog.get_width()//2, 700 - 90))
            
        # 5. 엔딩 분기 및 딜레마 오버레이 연출
        if self.state == "SUCCESS":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((5, 20, 10, 230))
            virtual_surf.blit(overlay, (0, 0))
            
            msg = self.font_main.render("■ 아슬아슬한 정상 착륙 (SUCCESS) ■", True, self.MINT)
            sub1 = self.font_sub.render("모든 승무원이 합심하여 레버를 당겨 선체를 제어했습니다.", True, self.WHITE)
            sub2 = self.font_sub.render("급격한 역추진 여파로 연료, 산소, 전력 등 [모든 자원이 1로 감소]합니다.", True, self.RED)
            is_campaign = False
            settings = get_main_val('settings')
            if settings and settings.is_campaign:
                is_campaign = True
                
            if is_campaign:
                sub3_text = "[ ENTER: 계속 진행 ]"
            else:
                sub3_text = "[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]"
                
            sub3 = self.font_sub.render(sub3_text, True, self.WHITE)
            
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 300))
            virtual_surf.blit(sub1, (500 - sub1.get_width()//2, 350))
            virtual_surf.blit(sub2, (500 - sub2.get_width()//2, 385))
            virtual_surf.blit(sub3, (500 - sub3.get_width()//2, 440))
            
        elif self.state == "SELECT_SACRIFICE":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((30, 5, 5, 245))
            virtual_surf.blit(overlay, (0, 0))
            
            virtual_surf.blit(self.txt_critical_fail, (500 - self.txt_critical_fail.get_width()//2, 150))
            virtual_surf.blit(self.txt_instruction, (500 - self.txt_instruction.get_width()//2, 200))
            
            for i, crew in enumerate(self.crew_list):
                if i == self.selected_crew_idx:
                    text = self.font_main.render(f"▶ {crew} 승무원 (레버를 고정하고 압착 사망) ◀", True, self.RED)
                else:
                    text = self.font_sub.render(f"  {crew} 승무원 (생존 대기)", True, self.WHITE)
                virtual_surf.blit(text, (500 - text.get_width()//2, 320 + i * 50))
                
        elif self.state == "FAIL":
            # 최종 실패 상태 연출
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((10, 0, 0, 255))
            virtual_surf.blit(overlay, (0, 0))
            
            is_campaign = False
            settings = get_main_val('settings')
            if settings and settings.is_campaign:
                is_campaign = True
                
            if is_campaign:
                sub_control_text = "[ ENTER: 계속 진행 ]"
            else:
                sub_control_text = "[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]"
                
            sub = self.font_sub.render(f"[{self.crew_list[self.selected_crew_idx]}] 승무원의 고귀한 희생으로 우주선은 안전하게 착륙했습니다.", True, self.WHITE)
            sub_control = self.font_sub.render(sub_control_text, True, self.WHITE)
            
            virtual_surf.blit(self.txt_ending_title, (500 - self.txt_ending_title.get_width()//2, 300))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 350))
            virtual_surf.blit(sub_control, (500 - sub_control.get_width()//2, 400))
            
        # 메인 화면 스케일 블릿
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    # 단독 실행 테스트 환경
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = CrankLandingGame()
    from visual_effects import TerminalFilter
    filter_crt = TerminalFilter(1000, 700)
    
    class MockSettings:
        width = 1000
        height = 700
    import sys
    sys.modules['main'] = sys.modules[__name__]
    settings = MockSettings()
    WHITE = (255, 255, 255)
    def play_sfx(name): pass
    def go_to_minigames(): pygame.quit(); sys.exit()
    keyboard_sfx = None
    
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