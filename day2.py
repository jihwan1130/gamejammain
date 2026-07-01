import pygame
import sys
import os
import random

class Day2Manager:
    def __init__(self):
        self.bg_img = None
        try:
            bg_path = os.path.join("assets", "main.png")
            if os.path.exists(bg_path):
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
            
        self.font_title = get_sys_font(korean_fonts, 26, bold=True)
        self.font_body = get_sys_font(korean_fonts, 20, bold=True)
        self.font_btn = get_sys_font(korean_fonts, 18, bold=True)
        
    def reset(self):
        self.state = "INTRO_TEXT" # INTRO_TEXT, GLITCH_BG, WARNING_TOAST
        
        self.comments = [
            "2일차 항해를 시작했습니다.",
            "우주선에서 발생하는 문제를 해결하고, 무사히 목적지까지 도달해주세요.",
            "",
            "▶ [ SPACE ] 키를 눌러 계속 진행하십시오."
        ]
        
        self.typewriter_index = 0
        self.char_index = 0
        self.last_char_ticks = pygame.time.get_ticks()
        self.displayed_lines = []
        
        # 타이머 트래킹용 변수
        self.glitch_entered_ticks = 0
        
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
            
        # 화면 노이즈 글리치 사운드 (tv_glitch.mp3) 로드
        self.glitch_sound = None
        try:
            sound_path = os.path.join("assets", "tv_glitch.mp3")
            if not os.path.exists(sound_path):
                sound_path = os.path.join("assets", "tv.mp3")
            if os.path.exists(sound_path):
                self.glitch_sound = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"글리치 사운드 로드 실패: {e}")
            
        # 비상 화재 알림음 (8beep.MP3) 로드
        self.alarm_sound = None
        try:
            sound_path = os.path.join("assets", "8beep.MP3")
            if not os.path.exists(sound_path):
                sound_path = os.path.join("assets", "8beep.mp3")
            if os.path.exists(sound_path):
                self.alarm_sound = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"8beep.MP3 사운드 로드 실패: {e}")
            
        # 이번 라운드에 배정된 랜덤 게임 및 멘트 확인
        self.assigned_game = None
        self.warning_lines = ["위험 상황이 발생했습니다.", "문제를 해결하십시오."]
        
        try:
            from main import settings
            if hasattr(settings, 'random_day_games') and "DAY_2" in settings.random_day_games:
                self.assigned_game = settings.random_day_games["DAY_2"]
        except Exception as e:
            print(f"main settings 로드 실패 (단독 실행 예상): {e}")

        # 만약 단독 실행 등으로 배정된 게임이 없다면 랜덤으로 하나 선택
        if not self.assigned_game:
            candidates = ["GRAVITY_GAME", "OVERHEAT_GAME", "ROBOT_GAME", "RIOT_GAME", "NAV_GAME", "ELECTRIC_GAME", "QUARANTINE_GAME"]
            self.assigned_game = random.choice(candidates)

        # 게임별 멘트 정의
        game_toasts = {
            "GRAVITY_GAME": ["중력장치 프로그램이 고장났습니다.", "서버를 복구하십시오."],
            "OVERHEAT_GAME": ["원자력 온도 조절 장치가 고장나 우주선이 중심을 잃었습니다.", "원자로로 이동하여 이를 수리하십시오."],
            "ROBOT_GAME": ["우주선 내 ai들이 고장나 시민들을 공격하기 시작했습니다.", "고장난 로봇들을 파괴하십시오."],
            "RIOT_GAME": ["시민들이 장기간 과도한 긴장감에 시달려 폭동이 일어났습니다.", "시민들을 진정시키십시오."],
            "NAV_GAME": ["항법 장치가 고장나 우주선이 방향을 찾을 수 없습니다.", "항법 장치를 보정하여, 우주선을 수리해주십시오."],
            "ELECTRIC_GAME": ["에너지 장치가 고장났습니다.", "고압실에 들어가 이를 수리하십시오."],
            "QUARANTINE_GAME": ["장시간의 비행 속에 승무원이 공황을 일으키기 시작했습니다.", "진정제를 투여하여 승무원을 진정시키십시오."]
        }
        self.warning_lines = game_toasts.get(self.assigned_game, self.warning_lines)

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
                if now - self.last_char_ticks > 30:
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

        # 타이핑 효과음 제어
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
                    
    def stop_all_sounds(self):
        if hasattr(self, 'type_sound_channel') and self.type_sound_channel:
            try:
                self.type_sound_channel.stop()
            except:
                pass
            self.type_sound_channel = None
        if hasattr(self, 'glitch_sound') and self.glitch_sound:
            try:
                self.glitch_sound.stop()
            except:
                pass
        if hasattr(self, 'alarm_sound') and self.alarm_sound:
            try:
                self.alarm_sound.stop()
            except:
                pass

    def start_assigned_game(self):
        self.stop_all_sounds()
        
        # 1. main.py 프레임워크를 통해 실행 중인 경우
        try:
            from main import settings, play_sfx, stage_mappings, play_music_track, SYSTEM_BGM_PATH, MINIGAME_MUSIC_PATH
            play_sfx("sfx_click")
            
            settings.state = self.assigned_game
            active_game = stage_mappings.get(self.assigned_game)
            if active_game:
                active_game.reset()
                
                # 게임별 음악 재생
                try:
                    if self.assigned_game == "ROBOT_GAME":
                        play_music_track(SYSTEM_BGM_PATH, fade_ms=0)
                    else:
                        play_music_track(MINIGAME_MUSIC_PATH, fade_ms=0)
                except Exception as e:
                    print(f"음악 재생 실패: {e}")
            return
        except Exception as e:
            print(f"main 프레임워크를 통한 전환 실패 (단독 실행 모드 시도): {e}")

        # 2. day2.py 단독 실행 시 해당 게임을 서브프로세스로 직접 실행
        game_files = {
            "GRAVITY_GAME": "stage_2_gravity.py",
            "OVERHEAT_GAME": "stage_2_overheat.py",
            "ROBOT_GAME": "stage_2_robot.py",
            "RIOT_GAME": "stage_3_riot.py",
            "NAV_GAME": "stage_4_nav.py",
            "ELECTRIC_GAME": "stage_6_electric.py",
            "QUARANTINE_GAME": "stage_6_patient.py"
        }
        target_file = game_files.get(self.assigned_game)
        if target_file:
            try:
                import subprocess
                import sys
                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), target_file)
                if not os.path.exists(script_path):
                    script_path = target_file
                    
                if os.path.exists(script_path):
                    subprocess.Popen([sys.executable, script_path])
                    pygame.quit()
                    sys.exit()
                else:
                    print(f"파일을 찾을 수 없습니다: {script_path}")
            except Exception as e:
                print(f"직접 실행 실패: {e}")

    def update(self):
        if self.state == "INTRO_TEXT":
            self.update_typewriter(self.comments)
        elif self.state == "GLITCH_BG":
            # 4초(4000ms) 대기 후 경고 창(WARNING_TOAST)으로 자동 변환
            now = pygame.time.get_ticks()
            if now - self.glitch_entered_ticks >= 4000:
                if self.glitch_sound:
                    try:
                        self.glitch_sound.stop()
                    except:
                        pass
                self.state = "WARNING_TOAST"
                # 비상 경고음 재생
                if self.alarm_sound:
                    try:
                        from main import settings
                        self.alarm_sound.set_volume(settings.volume * 0.8)
                    except:
                        self.alarm_sound.set_volume(0.5)
                    try:
                        self.alarm_sound.play()
                    except:
                        pass
                try:
                    from main import play_sfx
                    play_sfx("sfx_crash")
                except:
                    pass
                    
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.stop_all_sounds()
                try:
                    from main import go_to_main_menu, play_sfx
                    play_sfx("sfx_end")
                    go_to_main_menu()
                except:
                    pass
                return

            if self.state == "INTRO_TEXT":
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    is_finished = False
                    if self.typewriter_index >= len(self.comments):
                        is_finished = True
                    elif self.typewriter_index == len(self.comments) - 1:
                        current_line = self.comments[self.typewriter_index]
                        if self.char_index >= len(current_line):
                            is_finished = True
                            
                    if is_finished:
                        self.stop_all_sounds()
                        self.state = "GLITCH_BG"
                        self.glitch_entered_ticks = pygame.time.get_ticks()
                        if self.glitch_sound:
                            try:
                                from main import settings
                                self.glitch_sound.set_volume(settings.volume * 0.7)
                                self.glitch_sound.play(-1) # 루프 재생
                            except:
                                pass
                        try:
                            from main import play_sfx
                            play_sfx("sfx_click")
                        except:
                            pass
                    else:
                        # 타이핑 생략 완료
                        self.typewriter_index = len(self.comments) - 1
                        self.char_index = len(self.comments[-1])
                        self.displayed_lines = list(self.comments)
                        try:
                            from main import play_sfx
                            play_sfx("sfx_click")
                        except:
                            pass
            elif self.state == "WARNING_TOAST":
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    self.start_assigned_game()
                    
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "WARNING_TOAST":
                mx, my = event.pos
                try:
                    from main import settings
                    vmx = int(mx * 1000 / settings.width)
                    vmy = int(my * 700 / settings.height)
                except:
                    vmx, vmy = mx, my
                    
                # 시작하기 버튼 터치 판정
                btn_rect = pygame.Rect(400, 410, 200, 50)
                if btn_rect.collidepoint(vmx, vmy):
                    self.start_assigned_game()

    def draw(self, surface):
        # 1000x700 가상 화면에 그림
        virtual_surf = pygame.Surface((1000, 700))
        
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
        else:
            virtual_surf.fill((10, 10, 15))
            
        # 흔들림 효과 변수
        shake_x = 0
        shake_y = 0
            
        if self.state == "INTRO_TEXT":
            box_w = 840
            box_h = 220
            box_x = (1000 - box_w) // 2
            box_y = 400
            
            box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(box_surf, (15, 8, 3, 200), (0, 0, box_w, box_h), border_radius=12)
            pygame.draw.rect(box_surf, (0, 220, 100, 180), (0, 0, box_w, box_h), 2, border_radius=12)
            virtual_surf.blit(box_surf, (box_x, box_y))
            
            text_y = box_y + 30
            for line in self.displayed_lines:
                color = (245, 245, 245)
                if "▶" in line:
                    color = (100, 240, 150)
                
                shadow_surf = self.font_body.render(line, True, (0, 0, 0))
                virtual_surf.blit(shadow_surf, (box_x + 42, text_y + 2))
                
                txt_surf = self.font_body.render(line, True, color)
                virtual_surf.blit(txt_surf, (box_x + 40, text_y))
                text_y += 38
                
        elif self.state == "GLITCH_BG":
            if random.random() < 0.20:
                for _ in range(random.randint(2, 6)):
                    y = random.randint(0, 700)
                    h = random.randint(3, 16)
                    w = random.randint(150, 1000)
                    x = random.randint(0, 1000 - w)
                    noise = pygame.Surface((w, h), pygame.SRCALPHA)
                    noise.fill((230, 230, 255, random.randint(90, 170)))
                    virtual_surf.blit(noise, (x, y))
            
            if random.random() < 0.12:
                pygame.draw.line(virtual_surf, (255, 40, 40), (0, random.randint(0, 700)), (1000, random.randint(0, 700)), random.randint(1, 3))
            if random.random() < 0.12:
                pygame.draw.line(virtual_surf, (30, 255, 60), (0, random.randint(0, 700)), (1000, random.randint(0, 700)), random.randint(1, 3))
            
            if random.random() < 0.25:
                shake_x = random.choice([-6, -3, 3, 6])
                shake_y = random.choice([-4, -2, 2, 4])
                
        elif self.state == "WARNING_TOAST":
            box_w = 700
            box_h = 280
            box_x = (1000 - box_w) // 2
            box_y = (700 - box_h) // 2
            
            toast_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(toast_surf, (20, 4, 4, 235), (0, 0, box_w, box_h), border_radius=16)
            
            pygame.draw.rect(toast_surf, (255, 50, 40), (0, 0, box_w, box_h), 3, border_radius=16)
            pygame.draw.rect(toast_surf, (255, 120, 30), (4, 4, box_w - 8, box_h - 8), 1, border_radius=12)
            virtual_surf.blit(toast_surf, (box_x, box_y))
            
            header_str = "🚨 위험 상황 발생 🚨"
            header_surf = self.font_title.render(header_str, True, (255, 80, 60))
            virtual_surf.blit(header_surf, (500 - header_surf.get_width() // 2, box_y + 35))
            
            line1 = self.warning_lines[0]
            line2 = self.warning_lines[1]
            
            s_surf1 = self.font_body.render(line1, True, (255, 220, 210))
            virtual_surf.blit(s_surf1, (500 - s_surf1.get_width() // 2, box_y + 105))
            
            s_surf2 = self.font_body.render(line2, True, (255, 220, 210))
            virtual_surf.blit(s_surf2, (500 - s_surf2.get_width() // 2, box_y + 145))
            
            mx, my = pygame.mouse.get_pos()
            try:
                from main import settings
                vmx = int(mx * 1000 / settings.width)
                vmy = int(my * 700 / settings.height)
            except:
                vmx, vmy = mx, my
                
            btn_rect = pygame.Rect(400, 410, 200, 50)
            is_hovered = btn_rect.collidepoint(vmx, vmy)
            
            if is_hovered:
                pygame.draw.rect(virtual_surf, (255, 60, 40), btn_rect, border_radius=8)
                pygame.draw.rect(virtual_surf, (255, 255, 255), btn_rect, 2, border_radius=8)
                btn_txt_color = (255, 255, 255)
            else:
                pygame.draw.rect(virtual_surf, (40, 10, 10), btn_rect, border_radius=8)
                pygame.draw.rect(virtual_surf, (255, 80, 60), btn_rect, 2, border_radius=8)
                btn_txt_color = (255, 160, 140)
                
            btn_txt = self.font_btn.render("시작하기", True, btn_txt_color)
            virtual_surf.blit(btn_txt, (500 - btn_txt.get_width() // 2, 410 + (50 - btn_txt.get_height()) // 2))

        scaled_surf = pygame.transform.scale(virtual_surf, surface.get_size())
        surface.fill((0, 0, 0))
        surface.blit(scaled_surf, (shake_x, shake_y))

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = Day2Manager()
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
