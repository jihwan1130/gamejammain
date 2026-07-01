import pygame
import sys
import os

class Day1Manager:
    def __init__(self):
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "main.png")
            if os.path.exists(bg_path):
                # 대형 이미지이므로 convert() 처리 후 1000x700 크기로 사전 스케일링
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
            else:
                print(f"경고: {bg_path} 파일이 존재하지 않습니다.")
        except Exception as e:
            print(f"main.png 로드 실패: {e}")
            
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
        self.font_body = get_sys_font(korean_fonts, 20, bold=True)
        
    def reset(self):
        self.state = "INTRO_TEXT" # INTRO_TEXT, BG_ONLY
        
        self.comments = [
            "1일차 항해를 시작했습니다.",
            "우주선에서 발생하는 문제를 해결하고, 무사히 목적지까지 도달해주세요.",
            "",
            "▶ [ SPACE ] 키를 눌러 계속 진행하십시오."
        ]
        
        self.typewriter_index = 0
        self.char_index = 0
        self.last_char_ticks = pygame.time.get_ticks()
        self.displayed_lines = []
        
        # 타이핑 사운드 (key2.mp3) 로드
        self.type_sound = None
        self.type_sound_channel = None
        try:
            sound_path = os.path.join("assets", "key2.mp3")
            if not os.path.exists(sound_path):
                sound_path = os.path.join("assets", "key2.MP3")
            if os.path.exists(sound_path):
                self.type_sound = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"key2.mp3 사운드 로드 실패: {e}")
            
    def update_typewriter(self, logs):
        now = pygame.time.get_ticks()
        while self.typewriter_index < len(logs):
            current_line = logs[self.typewriter_index]
            if current_line == "":
                self.typewriter_index += 1
                self.char_index = 0
                self.displayed_lines = logs[:self.typewriter_index]
                self.last_char_ticks = now
            else:
                break

        is_actively_typing = False

        if self.typewriter_index < len(logs):
            current_line = logs[self.typewriter_index]
            if self.char_index < len(current_line):
                is_actively_typing = True
                if now - self.last_char_ticks > 30: # 타이핑 속도 조절
                    self.char_index += 1
                    self.last_char_ticks = now
                    temp_lines = logs[:self.typewriter_index]
                    temp_lines.append(current_line[:self.char_index])
                    self.displayed_lines = temp_lines
            else:
                if self.typewriter_index == len(logs) - 1:
                    self.displayed_lines = logs[:self.typewriter_index + 1]
                else:
                    self.typewriter_index += 1
                    self.char_index = 0
                    self.last_char_ticks = now
                    is_actively_typing = True
        else:
            self.displayed_lines = logs

        # 글씨 타이핑 효과음 제어
        if self.type_sound:
            if is_actively_typing:
                playing = False
                if self.type_sound_channel is not None:
                    try:
                        playing = self.type_sound_channel.get_busy()
                    except:
                        pass
                
                if not playing:
                    try:
                        from main import settings
                        self.type_sound.set_volume(settings.volume)
                    except:
                        self.type_sound.set_volume(0.5)
                    try:
                        self.type_sound_channel = self.type_sound.play(loops=-1)
                    except Exception as e:
                        print(f"사운드 재생 실패: {e}")
            else:
                if self.type_sound_channel is not None:
                    try:
                        self.type_sound_channel.stop()
                    except:
                        pass
                    self.type_sound_channel = None
                    
    def update(self):
        if self.state == "INTRO_TEXT":
            self.update_typewriter(self.comments)
            
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if hasattr(self, 'type_sound_channel') and self.type_sound_channel:
                    try:
                        self.type_sound_channel.stop()
                    except:
                        pass
                    self.type_sound_channel = None
                try:
                    from main import go_to_main_menu, play_sfx
                    play_sfx("sfx_end")
                    go_to_main_menu()
                except:
                    pass
                return

            if self.state == "INTRO_TEXT":
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    # 모든 타이핑이 완료되었는지 확인
                    is_finished = False
                    if self.typewriter_index >= len(self.comments):
                        is_finished = True
                    elif self.typewriter_index == len(self.comments) - 1:
                        current_line = self.comments[self.typewriter_index]
                        if self.char_index >= len(current_line):
                            is_finished = True
                            
                    if is_finished:
                        # 타이핑 사운드 종료
                        if hasattr(self, 'type_sound_channel') and self.type_sound_channel:
                            try:
                                self.type_sound_channel.stop()
                            except:
                                pass
                            self.type_sound_channel = None
                            
                        # 멘트 없는 상태(BG_ONLY)로 전환
                        self.state = "BG_ONLY"
                        try:
                            from main import play_sfx
                            play_sfx("sfx_click")
                        except:
                            pass
                    else:
                        # 즉시 타이핑 생략 및 완료
                        self.typewriter_index = len(self.comments) - 1
                        self.char_index = len(self.comments[-1])
                        self.displayed_lines = list(self.comments)
                        try:
                            from main import play_sfx
                            play_sfx("sfx_click")
                        except:
                            pass
            elif self.state == "BG_ONLY":
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    try:
                        from main import next_campaign_day, play_sfx
                        play_sfx("sfx_click")
                        next_campaign_day()
                    except Exception as e:
                        # 단독 실행 시를 대비한 Fallback
                        print(f"next_campaign_day 호출. 에러: {e}")
                        try:
                            from main import go_to_main_menu
                            go_to_main_menu()
                        except:
                            pass

    def draw(self, surface):
        # 1000x700 가상 화면 크기로 렌더링
        virtual_surf = pygame.Surface((1000, 700))
        
        # 배경 그리기
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
        else:
            virtual_surf.fill((10, 10, 15))
            
        # INTRO_TEXT 상태일 때만 다이얼로그 박스 및 텍스트 렌더링
        if self.state == "INTRO_TEXT":
            box_w = 840
            box_h = 220
            box_x = (1000 - box_w) // 2
            box_y = 400
            
            box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            # 모던한 반투명 다크 스타일 다이얼로그 박스
            pygame.draw.rect(box_surf, (15, 8, 3, 200), (0, 0, box_w, box_h), border_radius=12)
            pygame.draw.rect(box_surf, (0, 220, 100, 180), (0, 0, box_w, box_h), 2, border_radius=12)
            virtual_surf.blit(box_surf, (box_x, box_y))
            
            # 줄별 텍스트 출력
            text_y = box_y + 30
            for line in self.displayed_lines:
                color = (245, 245, 245)
                if "▶" in line:
                    color = (100, 240, 150) # 프롬프트 색상 강조
                
                # 그림자 효과
                shadow_surf = self.font_body.render(line, True, (0, 0, 0))
                virtual_surf.blit(shadow_surf, (box_x + 42, text_y + 2))
                
                # 본문 텍스트
                txt_surf = self.font_body.render(line, True, color)
                virtual_surf.blit(txt_surf, (box_x + 40, text_y))
                text_y += 38
                
        # 최종 화면 크기에 맞춰 스케일링
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
