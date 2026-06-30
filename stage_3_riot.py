import pygame, random, sys

class RiotPacificationGame:
    def __init__(self):
        self.words = ["냉정", "논리", "화합", "신뢰", "공존", "소통", "중재", "평화"]
        self.reset()
        
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
        self.limit_time = 60.0
        self.state = "PLAYING" # PLAYING, SUCCESS, FAIL
        
        # Open text input for Korean IME support
        pygame.key.start_text_input()
        
    def update(self):
        if self.state == "PLAYING":
            self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            
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
                for w in self.word_data:
                    if self.user_input == w["text"] and not w["done"]:
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
        from visual_effects import draw_terminal_hud
        from main import CRT_GREEN, WHITE, get_scaled_font
        
        # Draw on virtual surface
        virtual_surf = pygame.Surface((1000, 700))
        virtual_surf.fill((5, 10, 25))
        
        # Fonts
        font_main = pygame.font.SysFont("malgungothic", 30, bold=True)
        font_sub = pygame.font.SysFont("malgungothic", 18)
        font_input = pygame.font.SysFont("malgungothic", 45, bold=True)
        
        # Draw words
        for w in self.word_data:
            color = (80, 80, 80) if w["done"] else (60, 120, 220)
            txt = font_main.render(w["text"], True, color)
            virtual_surf.blit(txt, w["pos"])
            if w["done"]:
                pygame.draw.line(virtual_surf, (80, 80, 80), (w["pos"][0], w["pos"][1] + 20), (w["pos"][0] + txt.get_width(), w["pos"][1] + 20), 3)
                
        # Draw input box
        pygame.draw.rect(virtual_surf, (60, 120, 220), (200, 550, 600, 70), 2)
        display_text = self.user_input + self.composition_text
        txt_input = font_input.render(display_text, True, WHITE)
        virtual_surf.blit(txt_input, (210, 560))
        
        # Draw blinking cursor
        show_cursor = (pygame.time.get_ticks() // 500) % 2 == 0
        cursor_x = 210 + font_input.size(display_text)[0]
        if show_cursor and self.state == "PLAYING":
            pygame.draw.line(virtual_surf, WHITE, (cursor_x, 565), (cursor_x, 615), 2)
            
        draw_terminal_hud(virtual_surf, "INTERNAL MUTINY PACIFICATION", self.limit_time, self.elapsed_time, (60, 120, 220))
        
        if self.state != "PLAYING":
            overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
            overlay.fill((5, 5, 20, 210))
            virtual_surf.blit(overlay, (0, 0))
            if self.state == "SUCCESS":
                msg = font_main.render("■ 설득 완료 (SUCCESS) ■", True, (100, 240, 150))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            else:
                msg = font_main.render("🚨 설득 실패 (FAIL) 🚨", True, (230, 50, 50))
                sub = font_sub.render("[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]", True, WHITE)
            virtual_surf.blit(msg, (500 - msg.get_width()//2, 325))
            virtual_surf.blit(sub, (500 - sub.get_width()//2, 370))
            
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