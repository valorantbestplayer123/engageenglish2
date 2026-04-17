"""
Button component with hover effects and smooth animations.
"""

import pygame
from typing import Callable, Optional, Tuple

from constants import Colors, BUTTON_RADIUS, BUTTON_HOVER_DURATION


class Button:
    """Modern flat button with hover effects."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 bg_color: Tuple[int, int, int] = Colors.ACCENT,
                 text_color: Tuple[int, int, int] = Colors.WHITE,
                 hover_color: Optional[Tuple[int, int, int]] = None,
                 font_size: int = 24, callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color if hover_color else self._lighten_color(bg_color, 20)
        self.font_size = font_size
        self.callback = callback
        
        self.hovered = False
        self.pressed = False
        self.hover_progress = 0.0  # 0.0 to 1.0
        
        # Animation state
        self.current_bg_color = list(bg_color)
    
    def _lighten_color(self, color: Tuple[int, int, int], amount: int) -> Tuple[int, int, int]:
        """Lighten a color by a given amount."""
        return (
            min(255, color[0] + amount),
            min(255, color[1] + amount),
            min(255, color[2] + amount)
        )
    
    def _interpolate_color(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                           t: float) -> Tuple[int, int, int]:
        """Interpolate between two colors."""
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )
    
    def update(self, dt: float):
        """Update button animation state."""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Animate hover progress
        target = 1.0 if self.hovered else 0.0
        speed = 1.0 / BUTTON_HOVER_DURATION
        if self.hover_progress < target:
            self.hover_progress = min(target, self.hover_progress + speed * dt)
        elif self.hover_progress > target:
            self.hover_progress = max(target, self.hover_progress - speed * dt)
        
        # Update current color
        self.current_bg_color = list(self._interpolate_color(
            self.bg_color, self.hover_color, self.hover_progress
        ))
    
    def draw(self, surface: pygame.Surface, resource_manager):
        """Draw the button."""
        # Draw button background
        pygame.draw.rect(surface, self.current_bg_color, self.rect, 
                        border_radius=BUTTON_RADIUS)
        
        # Draw button text
        font = resource_manager.get_font(self.font_size)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle button events. Returns True if button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pressed and self.hovered:
                self.pressed = False
                if self.callback:
                    self.callback()
                return True
            self.pressed = False
        
        return False
    
    def is_hovered(self) -> bool:
        """Check if button is being hovered."""
        return self.hovered
    
    def set_callback(self, callback: Callable):
        """Set the button click callback."""
        self.callback = callback
    
    def set_text(self, text: str):
        """Set the button text."""
        self.text = text
