"""
Context & Morphology Mode - Sentence completion and word formation.
"""

import random
import pygame

from core.scene_base import SceneBase
from ui.button import Button
from ui.label import Label, HorizontalAlign, VerticalAlign
from ui.timer import Timer
from ui.progress_bar import ProgressBar
from constants import (Colors, QUESTION_TIME_SECONDS, DEFAULT_HP, FONT_SIZE_SUBHEADER,
                       FONT_SIZE_BODY)


class ContextMode(SceneBase):
    """Sentence completion and word formation mode."""
    
    def __init__(self, scene_manager, level: int):
        super().__init__(scene_manager)
        self.level = level
        
        # Game state
        self.hp = DEFAULT_HP
        self.score = 0
        self.max_score = 0
        self.current_sentence_index = 0
        self.sentences = []
        self.current_sentence = None
        self.answered = False
        self.correct_answer = None
        self.selected_option = None
        
        # Timing
        self.start_time = 0
        self.total_time = 0
        
        # UI elements
        self.sentence_label = None
        self.option_buttons = []
        self.timer = None
        self.hp_bars = []
        self.score_label = None
        self.progress_label = None
        self.back_button = None
        
        # Load sentences
        self._load_sentences()
        self._create_ui()
    
    def _load_sentences(self):
        """Load context sentences for this level."""
        level_data = self.data_loader.get_context_level(self.level)
        
        if level_data and "sentences" in level_data:
            self.sentences = level_data["sentences"].copy()
            random.shuffle(self.sentences)
            self.max_score = len(self.sentences) * 100
        
        # If no context levels exist, create fallback from definition questions
        if not self.sentences:
            def_level = self.data_loader.get_definition_level(min(self.level, 5))
            if def_level and "questions" in def_level:
                # Convert definition questions to sentence format
                for q in def_level["questions"][:8]:
                    self.sentences.append({
                        "text": f"The word that means '{q['definition']}' is _____.",
                        "answer": q["answer"],
                        "options": q["options"] + [q["answer"]]
                    })
                random.shuffle(self.sentences)
                self.max_score = len(self.sentences) * 100
        
        if self.sentences:
            self.current_sentence = self.sentences[0]
    
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
        
        # Progress label
        self.progress_label = Label(
            f"Progress: 0/{len(self.sentences)}",
            screen_w // 2,
            30,
            font_size=24,
            color=Colors.TEAL,
            h_align=HorizontalAlign.CENTER
        )
        
        # Sentence label
        self.sentence_label = Label(
            "",
            screen_w // 2,
            250,
            font_size=FONT_SIZE_SUBHEADER,
            color=Colors.TEXT,
            h_align=HorizontalAlign.CENTER,
            max_width=900
        )
        
        # Option buttons
        option_width = 350
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
        
        # Load first sentence
        self._load_sentence_ui()
    
    def _load_sentence_ui(self):
        """Load current sentence into UI."""
        if not self.current_sentence:
            return
        
        # Update sentence text
        text = self.current_sentence.get("text", "")
        self.sentence_label.set_text(text)
        
        # Get options
        correct = self.current_sentence.get("answer", "")
        options = self.current_sentence.get("options", [])
        
        # Ensure correct answer is in options and we have 4 options
        if correct not in options:
            options.append(correct)
        
        if len(options) > 4:
            options = options[:4]
        elif len(options) < 4:
            # Fill with random words
            filler_words = ["however", "therefore", "moreover", "furthermore", 
                          "consequently", "nevertheless", "meanwhile", "further"]
            while len(options) < 4:
                word = random.choice(filler_words)
                if word not in options and word != correct:
                    options.append(word)
        
        # Shuffle options
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
            self.score += 100
            
            # Record correct attempt
            self.progress_manager.record_attempt("context", True)
            
            # Play sound
            self.resource_manager.play_sound("assets/sounds/correct.wav", 0.5)
            
            # Highlight correct button
            self.option_buttons[button_idx].bg_color = Colors.GREEN
            self.option_buttons[button_idx].hover_color = Colors.GREEN
        else:
            # Wrong answer
            self.hp -= 1
            
            # Record wrong attempt
            self.progress_manager.record_attempt("context", False)
            
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
        
        # Check for game over or next sentence
        pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
    
    def _next_sentence(self):
        """Move to next sentence."""
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        
        if self.hp <= 0 or self.current_sentence_index >= len(self.sentences) - 1:
            # Game over or level complete
            self._show_results()
        else:
            # Next sentence
            self.current_sentence_index += 1
            self.current_sentence = self.sentences[self.current_sentence_index]
            self._load_sentence_ui()
    
    def _show_results(self):
        """Show results screen."""
        from scenes.results_screen import ResultsScreen
        from core.transition import TransitionType
        
        accuracy = self.progress_manager.get_accuracy("context")
        
        results = ResultsScreen(
            self.scene_manager,
            "context",
            self.level,
            self.score,
            self.max_score,
            self.total_time,
            accuracy,
            context_score=self.score / self.max_score * 100 if self.max_score > 0 else 0,
            resilience_score=0.0
        )
        
        self.scene_manager.push_scene(results, TransitionType.FADE)
    
    def _update_ui(self):
        """Update UI elements."""
        self.score_label.set_text(f"Score: {self.score}")
        self.progress_label.set_text(f"Progress: {self.current_sentence_index + 1}/{len(self.sentences)}")
        
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
        self.progress_label.draw(self.screen, self.resource_manager)
        self.sentence_label.draw(self.screen, self.resource_manager)
        
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
            self._next_sentence()
