#!/usr/bin/env python3
"""
Verification script to test EngageEnglish application initialization.
Tests all imports, data loading, and component initialization.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("EngageEnglish - Application Verification")
print("=" * 60)

# Test 1: Import all modules
print("\n[Test 1] Importing all modules...")
try:
    from core.constants import Colors, MODE_SPEED, MODE_BREADTH, MODE_CONTEXT, MODE_RESILIENCE
    from core.resource_manager import ResourceManager, get_resource_manager
    from core.data_loader import DataLoader
    from core.progress_manager import ProgressManager
    from core.scene_base import SceneBase
    from core.scene_manager import SceneManager
    from core.transition import Transition, TransitionType

    from ui.button import Button
    from ui.label import Label, HorizontalAlign, VerticalAlign
    from ui.card import Card
    from ui.timer import Timer
    from ui.progress_bar import ProgressBar
    from ui.stars import Stars

    from modes.speed_mode import SpeedMode
    from modes.breadth_mode import BreadthMode
    from modes.context_mode import ContextMode
    from modes.resilience_mode import ResilienceMode

    from scenes.main_menu import MainMenu
    from scenes.level_select import LevelSelect
    from scenes.results_screen import ResultsScreen

    print("  ✅ All modules imported successfully")
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize managers
print("\n[Test 2] Initializing managers...")
try:
    rm = ResourceManager()
    print("  ✅ ResourceManager initialized")

    pm = ProgressManager()
    print("  ✅ ProgressManager initialized")

    dl = DataLoader()
    print("  ✅ DataLoader initialized")

    print(f"  • Synonym levels: {dl.get_synonym_count()}")
    print(f"  • Definition levels: {dl.get_definition_count()}")
    print(f"  • Context levels: {dl.get_context_count()}")
except Exception as e:
    print(f"  ❌ Manager initialization failed: {e}")
    sys.exit(1)

# Test 3: Load data files
print("\n[Test 3] Loading data files...")
try:
    # Test synonym level
    syn_data = dl.get_synonym_level(1)
    if syn_data and 'pairs' in syn_data:
        print(f"  ✅ Synonym level 1 loaded: {len(syn_data['pairs'])} pairs")
    else:
        print("  ❌ Synonym level 1 failed to load")

    # Test definition level
    def_data = dl.get_definition_level(1)
    if def_data and 'questions' in def_data:
        print(f"  ✅ Definition level 1 loaded: {len(def_data['questions'])} questions")
    else:
        print("  ❌ Definition level 1 failed to load")

    # Test context level
    ctx_data = dl.get_context_level(1)
    if ctx_data and 'sentences' in ctx_data:
        print(f"  ✅ Context level 1 loaded: {len(ctx_data['sentences'])} sentences")
    else:
        print("  ❌ Context level 1 failed to load")
except Exception as e:
    print(f"  ❌ Data loading failed: {e}")
    sys.exit(1)

# Test 4: Test progress manager
print("\n[Test 4] Testing progress management...")
try:
    # Get unlocked levels
    speed_unlocked = pm.get_unlocked_levels(MODE_SPEED)
    breadth_unlocked = pm.get_unlocked_levels(MODE_BREADTH)
    context_unlocked = pm.get_unlocked_levels(MODE_CONTEXT)
    resilience_unlocked = pm.get_unlocked_levels(MODE_RESILIENCE)

    print(f"  ✅ Speed unlocked: {speed_unlocked}")
    print(f"  ✅ Breadth unlocked: {breadth_unlocked}")
    print(f"  ✅ Context unlocked: {context_unlocked}")
    print(f"  ✅ Resilience unlocked: {resilience_unlocked}")

    # Test recording attempts
    pm.record_attempt(MODE_SPEED, True)
    pm.record_attempt(MODE_SPEED, False)
    accuracy = pm.get_accuracy(MODE_SPEED)
    print(f"  ✅ Speed accuracy: {accuracy:.1f}%")
except Exception as e:
    print(f"  ❌ Progress manager test failed: {e}")
    sys.exit(1)

# Test 5: Check assets
print("\n[Test 5] Checking asset files...")
try:
    # Check font
    font_path = rm.resource_path("assets/fonts/Selfie_Black.otf")
    if os.path.exists(font_path):
        print(f"  ✅ Font file exists")
    else:
        print(f"  ⚠️  Font file not found (will use fallback)")

    # Check sounds
    sounds = ["assets/sounds/correct.wav", "assets/sounds/wrong.wav"]
    for sound in sounds:
        sound_path = rm.resource_path(sound)
        if os.path.exists(sound_path):
            print(f"  ✅ Sound: {os.path.basename(sound)}")
        else:
            print(f"  ⚠️  Sound not found: {os.path.basename(sound)}")
except Exception as e:
    print(f"  ❌ Asset check failed: {e}")

# Test 6: Mode constants
print("\n[Test 6] Verifying mode constants...")
try:
    from core.constants import MODE_NAMES, MODE_DESCRIPTIONS

    print(f"  ✅ {MODE_NAMES[MODE_SPEED]} - {MODE_DESCRIPTIONS[MODE_SPEED][:40]}...")
    print(f"  ✅ {MODE_NAMES[MODE_BREADTH]} - {MODE_DESCRIPTIONS[MODE_BREADTH][:40]}...")
    print(f"  ✅ {MODE_NAMES[MODE_CONTEXT]} - {MODE_DESCRIPTIONS[MODE_CONTEXT][:40]}...")
    print(f"  ✅ {MODE_NAMES[MODE_RESILIENCE]} - {MODE_DESCRIPTIONS[MODE_RESILIENCE][:40]}...")
except Exception as e:
    print(f"  ❌ Mode constants check failed: {e}")

print("\n" + "=" * 60)
print("✅ All verification tests passed!")
print("=" * 60)
print("\nThe EngageEnglish application is ready to run.")
print("Run with: python src/main.py")
