"""Game state management for the snake game."""

from enum import Enum
from typing import Optional


class GameState(Enum):
    """Enumeration of possible game states."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    REPLAY = "replay"


class StateManager:
    """Manages game state transitions and current state tracking."""
    
    def __init__(self):
        self._current_state: GameState = GameState.MENU
        self._previous_state: Optional[GameState] = None
        self._state_handlers: Dict[GameState, Callable] = {}
    
    def get_current_state(self) -> GameState:
        """Get the current game state."""
        return self._current_state
    
    def set_state(self, new_state: GameState) -> bool:
        """Transition to a new state. Returns True if transition was successful."""
        if new_state == self._current_state:
            return False
        
        self._previous_state = self._current_state
        self._current_state = new_state
        
        # Call state handler if registered
        if new_state in self._state_handlers:
            self._state_handlers[new_state]()
        
        return True
    
    def register_state_handler(self, state: GameState, handler: Callable[[], None]) -> None:
        """Register a handler function to be called when entering a state."""
        self._state_handlers[state] = handler
    
    def can_transition_to(self, target_state: GameState) -> bool:
        """Check if transition to target state is allowed from current state."""
        valid_transitions = {
            GameState.MENU: [GameState.PLAYING, GameState.REPLAY],
            GameState.PLAYING: [GameState.PAUSED, GameState.GAME_OVER],
            GameState.PAUSED: [GameState.PLAYING, GameState.MENU],
            GameState.GAME_OVER: [GameState.MENU, GameState.PLAYING],
            GameState.REPLAY: [GameState.MENU]
        }
        
        return target_state in valid_transitions.get(self._current_state, [])
    
    def is_in_gameplay(self) -> bool:
        """Check if currently in a gameplay state (playing or paused)."""
        return self._current_state in [GameState.PLAYING, GameState.PAUSED]
    
    def restart_gameplay(self) -> bool:
        """Restart gameplay from game over state."""
        if self._current_state == GameState.GAME_OVER:
            return self.set_state(GameState.PLAYING)
        return False