"""Snake entity for the snake game."""

from typing import List, Optional, Tuple
from enum import Enum
from .grid import SquareCoord


class Direction(Enum):
    """Enumeration of movement directions."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
    def get_dx_dy(self) -> Tuple[int, int]:
        """Get the x and y movement delta."""
        return self.value


class Snake:
    """Represents the snake entity."""
    
    def __init__(self, start_position: SquareCoord, start_direction: Direction = Direction.RIGHT, start_length: int = 3):
        self.segments: List[SquareCoord] = []
        self.direction = start_direction
        self.next_direction = start_direction
        self.growth_pending = 0  # No pending growth initially
        self.skin_id = "classic"
        
        # Initialize snake segments
        self._create_initial_segments(start_position, start_direction, start_length)
    
    def _create_initial_segments(self, start: SquareCoord, direction: Direction, length: int) -> None:
        """Create initial snake segments."""
        dx, dy = direction.get_dx_dy()
        
        # Create segments from head to tail
        for i in range(length):
            segment = SquareCoord(start.x - dx * i, start.y - dy * i)
            self.segments.append(segment)
    
    def get_head(self) -> SquareCoord:
        """Get the head position of the snake."""
        return self.segments[0] if self.segments else None
    
    def get_tail(self) -> SquareCoord:
        """Get the tail position of the snake."""
        return self.segments[-1] if self.segments else None
    
    def set_direction(self, new_direction: Direction) -> bool:
        """Set the next direction. Returns False if direction is invalid (reverse)."""
        dx, dy = self.direction.get_dx_dy()
        new_dx, new_dy = new_direction.get_dx_dy()
        
        # Prevent 180-degree turns
        if dx + new_dx == 0 and dy + new_dy == 0:
            return False
        
        self.next_direction = new_direction
        return True
    
    def move(self) -> SquareCoord:
        """Move the snake one step forward. Returns the new head position."""
        if not self.segments:
            return None
        
        # Update direction
        self.direction = self.next_direction
        
        # Calculate new head position
        head = self.get_head()
        dx, dy = self.direction.get_dx_dy()
        new_head = SquareCoord(head.x + dx, head.y + dy)
        
        # Insert new head
        self.segments.insert(0, new_head)
        
        # Remove tail if not growing
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            # Remove tail and return its position
            tail = self.segments.pop()
            return tail
        
        # Growing - no tail removed
        return None
    
    def grow(self, amount: int = 1) -> None:
        """Schedule snake to grow by specified amount."""
        self.growth_pending += amount
    
    def check_self_collision(self) -> bool:
        """Check if snake has collided with itself."""
        if len(self.segments) < 4:  # Can't self-collide with less than 4 segments
            return False
        
        head = self.get_head()
        return head in self.segments[1:]  # Check if head is in body (excluding head itself)
    
    def get_length(self) -> int:
        """Get the current length of the snake."""
        return len(self.segments)
    
    def occupies_position(self, coord: SquareCoord) -> bool:
        """Check if snake occupies a specific position."""
        return coord in self.segments
    
    def get_segments(self) -> List[SquareCoord]:
        """Get a copy of all snake segments."""
        return self.segments.copy()
    
    def set_skin(self, skin_id: str) -> None:
        """Set the snake skin."""
        self.skin_id = skin_id