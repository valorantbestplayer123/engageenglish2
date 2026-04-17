"""
Behavioral/Resilience Mode - Practice without penalties, hints allowed.
"""

import random
import pygame

from core.scene_base import SceneBase
from ui.button import Button
from ui.label import Label, HorizontalAlign, VerticalAlign
from ui.timer import Timer
from ui.progress_bar import ProgressBar
from constants import (Colors, QUESTION_TIME_SECONDS, FONT_SIZE_SUBHEADER,
                       FONT_SIZE_BODY)


class ResilienceMode(SceneBase):
    """Practice mode with hints and no HP penalty."""
    
    def __init__(self, scene_manager, level: int):
        super().__init__(scene_manager)
        self.level = level
        
        # Game state
        self.score = 0
        self.max_score = 0
        self.current_question_index = 0
        self.questions = []
        self.current_question = None
        self.answered = False
        self.correct_answer = None
        self.hints_used = 0
        self.retries = 0
        
        # Timing
        self.start_time = 0
        self.total_time = 0
        
        # UI elements
        self.question_label = None
        self.option_buttons = []
        self.timer = None
        self.score_label = None
        self.hint_button = None
        self.back_button = None
        self.hint_label = None
        
        # Load questions
        self._load_questions()
        self._create_ui()
    
    def _load_questions(self):
        """Load definition questions for this level."""
        level_data = self.data_loader.get_definition_level(min(self.level, 5))
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
        
        # Timer (no pressure, just for tracking)
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
        
        # Hint info
        self.hint_label = Label(
            "Hints Used: 0 | Retries: 0",
            screen_w // 2,
            30,
            font_size=20,
            color=Colors.TEXT_DIM,
            h_align=HorizontalAlign.CENTER
        )
        
        # Question label
        self.question_label = Label(
            "",
            screen_w // 2,
            180,
            font_size=FONT_SIZE_SUBHEADER,
            color=Colors.TEXT,
            h_align=HorizontalAlign.CENTER,
            max_width=800
        )
        
        # Hint button
        self.hint_button = Button(
            screen_w // 2 - 75,
            280,
            150,
            45,
            "Show Hint (-20 pts)",
            bg_color=Colors.GOLD,
            hover_color=Colors.GOLD_DIM,
            font_size=18,
            callback=self._show_hint
        )
        
        # Option buttons
        option_width = 400
        option_height = 60
        option_spacing = 15
        start_y = 350
        
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
        self.hint_button.visible = True
    
    def _show_hint(self):
        """Show a hint (remove one wrong option)."""
        if self.answered or self.hint_button.visible == False:
            return
        
        # Find wrong options
        wrong_options = []
        for i, (orig_idx, text) in enumerate(self.option_data):
            if text != self.correct_answer and not self.option_buttons[i].disabled:
                wrong_options.append(i)
        
        if wrong_options:
            # Disable one wrong option
            to_disable = random.choice(wrong_options)
            self.option_buttons[to_disable].disabled = True
            self.option_buttons[to_disable].bg_color = Colors.PANEL
            self.option_buttons[to_disable].hover_color = Colors.PANEL
            self.hints_used += 1
            self.score = max(0, self.score - 20)
            self.hint_button.visible = False
            self._update_ui()
    
    def _select_answer(self, button_idx: int):
        """Handle answer selection."""
        if self.answered:
            return
        
        original_idx, selected_text = self.option_data[button_idx]
        
        if selected_text == self.correct_answer:
            # Correct answer
            self.answered = True
            
            # Calculate score (base 100 - hints penalty)
            points = max(0, 100 - self.hints_used * 20)
            self.score += points
            
            # Record correct attempt
            self.progress_manager.record_attempt("resilience", True)
            
            # Play sound
            self.resource_manager.play_sound("assets/sounds/correct.wav", 0.5)
            
            # Highlight correct button
            self.option_buttons[button_idx].bg_color = Colors.GREEN
            self.option_buttons[button_idx].hover_color = Colors.GREEN
            
            # Move to next question after delay
            pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
        else:
            # Wrong answer - no HP penalty, just track retries
            self.retries += 1
            
            # Record wrong attempt
            self.progress_manager.record_attempt("resilience", False)
            
            # Play sound
            self.resource_manager.play_sound("assets/sounds/wrong.wav", 0.5)
            
            # Flash wrong
            self.option_buttons[button_idx].bg_color = Colors.RED
            self.option_buttons[button_idx].hover_color = Colors.RED
            
            # Reset after short delay
            pygame.time.set_timer(pygame.USEREVENT + 2, 500)
        
        self._update_ui()
    
    def _reset_wrong_colors(self):
        """Reset colors after wrong answer."""
        pygame.time.set_timer(pygame.USEREVENT + 2, 0)
        
        for i, (orig_idx, text) in enumerate(self.option_data):
            if text != self.correct_answer and not self.option_buttons[i].disabled:
                self.option_buttons[i].bg_color = Colors.CARD
                self.option_buttons[i].hover_color = Colors.CARD_HOVER
    
    def _next_question(self):
        """Move to next question."""
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        
        if self.current_question_index >= len(self.questions) - 1:
            # Level complete
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
        
        accuracy = self.progress_manager.get_accuracy("resilience")
        
        # Calculate resilience score based on learning (fewer retries + fewer hints is better)
        resilience_score = max(0, 100 - (self.retries * 5) - (self.hints_used * 10))
        
        results = ResultsScreen(
            self.scene_manager,
            "resilience",
            self.level,
            self.score,
            self.max_score,
            self.total_time,
            accuracy,
            context_score=0.0,
            resilience_score=resilience_score,
            hints_used=self.hints_used,
            retries=self.retries
        )
        
        # Update resilience mode stats
        if "practice_count" not in self.progress_manager.data["modes"]["resilience"]:
            self.progress_manager.data["modes"]["resilience"]["practice_count"] = 0
        self.progress_manager.data["modes"]["resilience"]["practice_count"] += 1
        self.progress_manager.data["modes"]["resilience"]["hints_used"] += self.hints_used
        self.progress_manager.data["modes"]["resilience"]["total_retries"] += self.retries
        
        self.scene_manager.push_scene(results, TransitionType.FADE)
    
    def _update_ui(self):
        """Update UI elements."""
        self.score_label.set_text(f"Score: {self.score}")
        self.hint_label.set_text(f"Hints Used: {self.hints_used} | Retries: {self.retries}")
    
    def _exit_level(self):
        """Exit level early."""
        self._show_results()
    
    def enter(self):
        super().enter()
        self.start_time = pygame.time.get_ticks()
        self.timer.start()
    
    def exit(self):
        super().exit()
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        pygame.time.set_timer(pygame.USEREVENT + 2, 0)
    
    def update(self, dt: float):
        """Update game state."""
        self.total_time += dt
        
        # Update timer (just for tracking, no time limit)
        self.timer.update(dt)
        
        # Update UI
        self.back_button.update(dt)
        
        if hasattr(self.hint_button, 'visible') and self.hint_button.visible:
            self.hint_button.update(dt)
        
        for btn in self.option_buttons:
            if not getattr(btn, 'disabled', False):
                btn.update(dt)
        
        self._update_ui()
    
    def draw(self):
        """Draw game screen."""
        self.screen.fill(Colors.BG)
        
        # Draw UI elements
        self.back_button.draw(self.screen, self.resource_manager)
        self.score_label.draw(self.screen, self.resource_manager)
        self.hint_label.draw(self.screen, self.resource_manager)
        self.question_label.draw(self.screen, self.resource_manager)
        
        if hasattr(self.hint_button, 'visible') and self.hint_button.visible:
            self.hint_button.draw(self.screen, self.resource_manager)
        
        for btn in self.option_buttons:
            btn.draw(self.screen, self.resource_manager)
        
        self.timer.draw(self.screen, self.resource_manager)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle events."""
        self.back_button.handle_event(event)
        
        if hasattr(self.hint_button, 'visible') and self.hint_button.visible:
            self.hint_button.handle_event(event)
        
        for i, btn in enumerate(self.option_buttons):
            if not getattr(btn, 'disabled', False):
                btn.handle_event(event)
        
        if event.type == pygame.USEREVENT + 1:
            self._next_question()
        elif event.type == pygame.USEREVENT + 2:
            self._reset_wrong_colors()
