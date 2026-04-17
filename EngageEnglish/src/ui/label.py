"""
Label component for text rendering with alignment options.
"""

import pygame
from typing import Tuple, Optional
from enum import Enum

from core.constants import Colors, FONT_SIZE_BODY


class HorizontalAlign(Enum):
    """Horizontal alignment options."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlign(Enum):
    """Vertical alignment options."""
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class Label:
    """Text label with alignment options."""
    
    def __init__(self, text: str, x: int, y: int,
                 font_size: int = FONT_SIZE_BODY,
                 color: Tuple[int, int, int] = Colors.TEXT,
                 h_align: HorizontalAlign = HorizontalAlign.LEFT,
                 v_align: VerticalAlign = VerticalAlign.TOP,
                 max_width: Optional[int] = None):
        self.text = text
        self.x = x
        self.y = y
        self.font_size = font_size
        self.color = color
        self.h_align = h_align
        self.v_align = v_align
        self.max_width = max_width
        
        self._cached_surface: Optional[pygame.Surface] = None
        self._cached_text = None
        self._cached_font_size = None
    
    def get_text_surface(self, resource_manager) -> pygame.Surface:
        """Get the text surface, using cache if possible."""
        # Check cache
        if (self._cached_surface is not None and 
            self._cached_text == self.text and 
            self._cached_font_size == self.font_size):
            return self._cached_surface
        
        font = resource_manager.get_font(self.font_size)
        
        if self.max_width:
            # Render with word wrap
            words = self.text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surface = font.render(test_line, True, self.color)
                if test_surface.get_width() <= self.max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Render all lines
            line_surfaces = [font.render(line, True, self.color) for line in lines]
            line_height = line_surfaces[0].get_height()
            total_height = len(lines) * line_height
            
            result = pygame.Surface((self.max_width, total_height), pygame.SRCALPHA)
            for i, line_surf in enumerate(line_surfaces):
                result.blit(line_surf, (0, i * line_height))
            
            self._cached_surface = result
        else:
            # Simple single-line render
            self._cached_surface = font.render(self.text, True, self.color)
        
        self._cached_text = self.text
        self._cached_font_size = self.font_size
        return self._cached_surface
    
    def draw(self, surface: pygame.Surface, resource_manager):
        """Draw the label."""
        text_surf = self.get_text_surface(resource_manager)
        rect = text_surf.get_rect()
        
        # Horizontal alignment
        if self.h_align == HorizontalAlign.CENTER:
            rect.centerx = self.x
        elif self.h_align == HorizontalAlign.RIGHT:
            rect.right = self.x
        else:  # LEFT
            rect.x = self.x
        
        # Vertical alignment
        if self.v_align == VerticalAlign.CENTER:
            rect.centery = self.y
        elif self.v_align == VerticalAlign.BOTTOM:
            rect.bottom = self.y
        else:  # TOP
            rect.y = self.y
        
        surface.blit(text_surf, rect)
    
    def get_size(self, resource_manager) -> Tuple[int, int]:
        """Get the size of the label."""
        surf = self.get_text_surface(resource_manager)
        return surf.get_size()
    
    def set_text(self, text: str):
        """Set the label text."""
        self.text = text
        self._cached_surface = None  # Invalidate cache
    
    def set_color(self, color: Tuple[int, int, int]):
        """Set the text color."""
        self.color = color
        self._cached_surface = None  # Invalidate cache
