"""
Screen transition effects for smooth scene changes.
Supports fade, slide, and scale transitions.
"""

import pygame
from typing import Callable, Optional, Tuple
from enum import Enum

from core.constants import TRANSITION_FADE_DURATION, TRANSITION_SLIDE_DURATION


class TransitionType(Enum):
    """Types of transitions."""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"


class Transition:
    """Handles animated screen transitions."""
    
    def __init__(self, transition_type: TransitionType, duration: float = TRANSITION_FADE_DURATION,
                 on_complete: Optional[Callable] = None):
        self.type = transition_type
        self.duration = duration
        self.on_complete = on_complete
        self.elapsed = 0.0
        self.complete = False
        
        # Surfaces for transition
        self.old_surface: Optional[pygame.Surface] = None
        self.new_surface: Optional[pygame.Surface] = None
    
    def start(self, old_surface: pygame.Surface, new_surface: pygame.Surface):
        """Start the transition with the two surfaces."""
        self.old_surface = old_surface.copy()
        self.new_surface = new_surface.copy()
        self.elapsed = 0.0
        self.complete = False
    
    def update(self, dt: float) -> bool:
        """Update transition animation. Returns True when complete."""
        if self.complete:
            return True
        
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.complete = True
            if self.on_complete:
                self.on_complete()
            return True
        
        return False
    
    def draw(self, screen: pygame.Surface):
        """Draw the transition to screen."""
        if not self.old_surface or not self.new_surface:
            return
        
        progress = self.elapsed / self.duration
        
        if self.type == TransitionType.FADE:
            self._draw_fade(screen, progress)
        elif self.type == TransitionType.SLIDE_LEFT:
            self._draw_slide(screen, progress, -1, 0)
        elif self.type == TransitionType.SLIDE_RIGHT:
            self._draw_slide(screen, progress, 1, 0)
        elif self.type == TransitionType.SLIDE_UP:
            self._draw_slide(screen, progress, 0, -1)
        elif self.type == TransitionType.SLIDE_DOWN:
            self._draw_slide(screen, progress, 0, 1)
        else:
            # Default: just draw new surface
            screen.blit(self.new_surface, (0, 0))
    
    def _draw_fade(self, screen: pygame.Surface, progress: float):
        """Draw fade transition."""
        # Draw old surface fading out
        alpha = int(255 * (1 - progress))
        self.old_surface.set_alpha(alpha)
        screen.blit(self.old_surface, (0, 0))
        
        # Draw new surface fading in
        self.old_surface.set_alpha(255)  # Reset alpha
        self.new_surface.set_alpha(int(255 * progress))
        screen.blit(self.new_surface, (0, 0))
        self.new_surface.set_alpha(255)
    
    def _draw_slide(self, screen: pygame.Surface, progress: float, dx: int, dy: int):
        """Draw slide transition."""
        width, height = screen.get_size()
        
        # Calculate offsets
        offset = int(max(width, height) * progress)
        ox = dx * offset
        oy = dy * offset
        
        # Draw new surface sliding in
        screen.blit(self.new_surface, (ox, oy))
        
        # Draw old surface sliding out
        screen.blit(self.old_surface, (-ox, -oy))
    
    def is_complete(self) -> bool:
        """Check if transition is complete."""
        return self.complete
    
    def get_progress(self) -> float:
        """Get transition progress (0.0 to 1.0)."""
        return min(1.0, self.elapsed / self.duration)
