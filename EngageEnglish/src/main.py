#!/usr/bin/env python3
"""
EngageEnglish v4 - Premium Pygame Application
Four proficiency-based modes with modern flat UI and smooth transitions.
"""

import sys
import os
import pygame

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.constants import *
from core.scene_manager import SceneManager
from scenes.main_menu import MainMenu
from core.progress_manager import ProgressManager
from core.data_loader import DataLoader

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller .exe"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    """Main application entry point."""
    pygame.init()
    pygame.display.set_caption("EngageEnglish - Premium Vocabulary Trainer")
    
    # Initialize screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    
    # Initialize managers
    progress_manager = ProgressManager()
    data_loader = DataLoader()
    scene_manager = SceneManager(screen, clock, progress_manager, data_loader)
    
    # Start with main menu
    scene_manager.push_scene(MainMenu(scene_manager))
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)
        
        scene_manager.update(dt)
        scene_manager.draw()
        pygame.display.flip()
    
    # Save progress on exit
    progress_manager.save()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
