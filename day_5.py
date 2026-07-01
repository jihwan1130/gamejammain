import pygame
import sys
import os
import math

class Day5Manager:
    def __init__(self):
        # 1. 미니게임 불러오기 (stage_6_patient.py 의 CrewCalmGame)
        from stage_6_patient import CrewCalmGame
        self.minigame = CrewCalmGame()
        
        # 2. 자원 및 폰트 로드
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "Stage_6.png")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"Stage_6.png 로드 실패: {e}")
            
        self.init_fonts()
        self.reset()
        
    def init_fonts(self):
        # 한글 및 영문 폰트 목록 캐싱
        korean_fonts = ["nanumgothiccoding", "nanumgothic", "malgungothic", "gulim", "batang"]
        code_fonts = ["nanumgothiccoding", "consolas", "lucidaconsole", "malgungothic"]
        
        def get_sys_font(names, size, bold=False):
            available = pygame.font.get_fonts()
            for name in names:
                clean_name = name.lower().replace(" ", "")
                if clean_name in available:
                    return pygame.font.SysFont(clean_name, size, bold=bold)
            return pygame.font.Font(None, size)
            
        self.font_title = get_sys_font(korean_fonts, 32, bold=True)
        self.font_main = get_sys_font(korean_fonts, 20, bold=True)
        self.font_body = get_sys_font(korean_fonts, 18)
        self.font_button = get_sys_font(korean_fonts, 16, bold=True)
        
    def reset(self):
        self.state = "INTRO" # INTRO, GAMEPLAY, OUTRO_SUCCESS, OUTRO_FAIL
        self.minigame.reset()
        
        # 타이핑 효과용 상태 변수
        self.intro_logs = [
            "■ SYSTEM LOG: DAY 5 ■",
            "--------------------------------------------------",
            ">> 항로 진입 5일차: 외부 복사열 2200K 급증",
            ">> 선원 구역(Crew Quarters) 내 산소 포화도 저하 발생",
            ">> 폐쇄형 장비 장기 조작으로 인한 선원들의 집단 공황 발작 감지",
            "--------------------------------------------------",
            "🚨 함내 비상 경보 발령: 격리 구역 폐쇄",
            "🚨 임무: 발작을 일으키는 승무원을 조준 추적하여 진정제를 투여하십시오.",
            "--------------------------------------------------",
            "▶ [ SPACE ] 키를 눌러 진정 프로토콜을 가동하십시오."
        ]
        
        self.success_logs = [
            "■ MISSION ACCOMPLISHED ■",
            "--------------------------------------------------",
            ">> 진정제 투여 완료: 선원실 생체 바이오 리듬 안정화",
            ">> 격리 해제 및 함내 소동 무사 진압 완료",
            "--------------------------------------------------",
            "▶ [ ENTER ] 키를 눌러 다음 단계로 진행하십시오."
        ]
        
        self.fail_logs = [
            "■ MISSION FAILED ■",
            "--------------------------------------------------",
            ">> 선원 진정화 실패: 공황 발작으로 인한 내부 격실 파손 발생",
            ">> 선실 에너지 배관망 파손 및 선내 산소 누출 경보 발령",
            "--------------------------------------------------",
            "▶ [ ENTER ] 다시 시작 | [ ESC ] 미니게임 선택으로 돌아가기"
        ]
        
        self.typewriter_index = 0
        self.char_index = 0
        self.last_char_ticks = pygame.time.get_ticks()
        self.displayed_lines = []
        
    def update_typewriter(self, logs):
        # 1글자씩 출력되는 타이핑 효과
        now = pygame.time.get_ticks()
        if self.typewriter_index < len(logs):
            current_line = logs[self.typewriter_index]
            if self.char_index < len(current_line):
                # 글자 타이핑 속도 (15ms당 1글자)
                if now - self.last_char_ticks > 15:
                    self.char_index += 1
                    self.last_char_ticks = now
                    # 현재 줄까지 렌더링된 텍스트 리스트 갱신
                    temp_lines = logs[:self.typewriter_index]
                    temp_lines.append(current_line[:self.char_index])
                    self.displayed_lines = temp_lines
            else:
                self.typewriter_index += 1
                self.char_index = 0
                self.displayed_lines = logs[:self.typewriter_index]
        else:
            self.displayed_lines = logs
            
    def update(self):
        if self.state == "INTRO":
            self.update_typewriter(self.intro_logs)
        elif self.state == "GAMEPLAY":
            self.minigame.update()
            # 미니게임의 성공/실패 판정 감지
            if self.minigame.state == "SUCCESS":
                self.state = "OUTRO_SUCCESS"
                self.typewriter_index = 0
                self.char_index = 0
                self.displayed_lines = []
                # 미니게임 사운드 재생
                try:
                    from main import play_sfx
                    play_sfx("sfx_click")
                except:
                    pass
            elif self.minigame.state == "FAIL":
                self.state = "OUTRO_FAIL"
                self.typewriter_index = 0
                self.char_index = 0
                self.displayed_lines = []
                try:
                    from main import play_sfx
                    play_sfx("sfx_end")
                except:
                    pass
        elif self.state == "OUTRO_SUCCESS":
            self.update_typewriter(self.success_logs)
        elif self.state == "OUTRO_FAIL":
            self.update_typewriter(self.fail_logs)
            
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        if self.state == "INTRO":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.state = "GAMEPLAY"
                    self.minigame.reset()
                    # 타이머 초기화 (시작 시간 갱신)
                    self.minigame.start_ticks = pygame.time.get_ticks()
                elif event.key == pygame.K_ESCAPE:
                    try:
                        from main import go_to_main_menu, play_sfx
                        play_sfx("sfx_end")
                        go_to_main_menu()
                    except:
                        pass
        elif self.state == "GAMEPLAY":
            # 미니게임 이벤트 처리기 호출
            self.minigame.handle_event(event)
        elif self.state == "OUTRO_SUCCESS":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                    try:
                        from main import next_campaign_day
                        next_campaign_day()
                    except:
                        try:
                            from main import go_to_main_menu
                            go_to_main_menu()
                        except:
                            pass
        elif self.state == "OUTRO_FAIL":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    try:
                        from main import go_to_main_menu
                        go_to_main_menu()
                    except:
                        pass


    def draw(self, surface):
        if self.state == "GAMEPLAY":
            self.minigame.draw(surface)
            return
            
        # INTRO, OUTRO 디자인 그리기
        virtual_surf = pygame.Surface((1000, 700))
        
        # 1. 배경
        COLOR_THEME = (230, 160, 40) # 따뜻한 골드 옐로우
        COLOR_BG_DARK = (15, 8, 5)
        
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 가독성을 높이기 위해 어두운 반투명 적갈색 오버레이 추가
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill((24, 6, 6, 200))
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill(COLOR_BG_DARK)
            
        # 2. 더블 보더 프레임
        pygame.draw.rect(virtual_surf, COLOR_THEME, (10, 10, 980, 680), 2)
        pygame.draw.rect(virtual_surf, COLOR_THEME, (15, 15, 970, 670), 1)
        
        # 3. 타이핑 로그 본문 출력
        text_y = 120
        line_height = 36
        
        for line in self.displayed_lines:
            color = (255, 235, 215) # 부드러운 화이트
            # 경고 줄의 경우 빨간색 강조
            if "🚨" in line or "FAILED" in line:
                color = (255, 80, 80)
            elif "SUCCESS" in line or "ACCOMPLISHED" in line:
                color = (100, 240, 150)
                
            txt_surf = self.font_body.render(line, True, color)
            virtual_surf.blit(txt_surf, (80, text_y))
            text_y += line_height
            
        # 4. 장식 코너 괄호
        corner_len = 15
        white = (255, 255, 255)
        rect = pygame.Rect(10, 10, 980, 680)
        # 상좌 코너
        pygame.draw.line(virtual_surf, white, (rect.left, rect.top), (rect.left + corner_len, rect.top), 3)
        pygame.draw.line(virtual_surf, white, (rect.left, rect.top), (rect.left, rect.top + corner_len), 3)
        # 상우 코너
        pygame.draw.line(virtual_surf, white, (rect.right - 1, rect.top), (rect.right - 1 - corner_len, rect.top), 3)
        pygame.draw.line(virtual_surf, white, (rect.right - 1, rect.top), (rect.right - 1, rect.top + corner_len), 3)
        # 하좌 코너
        pygame.draw.line(virtual_surf, white, (rect.left, rect.bottom - 1), (rect.left + corner_len, rect.bottom - 1), 3)
        pygame.draw.line(virtual_surf, white, (rect.left, rect.bottom - 1), (rect.left, rect.bottom - 1 - corner_len), 3)
        # 하우 코너
        pygame.draw.line(virtual_surf, white, (rect.right - 1, rect.bottom - 1), (rect.right - 1 - corner_len, rect.bottom - 1), 3)
        pygame.draw.line(virtual_surf, white, (rect.right - 1, rect.bottom - 1), (rect.right - 1, rect.bottom - 1 - corner_len), 3)

        # 화면 크기에 스케일링하여 블릿
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = Day5Manager()
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
