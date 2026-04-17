"""
Card component with shadow and hover lift effects.
"""

import pygame
from typing import Tuple, Optional

from core.constants import Colors, CARD_RADIUS, SHADOW_OFFSET, SHADOW_BLUR, CARD_LIFT_DURATION


class Card:
    """Modern card component with shadow and hover effects."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 bg_color: Tuple[int, int, int] = Colors.CARD,
                 hover_color: Optional[Tuple[int, int, int]] = None,
                 border_color: Tuple[int, int, int] = Colors.BORDER,
                 border_radius: int = CARD_RADIUS):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.hover_color = hover_color if hover_color else Colors.CARD_HOVER
        self.border_color = border_color
        self.border_radius = border_radius
        
        self.hovered = False
        self.lift_progress = 0.0  # 0.0 to 1.0
        
        self.current_bg_color = list(bg_color)
        self.lift_offset = 0
    
    def _interpolate_color(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                           t: float) -> Tuple[int, int, int]:
        """Interpolate between two colors."""
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )
    
    def update(self, dt: float):
        """Update card animation state."""
        mouse_pos = pygame.mouse.get_pos()
        rect = self.get_rect()
        self.hovered = rect.collidepoint(mouse_pos)
        
        # Animate lift progress
        target = 1.0 if self.hovered else 0.0
        speed = 1.0 / CARD_LIFT_DURATION
        if self.lift_progress < target:
            self.lift_progress = min(target, self.lift_progress + speed * dt)
        elif self.lift_progress > target:
            self.lift_progress = max(target, self.lift_progress - speed * dt)
        
        # Update current color
        self.current_bg_color = list(self._interpolate_color(
            self.bg_color, self.hover_color, self.lift_progress
        ))
        
        # Calculate lift offset (max 4 pixels)
        self.lift_offset = int(4 * self.lift_progress)
    
    def get_rect(self) -> pygame.Rect:
        """Get the card's rectangle (adjusted for lift)."""
        return pygame.Rect(self.x, self.y - self.lift_offset, self.width, self.height)
    
    def draw(self, surface: pygame.Surface):
        """Draw the card with shadow."""
        rect = self.get_rect()
        
        # Draw shadow
        shadow_rect = rect.copy()
        shadow_rect.x += SHADOW_OFFSET
        shadow_rect.y += SHADOW_OFFSET
        
        # Create shadow surface with alpha
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 50), shadow_surface.get_rect(), 
                        border_radius=self.border_radius)
        surface.blit(shadow_surface, shadow_rect)
        
        # Draw card background
        pygame.draw.rect(surface, self.current_bg_color, rect, 
                        border_radius=self.border_radius)
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, rect, 2, 
                        border_radius=self.border_radius)
    
    def is_hovered(self) -> bool:
        """Check if card is being hovered."""
        return self.hovered
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if point is inside card."""
        return self.get_rect().collidepoint(point)
