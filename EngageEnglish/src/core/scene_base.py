"""
Base scene class for all game scenes.
Provides interface for scene lifecycle management.
"""

from abc import ABC, abstractmethod
import pygame


class SceneBase(ABC):
    """Abstract base class for all scenes."""
    
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.screen = scene_manager.screen
        self.clock = scene_manager.clock
        self.progress_manager = scene_manager.progress_manager
        self.data_loader = scene_manager.data_loader
        self.resource_manager = scene_manager.resource_manager
        
        self.entered = False
        self.exited = False
    
    @abstractmethod
    def enter(self):
        """Called when scene is pushed onto the stack."""
        self.entered = True
        self.exited = False
    
    @abstractmethod
    def exit(self):
        """Called when scene is popped from the stack."""
        self.exited = True
    
    @abstractmethod
    def update(self, dt: float):
        """Update scene logic. dt is delta time in seconds."""
        pass
    
    @abstractmethod
    def draw(self):
        """Draw scene to screen."""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        pass
    
    def is_active(self) -> bool:
        """Check if scene is currently active (entered and not exited)."""
        return self.entered and not self.exited
