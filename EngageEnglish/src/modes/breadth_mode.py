"""
Breadth & Depth Mode - Progressive synonym matching with levels.
"""

import random
import pygame

from core.scene_base import SceneBase
from ui.button import Button
from ui.label import Label, HorizontalAlign, VerticalAlign
from ui.timer import Timer
from ui.progress_bar import ProgressBar
from constants import (Colors, DEFAULT_HP, FONT_SIZE_SUBHEADER, FONT_SIZE_BODY, PADDING)


class BreadthMode(SceneBase):
    """Synonym matching mode with progressive difficulty."""
    
    def __init__(self, scene_manager, level: int):
        super().__init__(scene_manager)
        self.level = level
        
        # Game state
        self.hp = DEFAULT_HP
        self.score = 0
        self.max_score = 0
        self.matches_made = 0
        self.total_matches = 0
        self.current_pairs = []
        self.matched_pairs = []
        self.selected_word = None
        self.selected_synonym = None
        self.dragging = False
        self.drag_item = None
        self.drag_offset = (0, 0)
        
        # Timing
        self.start_time = 0
        self.total_time = 0
        
        # UI elements
        self.instruction_label = None
        self.hp_bars = []
        self.score_label = None
        self.timer = None
        self.back_button = None
        self.complete_button = None
        
        # Word and synonym rects
        self.word_rects = []
        self.synonym_rects = []
        
        # Load level data
        self._load_level()
        self._create_ui()
    
    def _load_level(self):
        """Load synonym pairs for this level."""
        level_data = self.data_loader.get_synonym_level(self.level)
        if level_data and "pairs" in level_data:
            pairs = level_data["pairs"]
            # Limit to 8 pairs per round for better UX
            pair_items = list(pairs.items())
            random.shuffle(pair_items)
            self.current_pairs = pair_items[:8]
            self.total_matches = len(self.current_pairs)
            self.max_score = self.total_matches * 100
    
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
        self.timer.start()
        
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
            f"Matches: 0/{self.total_matches}",
            screen_w // 2,
            30,
            font_size=24,
            color=Colors.TEAL,
            h_align=HorizontalAlign.CENTER
        )
        
        # Instructions
        level_data = self.data_loader.get_synonym_level(self.level)
        instructions = level_data.get("instructions", "Match each word with its synonym.")
        self.instruction_label = Label(
            instructions,
            screen_w // 2,
            140,
            font_size=20,
            color=Colors.TEXT_DIM,
            h_align=HorizontalAlign.CENTER
        )
        
        # Create word and synonym cards
        self._create_word_cards()
    
    def _create_word_cards(self):
        """Create word and synonym matching cards."""
        screen_w, screen_h = self.screen.get_size()
        
        # Layout parameters
        card_width = 180
        card_height = 50
        card_spacing = 15
        cards_per_row = 4
        
        # Calculate positions
        start_x = (screen_w - (cards_per_row * (card_width + card_spacing) - card_spacing)) // 2
        words_y = 200
        synonyms_y = 400
        
        # Shuffle synonyms separately from words
        words = [(word, i) for i, (word, _) in enumerate(self.current_pairs)]
        synonyms = [(synonym, i) for i, (_, synonym) in enumerate(self.current_pairs)]
        random.shuffle(synonyms)
        
        # Create word cards
        self.word_rects = []
        for i, (word, idx) in enumerate(words):
            row = i // cards_per_row
            col = i % cards_per_row
            
            rect = pygame.Rect(
                start_x + col * (card_width + card_spacing),
                words_y + row * (card_height + card_spacing),
                card_width,
                card_height
            )
            
            self.word_rects.append({
                'rect': rect,
                'text': word,
                'index': idx,
                'matched': False,
                'selected': False,
                'color': Colors.DRAG_WORD
            })
        
        # Create synonym cards
        self.synonym_rects = []
        for i, (synonym, idx) in enumerate(synonyms):
            row = i // cards_per_row
            col = i % cards_per_row
            
            rect = pygame.Rect(
                start_x + col * (card_width + card_spacing),
                synonyms_y + row * (card_height + card_spacing),
                card_width,
                card_height
            )
            
            self.synonym_rects.append({
                'rect': rect,
                'text': synonym,
                'index': idx,
                'matched': False,
                'selected': False,
                'color': Colors.TARGET_BOX
            })
    
    def _check_match(self):
        """Check if selected word and synonym match."""
        if self.selected_word is not None and self.selected_synonym is not None:
            word_idx = self.word_rects[self.selected_word]['index']
            syn_idx = self.synonym_rects[self.selected_synonym]['index']
            
            if word_idx == syn_idx:
                # Correct match
                self.matches_made += 1
                self.score += 100
                
                self.word_rects[self.selected_word]['matched'] = True
                self.word_rects[self.selected_word]['color'] = Colors.MATCH_OK
                self.synonym_rects[self.selected_synonym]['matched'] = True
                self.synonym_rects[self.selected_synonym]['color'] = Colors.MATCH_OK
                
                # Play correct sound
                self.resource_manager.play_sound("assets/sounds/correct.wav", 0.5)
                
                # Record correct attempt
                self.progress_manager.record_attempt("breadth", True)
            else:
                # Wrong match
                self.hp -= 1
                
                # Flash wrong
                self.word_rects[self.selected_word]['color'] = Colors.WRONG_FLASH
                self.synonym_rects[self.selected_synonym]['color'] = Colors.WRONG_FLASH
                
                # Reset after short delay
                pygame.time.set_timer(pygame.USEREVENT + 2, 500)
                
                # Play wrong sound
                self.resource_manager.play_sound("assets/sounds/wrong.wav", 0.5)
                
                # Record wrong attempt
                self.progress_manager.record_attempt("breadth", False)
            
            # Deselect
            self.selected_word = None
            self.selected_synonym = None
            
            # Reset colors for unmatched items
            for item in self.word_rects:
                if not item['matched']:
                    item['color'] = Colors.DRAG_WORD
            for item in self.synonym_rects:
                if not item['matched']:
                    item['color'] = Colors.TARGET_BOX
            
            self._update_ui()
            
            # Check for level complete
            if self.matches_made >= self.total_matches:
                self._show_results()
    
    def _reset_wrong_colors(self):
        """Reset colors after wrong match flash."""
        pygame.time.set_timer(pygame.USEREVENT + 2, 0)
        
        for item in self.word_rects:
            if not item['matched']:
                item['color'] = Colors.DRAG_WORD
        for item in self.synonym_rects:
            if not item['matched']:
                item['color'] = Colors.TARGET_BOX
    
    def _show_results(self):
        """Show results screen."""
        from scenes.results_screen import ResultsScreen
        from core.transition import TransitionType
        
        accuracy = self.progress_manager.get_accuracy("breadth")
        
        results = ResultsScreen(
            self.scene_manager,
            "breadth",
            self.level,
            self.score,
            self.max_score,
            self.total_time,
            accuracy,
            context_score=0.0,
            resilience_score=0.0
        )
        
        self.scene_manager.push_scene(results, TransitionType.FADE)
    
    def _update_ui(self):
        """Update UI elements."""
        self.score_label.set_text(f"Score: {self.score}")
        self.progress_label.set_text(f"Matches: {self.matches_made}/{self.total_matches}")
        
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
        pygame.time.set_timer(pygame.USEREVENT + 2, 0)
    
    def update(self, dt: float):
        """Update game state."""
        self.total_time += dt
        
        # Update timer
        self.timer.update(dt)
        
        # Update UI
        self.back_button.update(dt)
        for bar in self.hp_bars:
            bar.update(dt)
        
        self._update_ui()
    
    def _draw_card(self, surface, card_data, font):
        """Draw a word or synonym card."""
        rect = card_data['rect']
        
        # Draw card background
        pygame.draw.rect(surface, card_data['color'], rect, border_radius=8)
        
        # Draw border
        border_color = Colors.MATCH_BORDER if card_data['matched'] else Colors.DRAG_BORDER
        if card_data['selected']:
            border_color = Colors.ACCENT
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=8)
        
        # Draw text
        text_surf = font.render(card_data['text'], True, Colors.TEXT)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)
    
    def draw(self):
        """Draw game screen."""
        self.screen.fill(Colors.BG)
        
        # Draw UI elements
        self.back_button.draw(self.screen, self.resource_manager)
        self.score_label.draw(self.screen, self.resource_manager)
        self.progress_label.draw(self.screen, self.resource_manager)
        self.instruction_label.draw(self.screen, self.resource_manager)
        
        for bar in self.hp_bars:
            bar.draw(self.screen)
        
        # Draw word and synonym cards
        font = self.resource_manager.get_font(FONT_SIZE_BODY)
        
        for card in self.word_rects:
            self._draw_card(self.screen, card, font)
        
        for card in self.synonym_rects:
            self._draw_card(self.screen, card, font)
        
        self.timer.draw(self.screen, self.resource_manager)
    
    def handle_event(self, event: pygame.event.Event):
        """Handle events."""
        self.back_button.handle_event(event)
        
        if event.type == pygame.USEREVENT + 2:
            self._reset_wrong_colors()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                
                # Check word cards
                for i, card in enumerate(self.word_rects):
                    if not card['matched'] and card['rect'].collidepoint(mouse_pos):
                        if self.selected_word == i:
                            self.selected_word = None
                            card['selected'] = False
                        else:
                            if self.selected_word is not None:
                                self.word_rects[self.selected_word]['selected'] = False
                            self.selected_word = i
                            card['selected'] = True
                        self._check_match()
                        break
                
                # Check synonym cards
                for i, card in enumerate(self.synonym_rects):
                    if not card['matched'] and card['rect'].collidepoint(mouse_pos):
                        if self.selected_synonym == i:
                            self.selected_synonym = None
                            card['selected'] = False
                        else:
                            if self.selected_synonym is not None:
                                self.synonym_rects[self.selected_synonym]['selected'] = False
                            self.selected_synonym = i
                            card['selected'] = True
                        self._check_match()
                        break
