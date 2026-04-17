"""
Progress bar component with animated fill.
"""

import pygame
from typing import Tuple

from core.constants import Colors


class ProgressBar:
    """Horizontal or vertical progress bar with animation."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 value: float = 0.0, max_value: float = 100.0,
                 bg_color: Tuple[int, int, int] = Colors.PANEL,
                 fill_color: Tuple[int, int, int] = Colors.ACCENT,
                 border_color: Tuple[int, int, int] = Colors.BORDER,
                 border_radius: int = 8, vertical: bool = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = value
        self.max_value = max_value
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.vertical = vertical
        
        self.display_value = value  # For animation
        self.animation_speed = 0.2  # Speed of fill animation
    
    def set_value(self, value: float, animate: bool = True):
        """Set the progress value."""
        self.value = max(0, min(value, self.max_value))
        if not animate:
            self.display_value = self.value
    
    def get_progress(self) -> float:
        """Get progress as a ratio (0.0 to 1.0)."""
        if self.max_value == 0:
            return 0.0
        return self.display_value / self.max_value
    
    def update(self, dt: float):
        """Update animation."""
        target = self.value
        
        # Smooth animation
        diff = target - self.display_value
        if abs(diff) > 0.01:
            self.display_value += diff * self.animation_speed
        else:
            self.display_value = target
    
    def draw(self, surface: pygame.Surface):
        """Draw the progress bar."""
        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, bg_rect, 
                        border_radius=self.border_radius)
        
        # Draw fill
        progress = self.get_progress()
        if progress > 0:
            if self.vertical:
                # Vertical bar
                fill_height = int(self.height * progress)
                fill_rect = pygame.Rect(self.x, 
                                       self.y + self.height - fill_height,
                                       self.width, 
                                       fill_height)
            else:
                # Horizontal bar
                fill_width = int(self.width * progress)
                fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            
            pygame.draw.rect(surface, self.fill_color, fill_rect, 
                            border_radius=self.border_radius)
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, bg_rect, 2, 
                        border_radius=self.border_radius)
    
    def get_rect(self) -> pygame.Rect:
        """Get the progress bar's rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_complete(self) -> bool:
        """Check if progress is at 100%."""
        return self.value >= self.max_value
