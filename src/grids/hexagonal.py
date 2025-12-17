"""Hexagonal grid implementation for the snake game."""

from typing import List, Optional
import random
import math
from .base import BaseGrid
from ..entities.grid import HexCoord


class HexagonalGrid(BaseGrid):
    """Hexagonal grid implementation with 6-directional movement."""
    
    def __init__(self, width: int, height: int, hex_size: int = 20):
        super().__init__(width, height)
        self.hex_size = hex_size
        # Hex directions for pointy-top hexagons
        self.directions = [
            HexCoord(1, 0),   # East
            HexCoord(1, -1),  # Northeast
            HexCoord(0, -1),  # Northwest
            HexCoord(-1, 0),  # West
            HexCoord(-1, 1),  # Southwest
            HexCoord(0, 1)    # Southeast
        ]
    
    def is_valid_position(self, coord: HexCoord) -> bool:
        """Check if a hexagonal coordinate is within grid bounds."""
        if not isinstance(coord, HexCoord):
            return False
        
        # Convert axial to pixel to check rectangular bounds
        pixel_x, pixel_y = self.axial_to_pixel(coord)
        
        # Define rectangular boundaries with margin for hexagons
        margin = self.hex_size
        return (margin <= pixel_x < self.width - margin and 
                margin <= pixel_y < self.height - margin)
    
    def get_neighbors(self, coord: HexCoord) -> List[HexCoord]:
        """Get all valid neighboring cells (6 directions)."""
        neighbors = []
        
        for direction in self.directions:
            neighbor = HexCoord(coord.q + direction.q, coord.r + direction.r)
            if self.is_valid_position(neighbor):
                neighbors.append(neighbor)
        
        return neighbors
    
    def axial_to_pixel(self, coord: HexCoord) -> tuple[int, int]:
        """Convert axial coordinates to pixel coordinates for pointy-top hexagons."""
        x = self.hex_size * (math.sqrt(3) * coord.q + math.sqrt(3)/2 * coord.r)
        y = self.hex_size * (3/2 * coord.r)
        return int(x), int(y)
    
    def pixel_to_axial(self, x: float, y: float) -> HexCoord:
        """Convert pixel coordinates to axial coordinates."""
        q = (math.sqrt(3)/3 * x - 1/3 * y) / self.hex_size
        r = (2/3 * y) / self.hex_size
        return self.axial_round(q, r)
    
    def axial_round(self, q: float, r: float) -> HexCoord:
        """Round fractional axial coordinates to nearest hex."""
        s = -q - r
        rq = round(q)
        rr = round(r)
        rs = round(s)
        
        q_diff = abs(rq - q)
        r_diff = abs(rr - r)
        s_diff = abs(rs - s)
        
        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
            
        return HexCoord(int(rq), int(rr))
    
    def get_hex_corners(self, coord: HexCoord) -> List[tuple[int, int]]:
        """Get the corner points of a hexagon for rendering."""
        center_x, center_y = self.axial_to_pixel(coord)
        corners = []
        
        for i in range(6):
            angle = math.pi / 3 * i
            x = center_x + self.hex_size * math.cos(angle)
            y = center_y + self.hex_size * math.sin(angle)
            corners.append((int(x), int(y)))
        
        return corners
    
    def get_random_empty_cell(self) -> Optional[HexCoord]:
        """Get a random empty cell on the hexagonal grid."""
        # Generate a reasonable range of axial coordinates
        max_q = int(self.width // (self.hex_size * 2))
        max_r = int(self.height // (self.hex_size * 1.5))
        
        empty_cells = []
        for q in range(-max_q, max_q + 1):
            for r in range(-max_r, max_r + 1):
                coord = HexCoord(q, r)
                if self.is_valid_position(coord) and not self.is_occupied(coord):
                    empty_cells.append(coord)
        
        return random.choice(empty_cells) if empty_cells else None
    
    def get_direction_vector(self, from_coord: HexCoord, to_coord: HexCoord) -> Optional[HexCoord]:
        """Get the direction vector from one hex to another."""
        dq = to_coord.q - from_coord.q
        dr = to_coord.r - from_coord.r
        
        # Normalize to one of the 6 directions
        for direction in self.directions:
            if direction.q == dq and direction.r == dr:
                return direction
        
        return None
    
    def get_all_valid_coords(self) -> List[HexCoord]:
        """Get all valid coordinates within the hexagonal grid."""
        valid_coords = []
        max_q = int(self.width // (self.hex_size * 2))
        max_r = int(self.height // (self.hex_size * 1.5))
        
        for q in range(-max_q, max_q + 1):
            for r in range(-max_r, max_r + 1):
                coord = HexCoord(q, r)
                if self.is_valid_position(coord):
                    valid_coords.append(coord)
        
        return valid_coords