"""Mathematical utilities for the game."""

import math
from typing import Tuple


class MathUtils:
    """Collection of mathematical utility functions."""
    
    @staticmethod
    def distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two points."""
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return math.sqrt(dx * dx + dy * dy)
    
    @staticmethod
    def lerp(start: float, end: float, t: float) -> float:
        """Linear interpolation between start and end."""
        return start + (end - start) * t
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Clamp a value between min and max."""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def smooth_step(edge0: float, edge1: float, x: float) -> float:
        """Smooth step interpolation function."""
        # Clamp x to [0, 1]
        t = MathUtils.clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
        # Smooth step function
        return t * t * (3.0 - 2.0 * t)