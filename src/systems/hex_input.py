"""Hexagonal input handling system for 6-directional movement."""

import pygame
from typing import Optional, Dict, Callable, Set
from .input import InputManager
from ..entities.grid import HexCoord


class HexInputManager(InputManager):
    """Extended input manager for hexagonal grid 6-directional movement."""
    
    def __init__(self):
        super().__init__()
        # Override with hexagonal mappings
        self._setup_hexagonal_mappings()
    
    def _setup_hexagonal_mappings(self) -> None:
        """Setup 6-directional key mappings for hexagonal grid."""
        # Primary WASD + QE for 6 directions (updated mapping)
        self._key_mappings = {
            # Updated primary controls
            pygame.K_d: 'move_southeast',      # Right (SE)
            pygame.K_a: 'move_southwest',     # Down-left (SW)
            pygame.K_e: 'move_northeast',      # Up-right (NE)
            pygame.K_q: 'move_northwest',      # Up-left (NW)
            
            # Additional directions for full 6-directional movement
            pygame.K_s: 'move_south',          # Down (S)
            pygame.K_w: 'move_north',          # Up (N)
            
            # Alternative arrow key mapping (updated to match new control scheme)
            pygame.K_UP: 'move_north',          # Up (N)
            pygame.K_DOWN: 'move_south',        # Down (S)
            pygame.K_LEFT: 'move_northwest',    # Up-left (NW)
            pygame.K_RIGHT: 'move_southeast',   # Right (SE)
            pygame.K_PAGEUP: 'move_northeast',  # Up-right (NE)
            pygame.K_PAGEDOWN: 'move_southwest', # Down-left (SW)
            
            # Control keys
            pygame.K_ESCAPE: 'pause',
            pygame.K_r: 'restart',
            pygame.K_SPACE: 'start',
        }
        
        # Map hex directions to vectors
        self._hex_directions = {
            'move_north': HexCoord(0, -1),
            'move_northeast': HexCoord(1, -1),
            'move_southeast': HexCoord(1, 0),
            'move_south': HexCoord(0, 1),
            'move_southwest': HexCoord(-1, 1),
            'move_northwest': HexCoord(-1, 0),
            'move_west': HexCoord(-1, 0),        # Alias for northwest
            'move_east': HexCoord(1, 0),         # Alias for southeast
        }
        
        # Opposite directions for invalid move prevention
        self._opposite_directions = {
            'move_north': 'move_south',
            'move_northeast': 'move_southwest',
            'move_southeast': 'move_northwest',
            'move_south': 'move_north',
            'move_southwest': 'move_northeast',
            'move_northwest': 'move_southeast',
            'move_west': 'move_east',
            'move_east': 'move_west',
        }
    
    def get_hex_direction_vector(self, action: str) -> Optional[HexCoord]:
        """Get the hexagonal direction vector for an action."""
        return self._hex_directions.get(action)
    
    def is_opposite_direction(self, current_direction: str, new_direction: str) -> bool:
        """Check if new direction is opposite to current direction."""
        opposite = self._opposite_directions.get(current_direction)
        return opposite == new_direction
    
    def get_validated_movement(self, current_direction: Optional[str] = None) -> Optional[HexCoord]:
        """Get next valid movement direction, preventing 180-degree turns."""
        movement_actions = []
        
        # Extract all movement actions from buffer
        temp_buffer = []
        while not self._input_buffer.empty():
            action = self._input_buffer.get()
            if action.startswith('move_'):
                movement_actions.append(action)
            else:
                temp_buffer.append(action)
        
        # Put non-movement actions back
        for action in temp_buffer:
            self._input_buffer.put(action)
        
        # Find the first valid movement
        for action in movement_actions:
            # Skip if it's opposite to current direction
            if current_direction and self.is_opposite_direction(current_direction, action):
                continue
            
            direction = self.get_hex_direction_vector(action)
            if direction:
                return direction
        
        return None
    
    def get_movement_direction(self) -> Optional[str]:
        """Get the next movement direction from buffer, filtering invalid sequences."""
        # Extract movement actions
        movement_actions = []
        temp_buffer = []
        
        while not self._input_buffer.empty():
            action = self._input_buffer.get()
            if action.startswith('move_'):
                movement_actions.append(action)
            else:
                temp_buffer.append(action)
        
        # Put non-movement actions back
        for action in temp_buffer:
            self._input_buffer.put(action)
        
        # Return the latest movement action
        return movement_actions[-1] if movement_actions else None
    
    def get_direction_name(self, coord: HexCoord) -> Optional[str]:
        """Get the direction name for a hexagonal coordinate vector."""
        for name, direction in self._hex_directions.items():
            if direction.q == coord.q and direction.r == coord.r:
                return name
        return None
    
    def get_all_direction_names(self) -> list[str]:
        """Get all available direction names."""
        return list(self._hex_directions.keys())
    
    def set_hex_key_mapping(self, key: int, direction: str) -> bool:
        """Set a custom hexagonal direction mapping."""
        action = f"move_{direction}"
        if action in self._hex_directions:
            self._key_mappings[key] = action
            return True
        return False
    
    def get_current_keys_pressed(self) -> Set[int]:
        """Get the set of currently pressed keys."""
        return self._active_keys.copy()
    
    def is_movement_key_pressed(self) -> bool:
        """Check if any movement key is currently pressed."""
        for key, action in self._key_mappings.items():
            if action.startswith('move_') and key in self._active_keys:
                return True
        return False
    
    def get_active_movement_directions(self) -> list[str]:
        """Get all currently active movement directions."""
        active_directions = []
        for key, action in self._key_mappings.items():
            if action.startswith('move_') and key in self._active_keys:
                active_directions.append(action)
        return active_directions