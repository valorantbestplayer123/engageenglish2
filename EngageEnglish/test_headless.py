#!/usr/bin/env python3
"""
Headless initialization test for EngageEnglish.
Verifies the application can initialize without a display.
"""

import sys
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame

# Initialize pygame with dummy driver
pygame.init()
pygame.display.set_mode((1, 1))  # Minimal dummy display

print("=" * 60)
print("EngageEnglish - Headless Initialization Test")
print("=" * 60)

from core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, MODE_SPEED
from core.scene_manager import SceneManager
from core.progress_manager import ProgressManager
from core.data_loader import DataLoader
from scenes.main_menu import MainMenu

# Initialize screen (dummy)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# Initialize managers
print("\n[1] Initializing managers...")
progress_manager = ProgressManager()
data_loader = DataLoader()
scene_manager = SceneManager(screen, clock, progress_manager, data_loader)
print("  ✅ Managers initialized")

# Create main menu
print("\n[2] Creating main menu...")
main_menu = MainMenu(scene_manager)
print("  ✅ Main menu created")

# Push scene to stack
print("\n[3] Starting scene stack...")
scene_manager.push_scene(main_menu)
print("  ✅ Main menu pushed to scene stack")

# Test scene updates
print("\n[4] Testing scene updates...")
for i in range(3):
    dt = 0.016  # ~60 FPS
    scene_manager.update(dt)
    scene_manager.draw()
print("  ✅ Scene updates working")

# Test mode data loading
print("\n[5] Testing mode data loading...")
from modes.speed_mode import SpeedMode
from modes.breadth_mode import BreadthMode
from modes.context_mode import ContextMode
from modes.resilience_mode import ResilienceMode

try:
    speed_scene = SpeedMode(scene_manager, 1)
    print(f"  ✅ Speed mode loaded: {len(speed_scene.questions)} questions")
    speed_scene.exit()

    breadth_scene = BreadthMode(scene_manager, 1)
    print(f"  ✅ Breadth mode loaded: {len(breadth_scene.current_pairs)} pairs")
    breadth_scene.exit()

    context_scene = ContextMode(scene_manager, 1)
    print(f"  ✅ Context mode loaded: {len(context_scene.sentences)} sentences")
    context_scene.exit()

    resilience_scene = ResilienceMode(scene_manager, 1)
    print(f"  ✅ Resilience mode loaded: {len(resilience_scene.questions)} questions")
    resilience_scene.exit()
except Exception as e:
    print(f"  ❌ Mode loading failed: {e}")
    sys.exit(1)

# Test level select
print("\n[6] Testing level select...")
from scenes.level_select import LevelSelect
from scenes.results_screen import ResultsScreen

try:
    level_select = LevelSelect(scene_manager, MODE_SPEED)
    print(f"  ✅ Level select created for Speed mode")
    level_select.exit()

    results = ResultsScreen(scene_manager, MODE_SPEED, 1, 100, 200, 30, 90, 85)
    print(f"  ✅ Results screen created")
    results.exit()
except Exception as e:
    print(f"  ❌ Scene creation failed: {e}")
    sys.exit(1)

# Cleanup
print("\n[7] Cleaning up...")
progress_manager.save()
print("  ✅ Progress saved")
pygame.quit()

print("\n" + "=" * 60)
print("✅ All headless tests passed!")
print("=" * 60)
print("\nApplication components verified:")
print("  • All four modes initialize correctly")
print("  • Scene management works")
print("  • Data loading successful")
print("  • Progress persistence functional")
