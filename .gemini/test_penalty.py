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

from main import GameSettings, settings

class MockResourcesGame:
    def __init__(self):
        self.resources = {"산소": 100, "전기": 100, "정신력": 100}
        self.my_crew = ["의사", "기술자", "경찰", "천문학자"]

settings.resources_game = MockResourcesGame()
sys.modules['main'].resources_game = settings.resources_game

try:
    print("Testing Stage 2 Overheat penalty...")
    from stage_2_overheat import CoreThermalStabilizerGame
    overheat_game = CoreThermalStabilizerGame()
    overheat_game.state = "FAIL"
    overheat_game.has_mechanic = True
    
    # Select penalty 2: Oxygen decrease by 50
    overheat_game.penalty_selected = 2
    
    print(f"Before penalty: Oxygen = {settings.resources_game.resources['산소']}")
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    overheat_game.handle_event(event)
    print(f"After penalty: Oxygen = {settings.resources_game.resources['산소']}")
    assert settings.resources_game.resources["산소"] == 50
    
    print("Testing Stage 2 Robot penalty...")
    from stage_2_robot import RogueRobotGame
    robot_game = RogueRobotGame()
    robot_game.state = "FAIL"
    robot_game.has_police = True
    
    # Select penalty 1: Police died
    robot_game.penalty_selected = 1
    
    print(f"Before penalty: Crew = {settings.resources_game.my_crew}")
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    robot_game.handle_event(event)
    print(f"After penalty: Crew = {settings.resources_game.my_crew}")
    assert "경찰" not in settings.resources_game.my_crew

    print("Testing spin.py landing success penalty (all to 1)...")
    from spin import CrankLandingGame
    spin_game = CrankLandingGame()
    spin_game.progress_gauge = 101.0
    
    print(f"Before landing: state={spin_game.state}, gauge={spin_game.progress_gauge}, resources={settings.resources_game.resources}")
    
    # Trigger update
    spin_game.update()
    
    print(f"After landing: state={spin_game.state}, resources={settings.resources_game.resources}")
    for k, v in settings.resources_game.resources.items():
        assert v == 1

    print("All penalty applications tested: SUCCESS with no crashes!")

except Exception as e:
    import traceback
    traceback.print_exc()
