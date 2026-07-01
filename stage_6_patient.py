import pygame
import sys
import random
import math
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

class CrewCalmGame:
    def __init__(self):
        # 색상 정의
        self.BLACK = (10, 10, 15)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 80, 80)
        self.GREEN = (80, 255, 80)
        self.GRAY = (50, 50, 50)
        
        # 1. 배경 이미지 로드 (환자 구역)
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "doctorhouse.png")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"doctorhouse.png 로드 실패: {e}")
            
        # 폰트 로딩 및 텍스트 캐싱 최적화
        get_scaled_font = get_main_val('get_scaled_font')
        if get_scaled_font:
            self.font = get_scaled_font(24, is_korean=True)
            self.title_font = get_scaled_font(36, is_korean=True)
        else:
            self.font = pygame.font.SysFont("malgungothic", 24)
            self.title_font = pygame.font.SysFont("malgungothic", 36, bold=True)
            
        # 정적 텍스트 렌더링 캐싱
        self.txt_gauge_label = self.font.render("진정제 주입 중...", True, self.BLACK)
        
        # 게임 상수
        self.target_radius = 45  # 기존 40에서 조금 키움
        self.max_progress = 180
        self.limit_time = 15.0  # 15초 제한시간
        
        self.reset()
        
    def reset(self):
        # 날뛰는 승무원 위치 및 움직임 매개변수
        self.target_x = 500
        self.target_y = 350
        self.angle = 0
        self.speed = 6.5  # 1000x700에 맞춰 속도 소폭 상향
        self.change_dir_timer = 0
        self.dx = 1
        self.dy = 1
        
        # 타이머 및 게이지
        self.progress = 0
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0.0
        
        self.state = "PLAYING"  # PLAYING, SUCCESS, FAIL
        self.is_tracking = False
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
            # 1. 승무원(과녁) 무작위 AI 이동 패턴
            self.change_dir_timer -= 1
            if self.change_dir_timer <= 0:
                self.change_dir_timer = random.randint(30, 60)
                self.angle = random.uniform(0, 2 * math.pi)
                self.dx = math.cos(self.angle) * self.speed
                self.dy = math.sin(self.angle) * self.speed
                
            # 위치 업데이트
            self.target_x += self.dx
            self.target_y += self.dy
            
            # 벽 충돌 이탈 방지 (1000, 700 가상 해상도 기준)
            if self.target_x < self.target_radius + 50 or self.target_x > 950 - self.target_radius:
                self.dx *= -1
                self.target_x = max(self.target_radius + 50, min(self.target_x, 950 - self.target_radius))
            if self.target_y < self.target_radius + 140 or self.target_y > 650 - self.target_radius:
                self.dy *= -1
                self.target_y = max(self.target_radius + 140, min(self.target_y, 650 - self.target_radius))
                
            # 2. 마우스 충돌 감지 (가상 좌표 기준 마우스 트래킹 판정)
            settings = get_main_val('settings')
            width = settings.width if settings else 1000
            height = settings.height if settings else 700
            
            mx, my = pygame.mouse.get_pos()
            vmx = int(mx * 1000 / width)
            vmy = int(my * 700 / height)
            
            distance = math.hypot(vmx - self.target_x, vmy - self.target_y)
            self.is_tracking = distance <= self.target_radius
            
            if self.is_tracking:
                self.progress += 3  # 과녁 안에 있으면 게이지 상승
            else:
                if self.progress > 0:
                    self.progress -= 0.5  # 벗어나면 게이지 감소
                    
            # 3. 승리 / 패배 조건 판단
            if self.progress >= self.max_progress:
                self.state = "SUCCESS"
            elif self.elapsed_time >= self.limit_time:
                self.state = "FAIL"
                
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        settings = get_main_val('settings')
        vol = settings.volume if settings else 0.5
        play_sfx = get_main_val('play_sfx')
        go_to_minigames = get_main_val('go_to_minigames') or get_main_val('go_to_main_menu')
        keyboard_sfx = get_main_val('keyboard_sfx')
        
        if self.state != "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if play_sfx:
                        play_sfx("sfx_end")
                    if go_to_minigames:
                        go_to_minigames()
                elif event.key == pygame.K_RETURN:
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
                
    def draw(self, surface):
        settings = get_main_val('settings')
        width = settings.width if settings else surface.get_width()
        height = settings.height if settings else surface.get_height()
        
        # 1000x700 가상 해상도 드로잉
        virtual_surf = pygame.Surface((1000, 700))
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 가독성을 높이기 위해 어두운 반투명 오버레이 추가
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((5, 10, 20, 160))
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill(self.BLACK)
        
        # 마우스 가상 좌표
        mx, my = pygame.mouse.get_pos()
        vmx = int(mx * 1000 / width)
        vmy = int(my * 700 / height)
        
        # 1. 상단 HUD 정보
        time_left = max(0.0, self.limit_time - self.elapsed_time)
        ui_text = self.font.render(f"남은 시간: {time_left:.1f}초 | 직업: 의사 (마우스로 승무원 추적)", True, self.WHITE)
        virtual_surf.blit(ui_text, (50, 80))
        
        # 2. 진정제 주입 게이지 바
        pygame.draw.rect(virtual_surf, self.GRAY, (500 - 150, 80, 300, 25))
        gauge_width = int((self.progress / self.max_progress) * 300)
        gauge_color = self.GREEN if self.is_tracking else self.RED
        pygame.draw.rect(virtual_surf, gauge_color, (500 - 150, 80, gauge_width, 25))
        
        # 게이지 내부 텍스트 blit
        virtual_surf.blit(self.txt_gauge_label, (500 - self.txt_gauge_label.get_width() // 2, 81))
        
        # 3. 날뛰는 승무원 (과녁) 그리기
        pygame.draw.circle(virtual_surf, self.RED, (int(self.target_x), int(self.target_y)), self.target_radius, 2)
        pygame.draw.circle(virtual_surf, self.RED, (int(self.target_x), int(self.target_y)), 8)
        
        if self.is_tracking:
            pygame.draw.circle(virtual_surf, self.GREEN, (int(self.target_x), int(self.target_y)), self.target_radius - 5, 3)
            
        # 4. 의사 주사기 커서 대용 (마우스 위치에 십자선 그리기)
        if self.state == "PLAYING":
            pygame.draw.line(virtual_surf, self.WHITE, (vmx - 15, vmy), (vmx + 15, vmy), 2)
            pygame.draw.line(virtual_surf, self.WHITE, (vmx, vmy - 15), (vmx, vmy + 15), 2)
            
        # 공통 터미널 HUD 그리기
        draw_terminal_hud(virtual_surf, "CREW PSYCHOLOGICAL CRISIS INTERVENTION", self.limit_time, self.elapsed_time, self.RED)
        
        # 결과 오버레이
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((10, 10, 15, 220))
            virtual_surf.blit(overlay, (0, 0))
            
            is_campaign = False
            settings = get_main_val('settings')
            if settings and settings.is_campaign:
                is_campaign = True
                
            if is_campaign:
                sub_success = "[ ENTER: 계속 진행 ]"
                sub_fail = "페널티: 전체 정신력 -20 | [ ENTER: 계속 진행 ]"
            else:
                sub_success = "[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]"
                sub_fail = "페널티: 전체 정신력 -20 | [ ENTER: 재시도 | ESC: 복귀 ]"
                
            if self.state == "SUCCESS":
                msg = self.title_font.render("■ 성공: 승무원을 진정시켰습니다. ■", True, self.GREEN)
                sub = self.font.render(sub_success, True, self.WHITE)
            else:
                msg = self.title_font.render("🚨 실패: 승무원의 부상이 고조되었습니다. 🚨", True, self.RED)
                sub = self.font.render(sub_fail, True, self.WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 380))
            
        # 메인 게임 스케일링 블릿
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = CrewCalmGame()
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