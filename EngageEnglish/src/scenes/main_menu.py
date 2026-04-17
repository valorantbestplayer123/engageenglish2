"""
Main menu scene with mode selection cards.
"""

import pygame

from core.scene_base import SceneBase
from ui.button import Button
from ui.card import Card
from ui.label import Label, HorizontalAlign, VerticalAlign
from constants import (Colors, MODE_SPEED, MODE_BREADTH, MODE_CONTEXT, MODE_RESILIENCE,
                       MODE_NAMES, MODE_DESCRIPTIONS, PADDING, FONT_SIZE_TITLE, FONT_SIZE_SUBHEADER)


class MainMenu(SceneBase):
    """Main menu with four mode selection cards."""
    
    def __init__(self, scene_manager):
        super().__init__(scene_manager)
        
        # Mode cards
        self.cards = []
        self.mode_buttons = []
        self.mode_labels = []
        self.desc_labels = []
        
        # Title
        self.title_label = None
        
        # Back button
        self.back_button = None
        
        # Create UI elements
        self._create_ui()
    
    def _create_ui(self):
        """Create all UI elements."""
        screen_w, screen_h = self.screen.get_size()
        
        # Title
        self.title_label = Label(
            "EngageEnglish",
            screen_w // 2,
            80,
            font_size=FONT_SIZE_TITLE,
            color=Colors.ACCENT2,
            h_align=HorizontalAlign.CENTER,
            v_align=VerticalAlign.TOP
        )
        
        # Mode cards layout (2x2 grid)
        card_width = 650
        card_height = 200
        card_spacing = 30
        start_x = (screen_w - (card_width * 2 + card_spacing)) // 2
        start_y = 180
        
        modes = [
            (MODE_SPEED, Colors.TEAL),
            (MODE_BREADTH, Colors.ACCENT),
            (MODE_CONTEXT, Colors.GOLD),
            (MODE_RESILIENCE, Colors.GREEN)
        ]
        
        for i, (mode_id, color) in enumerate(modes):
            row = i // 2
            col = i % 2
            
            card_x = start_x + col * (card_width + card_spacing)
            card_y = start_y + row * (card_height + card_spacing)
            
            # Create card
            card = Card(card_x, card_y, card_width, card_height, border_color=color)
            self.cards.append(card)
            
            # Create button for card area
            button = Button(
                card_x, card_y, card_width, card_height,
                "",
                bg_color=(0, 0, 0, 0),  # Transparent
                callback=lambda m=mode_id: self._select_mode(m)
            )
            self.mode_buttons.append(button)
            
            # Mode name label
            name_label = Label(
                MODE_NAMES[mode_id],
                card_x + card_width // 2,
                card_y + 50,
                font_size=FONT_SIZE_SUBHEADER,
                color=color,
                h_align=HorizontalAlign.CENTER
            )
            self.mode_labels.append(name_label)
            
            # Description label
            desc_label = Label(
                MODE_DESCRIPTIONS[mode_id],
                card_x + card_width // 2,
                card_y + 100,
                font_size=18,
                color=Colors.TEXT_DIM,
                h_align=HorizontalAlign.CENTER,
                max_width=card_width - 40
            )
            self.desc_labels.append(desc_label)
    
        # Stats button at bottom
        stats_btn_x = screen_w // 2 - 100
        stats_btn_y = screen_h - 80
        self.stats_button = Button(
            stats_btn_x, stats_btn_y,
            200, 50,
            "View Progress",
            bg_color=Colors.PANEL,
            hover_color=Colors.BORDER,
            font_size=20,
            callback=self._show_stats
        )
    
    def _select_mode(self, mode_id: str):
        """Handle mode selection."""
        # Import here to avoid circular imports
        from scenes.level_select import LevelSelect
        from core.transition import TransitionType
        
        level_select = LevelSelect(self.scene_manager, mode_id)
        self.scene_manager.push_scene(level_select, TransitionType.SLIDE_RIGHT)
    
    def _show_stats(self):
        """Show progress stats."""
        # For now, just print to console
        print("Progress Stats:")
        print(f"  Highest Level: {self.progress_manager.data['highest_level']}")
        print(f"  Consecutive Days: {self.progress_manager.get_consecutive_days()}")
        
        for mode in [MODE_SPEED, MODE_BREADTH, MODE_CONTEXT, MODE_RESILIENCE]:
            accuracy = self.progress_manager.get_accuracy(mode)
            unlocked = self.progress_manager.get_unlocked_levels(mode)
            print(f"  {MODE_NAMES[mode]}:")
            print(f"    Accuracy: {accuracy:.1f}%")
            print(f"    Unlocked Levels: {len(unlocked)}")
    
    def enter(self):
        super().enter()
    
    def exit(self):
        super().exit()
    
    def update(self, dt: float):
        """Update menu animations."""
        # Update cards
        for card in self.cards:
            card.update(dt)
        
        # Update buttons
        for button in self.mode_buttons:
            button.update(dt)
        
        self.stats_button.update(dt)
    
    def draw(self):
        """Draw main menu."""
        # Draw background
        self.screen.fill(Colors.BG)
        
        # Draw title
        self.title_label.draw(self.screen, self.resource_manager)
        
        # Draw cards
        for card in self.cards:
            card.draw(self.screen)
        
        # Draw mode labels
        for label in self.mode_labels:
            label.draw(self.screen, self.resource_manager)
        
        for label in self.desc_labels:
            label.draw(self.screen, self.resource_manager)
        
        # Draw stats button
        self.stats_button.draw(self.screen, self.resource_manager)
        
        # Draw footer text
        footer = Label(
            f"Consecutive Days: {self.progress_manager.get_consecutive_days()} | "
            f"Highest Level: {self.progress_manager.data['highest_level']}",
            self.screen.get_width() // 2,
            self.screen.get_height() - 30,
            font_size=16,
            color=Colors.TEXT_MUTED,
            h_align=HorizontalAlign.CENTER
        )
        footer.draw(self.screen, self.resource_manager)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle menu events."""
        # Handle mode buttons
        for button in self.mode_buttons:
            button.handle_event(event)
        
        # Handle stats button
        self.stats_button.handle_event(event)
