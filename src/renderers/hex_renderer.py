"""Hexagonal renderer for the snake game."""

import pygame
import math
from typing import List, Tuple
from .base import BaseRenderer
from ..entities.grid import HexCoord
from ..entities.snake import Snake
from ..entities.food import Food
from ..grids.hexagonal import HexagonalGrid
from ..utils.colors import Colors


class HexagonalRenderer(BaseRenderer):
    """Renderer for hexagonal grid snake game."""
    
    def __init__(self, screen: pygame.Surface, grid: HexagonalGrid):
        super().__init__(screen, grid)
        self.grid = grid  # Type hint for specific grid type
        
        # Colors
        self.grid_color = Colors.GRID_LINES
        self.snake_head_color = Colors.SNAKE_HEAD
        self.snake_body_color = Colors.SNAKE_BODY
        self.food_color = Colors.FOOD
        self.background_color = Colors.BACKGROUND
        
        # Animation and rendering settings
        self.show_grid_lines = True
        self.hex_outline_width = 1
    
    def draw_grid(self) -> None:
        """Draw the hexagonal grid."""
        if not self.show_grid_lines:
            return
        
        # Get all valid coordinates
        valid_coords = self.grid.get_all_valid_coords()
        
        for coord in valid_coords:
            corners = self.grid.get_hex_corners(coord)
            pygame.draw.polygon(self.screen, self.grid_color, corners, self.hex_outline_width)
    
    def draw_snake(self, snake: Snake) -> None:
        """Draw the snake on the hexagonal grid."""
        if not snake.segments:
            return
        
        # Draw body segments first (so head appears on top)
        for i, segment in enumerate(snake.segments[:-1]):
            coord = HexCoord(segment.x, segment.y) if hasattr(segment, 'x') else segment
            self._draw_hex_segment(coord, self.snake_body_color, is_head=False, segment_index=i)
        
        # Draw head last
        head_coord = HexCoord(snake.segments[-1].x, snake.segments[-1].y) if hasattr(snake.segments[-1], 'x') else snake.segments[-1]
        self._draw_hex_segment(head_coord, self.snake_head_color, is_head=True)
    
    def draw_food(self, food: Food) -> None:
        """Draw food on the hexagonal grid."""
        coord = HexCoord(food.position.x, food.position.y) if hasattr(food.position, 'x') else food.position
        self._draw_hex_segment(coord, self.food_color, is_head=False, is_food=True)
    
    def _draw_hex_segment(self, coord: HexCoord, color: Tuple[int, int, int], 
                          is_head: bool = False, segment_index: int = 0, is_food: bool = False) -> None:
        """Draw a single hexagonal segment."""
        corners = self.grid.get_hex_corners(coord)
        
        if is_food:
            # Draw food as a smaller circle inside the hex
            center_x, center_y = self.grid.axial_to_pixel(coord)
            radius = self.grid.hex_size * 0.4
            pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
            # Add a bright center
            pygame.draw.circle(self.screen, Colors.WHITE, (center_x, center_y), radius // 2)
        elif is_head:
            # Draw head with gradient effect
            pygame.draw.polygon(self.screen, color, corners)
            # Add darker outline for depth
            pygame.draw.polygon(self.screen, tuple(c // 2 for c in color), corners, 2)
            
            # Draw eyes (small circles)
            center_x, center_y = self.grid.axial_to_pixel(coord)
            eye_radius = self.grid.hex_size * 0.15
            eye_offset = self.grid.hex_size * 0.3
            
            # Position eyes based on snake direction if available
            left_eye_x = center_x - eye_offset
            left_eye_y = center_y - eye_offset // 2
            right_eye_x = center_x + eye_offset
            right_eye_y = center_y - eye_offset // 2
            
            pygame.draw.circle(self.screen, Colors.WHITE, (int(left_eye_x), int(left_eye_y)), eye_radius)
            pygame.draw.circle(self.screen, Colors.WHITE, (int(right_eye_x), int(right_eye_y)), eye_radius)
            pygame.draw.circle(self.screen, Colors.BLACK, (int(left_eye_x), int(left_eye_y)), eye_radius // 2)
            pygame.draw.circle(self.screen, Colors.BLACK, (int(right_eye_x), int(right_eye_y)), eye_radius // 2)
        else:
            # Draw body segments with slight gradient
            # Darken the color based on segment position for gradient effect
            gradient_factor = max(0.3, 1.0 - (segment_index * 0.05))
            segment_color = tuple(int(c * gradient_factor) for c in color)
            
            pygame.draw.polygon(self.screen, segment_color, corners)
            # Add subtle outline
            outline_color = tuple(int(c * 0.8) for c in segment_color)
            pygame.draw.polygon(self.screen, outline_color, corners, 1)
    
    def draw_highlight(self, coord: HexCoord, color: Tuple[int, int, int] = Colors.YELLOW, alpha: int = 128) -> None:
        """Draw a highlighted hexagon (for effects or debugging)."""
        corners = self.grid.get_hex_corners(coord)
        
        # Create a surface for transparency
        s = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(s, (*color, alpha), corners)
        self.screen.blit(s, (0, 0))
    
    def draw_path(self, path: List[HexCoord], color: Tuple[int, int, int] = Colors.GREEN, width: int = 3) -> None:
        """Draw a path through hexagons (useful for debugging AI)."""
        if len(path) < 2:
            return
        
        points = []
        for coord in path:
            x, y = self.grid.axial_to_pixel(coord)
            points.append((x, y))
        
        pygame.draw.lines(self.screen, color, False, points, width)
    
    def draw_distance_field(self, coord: HexCoord, max_distance: int = 5) -> None:
        """Draw a distance field around a coordinate (useful for debugging)."""
        for distance in range(1, max_distance + 1):
            # Get all hexes at this distance
            all_coords = self.grid.get_all_valid_coords()
            for test_coord in all_coords:
                if coord.get_distance(test_coord) == distance:
                    alpha = max(20, 128 - (distance * 20))
                    self.draw_highlight(test_coord, Colors.BLUE, alpha)
    
    def set_grid_visibility(self, visible: bool) -> None:
        """Toggle grid line visibility."""
        self.show_grid_lines = visible
    
    def set_hex_outline_width(self, width: int) -> None:
        """Set the width of hexagon outlines."""
        self.hex_outline_width = max(1, width)
    
    def draw_background_pattern(self) -> None:
        """Draw a decorative background pattern."""
        # Create subtle hexagonal pattern in background
        valid_coords = self.grid.get_all_valid_coords()
        
        # Draw every other hex with a very light shade
        for i, coord in enumerate(valid_coords):
            if i % 3 == 0:  # Every third hex
                corners = self.grid.get_hex_corners(coord)
                # Very light background hex
                bg_color = tuple(c + 10 for c in self.background_color)
                bg_color = tuple(min(255, c) for c in bg_color)
                pygame.draw.polygon(self.screen, bg_color, corners)