"""Abstract base renderer for the snake game."""

from abc import ABC, abstractmethod
import pygame
from ..grids.base import BaseGrid
from ..entities.snake import Snake
from ..entities.food import Food


class BaseRenderer(ABC):
    """Abstract base class for all rendering implementations."""
    
    def __init__(self, screen: pygame.Surface, grid: BaseGrid):
        self.screen = screen
        self.grid = grid
    
    @abstractmethod
    def draw_grid(self) -> None:
        """Draw the game grid."""
        pass
    
    @abstractmethod
    def draw_snake(self, snake: Snake) -> None:
        """Draw the snake."""
        pass
    
    @abstractmethod
    def draw_food(self, food: Food) -> None:
        """Draw food."""
        pass
    
    def clear_screen(self, color: tuple = (20, 20, 20)) -> None:
        """Clear the screen with specified color."""
        self.screen.fill(color)
    
    def update_display(self) -> None:
        """Update the display (flip double buffer)."""
        pygame.display.flip()