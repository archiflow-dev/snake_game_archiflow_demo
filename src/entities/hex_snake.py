"""Enhanced snake entity for hexagonal grid movement."""

from typing import List, Optional, Tuple
from enum import Enum
from ..entities.grid import HexCoord


class HexSnake:
    """Snake entity adapted for hexagonal grid movement."""
    
    def __init__(self, initial_position: HexCoord, initial_direction: HexCoord, grid: HexagonalGrid):
        # Convert to hexagonal coordinate system
        self.hex_grid = grid
        self.hex_directions = grid.directions
        
        # Initialize with hex coordinates
        self.segments: List[HexCoord] = [initial_position]
        self.direction: HexCoord = initial_direction
        self.next_direction: Optional[HexCoord] = None
        
        # Snake properties
        self.growing = 0
        self.alive = True
        
        # Occupy initial position on grid
        grid.occupy(initial_position)
    
    def move(self) -> bool:
        """Move the snake one hex in the current direction."""
        if not self.alive:
            return False
        
        # Update direction if there's a pending one
        if self.next_direction and self.next_direction != self.get_opposite_direction(self.direction):
            self.direction = self.next_direction
            self.next_direction = None
        
        # Calculate new head position
        current_head = self.segments[-1]
        new_head = HexCoord(
            current_head.q + self.direction.q,
            current_head.r + self.direction.r
        )
        
        # Check if new position is valid
        if not self.hex_grid.is_valid_position(new_head):
            self.alive = False
            return False
        
        # Check for self-collision (but not food collision)
        # Only check collision with snake segments, not food
        if new_head in self.segments[:-1]:  # Check all segments except head itself
            self.alive = False
            return False
        
        # Move snake
        self.segments.append(new_head)
        self.hex_grid.occupy(new_head)
        
        # Handle growth
        if self.growing > 0:
            self.growing -= 1
        else:
            # Remove tail if not growing
            tail = self.segments.pop(0)
            self.hex_grid.vacate(tail)
        
        return True
    
    def change_direction(self, new_direction: HexCoord) -> None:
        """Set the next movement direction."""
        # Only allow direction change if it's not opposite to current
        if new_direction != self.get_opposite_direction(self.direction):
            self.next_direction = new_direction
    
    def grow(self, amount: int = 1) -> None:
        """Make the snake grow by the specified amount."""
        self.growing += amount
    
    def get_head_position(self) -> HexCoord:
        """Get the current head position."""
        return self.segments[-1]
    
    def get_tail_position(self) -> HexCoord:
        """Get the current tail position."""
        return self.segments[0]
    
    def check_self_collision(self) -> bool:
        """Check if the snake has collided with itself."""
        head = self.get_head_position()
        # Check if head position is in body segments (excluding head itself)
        return head in self.segments[:-1]
    
    def get_opposite_direction(self, direction: HexCoord) -> HexCoord:
        """Get the opposite hexagonal direction."""
        return HexCoord(-direction.q, -direction.r)
    
    def get_possible_moves(self) -> List[HexCoord]:
        """Get all valid moves from current position."""
        head = self.get_head_position()
        possible_moves = []
        
        for direction in self.hex_directions:
            # Skip opposite direction
            if direction == self.get_opposite_direction(self.direction):
                continue
            
            new_pos = HexCoord(head.q + direction.q, head.r + direction.r)
            if self.hex_grid.is_valid_position(new_pos):
                possible_moves.append(new_pos)
        
        return possible_moves
    
    def get_safe_moves(self) -> List[HexCoord]:
        """Get moves that won't immediately cause collision."""
        possible_moves = self.get_possible_moves()
        safe_moves = []
        
        for move in possible_moves:
            if not self.hex_grid.is_occupied(move) or move == self.segments[0]:
                safe_moves.append(move)
        
        return safe_moves
    
    def get_length(self) -> int:
        """Get the current length of the snake."""
        return len(self.segments)
    
    def will_collide_at(self, position: HexCoord) -> bool:
        """Check if snake would collide at the given position."""
        # Would collide if position is occupied by body (except potential tail)
        if position == self.segments[0] and self.growing == 0:
            return False  # Will move tail away
        
        return position in self.segments and position != self.get_head_position()
    
    def reset(self, initial_position: HexCoord, initial_direction: HexCoord) -> None:
        """Reset the snake to initial state."""
        # Clear current segments from grid
        for segment in self.segments:
            self.hex_grid.vacate(segment)
        
        # Reset snake state
        self.segments = [initial_position]
        self.direction = initial_direction
        self.next_direction = None
        self.growing = 0
        self.alive = True
        
        # Occupy new initial position
        self.hex_grid.occupy(initial_position)
    
    def get_segment_positions(self) -> List[HexCoord]:
        """Get all segment positions in order from tail to head."""
        return self.segments.copy()
    
    def get_direction_name(self) -> Optional[str]:
        """Get the name of the current direction."""
        direction_names = {
            HexCoord(0, -1): 'north',
            HexCoord(1, -1): 'northeast',
            HexCoord(1, 0): 'southeast',
            HexCoord(0, 1): 'south',
            HexCoord(-1, 1): 'southwest',
            HexCoord(-1, 0): 'northwest',
        }
        return direction_names.get(self.direction)
    
    def calculate_future_head_position(self, steps: int = 1) -> Optional[HexCoord]:
        """Calculate where the head will be after given number of steps."""
        if not self.alive:
            return None
        
        head = self.get_head_position()
        future_pos = HexCoord(head.q + self.direction.q * steps, 
                             head.r + self.direction.r * steps)
        
        return future_pos if self.hex_grid.is_valid_position(future_pos) else None
    
    def is_at_position(self, position: HexCoord) -> bool:
        """Check if any part of the snake is at the given position."""
        return position in self.segments
    
    def get_distance_to_position(self, position: HexCoord) -> int:
        """Get hex distance from snake head to position."""
        return self.get_head_position().get_distance(position)
    
    def copy(self) -> 'HexSnake':
        """Create a deep copy of the snake (for simulation/preview)."""
        new_snake = HexSnake(self.segments[0], self.direction, self.hex_grid)
        new_snake.segments = self.segments.copy()
        new_snake.next_direction = self.next_direction
        new_snake.growing = self.growing
        new_snake.alive = self.alive
        return new_snake