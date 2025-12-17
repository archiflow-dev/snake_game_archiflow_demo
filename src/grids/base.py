"""Abstract base class for grid systems."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


class BaseGrid(ABC):
    """Abstract base class for all grid implementations."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._occupied_cells: set = set()
    
    @abstractmethod
    def is_valid_position(self, coord) -> bool:
        """Check if a coordinate is within grid bounds."""
        pass
    
    @abstractmethod
    def get_neighbors(self, coord) -> List:
        """Get all valid neighboring cells."""
        pass
    
    def is_occupied(self, coord) -> bool:
        """Check if a cell is occupied."""
        return coord in self._occupied_cells
    
    def occupy(self, coord) -> None:
        """Mark a cell as occupied."""
        self._occupied_cells.add(coord)
    
    def vacate(self, coord) -> None:
        """Mark a cell as unoccupied."""
        self._occupied_cells.discard(coord)
    
    def clear(self) -> None:
        """Clear all occupied cells."""
        self._occupied_cells.clear()
    
    def get_occupied_cells(self):
        """Get a list of all occupied cells."""
        return list(self._occupied_cells)
    
    def count_empty_cells(self) -> int:
        """Count the number of empty cells."""
        return self.width * self.height - len(self._occupied_cells)