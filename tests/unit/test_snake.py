"""Unit tests for snake functionality."""

import pytest
from src.entities.grid import SquareCoord
from src.entities.snake import Snake, Direction


class TestDirection:
    """Test Direction enum."""
    
    def test_direction_values(self):
        """Test direction coordinate values."""
        assert Direction.UP.get_dx_dy() == (0, -1)
        assert Direction.DOWN.get_dx_dy() == (0, 1)
        assert Direction.LEFT.get_dx_dy() == (-1, 0)
        assert Direction.RIGHT.get_dx_dy() == (1, 0)


class TestSnake:
    """Test Snake functionality."""
    
    def test_snake_creation(self):
        """Test creating a snake."""
        start_pos = SquareCoord(10, 7)
        snake = Snake(start_pos, Direction.RIGHT, 3)
        
        assert snake.get_length() == 3
        assert snake.direction == Direction.RIGHT
        assert snake.next_direction == Direction.RIGHT
        assert snake.growth_pending == 0
    
    def test_initial_segments(self):
        """Test initial segment placement."""
        start_pos = SquareCoord(10, 7)
        snake = Snake(start_pos, Direction.RIGHT, 3)
        
        segments = snake.get_segments()
        
        # Head should be at start position
        assert segments[0] == SquareCoord(10, 7)
        # Body segments should extend behind head
        assert segments[1] == SquareCoord(9, 7)
        assert segments[2] == SquareCoord(8, 7)
    
    def test_get_head_and_tail(self):
        """Test getting head and tail positions."""
        start_pos = SquareCoord(10, 7)
        snake = Snake(start_pos, Direction.RIGHT, 3)
        
        assert snake.get_head() == SquareCoord(10, 7)
        assert snake.get_tail() == SquareCoord(8, 7)
    
    def test_set_direction(self):
        """Test setting direction."""
        snake = Snake(SquareCoord(10, 7), Direction.RIGHT, 3)
        
        # Valid direction change
        assert snake.set_direction(Direction.UP)
        assert snake.next_direction == Direction.UP
        
        # Invalid 180-degree turn
        assert not snake.set_direction(Direction.LEFT)
        assert snake.next_direction == Direction.UP  # Should remain unchanged
    
    def test_movement(self):
        """Test snake movement."""
        snake = Snake(SquareCoord(10, 7), Direction.RIGHT, 3)
        
        # Move right
        tail_pos = snake.move()
        
        # Head should move right
        assert snake.get_head() == SquareCoord(11, 7)
        # Tail should move (no growth)
        assert tail_pos == SquareCoord(8, 7)
        # Length should remain same
        assert snake.get_length() == 3
        
        # Direction should be updated from next_direction
        assert snake.direction == Direction.RIGHT
    
    def test_movement_with_growth(self):
        """Test movement with growth."""
        snake = Snake(SquareCoord(10, 7), Direction.RIGHT, 3)
        
        # Schedule growth
        snake.grow(2)
        assert snake.growth_pending == 2
        
        # Move - should grow, no tail removal
        tail_pos = snake.move()
        assert tail_pos is None  # No tail removed
        assert snake.get_length() == 4
        assert snake.growth_pending == 1
        
        # Move again - should still grow
        tail_pos = snake.move()
        assert tail_pos is None
        assert snake.get_length() == 5
        assert snake.growth_pending == 0
        
        # Move again - no more growth, tail should move
        tail_pos = snake.move()
        assert tail_pos == SquareCoord(8, 7)  # Original tail
        assert snake.get_length() == 5
    
    def test_self_collision(self):
        """Test self-collision detection."""
        snake = Snake(SquareCoord(5, 5), Direction.RIGHT, 4)
        
        # Short snake can't self-collide
        assert not snake.check_self_collision()
        
        # Grow snake to make it longer
        snake.grow(10)
        
        # Move snake in a square pattern
        for _ in range(3):
            snake.move()
        
        snake.set_direction(Direction.DOWN)
        snake.move()
        snake.set_direction(Direction.LEFT)
        snake.move()
        snake.set_direction(Direction.UP)
        snake.move()
        
        # Now head should be adjacent to body, not colliding yet
        assert not snake.check_self_collision()
        
        # One more move up should cause collision
        snake.move()
        assert snake.check_self_collision()
    
    def test_occupies_position(self):
        """Test checking if snake occupies a position."""
        snake = Snake(SquareCoord(10, 7), Direction.RIGHT, 3)
        
        # Head position
        assert snake.occupies_position(SquareCoord(10, 7))
        # Body positions
        assert snake.occupies_position(SquareCoord(9, 7))
        assert snake.occupies_position(SquareCoord(8, 7))
        # Empty position
        assert not snake.occupies_position(SquareCoord(11, 7))
    
    def test_skin_management(self):
        """Test skin management."""
        snake = Snake(SquareCoord(10, 7), Direction.RIGHT, 3)
        
        assert snake.skin_id == "classic"
        
        snake.set_skin("neon")
        assert snake.skin_id == "neon"