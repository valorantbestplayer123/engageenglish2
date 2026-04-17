"""
Resource manager for loading assets with PyInstaller compatibility.
Handles fonts, images, and sounds.
"""

import os
import sys
import pygame
from typing import Dict, Optional

from constants import FONT_SELFIE, FONT_FALLBACK


class ResourceManager:
    """Manages loading and caching of game assets."""
    
    def __init__(self):
        self._fonts: Dict[tuple, pygame.font.Font] = {}
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._images: Dict[str, pygame.Surface] = {}
        
    @staticmethod
    def resource_path(relative_path: str) -> str:
        """Get absolute path to resource, works for dev and PyInstaller .exe."""
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def get_font(self, size: int, name: str = FONT_SELFIE, bold: bool = False) -> pygame.font.Font:
        """Get a font with specified size and style."""
        key = (name, size, bold)
        
        if key not in self._fonts:
            try:
                font_path = self.resource_path(name)
                if os.path.exists(font_path):
                    self._fonts[key] = pygame.font.Font(font_path, size)
                else:
                    # Fallback to system font
                    font_name = FONT_FALLBACK
                    self._fonts[key] = pygame.font.SysFont(font_name, size, bold=bold)
            except Exception:
                # System font fallback
                font_name = FONT_FALLBACK
                self._fonts[key] = pygame.font.SysFont(font_name, size, bold=bold)
        
        return self._fonts[key]
    
    def get_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """Load and cache a sound effect."""
        if path not in self._sounds:
            try:
                sound_path = self.resource_path(path)
                if os.path.exists(sound_path):
                    self._sounds[path] = pygame.mixer.Sound(sound_path)
                else:
                    return None
            except Exception:
                return None
        
        return self._sounds[path]
    
    def get_image(self, path: str) -> Optional[pygame.Surface]:
        """Load and cache an image."""
        if path not in self._images:
            try:
                image_path = self.resource_path(path)
                if os.path.exists(image_path):
                    self._images[path] = pygame.image.load(image_path).convert_alpha()
                else:
                    return None
            except Exception:
                return None
        
        return self._images[path]
    
    def play_sound(self, path: str, volume: float = 1.0) -> bool:
        """Play a sound effect."""
        sound = self.get_sound(path)
        if sound:
            sound.set_volume(volume)
            sound.play()
            return True
        return False
    
    def clear_cache(self):
        """Clear all cached resources."""
        self._fonts.clear()
        self._sounds.clear()
        self._images.clear()


# Global instance
_resource_manager = ResourceManager()


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    return _resource_manager
