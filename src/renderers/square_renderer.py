"""Square grid renderer for the snake game."""

import pygame
from typing import Tuple
from .base import BaseRenderer
from ..entities.grid import SquareCoord, SquareGrid
from ..entities.snake import Snake
from ..entities.food import Food


class SquareRenderer(BaseRenderer):
    """Renderer for square grid layout."""
    
    def __init__(self, screen: pygame.Surface, grid: SquareGrid, cell_size: int = 20):
        super().__init__(screen, grid)
        self.cell_size = cell_size
        
        # Colors
        self.colors = {
            'background': (20, 20, 20),
            'grid_line': (40, 40, 40),
            'snake_head': (0, 255, 0),
            'snake_body': (0, 200, 0),
            'food': (255, 0, 0),
        }
        
        # Calculate grid offset to center it
        self._calculate_grid_offset()
    
    def _calculate_grid_offset(self) -> None:
        """Calculate offset to center the grid on screen."""
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        self.grid_offset_x = (screen_width - grid_width) // 2
        self.grid_offset_y = (screen_height - grid_height) // 2
    
    def draw_grid(self) -> None:
        """Draw the game grid."""
        # Draw grid lines
        for x in range(self.grid.width + 1):
            start_x = self.grid_offset_x + x * self.cell_size
            start_y = self.grid_offset_y
            end_x = start_x
            end_y = start_y + self.grid.height * self.cell_size
            pygame.draw.line(self.screen, self.colors['grid_line'], 
                           (start_x, start_y), (end_x, end_y), 1)
        
        for y in range(self.grid.height + 1):
            start_x = self.grid_offset_x
            start_y = self.grid_offset_y + y * self.cell_size
            end_x = start_x + self.grid.width * self.cell_size
            end_y = start_y
            pygame.draw.line(self.screen, self.colors['grid_line'], 
                           (start_x, start_y), (end_x, end_y), 1)
    
    def draw_snake(self, snake: Snake) -> None:
        """Draw the snake."""
        segments = snake.get_segments()
        
        for i, segment in enumerate(segments):
            # Choose color based on segment position
            if i == 0:  # Head
                color = self.colors['snake_head']
            else:  # Body
                color = self.colors['snake_body']
            
            # Draw segment
            self._draw_cell(segment, color)
    
    def draw_food(self, food: Food) -> None:
        """Draw food on the grid."""
        self._draw_cell(food.get_position(), self.colors['food'])
    
    def _draw_cell(self, coord: SquareCoord, color: Tuple[int, int, int]) -> None:
        """Draw a single cell with the given color."""
        x = self.grid_offset_x + coord.x * self.cell_size
        y = self.grid_offset_y + coord.y * self.cell_size
        
        # Draw filled rectangle with small margin
        margin = 2
        pygame.draw.rect(self.screen, color,
                        (x + margin, y + margin, 
                         self.cell_size - 2 * margin, self.cell_size - 2 * margin))
    
    def grid_to_screen_coords(self, coord: SquareCoord) -> Tuple[int, int]:
        """Convert grid coordinates to screen coordinates."""
        x = self.grid_offset_x + coord.x * self.cell_size
        y = self.grid_offset_y + coord.y * self.cell_size
        return (x, y)
    
    def set_cell_size(self, size: int) -> None:
        """Set the size of grid cells."""
        self.cell_size = size
        self._calculate_grid_offset()
    
    def set_color(self, element: str, color: Tuple[int, int, int]) -> None:
        """Set a color scheme element."""
        if element in self.colors:
            self.colors[element] = color