import pygame
import sys
import random
import math
import os

from visual_effects import draw_terminal_hud

class AlienEncounterGame:
    def __init__(self):
        # 색상 정의
        self.BLACK = (10, 10, 15)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 80, 80)
        self.GREEN = (80, 255, 80)
        self.GRAY = (50, 50, 50)
        self.LIGHT_GRAY = (120, 100, 80)
        self.THEME_COLOR = (230, 160, 40) # 골드 옐로우
        self.THEME_TEXT = (255, 235, 215)
        
        self.init_fonts()
        
        # stranger.png 배경 이미지 로드
        self.stranger_bg = None
        try:
            stranger_path = os.path.join("assets", "stranger.png")
            if os.path.exists(stranger_path):
                raw_bg = pygame.image.load(stranger_path).convert()
                self.stranger_bg = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"Error loading stranger.png: {e}")
            
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
        self.font_main = get_sys_font(korean_fonts, 20, bold=True)
        self.font_body = get_sys_font(korean_fonts, 18)
        self.font_button = get_sys_font(korean_fonts, 16, bold=True)
        
    def reset(self):
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
        # main 모듈 및 settings 동적 로드 (순환 참조 회피)
        self.main_module = sys.modules.get('main')
        
        # 정치인 존재 여부 판정
        crew = self.get_my_crew()
        self.has_politician = "정치인" in crew
        
        # COMBAT 모드는 완전히 제거하고 NEGOTIATION 모드만 사용
        self.game_mode = "NEGOTIATION"
        self.neg_step = "MAIN" # MAIN, SACRIFICE, REWARD, REWARD_ENERGY
        self.sacrificed_crew = None
        self.chosen_reward = None
        self.reward_summary = ""
            
        # 로그 초기화 (Day5Manager 연동용)
        self.success_logs = []
        self.fail_logs = []
        self.update_log_templates()
        
    def get_my_crew(self):
        if self.main_module and hasattr(self.main_module, 'settings'):
            settings = self.main_module.settings
            if hasattr(settings, 'resources_game') and settings.resources_game:
                return settings.resources_game.my_crew
        return ["의사", "기술자", "경찰", "천문학자", "정치인"] # fallback
        
    def get_resources(self):
        if self.main_module and hasattr(self.main_module, 'settings'):
            settings = self.main_module.settings
            if hasattr(settings, 'resources_game') and settings.resources_game:
                return settings.resources_game.resources
        return {"산소": 80, "전기": 80, "정신력": 80} # fallback
        
    def update_log_templates(self):
        # 성공 시의 다이어로그 템플릿
        if self.has_politician:
            self.success_logs = [
                "■ MISSION ACCOMPLISHED (TRADE) ■",
                "--------------------------------------------------",
                ">> 외계인과의 계약 성립: 등가교환 성사",
                f">> 희생된 동료: [{self.sacrificed_crew}]" if self.sacrificed_crew and self.sacrificed_crew != "없음" else ">> 희생된 동료: 없음",
                f">> 획득한 보상: {self.reward_summary}",
                "--------------------------------------------------",
                "▶ [ ENTER ] 키를 눌러 다음 단계로 진행하십시오."
            ]
        else:
            self.success_logs = [
                "■ SYSTEM LOG (NO NEGOTIATION) ■",
                "--------------------------------------------------",
                ">> 정치인이 없어 협상이 일어나지 않았습니다.",
                ">> 다음날로 넘어가겠습니다.",
                "--------------------------------------------------",
                "▶ [ ENTER ] 키를 눌러 다음 단계로 진행하십시오."
            ]
            
        self.fail_logs = [
            "■ SYSTEM FAILURE ■",
            "--------------------------------------------------",
            ">> 협상 실패: 연결이 유실되었습니다.",
            "--------------------------------------------------",
            "▶ [ ENTER ] 다시 시작 | [ ESC ] 메인 메뉴로 돌아가기"
        ]



    def play_click_sfx(self):
        if self.main_module and hasattr(self.main_module, 'play_sfx'):
            self.main_module.play_sfx("sfx_click")
            
    def update(self):
        pass

    def handle_input(self):
        pass

    def handle_event(self, event):
        if self.state != "PLAYING":
            return
            
        if self.game_mode == "NEGOTIATION":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if self.main_module and hasattr(self.main_module, 'settings'):
                    settings = self.main_module.settings
                    vmx = int(mx * 1000 / settings.width)
                    vmy = int(my * 700 / settings.height)
                else:
                    vmx, vmy = mx, my
                    
                self.handle_click(vmx, vmy)

    def handle_click(self, vmx, vmy):
        if self.neg_step == "MAIN":
            btn1 = pygame.Rect(200, 320, 600, 60)
            btn2 = pygame.Rect(200, 410, 600, 60)
            
            if btn1.collidepoint(vmx, vmy):
                self.play_click_sfx()
                self.neg_step = "SACRIFICE"
            elif btn2.collidepoint(vmx, vmy):
                self.play_click_sfx()
                self.sacrificed_crew = "없음"
                self.reward_summary = "없음 (평화적 회피)"
                self.state = "SUCCESS"
                self.update_log_templates()
                
        elif self.neg_step == "SACRIFICE":
            # 생존 크루 리스트 획득 및 Rect 충돌 검사
            crew_list = self.get_my_crew()
            for idx, c_name in enumerate(crew_list):
                col = idx % 2
                row = idx // 2
                rx = 200 + col * 320
                ry = 280 + row * 70
                rect = pygame.Rect(rx, ry, 280, 50)
                
                if rect.collidepoint(vmx, vmy):
                    self.play_click_sfx()
                    self.sacrificed_crew = c_name
                    self.neg_step = "REWARD"
                    break
                    
        elif self.neg_step == "REWARD":
            btn1 = pygame.Rect(200, 320, 600, 60)
            btn2 = pygame.Rect(200, 410, 600, 60)
            
            if btn1.collidepoint(vmx, vmy):
                self.play_click_sfx()
                self.chosen_reward = "ALL_RESOURCES"
                self.apply_negotiation_results()
            elif btn2.collidepoint(vmx, vmy):
                self.play_click_sfx()
                self.neg_step = "REWARD_ENERGY"
                
        elif self.neg_step == "REWARD_ENERGY":
            btn1 = pygame.Rect(200, 260, 600, 60)
            btn2 = pygame.Rect(200, 350, 600, 60)
            btn3 = pygame.Rect(200, 440, 600, 60)
            
            if btn1.collidepoint(vmx, vmy):
                self.play_click_sfx()
                self.chosen_reward = "전기"
                self.apply_negotiation_results()
            elif btn2.collidepoint(vmx, vmy):
                self.play_click_sfx()
                self.chosen_reward = "산소"
                self.apply_negotiation_results()
            elif btn3.collidepoint(vmx, vmy):
                self.play_click_sfx()
                self.chosen_reward = "정신력"
                self.apply_negotiation_results()

    def apply_negotiation_results(self):
        # 1. 자원 지급
        resources = self.get_resources()
        if self.chosen_reward == "ALL_RESOURCES":
            for k in resources:
                resources[k] = min(200, resources[k] + 20)
            self.reward_summary = "모든 자원 +20"
        elif self.chosen_reward in ["전기", "산소", "정신력"]:
            resources[self.chosen_reward] = min(200, resources[self.chosen_reward] + 60)
            self.reward_summary = f"{self.chosen_reward} 에너지 +60"
            
        # 2. 크루 희생
        crew = self.get_my_crew()
        if self.sacrificed_crew in crew:
            crew.remove(self.sacrificed_crew)
            
        # 3. 상태 천이
        self.state = "SUCCESS"
        self.update_log_templates()

    def draw_retro_button(self, surface, rect, text, is_hovered):
        # 배경색
        bg_color = (25, 12, 6) if is_hovered else (15, 8, 4)
        pygame.draw.rect(surface, bg_color, rect)
        
        # 테두리
        border_col = self.THEME_COLOR if is_hovered else (100, 80, 60)
        pygame.draw.rect(surface, border_col, rect, 2)
        pygame.draw.rect(surface, border_col, (rect.x + 3, rect.y + 3, rect.width - 6, rect.height - 6), 1)
        
        # 텍스트 그리기
        txt_surf = self.font_button.render(text, True, self.THEME_TEXT)
        txt_rect = txt_surf.get_rect(center=rect.center)
        surface.blit(txt_surf, txt_rect)

    def draw(self, surface):
        # 1000x700 가상 버퍼 생성
        virtual_surf = pygame.Surface((1000, 700))
        
        if self.neg_step == "MAIN" and self.stranger_bg:
            virtual_surf.blit(self.stranger_bg, (0, 0))
            # 텍스트 가독성을 위해 반투명 어두운 오버레이 추가
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            virtual_surf.blit(overlay, (0, 0))
        else:
            virtual_surf.fill(self.BLACK)
        
        # 마우스 가상 좌표 연산
        if self.main_module and hasattr(self.main_module, 'settings'):
            settings = self.main_module.settings
            mx, my = pygame.mouse.get_pos()
            vmx = int(mx * 1000 / settings.width)
            vmy = int(my * 700 / settings.height)
        else:
            vmx, vmy = pygame.mouse.get_pos()
            
        # 더블 프레임 외곽 테두리
        pygame.draw.rect(virtual_surf, self.THEME_COLOR, (10, 10, 980, 680), 2)
        pygame.draw.rect(virtual_surf, self.THEME_COLOR, (15, 15, 970, 670), 1)
        
        # 상단 타이틀
        title = self.font_title.render("■ ALIEN ENCOUNTER - NEGOTIATION PROTOCOL ■", True, self.THEME_COLOR)
        virtual_surf.blit(title, (500 - title.get_width() // 2, 50))
        
        if self.neg_step == "MAIN":
            desc = self.font_main.render("우주선이 순항 중 외계인을 조우 했다.", True, self.THEME_TEXT)
            desc2 = self.font_main.render("외계인과 협상하여 협상 결과를 들고왔다.", True, self.THEME_TEXT)
            virtual_surf.blit(desc, (500 - desc.get_width() // 2, 160))
            virtual_surf.blit(desc2, (500 - desc2.get_width() // 2, 210))
            
            btn1_rect = pygame.Rect(200, 320, 600, 60)
            btn2_rect = pygame.Rect(200, 410, 600, 60)
            
            self.draw_retro_button(virtual_surf, btn1_rect, "1. 사람을 하나 희생시키고, 자원을 얻는다.", btn1_rect.collidepoint(vmx, vmy))
            self.draw_retro_button(virtual_surf, btn2_rect, "2. 사람을 희생시키지 않고 그냥 아무것도 받지 않는다.", btn2_rect.collidepoint(vmx, vmy))
            
        elif self.neg_step == "SACRIFICE":
            desc = self.font_main.render("희생시킬 승무원 동료를 선택하십시오.", True, self.RED)
            desc2 = self.font_body.render("※ 선택된 인원은 즉시 승무원 명단에서 제외됩니다.", True, self.THEME_TEXT)
            virtual_surf.blit(desc, (500 - desc.get_width() // 2, 160))
            virtual_surf.blit(desc2, (500 - desc2.get_width() // 2, 210))
            
            crew_list = self.get_my_crew()
            for idx, c_name in enumerate(crew_list):
                col = idx % 2
                row = idx // 2
                rx = 200 + col * 320
                ry = 280 + row * 70
                rect = pygame.Rect(rx, ry, 280, 50)
                
                self.draw_retro_button(virtual_surf, rect, c_name, rect.collidepoint(vmx, vmy))
                
        elif self.neg_step == "REWARD":
            desc = self.font_main.render(f"선택한 희생자: [{self.sacrificed_crew}]", True, self.RED)
            desc2 = self.font_main.render("외계인으로부터 거래할 기술/자원을 선택하십시오:", True, self.THEME_TEXT)
            virtual_surf.blit(desc, (500 - desc.get_width() // 2, 160))
            virtual_surf.blit(desc2, (500 - desc2.get_width() // 2, 210))
            
            btn1_rect = pygame.Rect(200, 320, 600, 60)
            btn2_rect = pygame.Rect(200, 410, 600, 60)
            
            self.draw_retro_button(virtual_surf, btn1_rect, "1. 모든 자원 +20 (산소, 전기, 정신력 전체)", btn1_rect.collidepoint(vmx, vmy))
            self.draw_retro_button(virtual_surf, btn2_rect, "2. 전기, 산소, 정신력 중 원하는 에너지 하나를 +60", btn2_rect.collidepoint(vmx, vmy))
            
        elif self.neg_step == "REWARD_ENERGY":
            desc = self.font_main.render("희생의 대가로 60만큼 보충할 에너지를 선택하십시오:", True, self.THEME_TEXT)
            virtual_surf.blit(desc, (500 - desc.get_width() // 2, 160))
            
            btn1_rect = pygame.Rect(200, 260, 600, 60)
            btn2_rect = pygame.Rect(200, 350, 600, 60)
            btn3_rect = pygame.Rect(200, 440, 600, 60)
            
            self.draw_retro_button(virtual_surf, btn1_rect, "⚡ 전기 (+60)", btn1_rect.collidepoint(vmx, vmy))
            self.draw_retro_button(virtual_surf, btn2_rect, "💨 산소 (+60)", btn2_rect.collidepoint(vmx, vmy))
            self.draw_retro_button(virtual_surf, btn3_rect, "🧠 정신력 (+60)", btn3_rect.collidepoint(vmx, vmy))
            
        # 메인 서페이스 스케일링 블릿
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)


class Day5Manager:
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
        
    def wrap_text_lines(self, lines, font, max_width):
        wrapped_lines = []
        for line in lines:
            if line.startswith("---"):
                wrapped_lines.append(line)
                continue
                
            current = ""
            for char in line:
                test = current + char
                if font.size(test)[0] <= max_width:
                    current = test
                else:
                    if current:
                        wrapped_lines.append(current)
                    current = char
            if current:
                wrapped_lines.append(current)
        return wrapped_lines
        
    def get_main_ref(self):
        settings = getattr(self, 'settings', None)
        play_sfx = getattr(self, 'play_sfx', None)
        go_to_main_menu = getattr(self, 'go_to_main_menu', None)
        play_music_track = getattr(self, 'play_music_track', None)
        stage_mappings = getattr(self, 'stage_mappings', None)
        
        if not settings or not play_sfx or not go_to_main_menu or not play_music_track or not stage_mappings:
            try:
                import sys
                main_mod = sys.modules.get('main') or sys.modules.get('__main__')
                if main_mod:
                    if not settings:
                        self.settings = getattr(main_mod, 'settings', None)
                    if not play_sfx:
                        self.play_sfx = getattr(main_mod, 'play_sfx', None)
                    if not go_to_main_menu:
                        self.go_to_main_menu = getattr(main_mod, 'go_to_main_menu', None)
                    if not play_music_track:
                        self.play_music_track = getattr(main_mod, 'play_music_track', None)
                    if not stage_mappings:
                        self.stage_mappings = getattr(main_mod, 'stage_mappings', None)
            except:
                pass
        return True

    def reset(self):
        self.state = "INTRO_TEXT" # INTRO_TEXT, NAVIGATION, GLITCH_BG, WARNING_TOAST, GAMEPLAY, SUCCESS_LOGS, FAIL_LOGS
        self.navigation_start_ticks = 0
        if self.__class__.__module__ == '__main__':
            try:
                pygame.mixer.music.load(os.path.join("assets", "engine.mp3"))
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"engine.mp3 재생 실패: {e}")
        self.check_count = 0
        self.incident_triggered = False
        
        self.minigame = AlienEncounterGame()
        self.comments = self.wrap_text_lines([
            "5일차 항해를 시작했습니다.",
            "우주선에서 발생하는 문제를 해결하고, 무사히 목적지까지 도달해주세요.",
            "",
            "▶ [ SPACE ] 키를 눌러 계속 진행하십시오."
        ], self.font_body, 760)
        
        self.typewriter_index = 0
        self.char_index = 0
        self.last_char_ticks = pygame.time.get_ticks()
        self.displayed_lines = []
        
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
            
        # 외계인 배경음 (alien.mp3) 로드
        self.alien_sound = None
        try:
            sound_path = os.path.join("assets", "alien.mp3")
            if os.path.exists(sound_path):
                self.alien_sound = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"alien.mp3 사운드 로드 실패: {e}")

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
                        settings = getattr(self, 'settings', None)
                        self.type_sound.set_volume(settings.volume if settings else 0.5)
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
        if hasattr(self, 'alien_sound') and self.alien_sound:
            try:
                self.alien_sound.stop()
            except:
                pass

    def start_minigame(self):
        self.stop_all_sounds()
        self.get_main_ref()
        
        # 정치인 존재 여부에 따라 분기 처리
        crew = self.minigame.get_my_crew()
        has_politician = "정치인" in crew
        
        if has_politician:
            self.state = "GAMEPLAY"
            self.minigame.reset()
            
            play_music_track = getattr(self, 'play_music_track', None)
            minigame_bgm = getattr(self, 'MINIGAME_MUSIC_PATH', None)
            if play_music_track and minigame_bgm:
                try:
                    play_music_track(minigame_bgm, fade_ms=0)
                except:
                    pass
        else:
            # 정치인이 없으면 즉시 SUCCESS_LOGS로 진행 (메시지 템플릿도 이에 맞게 로드됨)
            self.state = "SUCCESS_LOGS"
            self.minigame.reset()
            self.minigame.update_log_templates()
            self.minigame.success_logs = self.wrap_text_lines(self.minigame.success_logs, self.font_body, 860)
            self.typewriter_index = 0
            self.char_index = 0
            self.last_char_ticks = pygame.time.get_ticks()
            self.displayed_lines = []

    def update(self):
        self.get_main_ref()
        if self.state == "INTRO_TEXT":
            self.update_typewriter(self.comments)
        elif self.state == "NAVIGATION":
            now = pygame.time.get_ticks()
            elapsed = (now - self.navigation_start_ticks) / 1000.0
            
            # 3초 항해 후 100% 사건(외계인 습격) 발생
            if elapsed >= 3.0 and not self.incident_triggered:
                self.incident_triggered = True
                self.state = "GLITCH_BG"
                self.glitch_entered_ticks = pygame.time.get_ticks()
                if self.glitch_sound:
                    try:
                        settings = getattr(self, 'settings', None)
                        vol = settings.volume if settings else 0.5
                        self.glitch_sound.set_volume(vol * 0.7)
                        self.glitch_sound.play(-1)
                    except:
                        pass
                try:
                    play_sfx = getattr(self, 'play_sfx', None)
                    if play_sfx:
                        play_sfx("sfx_crash")
                except:
                    pass
                # alien.mp3 사운드 재생
                if self.alien_sound:
                    try:
                        settings = getattr(self, 'settings', None)
                        vol = settings.volume if settings else 0.5
                        self.alien_sound.set_volume(vol * 0.8)
                        self.alien_sound.play(-1)
                    except:
                        pass
                    
        elif self.state == "GLITCH_BG":
            now = pygame.time.get_ticks()
            if now - self.glitch_entered_ticks >= 4000:
                if self.glitch_sound:
                    try:
                        self.glitch_sound.stop()
                    except:
                        pass
                self.state = "WARNING_TOAST"
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
                if self.alarm_sound:
                    try:
                        settings = getattr(self, 'settings', None)
                        vol = settings.volume if settings else 0.5
                        self.alarm_sound.set_volume(vol * 0.8)
                    except:
                        self.alarm_sound.set_volume(0.5)
                    try:
                        self.alarm_sound.play()
                    except:
                        pass
                try:
                    play_sfx = getattr(self, 'play_sfx', None)
                    if play_sfx:
                        play_sfx("sfx_crash")
                except:
                    pass
        elif self.state == "GAMEPLAY":
            self.minigame.update()
            if self.minigame.state == "SUCCESS":
                self.stop_all_sounds()
                self.state = "SUCCESS_LOGS"
                self.minigame.update_log_templates()
                self.minigame.success_logs = self.wrap_text_lines(self.minigame.success_logs, self.font_body, 860)
                self.typewriter_index = 0
                self.char_index = 0
                self.last_char_ticks = pygame.time.get_ticks()
                self.displayed_lines = []
            elif self.minigame.state == "FAIL":
                self.stop_all_sounds()
                self.state = "FAIL_LOGS"
                self.minigame.update_log_templates()
                self.minigame.fail_logs = self.wrap_text_lines(self.minigame.fail_logs, self.font_body, 860)
                self.typewriter_index = 0
                self.char_index = 0
                self.last_char_ticks = pygame.time.get_ticks()
                self.displayed_lines = []
        elif self.state == "SUCCESS_LOGS":
            self.update_typewriter(self.minigame.success_logs)
        elif self.state == "FAIL_LOGS":
            self.update_typewriter(self.minigame.fail_logs)

    def handle_input(self):
        if self.state == "GAMEPLAY":
            self.minigame.handle_input()
            
    def handle_event(self, event):
        if self.state == "GAMEPLAY":
            self.minigame.handle_event(event)
            return
            
        self.get_main_ref()
        play_sfx = getattr(self, 'play_sfx', None)
        go_to_main_menu = getattr(self, 'go_to_main_menu', None)
        settings = getattr(self, 'settings', None)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.stop_all_sounds()
                try:
                    if play_sfx:
                        play_sfx("sfx_end")
                    if go_to_main_menu:
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
                        self.state = "NAVIGATION"
                        self.navigation_start_ticks = pygame.time.get_ticks()
                        self.check_count = 0
                        self.incident_triggered = False
                        try:
                            if play_sfx:
                                play_sfx("sfx_click")
                        except:
                            pass
                    else:
                        self.typewriter_index = len(self.comments) - 1
                        self.char_index = len(self.comments[-1])
                        self.displayed_lines = list(self.comments)
                        try:
                            if play_sfx:
                                play_sfx("sfx_click")
                        except:
                            pass
            elif self.state == "WARNING_TOAST":
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    self.start_minigame()
            elif self.state == "SUCCESS_LOGS":
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    is_finished = False
                    logs = self.minigame.success_logs
                    if self.typewriter_index >= len(logs):
                        is_finished = True
                    elif self.typewriter_index == len(logs) - 1:
                        current_line = logs[self.typewriter_index]
                        if self.char_index >= len(current_line):
                            is_finished = True
                            
                    if is_finished:
                        self.stop_all_sounds()
                        if play_sfx:
                            try:
                                play_sfx("sfx_click")
                            except:
                                pass
                        if settings:
                            settings.campaign_next_requested = True
                    else:
                        self.typewriter_index = len(logs) - 1
                        self.char_index = len(logs[-1])
                        self.displayed_lines = list(logs)
                        try:
                            if play_sfx:
                                play_sfx("sfx_click")
                        except:
                            pass
            elif self.state == "FAIL_LOGS":
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    is_finished = False
                    logs = self.minigame.fail_logs
                    if self.typewriter_index >= len(logs):
                        is_finished = True
                    elif self.typewriter_index == len(logs) - 1:
                        current_line = logs[self.typewriter_index]
                        if self.char_index >= len(current_line):
                            is_finished = True
                            
                    if is_finished:
                        self.stop_all_sounds()
                        if play_sfx:
                            try:
                                play_sfx("sfx_click")
                            except:
                                pass
                        self.reset()
                        self.state = "WARNING_TOAST"
                    else:
                        self.typewriter_index = len(logs) - 1
                        self.char_index = len(logs[-1])
                        self.displayed_lines = list(logs)
                        try:
                            if play_sfx:
                                play_sfx("sfx_click")
                        except:
                            pass
                    
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "WARNING_TOAST":
                mx, my = event.pos
                try:
                    if settings:
                        vmx = int(mx * 1000 / settings.width)
                        vmy = int(my * 700 / settings.height)
                    else:
                        vmx, vmy = mx, my
                except:
                    vmx, vmy = mx, my
                    
                btn_rect = pygame.Rect(400, 410, 200, 50)
                if btn_rect.collidepoint(vmx, vmy):
                    self.start_minigame()

    def draw(self, surface):
        self.get_main_ref()
        if self.state == "GAMEPLAY":
            self.minigame.draw(surface)
            return

        settings = getattr(self, 'settings', None)
        virtual_surf = pygame.Surface((1000, 700))
        
        if self.state in ["GLITCH_BG", "WARNING_TOAST", "SUCCESS_LOGS", "FAIL_LOGS"] and hasattr(self, 'minigame') and self.minigame.stranger_bg:
            virtual_surf.blit(self.minigame.stranger_bg, (0, 0))
            # 가독성을 위한 반투명 어두운 필터 블릿
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            virtual_surf.blit(overlay, (0, 0))
        elif self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
        else:
            virtual_surf.fill((10, 10, 15))
            
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
                
        elif self.state == "NAVIGATION":
            blink = (pygame.time.get_ticks() // 500) % 2
            if blink:
                nav_txt = self.font_btn.render("▶ NAVIGATING - SYSTEM NORMAL", True, (0, 220, 100))
                virtual_surf.blit(nav_txt, (50, 50))
                
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
            
            header_str = "🚨 외계인 조우 🚨"
            header_surf = self.font_title.render(header_str, True, (255, 80, 60))
            virtual_surf.blit(header_surf, (500 - header_surf.get_width() // 2, box_y + 35))
            
            # 정치인 생존 여부 판정
            crew = self.minigame.get_my_crew()
            has_politician = "정치인" in crew
            
            line1 = "외계인과 조우하였습니다."
            if has_politician:
                line2 = "협상 단계로 진입합니다."
            else:
                line2 = "정치인이 없어 협상이 일어나지 않았습니다. 다음날로 넘어가겠습니다."
            
            def draw_wrapped_text(surface, text, font, color, center_x, start_y, max_width, line_spacing=32):
                lines = []
                current_line = ""
                for char in text:
                    test_line = current_line + char
                    if font.size(test_line)[0] <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = char
                if current_line:
                    lines.append(current_line)
                
                y = start_y
                for line in lines:
                    surf = font.render(line, True, color)
                    surface.blit(surf, (center_x - surf.get_width() // 2, y))
                    y += line_spacing
                return y
                
            y_offset = box_y + 100
            y_offset = draw_wrapped_text(virtual_surf, line1, self.font_body, (255, 220, 210), 500, y_offset, box_w - 60)
            y_offset += 8
            draw_wrapped_text(virtual_surf, line2, self.font_body, (255, 220, 210), 500, y_offset, box_w - 60)
            
            mx, my = pygame.mouse.get_pos()
            try:
                if settings:
                    vmx = int(mx * 1000 / settings.width)
                    vmy = int(my * 700 / settings.height)
                else:
                    vmx, vmy = mx, my
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
                
            btn_label = "협상 시작" if has_politician else "확인"
            btn_txt = self.font_btn.render(btn_label, True, btn_txt_color)
            virtual_surf.blit(btn_txt, (500 - btn_txt.get_width() // 2, 410 + (50 - btn_txt.get_height()) // 2))

        elif self.state in ["SUCCESS_LOGS", "FAIL_LOGS"]:
            box_w = 920
            box_h = 460
            box_x = (1000 - box_w) // 2
            box_y = 120
            
            box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(box_surf, (10, 15, 10, 220) if self.state == "SUCCESS_LOGS" else (20, 5, 5, 220), (0, 0, box_w, box_h), border_radius=12)
            border_color = (100, 240, 150, 180) if self.state == "SUCCESS_LOGS" else (255, 80, 80, 180)
            pygame.draw.rect(box_surf, border_color, (0, 0, box_w, box_h), 2, border_radius=12)
            virtual_surf.blit(box_surf, (box_x, box_y))
            
            text_y = box_y + 30
            for line in self.displayed_lines:
                color = (215, 245, 220) if self.state == "SUCCESS_LOGS" else (255, 210, 210)
                if "▶" in line:
                    color = (100, 240, 150) if self.state == "SUCCESS_LOGS" else (255, 120, 100)
                elif "■" in line:
                    color = (100, 240, 150) if self.state == "SUCCESS_LOGS" else (255, 60, 60)
                    
                shadow_surf = self.font_body.render(line, True, (0, 0, 0))
                virtual_surf.blit(shadow_surf, (box_x + 42, text_y + 2))
                
                txt_surf = self.font_body.render(line, True, color)
                virtual_surf.blit(txt_surf, (box_x + 40, text_y))
                text_y += 34
                
        scaled_surf = pygame.transform.scale(virtual_surf, surface.get_size())
        surface.fill((0, 0, 0))
        surface.blit(scaled_surf, (shake_x, shake_y))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    
    # settings와 resources_game 모킹
    class MockResourcesGame:
        def __init__(self):
            # 원하는 시나리오 테스트를 위해 정치인을 넣거나 뺄 수 있습니다.
            self.my_crew = ["의사", "기술자", "정치인", "천문학자"]
            self.resources = {"산소": 80, "전기": 80, "정신력": 80}
            
    class MockSettings:
        width = 1000
        height = 700
        resources_game = MockResourcesGame()
        campaign_next_requested = False
        volume = 0.5
        
    class MockMainModule:
        settings = MockSettings()
        @staticmethod
        def play_sfx(name):
            print(f"[SFX] Playing: {name}")
            
    import sys
    sys.modules['main'] = MockMainModule()
    
    game = Day5Manager()
    
    # test를 위해 console/hud 관련 함수 모킹
    def mock_draw_terminal_hud(surface, text, limit_time, elapsed_time, color):
        font = pygame.font.SysFont("malgungothic", 16)
        hud_surf = font.render(f"HUD: {text} | TIME: {limit_time - elapsed_time:.1f}s", True, color)
        surface.blit(hud_surf, (20, 20))
        
    # global mock
    sys.modules['visual_effects'] = sys.modules[__name__]
    draw_terminal_hud = mock_draw_terminal_hud
    
    from visual_effects import TerminalFilter
    filter_crt = TerminalFilter(1000, 700)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
            if MockSettings.campaign_next_requested:
                print("Day 5 Campaign Next Requested! Resetting...")
                MockSettings.campaign_next_requested = False
                game.reset()
        game.update()
        game.draw(screen)
        filter_crt.apply(screen)
        pygame.display.flip()
        clock.tick(60)
