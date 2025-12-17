"""Enhanced hexagonal coordinate system with cube coordinates."""

import math
from typing import List, Tuple, Optional


class HexCoord:
    """Hexagonal coordinate system using axial coordinates with cube support."""
    
    def __init__(self, q: int, r: int, s: int = 0):
        self.q = q  # Column
        self.r = r  # Row
        self.s = s  # Cube coordinate for 3D calculations
    
    def __eq__(self, other):
        if not isinstance(other, HexCoord):
            return False
        return self.q == other.q and self.r == other.r
    
    def __hash__(self):
        return hash((self.q, self.r))
    
    def __str__(self):
        return f"({self.q},{self.r},{self.s})"
    
    def get_neighbors(self) -> List['HexCoord']:
        """Get all 6 neighboring hexagonal coordinates."""
        # Six directions in axial coordinates
        directions = [
            HexCoord(self.q + 1, self.r, self.s - 1),    # East
            HexCoord(self.q + 1, self.r - 1, self.s),    # Southeast
            HexCoord(self.q, self.r - 1, self.s + 1),    # Southwest
            HexCoord(self.q - 1, self.r, self.s + 1),    # West
            HexCoord(self.q - 1, self.r + 1, self.s),    # Northwest
            HexCoord(self.q, self.r + 1, self.s - 1)    # Northeast
        ]
        return directions
    
    def get_distance(self, other: 'HexCoord') -> int:
        """Calculate hex distance using axial coordinates."""
        return (abs(self.q - other.q) + 
                abs(self.q + self.r - other.q - other.r) + 
                abs(self.r - other.r)) // 2
    
    def get_cube_coords(self) -> Tuple[int, int, int]:
        """Convert to cube coordinates."""
        x = self.q
        z = self.s
        y = self.r - (x - z) // 2
        return (x, y, z)
    
    def from_cube(self, x: int, y: int, z: int) -> 'HexCoord':
        """Create HexCoord from cube coordinates."""
        q = x
        r = y + (x - z) // 2
        s = z
        return HexCoord(q, r, s)
    
    @staticmethod
    def from_qr(q: int, r: int) -> 'HexCoord':
        """Create HexCoord from axial coordinates."""
        s = -q - r // 2
        return HexCoord(q, r, s)
    
    @staticmethod
    def direction_to_qr(direction: str) -> Tuple[int, int]:
        """Convert cardinal direction to axial coordinate delta."""
        mapping = {
            'E': (1, 0),      # East
            'NE': (1, -1),     # Northeast
            'N': (0, -1),     # North
            'NW': (-1, 0),     # Northwest
            'W': (-1, 0),      # West
            'SW': (0, 1),      # Southwest
            'SE': (1, 1),      # Southeast
            'S': (0, 1)       # South
        }
        return mapping.get(direction, (0, 0))
    
    @staticmethod
    def get_all_axial_in_range(q_range: Tuple[int, int], r_range: Tuple[int, int]) -> List['HexCoord']:
        """Get all axial coordinates within specified ranges."""
        coords = []
        for r in range(r_range[0], r_range[1] + 1):
            for q in range(q_range[0], q_range[1] + 1):
                # Check if (q, r) is a valid axial coordinate
                if abs(-q - r) <= max(abs(q_range[1] - q_range[0]), 
                                  abs(r_range[1] - r_range[0])) + 1:
                    s = -q - r // 2
                    coords.append(HexCoord(q, r, s))
        return coords
    
    def rotate(self, direction: str) -> 'HexCoord':
        """Rotate coordinate in specified direction."""
        # Simplified rotation using axial coordinates
        rotation_map = {
            'clockwise': {
                'E': 'SE',
                'SE': 'S',
                'S': 'SW',
                'SW': 'W',
                'W': 'NW',
                'NW': 'N',
                'N': 'NE'
            },
            'counterclockwise': {
                'E': 'NE',
                'NE': 'N',
                'N': 'NW',
                'NW': 'W',
                'W': 'SW',
                'SW': 'S',
                'S': 'SE'
            }
        }
        
        # This is a simplification - proper hex rotation would need more complex math
        # For now, we'll use basic axial coordinate transformations
        current_dir_map = rotation_map.get('clockwise', {})
        if direction in current_dir_map:
            dx, dy = HexCoord.direction_to_qr(current_dir_map[direction])
            return HexCoord(self.q + dx, self.r + dy, self.s - 1)
        
        return self
    
    def lerp_to(self, other: 'HexCoord', t: float) -> 'HexCoord':
        """Linear interpolation between two hex coordinates."""
        if t <= 0.0:
            return HexCoord(self.q, self.r, self.s)
        elif t >= 1.0:
            return HexCoord(other.q, other.r, other.s)
        
        # Interpolate using cube coordinates
        x1, y1, z1 = self.get_cube_coords()
        x2, y2, z2 = other.get_cube_coords()
        
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        z = int(z1 + (z2 - z1) * t)
        
        return HexCoord.from_cube(x, y, z)
    
    def get_3d_position(self) -> Tuple[float, float, float]:
        """Get 3D world position for hex rendering."""
        # Convert axial to world position
        size = 20  # Base hex size
        x = size * 3/2 * self.q
        y = size * (math.sqrt(3)/2 * self.q + math.sqrt(3) * self.r)
        
        return (x, y, 0)  # Z coordinate for layering
    
    def get_face_direction(self, target: 'HexCoord') -> str:
        """Get the cardinal direction to face a target hex."""
        # Calculate basic direction using axial coordinates
        dq = target.q - self.q
        dr = target.r - self.r
        
        # Determine dominant direction
        if abs(dq) > abs(dr):
            return 'E' if dq > 0 else 'W'
        else:
            return 'S' if dr > 0 else 'N'
    
    def get_screen_pos(self, size: int = 20, center_offset_x: int = 0, 
                    center_offset_y: int = 0) -> Tuple[int, int]:
        """Get screen position for rendering."""
        # Convert axial to pixel coordinates
        x = size * 3/2 * self.q
        y = size * (math.sqrt(3)/2 * self.q + math.sqrt(3) * self.r)
        
        # Add center offset
        screen_x = int(x + center_offset_x)
        screen_y = int(y + center_offset_y)
        
        return (screen_x, screen_y)