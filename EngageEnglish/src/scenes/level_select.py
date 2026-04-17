"""
Level selection scene for each game mode.
"""

import pygame

from core.scene_base import SceneBase
from ui.button import Button
from ui.card import Card
from ui.label import Label, HorizontalAlign, VerticalAlign
from ui.stars import Stars
from core.constants import (Colors, MODE_SPEED, MODE_BREADTH, MODE_CONTEXT, MODE_RESILIENCE,
                       MODE_NAMES, PADDING, FONT_SIZE_HEADER)


class LevelSelect(SceneBase):
    """Level selection screen for a specific mode."""
    
    def __init__(self, scene_manager, mode: str):
        super().__init__(scene_manager)
        self.mode = mode
        
        # UI elements
        self.title_label = None
        self.back_button = None
        self.level_cards = []
        self.level_buttons = []
        self.level_labels = []
        self.stars_displays = []
        
        self._create_ui()
    
    def _create_ui(self):
        """Create all UI elements."""
        screen_w, screen_h = self.screen.get_size()
        
        # Title
        self.title_label = Label(
            MODE_NAMES[self.mode],
            screen_w // 2,
            60,
            font_size=FONT_SIZE_HEADER,
            color=Colors.ACCENT2,
            h_align=HorizontalAlign.CENTER,
            v_align=VerticalAlign.TOP
        )
        
        # Back button
        self.back_button = Button(
            30, 30,
            120, 50,
            "Back",
            bg_color=Colors.PANEL,
            hover_color=Colors.BORDER,
            font_size=20,
            callback=self._go_back
        )
        
        # Get level count based on mode
        if self.mode == MODE_SPEED:
            level_count = self.data_loader.get_definition_count()
            get_level = self.data_loader.get_definition_level
        elif self.mode == MODE_BREADTH:
            level_count = self.data_loader.get_synonym_count()
            get_level = self.data_loader.get_synonym_level
        elif self.mode == MODE_CONTEXT:
            level_count = self.data_loader.get_context_count()
            get_level = self.data_loader.get_context_level
        else:  # MODE_RESILIENCE
            level_count = self.data_loader.get_synonym_count()
            get_level = self.data_loader.get_synonym_level
        
        # Get unlocked levels
        unlocked = self.progress_manager.get_unlocked_levels(self.mode)
        
        # Create level cards (grid layout)
        card_width = 200
        card_height = 120
        card_spacing = 20
        cards_per_row = 6
        
        start_x = (screen_w - (cards_per_row * (card_width + card_spacing) - card_spacing)) // 2
        start_y = 150
        
        for level_num in range(1, level_count + 1):
            row = (level_num - 1) // cards_per_row
            col = (level_num - 1) % cards_per_row
            
            card_x = start_x + col * (card_width + card_spacing)
            card_y = start_y + row * (card_height + card_spacing)
            
            is_unlocked = level_num in unlocked
            
            # Determine card color
            if is_unlocked:
                card_color = Colors.CARD
                text_color = Colors.TEXT
            else:
                card_color = Colors.PANEL
                text_color = Colors.TEXT_MUTED
            
            # Create card
            card = Card(card_x, card_y, card_width, card_height, bg_color=card_color)
            self.level_cards.append(card)
            
            # Create button for card
            button = Button(
                card_x, card_y, card_width, card_height,
                "",
                bg_color=(0, 0, 0, 0),
                callback=lambda n=level_num: self._select_level(n) if is_unlocked else None
            )
            self.level_buttons.append(button)
            
            # Level number label
            level_text = f"Level {level_num}"
            level_label = Label(
                level_text,
                card_x + card_width // 2,
                card_y + 40,
                font_size=28,
                color=text_color,
                h_align=HorizontalAlign.CENTER
            )
            self.level_labels.append(level_label)
            
            # Stars display for Breadth mode
            if self.mode == MODE_BREADTH:
                stars = Stars(
                    card_x + card_width // 2,
                    card_y + 80,
                    count=self.progress_manager.get_stars(self.mode, level_num),
                    max_stars=3,
                    star_size=20
                )
                self.stars_displays.append(stars)
    
    def _go_back(self):
        """Go back to main menu."""
        from core.transition import TransitionType
        self.scene_manager.pop_scene(TransitionType.SLIDE_LEFT)
    
    def _select_level(self, level_num: int):
        """Handle level selection."""
        from core.transition import TransitionType
        
        # Create appropriate game scene based on mode
        if self.mode == MODE_SPEED:
            from modes.speed_mode import SpeedMode
            game_scene = SpeedMode(self.scene_manager, level_num)
        elif self.mode == MODE_BREADTH:
            from modes.breadth_mode import BreadthMode
            game_scene = BreadthMode(self.scene_manager, level_num)
        elif self.mode == MODE_CONTEXT:
            from modes.context_mode import ContextMode
            game_scene = ContextMode(self.scene_manager, level_num)
        else:  # MODE_RESILIENCE
            from modes.resilience_mode import ResilienceMode
            game_scene = ResilienceMode(self.scene_manager, level_num)
        
        self.scene_manager.push_scene(game_scene, TransitionType.SLIDE_RIGHT)
    
    def enter(self):
        super().enter()
    
    def exit(self):
        super().exit()
    
    def update(self, dt: float):
        """Update animations."""
        for card in self.level_cards:
            card.update(dt)
        
        for button in self.level_buttons:
            button.update(dt)
        
        self.back_button.update(dt)
    
    def draw(self):
        """Draw level select screen."""
        # Draw background
        self.screen.fill(Colors.BG)
        
        # Draw title
        self.title_label.draw(self.screen, self.resource_manager)
        
        # Draw level cards
        for card in self.level_cards:
            card.draw(self.screen)
        
        # Draw level labels
        for label in self.level_labels:
            label.draw(self.screen, self.resource_manager)
        
        # Draw stars (Breadth mode only)
        for stars in self.stars_displays:
            stars.draw(self.screen, self.resource_manager)
        
        # Draw back button
        self.back_button.draw(self.screen, self.resource_manager)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle events."""
        self.back_button.handle_event(event)
        for button in self.level_buttons:
            button.handle_event(event)
