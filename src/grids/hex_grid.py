"""Hexagonal grid system for Phase 4."""

import math
from typing import List, Tuple, Optional
from ..entities.grid_new import HexCoord


class HexGrid:
    """Hexagonal grid system using axial coordinates."""
    
    def __init__(self, width: int, height: int, hex_size: int = 20):
        self.width = width
        self.height = height
        self.hex_size = hex_size
        self._occupied_cells: set = set()
        
        # Pre-calculate hex vertices for rendering
        self._hex_vertices = self._calculate_hex_vertices()
    
    def _calculate_hex_vertices(self) -> List[Tuple[float, float]]:
        """Calculate vertices for a pointy-top hexagon."""
        size = self.hex_size
        height = size * math.sqrt(3)
        
        vertices = [
            (size, 0),                # Right
            (size / 2, height / 2),  # Top-right
            (-size / 2, height / 2), # Top-left
            (-size, 0),               # Left
            (-size / 2, -height / 2), # Bottom-left
            (size / 2, -height / 2),  # Bottom-right
        ]
        
        return vertices
    
    def is_valid_position(self, coord: HexCoord) -> bool:
        """Check if a coordinate is within grid bounds."""
        # Convert axial to bounds checking
        # Simple rectangular bounds for now
        return (abs(coord.q) <= self.width // 2 and 
                abs(coord.r) <= self.height // 2 and
                abs(coord.s) <= max(self.width, self.height) // 2)
    
    def is_occupied(self, coord: HexCoord) -> bool:
        """Check if a cell is occupied."""
        return coord in self._occupied_cells
    
    def occupy(self, coord: HexCoord) -> None:
        """Mark a cell as occupied."""
        self._occupied_cells.add(coord)
    
    def vacate(self, coord: HexCoord) -> None:
        """Mark a cell as unoccupied."""
        self._occupied_cells.discard(coord)
    
    def get_neighbors(self, coord: HexCoord) -> List[HexCoord]:
        """Get all 6 neighboring hexagons."""
        # Six directions in axial coordinates
        directions = [
            HexCoord(1, 0),    # East
            HexCoord(1, -1),   # Southeast
            HexCoord(0, -1),   # Southwest
            HexCoord(-1, 0),   # West
            HexCoord(-1, 1),   # Northwest
            HexCoord(0, 1),    # Northeast
        ]
        
        neighbors = []
        for direction in directions:
            neighbor = HexCoord(coord.q + direction.q, coord.r + direction.r)
            if self.is_valid_position(neighbor):
                neighbors.append(neighbor)
        
        return neighbors
    
    def get_all_cells(self) -> List[HexCoord]:
        """Get all valid hexagonal coordinates."""
        cells = []
        
        # Generate hex grid in axial coordinates
        for r in range(-self.height // 2, self.height // 2 + 1):
            for q in range(-self.width // 2, self.width // 2 + 1):
                coord = HexCoord(q, r)
                if self.is_valid_position(coord):
                    cells.append(coord)
        
        return cells
    
    def get_random_empty_cell(self) -> Optional[HexCoord]:
        """Get a random empty hexagonal cell."""
        all_cells = self.get_all_cells()
        empty_cells = [cell for cell in all_cells if not self.is_occupied(cell)]
        
        if empty_cells:
            import random
            return random.choice(empty_cells)
        
        return None
    
    def clear(self) -> None:
        """Clear all occupied cells."""
        self._occupied_cells.clear()
    
    def get_occupied_cells(self) -> List[HexCoord]:
        """Get all occupied cells."""
        return list(self._occupied_cells)
    
    def count_empty_cells(self) -> int:
        """Count the number of empty cells."""
        return len(self.get_all_cells()) - len(self._occupied_cells)
    
    def hex_to_pixel(self, coord: HexCoord) -> Tuple[int, int]:
        """Convert hexagonal coordinate to pixel position."""
        size = self.hex_size
        x = size * (3/2 * coord.q)
        y = size * (math.sqrt(3)/2 * coord.q + math.sqrt(3) * coord.r)
        
        # Center on screen
        screen_width = 1200  # From config
        screen_height = 800   # From config
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        return (int(center_x + x), int(center_y + y))
    
    def get_hex_vertices(self, coord: HexCoord) -> List[Tuple[int, int]]:
        """Get pixel vertices for a specific hexagon."""
        center_x, center_y = self.hex_to_pixel(coord)
        
        vertices = []
        for vx, vy in self._hex_vertices:
            vertices.append((int(center_x + vx), int(center_y + vy)))
        
        return vertices
    
    def get_hex_center(self, coord: HexCoord) -> Tuple[int, int]:
        """Get center pixel position of a hexagon."""
        return self.hex_to_pixel(coord)
    
    def get_distance(self, coord1: HexCoord, coord2: HexCoord) -> int:
        """Calculate hex distance between two coordinates."""
        return coord1.get_distance(coord2)
    
    def hex_lerp(self, coord1: HexCoord, coord2: HexCoord, t: float) -> Tuple[float, float]:
        """Linear interpolation between two hex coordinates."""
        # Convert to pixel space, lerp, return pixel coordinates
        x1, y1 = self.hex_to_pixel(coord1)
        x2, y2 = self.hex_to_pixel(coord2)
        
        return (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)