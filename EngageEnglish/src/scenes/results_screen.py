"""
Unified results screen showing performance across all four proficiency indicators.
"""

import pygame

from core.scene_base import SceneBase
from ui.button import Button
from ui.card import Card
from ui.label import Label, HorizontalAlign, VerticalAlign
from ui.progress_bar import ProgressBar
from ui.stars import Stars
from core.constants import (Colors, MODE_NAMES, FONT_SIZE_HEADER, FONT_SIZE_SUBHEADER,
                       STAR_THRESHOLDS)


class ResultsScreen(SceneBase):
    """Results screen showing performance breakdown."""
    
    def __init__(self, scene_manager, mode: str, level: int, score: int, max_score: int,
                 time_taken: float, accuracy: float, context_score: float = 0.0,
                 resilience_score: float = 0.0, hints_used: int = 0, retries: int = 0):
        super().__init__(scene_manager)
        
        self.mode = mode
        self.level = level
        self.score = score
        self.max_score = max_score
        self.time_taken = time_taken
        self.accuracy = accuracy
        self.context_score = context_score
        self.resilience_score = resilience_score
        self.hints_used = hints_used
        self.retries = retries
        
        self._create_ui()
    
    def _create_ui(self):
        """Create all UI elements."""
        screen_w, screen_h = self.screen.get_size()
        
        # Title
        self.title_label = Label(
            f"Level {self.level} Complete!",
            screen_w // 2,
            60,
            font_size=FONT_SIZE_HEADER,
            color=Colors.ACCENT2,
            h_align=HorizontalAlign.CENTER,
            v_align=VerticalAlign.TOP
        )
        
        # Mode label
        self.mode_label = Label(
            MODE_NAMES[self.mode],
            screen_w // 2,
            120,
            font_size=FONT_SIZE_SUBHEADER,
            color=Colors.TEXT_DIM,
            h_align=HorizontalAlign.CENTER
        )
        
        # Main score card
        score_card_width = 400
        score_card_height = 200
        self.score_card = Card(
            (screen_w - score_card_width) // 2,
            160,
            score_card_width,
            score_card_height,
            border_color=Colors.ACCENT
        )
        
        # Score label
        self.score_label = Label(
            f"{self.score} / {self.max_score}",
            screen_w // 2,
            240,
            font_size=64,
            color=Colors.GOLD,
            h_align=HorizontalAlign.CENTER
        )
        
        # Percentage label
        percentage = (self.score / self.max_score * 100) if self.max_score > 0 else 0
        self.percent_label = Label(
            f"{percentage:.1f}%",
            screen_w // 2,
            300,
            font_size=28,
            color=Colors.TEXT_DIM,
            h_align=HorizontalAlign.CENTER
        )
        
        # Stars
        self.stars = Stars(
            screen_w // 2,
            340,
            count=self._calculate_stars(percentage),
            max_stars=3,
            star_size=50
        )
        
        # Four proficiency indicators
        self.indicator_bars = []
        self.indicator_labels = []
        
        indicators = [
            ("Speed", self._get_speed_score(), Colors.TEAL),
            ("Accuracy", self.accuracy, Colors.GREEN),
            ("Context", self.context_score, Colors.GOLD),
            ("Resilience", self.resilience_score, Colors.ACCENT)
        ]
        
        bar_width = 300
        bar_height = 30
        bar_spacing = 40
        start_y = 420
        
        for i, (name, value, color) in enumerate(indicators):
            label = Label(
                name,
                screen_w // 2 - 180,
                start_y + i * (bar_height + bar_spacing) + bar_height // 2,
                font_size=20,
                color=color,
                h_align=HorizontalAlign.RIGHT
            )
            self.indicator_labels.append(label)
            
            bar = ProgressBar(
                screen_w // 2 - 150,
                start_y + i * (bar_height + bar_spacing),
                bar_width,
                bar_height,
                value=value,
                max_value=100,
                fill_color=color
            )
            self.indicator_bars.append(bar)
        
        # Additional stats for Resilience mode
        if self.mode == "resilience":
            self.hints_label = Label(
                f"Hints Used: {self.hints_used}",
                screen_w // 2,
                620,
                font_size=18,
                color=Colors.TEXT_DIM,
                h_align=HorizontalAlign.CENTER
            )
            self.retries_label = Label(
                f"Retries: {self.retries}",
                screen_w // 2,
                650,
                font_size=18,
                color=Colors.TEXT_DIM,
                h_align=HorizontalAlign.CENTER
            )
        
        # Buttons
        btn_y = screen_h - 100
        self.retry_button = Button(
            screen_w // 2 - 220,
            btn_y,
            200,
            50,
            "Retry Level",
            bg_color=Colors.PANEL,
            hover_color=Colors.BORDER,
            font_size=20,
            callback=self._retry_level
        )
        
        self.menu_button = Button(
            screen_w // 2 + 20,
            btn_y,
            200,
            50,
            "Main Menu",
            bg_color=Colors.ACCENT,
            hover_color=Colors.ACCENT2,
            font_size=20,
            callback=self._go_to_menu
        )
    
    def _calculate_stars(self, percentage: float) -> int:
        """Calculate star count based on percentage."""
        for stars, threshold in sorted(STAR_THRESHOLDS.items(), reverse=True):
            if percentage >= threshold:
                return stars
        return 0
    
    def _get_speed_score(self) -> float:
        """Calculate speed score based on time taken."""
        # Assume optimal time is 1 second per question
        optimal_time = self.max_score  # Rough estimate
        if optimal_time == 0:
            return 100.0
        
        ratio = optimal_time / (self.time_taken + 0.1)
        return min(100.0, max(0.0, ratio * 100))
    
    def _retry_level(self):
        """Retry the same level."""
        from core.transition import TransitionType
        self.scene_manager.pop_scene(TransitionType.SLIDE_LEFT)
        # The previous scene will handle retry
    
    def _go_to_menu(self):
        """Go back to main menu."""
        from scenes.main_menu import MainMenu
        from core.transition import TransitionType
        self.scene_manager.replace_scene(MainMenu(self.scene_manager), TransitionType.FADE)
    
    def enter(self):
        super().enter()
        
        # Save progress
        self.progress_manager.set_level_score(self.mode, self.level, self.score)
        
        # Calculate stars for Breadth mode
        if self.mode == "breadth":
            percentage = (self.score / self.max_score * 100) if self.max_score > 0 else 0
            stars = self._calculate_stars(percentage)
            self.progress_manager.set_stars(self.mode, self.level, stars)
            
            # Unlock next level if passed
            if stars > 0:
                self.progress_manager.unlock_level(self.mode, self.level + 1)
        else:
            # For other modes, unlock next level if passed 50%
            percentage = (self.score / self.max_score * 100) if self.max_score > 0 else 0
            if percentage >= 50:
                self.progress_manager.unlock_level(self.mode, self.level + 1)
        
        self.progress_manager.save()
    
    def exit(self):
        super().exit()
    
    def update(self, dt: float):
        """Update animations."""
        self.score_card.update(dt)
        
        for bar in self.indicator_bars:
            bar.update(dt)
        
        self.retry_button.update(dt)
        self.menu_button.update(dt)
    
    def draw(self):
        """Draw results screen."""
        # Draw background
        self.screen.fill(Colors.BG)
        
        # Draw title and mode
        self.title_label.draw(self.screen, self.resource_manager)
        self.mode_label.draw(self.screen, self.resource_manager)
        
        # Draw score card
        self.score_card.draw(self.screen)
        self.score_label.draw(self.screen, self.resource_manager)
        self.percent_label.draw(self.screen, self.resource_manager)
        self.stars.draw(self.screen, self.resource_manager)
        
        # Draw indicators
        for label in self.indicator_labels:
            label.draw(self.screen, self.resource_manager)
        
        for bar in self.indicator_bars:
            bar.draw(self.screen)
        
        # Draw resilience stats if applicable
        if self.mode == "resilience":
            self.hints_label.draw(self.screen, self.resource_manager)
            self.retries_label.draw(self.screen, self.resource_manager)
        
        # Draw buttons
        self.retry_button.draw(self.screen, self.resource_manager)
        self.menu_button.draw(self.screen, self.resource_manager)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle events."""
        self.retry_button.handle_event(event)
        self.menu_button.handle_event(event)
