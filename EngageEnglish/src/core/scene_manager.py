"""
Scene manager for handling scene stack and transitions.
Manages scene lifecycle and smooth screen transitions.
"""

import pygame
from typing import List, Optional

from core.scene_base import SceneBase
from core.transition import Transition, TransitionType
from core.resource_manager import get_resource_manager


class SceneManager:
    """Manages scene stack and transitions."""
    
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock,
                 progress_manager, data_loader):
        self.screen = screen
        self.clock = clock
        self.progress_manager = progress_manager
        self.data_loader = data_loader
        self.resource_manager = get_resource_manager()
        
        self.scene_stack: List[SceneBase] = []
        self.transition: Optional[Transition] = None
        self.transition_surface: Optional[pygame.Surface] = None
    
    def push_scene(self, scene: SceneBase, transition_type: TransitionType = TransitionType.FADE):
        """Push a new scene onto the stack."""
        # Capture current screen if there's a scene
        if self.scene_stack:
            self.transition_surface = self.screen.copy()
        
        # Enter new scene
        scene.enter()
        self.scene_stack.append(scene)
        
        # Setup transition
        if self.transition_surface:
            self.transition = Transition(transition_type)
            self.transition.start(self.transition_surface, self.screen.copy())
    
    def pop_scene(self, transition_type: TransitionType = TransitionType.FADE):
        """Pop the current scene from the stack."""
        if len(self.scene_stack) > 1:
            # Capture current screen
            current_scene = self.scene_stack[-1]
            current_scene.draw()
            self.transition_surface = self.screen.copy()
            
            # Exit current scene
            current_scene.exit()
            self.scene_stack.pop()
            
            # Enter previous scene (it's already in stack, just needs to be active)
            # No need to call enter() again as scene is still in stack
            
            # Setup transition
            if self.transition_surface:
                self.transition = Transition(transition_type)
                # Draw previous scene to get new surface
                self.scene_stack[-1].draw()
                self.transition.start(self.transition_surface, self.screen.copy())
        else:
            # Can't pop the last scene
            pass
    
    def replace_scene(self, scene: SceneBase, transition_type: TransitionType = TransitionType.FADE):
        """Replace the current scene with a new one."""
        if self.scene_stack:
            # Capture current screen
            current_scene = self.scene_stack[-1]
            current_scene.draw()
            self.transition_surface = self.screen.copy()
            
            # Exit current scene
            current_scene.exit()
            self.scene_stack.pop()
        
        # Push new scene
        scene.enter()
        self.scene_stack.append(scene)
        
        # Setup transition
        if self.transition_surface:
            self.transition = Transition(transition_type)
            self.transition.start(self.transition_surface, self.screen.copy())
    
    def update(self, dt: float):
        """Update all active scenes and transitions."""
        # Update transition if active
        if self.transition:
            self.transition.update(dt)
            if self.transition.is_complete():
                self.transition = None
                self.transition_surface = None
            return  # Don't update scenes during transition
        
        # Update current scene only
        if self.scene_stack:
            self.scene_stack[-1].update(dt)
    
    def draw(self):
        """Draw current scene or transition."""
        # Draw transition if active
        if self.transition and self.transition_surface:
            # Redraw new scene to ensure it's current
            if self.scene_stack:
                self.scene_stack[-1].draw()
            self.transition.draw(self.screen)
            return
        
        # Draw current scene
        if self.scene_stack:
            self.scene_stack[-1].draw()
    
    def handle_event(self, event: pygame.event.Event):
        """Handle events for current scene."""
        # Block events during transition
        if self.transition:
            return
        
        # Pass event to current scene
        if self.scene_stack:
            self.scene_stack[-1].handle_event(event)
    
    def get_current_scene(self) -> Optional[SceneBase]:
        """Get the current active scene."""
        if self.scene_stack:
            return self.scene_stack[-1]
        return None
    
    def is_transitioning(self) -> bool:
        """Check if a transition is currently active."""
        return self.transition is not None
