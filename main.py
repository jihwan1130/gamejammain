import pygame
import sys
import os
import random
import math
import json
from mini_game import MeteorGame

# 초기화
pygame.init()

# 글로벌 게임 설정 상태
class GameSettings:
    def __init__(self):
        # Get desktop display info for default fullscreen mode
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        self.volume = 0.5  # 0.0 ~ 1.0
        self.screen = None
        self.background_raw = None
        self.background = None
        self.space3_raw = None
        self.space3 = None
        self.state = "MENU"  # "MENU", "SETTINGS", "GAME"
        self.view_mode = "COCKPIT"  # "COCKPIT", "TRANSITION", "SPACE"
        self.transition_progress = 0.0  # 0.0 to 1.0
        self.transition_direction = 1  # 1: cockpit->space, -1: space->cockpit
        self.zoom_factor = 1.0  # 1.0 to 3.0
        self.zoom_x = 0
        self.zoom_y = 0
        self.fullscreen = True  # Default to fullscreen
        self.current_music_path = None
        
    def setup_display(self):
        # 해상도 변경 및 전체화면 플래그 적용 시 호출
        flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
        if not self.fullscreen:
            flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption("Utopia 2 - Retro Console")
        self.update_background()
        
    def update_background(self):
        if self.background_raw:
            self.background = pygame.transform.scale(self.background_raw, (self.width, self.height))
        else:
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill((5, 15, 5))
            
        if self.space3_raw:
            self.space3 = pygame.transform.scale(self.space3_raw, (self.width, self.height))

settings = GameSettings()

# 업적 및 엔딩 진행도 관리 클래스
class ProgressManager:
    def __init__(self, filename="progress_save.json"):
        self.filename = filename
        self.data = {
            "endings": {
                "ending_a": True,   # 데모용 기본 해금
                "ending_b": False,
                "ending_c": False,
                "ending_d": False
            },
            "achievements": {
                "first_boot": False,
                "quantum_engineer": False,
                "muted_silence": False,
                "warp_overload": False,
                "utopian_pioneer": False,
                "meteor_survivor": False
            }
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    for k in ["endings", "achievements"]:
                        if k in saved:
                            self.data[k].update(saved[k])
            except Exception as e:
                print(f"진행도를 로드할 수 없습니다: {e}")

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"진행도를 저장할 수 없습니다: {e}")

    def is_ending_unlocked(self, name):
        return self.data["endings"].get(name, False)

    def unlock_ending(self, name):
        if name in self.data["endings"] and not self.data["endings"][name]:
            self.data["endings"][name] = True
            self.save()
            return True
        return False

    def is_achievement_unlocked(self, name):
        return self.data["achievements"].get(name, False)

    def unlock_achievement(self, name):
        if name in self.data["achievements"] and not self.data["achievements"][name]:
            self.data["achievements"][name] = True
            self.save()
            return True
        return False

progress = ProgressManager()

# 디스플레이 설정
settings.setup_display()

# 이미지 로드 (새로운 픽셀 아트 이미지 적용)
BG_PATH = os.path.join("assets", "spaceship.jpg")
SPACE3_PATH = os.path.join("assets", "space3.png")
try:
    settings.background_raw = pygame.image.load(BG_PATH).convert()
    try:
        settings.space3_raw = pygame.image.load(SPACE3_PATH).convert()
    except Exception as e3:
        print(f"space3 이미지를 로드할 수 없습니다: {e3}")
    settings.update_background()
except Exception as e:
    print(f"배경 이미지를 로드할 수 없습니다: {e}")

# 사운드 로드 및 재생
BGM_PATH = os.path.join("assets", "spacesound.mp3")
MINIGAME_MUSIC_PATH = os.path.join("assets", "minigame_rain.mp3")

def play_music_track(path, fade_ms=0, loops=-1):
    try:
        if settings.current_music_path == path and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(settings.volume)
            return
        settings.current_music_path = path
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(settings.volume)
        pygame.mixer.music.play(loops, fade_ms=fade_ms)
    except Exception as e:
        print(f"배경음을 로드할 수 없습니다: {e}")


def transition_music_track(path, fade_out_ms=0, fade_in_ms=0):
    try:
        play_music_track(path, fade_ms=fade_in_ms)
    except Exception as e:
        print(f"배경음 전환 중 오류가 발생했습니다: {e}")


try:
    play_music_track(BGM_PATH, fade_ms=0)
except Exception as e:
    print(f"배경음악을 로드할 수 없습니다: {e}")

SFX_PATH = os.path.join("assets", "hackingsound2.mp3")
KEYBOARD_SFX_PATH = os.path.join("assets", "keyboardsound.MP3")
WALK2_SFX_PATH = os.path.join("assets", "walksound2.MP3")
click_sfx = None
keyboard_sfx = None
walk2_sfx = None
try:
    click_sfx = pygame.mixer.Sound(SFX_PATH)
except Exception as e:
    print(f"효과음을 로드할 수 없습니다: {e}")
try:
    keyboard_sfx = pygame.mixer.Sound(KEYBOARD_SFX_PATH)
    keyboard_sfx.set_volume(settings.volume)
except Exception as e:
    print(f"키보드 효과음을 로드할 수 없습니다: {e}")
try:
    walk2_sfx = pygame.mixer.Sound(WALK2_SFX_PATH)
    walk2_sfx.set_volume(settings.volume)
except Exception as e:
    print(f"걸음 효과음2를 로드할 수 없습니다: {e}")
clock = pygame.time.Clock()

# 레트로 엠버 모노크롬 색상 정의 (Retro CRT Amber theme)
CRT_BLACK = (20, 10, 5)
CRT_DARK = (45, 20, 10)
CRT_GREEN = (235, 120, 30)
CRT_BRIGHT = (255, 190, 80)
WHITE = (255, 235, 215)
GRAY = (110, 95, 85)
DARK_GRAY = (45, 38, 35)

# 폰트 로드
def get_font(name, size):
    try:
        available = pygame.font.get_fonts()
        if name == "korean":
            target_fonts = ["malgungothic", "gulim", "nanumgothic", "batang"]
        else:
            target_fonts = ["lucidaconsole", "couriernew", "consolas", "monospace", "malgungothic"]
        chosen_font = None
        for tf in target_fonts:
            if tf in available:
                chosen_font = tf
                break
        return pygame.font.SysFont(chosen_font, size, bold=True)
    except:
        return pygame.font.Font(None, size)

font_cache = {}
def get_scaled_font(size, is_korean=False):
    scaled_size = int(size * (settings.height / 720.0))
    cache_key = (scaled_size, is_korean)
    if cache_key not in font_cache:
        font_name = "korean" if is_korean else "lucidaconsole"
        font_cache[cache_key] = get_font(font_name, scaled_size)
    return font_cache[cache_key]

# 레트로 스타일 버튼 (직각 모서리, 고전 도스 게임 테두리)
class RetroButton:
    def __init__(self, x_ratio, y_ratio, width_ratio, height_ratio, text, action=None):
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.text = text
        self.action = action
        self.is_hovered = False
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.update_rect()

    def update_rect(self):
        w = int(settings.width * self.width_ratio)
        h = int(settings.height * self.height_ratio)
        x = int(settings.width * self.x_ratio)
        y = int(settings.height * self.y_ratio)
        self.rect = pygame.Rect(x, y, w, h)
        
    def draw(self, surface, time_ms=0):
        self.update_rect()
        mouse_pos = pygame.mouse.get_pos()
        
        # 마우스 호버 처리
        if self.rect.collidepoint(mouse_pos):
            self.is_hovered = True
        else:
            self.is_hovered = False
            
        # 버튼 패널 (반투명 어두운 엠버/구리)
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg_color = (50, 25, 10, 190) if self.is_hovered else (15, 8, 3, 140)
        pygame.draw.rect(button_surface, bg_color, (0, 0, self.rect.width, self.rect.height))
        
        # 레트로 더블 라인 테두리 그리기
        border_color = CRT_BRIGHT if self.is_hovered else CRT_GREEN
        # 바깥 테두리
        pygame.draw.rect(button_surface, border_color, (0, 0, self.rect.width, self.rect.height), 2)
        # 안쪽 테두리 (클래식 UI 감성)
        pygame.draw.rect(button_surface, border_color, (4, 4, self.rect.width - 8, self.rect.height - 8), 1)
        
        # 텍스트 그리기
        has_korean = any(ord(c) > 127 for c in self.text)
        font = get_scaled_font(22, is_korean=has_korean)
        text_color = WHITE if self.is_hovered else CRT_GREEN
        
        # 호버 시 포인터 표시 (예: "> START GAME <")
        display_text = f"> {self.text} <" if self.is_hovered else self.text
        text_surf = font.render(display_text, True, text_color)
        text_rect = text_surf.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        button_surface.blit(text_surf, text_rect)
        
        surface.blit(button_surface, (self.rect.x, self.rect.y))

    def handle_event(self, event):
        self.update_rect()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if click_sfx:
                    click_sfx.set_volume(settings.volume)
                    click_sfx.play()
                if self.action:
                    self.action()
                    return True
        return False
        
# 레트로 스타일 트로피 버튼
class TrophyButton:
    def __init__(self, x_ratio, y_ratio, size_pixels=54, action=None):
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.size_pixels = size_pixels
        self.action = action
        self.is_hovered = False
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.update_rect()

    def update_rect(self):
        size = int(settings.height * 0.075)
        x = int(settings.width * self.x_ratio)
        y = int(settings.height * self.y_ratio)
        self.rect = pygame.Rect(x, y, size, size)
        
    def draw(self, surface):
        self.update_rect()
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # 버튼 패널 (반투명 어두운 엠버/구리)
        bg_color = (50, 25, 10, 190) if self.is_hovered else (15, 8, 3, 140)
        pygame.draw.rect(surface, bg_color, self.rect)
        
        # 테두리
        border_color = CRT_BRIGHT if self.is_hovered else CRT_GREEN
        pygame.draw.rect(surface, border_color, self.rect, 2)
        inset = max(2, int(4 * (settings.height / 720.0)))
        pygame.draw.rect(surface, border_color, (self.rect.x + inset, self.rect.y + inset, self.rect.width - inset * 2, self.rect.height - inset * 2), 1)
        
        # 트로피 그리기
        cx = self.rect.centerx
        cy = self.rect.centery
        color = CRT_BRIGHT if self.is_hovered else CRT_GREEN
        scale = settings.height / 720.0
        
        # 컵 테두리 (Rim)
        pygame.draw.rect(surface, color, (cx - int(10*scale), cy - int(12*scale), int(20*scale), int(3*scale)))
        # 컵 몸통 (Body)
        pygame.draw.polygon(surface, color, [
            (cx - int(10*scale), cy - int(9*scale)), (cx + int(10*scale), cy - int(9*scale)),
            (cx + int(6*scale), cy + int(1*scale)), (cx - int(6*scale), cy + int(1*scale))
        ])
        # 줄기 (Stem)
        pygame.draw.rect(surface, color, (cx - int(2*scale), cy + int(1*scale), int(4*scale), int(6*scale)))
        # 받침대 (Base)
        pygame.draw.rect(surface, color, (cx - int(8*scale), cy + int(7*scale), int(16*scale), int(3*scale)))
        # 손잡이 (Handles)
        pygame.draw.lines(surface, color, False, [
            (cx - int(10*scale), cy - int(8*scale)), (cx - int(14*scale), cy - int(8*scale)),
            (cx - int(14*scale), cy - int(2*scale)), (cx - int(6*scale), cy - int(1*scale))
        ], max(1, int(2*scale)))
        pygame.draw.lines(surface, color, False, [
            (cx + int(10*scale), cy - int(8*scale)), (cx + int(14*scale), cy - int(8*scale)),
            (cx + int(14*scale), cy - int(2*scale)), (cx + int(6*scale), cy - int(1*scale))
        ], max(1, int(2*scale)))

    def handle_event(self, event):
        self.update_rect()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if click_sfx:
                    click_sfx.set_volume(settings.volume)
                    click_sfx.play()
                if self.action:
                    self.action()
                    return True
        return False

# 레트로 스타일 설정 기어 버튼
class SettingsButton:
    def __init__(self, x_ratio, y_ratio, size_pixels=54, action=None):
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.size_pixels = size_pixels
        self.action = action
        self.is_hovered = False
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.update_rect()

    def update_rect(self):
        size = int(settings.height * 0.075)
        x = int(settings.width * self.x_ratio)
        y = int(settings.height * self.y_ratio)
        self.rect = pygame.Rect(x, y, size, size)
        
    def draw(self, surface):
        self.update_rect()
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # 버튼 패널 (반투명 어두운 엠버/구리)
        bg_color = (50, 25, 10, 190) if self.is_hovered else (15, 8, 3, 140)
        pygame.draw.rect(surface, bg_color, self.rect)
        
        # 테두리
        border_color = CRT_BRIGHT if self.is_hovered else CRT_GREEN
        pygame.draw.rect(surface, border_color, self.rect, 2)
        inset = max(2, int(4 * (settings.height / 720.0)))
        pygame.draw.rect(surface, border_color, (self.rect.x + inset, self.rect.y + inset, self.rect.width - inset * 2, self.rect.height - inset * 2), 1)
        
        # 톱니바퀴 기어 아이콘 그리기
        cx = self.rect.centerx
        cy = self.rect.centery
        color = CRT_BRIGHT if self.is_hovered else CRT_GREEN
        scale = settings.height / 720.0
        
        # 중앙 원
        pygame.draw.circle(surface, color, (cx, cy), int(6*scale), max(1, int(2*scale)))
        # 바깥 원
        pygame.draw.circle(surface, color, (cx, cy), int(11*scale), max(1, int(2*scale)))
        # 톱니
        import math
        for i in range(8):
            angle = i * (math.pi / 4)
            x1 = cx + int(10 * scale * math.cos(angle))
            y1 = cy + int(10 * scale * math.sin(angle))
            x2 = cx + int(15 * scale * math.cos(angle))
            y2 = cy + int(15 * scale * math.sin(angle))
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), max(1, int(3*scale)))

    def handle_event(self, event):
        self.update_rect()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if click_sfx:
                    click_sfx.set_volume(settings.volume)
                    click_sfx.play()
                if self.action:
                    self.action()
                    return True
        return False

# 레트로 슬라이더 (사각형 블록 스타일)
class RetroSlider:
    def __init__(self, x_ratio, y_ratio, width_ratio, text, get_val, set_val):
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.width_ratio = width_ratio
        self.text = text
        self.get_val = get_val
        self.set_val = set_val
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.dragging = False
        self.update_rect()
        
    def update_rect(self):
        w = int(settings.width * self.width_ratio)
        h = 16
        x = int(settings.width * self.x_ratio)
        y = int(settings.height * self.y_ratio)
        self.rect = pygame.Rect(x, y, w, h)
        
    def draw(self, surface):
        self.update_rect()
        current_val = self.get_val()
        
        # 텍스트 라벨 (레트로 등폭)
        font = get_scaled_font(18)
        label_surf = font.render(f"{self.text}: {int(current_val * 100)}%", True, CRT_GREEN)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 25))
        
        # 슬라이더 트랙 (클래식 도트 라인 느낌)
        pygame.draw.rect(surface, CRT_DARK, self.rect)
        pygame.draw.rect(surface, CRT_GREEN, self.rect, 2)
        
        # 채워진 구간
        fill_width = int((self.rect.width - 8) * current_val)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 4, fill_width, self.rect.height - 8)
            pygame.draw.rect(surface, CRT_GREEN, fill_rect)
            
        # 레트로 사각형 노브 [ ]
        knob_width = 16
        knob_height = 24
        knob_x = self.rect.x + int((self.rect.width - knob_width) * current_val)
        knob_y = self.rect.centery - (knob_height // 2)
        
        knob_rect = pygame.Rect(knob_x, knob_y, knob_width, knob_height)
        pygame.draw.rect(surface, CRT_BRIGHT if self.dragging else CRT_GREEN, knob_rect)
        pygame.draw.rect(surface, CRT_BLACK, knob_rect, 2)
        
    def handle_event(self, event):
        self.update_rect()
        current_val = self.get_val()
        knob_width = 16
        knob_x = self.rect.x + int((self.rect.width - knob_width) * current_val)
        knob_y = self.rect.centery - 12
        knob_rect = pygame.Rect(knob_x, knob_y, knob_width, 24)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if knob_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.update_value_from_mouse(mouse_pos[0])
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_value_from_mouse(event.pos[0])
                return True
        return False
        
    def update_value_from_mouse(self, mouse_x):
        relative_x = mouse_x - self.rect.x
        val = max(0.0, min(1.0, relative_x / self.rect.width))
        self.set_val(val)

# 레트로 텍스트 레이블
class RetroLabel:
    def __init__(self, x_ratio, y_ratio, text, size, color=CRT_GREEN, is_center=False):
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.text = text
        self.size = size
        self.color = color
        self.is_center = is_center
        
    def draw(self, surface):
        font = get_scaled_font(self.size)
        surf = font.render(self.text, True, self.color)
        x = int(settings.width * self.x_ratio)
        y = int(settings.height * self.y_ratio)
        if self.is_center:
            rect = surf.get_rect(center=(x, y))
            surface.blit(surf, rect)
        else:
            surface.blit(surf, (x, y))

# 극대화된 CRT 스캔라인 오버레이
class ScanlineEffect:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.overlay = None
        
    def update_overlay(self):
        if self.width != settings.width or self.height != settings.height:
            self.width = settings.width
            self.height = settings.height
            # 투명 레이어 생성
            self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # 1. 촘촘한 레트로 스캔라인 (3픽셀 단위로 선을 굵게 그려 브라운관 감성 극대화)
            for y in range(0, self.height, 3):
                pygame.draw.line(self.overlay, (20, 10, 0, 40), (0, y), (self.width, y), 1)
            
            # 2. 비네팅 (화면 가장자리를 어둡게 깎아 볼록 모니터 입체감 형성)
            # 모서리 그라데이션 대신 단순 외곽 섀도우 박스로 빈티지 연출
            border_w = int(self.width * 0.02)
            pygame.draw.rect(self.overlay, (0, 0, 0, 120), (0, 0, self.width, self.height), border_w)
                
    def draw(self, surface):
        self.update_overlay()
        surface.blit(self.overlay, (0, 0))

# 레트로 모니터 노이즈 라인 (지속적으로 부드럽게 한 줄씩 내려가는 화면 리프레시선)
class CRTBeamEffect:
    def __init__(self):
        # 여러 개의 아날로그 스캔 빔 정의 (다양한 속도, 높이, 투명도로 아날로그 롤링 잦게 연출)
        self.beams = [
            {"y": 0, "speed": 0.8, "height": 12, "color": (255, 120, 30, 16)},
            {"y": -200, "speed": 1.2, "height": 6, "color": (255, 120, 30, 24)},  # 더 얇고 빠른 글리치성 빔
            {"y": -450, "speed": 0.5, "height": 20, "color": (255, 120, 30, 8)}   # 더 넓고 느리게 깔리는 음극선 빔
        ]
        
    def draw(self, surface):
        for beam in self.beams:
            beam["y"] += beam["speed"]
            if beam["y"] > settings.height:
                beam["y"] = -beam["height"] - 50  # 화면 위쪽에서 재출발
                
            if beam["y"] >= 0:
                beam_surf = pygame.Surface((settings.width, beam["height"]), pygame.SRCALPHA)
                beam_surf.fill(beam["color"])
                surface.blit(beam_surf, (0, int(beam["y"])))

# 레트로 스타일 우주선 터미널 로그
class RetroConsole:
    def __init__(self):
        self.logs = [
            "SYS BOOT: OK",
            "MAIN DRIVE: CHARGED 100%",
            "GRAVITY GRID: COLD RUN",
            "TERM LINK: SECURE_102",
            "DESTINATION: COORD_UTOPIA_2"
        ]
        self.log_timer = 0
        
    def update(self):
        self.log_timer += 1
        if self.log_timer > 102:
            self.log_timer = 0
            new_events = [
                "PING: ORBITAL BEACON ONLINE",
                "MON: REACTOR TEMP NOMINAL",
                "WARN: NO EXTERNAL THREATS",
                "NAV: AUTO-CALIBRATION OK",
                "FUEL CELL: STATUS NOMINAL"
            ]
            self.logs.pop(0)
            self.logs.append(random.choice(new_events))
            
    def draw(self, surface):
        panel_w = int(settings.width * 0.3375)
        panel_h = int(settings.height * 0.24)
        panel_x = int(settings.width * 0.03)
        panel_y = int(settings.height * 0.65)
        
        # 검은색 단색 레트로 터미널 창
        panel = pygame.Surface((panel_w, panel_h))
        panel.fill((20, 10, 5))
        
        # 이중 선 테두리
        pygame.draw.rect(panel, CRT_GREEN, (0, 0, panel_w, panel_h), 2)
        pygame.draw.rect(panel, CRT_GREEN, (3, 3, panel_w - 6, panel_h - 6), 1)
        
        font_header = get_scaled_font(15)
        font_log = get_scaled_font(13)
        
        # 헤더
        header_surf = font_header.render("[= CONSOLE DIAGNOSTICS =]", True, CRT_BRIGHT)
        panel.blit(header_surf, (15, 10))
        pygame.draw.line(panel, CRT_GREEN, (15, 26), (panel_w - 15, 26), 1)
        
        y_offset = 35
        for log in self.logs:
            log_surf = font_log.render(f"> {log}", True, CRT_GREEN)
            panel.blit(log_surf, (15, y_offset))
            y_offset += int(panel_h * 0.13)
            
        # 1. 아날로그 미세 지지직 노이즈 (가로형 아날로그 노이즈 입자 - 주황색 테마 맞춤)
        if random.random() < 0.15:  # 발생 확률 하향 (더 느긋하게 작동)
            for _ in range(random.randint(2, 5)):
                nx = random.randint(5, panel_w - 35)
                ny = random.randint(5, panel_h - 5)
                nw = random.randint(8, 40)
                pygame.draw.line(panel, (255, 150, 40, 40), (nx, ny), (nx + nw, ny), 1)

        # 2. 순간적인 화면 가로 성분 동적 간섭선 (주황색 바코드 글리치)
        if random.random() < 0.03:  # 발생 확률 하향 (가끔씩만 지지직거리도록)
            iy = random.randint(8, panel_h - 15)
            ih = random.randint(2, 6)
            interference = pygame.Surface((panel_w - 10, ih), pygame.SRCALPHA)
            interference.fill((255, 150, 40, 25))
            panel.blit(interference, (5, iy))

        # 3. 화면 미세 지터(Jitter) 효과 (주파수 흔들림 현상)
        jx, jy = 0, 0
        if random.random() < 0.02:  # 발생 확률 하향 (드물고 조용히 흔들리게)
            jx = random.choice([-2, -1, 1, 2])
            jy = random.choice([-1, 0, 1])

        surface.blit(panel, (panel_x + jx, panel_y + jy))
        
    def handle_event(self, event):
        panel_w = int(settings.width * 0.3375)
        panel_h = int(settings.height * 0.24)
        panel_x = int(settings.width * 0.03)
        panel_y = int(settings.height * 0.65)
        rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(event.pos):
                if keyboard_sfx:
                    keyboard_sfx.set_volume(settings.volume)
                    keyboard_sfx.play()
                # 인터랙티브 로그 엔트리 추가
                new_logs = [
                    "KEY: INPUT REGISTERED",
                    "SYS: KEYSTROKE CAPTURED",
                    "TERM: DIAGNOSTIC MANUAL",
                    "MON: MANUAL PING RETENT",
                    "SEC: OVERRIDE BYPASS"
                ]
                self.logs.pop(0)
                self.logs.append(random.choice(new_logs))
                return True
        return False

# ----------------- 씬 액션 정의 -----------------

def go_to_game():
    settings.state = "GAME"
    progress.unlock_achievement("warp_overload")
    progress.unlock_ending("ending_b")
    try:
        pygame.mixer.music.fadeout(1000)
    except:
        pass

def go_to_settings():
    settings.state = "SETTINGS"

def go_to_achievements():
    settings.state = "ACHIEVEMENTS"

def exit_app():
    pygame.quit()
    sys.exit()

def set_volume(val):
    settings.volume = val
    try:
        pygame.mixer.music.set_volume(val)
    except:
        pass
    try:
        if click_sfx:
            click_sfx.set_volume(val)
    except:
        pass
    try:
        if keyboard_sfx:
            keyboard_sfx.set_volume(val)
    except:
        pass
    try:
        if walk2_sfx:
            walk2_sfx.set_volume(val)
    except:
        pass
    if val == 0.0:
        progress.unlock_achievement("muted_silence")

def get_volume():
    return settings.volume

def change_resolution(width, height):
    settings.fullscreen = False  # Switch to windowed mode for custom resolution
    settings.width = width
    settings.height = height
    settings.setup_display()
    if width == 1600 and height == 900:
        progress.unlock_achievement("quantum_engineer")

def toggle_screen_mode():
    settings.fullscreen = not settings.fullscreen
    if settings.fullscreen:
        info = pygame.display.Info()
        settings.width = info.current_w
        settings.height = info.current_h
    else:
        settings.width = 1280
        settings.height = 720
    settings.setup_display()

def go_to_minigames():
    settings.state = "MINIGAMES"


def go_to_main_menu():
    settings.state = "MENU"
    transition_music_track(BGM_PATH, fade_out_ms=1000, fade_in_ms=1800)

# 레트로 씬 버튼 등록
menu_buttons = [
    RetroButton(0.03, 0.30, 0.225, 0.072, "START GAME", go_to_game),
    RetroButton(0.03, 0.40, 0.225, 0.072, "MINI GAMES", go_to_minigames),
    RetroButton(0.03, 0.50, 0.225, 0.072, "EXIT", exit_app)
]

trophy_button = TrophyButton(0.92, 0.70, 54, go_to_achievements)
settings_button = SettingsButton(0.92, 0.80, 54, go_to_settings)

def go_back_to_menu():
    go_to_main_menu()


achievements_buttons = [
    RetroButton(0.34, 0.79, 0.32, 0.08, "메인 메뉴로 돌아가기", go_back_to_menu)
]

minigames_buttons = [
    RetroButton(0.34, 0.79, 0.32, 0.08, "메인 메뉴로 돌아가기", go_back_to_menu)
]

settings_components = [
    # 볼륨 조절 슬라이더
    RetroSlider(0.35, 0.35, 0.30, "MASTER VOLUME", get_volume, set_volume),
    
    # 해상도 설정 레이블 & 버튼
    RetroLabel(0.35, 0.48, "[SCREEN CONFIGURATION SELECT]", 18, CRT_GREEN),
    RetroButton(0.35, 0.53, 0.14, 0.07, "1280x720", lambda: change_resolution(1280, 720)),
    RetroButton(0.51, 0.53, 0.14, 0.07, "1024x576", lambda: change_resolution(1024, 576)),
    RetroButton(0.35, 0.62, 0.14, 0.07, "1600x900", lambda: change_resolution(1600, 900)),
    RetroButton(0.51, 0.62, 0.14, 0.07, "SCREEN MODE", toggle_screen_mode),
    
    # 뒤로가기 버튼
    RetroButton(0.35, 0.77, 0.30, 0.08, "SAVE & BACK", lambda: setattr(settings, 'state', 'MENU'))
]

class MeteorGame:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.player_x = settings.width // 2
        self.player_y = settings.height - 120
        self.player_size = 48  # 2배 증가 (24 -> 48)
        self.hp = 3
        self.max_hp = 3
        self.invincible_timer = 0
        self.meteors = []
        self.particles = []
        self.state = "COUNTDOWN"  # "COUNTDOWN", "PLAYING", "PAUSED", "RESUMING", "WON", "LOST"
        self.start_ticks = pygame.time.get_ticks()
        self.play_start_ticks = 0
        self.elapsed_time = 0
        self.pause_total_duration = 0
        self.pause_started_at = 0
        self.resume_started_at = 0
        self.game_duration = 30000  # 30초 플레이 타임
        self.shake_intensity = 0
        self.pause_resume_rect = pygame.Rect(0, 0, 0, 0)
        self.pause_exit_rect = pygame.Rect(0, 0, 0, 0)
        
    def update(self):
        current_ticks = pygame.time.get_ticks()
        
        # Screen shake dampening
        if self.shake_intensity > 0:
            self.shake_intensity -= 1
            
        if self.state == "COUNTDOWN":
            self.elapsed_time = 0
            countdown_elapsed = current_ticks - self.start_ticks
            if countdown_elapsed >= 3000:  # 3 seconds countdown
                self.state = "PLAYING"
                self.play_start_ticks = current_ticks
                self.pause_total_duration = 0
                self.pause_started_at = 0
                self.meteors = []
        elif self.state == "PLAYING":
            self.elapsed_time = current_ticks - self.play_start_ticks - self.pause_total_duration
            if self.elapsed_time >= self.game_duration:
                self.state = "WON"
                progress.unlock_achievement("meteor_survivor")
                
            # Invincibility frame countdown
            if self.invincible_timer > 0:
                self.invincible_timer -= 1
                
            # Spawn meteors - spawn rate increases over time (밸런스 재조정)
            spawn_chance = 0.06 + (self.elapsed_time / self.game_duration) * 0.07
            if random.random() < spawn_chance:
                # 난이도 완화 (동시 생성 개수 축소: 초중반 무조건 1개, 극후반 70% 이후 가끔 2개)
                num_spawn = 1
                if (self.elapsed_time / self.game_duration) >= 0.7:
                    num_spawn = 2 if random.random() < 0.3 else 1
                    
                for _ in range(num_spawn):
                    # 거대 운석의 빈도를 낮추고 소형 운석의 비율을 늘림 (지수 스케일링)
                    size = int(8 + (random.random() ** 1.8) * 40)
                    m_x = random.randint(30, settings.width - 30)
                    m_y = -size
                    
                    # [크기-속도 연동 물리 법칙] 큰 운석은 느리고 묵직하게 길목을 막고, 작은 운석은 빠르게 떨어짐!
                    if size >= 32:
                        base_speed_y = random.uniform(2.2, 3.8)
                        speed_x = random.uniform(-0.8, 0.8)  # 거대 운석은 거의 직선 낙하
                    elif size >= 18:
                        base_speed_y = random.uniform(3.8, 5.8)
                        speed_x = random.uniform(-1.8, 1.8)
                    else:
                        base_speed_y = random.uniform(5.8, 8.8)
                        speed_x = random.uniform(-2.8, 2.8)  # 초소형 운석은 날렵하게 꺾임
                        
                    # 시간 경과에 따른 가속
                    speed_y = base_speed_y + (self.elapsed_time / self.game_duration) * 2.0
                    self.meteors.append({
                        "x": m_x,
                        "y": m_y,
                        "size": size,
                        "speed_x": speed_x,
                        "speed_y": speed_y
                    })
                
            # Update meteors
            for m in self.meteors[:]:
                m["x"] += m["speed_x"]
                m["y"] += m["speed_y"]
                
                # Check collision with player
                dist = math.hypot(m["x"] - self.player_x, m["y"] - self.player_y)
                if dist < (m["size"] + self.player_size - 4):
                    if self.invincible_timer == 0:
                        self.hp -= 1
                        self.invincible_timer = 60  # 1 second invincibility
                        self.shake_intensity = 15
                        # Create explosion particles
                        for _ in range(15):
                            self.particles.append({
                                "x": self.player_x,
                                "y": self.player_y,
                                "vx": random.uniform(-4, 4),
                                "vy": random.uniform(-4, 4),
                                "life": random.randint(15, 30),
                                "color": (255, 120, 30)
                            })
                        play_sfx("sfx_click")
                        if self.hp <= 0:
                            self.state = "LOST"
                    # Remove the hit meteor
                    self.meteors.remove(m)
                    continue
                    
                # Remove if off-screen
                if m["y"] > settings.height + 50 or m["x"] < -50 or m["x"] > settings.width + 50:
                    self.meteors.remove(m)
                    
        elif self.state == "RESUMING":
            if current_ticks - self.resume_started_at >= 3000:
                self.state = "PLAYING"
                self.resume_started_at = 0

        # Update particles
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0:
                self.particles.remove(p)

    # [요구사항 3] 일시정지 메뉴 버튼 위치 업데이트
    def update_pause_buttons(self):
        button_w = int(settings.width * 0.18)
        button_h = int(settings.height * 0.07)
        button_y = int(settings.height * 0.56)
        self.pause_resume_rect = pygame.Rect((settings.width - button_w * 2 - 24) // 2, button_y, button_w, button_h)
        self.pause_exit_rect = pygame.Rect(self.pause_resume_rect.right + 24, button_y, button_w, button_h)
    
    # [요구사항 3] 게임 일시정지
    def pause_game(self):
        if self.state == "PLAYING":
            self.state = "PAUSED"
            self.pause_started_at = pygame.time.get_ticks()
            self.update_pause_buttons()

    # [요구사항 3] 게임 재개
    def resume_game(self):
        if self.state == "PAUSED":
            if self.pause_started_at:
                # 일시정지된 시간을 누적
                self.pause_total_duration += pygame.time.get_ticks() - self.pause_started_at
                self.pause_started_at = 0
            self.state = "RESUMING"
            self.resume_started_at = pygame.time.get_ticks()

    # [요구사항 3] 일시정지 메뉴 이벤트 처리
    def handle_event(self, event):
        from main import go_to_main_menu
        # PAUSED 상태일 때만 버튼 클릭을 처리
        if self.state != "PAUSED" or not (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            return False

        self.update_pause_buttons()
        if self.pause_resume_rect.collidepoint(event.pos):
            play_sfx("sfx_click")
            self.resume_game()
            return True
        if self.pause_exit_rect.collidepoint(event.pos):
            play_sfx("sfx_click")
            go_to_main_menu()
            return True
        return False

    def handle_input(self):
        # PAUSED, RESUMING 상태에서는 플레이어 조작 불가
        if self.state != "PLAYING":
            return
            
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            
        # Normalize diagonal speed
        if dx != 0 and dy != 0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            
        speed = 6.0
        self.player_x += dx * speed
        self.player_y += dy * speed
        
        # Constrain to screen boundaries
        self.player_x = max(20 + self.player_size, min(settings.width - 20 - self.player_size, self.player_x))
        self.player_y = max(50 + self.player_size, min(settings.height - 50 - self.player_size, self.player_y))

    def draw(self, surface):
        # Dark red/brown simulation tint backdrop
        overlay = pygame.Surface((settings.width, settings.height), pygame.SRCALPHA)
        overlay.fill((12, 6, 3, 230))
        surface.blit(overlay, (0, 0))
        
        # Shake offset
        ox, oy = 0, 0
        if self.shake_intensity > 0:
            ox = random.randint(-self.shake_intensity, self.shake_intensity)
            oy = random.randint(-self.shake_intensity, self.shake_intensity)
            
        # Draw retro grid
        grid_w = 40
        for x in range(0, settings.width, grid_w):
            pygame.draw.line(surface, (40, 20, 10), (x + ox, 0), (x + ox, settings.height), 1)
        for y in range(0, settings.height, grid_w):
            pygame.draw.line(surface, (40, 20, 10), (ox, y + oy), (settings.width + ox, y + oy), 1)
            
        # Draw Meteors
        for m in self.meteors:
            mx, my = int(m["x"] + ox), int(m["y"] + oy)
            r = m["size"]
            pygame.draw.circle(surface, (140, 70, 30), (mx, my), r)
            pygame.draw.circle(surface, CRT_BRIGHT, (mx, my), r, 2)
            # Crater details
            pygame.draw.line(surface, CRT_BRIGHT, (mx - r//2, my - r//3), (mx - r//4, my - r//4), 2)
            pygame.draw.line(surface, CRT_BRIGHT, (mx + r//3, my + r//4), (mx + r//2, my + r//5), 2)
            
        # Draw Particles
        for p in self.particles:
            px, py = int(p["x"] + ox), int(p["y"] + oy)
            pygame.draw.rect(surface, p["color"], (px, py, 4, 4))
            
        # Draw Player Ship
        if self.invincible_timer == 0 or (self.invincible_timer // 4) % 2 == 0:
            px, py = int(self.player_x + ox), int(self.player_y + oy)
            points = [
                (px, py - 44),       # 로켓 상단 팁 (2배 확대)
                (px - 36, py + 32),  # 좌측 하단 날개
                (px - 16, py + 16),  # 좌측 안쪽 인덴트
                (px + 16, py + 16),  # 우측 안쪽 인덴트
                (px + 36, py + 32)   # 우측 하단 날개
            ]
            pygame.draw.polygon(surface, (100, 255, 100), points)
            pygame.draw.polygon(surface, CRT_GREEN, points, 2)
            
            # Jet flame animation (2배 크기 확대)
            if self.state == "PLAYING" and pygame.time.get_ticks() % 100 < 50:
                flame = [
                    (px - 12, py + 20),
                    (px, py + 48),
                    (px + 12, py + 20)
                ]
                pygame.draw.polygon(surface, (255, 120, 30), flame)
                
        # Draw HUD elements
        font_hud = get_scaled_font(16, is_korean=True)
        
        # [요구사항 1] Time remaining progress bar
        time_ratio = max(0.0, (self.game_duration - self.elapsed_time) / self.game_duration)
        bar_max_w = settings.width // 2 - 60 # 프로그레스 바 최대 너비
        bar_h = 16
        bar_x = 30
        bar_y = 22

        # 프로그레스 바 테두리
        pygame.draw.rect(surface, CRT_GREEN, (bar_x, bar_y, bar_max_w, bar_h), 2)
        # 프로그레스 바 내부 채우기
        fill_w = int(bar_max_w * time_ratio)
        if fill_w > 0:
            # 남은 시간에 따라 색상 변경 (녹색 -> 주황색 -> 적색)
            bar_color = CRT_BRIGHT if time_ratio > 0.5 else ((255, 120, 30) if time_ratio > 0.2 else (255, 60, 40))
            pygame.draw.rect(surface, bar_color, (bar_x + 2, bar_y + 2, fill_w - 4, bar_h - 4))

        # Shield health bar
        shield_text = "SHIELDS: "
        shield_lbl = font_hud.render(shield_text, True, CRT_GREEN)
        surface.blit(shield_lbl, (settings.width - 240, 20))
        
        # Draw shield energy blocks
        for hp_i in range(self.max_hp):
            bx = settings.width - 140 + hp_i * 22
            by = 22
            color = (100, 255, 100) if hp_i < self.hp else (40, 20, 10)
            pygame.draw.rect(surface, color, (bx, by, 16, 12))
            pygame.draw.rect(surface, CRT_GREEN, (bx, by, 16, 12), 1)
            
        # Draw game boundaries
        pygame.draw.rect(surface, CRT_GREEN, (15 + ox, 45 + oy, settings.width - 30, settings.height - 85), 2)
            
        # Countdown overlay rendering
        if self.state == "COUNTDOWN":
            font_title = get_scaled_font(36, is_korean=True)
            elapsed = pygame.time.get_ticks() - self.start_ticks
            num = 3 - (elapsed // 1000)
            num_str = str(num) if num > 0 else "START!"
            
            # Pulse size
            pulse = 1.0 + (elapsed % 1000) / 1000.0 * 0.3
            font_num = get_scaled_font(int(48 * pulse), is_korean=True)
            
            num_surf = font_num.render(num_str, True, CRT_BRIGHT)
            num_rect = num_surf.get_rect(center=(settings.width // 2, settings.height // 2))
            
            box_w, box_h = 300, 120
            box_rect = pygame.Rect(settings.width//2 - box_w//2, settings.height//2 - box_h//2, box_w, box_h)
            pygame.draw.rect(surface, (15, 8, 3, 220), box_rect)
            pygame.draw.rect(surface, CRT_GREEN, box_rect, 2)
            
            surface.blit(num_surf, num_rect)
            
        # End results overlay rendering
        elif self.state in ["WON", "LOST"]:
            font_end = get_scaled_font(28, is_korean=True)
            font_sub = get_scaled_font(15, is_korean=True)
            
            msg = "MISSION SUCCESS" if self.state == "WON" else "SHIELD COLLAPSE - GAME OVER"
            color = (100, 255, 100) if self.state == "WON" else (255, 60, 40)
            
            msg_surf = font_end.render(msg, True, color)
            msg_rect = msg_surf.get_rect(center=(settings.width // 2, settings.height // 2 - 30))
            
            sub_text = "[ ENTER: 다시 시작 | ESC: 미니게임 선택으로 돌아가기 ]"
            sub_surf = font_sub.render(sub_text, True, (255, 255, 255))
            sub_rect = sub_surf.get_rect(center=(settings.width // 2, settings.height // 2 + 30))
            
            box_w = int(settings.width * 0.6)
            box_h = 160
            box_rect = pygame.Rect(settings.width//2 - box_w//2, settings.height//2 - box_h//2, box_w, box_h)
            
            pygame.draw.rect(surface, (15, 8, 3, 240), box_rect)
            pygame.draw.rect(surface, color, box_rect, 2)
            pygame.draw.rect(surface, color, (box_rect.x + 4, box_rect.y + 4, box_rect.width - 8, box_rect.height - 8), 1)
            
            surface.blit(msg_surf, msg_rect)
            surface.blit(sub_surf, sub_rect)

        # [요구사항 3] 일시정지 및 재개 화면 렌더링
        # PAUSED 또는 RESUMING 상태일 때 화면을 어둡게 하고 UI를 그림
        if self.state in ["PAUSED", "RESUMING"]:
            dim = pygame.Surface((settings.width, settings.height), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 150))
            surface.blit(dim, (0, 0))

            panel_w = int(settings.width * 0.42)
            panel_h = int(settings.height * 0.26)
            panel_x = (settings.width - panel_w) // 2
            panel_y = int(settings.height * 0.32)
            panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (15, 8, 3, 220), (0, 0, panel_w, panel_h))
            pygame.draw.rect(panel_surf, CRT_GREEN, (0, 0, panel_w, panel_h), 2)
            pygame.draw.rect(panel_surf, CRT_GREEN, (4, 4, panel_w - 8, panel_h - 8), 1)
            surface.blit(panel_surf, (panel_x, panel_y))

            title_font = get_scaled_font(24, is_korean=True)
            title_surf = title_font.render("게임 일시정지", True, CRT_BRIGHT)
            title_rect = title_surf.get_rect(center=(settings.width // 2, panel_y + 44))
            surface.blit(title_surf, title_rect)

            # RESUMING 상태가 아닐 때만 버튼을 그림
            if self.state == "PAUSED":
                self.update_pause_buttons()
                button_y = panel_y + int(panel_h * 0.56)
                self.pause_resume_rect.y = button_y
                self.pause_exit_rect.y = button_y

                # 버튼 렌더링
                for rect, text, color in [
                    (self.pause_resume_rect, "다시 진행하기", CRT_BRIGHT),
                    (self.pause_exit_rect, "나가기", CRT_GREEN),
                ]:
                    btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(btn_surf, (40, 20, 10, 220), (0, 0, rect.width, rect.height))
                    pygame.draw.rect(btn_surf, color, (0, 0, rect.width, rect.height), 2)
                    btn_font = get_scaled_font(16, is_korean=True)
                    text_surf = btn_font.render(text, True, WHITE)
                    text_rect = text_surf.get_rect(center=(rect.width // 2, rect.height // 2))
                    btn_surf.blit(text_surf, text_rect)
                    surface.blit(btn_surf, (rect.x, rect.y))
            
            # RESUMING 상태일 때 카운트다운 숫자를 그림
            if self.state == "RESUMING":
                countdown = 3 - ((pygame.time.get_ticks() - self.resume_started_at) // 1000)
                countdown = max(1, countdown)
                count_font = get_scaled_font(36, is_korean=True)
                count_surf = count_font.render(str(countdown), True, CRT_BRIGHT)
                count_rect = count_surf.get_rect(center=(settings.width // 2, panel_y + int(panel_h * 0.65)))
                surface.blit(count_surf, count_rect)

game_components = [
    RetroLabel(0.5, 0.45, "=== SIMULATION IN PROGRESS ===", 36, CRT_BRIGHT, is_center=True),
    RetroLabel(0.5, 0.53, "[PRESS ESC TO TERMINATE LINK]", 18, CRT_GREEN, is_center=True)
]

def main():
    progress.unlock_achievement("first_boot")
    scanlines = ScanlineEffect()
    beam = CRTBeamEffect()
    console = RetroConsole()
    meteor_game = MeteorGame()
    
    # 드래그 줌 상태 변수
    dragging_zoom = False
    drag_start_x = 0
    drag_start_y = 0
    zoom_start_factor = 1.0
    
    running = True
    
    while running:
        time_ms = pygame.time.get_ticks()
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if settings.state == "METEOR_GAME":
                    # [요구사항 3] ESC 키로 일시정지/재개 토글
                    if meteor_game.state == "PLAYING":
                        meteor_game.pause_game()
                elif settings.state == "MENU" and settings.view_mode == "SPACE":
                    settings.view_mode = "TRANSITION"
                    settings.transition_progress = 1.0
                    settings.transition_direction = -1
                    if walk2_sfx:
                        walk2_sfx.set_volume(settings.volume)
                        walk2_sfx.play()
                    try:
                        pygame.mixer.music.fadeout(800)
                    except:
                        pass
                    continue
                elif settings.state != "MENU":
                    was_in_game = (settings.state == "GAME")
                    settings.state = "MENU"
                    if was_in_game:
                        try:
                            pygame.mixer.music.load(os.path.join("assets", "spacesound.mp3"))
                            pygame.mixer.music.set_volume(settings.volume)
                            pygame.mixer.music.play(-1)
                        except:
                            pass
            
            if settings.state == "MENU":
                if settings.view_mode == "COCKPIT":
                    # 창문 클릭 체크 (rx: 0.35 ~ 0.65, ry: 0.12 ~ 0.42)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = event.pos
                        rx = mx / settings.width
                        ry = my / settings.height
                        if 0.35 <= rx <= 0.65 and 0.12 <= ry <= 0.42:
                            settings.view_mode = "TRANSITION"
                            settings.transition_progress = 0.0
                            settings.transition_direction = 1
                            if walk2_sfx:
                                walk2_sfx.set_volume(settings.volume)
                                walk2_sfx.play()
                            try:
                                pygame.mixer.music.fadeout(800)
                            except:
                                pass
                            continue
                            
                    for btn in menu_buttons:
                        btn.handle_event(event)
                    trophy_button.handle_event(event)
                    settings_button.handle_event(event)
                    console.handle_event(event)
                elif settings.view_mode == "SPACE":
                    # 스페이스 뷰 상태에서 휠 스크롤로 줌, 클릭 시 복귀
                    if event.type == pygame.MOUSEWHEEL:
                        mx, my = pygame.mouse.get_pos()
                        old_factor = settings.zoom_factor
                        new_factor = max(1.0, min(3.0, old_factor + event.y * 0.15))
                        
                        if new_factor != old_factor:
                            w_old = int(settings.width * old_factor)
                            h_old = int(settings.height * old_factor)
                            w_new = int(settings.width * new_factor)
                            h_new = int(settings.height * new_factor)
                            
                            # 마우스 좌표의 현재 이미지 상의 비율(0.0 ~ 1.0) 계산
                            px = (mx - settings.zoom_x) / w_old
                            py = (my - settings.zoom_y) / h_old
                            
                            # 새 줌 비율에 따른 새로운 오프셋 계산 (마우스 좌표 고정)
                            new_x = mx - px * w_new
                            new_y = my - py * h_new
                            
                            # 경계 제한 (화면 밖으로 검은 여백이 남지 않도록)
                            if new_factor == 1.0:
                                settings.zoom_x = 0
                                settings.zoom_y = 0
                            else:
                                settings.zoom_x = max(settings.width - w_new, min(0, new_x))
                                settings.zoom_y = max(settings.height - h_new, min(0, new_y))
                            settings.zoom_factor = new_factor
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        settings.view_mode = "TRANSITION"
                        settings.transition_progress = 1.0
                        settings.transition_direction = -1
                        if walk2_sfx:
                            walk2_sfx.set_volume(settings.volume)
                            walk2_sfx.play()
                        try:
                            pygame.mixer.music.fadeout(800)
                        except:
                            pass
            elif settings.state == "SETTINGS":
                for comp in settings_components:
                    if hasattr(comp, 'handle_event'):
                        comp.handle_event(event)
            elif settings.state == "ACHIEVEMENTS":
                for btn in achievements_buttons:
                    btn.handle_event(event)
            elif settings.state == "MINIGAMES":
                for btn in minigames_buttons:
                    btn.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    panel_w = int(settings.width * 0.88)
                    panel_h = int(settings.height * 0.78)
                    panel_x = int(settings.width * 0.06)
                    panel_y = int(settings.height * 0.10)
                    
                    card_w = int(panel_w * 0.27)
                    card_h = int(panel_h * 0.48)
                    gap = int(panel_w * 0.035)
                    start_x = panel_x + int(panel_w * 0.06)
                    card_y = panel_y + int(panel_h * 0.20)
                    
                    # 2번째 카드 (index 1) - 운석 소나기 카드 클릭 시 실행
                    cx2 = start_x + 1 * (card_w + gap)
                    rect2 = pygame.Rect(cx2, card_y, card_w, card_h)
                    if rect2.collidepoint(event.pos):
                        settings.state = "METEOR_GAME"
                        meteor_game.reset()
                        # 메인 BGM(spacesound)을 페이드 아웃하고 미니게임 BGM을 페이드 인으로 재생
                        pygame.mixer.music.fadeout(1500) # 1.5초 동안 현재 음악(spacesound)을 서서히 끔
                        play_music_track(MINIGAME_MUSIC_PATH, fade_ms=1000) # 1초 동안 새 음악(minigame_rain)을 서서히 켬
                        if keyboard_sfx:
                            keyboard_sfx.set_volume(settings.volume)
                            keyboard_sfx.play()
            elif settings.state == "METEOR_GAME":
                if meteor_game.handle_event(event):
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if meteor_game.state == "PLAYING":
                            # [수정] ESC 키는 게임을 'PAUSED' 상태로 만들기만 함
                            meteor_game.pause_game()
                            play_sfx("sfx_keyboard")
                        # [수정] PAUSED 상태에서 ESC를 눌러도 재개되지 않도록 관련 로직 제거
                        elif meteor_game.state in ["WON", "LOST"]:
                            go_to_main_menu()
                    elif event.key == pygame.K_RETURN and meteor_game.state in ["WON", "LOST"]:
                        meteor_game.reset()
                        if keyboard_sfx:
                            keyboard_sfx.set_volume(settings.volume)
                            keyboard_sfx.play()
        if settings.state == "METEOR_GAME":
            meteor_game.handle_input()
            meteor_game.update()
            
        # 1. 배경 (픽셀 아트 화면) 및 전환 처리
        if settings.state == "MENU":
            if settings.view_mode == "COCKPIT":
                settings.screen.blit(settings.background, (0, 0))
            elif settings.view_mode == "SPACE":
                if settings.space3:
                    if settings.zoom_factor == 1.0:
                        settings.screen.blit(settings.space3, (0, 0))
                    else:
                        w = int(settings.width * settings.zoom_factor)
                        h = int(settings.height * settings.zoom_factor)
                        zoomed = pygame.transform.scale(settings.space3, (w, h))
                        settings.screen.blit(zoomed, (settings.zoom_x, settings.zoom_y))
                else:
                    settings.screen.blit(settings.background, (0, 0))
            elif settings.view_mode == "TRANSITION":
                # Update progress
                settings.transition_progress += settings.transition_direction * 0.025 # 40 frames (~0.6s)
                if settings.transition_direction == 1:
                    if settings.transition_progress >= 1.0:
                        settings.transition_progress = 1.0
                        settings.view_mode = "SPACE"
                        try:
                            pygame.mixer.music.load(os.path.join("assets", "ambiencesound.mp3"))
                            pygame.mixer.music.set_volume(settings.volume)
                            pygame.mixer.music.play(-1, fade_ms=2000)
                        except Exception as em:
                            print(f"앰비언스 BGM 로드 실패: {em}")
                else:
                    if settings.transition_progress <= 0.0:
                        settings.transition_progress = 0.0
                        settings.view_mode = "COCKPIT"
                        settings.zoom_factor = 1.0 # Reset zoom when returning to cockpit!
                        settings.zoom_x = 0
                        settings.zoom_y = 0
                        try:
                            pygame.mixer.music.load(os.path.join("assets", "spacesound.mp3"))
                            pygame.mixer.music.set_volume(settings.volume)
                            pygame.mixer.music.play(-1, fade_ms=2000)
                        except Exception as em:
                            print(f"우주선 BGM 로드 실패: {em}")
                
                # Cross-fade 배경 그리기
                settings.screen.blit(settings.background, (0, 0))
                if settings.space3:
                    temp_space = settings.space3.copy()
                    temp_space.set_alpha(int(settings.transition_progress * 255))
                    settings.screen.blit(temp_space, (0, 0))
        else:
            settings.screen.blit(settings.background, (0, 0))
        
        # 2. 상태 렌더링
        if settings.state == "MENU":
            if settings.view_mode == "COCKPIT":
                # 메인 타이틀 패널
                panel_w = int(settings.width * 0.3375)
                panel_h = int(settings.height * 0.18)
                panel_x = int(settings.width * 0.03)
                panel_y = int(settings.height * 0.08)
                
                # 클래식 메인 프레임
                title_panel = pygame.Surface((panel_w, panel_h))
                title_panel.fill((20, 10, 5))
                pygame.draw.rect(title_panel, CRT_GREEN, (0, 0, panel_w, panel_h), 2)
                pygame.draw.rect(title_panel, CRT_GREEN, (4, 4, panel_w - 8, panel_h - 8), 1)
                
                # 장식 모서리 크로스바
                pygame.draw.line(title_panel, CRT_BRIGHT, (0, 0), (12, 12), 2)
                pygame.draw.line(title_panel, CRT_BRIGHT, (panel_w, 0), (panel_w - 12, 12), 2)
                pygame.draw.line(title_panel, CRT_BRIGHT, (0, panel_h), (12, panel_h - 12), 2)
                pygame.draw.line(title_panel, CRT_BRIGHT, (panel_w, panel_h), (panel_w - 12, panel_h - 12), 2)
                
                settings.screen.blit(title_panel, (panel_x, panel_y))
                
                # 타이틀 텍스트 (완벽한 도트 느낌의 모노크롬 텍스트)
                font_title = get_scaled_font(36)
                
                title_main = font_title.render("SPACE ADVENTURE", True, CRT_BRIGHT)
                title_rect = title_main.get_rect()
                title_rect.centerx = panel_x + (panel_w // 2)
                title_rect.centery = panel_y + (panel_h // 2)
                settings.screen.blit(title_main, title_rect)
                
                # 버튼 렌더링
                for btn in menu_buttons:
                    btn.draw(settings.screen, time_ms)
                trophy_button.draw(settings.screen)
                settings_button.draw(settings.screen)
                    
                # 콘솔 갱신
                console.update()
                console.draw(settings.screen)
                
            elif settings.view_mode == "SPACE":
                font_guide = get_scaled_font(16, is_korean=True)
                guide_surf = font_guide.render("[ 휠 스크롤: 줌 인/아웃 | 클릭 또는 ESC: 콕핏 복귀 ]", True, (255, 255, 255))
                
                # 가이드 텍스트 위치
                guide_rect = guide_surf.get_rect(center=(settings.width // 2, settings.height - 80))
                
                # 반투명 어두운 배경 판넬 및 흰색 테두리 그리기
                pad_x = 20
                pad_y = 10
                box_rect = pygame.Rect(guide_rect.x - pad_x, guide_rect.y - pad_y, guide_rect.width + pad_x*2, guide_rect.height + pad_y*2)
                
                box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(box_surf, (15, 8, 3, 220), (0, 0, box_rect.width, box_rect.height))
                pygame.draw.rect(box_surf, (255, 255, 255, 160), (0, 0, box_rect.width, box_rect.height), 1)
                
                settings.screen.blit(box_surf, (box_rect.x, box_rect.y))
                
                # 텍스트 그리기
                settings.screen.blit(guide_surf, guide_rect)
                
            elif settings.view_mode == "TRANSITION":
                # UI 페이드 표면 생성
                ui_surf = pygame.Surface((settings.width, settings.height), pygame.SRCALPHA)
                
                panel_w = int(settings.width * 0.3375)
                panel_h = int(settings.height * 0.18)
                panel_x = int(settings.width * 0.03)
                panel_y = int(settings.height * 0.08)
                
                title_panel = pygame.Surface((panel_w, panel_h))
                title_panel.fill((20, 10, 5))
                pygame.draw.rect(title_panel, CRT_GREEN, (0, 0, panel_w, panel_h), 2)
                pygame.draw.rect(title_panel, CRT_GREEN, (4, 4, panel_w - 8, panel_h - 8), 1)
                
                pygame.draw.line(title_panel, CRT_BRIGHT, (0, 0), (12, 12), 2)
                pygame.draw.line(title_panel, CRT_BRIGHT, (panel_w, 0), (panel_w - 12, 12), 2)
                pygame.draw.line(title_panel, CRT_BRIGHT, (0, panel_h), (12, panel_h - 12), 2)
                pygame.draw.line(title_panel, CRT_BRIGHT, (panel_w, panel_h), (panel_w - 12, panel_h - 12), 2)
                
                ui_surf.blit(title_panel, (panel_x, panel_y))
                
                font_title = get_scaled_font(36)
                title_main = font_title.render("SPACE ADVENTURE", True, CRT_BRIGHT)
                title_rect = title_main.get_rect()
                title_rect.centerx = panel_x + (panel_w // 2)
                title_rect.centery = panel_y + (panel_h // 2)
                ui_surf.blit(title_main, title_rect)
                
                for btn in menu_buttons:
                    btn.draw(ui_surf, time_ms)
                trophy_button.draw(ui_surf)
                settings_button.draw(ui_surf)
                
                console.update()
                console.draw(ui_surf)
                
                # UI를 투명도와 함께 블릿
                ui_surf.set_alpha(int((1.0 - settings.transition_progress) * 255))
                settings.screen.blit(ui_surf, (0, 0))
            
        elif settings.state == "SETTINGS":
            # 설정 패널
            panel_w = int(settings.width * 0.45)
            panel_h = int(settings.height * 0.76)
            panel_x = int(settings.width * 0.28)
            panel_y = int(settings.height * 0.12)
            
            panel = pygame.Surface((panel_w, panel_h))
            panel.fill((20, 10, 5))
            pygame.draw.rect(panel, CRT_GREEN, (0, 0, panel_w, panel_h), 2)
            pygame.draw.rect(panel, CRT_GREEN, (4, 4, panel_w - 8, panel_h - 8), 1)
            
            font_sett = get_scaled_font(30)
            title_surf = font_sett.render("[ SYSTEM CONFIGURATION ]", True, CRT_BRIGHT)
            panel.blit(title_surf, (30, 30))
            pygame.draw.line(panel, CRT_GREEN, (30, 75), (panel_w - 30, 75), 1)
            
            settings.screen.blit(panel, (panel_x, panel_y))
            
            # 설정 요소 그리기
            for comp in settings_components:
                comp.draw(settings.screen)
                if hasattr(comp, 'update_rect'):
                    comp.update_rect()
                    
        elif settings.state == "GAME":
            panel_w = int(settings.width * 0.70)
            panel_h = int(settings.height * 0.50)
            panel_x = int(settings.width * 0.15)
            panel_y = int(settings.height * 0.25)
            
            panel = pygame.Surface((panel_w, panel_h))
            panel.fill((15, 8, 5))
            pygame.draw.rect(panel, CRT_GREEN, (0, 0, panel_w, panel_h), 2)
            pygame.draw.rect(panel, CRT_GREEN, (4, 4, panel_w - 8, panel_h - 8), 1)
            
            settings.screen.blit(panel, (panel_x, panel_y))
            
            for comp in game_components:
                comp.draw(settings.screen)
                
        elif settings.state == "ACHIEVEMENTS":
            # 아카이브 패널
            panel_w = int(settings.width * 0.88)
            panel_h = int(settings.height * 0.78)
            panel_x = int(settings.width * 0.06)
            panel_y = int(settings.height * 0.10)
            
            panel = pygame.Surface((panel_w, panel_h))
            panel.fill((20, 10, 5))
            pygame.draw.rect(panel, CRT_GREEN, (0, 0, panel_w, panel_h), 2)
            pygame.draw.rect(panel, CRT_GREEN, (4, 4, panel_w - 8, panel_h - 8), 1)
            
            font_title = get_scaled_font(28, is_korean=True)
            title_surf = font_title.render("[ 엔딩 및 업적 둘러보기 ]", True, CRT_BRIGHT)
            panel.blit(title_surf, (30, 25))
            pygame.draw.line(panel, CRT_GREEN, (30, 65), (panel_w - 30, 65), 1)
            
            settings.screen.blit(panel, (panel_x, panel_y))
            
            # --- 1. 엔딩 목록 렌더링 (좌측) ---
            left_x = panel_x + 30
            start_y = panel_y + 85
            
            font_sub = get_scaled_font(18, is_korean=True)
            endings_header = font_sub.render("[ 엔딩 데이터베이스 ]", True, CRT_BRIGHT)
            settings.screen.blit(endings_header, (left_x, start_y))
            
            endings_list = [
                ("ending_a", "엔딩 A: 유토피아 재탄생", "중력 격자를 복구하고 유토피아-II warp 링크를 연결했습니다."),
                ("ending_b", "엔딩 B: 공허 속의 미아", "원자로 폭주로 인해 시스템이 중지되어 우주를 부유하게 되었습니다."),
                ("ending_c", "엔딩 C: 인공지능의 반란", "터미널 AI가 통제권을 가져가며 인간 크루의 접속을 영구 차단했습니다."),
                ("ending_d", "엔딩 D: 지구의 메아리", "고대 통신 로그를 해독하고 과거 인류의 행성으로 갈 좌표를 얻었습니다.")
            ]
            
            box_w = int(panel_w * 0.43)
            box_h = int(panel_h * 0.13)
            gap = int(panel_h * 0.02)
            
            font_item_title = get_scaled_font(15, is_korean=True)
            font_item_desc = get_scaled_font(12, is_korean=True)
            
            for i, (key, title, desc) in enumerate(endings_list):
                item_y = start_y + 35 + i * (box_h + gap)
                unlocked = progress.is_ending_unlocked(key)
                
                item_surf = pygame.Surface((box_w, box_h))
                item_surf.fill((25, 12, 6) if unlocked else (15, 8, 4))
                border_col = CRT_GREEN if unlocked else GRAY
                pygame.draw.rect(item_surf, border_col, (0, 0, box_w, box_h), 1)
                
                if unlocked:
                    t_surf = font_item_title.render(f"🎬 {title}", True, CRT_BRIGHT)
                    d_surf = font_item_desc.render(desc, True, WHITE)
                    item_surf.blit(t_surf, (15, 12))
                    item_surf.blit(d_surf, (15, box_h - 28))
                else:
                    t_surf = font_item_title.render("🔒 [ 기밀 아카이브 ]", True, GRAY)
                    d_surf = font_item_desc.render("해금 조건: 시뮬레이션 플레이 중 획득", True, DARK_GRAY)
                    item_surf.blit(t_surf, (15, 12))
                    item_surf.blit(d_surf, (15, box_h - 28))
                    
                settings.screen.blit(item_surf, (left_x, item_y))
                
            # --- 2. 업적 목록 렌더링 (우측) ---
            right_x = panel_x + panel_w // 2 + 15
            
            achieve_header = font_sub.render("[ 미션 및 업적 ]", True, CRT_BRIGHT)
            settings.screen.blit(achieve_header, (right_x, start_y))
            
            achievements_list = [
                ("first_boot", "시스템 첫 가동", "콘솔 시스템을 성공적으로 부팅시켰습니다.", "기기 부팅하기", False),
                ("quantum_engineer", "양자 엔지니어", "화면 해상도를 최대 규격으로 설정했습니다.", "설정에서 해상도를 1600x900으로 조절", False),
                ("muted_silence", "음소거 침묵", "콘솔 마스터 볼륨을 완전히 음소거했습니다.", "설정에서 볼륨 강도를 0%로 조절", False),
                ("warp_overload", "워프 드라이브 과부하", "원자로 출력을 설계 한계 이상으로 초과시켰습니다.", "원자로 가동율 100% 한계 돌파", True),
                ("meteor_survivor", "소나기 속의 생존자", "운석 소나기를 30초 동안 버텨냈습니다.", "미니게임: 운석 소나기 클리어", False),
                ("utopian_pioneer", "유토피아 개척자", "성공적으로 워프 시퀀스를 완수했습니다.", "엔딩 A 잠금 해제", True)
            ]
            
            ach_box_h = int(panel_h * 0.10)
            ach_gap = int(panel_h * 0.015)
            
            for i, (key, title, desc, cond, is_hidden) in enumerate(achievements_list):
                item_y = start_y + 35 + i * (ach_box_h + ach_gap)
                unlocked = progress.is_achievement_unlocked(key)
                
                item_surf = pygame.Surface((box_w, ach_box_h))
                item_surf.fill((25, 12, 6) if unlocked else (15, 8, 4))
                border_col = CRT_GREEN if unlocked else GRAY
                pygame.draw.rect(item_surf, border_col, (0, 0, box_w, ach_box_h), 1)
                
                if unlocked:
                    t_surf = font_item_title.render(f"🏆 {title}", True, CRT_BRIGHT)
                    d_surf = font_item_desc.render(desc, True, WHITE)
                    item_surf.blit(t_surf, (15, 8))
                    item_surf.blit(d_surf, (15, ach_box_h - 22))
                else:
                    if is_hidden:
                        t_surf = font_item_title.render("🔒 [ 기밀 기증 아카이브 ]", True, GRAY)
                        d_surf = font_item_desc.render("[ 접근 권한 제한됨 / 히든 미션 ]", True, DARK_GRAY)
                        item_surf.blit(t_surf, (15, 8))
                        item_surf.blit(d_surf, (15, ach_box_h - 22))
                    else:
                        t_surf = font_item_title.render(f"🔒 {title} [잠김]", True, GRAY)
                        d_surf = font_item_desc.render(f"해금 조건: {cond}", True, DARK_GRAY)
                        item_surf.blit(t_surf, (15, 8))
                        item_surf.blit(d_surf, (15, ach_box_h - 22))
                        
                settings.screen.blit(item_surf, (right_x, item_y))
                
            # --- 3. BACK 버튼 그리기 ---
            for btn in achievements_buttons:
                btn.draw(settings.screen, time_ms)
                
        elif settings.state == "MINIGAMES":
            # 미니게임 허브 패널
            panel_w = int(settings.width * 0.88)
            panel_h = int(settings.height * 0.78)
            panel_x = int(settings.width * 0.06)
            panel_y = int(settings.height * 0.10)
            
            panel = pygame.Surface((panel_w, panel_h))
            panel.fill((20, 10, 5))
            pygame.draw.rect(panel, CRT_GREEN, (0, 0, panel_w, panel_h), 2)
            pygame.draw.rect(panel, CRT_GREEN, (4, 4, panel_w - 8, panel_h - 8), 1)
            
            font_title = get_scaled_font(28, is_korean=True)
            title_surf = font_title.render("[ UTOPIA MINI GAME HUB ]", True, CRT_BRIGHT)
            panel.blit(title_surf, (30, 25))
            pygame.draw.line(panel, CRT_GREEN, (30, 65), (panel_w - 30, 65), 1)
            
            settings.screen.blit(panel, (panel_x, panel_y))
            
            # 3개 카드 가로 배치
            card_w = int(panel_w * 0.27)
            card_h = int(panel_h * 0.48)
            gap = int(panel_w * 0.035)
            start_x = panel_x + int(panel_w * 0.06)
            card_y = panel_y + int(panel_h * 0.20)
            
            font_card_title = get_scaled_font(15, is_korean=True)
            font_card_desc = get_scaled_font(12, is_korean=True)
            
            games_list = [
                ("WARP DUST AVOID", "워프 먼지 피하기", "우주선에 다가오는 워프 먼지들을 피해 생존하는 미니게임입니다.", "[ 대기 중 - 모듈 로드 필요 ]"),
                ("METEOR SHOWER", "운석 소나기", "안전 보호막이 손상된 구역에서 쏟아지는 운석을 피합니다.", "[ 모듈 로드 완료 - 클릭하여 실행 ]"),
                ("REACTOR REPAIR", "원자로 긴급 수리", "제한 시간 내에 과부하된 원자로 노드를 복구합니다.", "[ 준비 중 - 차후 업로드 ]")
            ]
            
            for i, (eng, kor, desc, status) in enumerate(games_list):
                cx = start_x + i * (card_w + gap)
                
                # 카드 배경 및 더블 테두리
                card_surf = pygame.Surface((card_w, card_h))
                card_surf.fill((15, 8, 4))
                pygame.draw.rect(card_surf, GRAY, (0, 0, card_w, card_h), 1)
                pygame.draw.rect(card_surf, DARK_GRAY, (4, 4, card_w - 8, card_h - 8), 1)
                
                # 카드 타이틀
                e_surf = font_card_desc.render(eng, True, GRAY)
                k_surf = font_card_title.render(kor, True, CRT_BRIGHT)
                card_surf.blit(e_surf, (15, 15))
                card_surf.blit(k_surf, (15, 35))
                
                # 장식선
                pygame.draw.line(card_surf, DARK_GRAY, (15, 62), (card_w - 15, 62), 1)
                
                # 설명 문장 단락 분리 출력 (줄바꿈 대응)
                if i == 0:
                    d_surf1 = font_card_desc.render("우주선에 다가오는", True, WHITE)
                    d_surf2 = font_card_desc.render("워프 먼지들을 피해", True, WHITE)
                    d_surf3 = font_card_desc.render("생존하는 미니게임.", True, WHITE)
                    card_surf.blit(d_surf1, (15, 80))
                    card_surf.blit(d_surf2, (15, 100))
                    card_surf.blit(d_surf3, (15, 120))
                elif i == 1:
                    d_surf1 = font_card_desc.render("안전 보호막이 손상된", True, WHITE)
                    d_surf2 = font_card_desc.render("구역에서 쏟아지는", True, WHITE)
                    d_surf3 = font_card_desc.render("운석을 피합니다.", True, WHITE)
                    card_surf.blit(d_surf1, (15, 80))
                    card_surf.blit(d_surf2, (15, 100))
                    card_surf.blit(d_surf3, (15, 120))
                else:
                    d_surf1 = font_card_desc.render("제한 시간 내에", True, WHITE)
                    d_surf2 = font_card_desc.render("과부하된 원자로", True, WHITE)
                    d_surf3 = font_card_desc.render("노드를 복구합니다.", True, WHITE)
                    card_surf.blit(d_surf1, (15, 80))
                    card_surf.blit(d_surf2, (15, 100))
                    card_surf.blit(d_surf3, (15, 120))
                    
                # 상태 표시
                status_surf = font_card_desc.render(status, True, CRT_GREEN if i in [0, 1] else GRAY)
                card_surf.blit(status_surf, (15, card_h - 30))
                
                settings.screen.blit(card_surf, (cx, card_y))
                
            # 뒤로가기 버튼
            for btn in minigames_buttons:
                btn.draw(settings.screen, time_ms)
        elif settings.state == "METEOR_GAME":
            meteor_game.draw(settings.screen)
        
        # 3. 브라운관 전자 빔 및 스캔라인/비네팅 오버레이 필터
        beam.draw(settings.screen)
        scanlines.draw(settings.screen)
        
        # 4. 하단 스테이터스 워터마크
        font_watermark = get_scaled_font(13)
        credit_surf = font_watermark.render("UTOPIA-II MODULE V2.1 // SYS_RES: {}x{}".format(settings.width, settings.height), True, CRT_GREEN)
        settings.screen.blit(credit_surf, (settings.width - credit_surf.get_width() - 30, settings.height - 30))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
