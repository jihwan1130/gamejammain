import pygame
import sys
import os
import random

class Day0Manager:
    def __init__(self):
        # 1. assets\start.png 로드
        self.main_img = None
        try:
            img_path = os.path.join("assets", "start.png")
            if os.path.exists(img_path):
                # 대형 이미지이므로 convert() 처리 후 1000x700 크기로 사전 스케일링
                raw_img = pygame.image.load(img_path).convert()
                self.main_img = pygame.transform.scale(raw_img, (1000, 700))
            else:
                print(f"경고: {img_path} 파일이 존재하지 않습니다.")
        except Exception as e:
            print(f"start.png 로드 실패: {e}")
            
        # 2. tv.mp3 또는 tv_glitch.mp3 로드
        self.glitch_sound = None
        try:
            sound_path = os.path.join("assets", "tv.mp3")
            if not os.path.exists(sound_path):
                sound_path = os.path.join("assets", "tv_glitch.mp3")
            if os.path.exists(sound_path):
                self.glitch_sound = pygame.mixer.Sound(sound_path)
            else:
                print(f"경고: tv.mp3 또는 tv_glitch.mp3 파일이 존재하지 않습니다.")
        except Exception as e:
            print(f"사운드 로드 실패: {e}")
            
        # 3. key2.mp3 또는 key2.MP3 로드
        self.type_sound = None
        self.type_sound_channel = None
        try:
            sound_path = os.path.join("assets", "key2.mp3")
            if not os.path.exists(sound_path):
                sound_path = os.path.join("assets", "key2.MP3")
            if os.path.exists(sound_path):
                self.type_sound = pygame.mixer.Sound(sound_path)
            else:
                print(f"경고: key2.mp3 또는 key2.MP3 파일이 존재하지 않습니다.")
        except Exception as e:
            print(f"key2.mp3 사운드 로드 실패: {e}")
            
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
            
        self.font_body = get_sys_font(korean_fonts, 20, bold=True)
        self.font_title = get_sys_font(korean_fonts, 26, bold=True)
        
    def reset(self):
        self.state = "GLITCH" # GLITCH, MAIN_SCREEN
        self.start_ticks = pygame.time.get_ticks()
        self.glitch_duration = 2000 # 지지직 거리는 효과 (2초로 설정)
        
        # 타이핑 사운드 채널 정지
        if hasattr(self, 'type_sound_channel') and self.type_sound_channel:
            try:
                self.type_sound_channel.stop()
            except:
                pass
        self.type_sound_channel = None
        
        # tv.mp3 또는 tv_glitch.mp3 루프 재생 (DAY_0 진입 시에만 재생)
        is_active = False
        try:
            from main import settings
            if settings.state == "DAY_0":
                is_active = True
        except:
            is_active = True # 단독 실행 대비
            
        if is_active and self.glitch_sound:
            try:
                from main import settings
                self.glitch_sound.set_volume(settings.volume)
            except:
                self.glitch_sound.set_volume(0.5)
            self.glitch_sound.play(-1)
        
        self.comments = [
            "▶ [ SPACE ] 키를 눌러 진행하십시오.",
            "",
            "2136년 지구는 멸종 위기에 처했습니다.",
            "당신의 미래호 우주선의 함장으로 우주선에 탑승 시킬",
            "사람들과 자원을 확보하여 우주선에 탑승하여 주십시오.",
            "",
            "... ... ...",
            "",
            "부디 무사히 탈출하십시오."
        ]
        
        self.typewriter_index = 0
        self.char_index = 0
        self.last_char_ticks = pygame.time.get_ticks()
        self.displayed_lines = []
        self.pause_indices = {0, 4, 6, 8} # 대화 그룹화 및 정지 지점 설정
        
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
                if now - self.last_char_ticks > 50: # 타이핑 속도 조절 (2배 느리게)
                    self.char_index += 1
                    self.last_char_ticks = now
                    temp_lines = logs[:self.typewriter_index]
                    temp_lines.append(current_line[:self.char_index])
                    self.displayed_lines = temp_lines
            else:
                # Fully typed. Check if we need to pause here.
                if self.typewriter_index in self.pause_indices:
                    self.displayed_lines = logs[:self.typewriter_index + 1]
                else:
                    # Auto-advance immediately if this line is not a pause point
                    self.typewriter_index += 1
                    self.char_index = 0
                    self.last_char_ticks = now
                    is_actively_typing = True
        else:
            self.displayed_lines = logs

        # 글씨 재생 여부에 따라 루프 재생/정지 제어
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
            
    def show_summary(self, collected_crew, collected_resources, final_crew, final_resources):
        self.state = "SUMMARY"
        self.start_ticks = pygame.time.get_ticks()
        
        # Format collected crew list
        crew_res = ", ".join(collected_crew) if collected_crew else "없음"
        
        # Format collected resources
        res_res = ", ".join([f"{k} +{v}" for k, v in collected_resources.items() if v > 0])
        if not res_res:
            res_res = "없음"
            
        # Format final crew list
        final_crew_str = ", ".join(final_crew)
        
        # Format final resources
        final_res_str = ", ".join([f"{k}: {v}" for k, v in final_resources.items()])
        
        # 멘트 설정
        self.comments = [
            "긴급 지구 탈출",
            f"구출 인원: {crew_res}",
            f"획득 자원: {res_res}",
            f"총 자원: 인원 ({final_crew_str}) / 자원 ({final_res_str})",
            "",
            "Day 0 End",
            "다음날로 넘어가시겠습니까?"
        ]
        
        self.typewriter_index = 0
        self.char_index = 0
        self.last_char_ticks = pygame.time.get_ticks()
        self.displayed_lines = []
        self.pause_indices = set() # 요약 화면은 중간 정지 없이 끝까지 출력
        
        # BGM 정지
        try:
            pygame.mixer.music.stop()
        except:
            pass

    def update(self):
        now = pygame.time.get_ticks()
        if self.state == "GLITCH":
            if now - self.start_ticks >= self.glitch_duration:
                self.state = "MAIN_SCREEN"
                if self.glitch_sound:
                    self.glitch_sound.stop()
                self.typewriter_index = 0
                self.char_index = 0
                self.displayed_lines = []
                self.last_char_ticks = now
                
                # start.png 가 나타날 때 orbit.mp3 BGM 재생
                try:
                    import os
                    from main import play_music_track
                    play_music_track(os.path.join("assets", "orbit.mp3"), fade_ms=500, loops=-1)
                except:
                    # 단독 실행 및 예외 대비
                    try:
                        import os
                        pygame.mixer.music.load(os.path.join("assets", "orbit.mp3"))
                        pygame.mixer.music.set_volume(0.5)
                        pygame.mixer.music.play(-1)
                    except Exception as e:
                        print(f"orbit.mp3 재생 실패: {e}")
        elif self.state in ["MAIN_SCREEN", "SUMMARY"]:
            self.update_typewriter(self.comments)
            
    def handle_input(self):
        pass
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.glitch_sound:
                self.glitch_sound.stop()
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
            
        if self.state in ["MAIN_SCREEN", "SUMMARY"]:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    # Check if the last line has finished typing, or typewriter is fully finished
                    is_last_line_finished = False
                    if self.typewriter_index >= len(self.comments):
                        is_last_line_finished = True
                    elif self.typewriter_index == len(self.comments) - 1:
                        current_line = self.comments[self.typewriter_index]
                        if self.char_index >= len(current_line):
                            is_last_line_finished = True
                            
                    if is_last_line_finished:
                        if hasattr(self, 'type_sound_channel') and self.type_sound_channel:
                            try:
                                self.type_sound_channel.stop()
                            except:
                                pass
                            self.type_sound_channel = None
                        
                        if self.state == "SUMMARY":
                            try:
                                from main import settings, play_sfx
                                play_sfx("sfx_click")
                                settings.current_day = 1
                                settings.state = "DAY_1"
                                if hasattr(settings, 'day_1_manager') and settings.day_1_manager:
                                    settings.day_1_manager.reset()
                            except Exception as e:
                                print(f"DAY_1 전환 실패: {e}")
                        else:
                            try:
                                from main import settings, play_sfx
                                play_sfx("sfx_click")
                                settings.state = "RESOURCE_GAME"
                                if hasattr(settings, 'resources_game') and settings.resources_game:
                                    settings.resources_game.reset()
                            except Exception as e:
                                print(f"RESOURCE_GAME 전환 실패: {e}")
                    else:
                        # Find the target pause index for the current sentence group
                        target_pause_index = len(self.comments) - 1
                        for idx in sorted(self.pause_indices):
                            if self.typewriter_index <= idx:
                                target_pause_index = idx
                                break
                                
                        is_typing = False
                        if self.typewriter_index < target_pause_index:
                            is_typing = True
                        else:
                            current_line = self.comments[self.typewriter_index]
                            if self.char_index < len(current_line):
                                is_typing = True
                                
                        if is_typing:
                            # Instantly complete typing for the current group up to target_pause_index
                            self.typewriter_index = target_pause_index
                            self.char_index = len(self.comments[target_pause_index])
                            self.displayed_lines = self.comments[:target_pause_index + 1]
                            try:
                                from main import play_sfx
                                play_sfx("sfx_click")
                            except:
                                pass
                        else:
                            # Already fully typed: advance to the next group
                            self.typewriter_index += 1
                            self.char_index = 0
                            self.last_char_ticks = pygame.time.get_ticks()
                            try:
                                from main import play_sfx
                                play_sfx("sfx_click")
                            except:
                                pass

    def draw(self, surface):
        virtual_surf = pygame.Surface((1000, 700))
        
        if self.state == "GLITCH":
            # 검은 화면에 지지직 거리는 효과 (노이즈, 글리치 라인, 흔들림)
            virtual_surf.fill((0, 0, 0))
            
            # 가로 노이즈 밴드
            num_bands = random.randint(6, 15)
            for _ in range(num_bands):
                y = random.randint(0, 700)
                h = random.randint(3, 30)
                gray = random.randint(20, 160)
                pygame.draw.rect(virtual_surf, (gray, gray, gray), (0, y, 1000, h))
                
            # 미세한 가로 노이즈 픽셀선들
            for _ in range(50):
                x = random.randint(0, 1000)
                y = random.randint(0, 700)
                w = random.randint(5, 80)
                h = random.randint(1, 3)
                gray = random.randint(80, 240)
                pygame.draw.rect(virtual_surf, (gray, gray, gray), (x, y, w, h))
                
            # RGB 글리치 라인
            if random.random() < 0.5:
                pygame.draw.line(virtual_surf, (0, 255, 60), (0, random.randint(0, 700)), (1000, random.randint(0, 700)), random.randint(1, 4))
            if random.random() < 0.5:
                pygame.draw.line(virtual_surf, (255, 30, 30), (0, random.randint(0, 700)), (1000, random.randint(0, 700)), random.randint(1, 4))
            if random.random() < 0.3:
                y = random.randint(0, 700)
                pygame.draw.rect(virtual_surf, (0, 0, 255), (0, y, 1000, random.randint(8, 25)))
                
            # 화면 흔들림 효과
            shake_x = random.randint(-6, 6) if random.random() < 0.4 else 0
            shake_y = random.randint(-6, 6) if random.random() < 0.4 else 0
            
            surf_w, surf_h = surface.get_size()
            pygame.transform.scale(virtual_surf, (surf_w, surf_h), surface)
            
            # 흔들림이 있을 때 화면을 약간 밀어서 그리기
            if shake_x != 0 or shake_y != 0:
                temp_surf = surface.copy()
                surface.fill((0, 0, 0))
                surface.blit(temp_surf, (shake_x, shake_y))
                
        elif self.state in ["MAIN_SCREEN", "SUMMARY"]:
            if self.main_img:
                virtual_surf.blit(self.main_img, (0, 0))
            else:
                virtual_surf.fill((10, 10, 15))
                # 대체 텍스트
                font = pygame.font.SysFont(None, 40)
                text = font.render("START SCREEN (start.png is missing)", True, (255, 255, 255))
                virtual_surf.blit(text, (300, 330))
                
            # 텍스트 직접 출력 (대화 상자 없음, 가독성을 위한 그림자 효과 적용)
            text_y = 200
            for line in self.displayed_lines:
                color = (245, 245, 245) # 소프트 화이트
                if "▶" in line:
                    color = (100, 240, 150) # 초록색 힌트
                
                # 그림자 렌더링
                shadow_surf = self.font_body.render(line, True, (0, 0, 0))
                virtual_surf.blit(shadow_surf, (102, text_y + 2))
                
                # 본문 렌더링
                txt_surf = self.font_body.render(line, True, color)
                virtual_surf.blit(txt_surf, (100, text_y))
                text_y += 40
                
            pygame.transform.scale(virtual_surf, surface.get_size(), surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    game = Day0Manager()
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
