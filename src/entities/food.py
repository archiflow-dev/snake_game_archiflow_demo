"""Food entity for the snake game."""

from typing import Optional, Union
import random
from .grid import SquareCoord, Grid


class Food:
    """Represents food that the snake can eat."""

    def __init__(self, position: Union['SquareCoord', 'HexCoord'], food_type: str = "apple", point_value: int = 10):
        self.position = position
        self.food_type = food_type
        self.point_value = point_value
        self.visual_effects = []  # Will be used for visual effects later
    
    def __repr__(self) -> str:
        return f"Food({self.position}, {self.food_type}, {self.point_value})"
    
    @staticmethod
    def spawn_food(grid: Grid, food_type: str = "apple", point_value: int = 10) -> Optional['Food']:
        """Spawn a new food item at a random empty position."""
        empty_position = grid.get_random_empty_cell()
        
        if empty_position is None:
            return None
        
        return Food(empty_position, food_type, point_value)
    
    def set_position(self, position: Union['SquareCoord', 'HexCoord']) -> None:
        """Set the food position."""
        self.position = position

    def get_position(self) -> Union['SquareCoord', 'HexCoord']:
        """Get the food position."""
        return self.position
    
    def get_type(self) -> str:
        """Get the food type."""
        return self.food_type
    
    def get_point_value(self) -> int:
        """Get the point value of this food."""
        return self.point_value
    
    def add_visual_effect(self, effect: str) -> None:
        """Add a visual effect to the food."""
        if effect not in self.visual_effects:
            self.visual_effects.append(effect)
    
    def remove_visual_effect(self, effect: str) -> None:
        """Remove a visual effect from the food."""
        if effect in self.visual_effects:
            self.visual_effects.remove(effect)
    
    def has_visual_effect(self, effect: str) -> bool:
        """Check if the food has a specific visual effect."""
        return effect in self.visual_effects