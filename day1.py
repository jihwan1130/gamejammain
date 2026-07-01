import pygame
import sys
import os

class Day1Manager:
    def __init__(self):
        self.init_fonts()
        self.reset()
        
    def init_fonts(self):
        korean_fonts = ["nanumgothiccoding", "nanumgothic", "malgungothic", "gulim", "batang"]
        
        def get_sys_font(names, size, bold=False):
            available = pygame.font.get_fonts()
            for name in names:
                clean_name = name.lower().replace(" ", "")
                if clean_name in available:
                    return pygame.font.SysFont(clean_name, size, bold=bold)
            return pygame.font.Font(None, size)
            
        self.font_title = get_sys_font(korean_fonts, 32, bold=True)
        self.font_body = get_sys_font(korean_fonts, 18)
        
    def reset(self):
        self.state = "INTRO" # INTRO, OUTRO_SUCCESS
        
        self.intro_logs = [
            "■ SYSTEM LOG: DAY 1 ■",
            "--------------------------------------------------",
            ">> 메인 컴퓨터 통신 활성화 완료",
            ">> 시스템 초기화 시퀀스 개시...",
            ">> 메인 원자로 기동 테스트: 정상 (100%)",
            ">> 생명 유지 장치 및 보조 필터 온라인 확인",
            "--------------------------------------------------",
            "🚨 시스템 부팅 중 원인 불명의 데이터 오염 징후가 검출되었습니다.",
            "🚨 메인 탐사 궤도 진입 전에 오염 제거 및 안전 필터를 복구해야 합니다.",
            "--------------------------------------------------",
            "▶ [ SPACE ] 키를 눌러 대기 정화 및 시스템 통신 점검을 시작하십시오."
        ]
        
        self.success_logs = [
            "■ COMMUNICATIONS & FILTER TEST COMPLISHED ■",
            "--------------------------------------------------",
            ">> 전 시스템 정상 동기화 완료",
            ">> 궤도 진입 전 데이터 송수신 이상 없음 확인",
            "--------------------------------------------------",
            "▶ [ ENTER ] 키를 눌러 다음 단계로 진행하십시오."
        ]
        
        self.typewriter_index = 0
        self.char_index = 0
        self.last_char_ticks = pygame.time.get_ticks()
        self.displayed_lines = []
        
    def update_typewriter(self, logs):
        now = pygame.time.get_ticks()
        if self.typewriter_index < len(logs):
            current_line = logs[self.typewriter_index]
            if self.char_index < len(current_line):
                if now - self.last_char_ticks > 15:
                    self.char_index += 1
                    self.last_char_ticks = now
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
        elif self.state == "OUTRO_SUCCESS":
            self.update_typewriter(self.success_logs)
            
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        if self.state == "INTRO":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.state = "OUTRO_SUCCESS"
                    self.typewriter_index = 0
                    self.char_index = 0
                    self.displayed_lines = []
                    try:
                        from main import play_sfx
                        play_sfx("sfx_click")
                    except:
                        pass
                elif event.key == pygame.K_ESCAPE:
                    try:
                        from main import go_to_main_menu, play_sfx
                        play_sfx("sfx_end")
                        go_to_main_menu()
                    except:
                        pass
        elif self.state == "OUTRO_SUCCESS":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                    try:
                        from main import next_campaign_day, play_sfx
                        play_sfx("sfx_click")
                        next_campaign_day()
                    except:
                        try:
                            from main import go_to_main_menu
                            go_to_main_menu()
                        except:
                            pass

    def draw(self, surface):
        # INTRO, OUTRO 디자인 그리기
        virtual_surf = pygame.Surface((1000, 700))
        
        COLOR_THEME = (0, 220, 100) # 초록색 미래형 터미널 테마
        COLOR_BG_DARK = (5, 15, 10)
        
        virtual_surf.fill(COLOR_BG_DARK)
            
        # 더블 보더 프레임
        pygame.draw.rect(virtual_surf, COLOR_THEME, (10, 10, 980, 680), 2)
        pygame.draw.rect(virtual_surf, COLOR_THEME, (15, 15, 970, 670), 1)
        
        # 타이핑 로그 본문 출력
        text_y = 120
        line_height = 36
        
        for line in self.displayed_lines:
            color = (200, 255, 220)
            if "🚨" in line or "FAILED" in line:
                color = (255, 80, 80)
            elif "SUCCESS" in line or "COMPLISHED" in line:
                color = (100, 240, 150)
                
            txt_surf = self.font_body.render(line, True, color)
            virtual_surf.blit(txt_surf, (80, text_y))
            text_y += line_height
            
        # 장식 코너 괄호
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
    game = Day1Manager()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
