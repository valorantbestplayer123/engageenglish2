"""
Star rating display component.
"""

import pygame
from typing import Tuple

from constants import Colors, GOLD_DIM


class Stars:
    """Star rating display component."""
    
    def __init__(self, x: int, y: int, count: int = 0, max_stars: int = 3,
                 star_size: int = 40, spacing: int = 10):
        self.x = x
        self.y = y
        self.count = count
        self.max_stars = max_stars
        self.star_size = star_size
        self.spacing = spacing
    
    def set_count(self, count: int):
        """Set the number of stars."""
        self.count = max(0, min(count, self.max_stars))
    
    def get_count(self) -> int:
        """Get the current star count."""
        return self.count
    
    def draw(self, surface: pygame.Surface, resource_manager):
        """Draw the stars."""
        # Calculate total width
        total_width = (self.star_size + self.spacing) * self.max_stars - self.spacing
        start_x = self.x - total_width // 2
        
        for i in range(self.max_stars):
            star_x = start_x + i * (self.star_size + self.spacing)
            star_y = self.y - self.star_size // 2
            
            if i < self.count:
                # Filled star
                color = Colors.GOLD
            else:
                # Empty star
                color = GOLD_DIM
            
            self._draw_star(surface, star_x, star_y, self.star_size, color)
    
    def _draw_star(self, surface: pygame.Surface, x: int, y: int, size: int,
                   color: Tuple[int, int, int]):
        """Draw a single star shape."""
        # Star points (5-pointed star)
        outer_radius = size // 2
        inner_radius = size // 4
        center_x = x + outer_radius
        center_y = y + outer_radius
        
        points = []
        for i in range(10):
            angle = i * 36 - 90  # Start at top
            angle_rad = angle * 3.14159 / 180
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = center_x + radius * (angle_rad ** 1 / 57.29) * 57.29  # Approximate
            # Better approach:
            px = center_x + radius * (1 if i % 4 == 0 else 0.5) * (1 if i < 5 else -1)
            py = center_y + radius * (0 if i % 4 == 2 else 0.866) * (1 if i < 5 else -1)
        
        # Simpler approach: draw a filled circle for now
        # A proper star would need more complex math
        pygame.draw.circle(surface, color, (center_x, center_y), outer_radius)
        
        # For a star shape, let's use a polygon
        points = []
        for i in range(10):
            angle = i * 36 - 90
            angle_rad = angle * 3.14159265 / 180
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = center_x + radius * (angle_rad ** 1 / 57.29) * 57.29  # This is wrong
            # Correct:
            import math
            px = center_x + radius * math.cos(angle_rad)
            py = center_y + radius * math.sin(angle_rad)
            points.append((px, py))
        
        if len(points) >= 3:
            pygame.draw.polygon(surface, color, points)
    
    def get_rect(self) -> pygame.Rect:
        """Get the bounding rectangle of the stars."""
        total_width = (self.star_size + self.spacing) * self.max_stars - self.spacing
        return pygame.Rect(
            self.x - total_width // 2,
            self.y - self.star_size // 2,
            total_width,
            self.star_size
        )
