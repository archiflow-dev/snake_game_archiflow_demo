"""Unit tests for food functionality."""

import pytest
from src.entities.grid import SquareCoord, Grid
from src.entities.food import Food


class TestFood:
    """Test Food functionality."""
    
    def test_food_creation(self):
        """Test creating food."""
        pos = SquareCoord(5, 5)
        food = Food(pos, "apple", 10)
        
        assert food.get_position() == pos
        assert food.get_type() == "apple"
        assert food.get_point_value() == 10
    
    def test_food_position_management(self):
        """Test food position management."""
        pos = SquareCoord(5, 5)
        food = Food(pos, "apple", 10)
        
        new_pos = SquareCoord(10, 10)
        food.set_position(new_pos)
        
        assert food.get_position() == new_pos
    
    def test_visual_effects(self):
        """Test visual effects management."""
        food = Food(SquareCoord(5, 5), "apple", 10)
        
        # Initially no effects
        assert len(food.visual_effects) == 0
        assert not food.has_visual_effect("sparkle")
        
        # Add effect
        food.add_visual_effect("sparkle")
        assert food.has_visual_effect("sparkle")
        assert "sparkle" in food.visual_effects
        
        # Add another effect
        food.add_visual_effect("glow")
        assert food.has_visual_effect("sparkle")
        assert food.has_visual_effect("glow")
        assert len(food.visual_effects) == 2
        
        # Remove effect
        food.remove_visual_effect("sparkle")
        assert not food.has_visual_effect("sparkle")
        assert food.has_visual_effect("glow")
        assert len(food.visual_effects) == 1
        
        # Remove non-existent effect (should not error)
        food.remove_visual_effect("nonexistent")
        assert len(food.visual_effects) == 1
    
    def test_spawn_food(self):
        """Test spawning food on grid."""
        grid = Grid(10, 10)
        
        # Spawn food on empty grid
        food = Food.spawn_food(grid)
        assert food is not None
        assert grid.is_valid_position(food.get_position())
        assert not grid.is_occupied(food.get_position())
        
        # Mark the position as occupied
        grid.occupy(food.get_position())
        
        # Try to spawn another food
        food2 = Food.spawn_food(grid)
        assert food2 is not None
        assert food2.get_position() != food.get_position()
        
        # Occupy all cells
        for x in range(10):
            for y in range(10):
                grid.occupy(SquareCoord(x, y))
        
        # Should not be able to spawn food
        food3 = Food.spawn_food(grid)
        assert food3 is None
    
    def test_spawn_food_with_custom_type(self):
        """Test spawning food with custom type and value."""
        grid = Grid(10, 10)
        
        food = Food.spawn_food(grid, "golden_apple", 50)
        assert food is not None
        assert food.get_type() == "golden_apple"
        assert food.get_point_value() == 50
    
    def test_food_repr(self):
        """Test food string representation."""
        pos = SquareCoord(5, 5)
        food = Food(pos, "apple", 10)
        
        repr_str = repr(food)
        assert "Food" in repr_str
        assert "(5, 5)" in repr_str
        assert "apple" in repr_str
        assert "10" in repr_str