"""Grid system for snake game."""

from typing import List, Tuple, Optional
import random


class SquareCoord:
    """Coordinate system for square grid."""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, SquareCoord):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __repr__(self) -> str:
        return f"SquareCoord({self.x}, {self.y})"


class HexCoord:
    """Axial coordinate system for hexagonal grid."""
    
    def __init__(self, q: int, r: int):
        self.q = q  # Column
        self.r = r  # Row
    
    @property
    def s(self) -> int:
        """Third axial coordinate (derived from q + r + s = 0)."""
        return -self.q - self.r
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, HexCoord):
            return False
        return self.q == other.q and self.r == other.r
    
    def __hash__(self) -> int:
        return hash((self.q, self.r))
    
    def __repr__(self) -> str:
        return f"HexCoord({self.q}, {self.r})"
    
    def get_distance(self, other: 'HexCoord') -> int:
        """Calculate hex distance between two coordinates."""
        return (abs(self.q - other.q) + abs(self.q + self.r - other.q - other.r) + abs(self.r - other.r)) // 2


class Grid:
    """Square grid for the snake game."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._occupied_cells: set = set()
    
    def is_valid_position(self, coord: SquareCoord) -> bool:
        """Check if a coordinate is within grid bounds."""
        return (0 <= coord.x < self.width and 
                0 <= coord.y < self.height)
    
    def is_occupied(self, coord: SquareCoord) -> bool:
        """Check if a cell is occupied."""
        return coord in self._occupied_cells
    
    def occupy(self, coord: SquareCoord) -> None:
        """Mark a cell as occupied."""
        self._occupied_cells.add(coord)
    
    def vacate(self, coord: SquareCoord) -> None:
        """Mark a cell as unoccupied."""
        self._occupied_cells.discard(coord)
    
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
    
    def get_neighbors(self, coord: SquareCoord) -> List[SquareCoord]:
        """Get all valid neighboring cells (up, down, left, right)."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
        neighbors = []
        
        for dx, dy in directions:
            neighbor = SquareCoord(coord.x + dx, coord.y + dy)
            if self.is_valid_position(neighbor):
                neighbors.append(neighbor)
        
        return neighbors
    
    def clear(self) -> None:
        """Clear all occupied cells."""
        self._occupied_cells.clear()
    
    def get_occupied_cells(self) -> List[SquareCoord]:
        """Get a list of all occupied cells."""
        return list(self._occupied_cells)
    
    def count_empty_cells(self) -> int:
        """Count the number of empty cells."""
        return self.width * self.height - len(self._occupied_cells)