import pygame
import sys
import os
import math

def get_main_val(name, default=None):
    try:
        import sys
        main_mod = sys.modules.get('main') or sys.modules.get('__main__')
        if main_mod and hasattr(main_mod, name):
            return getattr(main_mod, name)
    except:
        pass
    return default

class ReverseThrustDecelerationGame:
    def __init__(self):
        self.init_fonts()
        self.reset()
        
    def get_sys_font(self, names, size, bold=False):
        available = pygame.font.get_fonts()
        for name in names:
            clean_name = name.lower().replace(" ", "")
            if clean_name in available:
                return pygame.font.SysFont(clean_name, size, bold=bold)
        return pygame.font.Font(None, size)

    def init_fonts(self):
        korean_fonts = ["nanumgothiccoding", "nanumgothic", "malgungothic", "gulim", "batang"]
        self.font_large = self.get_sys_font(korean_fonts, 24, bold=True)
        self.font_main = self.get_sys_font(korean_fonts, 20, bold=True)
        self.font_sub = self.get_sys_font(korean_fonts, 15)

    def reset(self):
        # 게이지 및 타이머 시스템 (0.0 ~ 100.0 범위)
        self.gauge = 0.0
        self.decay_rate = 16.5      # 초당 감소하는 게이지 양 (저항력 - 난이도 상승)
        self.boost_power = 3.96     # 스페이스바 1회당 최대 추진 상승량 (1.1배 상향)
        
        # 엔진 예열 효율 시스템 (꾸준한 조작 유도)
        self.warmup = 30.0          # 초기 예열값을 30%로 주어 밸런스 유지
        self.warmup_decay = 18.0    # 초당 예열 감소율
        self.warmup_gain = 7.42     # 스페이스 타건당 예열 증가량 (1.1배 상향)
        
        # 과열(Overheat) 시스템
        self.overheat_threshold = 92.0 # 과열 경고가 시작되는 지점
        self.is_overheated = False
        self.overheat_timer = 0
        self.overheat_duration = 72    # 과부하 패널티 시간 (60프레임 = 1.2초)
        
        # 기본 시간 제한
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 8.0          # 시간 제한 8초로 단축
        self.state = "PLAYING"         # PLAYING, SUCCESS, FAIL
        self.penalty_selected = None
        self.dead_crew_candidate = None
        
    def on_fail(self):
        self.penalty_selected = 1
        settings = get_main_val('settings')
        resources_game = getattr(settings, 'resources_game', None) if settings else None
        self.dead_crew_candidate = None
        if resources_game and hasattr(resources_game, 'my_crew') and len(resources_game.my_crew) > 0:
            import random as py_random
            self.dead_crew_candidate = py_random.choice(resources_game.my_crew)

    def apply_penalty(self):
        settings = get_main_val('settings')
        resources_game = getattr(settings, 'resources_game', None) if settings else None
        if not resources_game:
            return
        if hasattr(resources_game, 'my_crew') and len(resources_game.my_crew) > 0:
            if hasattr(self, 'dead_crew_candidate') and self.dead_crew_candidate in resources_game.my_crew:
                resources_game.my_crew.remove(self.dead_crew_candidate)
                print(f"[PENALTY] Landing failed. {self.dead_crew_candidate} died.")
            else:
                import random as py_random
                removed = py_random.choice(resources_game.my_crew)
                resources_game.my_crew.remove(removed)
                print(f"[PENALTY] Landing failed. {removed} died.")

    def apply_success(self):
        settings = get_main_val('settings')
        resources_game = getattr(settings, 'resources_game', None) if settings else None
        if not resources_game:
            return
        if hasattr(resources_game, 'resources'):
            for key in list(resources_game.resources.keys()):
                resources_game.resources[key] = 1
            print("[SUCCESS] Deceleration complete! All resources reduced to 1.")

    def update(self):
        if self.state != "PLAYING":
            return
            
        # 시간 계산
        self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
        
        # 엔진 예열 자연 감쇄 (초당 25%씩 식음)
        self.warmup = max(0.0, self.warmup - self.warmup_decay / 60.0)
        
        # 1. 과열(과부하) 패널티 처리
        if self.is_overheated:
            self.overheat_timer -= 1
            # 과열 중에는 게이지가 빠르게 식음 (감소)
            self.gauge = max(0.0, self.gauge - (self.decay_rate * 2.5) / 60.0)
            if self.overheat_timer <= 0:
                self.is_overheated = False
            
            # 과열 패널티 중에도 시간이 다 되면 바로 판정 돌입
            if self.elapsed_time >= self.limit_time:
                self.state = "FAIL"
                self.on_fail()
            return # 과열 중에는 아래 일반 감쇄 로직 건너뜀
            
        # 2. 실시간 게이지 자연 감소 (저항력 적용)
        if self.gauge > 0:
            self.gauge = max(0.0, self.gauge - self.decay_rate / 60.0)
            
        # 3. 시간 종료 시 최종 승리/패배 판정
        if self.elapsed_time >= self.limit_time:
            # 12.0초가 되는 시점에 압력이 정확히 80% ~ 100% 영역 안에 안착해야 성공
            if 80.0 <= self.gauge <= 100.0 and not self.is_overheated:
                self.state = "SUCCESS"
                self.apply_success()
            else:
                self.state = "FAIL"
                self.on_fail()
                    
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
            
        if self.state != "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if play_sfx:
                        play_sfx("sfx_end")
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
                go_to_minigames()
                
            elif event.key == pygame.K_SPACE:
                # 과열 상태면 스페이스바 입력 무시
                if self.is_overheated:
                    return
                
                # 예열 효율에 따른 가중 추진력 계산 (예열이 0%면 최대의 25% 출력만 가능)
                efficiency = 0.25 + 0.75 * (self.warmup / 100.0)
                actual_boost = self.boost_power * efficiency
                
                # 게이지 상승 및 예열량 누적
                self.gauge = min(100.0, self.gauge + actual_boost)
                self.warmup = min(100.0, self.warmup + self.warmup_gain)
                
                if play_sfx:
                    play_sfx("sfx_click")
                
                # 100.0%에 완전히 도달하면 제어 장치 과열 폭발 (Lock & Reset)
                if self.gauge >= 100.0:
                    self.is_overheated = True
                    self.overheat_timer = self.overheat_duration
                    if play_sfx:
                        play_sfx("sfx_fail")

    def draw(self, surface):
        from main import WHITE
        
        # 기본 가상 화면 (진한 붉은 톤)
        virtual_surf = pygame.Surface((1000, 700))
        virtual_surf.fill((25, 5, 5))
        
        # 색상 테마 정의
        COLOR_THEME = (240, 50, 50)  # 강렬한 레드 (역추진/비상 착륙 테마)
        
        # 1. 외부 프레임 테두리
        pygame.draw.rect(virtual_surf, COLOR_THEME, (10, 10, 980, 680), 2)
        pygame.draw.rect(virtual_surf, COLOR_THEME, (15, 15, 970, 670), 1)
        
        # 화면 효과: 흰색 오라 맥동(Pulsing Glow) 테두리 그리기
        glow_alpha = int(40 + 35 * math.sin(pygame.time.get_ticks() * 0.005))
        glow_surf = pygame.Surface((1000, 700), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 255, 255, glow_alpha), (15, 15, 970, 670), 2)
        virtual_surf.blit(glow_surf, (0, 0))
        
        # 화면 상단 흰색 문구 맥동 연출
        pulse = int(180 + 75 * math.sin(pygame.time.get_ticks() * 0.005))
        txt_press_fast = self.font_main.render("화면을 연타해주세요", True, (pulse, pulse, pulse))
        virtual_surf.blit(txt_press_fast, (500 - txt_press_fast.get_width() // 2, 75))

        
        # 모서리 코너 괄호 장식
        corner_len = 15
        white = (255, 255, 255)
        # 상좌 코너
        pygame.draw.line(virtual_surf, white, (10, 10), (10 + corner_len, 10), 3)
        pygame.draw.line(virtual_surf, white, (10, 10), (10, 10 + corner_len), 3)
        # 상우 코너
        pygame.draw.line(virtual_surf, white, (990, 10), (990 - corner_len, 10), 3)
        pygame.draw.line(virtual_surf, white, (990, 10), (990, 10 + corner_len), 3)
        # 하좌 코너
        pygame.draw.line(virtual_surf, white, (10, 690), (10 + corner_len, 690), 3)
        pygame.draw.line(virtual_surf, white, (10, 690), (10, 690 - corner_len), 3)
        # 하우 코너
        pygame.draw.line(virtual_surf, white, (990, 690), (990 - corner_len, 690), 3)
        pygame.draw.line(virtual_surf, white, (990, 690), (990, 690 - corner_len), 3)
        
        # 2. 상단 시간 표시 프로그레스바 (stage_2_gravity 스타일 일치, 레드 테마)
        remain = max(0.0, self.limit_time - self.elapsed_time)
        time_ratio = remain / self.limit_time
        
        # TIME 라벨 출력
        time_label = self.font_sub.render("TIME", True, COLOR_THEME)
        virtual_surf.blit(time_label, (30, 23))
        
        # 프로그레스바 테두리 및 배경 (어두운 배경색 적용)
        pygame.draw.rect(virtual_surf, (20, 5, 5), (80, 25, 220, 20))
        pygame.draw.rect(virtual_surf, COLOR_THEME, (80, 25, 220, 20), 1)
        
        # 게이지 채우기
        fill_w = int(216 * time_ratio)
        if fill_w > 0:
            bar_color = COLOR_THEME
            if time_ratio <= 0.25:
                if (pygame.time.get_ticks() // 200) % 2 == 0:
                    bar_color = (255, 100, 100) # 위험 경고 깜빡임
                else:
                    bar_color = (200, 20, 20)
            pygame.draw.rect(virtual_surf, bar_color, (82, 27, fill_w, 16))
            
        # 3. 상태에 따른 한글 경고 메시지 변화 (로컬라이징)
        if self.is_overheated:
            txt_alert = self.font_large.render("🚨 엔진 과열 경보: 제어 장치 임시 잠금 및 압력 역류 🚨", True, (255, 30, 30))
        elif self.warmup < 40.0:
            txt_alert = self.font_large.render("⚠️ 예열 부족: 엔진 제어 효율이 저하되었습니다 (예열 필요) ⚠️", True, (240, 160, 40))
        elif 80.0 <= self.gauge <= 100.0:
            txt_alert = self.font_large.render("✔ 최적 압력대 진입: 안정 궤도 영역 진입 완료 ✔", True, (100, 255, 150))
        else:
            txt_alert = self.font_large.render("역추진 압력 제어 중: 예열을 축적하여 압력을 제어하십시오", True, COLOR_THEME)
            
        txt_guide = self.font_sub.render("엔진 예열도를 유지하며 조작해 제한 시간 종료 시점에 압력을 80% ~ 100% 사이로 맞추십시오!", True, WHITE)
        virtual_surf.blit(txt_alert, (500 - txt_alert.get_width()//2, 160))
        virtual_surf.blit(txt_guide, (500 - txt_guide.get_width()//2, 230))
        
        # 현재 엔진 압력 및 최종 카운트다운 표시
        txt_countdown = self.font_main.render(f"역추진 제어 종료까지: {remain:.2f}초", True, WHITE)
        
        is_in_target = 80.0 <= self.gauge <= 100.0 and not self.is_overheated
        txt_pressure = self.font_sub.render(f"현재 역추진 압력 수치: {self.gauge:.1f}%", True, (100, 255, 150) if is_in_target else WHITE)
        
        virtual_surf.blit(txt_countdown, (500 - txt_countdown.get_width()//2, 310))
        virtual_surf.blit(txt_pressure, (500 - txt_pressure.get_width()//2, 350))
        
        # --- 4. 메인 압력 게이지 바 ---
        gauge_width = 500
        gx, gy = 500 - gauge_width//2, 420
        
        # 엔진 압력 게이지 그리기 (1번 바)
        pygame.draw.rect(virtual_surf, (15, 5, 5), (gx, gy, gauge_width, 35))
        
        # 게이지 색상 동적 변경 (일반: 빨강, 과열 임박: 주황, 과열 봉쇄: 보라/깜빡임)
        if self.is_overheated:
            bar_color = (130, 30, 160) # 과열 패널티 상태는 보라색
        elif self.gauge >= self.overheat_threshold:
            bar_color = (255, 160, 0)  # 경고 주황색
        else:
            bar_color = COLOR_THEME     # 일반 빨간색
            
        pygame.draw.rect(virtual_surf, bar_color, (gx, gy, int((self.gauge / 100.0) * gauge_width), 35))
        
        # 과열 경고선 가이드라인 표시 (92% 지점)
        line_x = gx + int((self.overheat_threshold / 100.0) * gauge_width)
        pygame.draw.line(virtual_surf, (255, 128, 0), (line_x, gy), (line_x, gy + 35), 2)
        
        # TARGET 영역 하이라이트 (80% ~ 100%) - 반투명 녹색 박스
        target_rect = pygame.Rect(gx + int(0.80 * gauge_width), gy, int(0.20 * gauge_width), 35)
        target_bg = pygame.Surface((target_rect.width, target_rect.height), pygame.SRCALPHA)
        target_bg.fill((100, 255, 150, 40)) # 아주 옅은 녹색
        virtual_surf.blit(target_bg, target_rect.topleft)
        
        # TARGET 영역 테두리 그리기
        pygame.draw.rect(virtual_surf, (100, 255, 150), target_rect, 2)
        
        # TARGET 레이블 텍스트 그리기 (안정 구역 중앙에 정렬)
        txt_target_tag = self.font_sub.render("TARGET (80~100%)", True, (100, 255, 150))
        target_center_x = gx + int(0.90 * gauge_width)
        virtual_surf.blit(txt_target_tag, (target_center_x - txt_target_tag.get_width() // 2, gy - 24))

        
        # 테두리
        pygame.draw.rect(virtual_surf, WHITE, (gx, gy, gauge_width, 35), 2)
        
        # 좌측 레이블
        txt_press_lbl = self.font_sub.render("엔진 압력", True, COLOR_THEME)
        virtual_surf.blit(txt_press_lbl, (gx - txt_press_lbl.get_width() - 15, gy + 8))
        
        # --- 5. 추진 예열 효율 게이지 바 ---
        gy_warm = gy + 50
        pygame.draw.rect(virtual_surf, (15, 10, 5), (gx, gy_warm, gauge_width, 18))
        
        # 예열 바 채우기 (피드백 오렌지 계열)
        pygame.draw.rect(virtual_surf, (240, 160, 40), (gx, gy_warm, int((self.warmup / 100.0) * gauge_width), 18))
        
        # 예열 바 테두리
        pygame.draw.rect(virtual_surf, (240, 160, 40), (gx, gy_warm, gauge_width, 18), 1)
        
        # 예열 좌측 레이블
        txt_warm_lbl = self.font_sub.render("추진 예열도", True, (240, 160, 40))
        virtual_surf.blit(txt_warm_lbl, (gx - txt_warm_lbl.get_width() - 15, gy_warm + 1))
        
        # --- 6. 결과 오버레이 다이얼로그 (캠페인 스타일 일치) ---
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((10, 5, 5, 200))
            virtual_surf.blit(overlay, (0, 0))
            
            panel_w, panel_h = 600, 220
            panel_x, panel_y = 500 - panel_w // 2, 350 - panel_h // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            
            panel_bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel_bg.fill((20, 10, 10, 230))
            virtual_surf.blit(panel_bg, (panel_x, panel_y))
            
            is_campaign = False
            settings = get_main_val('settings')
            if settings and settings.is_campaign:
                is_campaign = True
                
            if is_campaign:
                sub_text = "[ ENTER: 결과 확인 및 계속 진행 ]"
            else:
                sub_text = "[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]"
                
            if self.state == "SUCCESS":
                border_color = (100, 255, 100)
                msg = self.font_main.render("■ 역추진 브레이킹 성공! 안전 궤도 안착 완료 (SUCCESS) ■", True, border_color)
                sub_desc = self.font_sub.render("모든 자원이 1%까지 하락했습니다.", True, (200, 255, 200))
            else:
                border_color = COLOR_THEME
                msg = self.font_main.render("🚨 제어 실패: 하강 속도 제어 불능 (FAIL) 🚨", True, border_color)
                
                # 튕겨 나간 대원 안내 문구
                if hasattr(self, 'dead_crew_candidate') and self.dead_crew_candidate:
                    crew_text = f"우주선 충격으로 {self.dead_crew_candidate} 대원이 튕겨 나갔습니다."
                else:
                    crew_text = "우주선 충격으로 사람이 한 명 튕겨 나갔습니다."
                sub_desc = self.font_sub.render(crew_text, True, (255, 120, 120))
                
            pygame.draw.rect(virtual_surf, border_color, panel_rect, 2, border_radius=8)
            
            # 팝업 패널 모서리 장식
            white = (255, 255, 255)
            pygame.draw.line(virtual_surf, white, (panel_rect.left, panel_rect.top), (panel_rect.left + 15, panel_rect.top), 3)
            pygame.draw.line(virtual_surf, white, (panel_rect.left, panel_rect.top), (panel_rect.left, panel_rect.top + 15), 3)
            pygame.draw.line(virtual_surf, white, (panel_rect.right - 1, panel_rect.top), (panel_rect.right - 1 - 15, panel_rect.top), 3)
            pygame.draw.line(virtual_surf, white, (panel_rect.right - 1, panel_rect.top), (panel_rect.right - 1, panel_rect.top + 15), 3)
            
            sub = self.font_sub.render(sub_text, True, white)
            
            virtual_surf.blit(msg, (500 - msg.get_width()//2, panel_y + 45))
            virtual_surf.blit(sub_desc, (500 - sub_desc.get_width()//2, panel_y + 95))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, panel_y + 145))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = ReverseThrustDecelerationGame()
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