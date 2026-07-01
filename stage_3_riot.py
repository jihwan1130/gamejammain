import pygame, random, sys, os

class RiotPacificationGame:
    def __init__(self):
        self.words = ["냉정", "논리", "화합", "신뢰", "공존", "소통", "중재", "평화"]
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
        
        self.font_main = self.get_sys_font(korean_fonts, 26, bold=True)
        self.font_sub = self.get_sys_font(korean_fonts, 16)
        self.font_input = self.get_sys_font(korean_fonts, 38, bold=True) # 한글 깨짐 방지를 위해 한국어 지원 폰트 적용
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
                        # 1 = IME_CMODE_HANGUL (or IME_CMODE_NATIVE)
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
        jung_list = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
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
                # Fallback positions
                positions.append((random.randint(100, 800), random.randint(150, 450)))
        return positions
        
    def reset(self):
        self.word_data = []
        positions = self.get_random_positions(self.words)
        for i, text in enumerate(self.words):
            self.word_data.append({"text": text, "pos": positions[i], "done": False})
            
        self.user_input = ""
        self.composition_text = ""
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.limit_time = 10.0

        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
        # Open text input for Korean IME support
        pygame.key.start_text_input()
        self.set_ime_to_hangul()

        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            self.set_ime_to_hangul()
            
            if self.elapsed_time >= self.limit_time:
                self.state = "FAIL"
                pygame.key.stop_text_input()

                
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        from main import settings, go_to_minigames, play_sfx, keyboard_sfx
        if self.state != "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play_sfx("sfx_end")
                    pygame.key.stop_text_input()
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
                pygame.key.stop_text_input()
                go_to_minigames()
                return
            elif event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
                play_sfx("sfx_click")
            elif event.key == pygame.K_RETURN:
                matched = False
                converted_input = self.qwerty_to_hangul(self.user_input)
                for w in self.word_data:
                    if (self.user_input == w["text"] or converted_input == w["text"]) and not w["done"]:
                        w["done"] = True
                        self.user_input = ""
                        play_sfx("sfx_click")
                        matched = True
                        break
                if matched:
                    if all(w["done"] for w in self.word_data):
                        self.state = "SUCCESS"
                        pygame.key.stop_text_input()
                else:
                    self.user_input = "" # Clear on wrong input

                    
        elif event.type == pygame.TEXTEDITING:
            self.composition_text = event.text
        elif event.type == pygame.TEXTINPUT:
            self.user_input += event.text
            self.composition_text = ""
            
    def draw(self, surface):
        from main import CRT_GREEN, WHITE
        import math

        
        # 색상 테마 정의
        COLOR_THEME = (230, 160, 40)        # 따뜻한 골드/오렌지 (붉은 배경과 조화)
        COLOR_WORD_ACTIVE = (255, 230, 120) # 밝은 네온 옐로우 (높은 가독성)
        COLOR_WORD_DONE = (120, 80, 80)     # 어두운 적갈색 (완료됨)
        COLOR_OVERLAY = (24, 6, 6, 175)     # 어두운 붉은빛 반투명 오버레이
        
        # 펄스 애니메이션 계산
        time_ms = pygame.time.get_ticks()
        pulse = (math.sin(time_ms * 0.005) + 1.0) / 2.0  # 0.0 to 1.0
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        if self.bg_img:
            virtual_surf.blit(self.bg_img, (0, 0))
            # 가독성을 높이기 위해 어두운 반투명 오버레이 추가 (붉은 갈색 톤)
            dim_overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            dim_overlay.fill(COLOR_OVERLAY)
            virtual_surf.blit(dim_overlay, (0, 0))
        else:
            virtual_surf.fill((25, 10, 10))  # 단색 배경도 어두운 붉은색 톤으로 설정
        
        # Draw words (Styled as modern UI cards/badges)
        for w in self.word_data:
            color = COLOR_WORD_DONE if w["done"] else COLOR_WORD_ACTIVE
            txt = self.font_main.render(w["text"], True, color)
            txt_w, txt_h = txt.get_size()
            
            # 카드 배경 사각형 영역 정의
            card_rect = pygame.Rect(w["pos"][0] - 25, w["pos"][1] - 8, txt_w + 40, txt_h + 16)
            
            card_bg = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
            if w["done"]:
                # 완료된 카드: 조용하고 가독성 낮은 어두운 적갈색 톤
                card_bg.fill((20, 15, 15, 120))
                virtual_surf.blit(card_bg, card_rect.topleft)
                pygame.draw.rect(virtual_surf, (80, 50, 50), card_rect, 1, border_radius=6)
                
                # 완료 체크 마크 드로잉 (아이콘 스타일)
                check_color = (100, 180, 120)
                cx = card_rect.left + 12
                cy = card_rect.centery
                pygame.draw.line(virtual_surf, check_color, (cx - 4, cy), (cx - 1, cy + 3), 2)
                pygame.draw.line(virtual_surf, check_color, (cx - 1, cy + 3), (cx + 5, cy - 4), 2)
            else:
                # 진행 중인 카드: 약간 반짝이는 웜 골드빛 배경과 테두리
                bg_alpha = 110 + int(pulse * 30)
                card_bg.fill((45, 30, 12, bg_alpha))
                virtual_surf.blit(card_bg, card_rect.topleft)
                
                # 부드럽게 깜빡이는 테두리 컬러
                border_color = (
                    int(COLOR_WORD_ACTIVE[0] * (0.85 + pulse * 0.15)),
                    int(COLOR_WORD_ACTIVE[1] * (0.85 + pulse * 0.15)),
                    int(COLOR_WORD_ACTIVE[2] * (0.85 + pulse * 0.15))
                )
                pygame.draw.rect(virtual_surf, border_color, card_rect, 2, border_radius=6)
                
                # 조준점/레이더 블립 애니메이션
                dot_color = COLOR_WORD_ACTIVE
                cx = card_rect.left + 12
                cy = card_rect.centery
                pygame.draw.circle(virtual_surf, dot_color, (cx, cy), 3)
                pygame.draw.circle(virtual_surf, (dot_color[0], dot_color[1], dot_color[2], int(255 * (1 - pulse))), (cx, cy), 4 + int(pulse * 6), 1)
                
            # 단어 텍스트 블릿 (아이콘 영역을 고려해 우측으로 약간 이동)
            text_pos = (w["pos"][0] + 12, w["pos"][1])
            virtual_surf.blit(txt, text_pos)
            
            if w["done"]:
                # 완료 취소선 (가로지르는 얇은 라인)
                pygame.draw.line(virtual_surf, COLOR_WORD_DONE, (text_pos[0], text_pos[1] + txt_h // 2 + 2), (text_pos[0] + txt_w, text_pos[1] + txt_h // 2 + 2), 2)
                
        # Draw input box (키보드 입력부 디자인 개선)
        input_rect = pygame.Rect(200, 540, 600, 80)
        
        # 1. 반투명 배경 패널
        input_bg = pygame.Surface((input_rect.width, input_rect.height), pygame.SRCALPHA)
        input_bg.fill((15, 10, 5, 220))  # 어두운 엠버 톤의 반투명
        virtual_surf.blit(input_bg, input_rect.topleft)
        
        # 2. 테크니컬 디자인 테두리 및 코너 괄호
        pygame.draw.rect(virtual_surf, COLOR_THEME, input_rect, 2, border_radius=4)
        
        corner_len = 10
        # 상좌 코너
        pygame.draw.line(virtual_surf, WHITE, (input_rect.left, input_rect.top), (input_rect.left + corner_len, input_rect.top), 3)
        pygame.draw.line(virtual_surf, WHITE, (input_rect.left, input_rect.top), (input_rect.left, input_rect.top + corner_len), 3)
        # 상우 코너
        pygame.draw.line(virtual_surf, WHITE, (input_rect.right - 1, input_rect.top), (input_rect.right - 1 - corner_len, input_rect.top), 3)
        pygame.draw.line(virtual_surf, WHITE, (input_rect.right - 1, input_rect.top), (input_rect.right - 1, input_rect.top + corner_len), 3)
        # 하좌 코너
        pygame.draw.line(virtual_surf, WHITE, (input_rect.left, input_rect.bottom - 1), (input_rect.left + corner_len, input_rect.bottom - 1), 3)
        pygame.draw.line(virtual_surf, WHITE, (input_rect.left, input_rect.bottom - 1), (input_rect.left, input_rect.bottom - 1 - corner_len), 3)
        # 하우 코너
        pygame.draw.line(virtual_surf, WHITE, (input_rect.right - 1, input_rect.bottom - 1), (input_rect.right - 1 - corner_len, input_rect.bottom - 1), 3)
        pygame.draw.line(virtual_surf, WHITE, (input_rect.right - 1, input_rect.bottom - 1), (input_rect.right - 1, input_rect.bottom - 1 - corner_len), 3)
        
        # 입력창 소형 메타 텍스트 라벨 추가
        lbl_surf = self.font_label.render(" KEYBOARD INPUT INTERFACE ", True, COLOR_THEME, (15, 10, 5))
        virtual_surf.blit(lbl_surf, (input_rect.left + 15, input_rect.top - 6))
        
        # 3. 프롬프트 기호 및 텍스트 렌더링
        display_text = self.qwerty_to_hangul(self.user_input + self.composition_text)
        
        prompt_surf = self.font_prompt.render("▶", True, COLOR_THEME)
        virtual_surf.blit(prompt_surf, (input_rect.left + 20, input_rect.top + 20))
        prompt_w = prompt_surf.get_width()
        
        text_x = input_rect.left + 20 + prompt_w + 10
        if display_text == "" and self.state == "PLAYING":
            # 입력 전 플레이스홀더 출력
            txt_placeholder = self.font_sub.render("여기에 설득 단어를 입력하세요...", True, (100, 70, 40))
            virtual_surf.blit(txt_placeholder, (text_x, input_rect.top + 28))
        else:
            # 최종 변환된 한글 텍스트 드로잉
            korean_user = self.qwerty_to_hangul(self.user_input)
            korean_total = display_text
            
            txt_user = self.font_input.render(korean_total, True, WHITE)
            virtual_surf.blit(txt_user, (text_x, input_rect.top + 16))
            
            # 입력 중인(조합 중인) 부분에 대한 노란색 강조 언더라인
            if self.composition_text:
                user_w = self.font_input.size(korean_user)[0]
                total_w = self.font_input.size(korean_total)[0]
                comp_w = total_w - user_w
                if comp_w > 0:
                    pygame.draw.line(virtual_surf, (255, 200, 50), (text_x + user_w, input_rect.top + 58), (text_x + user_w + comp_w, input_rect.top + 58), 2)


        
        # 4. 블록 커서 그리기 (터미널 감성)
        show_cursor = (pygame.time.get_ticks() // 500) % 2 == 0
        cursor_x = text_x + self.font_input.size(display_text)[0]
        if show_cursor and self.state == "PLAYING":
            pygame.draw.rect(virtual_surf, COLOR_THEME, (cursor_x, input_rect.top + 20, 14, 38))
            
        # 1. 외부 프레임 테두리 (기본 HUD 스타일 유지)

        pygame.draw.rect(virtual_surf, COLOR_THEME, (10, 10, 980, 680), 2)
        pygame.draw.rect(virtual_surf, COLOR_THEME, (15, 15, 970, 670), 1)
        
        # 2. 상단 시간 표시 프로그레스바 (stage_2_gravity 스타일 일치, 노란색 테마 적용)
        remain = max(0.0, self.limit_time - self.elapsed_time)
        time_ratio = remain / self.limit_time
        
        # TIME 라벨 출력
        time_label = self.font_sub.render("TIME", True, COLOR_THEME)
        virtual_surf.blit(time_label, (30, 23))
        
        # 프로그레스바 테두리 및 배경 (어두운 배경색 적용)
        pygame.draw.rect(virtual_surf, (20, 10, 5), (80, 25, 220, 20))
        pygame.draw.rect(virtual_surf, COLOR_THEME, (80, 25, 220, 20), 1)
        
        # 게이지 채우기
        fill_w = int(216 * time_ratio)
        if fill_w > 0:
            bar_color = COLOR_THEME
            if time_ratio <= 0.25:
                if (pygame.time.get_ticks() // 200) % 2 == 0:
                    bar_color = (255, 100, 100) # 위험 경고 깜빡임
                else:
                    bar_color = (230, 50, 50)
            pygame.draw.rect(virtual_surf, bar_color, (82, 27, fill_w, 16))


        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((10, 5, 5, 200))
            virtual_surf.blit(overlay, (0, 0))
            
            # 팝업 패널 디자인 적용
            panel_w, panel_h = 550, 180
            panel_x, panel_y = 500 - panel_w // 2, 350 - panel_h // 2
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            
            panel_bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel_bg.fill((20, 15, 15, 230))
            virtual_surf.blit(panel_bg, (panel_x, panel_y))
            
            if self.state == "SUCCESS":
                border_color = (100, 240, 150)
                msg = self.font_main.render("■ 설득 완료 (SUCCESS) ■", True, border_color)
            else:
                border_color = (230, 50, 50)
                msg = self.font_main.render("🚨 설득 실패 (FAIL) 🚨", True, border_color)
                
            pygame.draw.rect(virtual_surf, border_color, panel_rect, 2, border_radius=8)
            
            # 팝업 상단 및 하단 모서리 장식 라인
            pygame.draw.line(virtual_surf, WHITE, (panel_rect.left, panel_rect.top), (panel_rect.left + 15, panel_rect.top), 3)
            pygame.draw.line(virtual_surf, WHITE, (panel_rect.left, panel_rect.top), (panel_rect.left, panel_rect.top + 15), 3)
            pygame.draw.line(virtual_surf, WHITE, (panel_rect.right - 1, panel_rect.top), (panel_rect.right - 1 - 15, panel_rect.top), 3)
            pygame.draw.line(virtual_surf, WHITE, (panel_rect.right - 1, panel_rect.top), (panel_rect.right - 1, panel_rect.top + 15), 3)
            
            sub = self.font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            
            virtual_surf.blit(msg, (500 - msg.get_width()//2, panel_y + 45))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, panel_y + 110))
            
        pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = RiotPacificationGame()
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