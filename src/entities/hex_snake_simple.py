"""Simple hex snake entity for testing."""

from typing import List, Tuple, Optional
from src.entities.grid_new import HexCoord
from enum import Enum


class Snake:
    """Simple snake base class for compatibility."""
    
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
    
    def get_head(self):
        return self.position
    
    def move(self):
        return None
    
    def grow(self):
        pass


class HexDirection(Enum):
    """Directions for hexagonal movement."""
    N = "N"    # North
    NE = "NE"  # North-East
    E = "E"    # East
    SE = "SE"  # South-East
    S = "S"    # South
    SW = "SW"  # South-West
    W = "W"    # West
    NW = "NW"  # North-West
    
    def get_dx_dy(self) -> Tuple[int, int]:
        """Get x,y movement for this direction."""
        movement_map = {
            HexDirection.N: (0, -1),      # Up
            HexDirection.NE: (1, 0),      # Up-Right
            HexDirection.E: (1, -1),      # Right
            HexDirection.SE: (0, 1),      # Down-Right
            HexDirection.S: (0, 1),      # Down (same as SE for hex)
            HexDirection.SW: (-1, 1),     # Down-Left
            HexDirection.W: (-1, 0),      # Left
            HexDirection.NW: (-1, 0)      # Up-Left (same as W for hex)
        }
        return movement_map[self]
    
    def get_opposite(self) -> 'HexDirection':
        """Get the opposite direction."""
        opposites = {
            HexDirection.N: HexDirection.S,
            HexDirection.NE: HexDirection.SW,
            HexDirection.E: HexDirection.W,
            HexDirection.SE: HexDirection.NW,
            HexDirection.S: HexDirection.N,
            HexDirection.SW: HexDirection.NE,
            HexDirection.W: HexDirection.E,
            HexDirection.NW: HexDirection.SE
        }
        return opposites[self]


class HexSnake:
    """Simple hexagonal snake for testing."""
    
    def __init__(self, position: HexCoord, direction: Optional[HexDirection] = None):
        self.segments: List[HexCoord] = [position]
        self.direction = direction
        self.next_direction = None
    
    def get_head(self) -> HexCoord:
        """Get the head position."""
        return self.segments[0] if self.segments else None
    
    def get_segments(self) -> List[HexCoord]:
        """Get all segments."""
        return self.segments.copy()
    
    def occupies_position(self, pos: HexCoord) -> bool:
        """Check if snake occupies position."""
        return any(segment.q == pos.q and segment.r == pos.r for segment in self.segments)
    
    def move(self) -> Optional[HexCoord]:
        """Move snake in current direction."""
        if not self.direction or not self.segments:
            return None
        
        # Update direction from next_direction if available
        if hasattr(self, 'next_direction') and self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None
        
        # Get movement
        dx, dy = self.direction.get_dx_dy()
        
        # Calculate new head position
        head = self.segments[0]
        new_q = head.q + dx
        new_r = head.r + dy
        new_pos = HexCoord(new_q, new_r)
        
        # Check self-collision (head hitting body)
        if len(self.segments) > 1:
            for segment in self.segments[1:]:  # Check all segments except head
                if new_pos.q == segment.q and new_pos.r == segment.r:
                    return None  # Collision detected
        
        # Insert new head
        self.segments.insert(0, new_pos)
        
        # Return tail position to be freed
        return self.segments.pop()
    
    def grow(self) -> None:
        """Grow snake by adding segment."""
        if self.segments:
            tail = self.segments[-1]
            self.segments.append(tail)
    
    def set_direction(self, direction: HexDirection) -> None:
        """Set next direction."""
        # Check if it's a 180-degree turn
        if self.direction and self.direction.get_opposite() == direction:
            return
        
        self.next_direction = direction
    
    def check_self_collision(self) -> bool:
        """Check if head collides with body."""
        if len(self.segments) <= 1:
            return False
        
        head = self.segments[0]
        return any(head.q == seg.q and head.r == seg.r for seg in self.segments[1:])