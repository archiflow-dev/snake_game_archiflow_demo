"""Event system for decoupled communication between game systems."""

from typing import Callable, Dict, List, Any
from enum import Enum


class EventType(Enum):
    """Enumeration of game event types."""
    QUIT = "quit"
    PAUSE = "pause"
    RESUME = "resume"
    RESTART = "restart"
    GAME_OVER = "game_over"
    FOOD_EATEN = "food_eaten"
    SCORE_CHANGED = "score_changed"
    SPEED_CHANGED = "speed_changed"
    SNAAKE_MOVED = "snake_moved"


class Event:
    """Represents a game event with optional data."""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any] = None):
        self.type = event_type
        self.data = data or {}
        self.timestamp = 0  # Would be set to current time in real implementation


class EventManager:
    """Manages event registration and dispatching between game systems."""
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """Subscribe to a specific event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """Unsubscribe from a specific event type."""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
            except ValueError:
                pass  # Callback not found
    
    def dispatch(self, event: Event) -> None:
        """Dispatch an event to all subscribed listeners."""
        if event.type in self._listeners:
            for callback in self._listeners[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")
    
    def clear_all_listeners(self) -> None:
        """Clear all event listeners."""
        self._listeners.clear()