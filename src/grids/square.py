"""Square grid implementation for the snake game."""

from typing import List, Optional
import random
from .base import BaseGrid
from ..entities.grid import SquareCoord


class SquareGrid(BaseGrid):
    """Square grid implementation with 4-directional movement."""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
    
    def is_valid_position(self, coord: SquareCoord) -> bool:
        """Check if a coordinate is within grid bounds."""
        if not isinstance(coord, SquareCoord):
            return False
        return (0 <= coord.x < self.width and 
                0 <= coord.y < self.height)
    
    def get_neighbors(self, coord: SquareCoord) -> List[SquareCoord]:
        """Get all valid neighboring cells (up, down, left, right)."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
        neighbors = []
        
        for dx, dy in directions:
            neighbor = SquareCoord(coord.x + dx, coord.y + dy)
            if self.is_valid_position(neighbor):
                neighbors.append(neighbor)
        
        return neighbors
    
    def get_random_empty_cell(self) -> Optional[SquareCoord]:
        """Get a random empty cell on the grid."""
        if len(self._occupied_cells) >= self.width * self.height:
            return None
        
        # Find empty cells
        empty_cells = []
        for x in range(self.width):
            for y in range(self.height):
                coord = SquareCoord(x, y)
                if not self.is_occupied(coord):
                    empty_cells.append(coord)
        
        return random.choice(empty_cells) if empty_cells else None