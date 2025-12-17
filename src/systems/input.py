"""Input handling system for the snake game."""

import pygame
from typing import Optional, Dict, Callable, List
from queue import Queue


class InputManager:
    """Manages keyboard input with buffering for responsive controls."""
    
    def __init__(self):
        self._key_mappings: Dict[int, str] = {}
        self._action_handlers: Dict[str, Callable] = {}
        self._input_buffer: Queue = Queue()
        self._active_keys: set = set()
        
        # Default WASD mapping
        self._setup_default_mappings()
    
    def _setup_default_mappings(self) -> None:
        """Setup default key mappings."""
        self._key_mappings = {
            pygame.K_w: 'move_up',
            pygame.K_a: 'move_left',
            pygame.K_s: 'move_down',
            pygame.K_d: 'move_right',
            pygame.K_ESCAPE: 'pause',
            pygame.K_r: 'restart',
            pygame.K_SPACE: 'start',
        }
    
    def register_action_handler(self, action: str, handler: Callable[[], None]) -> None:
        """Register a handler for a specific action."""
        self._action_handlers[action] = handler
    
    def set_key_mapping(self, key: int, action: str) -> None:
        """Set or change a key mapping."""
        self._key_mappings[key] = action
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event."""
        if event.type == pygame.KEYDOWN:
            self._handle_key_down(event.key)
        elif event.type == pygame.KEYUP:
            self._handle_key_up(event.key)
    
    def _handle_key_down(self, key: int) -> None:
        """Handle key press events."""
        self._active_keys.add(key)
        
        # Check if this key is mapped to an action
        if key in self._key_mappings:
            action = self._key_mappings[key]
            
            # Add to input buffer for actions that need buffering (like movement)
            if action.startswith('move_'):
                self._input_buffer.put(action)
            
            # Call immediate handler for other actions
            if action in self._action_handlers:
                self._action_handlers[action]()
    
    def _handle_key_up(self, key: int) -> None:
        """Handle key release events."""
        self._active_keys.discard(key)
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed."""
        return key in self._active_keys
    
    def get_buffered_action(self) -> Optional[str]:
        """Get the next buffered action (FIFO)."""
        if not self._input_buffer.empty():
            return self._input_buffer.get()
        return None
    
    def clear_buffer(self) -> None:
        """Clear the input buffer."""
        while not self._input_buffer.empty():
            self._input_buffer.get()
    
    def get_action_from_key(self, key: int) -> Optional[str]:
        """Get the action mapped to a key."""
        return self._key_mappings.get(key)
    
    def update(self) -> None:
        """Update input state (call once per frame)."""
        # This can be used for more complex input processing
        pass
    
    def get_movement_direction(self) -> Optional[str]:
        """Get the next movement direction from buffer, filtering invalid sequences."""
        # Get all buffered movement actions
        movement_actions = []
        temp_buffer = Queue()
        
        # Extract movement actions while preserving other actions
        while not self._input_buffer.empty():
            action = self._input_buffer.get()
            if action.startswith('move_'):
                movement_actions.append(action)
            else:
                temp_buffer.put(action)
        
        # Put non-movement actions back
        while not temp_buffer.empty():
            self._input_buffer.put(temp_buffer.get())
        
        # Return the latest movement action
        return movement_actions[-1] if movement_actions else None