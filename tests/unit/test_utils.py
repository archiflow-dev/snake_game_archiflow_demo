"""Unit tests for utility functions."""

import pytest
from src.utils.math_utils import MathUtils
from src.utils.colors import Colors


class TestMathUtils:
    """Test MathUtils functionality."""
    
    def test_distance(self):
        """Test distance calculation."""
        # Same point
        assert MathUtils.distance((0, 0), (0, 0)) == 0
        
        # Horizontal distance
        assert MathUtils.distance((0, 0), (3, 0)) == 3
        
        # Vertical distance
        assert MathUtils.distance((0, 0), (0, 4)) == 4
        
        # Diagonal distance (3-4-5 triangle)
        assert MathUtils.distance((0, 0), (3, 4)) == 5
    
    def test_lerp(self):
        """Test linear interpolation."""
        # Start point
        assert MathUtils.lerp(10, 20, 0.0) == 10
        
        # End point
        assert MathUtils.lerp(10, 20, 1.0) == 20
        
        # Middle point
        assert MathUtils.lerp(10, 20, 0.5) == 15
        
        # Beyond range (should still work)
        assert MathUtils.lerp(10, 20, 2.0) == 30
        assert MathUtils.lerp(10, 20, -1.0) == 0
    
    def test_clamp(self):
        """Test value clamping."""
        # Within range
        assert MathUtils.clamp(5, 0, 10) == 5
        
        # Below range
        assert MathUtils.clamp(-5, 0, 10) == 0
        
        # Above range
        assert MathUtils.clamp(15, 0, 10) == 10
        
        # At boundaries
        assert MathUtils.clamp(0, 0, 10) == 0
        assert MathUtils.clamp(10, 0, 10) == 10
    
    def test_smooth_step(self):
        """Test smooth step interpolation."""
        # Before range
        assert MathUtils.smooth_step(0.3, 0.7, 0.0) == 0.0
        
        # After range
        assert MathUtils.smooth_step(0.3, 0.7, 1.0) == 1.0
        
        # Middle of range
        middle = MathUtils.smooth_step(0.3, 0.7, 0.5)
        assert 0.0 < middle < 1.0
        
        # Should be smooth (acceleration at start, deceleration at end)
        early = MathUtils.smooth_step(0.3, 0.7, 0.4)
        middle = MathUtils.smooth_step(0.3, 0.7, 0.5)
        late = MathUtils.smooth_step(0.3, 0.7, 0.6)
        
        # The function should accelerate then decelerate
        # (difference between consecutive points should increase then decrease)
        diff_early_middle = middle - early
        diff_middle_late = late - middle
        
        assert diff_early_middle < diff_middle_late  # Still accelerating


class TestColors:
    """Test Colors functionality."""
    
    def test_basic_colors(self):
        """Test basic color constants."""
        assert Colors.BLACK == (0, 0, 0)
        assert Colors.WHITE == (255, 255, 255)
        assert Colors.RED == (255, 0, 0)
        assert Colors.GREEN == (0, 255, 0)
        assert Colors.BLUE == (0, 0, 255)
    
    def test_game_colors(self):
        """Test game-specific color constants."""
        assert Colors.SNAKE_HEAD == (0, 255, 0)
        assert Colors.SNAKE_BODY == (0, 200, 0)
        assert Colors.FOOD == (255, 0, 0)
        assert Colors.BACKGROUND == (20, 20, 20)
    
    def test_theme_colors(self):
        """Test theme color constants."""
        assert len(Colors.NEON_GREEN) == 3
        assert len(Colors.NEON_PINK) == 3
        assert len(Colors.NEON_BLUE) == 3
        assert len(Colors.NEON_YELLOW) == 3
        
        # Check that values are valid RGB (0-255)
        for color in [Colors.NEON_GREEN, Colors.NEON_PINK, Colors.NEON_BLUE, Colors.NEON_YELLOW]:
            for component in color:
                assert 0 <= component <= 255
    
    def test_hex_to_rgb(self):
        """Test hex color conversion."""
        # Black
        assert Colors.hex_to_rgb("#000000") == (0, 0, 0)
        
        # White
        assert Colors.hex_to_rgb("#FFFFFF") == (255, 255, 255)
        
        # Red
        assert Colors.hex_to_rgb("#FF0000") == (255, 0, 0)
        
        # Green
        assert Colors.hex_to_rgb("#00FF00") == (0, 255, 0)
        
        # Blue
        assert Colors.hex_to_rgb("#0000FF") == (0, 0, 255)
        
        # Without hash
        assert Colors.hex_to_rgb("FF0000") == (255, 0, 0)
        
        # Mixed case
        assert Colors.hex_to_rgb("#ff00FF") == (255, 0, 255)