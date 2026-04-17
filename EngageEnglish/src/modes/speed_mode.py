"""
Speed & Automaticity Mode - Fast-paced multiple choice with time pressure.
"""

import random
import pygame

from core.scene_base import SceneBase
from ui.button import Button
from ui.label import Label, HorizontalAlign, VerticalAlign
from ui.timer import Timer
from ui.progress_bar import ProgressBar
from core.constants import (Colors, QUESTION_TIME_SECONDS, DEFAULT_HP, FONT_SIZE_SUBHEADER,
                       FONT_SIZE_BODY)


class SpeedMode(SceneBase):
    """Fast-paced multiple choice mode with streak bonuses."""
    
    def __init__(self, scene_manager, level: int):
        super().__init__(scene_manager)
        self.level = level
        
        # Game state
        self.hp = DEFAULT_HP
        self.score = 0
        self.max_score = 0
        self.streak = 0
        self.best_streak = 0
        self.current_question_index = 0
        self.questions = []
        self.current_question = None
        self.answered = False
        self.correct_answer = None
        
        # Timing
        self.start_time = 0
        self.total_time = 0
        
        # UI elements
        self.question_label = None
        self.option_buttons = []
        self.timer = None
        self.hp_bars = []
        self.score_label = None
        self.streak_label = None
        self.back_button = None
        
        # Load questions
        self._load_questions()
        self._create_ui()
    
    def _load_questions(self):
        """Load definition questions for this level."""
        level_data = self.data_loader.get_definition_level(self.level)
        if level_data and "questions" in level_data:
            self.questions = level_data["questions"].copy()
            random.shuffle(self.questions)
            self.max_score = len(self.questions) * 100
        
        if self.questions:
            self.current_question = self.questions[0]
    
    def _create_ui(self):
        """Create UI elements."""
        screen_w, screen_h = self.screen.get_size()
        
        # Back button
        self.back_button = Button(
            30, 30,
            120, 50,
            "Exit",
            bg_color=Colors.PANEL,
            hover_color=Colors.BORDER,
            font_size=20,
            callback=self._exit_level
        )
        
        # HP bars
        for i in range(DEFAULT_HP):
            bar = ProgressBar(
                30 + i * 45,
                100,
                35,
                10,
                value=1,
                max_value=1,
                fill_color=Colors.RED,
                bg_color=Colors.PANEL
            )
            self.hp_bars.append(bar)
        
        # Timer
        self.timer = Timer(screen_w - 80, 70)
        
        # Score label
        self.score_label = Label(
            "Score: 0",
            screen_w - 150,
            30,
            font_size=24,
            color=Colors.GOLD,
            h_align=HorizontalAlign.RIGHT
        )
        
        # Streak label
        self.streak_label = Label(
            "Streak: 0",
            screen_w // 2,
            30,
            font_size=24,
            color=Colors.TEAL,
            h_align=HorizontalAlign.CENTER
        )
        
        # Question label
        self.question_label = Label(
            "",
            screen_w // 2,
            200,
            font_size=FONT_SIZE_SUBHEADER,
            color=Colors.TEXT,
            h_align=HorizontalAlign.CENTER,
            max_width=800
        )
        
        # Option buttons
        option_width = 400
        option_height = 60
        option_spacing = 15
        start_y = 300
        
        for i in range(4):
            btn = Button(
                (screen_w - option_width) // 2,
                start_y + i * (option_height + option_spacing),
                option_width,
                option_height,
                "",
                bg_color=Colors.CARD,
                hover_color=Colors.CARD_HOVER,
                font_size=FONT_SIZE_BODY,
                callback=lambda idx=i: self._select_answer(idx)
            )
            self.option_buttons.append(btn)
        
        # Load first question
        self._load_question_ui()
    
    def _load_question_ui(self):
        """Load current question into UI."""
        if not self.current_question:
            return
        
        # Update question text
        definition = self.current_question.get("definition", "")
        self.question_label.set_text(definition)
        
        # Get options and shuffle
        options = self.current_question.get("options", [])
        correct = self.current_question.get("answer", "")
        
        # Store correct answer and shuffle with indices
        self.option_data = list(enumerate(options))
        random.shuffle(self.option_data)
        self.correct_answer = correct
        
        # Update button texts
        for i, (original_idx, text) in enumerate(self.option_data):
            self.option_buttons[i].set_text(text)
            self.option_buttons[i].bg_color = Colors.CARD
            self.option_buttons[i].hover_color = Colors.CARD_HOVER
        
        self.answered = False
        self.timer.reset()
        self.timer.start()
    
    def _select_answer(self, button_idx: int):
        """Handle answer selection."""
        if self.answered:
            return
        
        self.answered = True
        self.timer.stop()
        
        original_idx, selected_text = self.option_data[button_idx]
        
        if selected_text == self.correct_answer:
            # Correct answer
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
            
            # Calculate score with streak bonus
            base_score = 100
            streak_bonus = min(self.streak * 10, 50)  # Max +50 bonus
            self.score += base_score + streak_bonus
            
            # Record correct attempt
            self.progress_manager.record_attempt("speed", True)
            
            # Play sound
            self.resource_manager.play_sound("assets/sounds/correct.wav", 0.5)
            
            # Highlight correct button
            self.option_buttons[button_idx].bg_color = Colors.GREEN
            self.option_buttons[button_idx].hover_color = Colors.GREEN
        else:
            # Wrong answer
            self.streak = 0
            self.hp -= 1
            
            # Record wrong attempt
            self.progress_manager.record_attempt("speed", False)
            
            # Play sound
            self.resource_manager.play_sound("assets/sounds/wrong.wav", 0.5)
            
            # Highlight wrong and correct buttons
            self.option_buttons[button_idx].bg_color = Colors.RED
            self.option_buttons[button_idx].hover_color = Colors.RED
            
            # Find and highlight correct answer
            for i, (orig_idx, text) in enumerate(self.option_data):
                if text == self.correct_answer:
                    self.option_buttons[i].bg_color = Colors.GREEN
                    self.option_buttons[i].hover_color = Colors.GREEN
                    break
        
        # Update UI
        self._update_ui()
        
        # Check for game over or next question
        pygame.time.set_timer(pygame.USEREVENT + 1, 1500)  # Show result for 1.5s
    
    def _next_question(self):
        """Move to next question."""
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Clear timer
        
        if self.hp <= 0 or self.current_question_index >= len(self.questions) - 1:
            # Game over or level complete
            self._show_results()
        else:
            # Next question
            self.current_question_index += 1
            self.current_question = self.questions[self.current_question_index]
            self._load_question_ui()
    
    def _show_results(self):
        """Show results screen."""
        from scenes.results_screen import ResultsScreen
        from core.transition import TransitionType
        
        accuracy = self.progress_manager.get_accuracy("speed")
        
        results = ResultsScreen(
            self.scene_manager,
            "speed",
            self.level,
            self.score,
            self.max_score,
            self.total_time,
            accuracy,
            context_score=0.0,
            resilience_score=min(100, self.best_streak * 10)
        )
        
        # Update best streak in progress
        self.progress_manager.set_best_streak("speed", self.best_streak)
        
        self.scene_manager.push_scene(results, TransitionType.FADE)
    
    def _update_ui(self):
        """Update UI elements."""
        self.score_label.set_text(f"Score: {self.score}")
        self.streak_label.set_text(f"Streak: {self.streak}")
        
        # Update HP bars
        for i, bar in enumerate(self.hp_bars):
            bar.set_value(1.0 if i < self.hp else 0.0, animate=False)
    
    def _exit_level(self):
        """Exit level early."""
        self._show_results()
    
    def enter(self):
        super().enter()
        self.start_time = pygame.time.get_ticks()
    
    def exit(self):
        super().exit()
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)
    
    def update(self, dt: float):
        """Update game state."""
        self.total_time += dt
        
        # Update timer
        if not self.answered:
            self.timer.update(dt)
            
            # Check if time ran out
            if self.timer.is_time_up():
                self._select_answer(-1)  # Wrong answer
        else:
            self.timer.stop()
        
        # Update UI
        self.back_button.update(dt)
        for btn in self.option_buttons:
            btn.update(dt)
        for bar in self.hp_bars:
            bar.update(dt)
        
        self._update_ui()
    
    def draw(self):
        """Draw game screen."""
        self.screen.fill(Colors.BG)
        
        # Draw UI elements
        self.back_button.draw(self.screen, self.resource_manager)
        self.score_label.draw(self.screen, self.resource_manager)
        self.streak_label.draw(self.screen, self.resource_manager)
        self.question_label.draw(self.screen, self.resource_manager)
        
        for bar in self.hp_bars:
            bar.draw(self.screen)
        
        for btn in self.option_buttons:
            btn.draw(self.screen, self.resource_manager)
        
        self.timer.draw(self.screen, self.resource_manager)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle events."""
        self.back_button.handle_event(event)
        
        for btn in self.option_buttons:
            btn.handle_event(event)
        
        if event.type == pygame.USEREVENT + 1:
            self._next_question()
