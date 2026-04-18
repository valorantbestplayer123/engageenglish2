"""
Timer component with visual countdown and urgency states.
"""

import pygame
from typing import Tuple

from core.constants import Colors, QUESTION_TIME_SECONDS, FONT_SIZE_HEADER


class Timer:
    """Visual countdown timer with color-coded urgency."""
    
    def __init__(self, x: int, y: int, max_time: float = QUESTION_TIME_SECONDS,
                 font_size: int = FONT_SIZE_HEADER):
        self.x = x
        self.y = y
        self.max_time = max_time
        self.current_time = max_time
        self.font_size = font_size
        self.running = False
        
        # Urgency thresholds (percentage of max_time)
        self.urgency_high = 0.3   # Below 30% - red
        self.urgency_med = 0.6    # Below 60% - gold
        self.urgency_low = 1.0    # Below 100% - normal (teal/green)
    
    def start(self):
        """Start the timer."""
        self.current_time = self.max_time
        self.running = True
    
    def stop(self):
        """Stop the timer."""
        self.running = False
    
    def reset(self):
        """Reset the timer to max time."""
        self.current_time = self.max_time
        self.running = False
    
    def set_time(self, time: float):
        """Set the current time."""
        self.current_time = max(0, min(time, self.max_time))
    
    def update(self, dt: float):
        """Update timer."""
        if self.running and self.current_time > 0:
            self.current_time -= dt
            if self.current_time < 0:
                self.current_time = 0
    
    def get_remaining_ratio(self) -> float:
        """Get remaining time as ratio (0.0 to 1.0)."""
        if self.max_time == 0:
            return 0.0
        return self.current_time / self.max_time
    
    def get_color(self) -> Tuple[int, int, int]:
        """Get color based on urgency."""
        ratio = self.get_remaining_ratio()
        
        if ratio <= self.urgency_high:
            return Colors.RED
        elif ratio <= self.urgency_med:
            return Colors.GOLD
        else:
            return Colors.GREEN
    
    def draw(self, surface: pygame.Surface, resource_manager):
        """Draw the timer."""
        # Get color based on urgency
        color = self.get_color()
        
        # Render time text
        font = resource_manager.get_font(self.font_size)
        time_text = f"{self.current_time:.1f}s"
        text_surf = font.render(time_text, True, color)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        
        # Draw text
        surface.blit(text_surf, text_rect)
        
        # Draw progress ring
        center_x, center_y = self.x, self.y
        radius = self.font_size + 10
        
        # Background ring
        pygame.draw.circle(surface, Colors.PANEL, (center_x, center_y), radius, 4)
        
        # Progress arc
        if self.get_remaining_ratio() > 0:
            # Draw arc (pygame doesn't have arc with thickness, so we use a workaround)
            # For simplicity, we'll just draw a colored circle that shrinks
            progress_radius = int(radius * self.get_remaining_ratio())
            if progress_radius > 0:
                pygame.draw.circle(surface, color, (center_x, center_y), progress_radius, 4)
    
    def is_time_up(self) -> bool:
        """Check if time has run out."""
        return self.current_time <= 0
    
    def get_time_left(self) -> float:
        """Get remaining time."""
        return self.current_time
