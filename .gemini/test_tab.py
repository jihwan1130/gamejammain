import pygame
import sys
import os
import importlib.util

# Inject sys.path first to ensure local imports work
sys.path.insert(0, r"C:\Users\1yo1x\OneDrive\바탕 화면\gamejammain")

# Initialize pygame normally
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((1000, 700))

# Manually load main.py as both 'main' and '__main__' to satisfy the sys.modules trick in main.py
main_path = r"C:\Users\1yo1x\OneDrive\바탕 화면\gamejammain\main.py"
spec = importlib.util.spec_from_file_location("main", main_path)
main_mod = importlib.util.module_from_spec(spec)
sys.modules['main'] = main_mod
sys.modules['__main__'] = main_mod
spec.loader.exec_module(main_mod)

from main import GameSettings, settings, get_scaled_font, CRT_GREEN, CRT_BRIGHT, WHITE, GRAY

try:
    print("Testing TAB key overlay rendering with Day progress bar...")
    
    # Setup mock settings state
    settings.fullscreen = False
    settings.width = 1000
    settings.height = 700
    settings.state = "DAY_1"
    settings.is_campaign = True
    settings.current_day = 7 # Test day 7 progress
    
    # Mock resources game instance in settings
    class MockResourcesGame:
        def __init__(self):
            self.resources = {"산소": 120, "전기": 95, "정신력": 150}
            self.my_crew = ["의사", "기술자", "경찰", "천문학자", "개발자", "전기 기술자"]
            
    settings.resources_game = MockResourcesGame()
    
    screen.fill((5, 15, 5))
    
    # Simulated TAB key logic rendering directly
    print("Drawing panel surface...")
    panel_w = int(settings.width * 0.6)
    panel_h = int(settings.height * 0.6)
    panel_x = (settings.width - panel_w) // 2
    panel_y = (settings.height - panel_h) // 2
    
    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (15, 8, 3, 230), (0, 0, panel_w, panel_h), border_radius=10)
    pygame.draw.rect(panel_surf, CRT_GREEN, (0, 0, panel_w, panel_h), 3, border_radius=10)
    pygame.draw.rect(panel_surf, CRT_BRIGHT, (4, 4, panel_w - 8, panel_h - 8), 1, border_radius=8)
    
    # Title
    title_font = get_scaled_font(22, is_korean=True)
    title_surf = title_font.render("📋 수집 자원 및 크루 목록 (TAB)", True, CRT_BRIGHT)
    panel_surf.blit(title_surf, (panel_w // 2 - title_surf.get_width() // 2, 25))
    
    res = settings.resources_game.resources
    crew = settings.resources_game.my_crew
    
    content_font = get_scaled_font(18, is_korean=True)
    sub_font = get_scaled_font(14, is_korean=True)
    
    # Progress bar
    y_offset = 70
    progress_lbl = content_font.render("■ 우주선 항해 진행도", True, CRT_GREEN)
    panel_surf.blit(progress_lbl, (40, y_offset))
    y_offset += 30
    
    curr_day = settings.current_day
    day_percent = int(curr_day * 10)
    
    pbar_x = 120
    pbar_w = 380
    pbar_h = 16
    pygame.draw.rect(panel_surf, (30, 15, 5), (pbar_x, y_offset + 2, pbar_w, pbar_h))
    pygame.draw.rect(panel_surf, CRT_GREEN, (pbar_x, y_offset + 2, pbar_w, pbar_h), 1)
    
    pfill_w = int(pbar_w * (curr_day / 10.0))
    if pfill_w > 0:
        pygame.draw.rect(panel_surf, CRT_BRIGHT, (pbar_x + 2, y_offset + 4, pfill_w - 4, pbar_h - 4))
        
    day_lbl_left = sub_font.render("Day 0", True, WHITE)
    panel_surf.blit(day_lbl_left, (pbar_x - day_lbl_left.get_width() - 10, y_offset))
    
    day_lbl_right = sub_font.render("Day 10", True, WHITE)
    panel_surf.blit(day_lbl_right, (pbar_x + pbar_w + 10, y_offset))
    
    y_offset += 22
    status_str = f"▶ 현재: {curr_day}일차 항해 중 ({day_percent}% 돌파)"
    status_surf = sub_font.render(status_str, True, CRT_BRIGHT)
    panel_surf.blit(status_surf, (pbar_x, y_offset))
    
    # Resources
    y_offset += 38
    res_lbl = content_font.render("■ 보유 자원 현황", True, CRT_GREEN)
    panel_surf.blit(res_lbl, (40, y_offset))
    y_offset += 35
    
    for rname, rval in res.items():
        lbl_text = f"{rname}: {rval}/200"
        r_text_surf = sub_font.render(lbl_text, True, WHITE)
        panel_surf.blit(r_text_surf, (50, y_offset))
        
        bar_x = 180
        bar_w = 320
        bar_h = 16
        pygame.draw.rect(panel_surf, (30, 15, 5), (bar_x, y_offset + 2, bar_w, bar_h))
        pygame.draw.rect(panel_surf, CRT_GREEN, (bar_x, y_offset + 2, bar_w, bar_h), 1)
        
        fill_w = int(bar_w * (min(200, rval) / 200.0))
        if fill_w > 0:
            pygame.draw.rect(panel_surf, CRT_GREEN, (bar_x + 2, y_offset + 4, fill_w - 4, bar_h - 4))
            
        y_offset += 30
    
    # Crew
    y_offset += 15
    crew_lbl = content_font.render("■ 탑승 크루 목록", True, CRT_GREEN)
    panel_surf.blit(crew_lbl, (40, y_offset))
    y_offset += 35
    
    crew_str = ", ".join(crew) if crew else "없음 (수집된 크루가 없습니다)"
    crew_words_surf = sub_font.render(crew_str, True, WHITE)
    if crew_words_surf.get_width() > panel_w - 100:
        words = crew_str.split(", ")
        line1 = ", ".join(words[:4])
        line2 = ", ".join(words[4:])
        
        c_surf1 = sub_font.render(line1, True, WHITE)
        panel_surf.blit(c_surf1, (50, y_offset))
        y_offset += 25
        if line2:
            c_surf2 = sub_font.render(line2, True, WHITE)
            panel_surf.blit(c_surf2, (50, y_offset))
    else:
        panel_surf.blit(crew_words_surf, (50, y_offset))
        
    tip_font = get_scaled_font(12, is_korean=True)
    tip_surf = tip_font.render("[ TAB 키를 떼면 화면이 닫힙니다 ]", True, GRAY)
    panel_surf.blit(tip_surf, (panel_w // 2 - tip_surf.get_width() // 2, panel_h - 30))
    
    screen.blit(panel_surf, (panel_x, panel_y))
    pygame.display.flip()
    
    print("Overlay rendering simulation: SUCCESS with no crashes!")

except Exception as e:
    import traceback
    traceback.print_exc()
