import pygame
import random
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

class Day10Manager:
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

    def __init__(self):
        self.words = ["도착", "착륙", "생존", "미래", "희망", "개척", "안착", "시작"]
        self.bg_img = None
        self.ending_imgs = {}
        
        # 메인 배경화면 로드
        try:
            bg_path = os.path.join("assets", "main.png")
            if os.path.exists(bg_path):
                raw_bg = pygame.image.load(bg_path).convert()
                self.bg_img = pygame.transform.scale(raw_bg, (1000, 700))
        except Exception as e:
            print(f"main.png 로드 실패: {e}")
            
        # 엔딩 배경 에셋 시도 로드
        for ending in ["a", "b", "c", "red", "blue", "earth"]:
            try:
                img_path = os.path.join("assets", f"ending_{ending}.png")
                if os.path.exists(img_path):
                    raw_ending = pygame.image.load(img_path).convert()
                    self.ending_imgs[ending] = pygame.transform.scale(raw_ending, (1000, 700))
            except Exception as e:
                print(f"ending_{ending}.png 로드 실패: {e}")

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
        code_fonts = ["nanumgothiccoding", "consolas", "lucidaconsole", "malgungothic"]
        
        self.font_title = self.get_sys_font(korean_fonts, 26, bold=True)
        self.font_body = self.get_sys_font(korean_fonts, 20, bold=True)
        self.font_btn = self.get_sys_font(korean_fonts, 18, bold=True)
        
        self.font_main = self.get_sys_font(korean_fonts, 26, bold=True)
        self.font_sub = self.get_sys_font(korean_fonts, 16)
        self.font_input = self.get_sys_font(korean_fonts, 38, bold=True)
        self.font_label = self.get_sys_font(code_fonts, 12, bold=True)
        self.font_prompt = self.get_sys_font(korean_fonts, 32, bold=True)

    def set_ime_to_hangul(self):
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = pygame.display.get_wm_info().get("window")
                if hwnd:
                    himc = ctypes.windll.imm32.ImmGetContext(hwnd)
                    if himc:
                        ctypes.windll.imm32.ImmSetConversionStatus(himc, 1, 0)
                        ctypes.windll.imm32.ImmReleaseContext(hwnd, himc)
            except Exception as e:
                print(f"IME 한글 모드 설정 실패: {e}")

    def qwerty_to_hangul(self, text):
        text = text.lower()
        eng_to_jamo = {
            'r':'ㄱ', 's':'ㄴ', 'e':'ㄷ', 'f':'ㄹ', 'a':'ㅁ', 'q':'ㅂ', 't':'ㅅ', 'd':'ㅇ', 'w':'ㅈ', 'c':'ㅊ', 'z':'ㅋ', 'x':'ㅌ', 'v':'ㅍ', 'g':'ㅎ',
            'k':'ㅏ', 'o':'ㅐ', 'i':'ㅑ', 'j':'ㅓ', 'p':'ㅔ', 'u':'ㅕ', 'h':'ㅗ', 'y':'ㅛ', 'n':'ㅜ', 'b':'ㅠ', 'm':'ㅡ', 'l':'ㅣ'
        }
        
        cho_list = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        jung_list = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', '요', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
        jong_list = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㅈ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        
        cho_map = {v: i for i, v in enumerate(cho_list)}
        jung_map = {v: i for i, v in enumerate(jung_list)}
        
        double_jung = {
            ('ㅗ', 'ㅏ'): 'ㅘ', ('ㅗ', 'ㅐ'): 'ㅙ', ('ㅗ', 'ㅣ'): 'ㅚ',
            ('ㅜ', 'ㅓ'): 'ㅝ', ('ㅜ', 'ㅔ'): 'ㅞ', ('ㅜ', 'ㅣ'): 'ㅟ',
            ('ㅡ', 'ㅣ'): 'ㅢ'
        }
        double_jong = {
            ('ㄱ', 'ㅅ'): 'ㄳ',
            ('ㄴ', 'ㅈ'): 'ㅈ', ('ㄴ', 'ㅎ'): 'ㄶ',
            ('ㄹ', 'ㄱ'): 'ㄺ', ('ㄹ', 'ㅁ'): 'ㄻ', ('ㄹ', 'ㅂ'): 'ㄼ', ('ㄹ', 'ㅅ'): 'ㄽ', ('ㄹ', 'ㅌ'): 'ㄾ', ('ㄹ', 'ㅍ'): 'ㄿ', ('ㄹ', 'ㅎ'): 'ㅀ',
            ('ㅂ', 'ㅅ'): 'ㅄ'
        }
        
        jamo_seq = []
        for char in text:
            if char in eng_to_jamo:
                jamo_seq.append(eng_to_jamo[char])
            else:
                jamo_seq.append(char)
                
        result = []
        i = 0
        n = len(jamo_seq)
        
        while i < n:
            if jamo_seq[i] not in cho_map:
                result.append(jamo_seq[i])
                i += 1
                continue
                
            cho = jamo_seq[i]
            
            if i + 1 < n and jamo_seq[i+1] in jung_map:
                jung = jamo_seq[i+1]
                i_next = i + 2
                
                if i_next < n and (jung, jamo_seq[i_next]) in double_jung:
                    jung = double_jung[(jung, jamo_seq[i_next])]
                    i_next += 1
                    
                jong = ''
                if i_next < n and jamo_seq[i_next] in jong_list:
                    is_next_cho = False
                    if i_next + 1 < n and jamo_seq[i_next+1] in jung_map:
                        is_next_cho = True
                    
                    if not is_next_cho:
                        jong = jamo_seq[i_next]
                        i_next += 1
                        
                        if i_next < n and jamo_seq[i_next] in jong_list:
                            if (jong, jamo_seq[i_next]) in double_jong:
                                is_double_next_cho = False
                                if i_next + 1 < n and jamo_seq[i_next+1] in jung_map:
                                    is_double_next_cho = True
                                if not is_double_next_cho:
                                    jong = double_jong[(jong, jamo_seq[i_next])]
                                    i_next += 1
                                    
                cho_idx = cho_map[cho]
                jung_idx = jung_map[jung]
                jong_idx = jong_list.index(jong) if jong in jong_list else 0
                
                code = 0xAC00 + (cho_idx * 21 * 28) + (jung_idx * 28) + jong_idx
                result.append(chr(code))
                i = i_next
            else:
                result.append(cho)
                i += 1
                
        return "".join(result)

    def get_random_positions(self, words, min_dist=150):
        positions = []
        for word in words:
            attempts = 0
            while attempts < 100:
                x = random.randint(100, 800)
                y = random.randint(150, 450)
                is_valid = True
                for px, py in positions:
                    if ((x - px)**2 + (y - py)**2)**0.5 < min_dist:
                        is_valid = False
                        break
                if is_valid:
                    positions.append((x, y))
                    break
                attempts += 1
            if attempts >= 100:
                positions.append((random.randint(100, 800), random.randint(150, 450)))
        return positions

    def trigger_ending_unlock(self):
        self.get_main_ref()
        settings = getattr(self, 'settings', None) or get_main_val('settings')
        progress = get_main_val('progress')
        if settings and progress:
            selected = getattr(settings, 'selected_planet', 'earth2')
            if selected == "blue2":
                progress.unlock_ending("ending_a")
            elif selected == "red2":
                progress.unlock_ending("ending_b")
            else:
                progress.unlock_ending("ending_c")

    def reset(self):
        self.state = "INTRO_TEXT" # INTRO_TEXT, NAVIGATION, GLITCH_BG, WARNING_TOAST, PLAYING, FAIL, SHOW_ENDING
        self.navigation_start_ticks = 0
        self.check_count = 0
        self.incident_triggered = False
        
        self.comments = [
            "10일차 마지막 항해를 완료하였습니다.",
            "선택하신 목적지에 안전하게 접근 중입니다...",
            "행성 진입 및 착륙 절차를 개시합니다.",
            "",
            "▶ [ SPACE ] 키를 눌러 엔딩을 확인하십시오."
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
            
        # 비상 알림음 (8beep.MP3) 로드
        self.alarm_sound = None
        try:
            sound_path = os.path.join("assets", "8beep.MP3")
            if not os.path.exists(sound_path):
                sound_path = os.path.join("assets", "8beep.mp3")
            if os.path.exists(sound_path):
                self.alarm_sound = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"8beep.MP3 사운드 로드 실패: {e}")

        # 타이핑 게임 관련 변수
        self.word_data = []
        positions = self.get_random_positions(self.words)
        for i, text in enumerate(self.words):
            self.word_data.append({"text": text, "pos": positions[i], "done": False})
            
        self.user_input = ""
        self.composition_text = ""
        self.start_ticks = 0
        self.elapsed_time = 0
        self.limit_time = 20.0
        
        # IME 및 텍스트 모드는 일단 정지 상태로 시작
        try:
            pygame.key.stop_text_input()
        except:
            pass

    def start_typing_game(self):
        self.stop_all_sounds()
        self.state = "PLAYING"
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        
        # IME 모드 시작
        pygame.key.start_text_input()
        self.set_ime_to_hangul()

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
                        self.get_main_ref()
                        settings = getattr(self, 'settings', None) or get_main_val('settings')
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

    def update(self):
        self.get_main_ref()
        settings = getattr(self, 'settings', None) or get_main_val('settings')
        play_sfx = getattr(self, 'play_sfx', None) or get_main_val('play_sfx')
        
        if self.state == "INTRO_TEXT":
            self.update_typewriter(self.comments)
        elif self.state == "NAVIGATION":
            now = pygame.time.get_ticks()
            elapsed = (now - self.navigation_start_ticks) / 1000.0
            
            # 5초 도달 시 100% 확률로 고정 이벤트 발생
            expected_checks = int(elapsed // 5.0)
            if expected_checks > self.check_count and self.check_count < 1:
                self.check_count = expected_checks
                self.incident_triggered = True
                self.state = "GLITCH_BG"
                self.glitch_entered_ticks = pygame.time.get_ticks()
                if self.glitch_sound:
                    try:
                        vol = settings.volume if settings else 0.5
                        self.glitch_sound.set_volume(vol * 0.7)
                        self.glitch_sound.play(-1) # 루프 재생
                    except:
                        pass
                try:
                    if play_sfx:
                        play_sfx("sfx_crash")
                except:
                    pass
            
            if not self.incident_triggered and elapsed >= 20.0:
                self.state = "PEACEFUL_TOAST"
                self.stop_all_sounds()
                
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
                        vol = settings.volume if settings else 0.5
                        self.alarm_sound.set_volume(vol * 0.8)
                    except:
                        self.alarm_sound.set_volume(0.5)
                    try:
                        self.alarm_sound.play()
                    except:
                        pass
                try:
                    if play_sfx:
                        play_sfx("sfx_crash")
                except:
                    pass
                    
        elif self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            self.set_ime_to_hangul()
            
            if self.elapsed_time >= self.limit_time:
                self.state = "FAIL"
                pygame.key.stop_text_input()

    def handle_input(self):
        pass

    def handle_event(self, event):
        self.get_main_ref()
        settings = getattr(self, 'settings', None) or get_main_val('settings')
        vol = settings.volume if settings else 0.5
        play_sfx = getattr(self, 'play_sfx', None) or get_main_val('play_sfx')
        go_to_main_menu = getattr(self, 'go_to_main_menu', None) or get_main_val('go_to_main_menu')
        keyboard_sfx = get_main_val('keyboard_sfx')
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.stop_all_sounds()
                try:
                    pygame.key.stop_text_input()
                except:
                    pass
                if play_sfx:
                    play_sfx("sfx_end")
                if go_to_main_menu:
                    go_to_main_menu()
                return

        if self.state == "INTRO_TEXT":
            if event.type == pygame.KEYDOWN:
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
                        if play_sfx:
                            try:
                                play_sfx("sfx_click")
                            except:
                                pass
                    else:
                        # 타이핑 생략 완료
                        self.typewriter_index = len(self.comments) - 1
                        self.char_index = len(self.comments[-1])
                        self.displayed_lines = list(self.comments)
                        if play_sfx:
                            try:
                                play_sfx("sfx_click")
                            except:
                                pass
                                
        elif self.state == "WARNING_TOAST":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    self.start_typing_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
                    self.start_typing_game()
                    
        elif self.state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                    if play_sfx:
                        play_sfx("sfx_click")
                elif event.key == pygame.K_RETURN:
                    matched = False
                    converted_input = self.qwerty_to_hangul(self.user_input)
                    for w in self.word_data:
                        if (self.user_input == w["text"] or converted_input == w["text"]) and not w["done"]:
                            w["done"] = True
                            self.user_input = ""
                            if play_sfx:
                                play_sfx("sfx_click")
                            matched = True
                            break
                    if matched:
                        if all(w["done"] for w in self.word_data):
                            self.state = "SHOW_ENDING"
                            self.trigger_ending_unlock()
                            pygame.key.stop_text_input()
                    else:
                        self.user_input = ""
                        
            elif event.type == pygame.TEXTEDITING:
                self.composition_text = event.text
            elif event.type == pygame.TEXTINPUT:
                self.user_input += event.text
                self.composition_text = ""
                
        elif self.state == "FAIL":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # 단어 리스트 재배치 후 게임 재시작
                    self.word_data = []
                    positions = self.get_random_positions(self.words)
                    for i, text in enumerate(self.words):
                        self.word_data.append({"text": text, "pos": positions[i], "done": False})
                    self.user_input = ""
                    self.composition_text = ""
                    self.start_typing_game()
                    if keyboard_sfx:
                        keyboard_sfx.set_volume(vol)
                        keyboard_sfx.play()
                        
        elif self.state == "SHOW_ENDING":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if play_sfx:
                        play_sfx("sfx_end")
                    if settings:
                        settings.campaign_next_requested = True

    def draw(self, surface):
        self.get_main_ref()
        WHITE = get_main_val('WHITE', (255, 255, 255))
        settings = getattr(self, 'settings', None) or get_main_val('settings')
        
        # 색상 테마 정의
        COLOR_THEME = (230, 160, 40)
        COLOR_WORD_ACTIVE = (255, 230, 120)
        COLOR_WORD_DONE = (120, 80, 80)
        COLOR_OVERLAY = (24, 6, 6, 175)
        
        time_ms = pygame.time.get_ticks()
        pulse = (math.sin(time_ms * 0.005) + 1.0) / 2.0
        
        virtual_surf = pygame.Surface((1000, 700))
        
        # 기본 우주선 조종석 배경화면 blit
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
        else:
            virtual_surf.fill((10, 10, 15))
            
        shake_x = 0
        shake_y = 0
        
        # 1. 인트로 텍스트 연출
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
                
        # 2. NAVIGATION 모드 연출
        elif self.state == "NAVIGATION":
            blink = (pygame.time.get_ticks() // 500) % 2
            if blink:
                nav_txt = self.font_btn.render("▶ NAVIGATING - FINAL APPROACH", True, (0, 220, 100))
                virtual_surf.blit(nav_txt, (50, 50))
                
        # 3. 화면 글리치 효과음 및 글리치 드로잉
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
                
        # 4. 경고 토스트 드로잉
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
            
            header_str = "🚨 최종 접근 프로토콜 🚨"
            header_surf = self.font_title.render(header_str, True, (255, 80, 60))
            virtual_surf.blit(header_surf, (500 - header_surf.get_width() // 2, box_y + 35))
            
            warning_lines = [
                "목적지 행성 진입을 앞두고 선체 균열이 감지되었습니다.",
                "착륙 안정을 위해 조종 단어를 정확히 입력해 주십시오."
            ]
            
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
            y_offset = draw_wrapped_text(virtual_surf, warning_lines[0], self.font_body, (255, 220, 210), 500, y_offset, box_w - 60)
            y_offset += 8
            draw_wrapped_text(virtual_surf, warning_lines[1], self.font_body, (255, 220, 210), 500, y_offset, box_w - 60)
            
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
                
            btn_txt = self.font_btn.render("시작하기", True, btn_txt_color)
            virtual_surf.blit(btn_txt, (500 - btn_txt.get_width() // 2, 410 + (50 - btn_txt.get_height()) // 2))

        # 5. PLAYING 또는 FAIL 타자 게임 상태 연출
        elif self.state in ["PLAYING", "FAIL"]:
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill(COLOR_OVERLAY)
            virtual_surf.blit(dim_overlay, (0, 0))
            
            # 단어들 카드 형태로 렌더링
            for w in self.word_data:
                color = COLOR_WORD_DONE if w["done"] else COLOR_WORD_ACTIVE
                txt = self.font_main.render(w["text"], True, color)
                txt_w, txt_h = txt.get_size()
                
                card_rect = pygame.Rect(w["pos"][0] - 25, w["pos"][1] - 8, txt_w + 40, txt_h + 16)
                card_bg = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
                
                if w["done"]:
                    card_bg.fill((20, 15, 15, 120))
                    virtual_surf.blit(card_bg, card_rect.topleft)
                    pygame.draw.rect(virtual_surf, (80, 50, 50), card_rect, 1, border_radius=6)
                    
                    check_color = (100, 180, 120)
                    cx = card_rect.left + 12
                    cy = card_rect.centery
                    pygame.draw.line(virtual_surf, check_color, (cx - 4, cy), (cx - 1, cy + 3), 2)
                    pygame.draw.line(virtual_surf, check_color, (cx - 1, cy + 3), (cx + 5, cy - 4), 2)
                else:
                    bg_alpha = 110 + int(pulse * 30)
                    card_bg.fill((45, 30, 12, bg_alpha))
                    virtual_surf.blit(card_bg, card_rect.topleft)
                    
                    border_color = (
                        int(COLOR_WORD_ACTIVE[0] * (0.85 + pulse * 0.15)),
                        int(COLOR_WORD_ACTIVE[1] * (0.85 + pulse * 0.15)),
                        int(COLOR_WORD_ACTIVE[2] * (0.85 + pulse * 0.15))
                    )
                    pygame.draw.rect(virtual_surf, border_color, card_rect, 2, border_radius=6)
                    
                    dot_color = COLOR_WORD_ACTIVE
                    cx = card_rect.left + 12
                    cy = card_rect.centery
                    pygame.draw.circle(virtual_surf, dot_color, (cx, cy), 3)
                    pygame.draw.circle(virtual_surf, (dot_color[0], dot_color[1], dot_color[2], int(255 * (1 - pulse))), (cx, cy), 4 + int(pulse * 6), 1)
                    
                text_pos = (w["pos"][0] + 12, w["pos"][1])
                virtual_surf.blit(txt, text_pos)
                
                if w["done"]:
                    pygame.draw.line(virtual_surf, COLOR_WORD_DONE, (text_pos[0], text_pos[1] + txt_h // 2 + 2), (text_pos[0] + txt_w, text_pos[1] + txt_h // 2 + 2), 2)
                    
            # 키보드 입력 인터페이스 박스 렌더링
            input_rect = pygame.Rect(200, 540, 600, 80)
            input_bg = pygame.Surface((input_rect.width, input_rect.height), pygame.SRCALPHA)
            input_bg.fill((15, 10, 5, 220))
            virtual_surf.blit(input_bg, input_rect.topleft)
            pygame.draw.rect(virtual_surf, COLOR_THEME, input_rect, 2, border_radius=4)
            
            corner_len = 10
            pygame.draw.line(virtual_surf, WHITE, (input_rect.left, input_rect.top), (input_rect.left + corner_len, input_rect.top), 3)
            pygame.draw.line(virtual_surf, WHITE, (input_rect.left, input_rect.top), (input_rect.left, input_rect.top + corner_len), 3)
            pygame.draw.line(virtual_surf, WHITE, (input_rect.right - 1, input_rect.top), (input_rect.right - 1 - corner_len, input_rect.top), 3)
            pygame.draw.line(virtual_surf, WHITE, (input_rect.right - 1, input_rect.top), (input_rect.right - 1, input_rect.top + corner_len), 3)
            pygame.draw.line(virtual_surf, WHITE, (input_rect.left, input_rect.bottom - 1), (input_rect.left + corner_len, input_rect.bottom - 1), 3)
            pygame.draw.line(virtual_surf, WHITE, (input_rect.left, input_rect.bottom - 1), (input_rect.left, input_rect.bottom - 1 - corner_len), 3)
            pygame.draw.line(virtual_surf, WHITE, (input_rect.right - 1, input_rect.bottom - 1), (input_rect.right - 1 - corner_len, input_rect.bottom - 1), 3)
            pygame.draw.line(virtual_surf, WHITE, (input_rect.right - 1, input_rect.bottom - 1), (input_rect.right - 1, input_rect.bottom - 1 - corner_len), 3)
            
            lbl_surf = self.font_label.render(" COGNITIVE PACIFICATION TERMINAL ", True, COLOR_THEME, (15, 10, 5))
            virtual_surf.blit(lbl_surf, (input_rect.left + 15, input_rect.top - 6))
            
            display_text = self.qwerty_to_hangul(self.user_input + self.composition_text)
            prompt_surf = self.font_prompt.render("▶", True, COLOR_THEME)
            virtual_surf.blit(prompt_surf, (input_rect.left + 20, input_rect.top + 20))
            prompt_w = prompt_surf.get_width()
            
            text_x = input_rect.left + 20 + prompt_w + 10
            if display_text == "" and self.state == "PLAYING":
                txt_placeholder = self.font_sub.render("착륙 안정을 위한 조종 키워드를 입력하세요...", True, (100, 70, 40))
                virtual_surf.blit(txt_placeholder, (text_x, input_rect.top + 28))
            else:
                korean_user = self.qwerty_to_hangul(self.user_input)
                korean_total = display_text
                txt_user = self.font_input.render(korean_total, True, WHITE)
                virtual_surf.blit(txt_user, (text_x, input_rect.top + 16))
                
                if self.composition_text:
                    user_w = self.font_input.size(korean_user)[0]
                    total_w = self.font_input.size(korean_total)[0]
                    comp_w = total_w - user_w
                    if comp_w > 0:
                        pygame.draw.line(virtual_surf, (255, 200, 50), (text_x + user_w, input_rect.top + 58), (text_x + user_w + comp_w, input_rect.top + 58), 2)
            
            show_cursor = (pygame.time.get_ticks() // 500) % 2 == 0
            cursor_x = text_x + self.font_input.size(display_text)[0]
            if show_cursor and self.state == "PLAYING":
                pygame.draw.rect(virtual_surf, COLOR_THEME, (cursor_x, input_rect.top + 20, 14, 38))
                
            pygame.draw.rect(virtual_surf, COLOR_THEME, (10, 10, 980, 680), 2)
            pygame.draw.rect(virtual_surf, COLOR_THEME, (15, 15, 970, 670), 1)
            
            # 남은 시간 게이지바
            remain = max(0.0, self.limit_time - self.elapsed_time)
            time_ratio = remain / self.limit_time
            time_label = self.font_sub.render("TIME", True, COLOR_THEME)
            virtual_surf.blit(time_label, (30, 23))
            
            pygame.draw.rect(virtual_surf, (20, 10, 5), (80, 25, 220, 20))
            pygame.draw.rect(virtual_surf, COLOR_THEME, (80, 25, 220, 20), 1)
            
            fill_w = int(216 * time_ratio)
            if fill_w > 0:
                bar_color = COLOR_THEME
                if time_ratio <= 0.25:
                    if (pygame.time.get_ticks() // 200) % 2 == 0:
                        bar_color = (255, 100, 100)
                    else:
                        bar_color = (230, 50, 50)
                pygame.draw.rect(virtual_surf, bar_color, (82, 27, fill_w, 16))
                
            # 실패 창 연출
            if self.state == "FAIL":
                overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
                overlay.fill((10, 5, 5, 200))
                virtual_surf.blit(overlay, (0, 0))
                
                panel_w, panel_h = 550, 180
                panel_x, panel_y = 500 - panel_w // 2, 350 - panel_h // 2
                panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
                
                panel_bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                panel_bg.fill((20, 15, 15, 230))
                virtual_surf.blit(panel_bg, (panel_x, panel_y))
                
                border_color = (230, 50, 50)
                msg = self.font_main.render("🚨 착륙 보정 실패 (FAIL) 🚨", True, border_color)
                pygame.draw.rect(virtual_surf, border_color, panel_rect, 2, border_radius=8)
                
                pygame.draw.line(virtual_surf, WHITE, (panel_rect.left, panel_rect.top), (panel_rect.left + 15, panel_rect.top), 3)
                pygame.draw.line(virtual_surf, WHITE, (panel_rect.left, panel_rect.top), (panel_rect.left, panel_rect.top + 15), 3)
                
                sub_text = "[ ENTER: 다시 시도 | ESC: 메인 메뉴로 ]"
                sub = self.font_sub.render(sub_text, True, WHITE)
                
                virtual_surf.blit(msg, (500 - msg.get_width()//2, panel_y + 45))
                virtual_surf.blit(sub, (500 - sub.get_width()//2, panel_y + 110))

        # 6. SHOW_ENDING 행성별 엔딩 연출
        elif self.state == "SHOW_ENDING":
            selected = getattr(settings, 'selected_planet', 'earth2') if settings else 'earth2'
            
            # Default to Ending C: 제2의 지구 (earth2)
            ending_key = "c"
            ending_title = "■ ENDING C: 제2의 지구 (EARTH PLANET) ■"
            ending_desc1 = "우주선은 푸르고 온화한 대기를 가진 지구형 행성에 안착하였습니다."
            ending_desc2 = "인류의 새로운 역사가 이곳에서 시작됩니다."
            theme_color = (80, 240, 120)
            bg_color_overlay = (10, 40, 10, 200)

            if selected == "blue2":
                ending_key = "a"
                ending_title = "■ ENDING A: 푸른 행성의 인도자 (BLUE PLANET) ■"
                ending_desc1 = "표면 전체가 물로 뒤덮인 아름답고 신비로운 행성에 도달하였습니다."
                ending_desc2 = "심해 탐사와 수중 도시 건설을 위한 첫 걸음을 내딛습니다."
                theme_color = (60, 180, 255)
                bg_color_overlay = (10, 10, 40, 200)
            elif selected == "red2":
                ending_key = "b"
                ending_title = "■ ENDING B: 붉은 행성의 개척자 (RED PLANET) ■"
                ending_desc1 = "척박하지만 광물이 풍부한 붉은 행성에 무사히 착륙하였습니다."
                ending_desc2 = "생존을 위한 기지 건설과 자원 채굴 작업이 개시됩니다."
                theme_color = (255, 80, 60)
                bg_color_overlay = (40, 10, 10, 200)

            # 이미지 출력 시도 (a, b, c 또는 red, blue, earth 에셋 모두 호환되도록 처리)
            img_key = ending_key
            if img_key not in self.ending_imgs:
                if ending_key == "a" and "blue" in self.ending_imgs:
                    img_key = "blue"
                elif ending_key == "b" and "red" in self.ending_imgs:
                    img_key = "red"
                elif ending_key == "c" and "earth" in self.ending_imgs:
                    img_key = "earth"

            if img_key in self.ending_imgs:
                virtual_surf.blit(self.ending_imgs[img_key], (0, 0))
            elif self.bg_img:
                virtual_surf.blit(self.bg_img, (0, 0))
                overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
                overlay.fill(bg_color_overlay)
                virtual_surf.blit(overlay, (0, 0))
            else:
                virtual_surf.fill((10, 10, 20))
                overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
                overlay.fill(bg_color_overlay)
                virtual_surf.blit(overlay, (0, 0))

            panel_w, panel_h = 750, 300
            panel_x, panel_y = 500 - panel_w // 2, 350 - panel_h // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            
            panel_bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel_bg.fill((15, 15, 15, 220))
            virtual_surf.blit(panel_bg, (panel_x, panel_y))
            
            pygame.draw.rect(virtual_surf, theme_color, panel_rect, 3, border_radius=12)
            pygame.draw.rect(virtual_surf, (255, 255, 255), (panel_rect.x + 4, panel_rect.y + 4, panel_rect.width - 8, panel_rect.height - 8), 1, border_radius=8)
            
            title_surf = self.font_main.render(ending_title, True, theme_color)
            desc_surf1 = self.font_sub.render(ending_desc1, True, WHITE)
            desc_surf2 = self.font_sub.render(ending_desc2, True, WHITE)
            
            sub_text = "[ ENTER / SPACE : 캠페인 완료 ]"
            sub_surf = self.font_sub.render(sub_text, True, theme_color)
            
            virtual_surf.blit(title_surf, (500 - title_surf.get_width()//2, panel_y + 45))
            virtual_surf.blit(desc_surf1, (500 - desc_surf1.get_width()//2, panel_y + 115))
            virtual_surf.blit(desc_surf2, (500 - desc_surf2.get_width()//2, panel_y + 155))
            
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                virtual_surf.blit(sub_surf, (500 - sub_surf.get_width()//2, panel_y + 230))

        scaled_surf = pygame.transform.scale(virtual_surf, surface.get_size())
        surface.fill((0, 0, 0))
        surface.blit(scaled_surf, (shake_x, shake_y))

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = Day10Manager()
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
